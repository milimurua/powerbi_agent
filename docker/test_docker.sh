#!/bin/bash
# Script para probar la configuración de base de datos en Docker

set -e

echo "🐳 Probando configuración de PostgreSQL con Docker"
echo "=================================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
info() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Paso 1: Verificar que Docker esté corriendo
echo "1. Verificando Docker..."
if ! docker info > /dev/null 2>&1; then
    error "Docker no está corriendo. Por favor inicia Docker primero."
    exit 1
fi
info "Docker está corriendo"

# Paso 2: Verificar que el archivo .env exista
echo ""
echo "2. Verificando configuración..."
if [ ! -f ".env" ]; then
    warn "Archivo .env no encontrado en la raíz del proyecto"
    echo "Creando archivo .env de ejemplo..."
    cat > .env << EOF
POSTGRES_USER=agent
POSTGRES_PASSWORD=agent
POSTGRES_DB=agentdb
EOF
    info "Archivo .env creado. Por favor revisa y ajusta los valores si es necesario."
fi

if [ ! -f "backend/.env" ]; then
    warn "Archivo backend/.env no encontrado"
    echo "Creando archivo backend/.env..."
    mkdir -p backend
    cat > backend/.env << EOF
POSTGRES_USER=agent
POSTGRES_PASSWORD=agent
POSTGRES_DB=agentdb
POSTGRES_HOST=postgres
DATABASE_URL=postgresql+psycopg://agent:agent@postgres:5432/agentdb
EOF
    info "Archivo backend/.env creado"
fi
info "Archivos de configuración listos"

# Paso 3: Iniciar PostgreSQL
echo ""
echo "3. Iniciando PostgreSQL..."
docker-compose up -d postgres

# Esperar a que PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
timeout=30
counter=0
while ! docker exec db-agent pg_isready -U agent -d agentdb > /dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        error "PostgreSQL no está respondiendo después de ${timeout} segundos"
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
    echo -n "."
done
echo ""
info "PostgreSQL está listo"

# Paso 4: Construir imagen del backend
echo ""
echo "4. Construyendo imagen del backend..."
docker-compose build backend
info "Imagen construida"

# Paso 5: Ejecutar migraciones
echo ""
echo "5. Ejecutando migraciones de Alembic..."
echo "   Creando migración inicial..."
docker-compose run --rm backend alembic revision --autogenerate -m "Initial migration" || {
    warn "La migración puede ya existir, continuando..."
}

echo "   Aplicando migraciones..."
docker-compose run --rm backend alembic upgrade head
info "Migraciones aplicadas"

# Paso 6: Ejecutar pruebas
echo ""
echo "6. Ejecutando pruebas de base de datos..."
docker-compose run --rm backend python test_database.py

# Resumen
echo ""
echo "=================================================="
info "¡Configuración completada exitosamente!"
echo ""
echo "📝 Próximos pasos:"
echo "   - Para iniciar todos los servicios: docker-compose up"
echo "   - Para ver logs: docker-compose logs -f"
echo "   - Para detener: docker-compose down"
echo "   - Para ejecutar comandos en el contenedor: docker-compose exec backend bash"
echo ""

