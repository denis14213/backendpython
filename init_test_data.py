"""
Script d'initialisation des données de test
Crée des utilisateurs, patients, rendez-vous, ordonnances, etc.
"""

from models.user import User
from models.patient import Patient
from models.medecin import Medecin
from models.rendezvous import RendezVous
from models.dossier_medical import DossierMedical
from models.ordonnance import Ordonnance
from models.notification import Notification
from config.database import init_db
from datetime import datetime, timedelta
import random

# Initialiser la base de données
init_db()

print("🚀 Initialisation des données de test...")

# ============================================
# 1. CRÉER L'ADMINISTRATEUR
# ============================================
print("\n📋 Création de l'administrateur...")

admin_email = "admin@clinique.com"
existing_admin = User.find_by_email(admin_email)

if existing_admin:
    print(f"✅ Admin existe déjà: {admin_email}")
    admin = existing_admin
else:
    admin = User(
        email=admin_email,
        password="Admin123!",
        role="admin",
        nom="Administrateur",
        prenom="Système",
        telephone="+216 1 23 45 67 89",
        is_active=True
    )
    admin.save()
    print(f"✅ Admin créé: {admin_email} / Admin123!")

# ============================================
# 2. CRÉER LES MÉDECINS
# ============================================
print("\n👨‍⚕️ Création des médecins...")

specialites = [
    "Médecine générale",
    "Cardiologie",
    "Dermatologie",
    "Endocrinologie",
    "Gastro-entérologie",
    "Gynécologie",
    "Neurologie",
    "Ophtalmologie",
    "Orthopédie",
    "Pédiatrie",
    "Pneumologie",
    "Psychiatrie",
    "Radiologie",
    "Rhumatologie",
    "Urologie"
]

medecins_data = [
    {"nom": "Dupont", "prenom": "Jean", "specialite": "Médecine générale"},
    {"nom": "Martin", "prenom": "Sophie", "specialite": "Cardiologie"},
    {"nom": "Bernard", "prenom": "Pierre", "specialite": "Dermatologie"},
    {"nom": "Dubois", "prenom": "Marie", "specialite": "Endocrinologie"},
    {"nom": "Thomas", "prenom": "Luc", "specialite": "Gastro-entérologie"},
    {"nom": "Robert", "prenom": "Claire", "specialite": "Gynécologie"},
    {"nom": "Petit", "prenom": "François", "specialite": "Neurologie"},
    {"nom": "Richard", "prenom": "Anne", "specialite": "Ophtalmologie"},
    {"nom": "Durand", "prenom": "Michel", "specialite": "Orthopédie"},
    {"nom": "Leroy", "prenom": "Isabelle", "specialite": "Pédiatrie"},
    {"nom": "Moreau", "prenom": "Philippe", "specialite": "Pneumologie"},
    {"nom": "Simon", "prenom": "Catherine", "specialite": "Psychiatrie"},
    {"nom": "Laurent", "prenom": "David", "specialite": "Radiologie"},
    {"nom": "Lefebvre", "prenom": "Nathalie", "specialite": "Rhumatologie"},
    {"nom": "Michel", "prenom": "Olivier", "specialite": "Urologie"}
]

medecins_ids = []

for i, med_data in enumerate(medecins_data):
    email = f"medecin{i+1}@clinique.com"
    existing_user = User.find_by_email(email)
    
    if existing_user:
        print(f"✅ Médecin existe: Dr. {med_data['prenom']} {med_data['nom']}")
        medecins_ids.append(str(existing_user._id))
        continue
    
    # Créer l'utilisateur médecin
    user = User(
        email=email,
        password="Medecin123!",
        role="medecin",
        nom=med_data["nom"],
        prenom=med_data["prenom"],
        telephone=f"+216 6 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}",
        is_active=True
    )
    user_id = user.save()
    medecins_ids.append(user_id)
    
    # Créer le profil médecin
    medecin = Medecin(
        user_id=user_id,
        specialite=med_data["specialite"],
        numero_ordre=f"ORD{random.randint(100000, 999999)}",
        horaires_travail={
            "lundi": "08:00-18:00",
            "mardi": "08:00-18:00",
            "mercredi": "08:00-18:00",
            "jeudi": "08:00-18:00",
            "vendredi": "08:00-18:00",
            "samedi": "09:00-13:00"
        }
    )
    medecin.save()
    
    print(f"✅ Médecin créé: Dr. {med_data['prenom']} {med_data['nom']} ({med_data['specialite']}) - {email} / Medecin123!")

