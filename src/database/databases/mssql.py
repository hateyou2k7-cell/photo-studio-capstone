from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.databases.base import Base

# Database configuration
try:
    from config import Config
    DATABASE_URI = Config.DATABASE_URI
    engine = create_engine(DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
except Exception:
    engine = None
    session = None

def init_mssql(app):
    if engine:
        Base.metadata.create_all(bind=engine)