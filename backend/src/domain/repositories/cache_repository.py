from abc import ABC, abstractmethod
from typing import Optional, Any

class CacheRepository(ABC):
    """Repositorio abstracto para operaciones de caché"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché
        
        Args:
            key: Clave del elemento a obtener
            
        Returns:
            Valor almacenado o None si no existe
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Guarda un valor en el caché
        
        Args:
            key: Clave bajo la cual guardar el valor
            value: Valor a guardar
            ttl: Tiempo de vida en segundos (opcional)
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Elimina un valor del caché
        
        Args:
            key: Clave del elemento a eliminar
        """
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe en el caché
        
        Args:
            key: Clave a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        pass
    
    @abstractmethod
    def clear_pattern(self, pattern: str) -> None:
        """
        Elimina todas las claves que coincidan con un patrón
        
        Args:
            pattern: Patrón para buscar claves (ej: "bigquery:*")
        """
        pass