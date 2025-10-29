"""Clear all workflow data from the database."""
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print("🗑️  Clearing database...")
print("=" * 80)

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        # Clear in order of dependencies
        cur.execute("DELETE FROM task_skills")
        cur.execute("DELETE FROM task_relationships")
        cur.execute("DELETE FROM workflow_relationships")
        cur.execute("DELETE FROM workflow_usage")
        cur.execute("DELETE FROM task_usage")
        cur.execute("DELETE FROM skill_usage")
        cur.execute("DELETE FROM tasks")
        cur.execute("DELETE FROM skills")
        cur.execute("DELETE FROM workflows")
        
        conn.commit()

print("✅ Database cleared!")
print("=" * 80)
