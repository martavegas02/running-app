import httpx
import json

print("=" * 70)
print("PROBANDO ENDPOINT DE LOGIN DE STRAVA")
print("=" * 70)

async def test():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://localhost:8000/auth/strava/login")
        print(f"\nStatus: {r.status_code}")
        data = r.json()
        print(f"\nRespuesta:")
        print(json.dumps(data, indent=2))
        
        if "oauth_url" in data:
            print("\n✅ OAuth URL GENERADA CORRECTAMENTE!")
            print(f"\nURL: {data['oauth_url'][:100]}...")
            print("\n📋 PASOS SIGUIENTES:")
            print("  1. Copia la URL completa")
            print("  2. Abre en tu navegador")
            print("  3. Autoriza tu cuenta de Strava")
            print("  4. Serás redirigido a la app")
        else:
            print("\n❌ Error en la respuesta")

import asyncio
asyncio.run(test())
