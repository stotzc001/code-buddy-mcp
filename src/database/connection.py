"""Database connection and session management."""
import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL connection pool."""
    
    def __init__(self, database_url: str = None):
        """Initialize database connection.
        
        Args:
            database_url: PostgreSQL connection string. 
                         Falls back to DATABASE_URL env var.
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL not provided")
        
        # Create engine with connection pooling
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=False  # Set to True for SQL debugging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info("Database connection initialized")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup.
        
        Yields:
            SQLAlchemy Session object
            
        Example:
            with db.get_session() as session:
                result = session.execute(text("SELECT 1"))
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connectivity.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def check_pgvector(self) -> bool:
        """Check if pgvector extension is installed.
        
        Returns:
            True if pgvector is available, False otherwise
        """
        try:
            with self.get_session() as session:
                result = session.execute(
                    text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
                )
                exists = result.scalar()
                if exists:
                    logger.info("pgvector extension is installed")
                else:
                    logger.warning("pgvector extension is NOT installed")
                return exists
        except Exception as e:
            logger.error(f"Error checking pgvector: {e}")
            return False
    
    def execute_schema(self, schema_path: str) -> bool:
        """Execute SQL schema file.
        
        Args:
            schema_path: Path to SQL schema file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Use raw psycopg connection to execute the entire schema
            # This handles functions with $ quotes properly
            import psycopg
            conn = psycopg.connect(self.database_url, autocommit=True)
            cur = conn.cursor()
            
            try:
                cur.execute(schema_sql)
                logger.info(f"Schema executed successfully from {schema_path}")
                return True
            finally:
                cur.close()
                conn.close()
                    
        except Exception as e:
            logger.error(f"Error executing schema: {e}")
            return False
    
    def close(self):
        """Close all database connections."""
        self.engine.dispose()
        logger.info("Database connections closed")


# Global database instance (initialized by server)
_db_instance: DatabaseConnection = None


def init_database(database_url: str = None) -> DatabaseConnection:
    """Initialize global database instance.
    
    Args:
        database_url: PostgreSQL connection string
        
    Returns:
        DatabaseConnection instance
    """
    global _db_instance
    _db_instance = DatabaseConnection(database_url)
    return _db_instance


def get_db() -> DatabaseConnection:
    """Get global database instance.
    
    Returns:
        DatabaseConnection instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if _db_instance is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _db_instance
