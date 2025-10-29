"""
Deploy Schema V2 - Granular Structure
Deploys the new granular schema with workflows, tasks, and skills.
"""

import os
import sys
from pathlib import Path
import psycopg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def deploy_schema_v2():
    """Deploy the v2 schema to the database."""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("Error: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    # Read schema file
    schema_path = Path(__file__).parent.parent / 'src' / 'database' / 'schema_v2.sql'
    
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}")
        sys.exit(1)
    
    print("=" * 80)
    print("DEPLOYING SCHEMA V2 - GRANULAR STRUCTURE")
    print("=" * 80)
    print(f"\nDatabase: {db_url.split('@')[1]}")
    print(f"Schema file: {schema_path}")
    print()
    
    # Confirm deployment
    confirm = input("This will DROP existing tables if they exist. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Deployment cancelled.")
        sys.exit(0)
    
    # Read schema SQL
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Connect and deploy
    try:
        with psycopg.connect(db_url) as conn:
            print("\n📡 Connected to database")
            
            # Drop existing tables (if migrating from v1)
            print("\n🗑️  Dropping old tables (if they exist)...")
            with conn.cursor() as cur:
                cur.execute("""
                    DROP TABLE IF EXISTS workflow_usage CASCADE;
                    DROP TABLE IF EXISTS task_usage CASCADE;
                    DROP TABLE IF EXISTS skill_usage CASCADE;
                    DROP TABLE IF EXISTS task_relationships CASCADE;
                    DROP TABLE IF EXISTS workflow_relationships CASCADE;
                    DROP TABLE IF EXISTS task_skills CASCADE;
                    DROP TABLE IF EXISTS skills CASCADE;
                    DROP TABLE IF EXISTS tasks CASCADE;
                    DROP TABLE IF EXISTS workflows CASCADE;
                    DROP TABLE IF EXISTS categories CASCADE;
                    DROP MATERIALIZED VIEW IF EXISTS popular_workflows CASCADE;
                    DROP MATERIALIZED VIEW IF EXISTS popular_tasks CASCADE;
                    DROP MATERIALIZED VIEW IF EXISTS popular_skills CASCADE;
                """)
                conn.commit()
            
            print("   ✓ Old tables dropped")
            
            # Execute schema
            print("\n🏗️  Creating new schema...")
            with conn.cursor() as cur:
                cur.execute(schema_sql)
                conn.commit()
            
            print("   ✓ Schema created")
            
            # Verify tables
            print("\n✅ Verifying tables...")
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """)
                
                tables = cur.fetchall()
                print(f"\n   Created {len(tables)} tables:")
                for table in tables:
                    print(f"      - {table[0]}")
            
            # Verify materialized views
            print("\n   Materialized views:")
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT matviewname
                    FROM pg_matviews
                    WHERE schemaname = 'public'
                    ORDER BY matviewname
                """)
                
                views = cur.fetchall()
                for view in views:
                    print(f"      - {view[0]}")
            
            # Check pgvector
            print("\n   Extensions:")
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT extname, extversion
                    FROM pg_extension
                    WHERE extname = 'vector'
                """)
                
                ext = cur.fetchone()
                if ext:
                    print(f"      ✓ pgvector {ext[1]} installed")
                else:
                    print("      ⚠️  pgvector not found")
            
            print("\n" + "=" * 80)
            print("✅ SCHEMA V2 DEPLOYED SUCCESSFULLY")
            print("=" * 80)
            print("\nNext steps:")
            print("1. Run: python scripts/import_workflows_v2.py")
            print("2. Test search with the new granular structure")
            print()
    
    except Exception as e:
        print(f"\n❌ Error deploying schema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    deploy_schema_v2()