# ============================================
# 3. CRÉER LES SECRÉTAIRES
# ============================================
print("\n👩‍💼 Création des secrétaires...")

secretaires_data = [
    {"nom": "Lefevre", "prenom": "Julie"},
    {"nom": "Garnier", "prenom": "Émilie"},
    {"nom": "Rousseau", "prenom": "Sandrine"}
]

secretaires_ids = []

for i, sec_data in enumerate(secretaires_data):
    email = f"secretaire{i+1}@clinique.com"
    existing_user = User.find_by_email(email)
    
    if existing_user:
        print(f"✅ Secrétaire existe: {sec_data['prenom']} {sec_data['nom']}")
        secretaires_ids.append(str(existing_user._id))
        continue
    
    user = User(
        email=email,
        password="Secretaire123!",
        role="secretaire",
        nom=sec_data["nom"],
        prenom=sec_data["prenom"],
        telephone=f"+216 6 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}",
        is_active=True
    )
    user_id = user.save()
    secretaires_ids.append(user_id)
    
    print(f"✅ Secrétaire créée: {sec_data['prenom']} {sec_data['nom']} - {email} / Secretaire123!")

# ============================================
# 4. CRÉER LES PATIENTS
# ============================================
print("\n🧑‍🤝‍🧑 Création des patients...")

patients_data = [
    {"nom": "Dubois", "prenom": "Alexandre", "sexe": "M", "date_naissance": "1985-03-15"},
    {"nom": "Lefebvre", "prenom": "Camille", "sexe": "F", "date_naissance": "1990-07-22"},
    {"nom": "Moreau", "prenom": "Lucas", "sexe": "M", "date_naissance": "1978-11-08"},
    {"nom": "Girard", "prenom": "Emma", "sexe": "F", "date_naissance": "1995-02-14"},
    {"nom": "Roux", "prenom": "Thomas", "sexe": "M", "date_naissance": "1982-09-30"},
    {"nom": "Fournier", "prenom": "Léa", "sexe": "F", "date_naissance": "1988-05-18"},
    {"nom": "Blanc", "prenom": "Hugo", "sexe": "M", "date_naissance": "1992-12-25"},
    {"nom": "Guerin", "prenom": "Chloé", "sexe": "F", "date_naissance": "1987-04-07"},
    {"nom": "Boyer", "prenom": "Nathan", "sexe": "M", "date_naissance": "1993-08-19"},
    {"nom": "Garnier", "prenom": "Manon", "sexe": "F", "date_naissance": "1991-01-11"},
    {"nom": "Chevalier", "prenom": "Antoine", "sexe": "M", "date_naissance": "1980-06-28"},
    {"nom": "Francois", "prenom": "Sarah", "sexe": "F", "date_naissance": "1994-10-03"},
    {"nom": "Legrand", "prenom": "Maxime", "sexe": "M", "date_naissance": "1986-03-21"},
    {"nom": "Mercier", "prenom": "Julie", "sexe": "F", "date_naissance": "1989-07-16"},
    {"nom": "Vincent", "prenom": "Julien", "sexe": "M", "date_naissance": "1983-11-29"},
    {"nom": "Rousseau", "prenom": "Laura", "sexe": "F", "date_naissance": "1996-02-08"},
    {"nom": "Picard", "prenom": "Nicolas", "sexe": "M", "date_naissance": "1981-05-14"},
    {"nom": "Giraud", "prenom": "Marine", "sexe": "F", "date_naissance": "1992-09-22"},
    {"nom": "Renard", "prenom": "Quentin", "sexe": "M", "date_naissance": "1988-12-05"},
    {"nom": "Arnaud", "prenom": "Pauline", "sexe": "F", "date_naissance": "1990-04-17"}
]

villes = ["Paris", "Tunis", "Sousse", "Toulouse", "Nice", "Nantes", "Strasbourg", "Bordeaux"]
patients_ids = []

