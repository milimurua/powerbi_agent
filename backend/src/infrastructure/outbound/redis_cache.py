import redis
import json
import logging
from typing import Optional, Any

from domain.repositories.cache_repository import CacheRepository
from infrastructure.config.settings import settings


logger = logging.getLogger(__name__)


class RedisCache(CacheRepository):
    """Implementación de caché usando Redis"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern para reutilizar la conexión a Redis"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa la conexión a Redis"""
        if self._initialized:
            return
            
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Verificar conexión
            self.client.ping()
            self._initialized = True
            logger.info(f"✅ Conexión a Redis establecida: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.warning(f"⚠️  No se pudo conectar a Redis: {e}. Usando caché en memoria.")
            self.client = None
            self._initialized = True
            # Fallback a diccionario en memoria
            self._memory_cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché
        
        Args:
            key: Clave del elemento a obtener
            
        Returns:
            Valor almacenado o None si no existe
        """
        try:
            if self.client:
                value = self.client.get(key)
                if value:
                    # Intentar deserializar JSON
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                return None
            else:
                # Fallback a memoria
                return self._memory_cache.get(key)
        except Exception as e:
            logger.error(f"Error obteniendo clave '{key}' del caché: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Guarda un valor en el caché
        
        Args:
            key: Clave bajo la cual guardar el valor
            value: Valor a guardar
            ttl: Tiempo de vida en segundos (opcional, default: 3600 = 1 hora)
        """
        try:
            # Serializar a JSON si no es string
            if not isinstance(value, str):
                value = json.dumps(value, default=str)
            
            if self.client:
                if ttl is None:
                    ttl = 3600  # 1 hora por defecto
                self.client.setex(key, ttl, value)
            else:
                # Fallback a memoria (sin TTL)
                self._memory_cache[key] = value
                
            logger.debug(f"✅ Guardado en caché: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Error guardando clave '{key}' en caché: {e}")
    
    def delete(self, key: str) -> None:
        """
        Elimina un valor del caché
        
        Args:
            key: Clave del elemento a eliminar
        """
        try:
            if self.client:
                self.client.delete(key)
            else:
                self._memory_cache.pop(key, None)
            logger.debug(f"  Eliminado del caché: {key}")
        except Exception as e:
            logger.error(f"Error eliminando clave '{key}' del caché: {e}")
    
    def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe en el caché
        
        Args:
            key: Clave a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        try:
            if self.client:
                return bool(self.client.exists(key))
            else:
                return key in self._memory_cache
        except Exception as e:
            logger.error(f"Error verificando existencia de '{key}': {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> None:
        """
        Elimina todas las claves que coincidan con un patrón
        
        Args:
            pattern: Patrón para buscar claves (ej: "bigquery:*")
        """
        try:
            if self.client:
                cursor = 0
                while True:
                    cursor, keys = self.client.scan(cursor, match=pattern, count=100)
                    if keys:
                        self.client.delete(*keys)
                    if cursor == 0:
                        break
                logger.info(f"🗑️  Limpiado caché con patrón: {pattern}")
            else:
                # Fallback a memoria
                keys_to_delete = [k for k in self._memory_cache.keys() if pattern.replace('*', '') in k]
                for key in keys_to_delete:
                    del self._memory_cache[key]
        except Exception as e:
            logger.error(f"Error limpiando patrón '{pattern}': {e}")
