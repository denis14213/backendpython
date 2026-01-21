"""
Contrôleur Admin - Gestion complète du système
"""

from flask import Blueprint, request, jsonify
from models.user import User
from models.patient import Patient
from models.rendezvous import RendezVous
from models.medecin import Medecin
from models.dossier_medical import DossierMedical
from models.ordonnance import Ordonnance
from services.email_service import EmailService
import secrets
import string
from datetime import datetime
from bson import ObjectId

bp = Blueprint('admin', __name__)

def generate_temp_password(length=12):
    """Génère un mot de passe temporaire"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

@bp.route('/users', methods=['GET'])
def get_all_users():
    """
    Récupère tous les utilisateurs avec filtres
    """
    try:
        role = request.args.get('role')
        is_active = request.args.get('is_active')
        
        is_active_bool = None
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
        
        users = User.find_all(role=role, is_active=is_active_bool)
        
        users_list = [user.to_dict() for user in users]
        
        return jsonify({'users': users_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des utilisateurs: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/users', methods=['POST'])
def create_user():
    """
    Crée un nouvel utilisateur (médecin ou secrétaire)
    
    Body JSON:
        email, password, role, nom, prenom, telephone
        specialite (si medecin), numero_ordre (si medecin)
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        nom = data.get('nom')
        prenom = data.get('prenom')
        telephone = data.get('telephone')
        
        if not email or not role:
            return jsonify({'error': 'Email et rôle requis'}), 400
        
        if role not in ['admin', 'medecin', 'secretaire']:
            return jsonify({'error': 'Rôle invalide'}), 400
        
        # Vérifier si l'email existe déjà
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify({'error': 'Cet email est déjà utilisé'}), 400
        
        # Générer un mot de passe si non fourni
        if not password:
            password = generate_temp_password()
        
        # Création de l'utilisateur
        user = User(
            email=email,
            password=password,
            role=role,
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            is_active=True
        )
        
        user_id = user.save()
        
        # Si c'est un médecin, créer l'entrée dans la collection medecins
        if role == 'medecin':
            specialite = data.get('specialite', 'Médecine générale')
            numero_ordre = data.get('numero_ordre')
            
            medecin = Medecin(
                user_id=user_id,
                specialite=specialite,
                numero_ordre=numero_ordre
            )
            medecin.save()
        
        # Envoi des identifiants par email
        try:
            email_service = EmailService()
            email_service.send_account_credentials(email, nom or '', prenom or '', email, password)
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            # Ne pas bloquer la création si l'email échoue
        
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'user': user.to_dict(),
            'password': password  # Retourner le mot de passe pour l'affichage (optionnel)
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur: {e}")
        return jsonify({'error': 'Erreur serveur lors de la création'}), 500

@bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Met à jour un utilisateur
    """
    try:
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404
        
        data = request.get_json()
        
        if 'nom' in data:
            user.nom = data['nom']
        if 'prenom' in data:
            user.prenom = data['prenom']
        if 'telephone' in data:
            user.telephone = data['telephone']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        # Si c'est un médecin, mettre à jour les infos du médecin
        if user.role == 'medecin' and data.get('specialite'):
            medecin = Medecin.find_by_user_id(user_id)
            if medecin:
                medecin.specialite = data.get('specialite', medecin.specialite)
                medecin.numero_ordre = data.get('numero_ordre', medecin.numero_ordre)
                medecin.update()
        
        user.update()
        
        return jsonify({
            'message': 'Utilisateur mis à jour avec succès',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour de l'utilisateur: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Désactive un utilisateur (soft delete)
    """
    try:
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404
        
        user.is_active = False
        user.update()
        
        return jsonify({'message': 'Utilisateur désactivé avec succès'}), 200
        
    except Exception as e:
        print(f"Erreur lors de la désactivation de l'utilisateur: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/users/<user_id>/reset-password', methods=['POST'])
def reset_user_password(user_id):
    """
    Réinitialise le mot de passe d'un utilisateur
    """
    try:
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404
        
        new_password = generate_temp_password()
        user.reset_password(new_password)
        
        # Envoi du nouveau mot de passe par email
        try:
            email_service = EmailService()
            email_service.send_account_credentials(
                user.email,
                user.nom or '',
                user.prenom or '',
                user.email,
                new_password
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
        
        return jsonify({
            'message': 'Mot de passe réinitialisé et envoyé par email',
            'password': new_password  # Retourner pour affichage si nécessaire
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la réinitialisation du mot de passe: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/statistiques', methods=['GET'])
def get_statistiques():
    """
    Récupère les statistiques globales de la clinique
    """
    try:
        from config.database import get_db
        db = get_db()
        
        # Nombre total de patients
        total_patients = db.patients.count_documents({})
        patients_actifs = db.patients.count_documents({'user_id': {'$ne': None}})
        
        # Nombre total d'utilisateurs par rôle
        total_admins = db.users.count_documents({'role': 'admin'})
        total_medecins = db.users.count_documents({'role': 'medecin', 'is_active': True})
        total_secretaires = db.users.count_documents({'role': 'secretaire', 'is_active': True})
        total_patients_users = db.users.count_documents({'role': 'patient', 'is_active': True})
        
        # Nombre de rendez-vous
        total_rdv = db.rendezvous.count_documents({})
        rdv_aujourdhui = db.rendezvous.count_documents({
            'date_rdv': {
                '$gte': datetime.combine(datetime.now().date(), datetime.min.time()),
                '$lte': datetime.combine(datetime.now().date(), datetime.max.time())
            }
        })
        
        # Nombre de consultations ce mois
        debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        consultations_mois = db.dossiers_medicaux.count_documents({
            'date_consultation': {'$gte': debut_mois}
        })
        
        # Consultations cette semaine
        from datetime import timedelta
        debut_semaine = datetime.now() - timedelta(days=datetime.now().weekday())
        debut_semaine = debut_semaine.replace(hour=0, minute=0, second=0, microsecond=0)
        consultations_semaine = db.dossiers_medicaux.count_documents({
            'date_consultation': {'$gte': debut_semaine}
        })
        
        # Rendez-vous par statut
        rdv_confirme = db.rendezvous.count_documents({'statut': 'confirme'})
        rdv_demande = db.rendezvous.count_documents({'statut': 'demande'})
        rdv_annule = db.rendezvous.count_documents({'statut': 'annule'})
        rdv_en_attente = rdv_demande
        
        stats = {
            'patients': {
                'total': total_patients,
                'actifs': patients_actifs,
                'avec_compte': total_patients_users
            },
            'utilisateurs': {
                'admins': total_admins,
                'medecins': total_medecins,
                'secretaires': total_secretaires,
                'patients': total_patients_users
            },
            'rendezvous': {
                'total': total_rdv,
                'aujourdhui': rdv_aujourdhui,
                'confirme': rdv_confirme,
                'demande': rdv_demande,
                'annule': rdv_annule,
                'en_attente': rdv_en_attente
            },
            'consultations': {
                'ce_mois': consultations_mois,
                'cette_semaine': consultations_semaine
            }
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/rendezvous', methods=['GET'])
def get_all_rendezvous():
    """
    Récupère tous les rendez-vous avec filtres
    """
    try:
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        statut = request.args.get('statut')
        
        from config.database import get_db
        db = get_db()
        
        query = {}
        if date_debut or date_fin:
            date_query = {}
            if date_debut:
                date_query['$gte'] = datetime.fromisoformat(date_debut)
            if date_fin:
                date_query['$lte'] = datetime.fromisoformat(date_fin)
            query['date_rdv'] = date_query
        
        if statut:
            query['statut'] = statut
        
        rdvs_data = db.rendezvous.find(query).sort('date_rdv', -1).limit(100)
        
        rdvs = []
        for rdv_data in rdvs_data:
            # Récupérer les informations du patient et du médecin
            patient = Patient.find_by_id(rdv_data['patient_id'])
            medecin_user = User.find_by_id(rdv_data['medecin_id'])
            
            rdv_dict = {
                '_id': str(rdv_data['_id']),
                'date_rdv': rdv_data['date_rdv'].isoformat() if isinstance(rdv_data['date_rdv'], datetime) else rdv_data['date_rdv'],
                'heure_rdv': rdv_data['heure_rdv'],
                'motif': rdv_data.get('motif'),
                'statut': rdv_data.get('statut'),
                'patient': {
                    'nom': patient.nom if patient else 'N/A',
                    'prenom': patient.prenom if patient else 'N/A',
                    'email': patient.email if patient else None
                } if patient else None,
                'medecin': {
                    'nom': medecin_user.nom if medecin_user else 'N/A',
                    'prenom': medecin_user.prenom if medecin_user else 'N/A'
                } if medecin_user else None
            }
            rdvs.append(rdv_dict)
        
        return jsonify({'rendezvous': rdvs}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des rendez-vous: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/specialites', methods=['GET'])
def get_specialites():
    """
    Récupère la liste des spécialités
    """
    try:
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

@bp.route('/specialites', methods=['POST'])
def create_specialite():
    """
    Ajoute une nouvelle spécialité (peut être étendu pour stocker en DB)
    """
    try:
        data = request.get_json()
        specialite = data.get('nom')
        
        if not specialite:
            return jsonify({'error': 'Nom de spécialité requis'}), 400
        
        # Pour l'instant, on retourne juste un message
        # En production, on pourrait stocker dans une collection spécialités
        return jsonify({
            'message': 'Spécialité ajoutée (à implémenter en base de données)',
            'specialite': specialite
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de la création de la spécialité: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/clinique', methods=['GET'])
def get_clinique_config():
    """
    Récupère la configuration de la clinique
    """
    try:
        from config.database import get_db
        db = get_db()
        
        # Récupérer ou créer la configuration
        config = db.clinique_config.find_one({})
        
        if not config:
            # Configuration par défaut
            default_config = {
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
            db.clinique_config.insert_one(default_config)
            config = default_config
            config['_id'] = str(config.get('_id', ''))
        else:
            config['_id'] = str(config['_id'])
        
        return jsonify({'config': config}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération de la configuration: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/clinique', methods=['PUT'])
def update_clinique_config():
    """
    Met à jour la configuration de la clinique
    """
    try:
        from config.database import get_db
        db = get_db()
        
        data = request.get_json()
        
        # Mettre à jour ou créer la configuration
        config = db.clinique_config.find_one({})
        
        if config:
            # Mise à jour
            update_data = {}
            if 'nom' in data:
                update_data['nom'] = data['nom']
            if 'description' in data:
                update_data['description'] = data['description']
            if 'adresse' in data:
                update_data['adresse'] = data['adresse']
            if 'telephone' in data:
                update_data['telephone'] = data['telephone']
            if 'email' in data:
                update_data['email'] = data['email']
            if 'horaires' in data:
                update_data['horaires'] = data['horaires']
            if 'services' in data:
                update_data['services'] = data['services']
            
            update_data['updated_at'] = datetime.utcnow()
            
            db.clinique_config.update_one({}, {'$set': update_data})
        else:
            # Création
            default_config = {
                'nom': data.get('nom', 'Clinique Médicale'),
                'description': data.get('description', ''),
                'adresse': data.get('adresse', ''),
                'telephone': data.get('telephone', ''),
                'email': data.get('email', ''),
                'horaires': data.get('horaires', {}),
                'services': data.get('services', []),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            db.clinique_config.insert_one(default_config)
        
        return jsonify({'message': 'Configuration mise à jour avec succès'}), 200
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la configuration: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500
