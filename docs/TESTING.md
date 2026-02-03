# Guía de Pruebas - PostgreSQL + SQLAlchemy + Alembic

Esta guía te ayudará a probar que la configuración de PostgreSQL con SQLAlchemy y Alembic funciona correctamente.

## Prerrequisitos

1. **PostgreSQL corriendo**:
   - Localmente instalado, o
   - Usando Docker Compose

2. **Variables de entorno configuradas**:
   - Archivo `.env` en `backend/` con las credenciales de PostgreSQL

## Opción 1: Probar con Docker Compose (Recomendado)

### Paso 1: Iniciar los servicios

```bash
# Desde la raíz del proyecto
docker-compose up -d postgres
```

Espera unos segundos a que PostgreSQL esté listo. Verifica con:

```bash
docker ps
```

### Paso 2: Configurar variables de entorno

Crea o edita `backend/.env`:

```env
POSTGRES_USER=agent
POSTGRES_PASSWORD=agent
POSTGRES_DB=agentdb
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://agent:agent@postgres:5432/agentdb
```

### Paso 3: Crear las migraciones

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
```

Esto creará un archivo en `alembic/versions/` con la migración.

### Paso 4: Aplicar las migraciones

```bash
alembic upgrade head
```

Deberías ver algo como:
```
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, Initial migration
```

### Paso 5: Ejecutar el script de prueba

```bash
python test_database.py
```

El script probará:
- ✅ Conexión a la base de datos
- ✅ Existencia de tablas
- ✅ Operaciones CRUD del repositorio
- ✅ Funcionamiento del servicio de dominio

## Opción 2: Probar con PostgreSQL Local

### Paso 1: Instalar PostgreSQL localmente

Si no lo tienes instalado, descarga desde [postgresql.org](https://www.postgresql.org/download/)

### Paso 2: Crear la base de datos

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos y usuario
CREATE DATABASE agentdb;
CREATE USER agent WITH PASSWORD 'agent';
GRANT ALL PRIVILEGES ON DATABASE agentdb TO agent;
\q
```

### Paso 3: Configurar variables de entorno

Crea `backend/.env`:

```env
POSTGRES_USER=agent
POSTGRES_PASSWORD=agent
POSTGRES_DB=agentdb
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://agent:agent@localhost:5432/agentdb
```

### Paso 4: Crear y aplicar migraciones

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Paso 5: Ejecutar pruebas

```bash
python test_database.py
```

## Verificación Manual

### 1. Verificar conexión directa

```bash
# Con Docker
docker exec -it db-agent psql -U agent -d agentdb

# Localmente
psql -U agent -d agentdb -h localhost
```

Luego ejecuta:
```sql
\dt  -- Listar tablas
SELECT * FROM kpis;  -- Ver KPIs
\q   -- Salir
```

### 2. Verificar estado de migraciones

```bash
cd backend
alembic current  # Ver versión actual
alembic history  # Ver historial de migraciones
```

### 3. Probar desde Python interactivo

```bash
cd backend
python
```

```python
from src.infrastructure.config.db import engine, SessionLocal
from src.infrastructure.outbound.kpi_repository import SQLAlchemyKPIRepository
from src.domain.entities.kpi import KPI

# Probar conexión
with engine.connect() as conn:
    result = conn.execute("SELECT 1").scalar()
    print(f"Conexión OK: {result}")

# Probar repositorio
db = SessionLocal()
repo = SQLAlchemyKPIRepository(db)

# Crear KPI
kpi = KPI(
    id="test_001",
    name="Test KPI",
    description="Descripción",
    sql_template="SELECT 1",
    owner="user",
    status="active"
)
saved = repo.save(kpi)
print(f"KPI guardado: {saved.name}")

# Buscar
found = repo.find_by_id("test_001")
print(f"KPI encontrado: {found.name if found else 'No encontrado'}")

# Limpiar
repo.delete("test_001")
db.close()
```

## Solución de Problemas

### Error: "DATABASE_URL not set"

**Solución**: Verifica que el archivo `.env` exista en `backend/` y tenga las variables correctas.

### Error: "connection refused" o "could not connect"

**Solución**: 
- Verifica que PostgreSQL esté corriendo: `docker ps` o `pg_isready`
- Verifica el host: `localhost` para local, `postgres` para Docker
- Verifica el puerto: `5432`

### Error: "relation 'kpis' does not exist"

**Solución**: Las migraciones no se han aplicado. Ejecuta:
```bash
cd backend
alembic upgrade head
```

### Error: "No module named 'src'"

**Solución**: Asegúrate de ejecutar los comandos desde el directorio `backend/`:
```bash
cd backend
python test_database.py
```

### Error: "password authentication failed"

**Solución**: Verifica las credenciales en `.env` y que el usuario exista en PostgreSQL.

## Resultado Esperado

Cuando todo funciona correctamente, deberías ver:

```
🧪 PRUEBAS DE CONFIGURACIÓN DE BASE DE DATOS
==================================================

📋 Configuración detectada:
   Host: postgres (o localhost)
   Database: agentdb
   User: agent

==================================================
1. Probando conexión a la base de datos...
==================================================
✅ Conexión exitosa a PostgreSQL

==================================================
2. Verificando que las tablas existan...
==================================================
✅ La tabla 'kpis' existe
   Registros actuales: 0

==================================================
3. Probando operaciones CRUD del repositorio...
==================================================
   📝 Creando KPI de prueba...
   ✅ KPI creado: test_...
   🔍 Buscando KPI por ID...
   ✅ KPI encontrado: KPI de Prueba
   ...
   ✅ Todas las operaciones CRUD funcionan correctamente

==================================================
4. Probando servicio de dominio...
==================================================
   ✅ Servicio de dominio funciona correctamente

==================================================
📊 RESUMEN DE PRUEBAS
==================================================
   ✅ PASS - Conexión
   ✅ PASS - Tablas
   ✅ PASS - Repositorio CRUD
   ✅ PASS - Servicio

==================================================
🎉 ¡Todas las pruebas pasaron! La configuración funciona correctamente.
==================================================
```

## Próximos Pasos

Una vez que las pruebas pasen:

1. ✅ La base de datos está configurada correctamente
2. ✅ Puedes usar el repositorio en tu aplicación
3. ✅ Puedes crear nuevas migraciones cuando agregues modelos
4. ✅ La arquitectura hexagonal está funcionando

¡Listo para desarrollar! 🚀