for i, pat_data in enumerate(patients_data):
    email = f"patient{i+1}@email.com"
    
    # Vérifier si le patient existe déjà
    existing_patient = Patient.find_by_email(email)
    if existing_patient:
        print(f"✅ Patient existe: {pat_data['prenom']} {pat_data['nom']}")
        patients_ids.append(str(existing_patient._id))
        continue
    
    # Créer le compte utilisateur pour le patient
    existing_user = User.find_by_email(email)
    if not existing_user:
        user = User(
            email=email,
            password="Patient123!",
            role="patient",
            nom=pat_data["nom"],
            prenom=pat_data["prenom"],
            telephone=f"+216 6 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}",
            is_active=True
        )
        user_id = user.save()
    else:
        user_id = str(existing_user._id)
    
    # Créer le patient
    ville = random.choice(villes)
    patient = Patient(
        nom=pat_data["nom"],
        prenom=pat_data["prenom"],
        email=email,
        telephone=f"+216 6 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}",
        date_naissance=pat_data["date_naissance"],
        adresse=f"{random.randint(1, 200)} Rue de la Santé",
        ville=ville,
        code_postal=f"{random.randint(10000, 99999)}",
        sexe=pat_data["sexe"],
        numero_securite_sociale=f"{random.randint(1, 2)}{random.randint(10, 99)}{random.randint(10, 12)}{random.randint(10, 99)}{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(10, 99)}",
        user_id=user_id
    )
    patient_id = patient.save()
    patients_ids.append(patient_id)
    
    print(f"✅ Patient créé: {pat_data['prenom']} {pat_data['nom']} - {email} / Patient123!")

# ============================================
# 5. CRÉER DES RENDEZ-VOUS
# ============================================
print("\n📅 Création des rendez-vous...")

motifs = [
    "Consultation générale",
    "Suivi médical",
    "Contrôle de routine",
    "Douleurs abdominales",
    "Maux de tête",
    "Fatigue chronique",
    "Problèmes de sommeil",
    "Vaccination",
    "Renouvellement ordonnance",
    "Bilan de santé"
]

statuts = [RendezVous.STATUT_CONFIRME, RendezVous.STATUT_DEMANDE, RendezVous.STATUT_TERMINE]

# Créer des RDV pour les 30 prochains jours
rdv_count = 0
for i in range(40):
    patient_id = random.choice(patients_ids)
    medecin_id = random.choice(medecins_ids)
    
    # Date aléatoire dans les 30 prochains jours
    jours_offset = random.randint(-10, 30)
    date_rdv = datetime.utcnow() + timedelta(days=jours_offset)
    
    # Heure aléatoire entre 8h et 18h
    heure = random.randint(8, 17)
    minute = random.choice([0, 30])
    heure_rdv = f"{heure:02d}:{minute:02d}"
    
    # Vérifier la disponibilité
    if not RendezVous.check_disponibilite(medecin_id, date_rdv, heure_rdv):
        continue
    
    statut = random.choice(statuts)
    
    rdv = RendezVous(
        patient_id=patient_id,
        medecin_id=medecin_id,
        date_rdv=date_rdv,
        heure_rdv=heure_rdv,
        motif=random.choice(motifs),
        statut=statut,
        notes="Rendez-vous de test" if random.random() > 0.7 else None
    )
    rdv.save()
    rdv_count += 1

print(f"✅ {rdv_count} rendez-vous créés")

# ============================================
# 6. CRÉER DES DOSSIERS MÉDICAUX
# ============================================
print("\n📋 Création des dossiers médicaux...")

diagnostics = [
    "Grippe saisonnière",
    "Hypertension artérielle",
    "Diabète de type 2",
    "Asthme",
    "Migraine",
    "Gastrite",
    "Anxiété",
    "Lombalgie",
    "Rhinite allergique",
    "Infection urinaire"
]

observations_list = [
    "Patient en bonne santé générale",
    "Signes vitaux normaux",
    "Légère fatigue constatée",
    "Amélioration depuis la dernière consultation",
    "Symptômes persistants",
    "Bonne réponse au traitement",
    "Nécessite un suivi régulier",
    "Recommandation de repos"
]

dossiers_count = 0
for i in range(30):
    patient_id = random.choice(patients_ids)
    medecin_id = random.choice(medecins_ids)
    
    # Date de consultation dans le passé
    jours_offset = random.randint(1, 180)
    date_consultation = datetime.utcnow() - timedelta(days=jours_offset)
    
    dossier = DossierMedical(
        patient_id=patient_id,
        medecin_id=medecin_id,
        date_consultation=date_consultation,
        observations=random.choice(observations_list),
        diagnostic=random.choice(diagnostics),
        examen_clinique="Examen clinique complet réalisé",
        poids=random.randint(50, 100),
        taille=random.randint(150, 190),
        tension_arterielle=f"{random.randint(10, 14)}/{random.randint(6, 9)}",
        temperature=round(random.uniform(36.5, 37.5), 1)
    )
    dossier.save()
    dossiers_count += 1

