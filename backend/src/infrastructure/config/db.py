from sqlalchemy import create_engine  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import sessionmaker, Session # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import declarative_base # pyright: ignore[reportMissingImports]
from src.infrastructure.config.settings import settings # pyright: ignore[reportMissingImports]

# Configurar engine con pool de conexiones para PostgreSQL
database_url = settings.get_database_url()
engine = create_engine(
    database_url,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=5,  # Tamaño del pool de conexiones
    max_overflow=10,  # Conexiones adicionales permitidas
    echo=False  # Cambiar a True para ver SQL queries en desarrollo
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db() -> Session:
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()