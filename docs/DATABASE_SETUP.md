# Configuración de PostgreSQL con SQLAlchemy y Alembic

Este documento explica cómo está configurado PostgreSQL con SQLAlchemy y Alembic en el proyecto, manteniendo la arquitectura hexagonal.

## Estructura de la Arquitectura Hexagonal

```
backend/
├── src/
│   ├── domain/                    # Capa de Dominio (sin dependencias externas)
│   │   ├── entities/              # Entidades de negocio
│   │   │   └── kpi.py
│   │   ├── repositories/          # Interfaces de repositorios (ABC)
│   │   │   └── kpi_repository.py
│   │   └── services/              # Servicios de dominio
│   │       └── kpi_service.py
│   ├── application/               # Capa de Aplicación
│   │   └── use_cases/
│   └── infrastructure/            # Capa de Infraestructura
│       ├── config/
│       │   ├── db.py              # Configuración SQLAlchemy
│       │   └── settings.py        # Configuración de entorno
│       └── outbound/              # Implementaciones de repositorios
│           ├── models/            # Modelos SQLAlchemy
│           │   └── kpi_model.py
│           └── kpi_repository.py # Implementación SQLAlchemy
└── alembic/                       # Migraciones de base de datos
    ├── env.py
    └── versions/
```

## Configuración

### 1. Variables de Entorno

Crea un archivo `.env` en el directorio `backend/` con las siguientes variables:

```env
# PostgreSQL Database Configuration
# Opción 1: URL completa de conexión
DATABASE_URL=postgresql+psycopg://agent:agent@localhost:5432/agentdb

# Opción 2: Variables individuales (se usarán si DATABASE_URL no está definida)
POSTGRES_USER=agent
POSTGRES_PASSWORD=agent
POSTGRES_DB=agentdb
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Para Docker Compose, usar:
# DATABASE_URL=postgresql+psycopg://agent:agent@postgres:5432/agentdb
# POSTGRES_HOST=postgres
```

### 2. Dependencias

Las dependencias ya están configuradas en `pyproject.toml`:
- `SQLAlchemy>=2.0`
- `psycopg[binary]` (driver de PostgreSQL)
- `alembic` (migraciones)

## Uso

### Inicializar la Base de Datos

1. **Asegúrate de que PostgreSQL esté corriendo** (localmente o en Docker)

2. **Crear la migración inicial**:
```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
```

3. **Aplicar las migraciones**:
```bash
alembic upgrade head
```

### Crear Nuevas Migraciones

Cuando agregues o modifiques modelos en `src/infrastructure/outbound/models/`:

```bash
# Generar migración automáticamente
alembic revision --autogenerate -m "Descripción del cambio"

# Revisar la migración generada en alembic/versions/
# Luego aplicar:
alembic upgrade head
```

### Comandos Útiles de Alembic

```bash
# Ver historial de migraciones
alembic history

# Ver la versión actual
alembic current

# Revertir última migración
alembic downgrade -1

# Revertir todas las migraciones
alembic downgrade base

# Aplicar todas las migraciones pendientes
alembic upgrade head
```

## Uso en el Código

### Ejemplo: Usar el Repositorio de KPI

```python
from src.infrastructure.config.db import get_db, SessionLocal
from src.infrastructure.outbound.kpi_repository import SQLAlchemyKPIRepository
from src.domain.services.kpi_service import KpiService
from src.domain.entities.kpi import KPI

# Obtener sesión de base de datos
db = next(get_db())

# Crear repositorio (capa de infraestructura)
kpi_repository = SQLAlchemyKPIRepository(db)

# Crear servicio de dominio (inyectar repositorio)
kpi_service = KpiService(kpi_repository)

# Usar el servicio
active_kpis = kpi_service.get_active_kpis()

# Crear un nuevo KPI
new_kpi = KPI(
    id="kpi_001",
    name="Ventas Mensuales",
    description="Total de ventas del mes",
    sql_template="SELECT SUM(amount) FROM sales WHERE month = :month",
    owner="user",
    status="active"
)
saved_kpi = kpi_repository.save(new_kpi)
```

### Con FastAPI (Dependency Injection)

```python
from fastapi import Depends
from src.infrastructure.config.db import get_db
from src.infrastructure.outbound.kpi_repository import SQLAlchemyKPIRepository
from src.domain.services.kpi_service import KpiService

def get_kpi_service(db = Depends(get_db)):
    repository = SQLAlchemyKPIRepository(db)
    return KpiService(repository)

@app.get("/kpis/active")
def get_active_kpis(service: KpiService = Depends(get_kpi_service)):
    return service.get_active_kpis()
```

## Arquitectura Hexagonal

La configuración respeta la arquitectura hexagonal:

1. **Dominio**: Las entidades (`KPI`) y repositorios (`KPIRepository`) no dependen de SQLAlchemy
2. **Infraestructura**: Los modelos SQLAlchemy (`KPIModel`) y la implementación del repositorio (`SQLAlchemyKPIRepository`) están en la capa de infraestructura
3. **Separación de responsabilidades**: El dominio define las interfaces, la infraestructura las implementa

### Flujo de Datos

```
Use Case (Application)
    ↓
Service (Domain) → Repository Interface (Domain)
    ↓
Repository Implementation (Infrastructure) → SQLAlchemy Model (Infrastructure)
    ↓
PostgreSQL Database
```

## Docker Compose

Si usas Docker Compose, la configuración ya está lista en `docker-compose.yml`. Solo asegúrate de que las variables de entorno estén configuradas correctamente para que el backend se conecte a `postgres:5432` en lugar de `localhost:5432`.

## Troubleshooting

### Error: "DATABASE_URL not set"
- Verifica que el archivo `.env` exista en `backend/`
- Verifica que las variables estén correctamente definidas

### Error: "No module named 'src'"
- Asegúrate de ejecutar los comandos desde el directorio `backend/`
- Verifica que `prepend_sys_path = .` esté en `alembic.ini`

### Error de conexión a PostgreSQL
- Verifica que PostgreSQL esté corriendo
- Verifica las credenciales en `.env`
- Si usas Docker, verifica que el contenedor esté corriendo: `docker ps`

