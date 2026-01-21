"""
Script de vérification des utilisateurs
Vérifie que tous les utilisateurs créés peuvent se connecter
"""

from models.user import User
from config.database import init_db

# Initialiser la base de données
init_db()

print("="*70)
print("🔍 VÉRIFICATION DES UTILISATEURS")
print("="*70)

# Liste des utilisateurs à tester
users_to_test = [
    {"email": "admin@clinique.com", "password": "Admin123!", "role": "admin"},
    {"email": "medecin1@clinique.com", "password": "Medecin123!", "role": "medecin"},
    {"email": "medecin2@clinique.com", "password": "Medecin123!", "role": "medecin"},
    {"email": "secretaire1@clinique.com", "password": "Secretaire123!", "role": "secretaire"},
    {"email": "patient1@email.com", "password": "Patient123!", "role": "patient"},
    {"email": "patient2@email.com", "password": "Patient123!", "role": "patient"},
]

print("\n📋 Test des utilisateurs créés par le script:\n")

success_count = 0
fail_count = 0

for user_data in users_to_test:
    email = user_data["email"]
    password = user_data["password"]
    expected_role = user_data["role"]
    
    # Chercher l'utilisateur
    user = User.find_by_email(email)
    
    if not user:
        print(f"❌ {email} - Utilisateur NON TROUVÉ")
        fail_count += 1
        continue
    
    # Vérifier le mot de passe
    if user.verify_password(password):
        print(f"✅ {email} - Mot de passe OK - Rôle: {user.role}")
        success_count += 1
    else:
        print(f"❌ {email} - Mot de passe INCORRECT")
        fail_count += 1

print("\n" + "="*70)
print(f"📊 RÉSULTAT: {success_count} OK / {fail_count} ÉCHEC")
print("="*70)

# Compter tous les utilisateurs
print("\n📊 STATISTIQUES GLOBALES:\n")

all_users = User.find_all()
print(f"Total utilisateurs: {len(all_users)}")

# Compter par rôle
admins = User.find_all(role='admin')
medecins = User.find_all(role='medecin')
secretaires = User.find_all(role='secretaire')
patients = User.find_all(role='patient')

print(f"  - Admins: {len(admins)}")
print(f"  - Médecins: {len(medecins)}")
print(f"  - Secrétaires: {len(secretaires)}")
print(f"  - Patients: {len(patients)}")

print("\n" + "="*70)
print("✅ VÉRIFICATION TERMINÉE")
print("="*70)

# Afficher les 5 premiers utilisateurs de chaque rôle
print("\n📋 LISTE DES UTILISATEURS PAR RÔLE:\n")

print("👨‍💼 ADMINS:")
for admin in admins[:5]:
    print(f"  - {admin.email} ({admin.prenom} {admin.nom})")

print("\n👨‍⚕️ MÉDECINS (5 premiers):")
for medecin in medecins[:5]:
    print(f"  - {medecin.email} ({medecin.prenom} {medecin.nom})")

print("\n👩‍💼 SECRÉTAIRES:")
for secretaire in secretaires[:5]:
    print(f"  - {secretaire.email} ({secretaire.prenom} {secretaire.nom})")

print("\n🧑‍🤝‍🧑 PATIENTS (5 premiers):")
for patient in patients[:5]:
    print(f"  - {patient.email} ({patient.prenom} {patient.nom})")

print("\n" + "="*70)
