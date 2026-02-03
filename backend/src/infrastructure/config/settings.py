import os
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
    BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "")
    # PostgreSQL connection URL: postgresql+psycopg://user:password@host:port/database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://agent:agent@localhost:5432/agentdb")
    
    # PostgreSQL settings from environment
    POSTGRES_USER = os.getenv("POSTGRES_USER", "agent")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "agent")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "agentdb")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    
    def get_database_url(self) -> str:
        """Construye la URL de conexión a la base de datos"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
