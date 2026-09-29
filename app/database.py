import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL
SQLALCHEMY_DATABASE_URL = db_url

if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            pass
    except Exception as e:
        print(f"Base de datos PostgreSQL no disponible ({e}), usando SQLite.")
        db_url = "sqlite:///./sql_app.db"
        SQLALCHEMY_DATABASE_URL = db_url
        engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

