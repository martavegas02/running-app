"""
Script de prueba rápida para verificar la conexión a la base de datos.
Ejecutar desde el directorio backend: python test_connection.py
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import engine
from app.models.database import Base

def test_database_connection():
    """Prueba la conexión a la base de datos."""
    print("🔍 Probando conexión a PostgreSQL...")
    
    try:
        # Intentar conectar
        with engine.connect() as conn:
            print("✅ Conexión exitosa a PostgreSQL")
            
            # Verificar si la tabla existe
            result = conn.execute("SELECT version();")
            version = result.fetchone()
            print(f"📊 Versión de PostgreSQL: {version[0]}")
            
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        print("\n💡 Asegúrate de que:")
        print("1. PostgreSQL está corriendo (docker-compose up -d)")
        print("2. Las variables de entorno en .env son correctas")
        print("3. El contenedor 'running_analytics_db' está activo")
        return False


def create_tables():
    """Crea todas las tablas en la base de datos."""
    print("\n📝 Creando tablas de la base de datos...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error al crear tablas: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("🏛️ Running Analytics Hub - Database Setup Test")
    print("=" * 60)
    
    # Test 1: Conexión
    if not test_database_connection():
        print("\n⚠️ Abortando... No se pudo conectar a la base de datos")
        sys.exit(1)
    
    # Test 2: Crear tablas
    if not create_tables():
        print("\n⚠️ Error al crear tablas")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✨ ¡Todo listo! Tu base de datos está configurada.")
    print("=" * 60)
    print("\n📌 Próximos pasos:")
    print("1. Ejecutar: docker-compose up -d")
    print("2. Verificar: curl http://localhost:8000/health")
    print("3. Ver API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
