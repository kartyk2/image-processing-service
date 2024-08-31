from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

# Database URL from settings
DATABASE_URL = settings.database_url.unicode_string()

# Create a reusable database engine for global usage
engine = create_engine(
    DATABASE_URL,
    pool_size=25,
    max_overflow=10,
    pool_recycle=300,
    pool_pre_ping=True,
    pool_use_lifo=True
)

# Create a configured "SessionLocal" class for the global engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Dependency for FastAPI to get a database session
def get_db():
    """Dependency that provides a database session."""
    db:Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConnectionManager:
    """
    Context manager to handle the creation and cleanup of a SQLAlchemy session.
    Useful for operations that require a dedicated session with a specific DB URL.
    """
    def __init__(self, url: str = DATABASE_URL):
        self.url = url
        # Create an engine specific to the provided URL
        self.engine = create_engine(self.url, pool_pre_ping=True)
        # Create a sessionmaker bound to the new engine
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = None

    def __enter__(self) -> Session:
        """Create and return a new session when entering the context."""
        self.session = self.Session()
        return self.session

    def __exit__(self, exc_type, exc_value, tb):
        """Close the session when exiting the context."""
        if self.session:
            self.session.close()
