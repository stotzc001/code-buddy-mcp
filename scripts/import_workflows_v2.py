"""
Import Workflows V2 - Granular Structure
Imports workflows, tasks, and skills into the v2 database schema.
"""

import os
import sys
from pathlib import Path
from typing import List
import psycopg
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.parse_workflows_v2 import WorkflowParserV2, WorkflowV2, Task, Skill
from src.utils.embeddings import init_embeddings

# Load environment variables
load_dotenv()

# Initialize embeddings (will be set in main)
embedding_generator = None


class WorkflowImporterV2:
    """Imports workflows into the v2 granular database schema."""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        self.parser = WorkflowParserV2()
        self.workflow_ids = {}
        self.skill_ids = {}
    
    def connect(self):
        """Create database connection."""
        return psycopg.connect(self.db_url)
    
    def import_workflow(self, workflow: WorkflowV2, conn) -> int:
        """Import a single workflow and return its ID."""
        print(f"  📋 Importing workflow: {workflow.title}")
        
        print(f"     Generating workflow embedding...")
        workflow_embedding = embedding_generator.generate(
            f"{workflow.title}\n{workflow.description}\n{workflow.overview}"
        )
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO workflows (
                    name, title, description, overview,
                    category, subcategory, tags, technologies,
                    complexity, estimated_time_minutes,
                    use_cases, problem_statement, author
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    overview = EXCLUDED.overview,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (
                workflow.name,
                workflow.title,
                workflow.description,
                workflow.overview,
                workflow.category,
                workflow.subcategory,
                workflow.tags,
                workflow.technologies,
                workflow.complexity,
                workflow.estimated_time_minutes,
                workflow.use_cases,
                workflow.problem_statement,
                workflow.author
            ))
            
            workflow_id = cur.fetchone()[0]
            
            cur.execute(
                "UPDATE workflows SET embedding = %s WHERE id = %s",
                (workflow_embedding, workflow_id)
            )
        
        print(f"     ✓ Workflow saved (ID: {workflow_id})")
        self.workflow_ids[workflow.name] = workflow_id
        
        return workflow_id
    
    def import_tasks(self, workflow_id: int, tasks: List[Task], conn):
        """Import tasks for a workflow."""
        print(f"  📝 Importing {len(tasks)} tasks...")
        
        for task in tasks:
            task_text = f"{task.title}\n{task.description}\n{task.content[:1000]}"
            task_embedding = embedding_generator.generate(task_text)
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO tasks (
                        workflow_id, name, title, description,
                        step_number, content, prerequisites,
                        commands, verification_checks, estimated_time_minutes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (workflow_id, step_number) DO UPDATE SET
                        name = EXCLUDED.name,
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        content = EXCLUDED.content,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """, (
                    workflow_id,
                    task.name,
                    task.title,
                    task.description,
                    task.step_number,
                    task.content,
                    task.prerequisites,
                    task.commands,
                    task.verification_checks,
                    task.estimated_time_minutes
                ))
                
                task_id = cur.fetchone()[0]
                
                cur.execute(
                    "UPDATE tasks SET embedding = %s WHERE id = %s",
                    (task_embedding, task_id)
                )
            
            print(f"     ✓ Task {task.step_number}: {task.title}")
    
    def import_skill(self, skill: Skill, conn) -> int:
        """Import a single skill and return its ID."""
        if skill.name in self.skill_ids:
            return self.skill_ids[skill.name]
        
        skill_text = f"{skill.title}\n{skill.description}\n{skill.content[:500]}"
        skill_embedding = embedding_generator.generate(skill_text)
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO skills (
                    name, title, description, content,
                    category, tags, use_cases,
                    example_code, example_usage
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    content = EXCLUDED.content,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (
                skill.name,
                skill.title,
                skill.description,
                skill.content,
                skill.category,
                skill.tags,
                skill.use_cases,
                skill.example_code,
                skill.example_usage
            ))
            
            skill_id = cur.fetchone()[0]
            
            cur.execute(
                "UPDATE skills SET embedding = %s WHERE id = %s",
                (skill_embedding, skill_id)
            )
        
        self.skill_ids[skill.name] = skill_id
        return skill_id
    
    def import_skills(self, skills: List[Skill], conn):
        """Import multiple skills."""
        if not skills:
            return
        
        print(f"  🎯 Importing {len(skills)} skills...")
        
        for skill in skills:
            skill_id = self.import_skill(skill, conn)
            print(f"     ✓ Skill: {skill.title}")
    
    def import_workflow_file(self, filepath: Path, conn):
        """Import a single workflow file."""
        print(f"\n📄 Processing: {filepath.name}")
        
        try:
            workflow = self.parser.parse_file(filepath)
            workflow_id = self.import_workflow(workflow, conn)
            self.import_tasks(workflow_id, workflow.tasks, conn)
            self.import_skills(workflow.skills, conn)
            
            conn.commit()
            print(f"  ✓ Complete\n")
            
            return True
        
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            conn.rollback()
            return False
    
    def import_all_workflows(self, workflows_dir: Path):
        """Import all workflow files from a directory."""
        print("=" * 80)
        print("IMPORTING WORKFLOWS V2 - GRANULAR STRUCTURE")
        print("=" * 80)
        
        workflow_files = []
        for category_dir in workflows_dir.iterdir():
            if category_dir.is_dir():
                for file in category_dir.glob("*.md"):
                    if file.name not in ['_INDEX.md', 'README.md']:
                        workflow_files.append(file)
        
        print(f"\nFound {len(workflow_files)} workflow files")
        print(f"Database: {self.db_url.split('@')[1]}\n")
        
        success_count = 0
        error_count = 0
        
        with self.connect() as conn:
            for filepath in sorted(workflow_files):
                if self.import_workflow_file(filepath, conn):
                    success_count += 1
                else:
                    error_count += 1
        
        print("=" * 80)
        print("IMPORT COMPLETE")
        print("=" * 80)
        print(f"✓ Successfully imported: {success_count}")
        print(f"✗ Errors: {error_count}")
        
        self._print_statistics()
    
    def _print_statistics(self):
        """Print database statistics."""
        print("\n" + "=" * 80)
        print("DATABASE STATISTICS")
        print("=" * 80)
        
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM workflows WHERE is_active = TRUE")
                workflow_count = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM tasks")
                task_count = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM skills WHERE is_active = TRUE")
                skill_count = cur.fetchone()[0]
                
                cur.execute("""
                    SELECT AVG(task_count)::INTEGER
                    FROM (
                        SELECT workflow_id, COUNT(*) as task_count
                        FROM tasks
                        GROUP BY workflow_id
                    ) t
                """)
                avg_tasks = cur.fetchone()[0] or 0
                
                cur.execute("""
                    SELECT category, COUNT(*)
                    FROM workflows
                    WHERE is_active = TRUE
                    GROUP BY category
                    ORDER BY category
                """)
                categories = cur.fetchall()
        
        print(f"\n📊 Totals:")
        print(f"   Workflows: {workflow_count}")
        print(f"   Tasks: {task_count}")
        print(f"   Skills: {skill_count}")
        print(f"   Avg tasks per workflow: {avg_tasks}")
        
        print(f"\n📁 By Category:")
        for category, count in categories:
            print(f"   {category}: {count}")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point."""
    global embedding_generator
    
    # Initialize embeddings
    print("Initializing embedding generator...")
    try:
        embedding_generator = init_embeddings()
        print(f"✓ Embedding generator initialized\n")
    except Exception as e:
        print(f"Error initializing embeddings: {e}")
        print("Make sure OPENAI_API_KEY is set in your .env file")
        sys.exit(1)
    
    workflows_dir = Path("C:/Repos/code_buddy_mcp/workflows")
    
    if not workflows_dir.exists():
        print(f"Error: Workflows directory not found: {workflows_dir}")
        sys.exit(1)
    
    importer = WorkflowImporterV2()
    importer.import_all_workflows(workflows_dir)


if __name__ == "__main__":
    main()
