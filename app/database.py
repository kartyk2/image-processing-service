from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

DATABASE_URL = settings.database_url.unicode_string()

engine = create_engine(DATABASE_URL, pool_size=25, max_overflow=10, pool_recycle=300, pool_pre_ping=True,  pool_use_lifo=True)
SessionLocal = sessionmaker(bind=engine)
 
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ConnectionManager:
    def __init__(self, url) -> None:
        self.engine = SessionLocal()

    def __enter__(self):
        return self.engine
        
    def __exit__(self, exc_type, exc_value, tb):
        self.engine.close()