import os

client_id = os.getenv("STRAVA_CLIENT_ID")
client_secret = os.getenv("STRAVA_CLIENT_SECRET")
redirect_uri = os.getenv("STRAVA_REDIRECT_URI")

print("=== STRAVA CREDENTIALS STATUS ===")
print(f"CLIENT_ID: {client_id}")
print(f"CLIENT_SECRET: {client_secret[:20] if client_secret else 'NOT SET'}...")
print(f"REDIRECT_URI: {redirect_uri}")
print()

if not client_id or client_id == "None":
    print("ERROR: STRAVA_CLIENT_ID is NOT configured!")
else:
    print("SUCCESS: STRAVA_CLIENT_ID is configured")
    
if not client_secret or client_secret == "None":
    print("ERROR: STRAVA_CLIENT_SECRET is NOT configured!")
else:
    print("SUCCESS: STRAVA_CLIENT_SECRET is configured")
