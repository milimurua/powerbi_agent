# 🐳 Probar PostgreSQL con Docker

Esta guía te muestra cómo probar la configuración de PostgreSQL con SQLAlchemy y Alembic usando Docker.

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)

```bash
# Desde la raíz del proyecto
chmod +x docker/test_docker.sh
./docker/test_docker.sh
```

Este script automáticamente:
- ✅ Verifica Docker
- ✅ Crea archivos `.env` si no existen
- ✅ Inicia PostgreSQL
- ✅ Construye la imagen del backend
- ✅ Ejecuta las migraciones
- ✅ Ejecuta las pruebas

### Opción 2: Manual

#### Paso 1: Configurar variables de entorno

Crea `.env` en la raíz del proyecto:
```env
POSTGRES_USER=agent
POSTGRES_PASSWORD=agent
POSTGRES_DB=agentdb
```

Crea `backend/.env`:
```env
POSTGRES_USER=agent
POSTGRES_PASSWORD=agent
POSTGRES_DB=agentdb
POSTGRES_HOST=postgres
DATABASE_URL=postgresql+psycopg://agent:agent@postgres:5432/agentdb
```

#### Paso 2: Iniciar PostgreSQL

```bash
docker-compose up -d postgres
```

Verifica que esté corriendo:
```bash
docker ps
```

#### Paso 3: Construir imagen del backend

```bash
docker-compose build backend
```

#### Paso 4: Ejecutar migraciones

```bash
# Crear migración inicial
docker-compose run --rm backend alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
docker-compose run --rm backend alembic upgrade head
```

#### Paso 5: Ejecutar pruebas

```bash
docker-compose run --rm backend python test_database.py
```

## 📋 Comandos Útiles

### Ver logs de PostgreSQL

```bash
docker-compose logs -f postgres
```

### Conectar a PostgreSQL desde el contenedor

```bash
docker exec -it db-agent psql -U agent -d agentdb
```

### Ejecutar comandos en el contenedor del backend

```bash
# Entrar al contenedor
docker-compose exec backend bash

# Dentro del contenedor puedes ejecutar:
alembic current          # Ver migración actual
alembic history          # Ver historial
python test_database.py  # Ejecutar pruebas
```

### Reiniciar todo desde cero

```bash
# Detener y eliminar contenedores y volúmenes
docker-compose down -v

# Volver a iniciar
docker-compose up -d postgres
docker-compose run --rm backend alembic upgrade head
```

### Ver estado de migraciones

```bash
docker-compose run --rm backend alembic current
docker-compose run --rm backend alembic history
```

## 🔧 Troubleshooting

### Error: "Cannot connect to database"

**Solución**: Verifica que PostgreSQL esté corriendo:
```bash
docker ps
docker-compose logs postgres
```

### Error: "ModuleNotFoundError"

**Solución**: Reconstruye la imagen:
```bash
docker-compose build --no-cache backend
```

### Error: "relation 'kpis' does not exist"

**Solución**: Las migraciones no se han aplicado:
```bash
docker-compose run --rm backend alembic upgrade head
```

### Error: "DATABASE_URL not set"

**Solución**: Verifica que `backend/.env` exista y tenga `DATABASE_URL` configurada.

### Limpiar todo y empezar de nuevo

```bash
# Detener contenedores
docker-compose down -v

# Eliminar imágenes (opcional)
docker-compose rm -f

# Reconstruir
docker-compose build --no-cache
docker-compose up -d postgres
```

## 🎯 Estructura de Archivos en Docker

```
/app (dentro del contenedor)
├── src/              # Código fuente
├── alembic/          # Migraciones
├── alembic.ini       # Configuración de Alembic
├── test_database.py  # Script de pruebas
└── agents/           # Agentes de Google ADK
```

## ✅ Verificación Final

Si todo funciona correctamente, deberías ver:

```
🎉 ¡Todas las pruebas pasaron! La configuración funciona correctamente.
```

## 🚀 Iniciar Aplicación Completa

Una vez que las pruebas pasen, puedes iniciar todos los servicios:

```bash
docker-compose up
```

Esto iniciará:
- ✅ PostgreSQL en el puerto 5432
- ✅ Backend en el puerto 8080

## 📝 Notas

- Los volúmenes están montados para desarrollo, así que los cambios en el código se reflejan automáticamente
- Las migraciones se ejecutan manualmente con `docker-compose run --rm backend alembic upgrade head`
- Para producción, considera ejecutar las migraciones en un script de inicio o en un contenedor separado

