import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, engine_from_config, pool  # pyright: ignore[reportMissingImports]
from alembic import context

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importar Base y todos los modelos para que Alembic los detecte
from src.infrastructure.config.db import Base
from src.infrastructure.outbound.models.kpi_model import KPIModel

# Importar settings para obtener la URL de la base de datos
from src.infrastructure.config.settings import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url() -> str:
    """Obtiene la URL de conexión a la base de datos desde settings"""
    url = settings.get_database_url()
    if not url:
        raise RuntimeError("DATABASE_URL not set in environment or settings")
    return url

def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo offline (sin conexión activa)"""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo online (con conexión activa)"""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
