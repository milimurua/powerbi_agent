# Instalación de Dependencias

## Problema: ModuleNotFoundError

Si ves el error `ModuleNotFoundError: No module named 'dotenv'`, significa que las dependencias no están instaladas.

## Solución Rápida (WSL/Linux)

### Opción 1: Script Automático (Recomendado)

```bash
cd backend
chmod +x setup_environment.sh
./setup_environment.sh
```

Este script:
- ✅ Crea un entorno virtual
- ✅ Instala todas las dependencias
- ✅ Verifica la instalación

### Opción 2: Manual

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -e .
```

### Opción 3: Instalar solo las dependencias necesarias

```bash
cd backend
pip install python-dotenv SQLAlchemy psycopg[binary] alembic
```

## Verificar Instalación

```bash
# Activar entorno virtual (si usaste uno)
source venv/bin/activate

# Verificar que las dependencias estén instaladas
python3 -c "import dotenv; import sqlalchemy; import alembic; print('✅ OK')"
```

## Usar el Entorno Virtual

Cada vez que trabajes en el proyecto:

```bash
cd backend
source venv/bin/activate
```

Verás `(venv)` al inicio de tu prompt, indicando que el entorno está activo.

## Ejecutar Alembic

Después de instalar las dependencias:

```bash
# Asegúrate de estar en el directorio backend
cd backend

# Activa el entorno virtual (si usaste uno)
source venv/bin/activate

# Ahora puedes ejecutar alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Dependencias del Proyecto

Las dependencias están definidas en `pyproject.toml`:

- `python-dotenv` - Para cargar variables de entorno
- `SQLAlchemy>=2.0` - ORM para PostgreSQL
- `psycopg[binary]` - Driver de PostgreSQL
- `alembic` - Migraciones de base de datos
- `fastapi` - Framework web
- `uvicorn` - Servidor ASGI
- `google-adk`, `google-generativeai`, `google-cloud-bigquery` - APIs de Google

## Troubleshooting

### Error: "python3: command not found"
```bash
# Instalar Python3
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Error: "pip: command not found"
```bash
# Instalar pip
sudo apt install python3-pip
```

### Error: "Permission denied"
```bash
# Dar permisos de ejecución al script
chmod +x setup_environment.sh
```

### Error: "No module named 'src'"
Asegúrate de ejecutar los comandos desde el directorio `backend/`:
```bash
cd backend
```

### Usar pip directamente sin entorno virtual (no recomendado)
```bash
pip3 install --user python-dotenv SQLAlchemy psycopg[binary] alembic
```

## Próximos Pasos

Una vez instaladas las dependencias:

1. ✅ Configura las variables de entorno en `.env`
2. ✅ Ejecuta las migraciones: `alembic upgrade head`
3. ✅ Prueba la configuración: `python test_database.py`

