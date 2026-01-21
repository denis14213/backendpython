"""
Script d'initialisation pour créer le premier administrateur
Exécuter: python init_admin.py
"""

import sys
import os

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import init_db
from models.user import User

def create_admin():
    """
    Crée le premier administrateur du système
    """
    print("=" * 50)
    print("Création du compte administrateur")
    print("=" * 50)
    
    # Initialiser la base de données
    try:
        init_db()
        print("✅ Connexion à MongoDB réussie")
    except Exception as e:
        print(f"❌ Erreur de connexion à MongoDB: {e}")
        return
    
    # Vérifier si un admin existe déjà
    existing_admin = User.find_all(role='admin')
    if existing_admin:
        print("⚠️  Un administrateur existe déjà dans le système.")
        response = input("Voulez-vous créer un autre administrateur ? (o/n): ")
        if response.lower() != 'o':
            print("Opération annulée.")
            return
    
    # Demander les informations
    print("\nVeuillez entrer les informations de l'administrateur:")
    email = input("Email: ").strip()
    
    if not email:
        print("❌ L'email est requis")
        return
    
    # Vérifier si l'email existe déjà
    existing_user = User.find_by_email(email)
    if existing_user:
        print(f"❌ Un utilisateur avec l'email {email} existe déjà")
        return
    
    nom = input("Nom: ").strip()
    prenom = input("Prénom: ").strip()
    telephone = input("Téléphone (optionnel): ").strip() or None
    
    password = input("Mot de passe: ").strip()
    if not password:
        print("❌ Le mot de passe est requis")
        return
    
    if len(password) < 8:
        print("⚠️  Le mot de passe doit contenir au moins 8 caractères")
        response = input("Continuer quand même ? (o/n): ")
        if response.lower() != 'o':
            print("Opération annulée.")
            return
    
    # Créer l'administrateur
    try:
        admin = User(
            email=email,
            password=password,
            role='admin',
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            is_active=True
        )
        
        admin_id = admin.save()
        
        print("\n" + "=" * 50)
        print("✅ Administrateur créé avec succès !")
        print("=" * 50)
        print(f"ID: {admin_id}")
        print(f"Email: {email}")
        print(f"Nom: {prenom} {nom}")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'administrateur: {e}")

if __name__ == '__main__':
    create_admin()

