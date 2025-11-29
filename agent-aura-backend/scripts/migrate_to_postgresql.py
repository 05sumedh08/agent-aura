"""
PostgreSQL Migration Script
Migrates data from SQLite to PostgreSQL for production deployment
"""
import asyncio
import os
import re
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, inspect
from app.models.database import Base, User, Session, Event, Student
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Handles migration from SQLite to PostgreSQL"""
    
    def __init__(
        self,
        sqlite_url: str = "sqlite+aiosqlite:///./agent_aura_local.db",
        postgres_url: str = None
    ):
        self.sqlite_url = sqlite_url
        self.postgres_url = postgres_url or os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://agent_aura_user:password@localhost:5432/agent_aura_prod"
        )
        
        logger.info(f"Source (SQLite): {self.sqlite_url}")
        logger.info(f"Target (PostgreSQL): {self.postgres_url.split('@')[0]}...")
        
        # Create engines
        self.sqlite_engine = create_async_engine(self.sqlite_url, echo=False)
        self.postgres_engine = create_async_engine(self.postgres_url, echo=False)
        
        # Session factories
        self.SQLiteSession = async_sessionmaker(
            self.sqlite_engine, class_=AsyncSession, expire_on_commit=False
        )
        self.PostgresSession = async_sessionmaker(
            self.postgres_engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def check_connections(self) -> bool:
        """Test database connections"""
        try:
            # Test SQLite
            async with self.sqlite_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("[OK] SQLite connection successful")
            
            # Test PostgreSQL
            async with self.postgres_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("[OK] PostgreSQL connection successful")
            
            return True
        except Exception as e:
            logger.error(f"✗ Connection test failed: {e}")
            return False
    
    async def create_postgres_schema(self):
        """Create all tables in PostgreSQL"""
        try:
            async with self.postgres_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("[OK] PostgreSQL schema created")
        except Exception as e:
            logger.error(f"✗ Failed to create schema: {e}")
            raise
    
    async def migrate_table(self, model_class, batch_size: int = 100):
        """Migrate data for a specific table"""
        table_name = model_class.__tablename__
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name or ""):
            raise ValueError("Invalid table identifier")
        logger.info(f"Migrating table: {table_name}")
        
        try:
            # Read from SQLite
            async with self.SQLiteSession() as sqlite_session:
                result = await sqlite_session.execute(
                    text("SELECT * FROM " + table_name)
                )
                rows = result.fetchall()
                
                if not rows:
                    logger.info(f"  No data to migrate in {table_name}")
                    return 0
                
                logger.info(f"  Found {len(rows)} rows")
                
                # Get column names
                columns = result.keys()
                
                # Write to PostgreSQL in batches
                async with self.PostgresSession() as postgres_session:
                    migrated = 0
                    
                    for i in range(0, len(rows), batch_size):
                        batch = rows[i:i + batch_size]
                        
                        # Convert rows to dictionaries
                        data = [dict(zip(columns, row)) for row in batch]
                        
                        # Insert batch
                        for item in data:
                            obj = model_class(**item)
                            postgres_session.add(obj)
                        
                        await postgres_session.commit()
                        migrated += len(batch)
                        logger.info(f"  Migrated {migrated}/{len(rows)} rows")
                
                logger.info(f"[OK] Completed migration of {table_name}: {migrated} rows")
                return migrated
                
        except Exception as e:
            logger.error(f"✗ Failed to migrate {table_name}: {e}")
            raise
    
    async def verify_migration(self, model_class):
        """Verify data was migrated correctly"""
        table_name = model_class.__tablename__
        
        try:
            # Count in SQLite
            async with self.SQLiteSession() as sqlite_session:
                result = await sqlite_session.execute(
                    text("SELECT COUNT(*) FROM " + table_name)
                )
                sqlite_count = result.scalar()
            
            # Count in PostgreSQL
            async with self.PostgresSession() as postgres_session:
                result = await postgres_session.execute(
                    text("SELECT COUNT(*) FROM " + table_name)
                )
                postgres_count = result.scalar()
            
            if sqlite_count == postgres_count:
                logger.info(f"[OK] Verification passed for {table_name}: {postgres_count} rows")
                return True
            else:
                logger.warning(
                    f"✗ Row count mismatch in {table_name}: "
                    f"SQLite={sqlite_count}, PostgreSQL={postgres_count}"
                )
                return False
                
        except Exception as e:
            logger.error(f"✗ Verification failed for {table_name}: {e}")
            return False
    
    async def migrate_all(self):
        """Execute complete migration"""
        logger.info("=" * 60)
        logger.info("Starting Database Migration: SQLite → PostgreSQL")
        logger.info("=" * 60)
        
        # Step 1: Check connections
        logger.info("\n[1/5] Checking connections...")
        if not await self.check_connections():
            logger.error("Migration aborted: Connection test failed")
            return False
        
        # Step 2: Create PostgreSQL schema
        logger.info("\n[2/5] Creating PostgreSQL schema...")
        await self.create_postgres_schema()
        
        # Step 3: Migrate tables in order (respecting foreign keys)
        logger.info("\n[3/5] Migrating data...")
        tables = [
            User,      # Users first (referenced by sessions)
            Student,   # Students (referenced by sessions)
            Session,   # Sessions (references users and students)
            Event,     # Events (references sessions)
        ]
        
        total_rows = 0
        for model in tables:
            rows = await self.migrate_table(model)
            total_rows += rows
        
        # Step 4: Verify migration
        logger.info("\n[4/5] Verifying migration...")
        all_verified = True
        for model in tables:
            verified = await self.verify_migration(model)
            all_verified = all_verified and verified
        
        # Step 5: Summary
        logger.info("\n[5/5] Migration Summary")
        logger.info("=" * 60)
        logger.info(f"Total rows migrated: {total_rows}")
        logger.info(f"Verification status: {'PASSED' if all_verified else 'FAILED'}")
        logger.info("=" * 60)
        
        if all_verified:
            logger.info("\n[OK] Migration completed successfully!")
            logger.info("\nNext steps:")
            logger.info("1. Update .env to use PostgreSQL DATABASE_URL")
            logger.info("2. Restart backend with production configuration")
            logger.info("3. Test application functionality")
            return True
        else:
            logger.warning("\n⚠ Migration completed with warnings")
            logger.warning("Please review the verification results above")
            return False
    
    async def cleanup(self):
        """Close database connections"""
        await self.sqlite_engine.dispose()
        await self.postgres_engine.dispose()


async def main():
    """Main migration entry point"""
    # Get database URLs from command line or environment
    sqlite_url = os.getenv(
        "SOURCE_DATABASE_URL",
        "sqlite+aiosqlite:///./agent_aura_local.db"
    )
    
    postgres_url = os.getenv(
        "TARGET_DATABASE_URL",
        os.getenv("DATABASE_URL", "postgresql+asyncpg://agent_aura_user:password@localhost:5432/agent_aura_prod")
    )
    
    # Create migrator
    migrator = DatabaseMigrator(sqlite_url, postgres_url)
    
    try:
        # Run migration
        success = await migrator.migrate_all()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Migration failed with error: {e}")
        sys.exit(1)
    finally:
        await migrator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
