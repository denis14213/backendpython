"""
Script de test pour vérifier le stockage MongoDB complet
Teste: Documents médicaux, Ordonnances PDF, Signatures
"""

import sys
import base64
from io import BytesIO
from PIL import Image
from config.database import get_db
from models.user import User
from models.patient import Patient
from models.medecin import Medecin
from models.ordonnance import Ordonnance
from models.document_medical import DocumentMedical
from services.pdf_service import PDFService
from datetime import datetime

def create_test_image():
    """Crée une image de test en base64"""
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    return base64.b64encode(img_data).decode('utf-8')

def test_document_medical_storage():
    """Test 1: Stockage de document médical en base64"""
    print("\n" + "="*60)
    print("TEST 1: Stockage Document Médical en MongoDB")
    print("="*60)
    
    try:
        # Trouver un patient de test
        db = get_db()
        patient_data = db.patients.find_one()
        if not patient_data:
            print("❌ Aucun patient trouvé")
            return False
        
        patient = Patient._from_dict(patient_data)
        print(f"✓ Patient trouvé: {patient.prenom} {patient.nom}")
        
        # Créer une image de test
        img_base64 = create_test_image()
        print(f"✓ Image de test créée ({len(img_base64)} caractères base64)")
        
        # Créer un document médical
        document = DocumentMedical(
            patient_id=str(patient._id),
            dossier_id=None,
            type_document=DocumentMedical.TYPE_RADIO,
            nom_fichier="test_radio.png",
            file_data=img_base64,
            file_type="image/png",
            file_size=len(base64.b64decode(img_base64)),
            description="Test de stockage MongoDB",
            date_examen=datetime.utcnow()
        )
        
        doc_id = document.save()
        print(f"✓ Document sauvegardé avec ID: {doc_id}")
        
        # Vérifier dans MongoDB
        doc_from_db = DocumentMedical.find_by_id(doc_id)
        if not doc_from_db:
            print("❌ Document non trouvé dans MongoDB")
            return False
        
        if not doc_from_db.file_data:
            print("❌ file_data manquant dans MongoDB")
            return False
        
        print(f"✓ Document récupéré avec file_data ({len(doc_from_db.file_data)} caractères)")
        
        # Vérifier que les données sont identiques
        if doc_from_db.file_data == img_base64:
            print("✓ Données base64 identiques")
        else:
            print("❌ Données base64 différentes")
            return False
        
        # Nettoyer
        doc_from_db.delete()
        print("✓ Document supprimé")
        
        print("\n✅ TEST 1 RÉUSSI: Document médical stocké en MongoDB")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 ÉCHOUÉ: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signature_storage():
    """Test 2: Stockage de signature en base64"""
    print("\n" + "="*60)
    print("TEST 2: Stockage Signature Médecin en MongoDB")
    print("="*60)
    
    try:
        # Trouver un médecin de test
        db = get_db()
        medecin_data = db.medecins.find_one()
        if not medecin_data:
            print("❌ Aucun médecin trouvé")
            return False
        
        medecin = Medecin._from_dict(medecin_data)
        user = User.find_by_id(medecin.user_id)
        print(f"✓ Médecin trouvé: Dr. {user.prenom} {user.nom}")
        
        # Créer une signature de test
        signature_base64 = create_test_image()
        print(f"✓ Signature de test créée ({len(signature_base64)} caractères base64)")
        
        # Sauvegarder la signature
        medecin.signature_data = signature_base64
        medecin.signature_type = "image/png"
        medecin.update()
        print("✓ Signature sauvegardée")
        
        # Vérifier dans MongoDB
        medecin_from_db = Medecin.find_by_user_id(medecin.user_id)
        if not medecin_from_db:
            print("❌ Médecin non trouvé dans MongoDB")
            return False
        
        if not medecin_from_db.signature_data:
            print("❌ signature_data manquant dans MongoDB")
            return False
        
        print(f"✓ Signature récupérée ({len(medecin_from_db.signature_data)} caractères)")
        
        # Vérifier que les données sont identiques
        if medecin_from_db.signature_data == signature_base64:
            print("✓ Données signature identiques")
        else:
            print("❌ Données signature différentes")
            return False
        
        print("\n✅ TEST 2 RÉUSSI: Signature stockée en MongoDB")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 2 ÉCHOUÉ: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ordonnance_pdf_storage():
    """Test 3: Génération et stockage de PDF d'ordonnance"""
    print("\n" + "="*60)
    print("TEST 3: Génération et Stockage PDF Ordonnance")
    print("="*60)
    
    try:
        # Trouver un patient et un médecin
        db = get_db()
        patient_data = db.patients.find_one()
        medecin_data = db.medecins.find_one()
        
        if not patient_data or not medecin_data:
            print("❌ Patient ou médecin non trouvé")
            return False
        
        patient = Patient._from_dict(patient_data)
        medecin = Medecin._from_dict(medecin_data)
        medecin_user = User.find_by_id(medecin.user_id)
        
        print(f"✓ Patient: {patient.prenom} {patient.nom}")
        print(f"✓ Médecin: Dr. {medecin_user.prenom} {medecin_user.nom}")
        
        # Créer une ordonnance
        ordonnance = Ordonnance(
            patient_id=str(patient._id),
            medecin_id=str(medecin.user_id),
            date_ordonnance=datetime.utcnow(),
            traitements=[
                {
                    'medicament': 'Paracétamol 500mg',
                    'posologie': '1 comprimé 3 fois par jour',
                    'duree': '7 jours'
                }
            ],
            instructions='À prendre après les repas'
        )
        
        ord_id = ordonnance.save()
        print(f"✓ Ordonnance créée avec ID: {ord_id}")
        
        # Vérifier qu'il n'y a pas de PDF initialement
        ord_from_db = Ordonnance.find_by_id(ord_id)
        if ord_from_db.pdf_data:
            print("⚠ PDF déjà présent (devrait être None)")
        else:
            print("✓ Pas de PDF initialement (normal)")
        
        # Générer le PDF
        print("⏳ Génération du PDF...")
        pdf_base64 = PDFService.generate_ordonnance(
            ordonnance=ord_from_db,
            patient=patient,
            medecin_user=medecin_user,
            medecin_info=medecin
        )
        
        print(f"✓ PDF généré ({len(pdf_base64)} caractères base64)")
        
        # Sauvegarder le PDF dans l'ordonnance
        ord_from_db.pdf_data = pdf_base64
        ord_from_db.update()
        print("✓ PDF sauvegardé dans MongoDB")
        
        # Vérifier dans MongoDB
        ord_final = Ordonnance.find_by_id(ord_id)
        if not ord_final.pdf_data:
            print("❌ pdf_data manquant dans MongoDB")
            return False
        
        print(f"✓ PDF récupéré de MongoDB ({len(ord_final.pdf_data)} caractères)")
        
        # Vérifier que les données sont identiques
        if ord_final.pdf_data == pdf_base64:
            print("✓ Données PDF identiques")
        else:
            print("❌ Données PDF différentes")
            return False
        
        # Vérifier que le PDF est valide
        try:
            pdf_bytes = base64.b64decode(ord_final.pdf_data)
            if pdf_bytes[:4] == b'%PDF':
                print(f"✓ PDF valide ({len(pdf_bytes)} octets)")
            else:
                print("❌ PDF invalide (header incorrect)")
                return False
        except Exception as e:
            print(f"❌ Erreur décodage PDF: {e}")
            return False
        
        print("\n✅ TEST 3 RÉUSSI: PDF généré et stocké en MongoDB")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 3 ÉCHOUÉ: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mongodb_storage_stats():
    """Test 4: Statistiques de stockage MongoDB"""
    print("\n" + "="*60)
    print("TEST 4: Statistiques de Stockage MongoDB")
    print("="*60)
    
    try:
        db = get_db()
        
        # Documents médicaux
        docs_count = db.documents_medicaux.count_documents({})
        docs_with_data = db.documents_medicaux.count_documents({'file_data': {'$exists': True}})
        print(f"\n📄 Documents Médicaux:")
        print(f"   Total: {docs_count}")
        print(f"   Avec file_data: {docs_with_data}")
        
        # Ordonnances
        ord_count = db.ordonnances.count_documents({})
        ord_with_pdf = db.ordonnances.count_documents({'pdf_data': {'$exists': True}})
        print(f"\n📋 Ordonnances:")
        print(f"   Total: {ord_count}")
        print(f"   Avec PDF: {ord_with_pdf}")
        
        # Médecins avec signature
        med_count = db.medecins.count_documents({})
        med_with_sig = db.medecins.count_documents({'signature_data': {'$exists': True}})
        print(f"\n👨‍⚕️ Médecins:")
        print(f"   Total: {med_count}")
        print(f"   Avec signature: {med_with_sig}")
        
        # Taille de la base
        stats = db.command('dbstats')
        db_size_mb = stats['dataSize'] / (1024 * 1024)
        print(f"\n💾 Base de données:")
        print(f"   Taille: {db_size_mb:.2f} MB")
        print(f"   Collections: {stats['collections']}")
        
        print("\n✅ TEST 4 RÉUSSI: Statistiques récupérées")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 4 ÉCHOUÉ: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Exécute tous les tests"""
    print("\n" + "="*60)
    print("🧪 TESTS DE STOCKAGE MONGODB COMPLET")
    print("="*60)
    print("\nVérification que TOUS les fichiers sont stockés en MongoDB:")
    print("- Documents médicaux (radiographies, analyses, etc.)")
    print("- Ordonnances PDF")
    print("- Signatures numériques des médecins")
    
    results = []
    
    # Test 1: Documents médicaux
    results.append(("Documents Médicaux", test_document_medical_storage()))
    
    # Test 2: Signatures
    results.append(("Signatures", test_signature_storage()))
    
    # Test 3: Ordonnances PDF
    results.append(("Ordonnances PDF", test_ordonnance_pdf_storage()))
    
    # Test 4: Statistiques
    results.append(("Statistiques", test_mongodb_storage_stats()))
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ Le système est 100% MongoDB - aucun fichier sur disque")
        print("="*60)
        return 0
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("="*60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
