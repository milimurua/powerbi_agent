from google.cloud import bigquery
from google.oauth2 import service_account
from typing import List, Dict, Any
import os

from domain.repositories.analytics_repository import AnalyticsRepository
from infrastructure.config.settings import settings


class BigQueryClient(AnalyticsRepository):
    """Cliente para ejecutar consultas en BigQuery"""

    def __init__(self):
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

    def run_query(self, query: str) -> str:
        """
        Ejecuta una consulta SQL en BigQuery y retorna los resultados como string
        
        Args:
            query: Consulta SQL a ejecutar
            
        Returns:
            String con los resultados de la consulta
        """
        try:
            # Ejecutar la consulta
            query_job = self.client.query(query)
            results = query_job.result()
            
            # Convertir resultados a lista de diccionarios
            rows = [dict(row) for row in results]
            
            if not rows:
                return "No se encontraron resultados para la consulta."
            
            # Formatear resultados como string
            return self._format_results(rows)
            
        except Exception as e:
            return f"Error ejecutando consulta en BigQuery: {str(e)}"

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL en BigQuery y retorna los resultados como lista de diccionarios
        
        Args:
            query: Consulta SQL a ejecutar
            
        Returns:
            Lista de diccionarios con los resultados
        """
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            return [dict(row) for row in results]
        except Exception as e:
            raise Exception(f"Error ejecutando consulta en BigQuery: {str(e)}")

    def get_tables(self) -> List[str]:
        """
        Obtiene la lista de tablas disponibles en el dataset
        
        Returns:
            Lista de nombres de tablas
        """
        try:
            tables = self.client.list_tables(f"{settings.GCP_PROJECT_ID}.{self.dataset}")
            return [table.table_id for table in tables]
        except Exception as e:
            raise Exception(f"Error obteniendo tablas: {str(e)}")

    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """
        Obtiene el esquema de una tabla específica
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Lista de diccionarios con información de las columnas
        """
        try:
            table_ref = f"{settings.GCP_PROJECT_ID}.{self.dataset}.{table_name}"
            table = self.client.get_table(table_ref)
            
            schema_info = []
            for field in table.schema:
                schema_info.append({
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode
                })
            
            return schema_info
        except Exception as e:
            raise Exception(f"Error obteniendo esquema de {table_name}: {str(e)}")

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
