import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Obtener URL desde settings o desde las variables de entorno de Render
db_url = getattr(settings, "DATABASE_URL", None) or os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Corrección imprescindible: Render envía 'postgres://', pero SQLAlchemy exige 'postgresql://'
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = db_url

if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print("✅ Conexión a PostgreSQL establecida con éxito.")
    except Exception as e:
        print(f"⚠️ Error conectando a PostgreSQL ({e}), usando SQLite de respaldo.")
        db_url = "sqlite:///./sql_app.db"
        SQLALCHEMY_DATABASE_URL = db_url
        engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()