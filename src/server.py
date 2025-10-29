"""Code Buddy MCP Server - Intelligent Workflow Management."""
import os
import sys
import logging
from typing import Optional, List
from dotenv import load_dotenv
from fastmcp import FastMCP

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import init_database, get_db
from utils.embeddings import init_embeddings
from tools.workflow_search import WorkflowSearcher

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Code Buddy")

# Initialize database and embeddings on startup
try:
    db = init_database()
    embeddings = init_embeddings()
    searcher = WorkflowSearcher()
    logger.info("Code Buddy MCP Server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize server: {e}")
    raise


@mcp.tool()
def search_workflows(
    query: str,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    technologies: Optional[List[str]] = None,
    complexity: Optional[str] = None,
    max_time_minutes: Optional[int] = None,
    limit: int = 5
) -> str:
    """Search for relevant workflows using intelligent multi-stage filtering.
    
    This tool uses a three-stage search strategy:
    1. Metadata filtering (category, tags, technologies, complexity, time)
    2. Semantic search using embeddings (finds conceptually similar workflows)
    3. Relationship-aware ranking (considers prerequisites, usage analytics)
    
    Args:
        query: Natural language description of what you need
        category: Filter by category (e.g., 'Development', 'Data Engineering')
        tags: List of tags to filter by (any match)
        technologies: List of technologies to filter by (e.g., ['Python', 'FastAPI'])
        complexity: Filter by complexity ('beginner', 'intermediate', 'advanced', 'expert')
        max_time_minutes: Maximum estimated time in minutes
        limit: Maximum number of results (default: 5)
    
    Returns:
        Formatted search results with workflow summaries
    
    Examples:
        search_workflows("create a REST API endpoint", technologies=["Python", "FastAPI"])
        search_workflows("database migration", category="Data Engineering", complexity="intermediate")
    """
    try:
        results = searcher.search(
            query=query,
            category=category,
            tags=tags,
            technologies=technologies,
            complexity=complexity,
            max_time_minutes=max_time_minutes,
            limit=limit
        )
        
        if not results:
            return "No workflows found matching your criteria. Try broadening your search."
        
        # Format results
        output = f"Found {len(results)} relevant workflow(s):\n\n"
        
        for i, wf in enumerate(results, 1):
            output += f"## {i}. {wf['title']}\n"
            output += f"**ID:** {wf['id']}\n"
            output += f"**Category:** {wf['category']}"
            if wf.get('subcategory'):
                output += f" > {wf['subcategory']}"
            output += "\n"
            output += f"**Complexity:** {wf['complexity']}\n"
            if wf.get('estimated_time_minutes'):
                output += f"**Estimated Time:** {wf['estimated_time_minutes']} minutes\n"
            output += f"**Similarity Score:** {wf['similarity']:.3f}\n"
            if wf.get('usage_count', 0) > 0:
                output += f"**Usage:** {wf['usage_count']} times "
                output += f"({wf['helpfulness']*100:.0f}% helpful)\n"
            output += f"\n{wf['description']}\n"
            
            if wf.get('tags'):
                output += f"\n**Tags:** {', '.join(wf['tags'])}\n"
            if wf.get('technologies'):
                output += f"**Technologies:** {', '.join(wf['technologies'])}\n"
            if wf.get('use_cases'):
                output += f"**Use Cases:** {', '.join(wf['use_cases'][:3])}\n"
            
            output += f"\n*Use `get_workflow({wf['id']})` to see the complete workflow*\n"
            output += "\n---\n\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Error in search_workflows: {e}")
        return f"Error searching workflows: {str(e)}"


