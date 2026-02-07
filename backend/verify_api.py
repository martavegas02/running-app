#!/usr/bin/env python3
"""
Verificación rápida del estado del API
"""
import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 60)
print("VERIFICACIÓN DE ENDPOINTS DEL API")
print("=" * 60)

async def test_endpoints():
    async with httpx.AsyncClient() as client:
        # Test 1: GET /users
        print("\n1. GET /users")
        r = await client.get(f"{BASE_URL}/users/")
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.text[:100]}")
        
        # Test 2: GET /docs
        print("\n2. GET /docs (Swagger UI)")
        r = await client.get("http://localhost:8000/docs")
        print(f"   Status: {r.status_code}")
        print(f"   HTML disponible: {'FastAPI' in r.text or 'swagger' in r.text}")
        
        # Test 3: GET /openapi.json
        print("\n3. GET /openapi.json (API Schema)")
        r = await client.get("http://localhost:8000/openapi.json")
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   Rutas disponibles: {len(data.get('paths', {}))}")
        
        # Test 4: Crear usuario
        print("\n4. POST /users (Crear usuario)")
        user_payload = {
            "strava_id": 999,
            "username": "test_user_001",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "strava_access_token": "test_token_12345",
            "strava_refresh_token": "refresh_token_12345"
        }
        r = await client.post(f"{BASE_URL}/users/", json=user_payload)
        print(f"   Status: {r.status_code}")
        if r.status_code in [200, 201]:
            user = r.json()
            print(f"   Usuario creado: ID={user.get('id')}, username={user.get('username')}")
        else:
            print(f"   Error: {r.text[:100]}")
        
        # Test 5: Listar usuarios
        print("\n5. GET /users (Listar usuarios)")
        r = await client.get(f"{BASE_URL}/users/")
        print(f"   Status: {r.status_code}")
        users = r.json()
        print(f"   Total usuarios: {len(users)}")

# Ejecutar pruebas
import asyncio
asyncio.run(test_endpoints())

print("\n" + "=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)
