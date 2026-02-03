from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.kpi import KPI

class KPIRepository(ABC):
    """Interfaz del repositorio de KPI (capa de dominio)"""
    
    @abstractmethod
    def find_by_id(self, kpi_id: str) -> Optional[KPI]:
        """Busca un KPI por su ID"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[KPI]:
        """Obtiene todos los KPIs"""
        pass
    
    @abstractmethod
    def find_by_status(self, status: str) -> List[KPI]:
        """Busca KPIs por estado"""
        pass
    
    @abstractmethod
    def find_active(self) -> List[KPI]:
        """Obtiene todos los KPIs activos"""
        pass
    
    @abstractmethod
    def save(self, kpi: KPI) -> KPI:
        """Guarda o actualiza un KPI"""
        pass
    
    @abstractmethod
    def delete(self, kpi_id: str) -> bool:
        """Elimina un KPI por su ID"""
        pass

