from google.cloud import bigquery
from google.oauth2 import service_account  # pyright: ignore[reportMissingImports]
from typing import List, Dict, Any, Optional
import os
import logging
import hashlib

from domain.repositories.analytics_repository import AnalyticsRepository
from domain.repositories.cache_repository import CacheRepository
from infrastructure.config.settings import settings


logger = logging.getLogger(__name__)


class BigQueryClient(AnalyticsRepository):
  
    
    _instance = None
    
    def __new__(cls, cache: Optional[CacheRepository] = None):
        """Singleton pattern para reutilizar la conexión"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, cache: Optional[CacheRepository] = None):
        """
        Inicializa el cliente de BigQuery (solo la primera vez)
        
        Args:
            cache: Repositorio de caché opcional (se inicializa automáticamente si no se provee)
        """
        # Solo inicializar una vez
        if self._initialized:
            return
        
        # Configurar caché
        if cache is None:
            try:
                from infrastructure.outbound.redis_cache import RedisCache
                self.cache = RedisCache()
            except Exception as e:
                logger.warning(f"No se pudo inicializar caché: {e}")
                self.cache = None
        else:
            self.cache = cache
        
        # Configurar credenciales si están disponibles
        credentials = None
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            if os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                credentials = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_APPLICATION_CREDENTIALS
                )
        
        # Inicializar cliente de BigQuery
        self.client = bigquery.Client(
            project=settings.GCP_PROJECT_ID,
            credentials=credentials
        )
        self.dataset = settings.BIGQUERY_DATASET
        
        self._initialized = True
        logger.info(f"✅ BigQueryClient inicializado - Project: {settings.GCP_PROJECT_ID}, Dataset: {self.dataset}")

    def run_query(self, query: str, use_cache: bool = False) -> str:
        """
        Ejecuta una consulta SQL en BigQuery y retorna los resultados como string
        
        Args:
            query: Consulta SQL a ejecutar
            use_cache: Si True, cachea los resultados de la query
            
        Returns:
            String con los resultados de la consulta
        """
        try:
            # Verificar caché si está habilitado
            if use_cache and self.cache:
                cache_key = self._get_query_cache_key(query)
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    logger.info(f"📦 Resultado obtenido del caché")
                    return cached_result
            
            # Validar query básica
            self._validate_query(query)
            
            # Ejecutar la consulta
            logger.info(f"🔍 Ejecutando query en BigQuery...")
            query_job = self.client.query(query)
            results = query_job.result()
            
            # Convertir resultados a lista de diccionarios
            rows = [dict(row) for row in results]
            
            if not rows:
                return "No se encontraron resultados para la consulta."
            
            # Formatear resultados como string
            formatted_result = self._format_results(rows)
            
            # Guardar en caché si está habilitado
            if use_cache and self.cache:
                cache_key = self._get_query_cache_key(query)
                self.cache.set(cache_key, formatted_result, ttl=300)  # 5 minutos
            
            logger.info(f"✅ Query ejecutada exitosamente - {len(rows)} filas")
            return formatted_result
            
        except Exception as e:
            error_msg = f"Error ejecutando consulta en BigQuery: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def execute_query(self, query: str, max_results: int = 1000) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL en BigQuery y retorna los resultados como lista de diccionarios
        
        Args:
            query: Consulta SQL a ejecutar
            max_results: Número máximo de resultados a retornar (seguridad)
            
        Returns:
            Lista de diccionarios con los resultados
        """
        try:
            # Validar query básica
            self._validate_query(query)
            
            logger.info(f"🔍 Ejecutando query en BigQuery (max {max_results} resultados)...")
            query_job = self.client.query(query)
            results = query_job.result(max_results=max_results)
            
            rows = [dict(row) for row in results]
            logger.info(f"✅ Query ejecutada - {len(rows)} filas retornadas")
            return rows
        except Exception as e:
            error_msg = f"Error ejecutando consulta en BigQuery: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_tables(self, use_cache: bool = True) -> List[str]:
        """
        Obtiene la lista de tablas disponibles en el dataset
        
        Args:
            use_cache: Si True, usa caché para la lista de tablas
        
        Returns:
            Lista de nombres de tablas
        """
        try:
            # Verificar caché
            cache_key = f"bigquery:tables:{self.dataset}"
            if use_cache and self.cache:
                cached_tables = self.cache.get(cache_key)
                if cached_tables:
                    logger.info(f"📦 Lista de tablas obtenida del caché")
                    return cached_tables
            
            logger.info(f"🔍 Obteniendo tablas del dataset {self.dataset}...")
            tables = self.client.list_tables(f"{settings.GCP_PROJECT_ID}.{self.dataset}")
            table_list = [table.table_id for table in tables]
            
            # Guardar en caché
            if use_cache and self.cache:
                self.cache.set(cache_key, table_list, ttl=1800)  # 30 minutos
            
            logger.info(f"✅ Encontradas {len(table_list)} tablas")
            return table_list
        except Exception as e:
            error_msg = f"Error obteniendo tablas: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_table_schema(self, table_name: str, use_cache: bool = True) -> List[Dict[str, str]]:
        """
        Obtiene el esquema de una tabla específica
        
        Args:
            table_name: Nombre de la tabla
            use_cache: Si True, usa caché para el esquema
            
        Returns:
            Lista de diccionarios con información de las columnas
        """
        try:
            # Verificar caché
            cache_key = f"bigquery:schema:{self.dataset}:{table_name}"
            if use_cache and self.cache:
                cached_schema = self.cache.get(cache_key)
                if cached_schema:
                    logger.info(f"📦 Esquema de '{table_name}' obtenido del caché")
                    return cached_schema
            
            logger.info(f"🔍 Obteniendo esquema de tabla {table_name}...")
            table_ref = f"{settings.GCP_PROJECT_ID}.{self.dataset}.{table_name}"
            table = self.client.get_table(table_ref)
            
            schema_info = []
            for field in table.schema:
                schema_info.append({
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or ""
                })
            
            # Guardar en caché
            if use_cache and self.cache:
                self.cache.set(cache_key, schema_info, ttl=3600)  # 1 hora
            
            logger.info(f"✅ Esquema obtenido - {len(schema_info)} columnas")
            return schema_info
        except Exception as e:
            error_msg = f"Error obteniendo esquema de {table_name}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _format_results(self, rows: List[Dict[str, Any]]) -> str:
        """
        Formatea los resultados de una consulta como string legible
        
        Args:
            rows: Lista de diccionarios con los resultados
            
        Returns:
            String formateado con los resultados
        """
        if not rows:
            return "No hay resultados."
        
        # Limitar a 10 filas para no saturar el contexto
        limited_rows = rows[:10]
        result = f"Resultados ({len(rows)} filas total, mostrando {len(limited_rows)}):\n\n"
        
        for i, row in enumerate(limited_rows, 1):
            result += f"Fila {i}:\n"
            for key, value in row.items():
                result += f"  {key}: {value}\n"
            result += "\n"
        
        return result
    
    def _validate_query(self, query: str) -> None:
        """
        Valida básicamente una query SQL antes de ejecutarla
        
        Args:
            query: Query SQL a validar
            
        Raises:
            ValueError: Si la query no pasa las validaciones
        """
        if not query or not query.strip():
            raise ValueError("La query no puede estar vacía")
        
        query_lower = query.lower().strip()
        
        # Verificar que sea una query SELECT (seguridad básica)
        if not query_lower.startswith('select') and not query_lower.startswith('with'):
            logger.warning(f"⚠️  Query no es SELECT: {query_lower[:50]}")
            # No lanzar error, solo advertir
        
        # Palabras prohibidas (comandos destructivos)
        forbidden_keywords = ['drop', 'delete', 'truncate', 'insert', 'update', 'alter', 'create']
        for keyword in forbidden_keywords:
            if f' {keyword} ' in f' {query_lower} ':
                raise ValueError(f"Query contiene comando prohibido: {keyword.upper()}")
        
        logger.debug("✅ Query validada")
    
    def _get_query_cache_key(self, query: str) -> str:
        """
        Genera una clave de caché única para una query
        
        Args:
            query: Query SQL
            
        Returns:
            Clave de caché
        """
        # Normalizar query (remover espacios extra, minúsculas)
        normalized = ' '.join(query.lower().split())
        # Hash MD5 de la query
        query_hash = hashlib.md5(normalized.encode()).hexdigest()
        return f"bigquery:query:{query_hash}"
    
    def clear_cache(self, pattern: str = "bigquery:*") -> None:
        """
        Limpia el caché de BigQuery
        
        Args:
            pattern: Patrón de claves a eliminar
        """
        if self.cache:
            self.cache.clear_pattern(pattern)
            logger.info(f"🗑️  Caché limpiado: {pattern}")
    
    def get_table_preview(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Obtiene una vista previa de los datos de una tabla
        
        Args:
            table_name: Nombre de la tabla
            limit: Número de filas a obtener
            
        Returns:
            Lista de diccionarios con los datos
        """
        query = f"SELECT * FROM `{self.client.project}.{self.dataset}.{table_name}` LIMIT {limit}"
        return self.execute_query(query, max_results=limit)
