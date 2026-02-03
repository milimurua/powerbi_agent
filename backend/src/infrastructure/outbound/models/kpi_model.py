from sqlalchemy import String, Text  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Mapped, mapped_column # pyright: ignore[reportMissingImports]
from src.infrastructure.config.db import Base # pyright: ignore[reportMissingImports]

class KPIModel(Base):
    """Modelo SQLAlchemy para la tabla kpis (capa de infraestructura)"""
    __tablename__ = "kpis"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sql_template: Mapped[str] = mapped_column(Text, nullable=False)

    owner: Mapped[str] = mapped_column(String(20), nullable=False)   # system/user
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # active/proposed/inactive
