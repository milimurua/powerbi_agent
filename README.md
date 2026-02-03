# powerbi_agent


## Ingesta de datos 
El agente soporta la ingesta de datos desde múltiples orígenes.

Uno de los casos de uso documentados es la carga de archivos Excel con múltiples hojas en BigQuery. En este escenario, cada hoja se transforma en un CSV, se genera automáticamente el esquema y se crea una tabla independiente en BigQuery.

La documentación específica de este flujo se encuentra en `docs/excel-to-bigquery.md`.
