from infrastructure.outbound.bigquery_client import BigQueryClient


def query_bigquery(sql_query: str) -> str:
    """
    Execute a SQL query in BigQuery and return formatted results.
    
    Args:
        sql_query: The SQL query to execute in BigQuery
        
    Returns:
        Formatted results from the query
    """
    client = BigQueryClient()
    return client.run_query(sql_query)


def get_available_tables() -> str:
    """
    Get the list of available tables in the BigQuery dataset.
    
    Returns:
        List of available tables
    """
    client = BigQueryClient()
    tables = client.get_tables()
    return f"Available tables: {', '.join(tables)}"


def get_table_info(table_name: str) -> str:
    """
    Get schema information for a specific table in BigQuery.
    
    Args:
        table_name: The name of the table to get schema for
        
    Returns:
        Schema information including column names, types, and modes
    """
    client = BigQueryClient()
    schema = client.get_table_schema(table_name)
    
    result = f"Schema for table '{table_name}':\n\n"
    for field in schema:
        result += f"- {field['name']} ({field['type']}) - {field['mode']}"
        if field.get('description'):
            result += f" - {field['description']}"
        result += "\n"
    
    return result