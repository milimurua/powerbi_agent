# Script PowerShell para probar la configuración de base de datos en Docker

Write-Host "🐳 Probando configuración de PostgreSQL con Docker" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Verificar que Docker esté corriendo
Write-Host "1. Verificando Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker está corriendo" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está corriendo. Por favor inicia Docker primero." -ForegroundColor Red
    exit 1
}

# Paso 2: Verificar archivos .env
Write-Host ""
Write-Host "2. Verificando configuración..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Archivo .env no encontrado en la raíz del proyecto" -ForegroundColor Yellow
    Write-Host "Creando archivo .env de ejemplo..." -ForegroundColor Yellow
    @"
POSTGRES_USER=agent
POSTGRES_PASSWORD=agent
POSTGRES_DB=agentdb
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Archivo .env creado. Por favor revisa y ajusta los valores si es necesario." -ForegroundColor Green
}

if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  Archivo backend\.env no encontrado" -ForegroundColor Yellow
    Write-Host "Creando archivo backend\.env..." -ForegroundColor Yellow
    if (-not (Test-Path "backend")) {
        New-Item -ItemType Directory -Path "backend" | Out-Null
    }
    @"
POSTGRES_USER=agent
POSTGRES_PASSWORD=agent
POSTGRES_DB=agentdb
POSTGRES_HOST=postgres
DATABASE_URL=postgresql+psycopg://agent:agent@postgres:5432/agentdb
"@ | Out-File -FilePath "backend\.env" -Encoding UTF8
    Write-Host "✅ Archivo backend\.env creado" -ForegroundColor Green
}
Write-Host "✅ Archivos de configuración listos" -ForegroundColor Green

# Paso 3: Iniciar PostgreSQL
Write-Host ""
Write-Host "3. Iniciando PostgreSQL..." -ForegroundColor Yellow
docker-compose up -d postgres

# Esperar a que PostgreSQL esté listo
Write-Host "Esperando a que PostgreSQL esté listo..." -ForegroundColor Yellow
$timeout = 30
$counter = 0
while ($counter -lt $timeout) {
    $result = docker exec db-agent pg_isready -U agent -d agentdb 2>&1
    if ($LASTEXITCODE -eq 0) {
        break
    }
    Start-Sleep -Seconds 1
    $counter++
    Write-Host "." -NoNewline
}
Write-Host ""
if ($counter -ge $timeout) {
    Write-Host "❌ PostgreSQL no está respondiendo después de $timeout segundos" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PostgreSQL está listo" -ForegroundColor Green

# Paso 4: Construir imagen del backend
Write-Host ""
Write-Host "4. Construyendo imagen del backend..." -ForegroundColor Yellow
docker-compose build backend
Write-Host "✅ Imagen construida" -ForegroundColor Green

# Paso 5: Ejecutar migraciones
Write-Host ""
Write-Host "5. Ejecutando migraciones de Alembic..." -ForegroundColor Yellow
Write-Host "   Creando migración inicial..." -ForegroundColor Gray
docker-compose run --rm backend alembic revision --autogenerate -m "Initial migration" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ⚠️  La migración puede ya existir, continuando..." -ForegroundColor Yellow
}

Write-Host "   Aplicando migraciones..." -ForegroundColor Gray
docker-compose run --rm backend alembic upgrade head
Write-Host "✅ Migraciones aplicadas" -ForegroundColor Green

# Paso 6: Ejecutar pruebas
Write-Host ""
Write-Host "6. Ejecutando pruebas de base de datos..." -ForegroundColor Yellow
docker-compose run --rm backend python test_database.py

# Resumen
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "✅ ¡Configuración completada exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   - Para iniciar todos los servicios: docker-compose up" -ForegroundColor White
Write-Host "   - Para ver logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   - Para detener: docker-compose down" -ForegroundColor White
Write-Host "   - Para ejecutar comandos en el contenedor: docker-compose exec backend bash" -ForegroundColor White
Write-Host ""