print(f"✅ {dossiers_count} dossiers médicaux créés")

# ============================================
# 7. CRÉER DES ORDONNANCES
# ============================================
print("\n💊 Création des ordonnances...")

medicaments = [
    {"medicament": "Paracétamol 1000mg", "posologie": "1 comprimé 3 fois par jour", "duree": "5 jours"},
    {"medicament": "Ibuprofène 400mg", "posologie": "1 comprimé matin et soir", "duree": "7 jours"},
    {"medicament": "Amoxicilline 500mg", "posologie": "1 gélule 3 fois par jour", "duree": "7 jours"},
    {"medicament": "Doliprane 500mg", "posologie": "2 comprimés 3 fois par jour", "duree": "3 jours"},
    {"medicament": "Ventoline", "posologie": "2 bouffées si besoin", "duree": "1 mois"},
    {"medicament": "Oméprazole 20mg", "posologie": "1 gélule le matin à jeun", "duree": "30 jours"},
    {"medicament": "Loratadine 10mg", "posologie": "1 comprimé par jour", "duree": "15 jours"},
    {"medicament": "Metformine 500mg", "posologie": "1 comprimé matin et soir", "duree": "3 mois"}
]

instructions_list = [
    "À prendre pendant les repas",
    "À prendre à jeun",
    "Éviter l'alcool pendant le traitement",
    "Boire beaucoup d'eau",
    "Consulter si les symptômes persistent",
    "Respecter les doses prescrites",
    "Ne pas arrêter le traitement sans avis médical"
]

ordonnances_count = 0
for i in range(25):
    patient_id = random.choice(patients_ids)
    medecin_id = random.choice(medecins_ids)
    
    # Date dans le passé
    jours_offset = random.randint(1, 90)
    date_ordonnance = datetime.utcnow() - timedelta(days=jours_offset)
    
    # Sélectionner 1 à 3 médicaments
    nb_medicaments = random.randint(1, 3)
    traitements = random.sample(medicaments, nb_medicaments)
    
    ordonnance = Ordonnance(
        patient_id=patient_id,
        medecin_id=medecin_id,
        date_ordonnance=date_ordonnance,
        traitements=traitements,
        instructions=random.choice(instructions_list)
    )
    ordonnance.save()
    ordonnances_count += 1

print(f"✅ {ordonnances_count} ordonnances créées")

# ============================================
# 8. CRÉER DES NOTIFICATIONS
# ============================================
print("\n🔔 Création des notifications...")

notifications_count = 0
for patient_id in patients_ids[:10]:  # Notifications pour les 10 premiers patients
    patient = Patient.find_by_id(patient_id)
    if patient and patient.user_id:
        # Notification de bienvenue
        notif = Notification(
            user_id=str(patient.user_id),
            type_notification=Notification.TYPE_COMPTE_CREE,
            titre="Bienvenue à la Clinique Médicale",
            message="Votre compte a été créé avec succès. Vous pouvez maintenant prendre rendez-vous en ligne.",
            is_read=random.choice([True, False])
        )
        notif.save()
        notifications_count += 1

print(f"✅ {notifications_count} notifications créées")

# ============================================
# RÉSUMÉ
# ============================================
print("\n" + "="*60)
print("✅ INITIALISATION TERMINÉE")
print("="*60)
print(f"""
📊 RÉSUMÉ DES DONNÉES CRÉÉES:
- 1 Administrateur
- {len(medecins_ids)} Médecins
- {len(secretaires_ids)} Secrétaires
- {len(patients_ids)} Patients
- {rdv_count} Rendez-vous
- {dossiers_count} Dossiers médicaux
- {ordonnances_count} Ordonnances
- {notifications_count} Notifications

🔑 IDENTIFIANTS DE CONNEXION:

ADMINISTRATEUR:
  Email: admin@clinique.com
  Mot de passe: Admin123!

MÉDECINS (tous):
  Email: medecin1@clinique.com à medecin15@clinique.com
  Mot de passe: Medecin123!
  Exemple: medecin1@clinique.com / Medecin123!

SECRÉTAIRES:
  Email: secretaire1@clinique.com à secretaire3@clinique.com
  Mot de passe: Secretaire123!

PATIENTS:
  Email: patient1@email.com à patient20@email.com
  Mot de passe: Patient123!
  Exemple: patient1@email.com / Patient123!

🌐 Vous pouvez maintenant tester l'application complète!
""")
