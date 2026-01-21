"""
Contrôleur public - Informations accessibles sans authentification
"""

from flask import Blueprint, jsonify, request
from models.medecin import Medecin
from models.user import User
from models.rendezvous import RendezVous
from datetime import datetime, timedelta

bp = Blueprint('public', __name__)

@bp.route('/info', methods=['GET'])
def get_clinic_info():
    """
    Endpoint pour récupérer les informations publiques de la clinique
    """
    try:
        from config.database import get_db
        db = get_db()
        
        # Récupérer la configuration depuis la base de données
        config = db.clinique_config.find_one({})
        
        if not config:
            # Configuration par défaut si aucune config n'existe
            clinic_info = {
                'nom': 'Clinique Médicale',
                'description': 'Votre santé est notre priorité. Nous offrons des soins médicaux de qualité avec une équipe de professionnels expérimentés.',
                'adresse': '123 Rue de la Santé, 75000 Paris',
                'telephone': '+33 1 23 45 67 89',
                'email': 'contact@clinique-medicale.fr',
                'horaires': {
                    'lundi': '08:00 - 18:00',
                    'mardi': '08:00 - 18:00',
                    'mercredi': '08:00 - 18:00',
                    'jeudi': '08:00 - 18:00',
                    'vendredi': '08:00 - 18:00',
                    'samedi': '09:00 - 13:00',
                    'dimanche': 'Fermé'
                },
                'services': [
                    'Consultation générale',
                    'Médecine spécialisée',
                    'Examens médicaux',
                    'Suivi médical',
                    'Urgences'
                ]
            }
        else:
            # Utiliser la configuration de la base de données
            clinic_info = {
                'nom': config.get('nom', 'Clinique Médicale'),
                'description': config.get('description', ''),
                'adresse': config.get('adresse', ''),
                'telephone': config.get('telephone', ''),
                'email': config.get('email', ''),
                'horaires': config.get('horaires', {}),
                'services': config.get('services', [])
            }
        
        return jsonify(clinic_info), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des informations: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/medecins', methods=['GET'])
def get_medecins():
    """
    Endpoint pour récupérer la liste des médecins disponibles
    """
    try:
        specialite = request.args.get('specialite')
        
        if specialite:
            medecins = Medecin.find_by_specialite(specialite)
        else:
            medecins = Medecin.find_all()
        
        medecins_list = []
        for medecin in medecins:
            user = User.find_by_id(medecin.user_id)
            if user and user.is_active:
                medecins_list.append({
                    '_id': str(medecin._id),
                    'user_id': str(medecin.user_id),
                    'nom': user.nom,
                    'prenom': user.prenom,
                    'specialite': medecin.specialite,
                    'numero_ordre': medecin.numero_ordre
                })
        
        return jsonify({'medecins': medecins_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des médecins: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/medecins/<medecin_id>/disponibilite', methods=['GET'])
def get_medecin_disponibilite(medecin_id):
    """
    Récupère les créneaux disponibles pour un médecin
    """
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({'error': 'Date requise'}), 400
        
        # Parser la date
        try:
            date_obj = datetime.fromisoformat(date_str.split('T')[0])
        except:
            return jsonify({'error': 'Format de date invalide'}), 400
        
        # Récupérer les rendez-vous du médecin pour cette date
        rdvs = RendezVous.find_by_date(date_obj, medecin_id)
        heures_prises = [rdv.heure_rdv for rdv in rdvs if rdv.statut in ['confirme', 'demande']]
        
        # Générer les créneaux disponibles (exemple: 8h-18h, toutes les 30 minutes)
        creneaux_disponibles = []
        heures_debut = 8
        heures_fin = 18
        
        for heure in range(heures_debut, heures_fin):
            for minute in [0, 30]:
                heure_str = f"{heure:02d}:{minute:02d}"
                if heure_str not in heures_prises:
                    creneaux_disponibles.append(heure_str)
        
        return jsonify({
            'date': date_str,
            'medecin_id': medecin_id,
            'creneaux_disponibles': creneaux_disponibles
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération de la disponibilité: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/specialites', methods=['GET'])
def get_specialites():
    """
    Endpoint pour récupérer la liste des spécialités disponibles
    """
    try:
        # Liste des spécialités (peut être stockée en base de données)
        specialites = [
            'Médecine générale',
            'Cardiologie',
            'Dermatologie',
            'Endocrinologie',
            'Gastro-entérologie',
            'Gynécologie',
            'Neurologie',
            'Ophtalmologie',
            'Orthopédie',
            'Pédiatrie',
            'Pneumologie',
            'Psychiatrie',
            'Radiologie',
            'Rhumatologie',
            'Urologie'
        ]
        
        return jsonify({'specialites': specialites}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des spécialités: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500
