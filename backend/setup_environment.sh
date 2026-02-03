#!/bin/bash
# Script para configurar el entorno de desarrollo

echo "🔧 Configurando entorno de desarrollo..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instálalo primero."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔌 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📥 Instalando dependencias desde pyproject.toml..."
pip install -e .

# Verificar instalación
echo ""
echo "✅ Verificando instalación..."
python3 -c "import dotenv; import sqlalchemy; import alembic; print('✅ Todas las dependencias están instaladas')" 2>/dev/null || {
    echo "⚠️  Algunas dependencias pueden no estar instaladas correctamente"
    echo "💡 Intenta ejecutar: pip install -e ."
}

echo ""
echo "🎉 Entorno configurado correctamente!"
echo ""
echo "📝 Para activar el entorno virtual en el futuro, ejecuta:"
echo "   source venv/bin/activate"
echo ""
echo "🚀 Ahora puedes ejecutar:"
echo "   alembic revision --autogenerate -m 'Initial migration'"
echo "   alembic upgrade head"
echo "   python test_database.py"

