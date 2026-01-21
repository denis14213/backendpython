"""
Script de vérification de l'installation
Vérifie que toutes les dépendances sont installées et que la configuration est correcte
"""

import sys
import os

def check_python_version():
    """Vérifie la version de Python"""
    print("🔍 Vérification de Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Version 3.8+ requise")
        return False

def check_dependencies():
    """Vérifie que les dépendances sont installées"""
    print("\n🔍 Vérification des dépendances...")
    required_packages = [
        'flask',
        'flask_cors',
        'flask_session',
        'pymongo',
        'bcrypt',
        'dotenv',
        'reportlab'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'flask_cors':
                __import__('flask_cors')
            elif package == 'flask_session':
                __import__('flask_session')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✅ {package} - Installé")
        except ImportError:
            print(f"❌ {package} - Manquant")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Packages manquants: {', '.join(missing)}")
        print("Installez-les avec: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Vérifie que le fichier .env existe"""
    print("\n🔍 Vérification du fichier .env...")
    if os.path.exists('.env'):
        print("✅ Fichier .env trouvé")
        return True
    else:
        print("⚠️  Fichier .env non trouvé")
        print("Créez un fichier .env à partir de .env.example")
        return False

def check_mongodb_connection():
    """Vérifie la connexion à MongoDB"""
    print("\n🔍 Vérification de la connexion MongoDB...")
    try:
        from pymongo import MongoClient
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✅ Connexion à MongoDB réussie")
        client.close()
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à MongoDB: {e}")
        print("Vérifiez que MongoDB est démarré et que l'URI est correcte dans .env")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("VÉRIFICATION DE L'INSTALLATION - Backend Clinique Médicale")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_env_file(),
        check_mongodb_connection()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ Toutes les vérifications sont passées !")
        print("Vous pouvez maintenant lancer le serveur avec: python app.py")
    else:
        print("⚠️  Certaines vérifications ont échoué")
        print("Corrigez les problèmes ci-dessus avant de continuer")
    print("=" * 60)

if __name__ == '__main__':
    main()

