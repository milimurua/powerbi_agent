from typing import List, Optional
from src.domain.entities.kpi import KPI
from src.domain.repositories.kpi_repository import KPIRepository


class KpiService:
    """Servicio de dominio para lógica de negocio de KPIs"""
    
    def __init__(self, kpi_repository: KPIRepository):
        self.kpi_repository = kpi_repository
    
    def get_active_kpis(self) -> List[KPI]:
        """Obtiene todos los KPIs activos"""
        return self.kpi_repository.find_active()
    
    def propose_kpis(self, question: str) -> List[KPI]:
        """Propone KPIs basados en una pregunta (lógica de negocio)"""
        # TODO: Implementar lógica de negocio para proponer KPIs
        return self.kpi_repository.find_by_status("proposed")
    
    def activate_kpi(self, kpi_id: str) -> Optional[KPI]:
        """Activa un KPI cambiando su estado a 'active'"""
        kpi = self.kpi_repository.find_by_id(kpi_id)
        if kpi:
            # Crear nueva instancia con estado activo (KPI es inmutable)
            activated_kpi = KPI(
                id=kpi.id,
                name=kpi.name,
                description=kpi.description,
                sql_template=kpi.sql_template,
                owner=kpi.owner,
                status="active"
            )
            return self.kpi_repository.save(activated_kpi)
        return None