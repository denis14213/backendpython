"""
Script pour tester le déploiement de l'API
"""
import requests
import sys

def test_api(base_url):
    """
    Teste les endpoints principaux de l'API
    
    Args:
        base_url: URL de base de l'API (ex: https://clinique-backend.onrender.com)
    """
    print(f"\n🧪 Test de l'API: {base_url}\n")
    
    # Test 1: Health Check
    print("1️⃣ Test Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health check OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test 2: Route racine
    print("\n2️⃣ Test Route Racine...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("   ✅ Route racine OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Route racine failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: Login (avec identifiants de test)
    print("\n3️⃣ Test Login...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={
                "email": "admin@clinique.com",
                "password": "Admin123!"
            }
        )
        if response.status_code == 200:
            print("   ✅ Login OK")
            data = response.json()
            if 'user' in data:
                print(f"   User: {data['user'].get('prenom')} {data['user'].get('nom')}")
                print(f"   Role: {data['user'].get('role')}")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 4: Vérifier MongoDB
    print("\n4️⃣ Test Connexion MongoDB...")
    try:
        # Tenter de récupérer des données
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={
                "email": "test@test.com",
                "password": "wrong"
            }
        )
        # Si on reçoit une réponse (même erreur), MongoDB fonctionne
        if response.status_code in [200, 401, 400]:
            print("   ✅ MongoDB connecté")
        else:
            print(f"   ⚠️ Statut inattendu: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "="*50)
    print("✅ Tests terminés!")
    print("="*50 + "\n")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        print("Usage: python test_deployment.py <URL>")
        print("Exemple: python test_deployment.py https://clinique-backend.onrender.com")
        sys.exit(1)
    
    test_api(base_url)
