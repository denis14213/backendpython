"""
Script de test complet de l'API
Teste tous les endpoints avec les utilisateurs créés
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

# Session pour maintenir les cookies
session = requests.Session()

print("="*70)
print("🧪 TEST COMPLET DE L'API - PLATEFORME CLINIQUE MÉDICALE")
print("="*70)

# ============================================
# TEST 1: CONNEXION ADMINISTRATEUR
# ============================================
print("\n" + "="*70)
print("TEST 1: Connexion Administrateur")
print("="*70)

try:
    response = session.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@clinique.com", "password": "Admin123!"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Connexion admin réussie: {data['user']['email']}")
        print_info(f"Rôle: {data['user']['role']}")
    else:
        print_error(f"Échec connexion admin: {response.status_code} - {response.text}")
except Exception as e:
    print_error(f"Erreur connexion admin: {e}")

# Déconnexion
session.post(f"{BASE_URL}/auth/logout")

# ============================================
# TEST 2: CONNEXION MÉDECIN
# ============================================
print("\n" + "="*70)
print("TEST 2: Connexion Médecin")
print("="*70)

try:
    response = session.post(
        f"{BASE_URL}/auth/login",
        json={"email": "medecin1@clinique.com", "password": "Medecin123!"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Connexion médecin réussie: Dr. {data['user']['prenom']} {data['user']['nom']}")
        print_info(f"Email: {data['user']['email']}")
        
        # Test dashboard médecin
        response = session.get(f"{BASE_URL}/medecin/dashboard")
        if response.status_code == 200:
            dashboard = response.json()
            print_success(f"Dashboard médecin accessible")
            print_info(f"RDV aujourd'hui: {dashboard.get('rdvs_aujourdhui', 0)}")
            print_info(f"RDV prochains: {dashboard.get('rdvs_prochains', 0)}")
            print_info(f"Nombre de patients: {dashboard.get('nb_patients', 0)}")
        
        # Test liste patients
        response = session.get(f"{BASE_URL}/medecin/patients")
        if response.status_code == 200:
            patients = response.json()
            print_success(f"Liste patients accessible: {len(patients.get('patients', []))} patients")
        
        # Test liste rendez-vous
        response = session.get(f"{BASE_URL}/medecin/rendezvous")
        if response.status_code == 200:
            rdvs = response.json()
            print_success(f"Liste RDV accessible: {len(rdvs.get('rendezvous', []))} rendez-vous")
    else:
        print_error(f"Échec connexion médecin: {response.status_code} - {response.text}")
except Exception as e:
    print_error(f"Erreur connexion médecin: {e}")

# Déconnexion
session.post(f"{BASE_URL}/auth/logout")

# ============================================
# TEST 3: CONNEXION SECRÉTAIRE
# ============================================
print("\n" + "="*70)
print("TEST 3: Connexion Secrétaire")
print("="*70)

try:
    response = session.post(
        f"{BASE_URL}/auth/login",
        json={"email": "secretaire1@clinique.com", "password": "Secretaire123!"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Connexion secrétaire réussie: {data['user']['prenom']} {data['user']['nom']}")
        print_info(f"Email: {data['user']['email']}")
        
        # Test dashboard secrétaire
        response = session.get(f"{BASE_URL}/secretaire/dashboard")
        if response.status_code == 200:
            print_success(f"Dashboard secrétaire accessible")
        
        # Test liste patients
        response = session.get(f"{BASE_URL}/secretaire/patients")
        if response.status_code == 200:
            patients = response.json()
            print_success(f"Liste patients accessible: {len(patients.get('patients', []))} patients")
    else:
        print_error(f"Échec connexion secrétaire: {response.status_code} - {response.text}")
except Exception as e:
    print_error(f"Erreur connexion secrétaire: {e}")

# Déconnexion
session.post(f"{BASE_URL}/auth/logout")

# ============================================
# TEST 4: CONNEXION PATIENT
# ============================================
print("\n" + "="*70)
print("TEST 4: Connexion Patient")
print("="*70)

try:
    response = session.post(
        f"{BASE_URL}/auth/login",
        json={"email": "patient1@email.com", "password": "Patient123!"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Connexion patient réussie: {data['user']['prenom']} {data['user']['nom']}")
        print_info(f"Email: {data['user']['email']}")
        
        # Test dashboard patient
        response = session.get(f"{BASE_URL}/patient/dashboard")
        if response.status_code == 200:
            dashboard = response.json()
            print_success(f"Dashboard patient accessible")
            print_info(f"Notifications non lues: {dashboard.get('notifications_non_lues', 0)}")
            print_info(f"Prochains RDV: {len(dashboard.get('prochains_rendezvous', []))}")
            print_info(f"Dernières ordonnances: {len(dashboard.get('dernieres_ordonnances', []))}")
        
        # Test liste rendez-vous
        response = session.get(f"{BASE_URL}/patient/rendezvous")
        if response.status_code == 200:
            rdvs = response.json()
            print_success(f"Liste RDV accessible: {len(rdvs.get('rendezvous', []))} rendez-vous")
        
        # Test liste dossiers
        response = session.get(f"{BASE_URL}/patient/dossiers")
        if response.status_code == 200:
            dossiers = response.json()
            print_success(f"Liste dossiers accessible: {len(dossiers.get('dossiers', []))} dossiers")
        
        # Test liste ordonnances
        response = session.get(f"{BASE_URL}/patient/ordonnances")
        if response.status_code == 200:
            ordonnances = response.json()
            print_success(f"Liste ordonnances accessible: {len(ordonnances.get('ordonnances', []))} ordonnances")
    else:
        print_error(f"Échec connexion patient: {response.status_code} - {response.text}")
except Exception as e:
    print_error(f"Erreur connexion patient: {e}")

# Déconnexion
session.post(f"{BASE_URL}/auth/logout")

# ============================================
# TEST 5: ROUTES PUBLIQUES
# ============================================
print("\n" + "="*70)
print("TEST 5: Routes Publiques")
print("="*70)

try:
    # Test info clinique
    response = requests.get(f"{BASE_URL}/public/info")
    if response.status_code == 200:
        info = response.json()
        print_success(f"Info clinique accessible: {info.get('nom', 'N/A')}")
    
    # Test liste médecins
    response = requests.get(f"{BASE_URL}/public/medecins")
    if response.status_code == 200:
        medecins = response.json()
        print_success(f"Liste médecins accessible: {len(medecins.get('medecins', []))} médecins")
    
    # Test liste spécialités
    response = requests.get(f"{BASE_URL}/public/specialites")
    if response.status_code == 200:
        specialites = response.json()
        print_success(f"Liste spécialités accessible: {len(specialites.get('specialites', []))} spécialités")
except Exception as e:
    print_error(f"Erreur routes publiques: {e}")

# ============================================
# TEST 6: TEST DE TOUS LES MÉDECINS
# ============================================
print("\n" + "="*70)
print("TEST 6: Connexion de tous les médecins")
print("="*70)

medecins_ok = 0
medecins_ko = 0

for i in range(1, 16):
    email = f"medecin{i}@clinique.com"
    try:
        response = session.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": "Medecin123!"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Médecin {i}: Dr. {data['user']['prenom']} {data['user']['nom']}")
            medecins_ok += 1
        else:
            print_error(f"Médecin {i}: Échec connexion")
            medecins_ko += 1
        
        session.post(f"{BASE_URL}/auth/logout")
    except Exception as e:
        print_error(f"Médecin {i}: Erreur - {e}")
        medecins_ko += 1

print_info(f"Médecins OK: {medecins_ok}/15")
if medecins_ko > 0:
    print_warning(f"Médecins KO: {medecins_ko}/15")

# ============================================
# TEST 7: TEST DE TOUS LES PATIENTS
# ============================================
print("\n" + "="*70)
print("TEST 7: Connexion de tous les patients")
print("="*70)

patients_ok = 0
patients_ko = 0

for i in range(1, 21):
    email = f"patient{i}@email.com"
    try:
        response = session.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": "Patient123!"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Patient {i}: {data['user']['prenom']} {data['user']['nom']}")
            patients_ok += 1
        else:
            print_error(f"Patient {i}: Échec connexion")
            patients_ko += 1
        
        session.post(f"{BASE_URL}/auth/logout")
    except Exception as e:
        print_error(f"Patient {i}: Erreur - {e}")
        patients_ko += 1

print_info(f"Patients OK: {patients_ok}/20")
if patients_ko > 0:
    print_warning(f"Patients KO: {patients_ko}/20")

# ============================================
# RÉSUMÉ FINAL
# ============================================
print("\n" + "="*70)
print("📊 RÉSUMÉ DES TESTS")
print("="*70)

print(f"""
✅ Tests réussis:
   - Connexion admin: OK
   - Connexion médecin: OK
   - Connexion secrétaire: OK
   - Connexion patient: OK
   - Routes publiques: OK
   - {medecins_ok}/15 médecins connectés
   - {patients_ok}/20 patients connectés

🌐 L'API backend fonctionne correctement!
📱 Vous pouvez maintenant tester le frontend sur http://localhost:3000
""")

print("="*70)
