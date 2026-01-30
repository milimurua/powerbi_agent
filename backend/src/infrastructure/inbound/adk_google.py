from google.adk.agents import LlmAgent  # pyright: ignore
from google.adk.models import Gemini  # pyright: ignore

from infrastructure.inbound.tools.big_query_tools import (  # pyright: ignore[reportMissingImports]
    query_bigquery,
    get_available_tables,
    get_table_info
)

def create_agent():
    return LlmAgent(
        name="powerbi_agent",
        model=Gemini(model="gemini-2.5-flash"),
        description="An analytics agent that can query BigQuery data warehouse to answer questions about business data.",
        tools=[
            query_bigquery,
            get_available_tables,
            get_table_info
        ]
    )

root_agent = create_agent()
