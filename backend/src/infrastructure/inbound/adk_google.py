from google.adk.agents import LlmAgent  # pyright: ignore
from google.adk.models import Gemini  # pyright: ignore

from infrastructure.inbound.tools.big_query_tools import (  # pyright: ignore[reportMissingImports]
    query_bigquery,
    get_available_tables,
    get_table_info,
    get_table_preview,
    ask_data_question,
    explain_sql_query,
    optimize_sql_query
)

def create_agent():
    return LlmAgent(
        name="powerbi_agent",
        model=Gemini(model="gemini-2.5-flash"),
        description="""An advanced analytics agent that can query BigQuery data warehouse to answer business questions.
        
        Capabilities:
        - Answer data questions in natural language (generates and executes SQL automatically)
        - Execute custom SQL queries
        - Explore available tables and their schemas
        - Preview table data
        - Explain SQL queries in business language
        - Optimize SQL queries for better performance
        """,
        tools=[
            # Herramienta principal: responder preguntas con AI
            ask_data_question,
            
            # Exploración de datos
            get_available_tables,
            get_table_info,
            get_table_preview,
            
            # Ejecución y optimización de SQL
            query_bigquery,
            explain_sql_query,
            optimize_sql_query
        ]
    )

root_agent = create_agent()
