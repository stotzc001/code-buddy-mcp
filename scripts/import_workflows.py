"""Import workflows from directory into PostgreSQL database."""
import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
import click
from dotenv import load_dotenv
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import DatabaseConnection
from src.utils.embeddings import init_embeddings, EmbeddingGenerator

load_dotenv()


class WorkflowImporter:
    """Import workflows from markdown files."""
    
    def __init__(self, db: DatabaseConnection, embeddings: EmbeddingGenerator):
        """Initialize importer.
        
        Args:
            db: Database connection
            embeddings: Embedding generator
        """
        self.db = db
        self.embeddings = embeddings
    
    def parse_workflow_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a workflow markdown file.
        
        Expected format:
        - YAML-style frontmatter with metadata
        - Markdown content
        
        Args:
            file_path: Path to workflow file
            
        Returns:
            Workflow dictionary or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple frontmatter parsing (between --- markers)
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # Parse frontmatter (basic YAML parsing)
                    frontmatter = parts[1].strip()
                    body = parts[2].strip()
                    
                    metadata = {}
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Handle arrays [item1, item2]
                            if value.startswith('[') and value.endswith(']'):
                                value = [v.strip().strip('"\'') 
                                        for v in value[1:-1].split(',') 
                                        if v.strip()]
                            # Handle quoted strings
                            elif value.startswith('"') or value.startswith("'"):
                                value = value.strip('"\'')
                            
                            metadata[key] = value
                else:
                    metadata = {}
                    body = content
            else:
                metadata = {}
                body = content
            
            # Extract name from filename
            name = file_path.stem
            
            # Build workflow dict
            workflow = {
                'name': name,
                'title': metadata.get('title', name.replace('-', ' ').title()),
                'description': metadata.get('description', ''),
                'content': body,
                'category': metadata.get('category', 'Uncategorized'),
                'subcategory': metadata.get('subcategory'),
                'tags': metadata.get('tags', []),
                'technologies': metadata.get('technologies', []),
                'complexity': metadata.get('complexity', 'intermediate'),
                'estimated_time_minutes': metadata.get('estimated_time_minutes'),
                'use_cases': metadata.get('use_cases', []),
                'problem_statement': metadata.get('problem_statement'),
                'author': metadata.get('author'),
            }
            
            # Generate content hash
            workflow['content_hash'] = hashlib.sha256(
                body.encode('utf-8')
            ).hexdigest()
            
            return workflow
            
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return None
    
    def import_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Import a single workflow into database.
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding
            print(f"  📊 Generating embedding for '{workflow['title']}'...")
            embedding = self.embeddings.generate_workflow_embedding(
                title=workflow['title'],
                description=workflow['description'],
                content=workflow['content'],
                tags=workflow.get('tags'),
                use_cases=workflow.get('use_cases')
            )
            
            # Convert embedding to PostgreSQL array format
            embedding_str = f"[{','.join(map(str, embedding))}]"
            
            # Check if workflow exists
            check_query = "SELECT id FROM workflows WHERE name = :name"
            
            with self.db.get_session() as session:
                result = session.execute(text(check_query), {"name": workflow['name']})
                existing = result.fetchone()
                
                if existing:
                    # Update existing workflow
                    update_query = """
                        UPDATE workflows SET
                            title = :title,
                            description = :description,
                            content = :content,
                            content_hash = :content_hash,
                            category = :category,
                            subcategory = :subcategory,
                            tags = :tags,
                            technologies = :technologies,
                            complexity = :complexity,
                            estimated_time_minutes = :estimated_time_minutes,
                            use_cases = :use_cases,
                            problem_statement = :problem_statement,
                            author = :author,
                            embedding = CAST(:embedding AS vector),
                            version = version + 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE name = :name
                    """
                    session.execute(text(update_query), {
                        **workflow,
                        'embedding': embedding_str
                    })
                    print(f"  ✅ Updated: {workflow['title']}")
                else:
                    # Insert new workflow
                    insert_query = """
                        INSERT INTO workflows (
                            name, title, description, content, content_hash,
                            category, subcategory, tags, technologies,
                            complexity, estimated_time_minutes, use_cases,
                            problem_statement, author, embedding
                        ) VALUES (
                            :name, :title, :description, :content, :content_hash,
                            :category, :subcategory, :tags, :technologies,
                            :complexity, :estimated_time_minutes, :use_cases,
                            :problem_statement, :author, CAST(:embedding AS vector)
                        )
                    """
                    session.execute(text(insert_query), {
                        **workflow,
                        'embedding': embedding_str
                    })
                    print(f"  ✅ Imported: {workflow['title']}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error importing workflow: {e}")
            return False
    
    def import_directory(self, directory: Path, recursive: bool = True) -> Dict[str, int]:
        """Import all workflows from a directory.
        
        Args:
            directory: Directory containing workflow files
            recursive: Whether to search subdirectories
            
        Returns:
            Dictionary with import statistics
        """
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Find all markdown files
        pattern = '**/*.md' if recursive else '*.md'
        workflow_files = list(directory.glob(pattern))
        
        print(f"📁 Found {len(workflow_files)} workflow files")
        
        for file_path in workflow_files:
            stats['total'] += 1
            print(f"\n[{stats['total']}/{len(workflow_files)}] Processing: {file_path.name}")
            
            # Parse workflow
            workflow = self.parse_workflow_file(file_path)
            if not workflow:
                stats['failed'] += 1
                continue
            
            # Import workflow
            if self.import_workflow(workflow):
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        return stats


@click.command()
@click.option(
    '--directory',
    '-d',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help='Directory containing workflow files'
)
@click.option(
    '--recursive/--no-recursive',
    default=True,
    help='Search subdirectories recursively'
)
def main(directory: Path, recursive: bool):
    """Import workflows from directory into database."""
    print("📦 Code Buddy - Workflow Importer")
    print("=" * 50)
    
    # Check environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found")
        sys.exit(1)
    
    # Check for embedding provider configuration
    provider = os.getenv("EMBEDDING_PROVIDER", "openai")
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found")
        print("   Set EMBEDDING_PROVIDER=cohere or add OPENAI_API_KEY")
        sys.exit(1)
    elif provider == "cohere" and not os.getenv("COHERE_API_KEY"):
        print("❌ ERROR: COHERE_API_KEY not found")
        sys.exit(1)
    
    try:
        # Initialize connections
        print("🔌 Connecting to database...")
        db = DatabaseConnection(database_url)
        
        print(f"🤖 Initializing {provider} embedding generator...")
        embeddings = init_embeddings()
        
        # Import workflows
        importer = WorkflowImporter(db, embeddings)
        stats = importer.import_directory(directory, recursive)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Import Summary")
        print(f"  Total files:   {stats['total']}")
        print(f"  ✅ Success:    {stats['success']}")
        print(f"  ❌ Failed:     {stats['failed']}")
        print(f"  ⏭️  Skipped:    {stats['skipped']}")
        print("=" * 50)
        
        if stats['success'] > 0:
            print("\n🎉 Import complete!")
            print("Next step: Start the MCP server with: python src/server.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
