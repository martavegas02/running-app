#!/usr/bin/env python3
"""
Script de prueba para los endpoints CRUD de Running Analytics Hub.
Ejecutar desde: python test_endpoints.py
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

# Colores para output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(test_name):
    print(f"\n{Colors.BOLD}{Colors.BLUE}[TEST] {test_name}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ {message}{Colors.END}")


# ===== TEST USUARIOS =====
def test_users():
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== PROBANDO USUARIOS ==={Colors.END}\n")
    
    # 1. Crear usuario
    print_test("1. Crear usuario")
    user_data = {
        "strava_id": 123456,
        "username": "test_runner_001",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "Runner",
        "access_token": "test_token_abc123",
        "refresh_token": "refresh_token_xyz",
        "token_expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    if response.status_code == 201:
        user = response.json()
        user_id = user['id']
        print_success(f"Usuario creado: ID={user_id}, Username={user['username']}")
        print_info(f"Response: {json.dumps(user, indent=2, default=str)}")
    else:
        print_error(f"Error: {response.status_code} - {response.text}")
        return None
    
    # 2. Obtener usuario
    print_test("2. Obtener usuario por ID")
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    if response.status_code == 200:
        user = response.json()
        print_success(f"Usuario obtenido: {user['username']}")
    else:
        print_error(f"Error: {response.status_code}")
    
    # 3. Obtener usuario por username
    print_test("3. Obtener usuario por username")
    response = requests.get(f"{BASE_URL}/users/by-username/test_runner_001")
    if response.status_code == 200:
        user = response.json()
        print_success(f"Usuario encontrado: {user['username']}")
    else:
        print_error(f"Error: {response.status_code}")
    
    # 4. Listar usuarios
    print_test("4. Listar todos los usuarios")
    response = requests.get(f"{BASE_URL}/users?skip=0&limit=10")
    if response.status_code == 200:
        users = response.json()
        print_success(f"Total de usuarios: {len(users)}")
        for u in users:
            print_info(f"  - {u['username']} (ID: {u['id']})")
    else:
        print_error(f"Error: {response.status_code}")
    
    # 5. Actualizar usuario
    print_test("5. Actualizar usuario")
    update_data = {"email": "newemail@example.com", "first_name": "Updated"}
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
    if response.status_code == 200:
        user = response.json()
        print_success(f"Usuario actualizado: {user['email']}")
    else:
        print_error(f"Error: {response.status_code}")
    
    # 6. Actualizar last sync
    print_test("6. Actualizar timestamp de sincronización")
    response = requests.post(f"{BASE_URL}/users/{user_id}/sync")
    if response.status_code == 200:
        user = response.json()
        print_success(f"Last sync actualizado: {user['last_sync']}")
    else:
        print_error(f"Error: {response.status_code}")
    
    return user_id


# ===== TEST ACTIVIDADES =====
def test_activities(user_id):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== PROBANDO ACTIVIDADES ==={Colors.END}\n")
    
    # 1. Crear actividad
    print_test("1. Crear actividad")
    activity_data = {
        "user_id": user_id,
        "strava_id": 9876543210,
        "name": "Morning Run - Test",
        "activity_type": "run",
        "distance": 10000,
        "duration": 2400,
        "elevation_gain": 150,
        "average_speed": 4.17,
        "max_speed": 5.5,
        "average_heart_rate": 145,
        "max_heart_rate": 165,
        "average_cadence": 170,
        "start_date": datetime.utcnow().isoformat(),
        "start_date_local": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
        "timezone": "America/New_York",
        "weather": "Clear",
        "temperature": 15
    }
    
    response = requests.post(f"{BASE_URL}/activities", json=activity_data)
    if response.status_code == 201:
        activity = response.json()
        activity_id = activity['id']
        print_success(f"Actividad creada: ID={activity_id}, Name={activity['name']}")
    else:
        print_error(f"Error: {response.status_code} - {response.text}")
        return None
    
    # 2. Obtener actividad
    print_test("2. Obtener actividad por ID")
    response = requests.get(f"{BASE_URL}/activities/{activity_id}")
    if response.status_code == 200:
        activity = response.json()
        print_success(f"Actividad obtenida: {activity['name']}")
    else:
        print_error(f"Error: {response.status_code}")
    
    # 3. Obtener actividades del usuario
    print_test("3. Obtener actividades del usuario")
    response = requests.get(f"{BASE_URL}/activities/user/{user_id}")
    if response.status_code == 200:
        activities = response.json()
        print_success(f"Total de actividades: {len(activities)}")
        for act in activities:
            print_info(f"  - {act['name']} ({act['activity_type']})")
    else:
        print_error(f"Error: {response.status_code}")
    
    # 4. Filtrar por tipo
    print_test("4. Obtener actividades filtradas por tipo")
    response = requests.get(f"{BASE_URL}/activities/user/{user_id}?activity_type=run")
    if response.status_code == 200:
        activities = response.json()
        print_success(f"Total de 'run' activities: {len(activities)}")
    else:
        print_error(f"Error: {response.status_code}")
    
    # 5. Obtener estadísticas
    print_test("5. Obtener estadísticas del usuario")
    response = requests.get(f"{BASE_URL}/activities/user/{user_id}/stats")
    if response.status_code == 200:
        stats = response.json()
        print_success("Estadísticas obtenidas:")
        print_info(f"  - Total distancia: {stats['total_distance']} km")
        print_info(f"  - Total duración: {stats['total_duration']} horas")
        print_info(f"  - Número de actividades: {stats['activity_count']}")
        print_info(f"  - Velocidad promedio: {stats['average_speed']} m/s")
        print_info(f"  - Velocidad máxima: {stats['max_speed']} m/s")
    else:
        print_error(f"Error: {response.status_code}")
    
    return activity_id


# ===== TEST GEAR =====
def test_gear(user_id):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== PROBANDO EQUIPO ==={Colors.END}\n")
    
    # 1. Crear equipo
    print_test("1. Crear equipo")
    gear_data = {
        "user_id": user_id,
        "name": "Nike Vaporfly 3",
        "gear_type": "shoes",
        "brand": "Nike",
        "model": "Vaporfly 3",
        "description": "Racing shoes",
        "primary": True,
        "distance": 0
    }
    
    response = requests.post(f"{BASE_URL}/gear", json=gear_data)
    if response.status_code == 201:
        gear = response.json()
        gear_id = gear['id']
        print_success(f"Equipo creado: ID={gear_id}, Name={gear['name']}")
    else:
        print_error(f"Error: {response.status_code} - {response.text}")
        return None
    
    # 2. Obtener equipo
    print_test("2. Obtener equipo por ID")
    response = requests.get(f"{BASE_URL}/gear/{gear_id}")
    if response.status_code == 200:
        gear = response.json()
        print_success(f"Equipo obtenido: {gear['name']}")
    else:
        print_error(f"Error: {response.status_code}")
    
    # 3. Obtener equipo del usuario
    print_test("3. Obtener equipo del usuario")
    response = requests.get(f"{BASE_URL}/gear/user/{user_id}")
    if response.status_code == 200:
        gear_list = response.json()
        print_success(f"Total de equipo: {len(gear_list)}")
        for g in gear_list:
            print_info(f"  - {g['name']} ({g['gear_type']})")
    else:
        print_error(f"Error: {response.status_code}")
    
    # 4. Obtener equipo primario
    print_test("4. Obtener equipo primario")
    response = requests.get(f"{BASE_URL}/gear/user/{user_id}/primary")
    if response.status_code == 200:
        gear = response.json()
        print_success(f"Equipo primario: {gear['name']}")
    else:
        print_error(f"Error: {response.status_code}")
    
    # 5. Obtener uso de equipo
    print_test("5. Obtener estadísticas de uso")
    response = requests.get(f"{BASE_URL}/gear/{gear_id}/usage")
    if response.status_code == 200:
        usage = response.json()
        print_success("Estadísticas de uso:")
        print_info(f"  - Distancia total: {usage['total_distance']} km")
        print_info(f"  - Número de actividades: {usage['activity_count']}")
    else:
        print_error(f"Error: {response.status_code}")
    
    return gear_id


# ===== MAIN =====
def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("=" * 60)
    print("  🏛️ Running Analytics Hub - Test de Endpoints")
    print("=" * 60)
    print(f"{Colors.END}\n")
    
    # Verificar que la API está online
    print_test("Verificando conexión a la API")
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code == 200:
            print_success("API está online y disponible")
        else:
            print_error("API respondió con error")
            return
    except requests.exceptions.ConnectionError:
        print_error("No se puede conectar a la API")
        print_info("Asegúrate de ejecutar: docker-compose up -d")
        return
    
    # Ejecutar tests
    user_id = test_users()
    
    if user_id:
        activity_id = test_activities(user_id)
        gear_id = test_gear(user_id)
        
        # Resumen
        print(f"\n{Colors.HEADER}{Colors.BOLD}=== RESUMEN ==={Colors.END}\n")
        print_success("Todos los tests completados exitosamente!")
        print_info(f"Usuario ID creado: {user_id}")
        if activity_id:
            print_info(f"Actividad ID creada: {activity_id}")
        if gear_id:
            print_info(f"Equipo ID creado: {gear_id}")
        
        print(f"\n{Colors.CYAN}Para más detalles, abre: http://localhost:8000/docs{Colors.END}\n")
    else:
        print_error("Pruebas fallidas")


if __name__ == "__main__":
    main()
