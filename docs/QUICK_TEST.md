# 🚀 Prueba Rápida - PostgreSQL + SQLAlchemy

## Pasos Rápidos para Probar

### 1. Iniciar PostgreSQL (Docker)

```bash
docker-compose up -d postgres
```

### 2. Configurar variables de entorno

Crea `backend/.env`:
```env
POSTGRES_USER=agent
POSTGRES_PASSWORD=agent
POSTGRES_DB=agentdb
POSTGRES_HOST=postgres
DATABASE_URL=postgresql+psycopg://agent:agent@postgres:5432/agentdb
```

### 3. Crear y aplicar migraciones

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. Ejecutar pruebas

```bash
python test_database.py
```

## ✅ Resultado Esperado

Si todo funciona, verás:
```
🎉 ¡Todas las pruebas pasaron! La configuración funciona correctamente.
```

## 📝 Comandos Útiles

```bash
# Ver estado de migraciones
alembic current

# Ver historial
alembic history

# Conectar a la base de datos
docker exec -it db-agent psql -U agent -d agentdb
```

Para más detalles, ver `TESTING.md`

