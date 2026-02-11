"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
import sys

# Handle imports for both module and direct execution
try:
    from .models import Base
    from ..config import DATABASE_URL
except ImportError:
    # Fallback for when running as script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database.models import Base
    from config import DATABASE_URL

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(engine)


def get_session():
    """Get database session"""
    return Session()


def close_session():
    """Close database session"""
    Session.remove()
