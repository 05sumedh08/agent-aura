"""
Production Database Configuration with PostgreSQL
Includes connection pooling, health checks, and migration support
"""
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import event, text
import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class DatabaseConfig:
    """Production database configuration"""
    
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL",
            "sqlite+aiosqlite:///./agent_aura_local.db"
        )
        
        # Convert PostgreSQL URL if needed (for compatibility)
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        
        self.is_sqlite = "sqlite" in self.database_url
        self.is_postgres = "postgresql" in self.database_url
        
        # Pool configuration
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
        # Connection retry
        self.max_retries = int(os.getenv("DB_MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("DB_RETRY_DELAY", "1"))
        
        logger.info(f"Database configured: {self.database_url.split('@')[0]}...")
        logger.info(f"Pool size: {self.pool_size}, Max overflow: {self.max_overflow}")


# Global database configuration
db_config = DatabaseConfig()


# Engine configuration based on database type
if db_config.is_sqlite:
    # SQLite: Use NullPool for better concurrency
    engine = create_async_engine(
        db_config.database_url,
        echo=os.getenv("DEBUG", "false").lower() == "true",
        poolclass=NullPool,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL: Use QueuePool for connection pooling
    engine = create_async_engine(
        db_config.database_url,
        echo=os.getenv("DEBUG", "false").lower() == "true",
        poolclass=QueuePool,
        pool_size=db_config.pool_size,
        max_overflow=db_config.max_overflow,
        pool_timeout=db_config.pool_timeout,
        pool_recycle=db_config.pool_recycle,
        pool_pre_ping=True,  # Verify connections before using
    )


# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions
    Includes automatic cleanup and error handling
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables
    Creates all tables if they don't exist
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def check_db_health() -> dict:
    """
    Health check for database connection
    Returns connection status and metrics
    """
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            
            # Get pool statistics if PostgreSQL
            pool_stats = {}
            if db_config.is_postgres and hasattr(engine.pool, 'size'):
                pool_stats = {
                    "pool_size": engine.pool.size(),
                    "checked_in": engine.pool.checkedin(),
                    "checked_out": engine.pool.checkedout(),
                    "overflow": engine.pool.overflow(),
                }
            
            return {
                "status": "healthy",
                "database_type": "postgresql" if db_config.is_postgres else "sqlite",
                "connection": "active",
                **pool_stats
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "connection": "failed"
        }


async def close_db():
    """
    Close database connections gracefully
    Call on application shutdown
    """
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


# Connection event listeners for PostgreSQL
if db_config.is_postgres:
    @event.listens_for(engine.sync_engine, "connect")
    def set_postgresql_pragma(dbapi_conn, connection_record):
        """Configure PostgreSQL connection settings"""
        cursor = dbapi_conn.cursor()
        # Set timezone
        cursor.execute("SET TIME ZONE 'UTC'")
        # Set statement timeout (30 seconds)
        cursor.execute("SET statement_timeout = 30000")
        cursor.close()
    
    logger.info("PostgreSQL connection event listeners registered")


# Export commonly used items
__all__ = [
    "Base",
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "init_db",
    "check_db_health",
    "close_db",
    "db_config",
]
