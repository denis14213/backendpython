"""
Test de création de dossier médical
"""
import requests
import json

# D'abord se connecter comme médecin
login_url = "http://localhost:5000/api/auth/login"
login_data = {
    "email": "medecin1@clinique.com",
    "password": "Medecin123!"
}

session = requests.Session()
login_response = session.post(login_url, json=login_data)
print(f"Login: {login_response.status_code}")
print(f"Response: {login_response.json()}")

if login_response.status_code == 200:
    # Récupérer les patients
    patients_url = "http://localhost:5000/api/medecin/patients"
    patients_response = session.get(patients_url)
    print(f"\nPatients: {patients_response.status_code}")
    patients = patients_response.json().get('patients', [])
    print(f"Nombre de patients: {len(patients)}")
    
    if patients:
        patient_id = patients[0]['_id']
        print(f"Patient ID: {patient_id}")
        
        # Créer un dossier médical
        dossier_url = "http://localhost:5000/api/medecin/dossiers"
        dossier_data = {
            "patient_id": patient_id,
            "date_consultation": "2026-01-21",
            "observations": "Test observations",
            "diagnostic": "Test diagnostic",
            "examen_clinique": "Test examen",
            "poids": "",  # String vide comme le frontend
            "taille": "",
            "tension_arterielle": "",
            "temperature": ""
        }
        
        print(f"\nCréation dossier avec données: {json.dumps(dossier_data, indent=2)}")
        dossier_response = session.post(dossier_url, json=dossier_data)
        print(f"Status: {dossier_response.status_code}")
        print(f"Response: {dossier_response.text}")
