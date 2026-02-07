#!/usr/bin/env python3
"""
Script de prueba completo para todos los endpoints del API
Ejecutar: python test_complete_flow.py
"""
import httpx
import json
import asyncio
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

class APITester:
    def __init__(self):
        self.user_id = None
        self.activity_id = None
        self.gear_id = None
        self.results = []
    
    async def test(self):
        async with httpx.AsyncClient() as client:
            print("=" * 70)
            print("FLUJO COMPLETO DE PRUEBAS - Running Analytics Hub")
            print("=" * 70)
            
            # 1. Crear usuario
            print("\n[1] CREAR USUARIO")
            user_data = {
                "strava_id": 12345,
                "username": "test_runner_2024",
                "email": "runner@example.com",
                "first_name": "Test",
                "last_name": "Runner",
                "strava_access_token": "test_access_token_abc123",
                "strava_refresh_token": "test_refresh_token_xyz789"
            }
            r = await client.post(f"{BASE_URL}/users/", json=user_data)
            if r.status_code == 201:
                user = r.json()
                self.user_id = user['id']
                print(f"✓ Usuario creado: ID={user['id']}, Username={user['username']}")
            else:
                print(f"✗ Error: {r.status_code} - {r.text[:200]}")
                return
            
            # 2. Obtener usuario
            print("\n[2] OBTENER USUARIO")
            r = await client.get(f"{BASE_URL}/users/{self.user_id}")
            if r.status_code == 200:
                user = r.json()
                print(f"✓ Usuario obtenido: {user['username']} ({user['email']})")
            else:
                print(f"✗ Error: {r.status_code}")
            
            # 3. Listar usuarios
            print("\n[3] LISTAR USUARIOS")
            r = await client.get(f"{BASE_URL}/users/")
            if r.status_code == 200:
                users = r.json()
                print(f"✓ Total de usuarios: {len(users)}")
            else:
                print(f"✗ Error: {r.status_code}")
            
            # 4. Crear actividad
            print("\n[4] CREAR ACTIVIDAD")
            activity_data = {
                "user_id": self.user_id,
                "strava_id": 99999,
                "name": "Morning Run - 10K",
                "activity_type": "Run",
                "distance": 10.5,
                "duration": 2700,  # 45 minutos
                "average_speed": 13.8,
                "start_date": "2024-01-15T06:30:00",
                "start_date_local": "2024-01-15T06:30:00"
            }
            r = await client.post(f"{BASE_URL}/activities/", json=activity_data)
            if r.status_code == 201:
                activity = r.json()
                self.activity_id = activity['id']
                print(f"✓ Actividad creada: ID={activity['id']}, {activity['name']}")
            else:
                print(f"✗ Error: {r.status_code} - {r.text[:200]}")
            
            # 5. Obtener actividad
            print("\n[5] OBTENER ACTIVIDAD")
            if self.activity_id:
                r = await client.get(f"{BASE_URL}/activities/{self.activity_id}")
                if r.status_code == 200:
                    activity = r.json()
                    print(f"✓ Actividad: {activity['name']}, Distancia: {activity['distance']}km")
                else:
                    print(f"✗ Error: {r.status_code}")
            
            # 6. Listar actividades del usuario
            print("\n[6] LISTAR ACTIVIDADES DEL USUARIO")
            r = await client.get(f"{BASE_URL}/activities/user/{self.user_id}")
            if r.status_code == 200:
                activities = r.json()
                print(f"✓ Total actividades: {len(activities)}")
                if activities:
                    print(f"  Distancia total: {sum(a.get('distance', 0) for a in activities):.1f}km")
            else:
                print(f"✗ Error: {r.status_code}")
            
            # 7. Crear equipo
            print("\n[7] CREAR EQUIPO")
            gear_data = {
                "user_id": self.user_id,
                "strava_id": "g88888",
                "name": "Nike Running Shoes",
                "gear_type": "Shoes",
                "brand": "Nike",
                "model": "Pegasus 40",
                "is_primary": True,
                "distance": 0.0
            }
            r = await client.post(f"{BASE_URL}/gear/", json=gear_data)
            if r.status_code == 201:
                gear = r.json()
                self.gear_id = gear['id']
                print(f"✓ Equipo creado: ID={gear['id']}, {gear['name']}")
            else:
                print(f"✗ Error: {r.status_code} - {r.text[:200]}")
            
            # 8. Obtener equipo
            print("\n[8] OBTENER EQUIPO")
            if self.gear_id:
                r = await client.get(f"{BASE_URL}/gear/{self.gear_id}")
                if r.status_code == 200:
                    gear = r.json()
                    print(f"✓ Equipo: {gear['name']}, Principal: {gear['is_primary']}")
                else:
                    print(f"✗ Error: {r.status_code}")
            
            # 9. Listar equipo del usuario
            print("\n[9] LISTAR EQUIPO DEL USUARIO")
            r = await client.get(f"{BASE_URL}/gear/user/{self.user_id}")
            if r.status_code == 200:
                gears = r.json()
                print(f"✓ Total equipamiento: {len(gears)}")
            else:
                print(f"✗ Error: {r.status_code}")
            
            # 10. Obtener estadísticas del usuario
            print("\n[10] ESTADÍSTICAS DEL USUARIO")
            r = await client.get(f"{BASE_URL}/activities/user/{self.user_id}/stats")
            if r.status_code == 200:
                stats = r.json()
                print(f"✓ Estadísticas:")
                print(f"  - Total actividades: {stats.get('total_activities', 0)}")
                print(f"  - Distancia total: {stats.get('total_distance', 0):.1f}km")
                print(f"  - Duración total: {stats.get('total_duration', 0)} segundos")
            else:
                print(f"✗ Error: {r.status_code}")
            
            # 11. Actualizar usuario
            print("\n[11] ACTUALIZAR USUARIO")
            update_data = {
                "first_name": "TestUpdated",
                "profile_picture": "https://example.com/pic.jpg"
            }
            r = await client.put(f"{BASE_URL}/users/{self.user_id}", json=update_data)
            if r.status_code == 200:
                user = r.json()
                print(f"✓ Usuario actualizado: {user['first_name']}")
            else:
                print(f"✗ Error: {r.status_code}")
            
            # 12. Verificar API Schema
            print("\n[12] VERIFICAR SCHEMA DEL API")
            r = await client.get("http://localhost:8000/openapi.json")
            if r.status_code == 200:
                schema = r.json()
                print(f"✓ Schema obtenido")
                print(f"  - Rutas disponibles: {len(schema.get('paths', {}))}")
                print(f"  - Versión OpenAPI: {schema.get('openapi', 'N/A')}")
            else:
                print(f"✗ Error: {r.status_code}")
            
            print("\n" + "=" * 70)
            print("FLUJO DE PRUEBAS COMPLETADO")
            print("=" * 70)
            print("\n📌 Próximas pruebas recomendadas:")
            print("  1. OAuth: Implementar flujo completo de autenticación con Strava")
            print("  2. Sincronización: Sincronizar actividades desde Strava")
            print("  3. Filtrado: Probar filtros en endpoints de actividades")
            print("  4. Validación: Probar casos de error (datos inválidos, etc)")
            print("\n🔗 Accede a Swagger para pruebas interactivas: http://localhost:8000/docs")

async def main():
    tester = APITester()
    await tester.test()

if __name__ == "__main__":
    asyncio.run(main())
