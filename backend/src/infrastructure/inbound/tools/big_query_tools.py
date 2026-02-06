from infrastructure.outbound.bigquery_client import BigQueryClient
from domain.services.sql_generator_service import SQLGeneratorService


# Cliente singleton compartido por todas las herramientas
_bq_client = None
_sql_generator = None


def _get_bq_client() -> BigQueryClient:
    """Obtiene la instancia singleton del cliente BigQuery"""
    global _bq_client
    if _bq_client is None:
        _bq_client = BigQueryClient()
    return _bq_client


def _get_sql_generator() -> SQLGeneratorService:
    """Obtiene la instancia singleton del generador SQL"""
    global _sql_generator
    if _sql_generator is None:
        _sql_generator = SQLGeneratorService()
    return _sql_generator


def query_bigquery(sql_query: str, use_cache: bool = False) -> str:
    """
    Ejecuta una consulta SQL en BigQuery y retorna los resultados formateados.
    
    Args:
        sql_query: La consulta SQL a ejecutar en BigQuery
        use_cache: Si es True, cachea los resultados para llamadas posteriores
        
    Returns:
        Resultados formateados de la consulta
    """
    client = _get_bq_client()
    return client.run_query(sql_query, use_cache=use_cache)


def get_available_tables() -> str:
    """
    Obtiene la lista de tablas disponibles en el dataset de BigQuery.
    
    Returns:
        Lista de tablas disponibles
    """
    client = _get_bq_client()
    tables = client.get_tables(use_cache=True)
    
    if not tables:
        return "No se encontraron tablas en el dataset."
    
    result = f"Tablas disponibles en el dataset ({len(tables)} total):\n\n"
    for table in tables:
        result += f"- {table}\n"
    
    return result


def get_table_info(table_name: str) -> str:
    """
    Obtiene información del esquema de una tabla específica en BigQuery.
    
    Args:
        table_name: El nombre de la tabla
        
    Returns:
        Información del esquema incluyendo nombres de columnas, tipos, modos y descripciones
    """
    # Validar que table_name es un string válido
    if not isinstance(table_name, str):
        return f"Error: table_name debe ser un string, recibido {type(table_name)}: {table_name}"
    
    if not table_name or not table_name.strip():
        return "Error: table_name no puede estar vacío"
    
    table_name = table_name.strip()
    
    client = _get_bq_client()
    
    try:
        schema = client.get_table_schema(table_name, use_cache=True)
        
        result = f"Esquema de la tabla '{table_name}':\n\n"
        for field in schema:
            result += f"- {field['name']} ({field['type']}) - {field['mode']}"
            if field.get('description'):
                result += f"\n  Descripción: {field['description']}"
            result += "\n"
        
        return result
    except Exception as e:
        return f"Error obteniendo esquema de tabla '{table_name}': {str(e)}"


def get_table_preview(table_name: str, rows: int = 5) -> str:
    """
    Obtiene una vista previa de los datos de una tabla específica.
    
    Args:
        table_name: El nombre de la tabla a previsualizar
        rows: Número de filas a mostrar (por defecto: 5, máximo: 10)
        
    Returns:
        Vista previa de los datos de la tabla
    """
    client = _get_bq_client()
    rows = min(rows, 10)  # Limitar a 10 filas máximo
    
    try:
        data = client.get_table_preview(table_name, limit=rows)
        
        if not data:
            return f"La tabla '{table_name}' está vacía."
        
        result = f"Vista previa de la tabla '{table_name}' (mostrando {len(data)} filas):\n\n"
        for i, row in enumerate(data, 1):
            result += f"Fila {i}:\n"
            for key, value in row.items():
                result += f"  {key}: {value}\n"
            result += "\n"
        
        return result
    except Exception as e:
        return f"Error obteniendo vista previa: {str(e)}"


def ask_data_question(question: str) -> str:
    """
    Hace una pregunta en lenguaje natural y obtiene insights de los datos.
    Esta herramienta genera una consulta SQL usando IA, la ejecuta y retorna los resultados.
    
    Args:
        question: Una pregunta de negocio en lenguaje natural (ej: "¿Cuáles fueron los top 5 productos por ventas?")
        
    Returns:
        Respuesta a la pregunta con datos de BigQuery
    """
    generator = _get_sql_generator()
    
    try:
        result = generator.generate_and_execute(question, return_format="formatted")
        return f"Pregunta: {question}\n\nRespuesta:\n{result}"
    except Exception as e:
        return f"Error respondiendo pregunta: {str(e)}"


def explain_sql_query(sql_query: str) -> str:
    """
    Explica qué hace una consulta SQL en lenguaje de negocio simple.
    
    Args:
        sql_query: La consulta SQL a explicar
        
    Returns:
        Explicación en lenguaje natural de la consulta
    """
    generator = _get_sql_generator()
    
    try:
        explanation = generator.explain_sql(sql_query)
        return f"Consulta SQL:\n{sql_query}\n\nExplicación:\n{explanation}"
    except Exception as e:
        return f"Error explicando consulta: {str(e)}"


def optimize_sql_query(sql_query: str) -> str:
    """
    Optimiza una consulta SQL para mejor rendimiento en BigQuery.
    
    Args:
        sql_query: La consulta SQL a optimizar
        
    Returns:
        Versión optimizada de la consulta con mejoras
    """
    generator = _get_sql_generator()
    
    try:
        optimized = generator.optimize_sql(sql_query)
        return f"Consulta Original:\n{sql_query}\n\nConsulta Optimizada:\n{optimized}"
    except Exception as e:
        return f"Error optimizando consulta: {str(e)}"
