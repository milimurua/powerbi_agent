#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión y métodos de BigQuery
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.outbound.bigquery_client import BigQueryClient  # pyright: ignore[reportMissingImports]


def test_connection():
    """Prueba la conexión y los métodos del BigQueryClient"""
    print("=" * 60)
    print("TESTING BIGQUERY CLIENT")
    print("=" * 60)
    
    try:
        # Crear cliente
        print("\n1. Inicializando cliente BigQuery...")
        client = BigQueryClient()
        print("✅ Cliente inicializado correctamente")
        print(f"   Project: {client.client.project}")
        print(f"   Dataset: {client.dataset}")
        
        # Listar tablas
        print("\n2. Listando tablas en el dataset...")
        tables = client.get_tables()
        print(f"✅ Se encontraron {len(tables)} tablas:")
        for table in tables:
            print(f"   - {table}")
        
        # Obtener esquema de la primera tabla
        if tables:
            first_table = tables[0]
            print(f"\n3. Obteniendo esquema de '{first_table}'...")
            schema = client.get_table_schema(first_table)
            print(f"✅ Esquema obtenido ({len(schema)} columnas):")
            for field in schema[:5]:  # Mostrar solo las primeras 5
                print(f"   - {field['name']} ({field['type']}) - {field['mode']}")
            if len(schema) > 5:
                print(f"   ... y {len(schema) - 5} columnas más")
            
            # Ejecutar una query de prueba
            print(f"\n4. Ejecutando query de prueba (SELECT * LIMIT 3)...")
            query = f"SELECT * FROM `{client.client.project}.{client.dataset}.{first_table}` LIMIT 3"
            results = client.execute_query(query)
            print(f"✅ Query ejecutada exitosamente ({len(results)} filas)")
            
            if results:
                print("\n   Muestra de datos:")
                for i, row in enumerate(results, 1):
                    print(f"\n   Fila {i}:")
                    for key, value in list(row.items())[:3]:  # Primeras 3 columnas
                        print(f"     {key}: {value}")
            
            # Probar método run_query
            print(f"\n5. Probando método run_query()...")
            formatted_result = client.run_query(query)
            print("✅ Resultado formateado:")
            print(formatted_result[:500])  # Primeros 500 caracteres
        
        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(test_connection())
