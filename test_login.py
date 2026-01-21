"""
Test de connexion direct pour déboguer
"""
import requests
import json

# Test de connexion
url = "http://localhost:5000/api/auth/login"
headers = {
    "Content-Type": "application/json",
    "Origin": "http://localhost:3001"
}
data = {
    "email": "admin@clinique.com",
    "password": "Admin123!"
}

print("🔍 Test de connexion...")
print(f"URL: {url}")
print(f"Data: {data}")

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📋 Headers: {dict(response.headers)}")
    print(f"📄 Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ Connexion réussie!")
    else:
        print(f"\n❌ Erreur: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
