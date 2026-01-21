"""
Configuration et connexion à la base de données MongoDB
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

# Variables de connexion
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'clinique_db')

# Client MongoDB global
client = None
db = None

def init_db():
    """
    Initialise la connexion à MongoDB et crée les index nécessaires
    """
    global client, db
    
    try:
        # Connexion à MongoDB
        client = MongoClient(MONGODB_URI)
        
        # Test de connexion
        client.admin.command('ping')
        print("✅ Connexion à MongoDB réussie")
        
        # Sélection de la base de données
        db = client[MONGODB_DB_NAME]
        
        # Création des index pour optimiser les requêtes
        create_indexes()
        
        return db
        
    except ConnectionFailure as e:
        print(f"❌ Erreur de connexion à MongoDB: {e}")
        raise

def get_db():
    """
    Retourne l'instance de la base de données
    """
    global db
    if db is None:
        init_db()
    return db

def create_indexes():
    """
    Crée les index nécessaires pour optimiser les performances
    """
    global db
    if db is None:
        db = get_db()
    
    # Index pour la collection users
    db.users.create_index("email", unique=True)
    db.users.create_index("role")
    db.users.create_index("is_active")
    
    # Index pour la collection patients
    db.patients.create_index("email", unique=True)
    db.patients.create_index("telephone")
    db.patients.create_index("created_at")
    
    # Index pour la collection rendezvous
    db.rendezvous.create_index("medecin_id")
    db.rendezvous.create_index("patient_id")
    db.rendezvous.create_index("date_rdv")
    db.rendezvous.create_index([("medecin_id", 1), ("date_rdv", 1)])
    
    # Index pour la collection dossiers_medicaux
    db.dossiers_medicaux.create_index("patient_id")
    db.dossiers_medicaux.create_index("medecin_id")
    db.dossiers_medicaux.create_index("date_consultation")
    
    # Index pour la collection ordonnances
    db.ordonnances.create_index("patient_id")
    db.ordonnances.create_index("medecin_id")
    db.ordonnances.create_index("date_ordonnance")
    
    # Index pour la collection documents_medicaux
    db.documents_medicaux.create_index("patient_id")
    db.documents_medicaux.create_index("dossier_id")
    
    # Index pour la collection notifications
    db.notifications.create_index("user_id")
    db.notifications.create_index("is_read")
    db.notifications.create_index("created_at")
    
    # Index pour la collection clinique_config (si elle existe)
    if 'clinique_config' in db.list_collection_names():
        db.clinique_config.create_index("updated_at")
    
    print("✅ Index MongoDB créés avec succès")

