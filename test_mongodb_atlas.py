"""
Script pour tester la connexion à MongoDB Atlas
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Charger les variables d'environnement
load_dotenv()

def test_mongodb_connection():
    """Teste la connexion à MongoDB Atlas"""
    print("\n" + "="*60)
    print("🧪 TEST DE CONNEXION MONGODB ATLAS")
    print("="*60 + "\n")
    
    # Récupérer l'URI
    mongodb_uri = os.getenv('MONGODB_URI')
    mongodb_db = os.getenv('MONGODB_DB_NAME', 'clinique_db')
    
    if not mongodb_uri:
        print("❌ MONGODB_URI non trouvé dans .env")
        return False
    
    print(f"📍 URI: {mongodb_uri[:50]}...")
    print(f"📍 Database: {mongodb_db}\n")
    
    try:
        # Créer le client MongoDB
        print("⏳ Connexion à MongoDB Atlas...")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Tester la connexion
        client.admin.command('ping')
        print("✅ Connexion réussie!\n")
        
        # Obtenir la base de données
        db = client[mongodb_db]
        
        # Lister les collections
        print("📊 Collections existantes:")
        collections = db.list_collection_names()
        if collections:
            for collection in collections:
                count = db[collection].count_documents({})
                print(f"   - {collection}: {count} documents")
        else:
            print("   (Aucune collection - base de données vide)")
        
        print("\n" + "="*60)
        print("✅ TEST RÉUSSI - MongoDB Atlas fonctionne!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR DE CONNEXION:")
        print(f"   {str(e)}\n")
        
        print("🔧 SOLUTIONS POSSIBLES:")
        print("   1. Vérifier que l'URI est correct dans .env")
        print("   2. Vérifier que 0.0.0.0/0 est autorisé dans MongoDB Atlas")
        print("   3. Vérifier que le mot de passe est correct")
        print("   4. Vérifier votre connexion Internet\n")
        
        print("="*60 + "\n")
        return False

if __name__ == "__main__":
    test_mongodb_connection()
