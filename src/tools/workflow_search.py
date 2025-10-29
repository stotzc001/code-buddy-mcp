"""Multi-stage workflow search with intelligent ranking."""
from typing import List, Dict, Any, Optional
from sqlalchemy import text
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db
from utils.embeddings import get_embeddings

logger = logging.getLogger(__name__)


class WorkflowSearcher:
    """Implements three-stage workflow search strategy."""
    
    def __init__(self):
        """Initialize workflow searcher."""
        self.db = get_db()
        self.embeddings = get_embeddings()
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        technologies: Optional[List[str]] = None,
        complexity: Optional[str] = None,
        max_time_minutes: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Execute three-stage workflow search.
        
        Stage 1: Metadata filtering
        Stage 2: Semantic search on filtered results
        Stage 3: Relationship-aware ranking
        
        Args:
            query: Natural language search query
            category: Filter by category
            tags: Filter by tags (any match)
            technologies: Filter by technologies (any match)
            complexity: Filter by complexity level
            max_time_minutes: Maximum estimated time
            limit: Maximum number of results
            
        Returns:
            List of workflow dictionaries with similarity scores
        """
        logger.info(f"Search query: '{query}', filters: category={category}, "
                   f"tags={tags}, technologies={technologies}")
        
        # Stage 1: Metadata Filtering
        filtered_ids = self._stage1_metadata_filter(
            category=category,
            tags=tags,
            technologies=technologies,
            complexity=complexity,
            max_time_minutes=max_time_minutes
        )
        
        if not filtered_ids:
            logger.warning("Stage 1 returned no results")
            return []
        
        logger.info(f"Stage 1: {len(filtered_ids)} workflows after metadata filtering")
        
        # Stage 2: Semantic Search
        query_embedding = self.embeddings.generate(query)
        semantic_results = self._stage2_semantic_search(
            query_embedding=query_embedding,
            filtered_ids=filtered_ids,
            limit=limit * 2  # Get more for ranking stage
        )
        
        if not semantic_results:
            logger.warning("Stage 2 returned no results")
            return []
        
        logger.info(f"Stage 2: {len(semantic_results)} workflows after semantic search")
        
        # Stage 3: Relationship-Aware Ranking
        ranked_results = self._stage3_relationship_ranking(
            semantic_results=semantic_results,
            limit=limit
        )
        
        logger.info(f"Stage 3: {len(ranked_results)} final ranked workflows")
        
        return ranked_results
    
    def _stage1_metadata_filter(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        technologies: Optional[List[str]] = None,
        complexity: Optional[str] = None,
        max_time_minutes: Optional[int] = None
    ) -> List[int]:
        """Stage 1: Filter workflows by metadata.
        
        Returns:
            List of workflow IDs that match filters
        """
        conditions = ["is_active = TRUE"]
        params = {}
        
        if category:
            conditions.append("category = :category")
            params["category"] = category
        
        if tags:
            conditions.append("tags && :tags")  # Array overlap operator
            params["tags"] = tags
        
        if technologies:
            conditions.append("technologies && :technologies")
            params["technologies"] = technologies
        
        if complexity:
            conditions.append("complexity = :complexity")
            params["complexity"] = complexity
        
        if max_time_minutes:
            conditions.append("estimated_time_minutes <= :max_time")
            params["max_time"] = max_time_minutes
        
        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT id 
            FROM workflows 
            WHERE {where_clause}
        """
        
        with self.db.get_session() as session:
            result = session.execute(text(query), params)
            workflow_ids = [row[0] for row in result]
        
        return workflow_ids
    
    def _stage2_semantic_search(
        self,
        query_embedding: List[float],
        filtered_ids: List[int],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Stage 2: Semantic search using pgvector.
        
        Args:
            query_embedding: Query embedding vector
            filtered_ids: Workflow IDs from Stage 1
            limit: Number of results to return
            
        Returns:
            List of workflows with similarity scores
        """
        # Convert embedding to PostgreSQL vector format
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        query = """
            SELECT 
                id,
                name,
                title,
                description,
                category,
                subcategory,
                tags,
                technologies,
                complexity,
                estimated_time_minutes,
                use_cases,
                prerequisites,
                1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
            FROM workflows
            WHERE id = ANY(:filtered_ids)
            ORDER BY embedding <=> CAST(:query_embedding AS vector)
            LIMIT :limit
        """
        
        with self.db.get_session() as session:
            result = session.execute(
                text(query),
                {
                    "query_embedding": embedding_str,
                    "filtered_ids": filtered_ids,
                    "limit": limit
                }
            )
            
            workflows = []
            for row in result:
                workflows.append({
                    "id": row[0],
                    "name": row[1],
                    "title": row[2],
                    "description": row[3],
                    "category": row[4],
                    "subcategory": row[5],
                    "tags": row[6] or [],
                    "technologies": row[7] or [],
                    "complexity": row[8],
                    "estimated_time_minutes": row[9],
                    "use_cases": row[10] or [],
                    "prerequisites": row[11] or [],
                    "similarity": float(row[12])
                })
        
        return workflows
    
    def _stage3_relationship_ranking(
        self,
        semantic_results: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Stage 3: Re-rank using relationships and usage analytics.
        
        Args:
            semantic_results: Results from Stage 2
            limit: Number of results to return
            
        Returns:
            Final ranked list of workflows
        """
        workflow_ids = [w["id"] for w in semantic_results]
        
        # Get usage statistics
        usage_query = """
            SELECT 
                workflow_id,
                COUNT(*) as usage_count,
                AVG(CASE WHEN was_helpful THEN 1 ELSE 0 END) as helpfulness_ratio
            FROM workflow_usage
            WHERE workflow_id = ANY(:workflow_ids)
            GROUP BY workflow_id
        """
        
        usage_stats = {}
        with self.db.get_session() as session:
            result = session.execute(
                text(usage_query),
                {"workflow_ids": workflow_ids}
            )
            for row in result:
                usage_stats[row[0]] = {
                    "usage_count": row[1],
                    "helpfulness_ratio": float(row[2]) if row[2] else 0.0
                }
        
        # Calculate final scores
        for workflow in semantic_results:
            wf_id = workflow["id"]
            
            # Base score from semantic similarity
            score = workflow["similarity"]
            
            # Boost based on usage
            if wf_id in usage_stats:
                stats = usage_stats[wf_id]
                # Boost by usage (logarithmic scale)
                usage_boost = min(0.1, stats["usage_count"] * 0.01)
                # Boost by helpfulness
                helpfulness_boost = stats["helpfulness_ratio"] * 0.05
                score += usage_boost + helpfulness_boost
            
            # Store final score
            workflow["final_score"] = score
            workflow["usage_count"] = usage_stats.get(wf_id, {}).get("usage_count", 0)
            workflow["helpfulness"] = usage_stats.get(wf_id, {}).get("helpfulness_ratio", 0.0)
        
        # Sort by final score and limit
        semantic_results.sort(key=lambda x: x["final_score"], reverse=True)
        
        return semantic_results[:limit]
    
    def get_workflow_by_id(self, workflow_id: int) -> Optional[Dict[str, Any]]:
        """Get complete workflow by ID.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow dictionary or None if not found
        """
        query = """
            SELECT 
                id, name, title, description, overview,
                category, subcategory, tags, technologies,
                complexity, estimated_time_minutes,
                use_cases, prerequisites, problem_statement,
                created_at, updated_at, version, author
            FROM workflows
            WHERE id = :workflow_id AND is_active = TRUE
        """
        
        with self.db.get_session() as session:
            result = session.execute(text(query), {"workflow_id": workflow_id})
            row = result.fetchone()
            
            if not row:
                return None
            
            return {
                "id": row[0],
                "name": row[1],
                "title": row[2],
                "description": row[3],
                "content": row[4],  # Database column is 'overview' but we return as 'content'
                "category": row[5],
                "subcategory": row[6],
                "tags": row[7] or [],
                "technologies": row[8] or [],
                "complexity": row[9],
                "estimated_time_minutes": row[10],
                "use_cases": row[11] or [],
                "prerequisites": row[12] or [],
                "problem_statement": row[13],
                "created_at": str(row[14]),
                "updated_at": str(row[15]),
                "version": row[16],
                "author": row[17]
            }
    
    def get_prerequisites_chain(self, workflow_id: int) -> List[Dict[str, Any]]:
        """Get prerequisite chain for a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            List of prerequisite workflows in order
        """
        query = """
            WITH RECURSIVE prereq_chain AS (
                -- Base case: direct prerequisites
                SELECT 
                    w.id, w.name, w.title, w.description,
                    1 as depth
                FROM workflows w
                WHERE w.id IN (
                    SELECT unnest(prerequisites) 
                    FROM workflows 
                    WHERE id = :workflow_id
                )
                
                UNION ALL
                
                -- Recursive case: prerequisites of prerequisites
                SELECT 
                    w.id, w.name, w.title, w.description,
                    pc.depth + 1
                FROM workflows w
                JOIN prereq_chain pc ON w.id = ANY(
                    SELECT unnest(prerequisites) 
                    FROM workflows 
                    WHERE id = pc.id
                )
                WHERE pc.depth < 5  -- Limit recursion depth
            )
            SELECT DISTINCT id, name, title, description, depth
            FROM prereq_chain
            ORDER BY depth, id
        """
        
        with self.db.get_session() as session:
            result = session.execute(text(query), {"workflow_id": workflow_id})
            
            prerequisites = []
            for row in result:
                prerequisites.append({
                    "id": row[0],
                    "name": row[1],
                    "title": row[2],
                    "description": row[3],
                    "depth": row[4]
                })
        
        return prerequisites
