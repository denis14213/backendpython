"""
Script de nettoyage des anciens fichiers
Supprime les fichiers du dossier uploads/ qui ne sont plus utilisés
(tout est maintenant stocké dans MongoDB)
"""

import os
import shutil

def cleanup_uploads():
    """Supprime le dossier uploads/ et son contenu"""
    uploads_dir = 'uploads'
    
    if not os.path.exists(uploads_dir):
        print("✓ Le dossier uploads/ n'existe pas (déjà nettoyé)")
        return
    
    # Compter les fichiers
    file_count = 0
    for root, dirs, files in os.walk(uploads_dir):
        file_count += len(files)
    
    if file_count == 0:
        print("✓ Le dossier uploads/ est vide")
        try:
            shutil.rmtree(uploads_dir)
            print("✓ Dossier uploads/ supprimé")
        except Exception as e:
            print(f"⚠ Erreur lors de la suppression du dossier: {e}")
        return
    
    print(f"\n⚠ ATTENTION: {file_count} fichier(s) trouvé(s) dans uploads/")
    print("\nCes fichiers ne sont plus utilisés car tout est maintenant dans MongoDB.")
    print("Voulez-vous les supprimer? (o/n): ", end='')
    
    response = input().lower()
    
    if response == 'o' or response == 'oui':
        try:
            shutil.rmtree(uploads_dir)
            print(f"\n✅ {file_count} fichier(s) supprimé(s)")
            print("✅ Dossier uploads/ supprimé")
            print("\n✓ Nettoyage terminé!")
        except Exception as e:
            print(f"\n❌ Erreur lors de la suppression: {e}")
    else:
        print("\n⚠ Nettoyage annulé")
        print("Les fichiers restent dans uploads/ mais ne sont plus utilisés")

if __name__ == '__main__':
    print("="*60)
    print("🧹 NETTOYAGE DES ANCIENS FICHIERS")
    print("="*60)
    print("\nCe script supprime les anciens fichiers du dossier uploads/")
    print("car tout est maintenant stocké dans MongoDB.\n")
    
    cleanup_uploads()
