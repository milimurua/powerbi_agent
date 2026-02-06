import logging
from typing import List, Dict, Any, Optional

from infrastructure.outbound.gemini_client import GeminiClient
from infrastructure.outbound.bigquery_client import BigQueryClient


logger = logging.getLogger(__name__)


class SQLGeneratorService:
    """Servicio para generar y ejecutar queries SQL con ayuda de Gemini"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.bq_client = BigQueryClient()
    
    def generate_sql(
        self, 
        question: str, 
        table_schemas: Optional[Dict[str, List[Dict[str, str]]]] = None
    ) -> str:
        """
        Genera una query SQL a partir de una pregunta en lenguaje natural
        
        Args:
            question: Pregunta del usuario en lenguaje natural
            table_schemas: Esquemas de las tablas disponibles (opcional)
            
        Returns:
            Query SQL generada
        """
        # Obtener esquemas si no se proporcionan
        if table_schemas is None:
            table_schemas = self._get_all_schemas()
        
        # Construir prompt para Gemini
        prompt = self._build_sql_generation_prompt(question, table_schemas)
        
        # Generar SQL con Gemini
        logger.info(f"🤖 Generando SQL para: {question}")
        sql_response = self.gemini_client.run_query(prompt)
        
        # Extraer solo el SQL (remover markdown si existe)
        sql = self._extract_sql_from_response(sql_response)
        
        logger.info(f"✅ SQL generado: {sql[:100]}...")
        return sql
    
    def generate_and_execute(
        self, 
        question: str,
        return_format: str = "formatted"
    ) -> str:
        """
        Genera una query SQL y la ejecuta, retornando los resultados
        
        Args:
            question: Pregunta del usuario en lenguaje natural
            return_format: Formato de retorno ("formatted", "json", "raw")
            
        Returns:
            Resultados de la query en el formato especificado
        """
        try:
            # Generar SQL
            sql = self.generate_sql(question)
            
            # Ejecutar query
            logger.info(f"🔍 Ejecutando query generada...")
            
            if return_format == "json":
                results = self.bq_client.execute_query(sql)
                return str(results)
            else:
                results = self.bq_client.run_query(sql)
                return results
                
        except Exception as e:
            error_msg = f"Error generando/ejecutando query: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def explain_sql(self, sql: str) -> str:
        """
        Explica qué hace una query SQL en lenguaje natural
        
        Args:
            sql: Query SQL a explicar
            
        Returns:
            Explicación en lenguaje natural
        """
        prompt = f"""Eres un experto en SQL y análisis de datos.
        
Explica en lenguaje natural y en español qué hace esta query SQL:

```sql
{sql}
```

Proporciona una explicación clara y concisa que un usuario de negocio pueda entender.
No uses términos técnicos complejos. Enfócate en QUÉ datos obtiene y PARA QUÉ sirve."""

        explanation = self.gemini_client.run_query(prompt)
        return explanation
    
    def optimize_sql(self, sql: str) -> str:
        """
        Optimiza una query SQL para mejor rendimiento
        
        Args:
            sql: Query SQL a optimizar
            
        Returns:
            Query SQL optimizada
        """
        prompt = f"""Eres un experto en optimización de queries SQL para BigQuery.

Optimiza esta query SQL para mejor rendimiento en BigQuery:

```sql
{sql}
```

Reglas:
1. Usa particiones si están disponibles
2. Evita SELECT *
3. Filtra lo antes posible
4. Usa agregaciones eficientes
5. Evita JOINs innecesarios

Retorna SOLO la query optimizada en formato SQL, sin explicaciones."""

        optimized = self.gemini_client.run_query(prompt)
        return self._extract_sql_from_response(optimized)
    
    def _get_all_schemas(self) -> Dict[str, List[Dict[str, str]]]:
        """Obtiene los esquemas de todas las tablas disponibles"""
        schemas = {}
        try:
            tables = self.bq_client.get_tables()
            
            # Validar que tables es una lista
            if not isinstance(tables, list):
                logger.error(f"⚠️  get_tables() retornó {type(tables)} en vez de list: {tables}")
                if isinstance(tables, str):
                    # Si es un string, convertirlo a lista con un solo elemento
                    tables = [tables]
                else:
                    return schemas
            
            logger.info(f"📋 Obteniendo esquemas de {len(tables)} tablas")
            
            for table in tables:
                # Validar que cada tabla es un string
                if not isinstance(table, str):
                    logger.warning(f"⚠️  Saltando tabla inválida (tipo {type(table)}): {table}")
                    continue
                    
                try:
                    schema = self.bq_client.get_table_schema(table)
                    schemas[table] = schema
                except Exception as e:
                    logger.warning(f"No se pudo obtener esquema de {table}: {e}")
        except Exception as e:
            logger.error(f"Error obteniendo esquemas: {e}")
        
        return schemas
    
    def _build_sql_generation_prompt(
        self, 
        question: str, 
        table_schemas: Dict[str, List[Dict[str, str]]]
    ) -> str:
        """Construye el prompt para que Gemini genere SQL"""
        
        # Formatear información de esquemas
        schema_info = "Tablas disponibles:\n\n"
        for table_name, schema in table_schemas.items():
            schema_info += f"Tabla: `{self.bq_client.dataset}.{table_name}`\n"
            schema_info += "Columnas:\n"
            for field in schema:
                schema_info += f"  - {field['name']} ({field['type']}) - {field.get('mode', 'NULLABLE')}\n"
            schema_info += "\n"
        
        prompt = f"""Eres un experto en SQL y BigQuery que ayuda a analistas de datos.

{schema_info}

Genera una query SQL válida para BigQuery que responda a esta pregunta:
"{question}"

Reglas IMPORTANTES:
1. Usa el formato completo: `{self.bq_client.client.project}.{self.bq_client.dataset}.tabla_name`
2. Retorna SOLO la query SQL, sin explicaciones
3. No uses markdown (```)
4. La query debe ser eficiente y correcta
5. Usa LIMIT 100 por defecto para no sobrecargar
6. Comenta solo si es necesario para claridad

SQL Query:"""

        return prompt
    
    def _extract_sql_from_response(self, response: str) -> str:
        """Extrae el SQL puro de la respuesta de Gemini"""
        # Remover bloques de markdown si existen
        if "```sql" in response:
            sql = response.split("```sql")[1].split("```")[0].strip()
        elif "```" in response:
            sql = response.split("```")[1].split("```")[0].strip()
        else:
            sql = response.strip()
        
        # Remover posibles prefijos
        sql = sql.replace("SQL Query:", "").strip()
        
        return sql
