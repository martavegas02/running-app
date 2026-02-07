#!/usr/bin/env python3
"""
Script interactivo para configurar Strava en Running Analytics Hub
Uso: python setup_strava.py
"""

import os
import re
from pathlib import Path

def read_env_file():
    """Leer archivo .env"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ No se encontró archivo .env")
        return None
    
    with open(env_path, 'r', encoding='utf-8') as f:
        return f.read()

def update_env_file(content, key, value):
    """Actualizar un valor en el archivo .env"""
    # Buscar la línea con el key y reemplazarla
    pattern = f"{key}=.*"
    if re.search(pattern, content):
        new_content = re.sub(pattern, f"{key}={value}", content)
        return new_content
    else:
        # Si no existe, añadirlo al final
        return content + f"\n{key}={value}\n"

def validate_client_id(client_id):
    """Validar que el Client ID sea válido (debe ser numérico)"""
    return client_id.isdigit() and len(client_id) > 0

def validate_client_secret(secret):
    """Validar que el Client Secret sea válido"""
    return len(secret) > 10 and len(secret) < 100

def main():
    print("=" * 70)
    print("   🏃 CONFIGURACIÓN DE STRAVA - Running Analytics Hub")
    print("=" * 70)
    
    print("\n📌 INSTRUCCIONES RÁPIDAS:")
    print("  1. Ve a: https://www.strava.com/settings/apps")
    print("  2. Inicia sesión con tu cuenta de Strava")
    print("  3. Haz clic en 'Create & Manage Your App'")
    print("  4. Rellena el formulario y crea la app")
    print("  5. Copia el Client ID y Client Secret")
    print("  6. Pega aquí cuando te lo pida")
    
    print("\n" + "=" * 70)
    
    # Leer .env actual
    env_content = read_env_file()
    if not env_content:
        print("❌ Error al leer .env")
        return
    
    # Extraer valores actuales
    current_client_id = re.search(r"STRAVA_CLIENT_ID=(\S+)", env_content)
    current_secret = re.search(r"STRAVA_CLIENT_SECRET=(\S+)", env_content)
    
    if current_client_id:
        print(f"\n✓ Client ID actual: {current_client_id.group(1)[:10]}...")
    if current_secret:
        print(f"✓ Client Secret actual: {'*' * 20}...")
    
    print("\n¿Quieres actualizar tus credenciales? (s/n): ", end="")
    response = input().strip().lower()
    
    if response != 's':
        print("\n✓ No se realizaron cambios")
        return
    
    # Solicitar nuevas credenciales
    print("\n" + "=" * 70)
    print("Ingresa tus nuevas credenciales:")
    print("=" * 70)
    
    while True:
        print("\n1️⃣  Ingresa tu CLIENT ID (numérico):")
        client_id = input("   > ").strip()
        
        if not validate_client_id(client_id):
            print("   ❌ Client ID inválido. Debe ser numérico.")
            continue
        break
    
    while True:
        print("\n2️⃣  Ingresa tu CLIENT SECRET:")
        client_secret = input("   > ").strip()
        
        if not validate_client_secret(client_secret):
            print("   ❌ Client Secret inválido. Debe tener más de 10 caracteres.")
            continue
        break
    
    print("\n3️⃣  Ingresa tu REDIRECT URI (por defecto: http://localhost:8000/auth/strava/callback):")
    redirect_uri = input("   > ").strip()
    if not redirect_uri:
        redirect_uri = "http://localhost:8000/auth/strava/callback"
    
    # Confirmar
    print("\n" + "=" * 70)
    print("RESUMEN DE CAMBIOS:")
    print("=" * 70)
    print(f"Client ID:     {client_id}")
    print(f"Client Secret: {'*' * len(client_secret)}")
    print(f"Redirect URI:  {redirect_uri}")
    
    print("\n¿Confirmas estos datos? (s/n): ", end="")
    confirm = input().strip().lower()
    
    if confirm != 's':
        print("\n❌ Operación cancelada")
        return
    
    # Actualizar .env
    env_content = update_env_file(env_content, "STRAVA_CLIENT_ID", client_id)
    env_content = update_env_file(env_content, "STRAVA_CLIENT_SECRET", client_secret)
    env_content = update_env_file(env_content, "STRAVA_REDIRECT_URI", redirect_uri)
    
    # Guardar cambios
    with open(".env", 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("\n" + "=" * 70)
    print("✅ CONFIGURACIÓN GUARDADA EXITOSAMENTE")
    print("=" * 70)
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("  1. Reinicia Docker:")
    print("     docker-compose restart running_analytics_backend")
    print("\n  2. Espera 5 segundos a que reinicie")
    print("\n  3. Abre Swagger UI:")
    print("     http://localhost:8000/docs")
    print("\n  4. Busca 'GET /auth/strava/login'")
    print("\n  5. Haz clic en 'Try it out' → 'Execute'")
    print("\n  6. Copia la URL de Strava y abre en tu navegador")
    print("\n  7. Autoriza la aplicación en Strava")
    print("\n  8. Sincroniza tus actividades con 'POST /sync/activities'")
    print("\n" + "=" * 70)
    print("¡Listo! Tus datos de Strava se sincronizarán automáticamente 🎉")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
