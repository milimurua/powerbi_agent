"""
Script de prueba para verificar la configuración de PostgreSQL con SQLAlchemy y Alembic
"""
import sys
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, 'src')

from src.infrastructure.config.db import engine, SessionLocal, Base
from src.infrastructure.config.settings import settings
from src.infrastructure.outbound.models.kpi_model import KPIModel
from src.infrastructure.outbound.kpi_repository import SQLAlchemyKPIRepository
from src.domain.services.kpi_service import KpiService
from src.domain.entities.kpi import KPI


def test_connection():
    """Prueba la conexión a la base de datos"""
    print("=" * 50)
    print("1. Probando conexión a la base de datos...")
    print("=" * 50)
    
    try:
        # Intentar conectar
        from sqlalchemy import text  # pyright: ignore[reportMissingImports]
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("✅ Conexión exitosa a PostgreSQL")
                db_url = settings.get_database_url()
                masked_url = db_url.replace(settings.POSTGRES_PASSWORD, '***') if settings.POSTGRES_PASSWORD else db_url
                print(f"   URL: {masked_url}")
                return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Verifica que:")
        print("   - PostgreSQL esté corriendo")
        print("   - Las variables de entorno estén configuradas en backend/.env")
        print("   - Las credenciales sean correctas")
        return False


def test_tables_exist():
    """Verifica que las tablas existan en la base de datos"""
    print("\n" + "=" * 50)
    print("2. Verificando que las tablas existan...")
    print("=" * 50)
    
    try:
        # Verificar que la tabla kpis existe
        from sqlalchemy import text  # pyright: ignore[reportMissingImports]
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'kpis')")
            ).scalar()
            
            if result:
                print("✅ La tabla 'kpis' existe")
                
                # Contar registros
                count = connection.execute(text("SELECT COUNT(*) FROM kpis")).scalar()
                print(f"   Registros actuales: {count}")
                return True
            else:
                print("❌ La tabla 'kpis' NO existe")
                print("\n💡 Ejecuta las migraciones:")
                print("   cd backend")
                print("   alembic revision --autogenerate -m 'Initial migration'")
                print("   alembic upgrade head")
                return False
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False


def test_repository_crud():
    """Prueba las operaciones CRUD del repositorio"""
    print("\n" + "=" * 50)
    print("3. Probando operaciones CRUD del repositorio...")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        repository = SQLAlchemyKPIRepository(db)
        
        # Crear un KPI de prueba
        test_kpi = KPI(
            id=f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name="KPI de Prueba",
            description="Este es un KPI creado para probar la funcionalidad",
            sql_template="SELECT COUNT(*) FROM test_table WHERE date = :date",
            owner="user",
            status="active"
        )
        
        print("\n   📝 Creando KPI de prueba...")
        saved_kpi = repository.save(test_kpi)
        print(f"   ✅ KPI creado: {saved_kpi.id} - {saved_kpi.name}")
        
        # Buscar por ID
        print("\n   🔍 Buscando KPI por ID...")
        found_kpi = repository.find_by_id(saved_kpi.id)
        if found_kpi and found_kpi.id == saved_kpi.id:
            print(f"   ✅ KPI encontrado: {found_kpi.name}")
        else:
            print("   ❌ No se pudo encontrar el KPI")
            return False
        
        # Buscar activos
        print("\n   🔍 Buscando KPIs activos...")
        active_kpis = repository.find_active()
        print(f"   ✅ KPIs activos encontrados: {len(active_kpis)}")
        
        # Buscar todos
        print("\n   🔍 Buscando todos los KPIs...")
        all_kpis = repository.find_all()
        print(f"   ✅ Total de KPIs: {len(all_kpis)}")
        
        # Actualizar
        print("\n   ✏️  Actualizando KPI...")
        updated_kpi = KPI(
            id=saved_kpi.id,
            name="KPI Actualizado",
            description=saved_kpi.description,
            sql_template=saved_kpi.sql_template,
            owner=saved_kpi.owner,
            status="inactive"
        )
        updated = repository.save(updated_kpi)
        if updated.name == "KPI Actualizado":
            print(f"   ✅ KPI actualizado: {updated.name} (status: {updated.status})")
        else:
            print("   ❌ No se pudo actualizar el KPI")
            return False
        
        # Eliminar
        print("\n   🗑️  Eliminando KPI de prueba...")
        deleted = repository.delete(saved_kpi.id)
        if deleted:
            print(f"   ✅ KPI eliminado: {saved_kpi.id}")
        else:
            print("   ❌ No se pudo eliminar el KPI")
            return False
        
        print("\n   ✅ Todas las operaciones CRUD funcionan correctamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en operaciones CRUD: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_service():
    """Prueba el servicio de dominio"""
    print("\n" + "=" * 50)
    print("4. Probando servicio de dominio...")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        repository = SQLAlchemyKPIRepository(db)
        service = KpiService(repository)
        
        # Obtener KPIs activos
        print("\n   🔍 Obteniendo KPIs activos mediante el servicio...")
        active_kpis = service.get_active_kpis()
        print(f"   ✅ KPIs activos obtenidos: {len(active_kpis)}")
        
        # Crear un KPI para activar
        test_kpi = KPI(
            id=f"test_activate_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name="KPI para Activar",
            description="KPI de prueba para activación",
            sql_template="SELECT 1",
            owner="user",
            status="proposed"
        )
        repository.save(test_kpi)
        print(f"   📝 KPI creado con status 'proposed': {test_kpi.id}")
        
        # Activar el KPI
        print("\n   ⚡ Activando KPI mediante el servicio...")
        activated = service.activate_kpi(test_kpi.id)
        if activated and activated.status == "active":
            print(f"   ✅ KPI activado: {activated.id} (status: {activated.status})")
        else:
            print("   ❌ No se pudo activar el KPI")
            return False
        
        # Limpiar
        repository.delete(test_kpi.id)
        print(f"   🗑️  KPI de prueba eliminado")
        
        print("\n   ✅ Servicio de dominio funciona correctamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en servicio: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "=" * 50)
    print("🧪 PRUEBAS DE CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 50)
    print(f"\n📋 Configuración detectada:")
    print(f"   Host: {settings.POSTGRES_HOST}")
    print(f"   Database: {settings.POSTGRES_DB}")
    print(f"   User: {settings.POSTGRES_USER}")
    print()
    
    results = []
    
    # Ejecutar pruebas
    results.append(("Conexión", test_connection()))
    results.append(("Tablas", test_tables_exist()))
    results.append(("Repositorio CRUD", test_repository_crud()))
    results.append(("Servicio", test_service()))
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ¡Todas las pruebas pasaron! La configuración funciona correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    print("=" * 50 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

