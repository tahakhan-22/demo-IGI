"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from ..config import DATABASE_URL
from .models import Base

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
