"""Setup PostgreSQL database with schema and pgvector extension."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import click

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import DatabaseConnection

load_dotenv()


@click.command()
@click.option('--reset', is_flag=True, help='Drop existing tables before creating new ones')
def main(reset):
    """Initialize database schema."""
    print("🚀 Code Buddy - Database Setup")
    print("=" * 50)
    
    # Check for DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    print(f"📡 Connecting to database...")
    
    try:
        db = DatabaseConnection(database_url)
        
        # Test connection
        print("🔍 Testing connection...")
        if not db.test_connection():
            print("❌ Connection test failed")
            sys.exit(1)
        print("✅ Connection successful")
        
        # Check pgvector
        print("🔍 Checking pgvector extension...")
        if not db.check_pgvector():
            print("⚠️  pgvector not found, attempting to install...")
            try:
                with db.get_session() as session:
                    from sqlalchemy import text
                    session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                print("✅ pgvector extension installed")
            except Exception as e:
                print(f"❌ Failed to install pgvector: {e}")
                print("Please install pgvector manually:")
                print("  https://github.com/pgvector/pgvector#installation")
                sys.exit(1)
        else:
            print("✅ pgvector extension found")
        
        # Reset database if requested
        if reset:
            print("⚠️  Dropping existing tables...")
            try:
                with db.get_session() as session:
                    from sqlalchemy import text
                    session.execute(text("""
                        DROP TABLE IF EXISTS workflow_usage CASCADE;
                        DROP TABLE IF EXISTS workflow_relationships CASCADE;
                        DROP TABLE IF EXISTS workflows CASCADE;
                        DROP TABLE IF EXISTS categories CASCADE;
                        DROP MATERIALIZED VIEW IF EXISTS popular_workflows;
                        DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
                    """))
                print("✅ Tables dropped successfully")
            except Exception as e:
                print(f"❌ Error dropping tables: {e}")
                sys.exit(1)
        
        # Execute schema
        schema_path = Path(__file__).parent.parent / "src" / "database" / "schema.sql"
        print(f"📄 Executing schema from {schema_path}...")
        
        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_path}")
            sys.exit(1)
        
        if not db.execute_schema(str(schema_path)):
            print("❌ Schema execution failed")
            sys.exit(1)
        
        print("✅ Schema executed successfully")
        
        # Verify tables
        print("🔍 Verifying tables...")
        with db.get_session() as session:
            from sqlalchemy import text
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
        
        expected_tables = [
            'workflows',
            'workflow_relationships',
            'workflow_usage',
            'categories'
        ]
        
        print("📋 Found tables:")
        for table in tables:
            status = "✅" if table in expected_tables else "ℹ️"
            print(f"  {status} {table}")
        
        missing = set(expected_tables) - set(tables)
        if missing:
            print(f"⚠️  Missing tables: {', '.join(missing)}")
        
        print("\n" + "=" * 50)
        print("🎉 Database setup complete!")
        print("\nNext steps:")
        print("1. Run: python scripts/import_workflows.py --directory ./workflows")
        print("2. Start MCP server: python src/server.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
