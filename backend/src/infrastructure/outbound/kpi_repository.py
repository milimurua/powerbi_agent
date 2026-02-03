from typing import Optional, List
from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]
from sqlalchemy import select  # pyright: ignore[reportMissingImports]

from src.domain.entities.kpi import KPI
from src.domain.repositories.kpi_repository import KPIRepository
from src.infrastructure.outbound.models.kpi_model import KPIModel


class SQLAlchemyKPIRepository(KPIRepository):
    """Implementación del repositorio de KPI usando SQLAlchemy (capa de infraestructura)"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def _model_to_entity(self, model: KPIModel) -> KPI:
        """Convierte un modelo SQLAlchemy a una entidad de dominio"""
        return KPI(
            id=model.id,
            name=model.name,
            description=model.description,
            sql_template=model.sql_template,
            owner=model.owner,  # type: ignore
            status=model.status  # type: ignore
        )
    
    def _entity_to_model(self, entity: KPI) -> KPIModel:
        """Convierte una entidad de dominio a un modelo SQLAlchemy"""
        return KPIModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            sql_template=entity.sql_template,
            owner=entity.owner,
            status=entity.status
        )
    
    def find_by_id(self, kpi_id: str) -> Optional[KPI]:
        """Busca un KPI por su ID"""
        stmt = select(KPIModel).where(KPIModel.id == kpi_id)
        model = self.session.scalar(stmt)
        return self._model_to_entity(model) if model else None
    
    def find_all(self) -> List[KPI]:
        """Obtiene todos los KPIs"""
        stmt = select(KPIModel)
        models = self.session.scalars(stmt).all()
        return [self._model_to_entity(model) for model in models]
    
    def find_by_status(self, status: str) -> List[KPI]:
        """Busca KPIs por estado"""
        stmt = select(KPIModel).where(KPIModel.status == status)
        models = self.session.scalars(stmt).all()
        return [self._model_to_entity(model) for model in models]
    
    def find_active(self) -> List[KPI]:
        """Obtiene todos los KPIs activos"""
        return self.find_by_status("active")
    
    def save(self, kpi: KPI) -> KPI:
        """Guarda o actualiza un KPI"""
        stmt = select(KPIModel).where(KPIModel.id == kpi.id)
        model = self.session.scalar(stmt)
        
        if model:
            # Actualizar modelo existente
            model.name = kpi.name
            model.description = kpi.description
            model.sql_template = kpi.sql_template
            model.owner = kpi.owner
            model.status = kpi.status
        else:
            # Crear nuevo modelo
            model = self._entity_to_model(kpi)
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    def delete(self, kpi_id: str) -> bool:
        """Elimina un KPI por su ID"""
        stmt = select(KPIModel).where(KPIModel.id == kpi_id)
        model = self.session.scalar(stmt)
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

