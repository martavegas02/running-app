"""
Test OAuth Endpoints
Script para probar los endpoints de autenticación OAuth con Strava
"""
import requests
import json
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{title.center(70)}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")

def test_oauth_login():
    """Test: Obtener URL de OAuth"""
    print_section("Test 1: Obtener URL de OAuth")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/strava/login")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Message: {data.get('message')}")
            
            oauth_url = data.get('oauth_url')
            if oauth_url:
                print_success(f"OAuth URL obtenida correctamente")
                print_info(f"URL contiene client_id: {('client_id' in oauth_url)}")
                print_info(f"URL contiene scope: {('scope' in oauth_url)}")
                print_info(f"URL contiene state: {('state' in oauth_url)}")
                return True
            else:
                print_error("No se obtuvo oauth_url")
                return False
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_token_status_no_user():
    """Test: Verificar estado de token (usuario no existe)"""
    print_section("Test 2: Estado de Token (Usuario no existe)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/strava/token-status",
            params={"user_id": 99999}
        )
        
        if response.status_code == 404:
            print_success(f"Status: {response.status_code} (esperado)")
            print_success("Endpoint valida que usuario existe")
            data = response.json()
            print_info(f"Response: {data.get('detail')}")
            return True
        else:
            print_error(f"Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_get_user_no_exists():
    """Test: Obtener usuario (no existe)"""
    print_section("Test 3: Obtener Usuario (No existe)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            params={"user_id": 99999}
        )
        
        if response.status_code == 404:
            print_success(f"Status: {response.status_code} (esperado)")
            print_success("Endpoint valida que usuario existe")
            return True
        else:
            print_error(f"Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_logout():
    """Test: Logout"""
    print_section("Test 4: Logout")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/logout")
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            data = response.json()
            print_success(f"Message: {data.get('message')}")
            print_info(f"Action: {data.get('action')}")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_refresh_token_no_user():
    """Test: Refrescar token (usuario no existe)"""
    print_section("Test 5: Refrescar Token (Usuario no existe)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/refresh",
            params={"user_id": 99999}
        )
        
        if response.status_code == 404:
            print_success(f"Status: {response.status_code} (esperado)")
            print_success("Endpoint valida que usuario existe")
            return True
        else:
            print_error(f"Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def main():
    """Ejecutar todos los tests"""
    print(f"\n{Fore.MAGENTA}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         PRUEBAS DE ENDPOINTS OAUTH - Running Analytics Hub         ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    print_info(f"Base URL: {BASE_URL}")
    print_info("Asegúrate de que: docker-compose up -d está ejecutándose\n")
    
    tests = [
        ("OAuth Login", test_oauth_login),
        ("Token Status (No User)", test_token_status_no_user),
        ("Get User (No User)", test_get_user_no_exists),
        ("Logout", test_logout),
        ("Refresh Token (No User)", test_refresh_token_no_user),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Error ejecutando {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Resumen
    print_section("Resumen de Pruebas")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Fore.GREEN}PASÓ{Style.RESET_ALL}" if result else f"{Fore.RED}FALLÓ{Style.RESET_ALL}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Fore.CYAN}Total: {passed}/{total} pruebas pasadas{Style.RESET_ALL}\n")
    
    if passed == total:
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}{'¡TODOS LOS TESTS PASARON!'.center(70)}")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}{'='*70}")
        print(f"{Fore.YELLOW}{'Algunos tests fallaron. Revisa los errores arriba.'.center(70)}")
        print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