@mcp.tool()
def get_workflow(workflow_id: int) -> str:
    """Get the complete content of a specific workflow.
    
    Args:
        workflow_id: The ID of the workflow to retrieve
    
    Returns:
        Complete workflow content with metadata
    """
    try:
        workflow = searcher.get_workflow_by_id(workflow_id)
        
        if not workflow:
            return f"Workflow with ID {workflow_id} not found."
        
        # Format complete workflow
        output = f"# {workflow['title']}\n\n"
        output += f"**ID:** {workflow['id']} | **Name:** {workflow['name']}\n"
        output += f"**Category:** {workflow['category']}"
        if workflow.get('subcategory'):
            output += f" > {workflow['subcategory']}"
        output += "\n\n"
        
        if workflow.get('problem_statement'):
            output += f"## Problem Statement\n{workflow['problem_statement']}\n\n"
        
        output += f"## Description\n{workflow['description']}\n\n"
        
        # Metadata section
        output += "## Metadata\n"
        output += f"- **Complexity:** {workflow['complexity']}\n"
        if workflow.get('estimated_time_minutes'):
            output += f"- **Estimated Time:** {workflow['estimated_time_minutes']} minutes\n"
        if workflow.get('tags'):
            output += f"- **Tags:** {', '.join(workflow['tags'])}\n"
        if workflow.get('technologies'):
            output += f"- **Technologies:** {', '.join(workflow['technologies'])}\n"
        if workflow.get('use_cases'):
            output += f"- **Use Cases:** {', '.join(workflow['use_cases'])}\n"
        output += f"- **Version:** {workflow['version']}\n"
        if workflow.get('author'):
            output += f"- **Author:** {workflow['author']}\n"
        output += "\n"
        
        # Prerequisites
        if workflow.get('prerequisites'):
            output += "## Prerequisites\n"
            prereqs = searcher.get_prerequisites_chain(workflow_id)
            if prereqs:
                output += "Complete these workflows first:\n"
                for prereq in prereqs:
                    output += f"- [{prereq['title']}] (ID: {prereq['id']})\n"
            else:
                output += "None\n"
            output += "\n"
        
        # Main content
        output += "## Workflow\n\n"
        output += workflow['content']
        
        return output
        
    except Exception as e:
        logger.error(f"Error in get_workflow: {e}")
        return f"Error retrieving workflow: {str(e)}"


@mcp.tool()
def list_categories() -> str:
    """List all available workflow categories for browsing.
    
    Returns:
        Formatted list of categories with descriptions
    """
    try:
        from sqlalchemy import text
        
        query = """
            SELECT 
                c.name,
                c.description,
                c.icon,
                COUNT(w.id) as workflow_count
            FROM categories c
            LEFT JOIN workflows w ON c.name = w.category AND w.is_active = TRUE
            GROUP BY c.id, c.name, c.description, c.icon, c.display_order
            ORDER BY c.display_order
        """
        
        with db.get_session() as session:
            result = session.execute(text(query))
            
            output = "# Workflow Categories\n\n"
            
            for row in result:
                name, desc, icon, count = row
                output += f"{icon} **{name}** ({count} workflows)\n"
                output += f"   {desc}\n\n"
            
            output += "\n*Use `search_workflows(category='Category Name')` to browse workflows*\n"
            
            return output
            
    except Exception as e:
        logger.error(f"Error in list_categories: {e}")
        return f"Error listing categories: {str(e)}"


@mcp.tool()
def get_prerequisites(workflow_id: int) -> str:
    """Get the prerequisite chain for a workflow.
    
    Shows all workflows that should be completed before the specified workflow,
    organized by dependency depth.
    
    Args:
        workflow_id: The ID of the workflow
    
    Returns:
        Formatted prerequisite chain
    """
    try:
        prereqs = searcher.get_prerequisites_chain(workflow_id)
        
        if not prereqs:
            return f"Workflow {workflow_id} has no prerequisites."
        
        output = f"# Prerequisites for Workflow {workflow_id}\n\n"
        output += "Complete these workflows in order:\n\n"
        
        current_depth = 0
        for prereq in prereqs:
            if prereq['depth'] > current_depth:
                current_depth = prereq['depth']
                output += f"\n**Level {current_depth}:**\n"
            
            output += f"- [{prereq['title']}] (ID: {prereq['id']})\n"
            output += f"  {prereq['description']}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Error in get_prerequisites: {e}")
        return f"Error getting prerequisites: {str(e)}"


@mcp.tool()
def track_usage(
    workflow_id: int,
    was_helpful: Optional[bool] = None,
    feedback: Optional[str] = None
) -> str:
    """Track workflow usage for analytics and improved ranking.
    
    This helps the system learn which workflows are most useful and improves
    future search results.
    
    Args:
        workflow_id: The ID of the workflow used
        was_helpful: Whether the workflow was helpful (True/False)
        feedback: Optional feedback text
    
    Returns:
        Confirmation message
    """
    try:
        from sqlalchemy import text
        
        query = """
            INSERT INTO workflow_usage 
                (workflow_id, was_helpful, feedback)
            VALUES 
                (:workflow_id, :was_helpful, :feedback)
        """
        
        with db.get_session() as session:
            session.execute(
                text(query),
                {
                    "workflow_id": workflow_id,
                    "was_helpful": was_helpful,
                    "feedback": feedback
                }
            )
        
        return f"Usage tracked for workflow {workflow_id}. Thank you for the feedback!"
        
    except Exception as e:
        logger.error(f"Error in track_usage: {e}")
        return f"Error tracking usage: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server
    logger.info("Starting Code Buddy MCP Server...")
    mcp.run()
