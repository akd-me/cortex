import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator

from ..models.context import Base

# Database configuration
# Use environment variable for database path, fallback to default
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.expanduser("~/.cortex"), "context.db"))
DATABASE_DIR = os.path.dirname(DATABASE_PATH)

# Ensure the database directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)

# Create SQLite engine with proper configuration for Electron app
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Allow multithreading
    },
    poolclass=StaticPool,
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """Initialize the database with tables"""
    create_tables()
    print(f"Database initialized at: {DATABASE_PATH}")

# Initialize database on import
init_database()
