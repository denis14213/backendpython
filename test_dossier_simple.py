"""
Test simple de création de dossier
"""
from models.dossier_medical import DossierMedical
from datetime import datetime

try:
    print("Test de création de dossier médical...")
    
    dossier = DossierMedical(
        patient_id="697031984e3356fdc95fe020",
        medecin_id="6970318d4e3356fdc95fdfee",
        date_consultation=datetime(2026, 1, 21),
        observations="Test",
        diagnostic="Test",
        examen_clinique="Test",
        poids=None,
        taille=None,
        tension_arterielle=None,
        temperature=None
    )
    
    print("Dossier créé en mémoire")
    print(f"Dossier dict: {dossier.to_dict()}")
    
    dossier_id = dossier.save()
    print(f"✅ Dossier sauvegardé avec ID: {dossier_id}")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
