"""
Contrôleur Secrétaire - Gestion des patients et rendez-vous
"""

from flask import Blueprint, request, jsonify, session
from models.user import User
from models.patient import Patient
from models.rendezvous import RendezVous
from models.notification import Notification
from services.email_service import EmailService
from datetime import datetime
from bson import ObjectId
import secrets
import string

bp = Blueprint('secretaire', __name__)

def generate_temp_password(length=12):
    """Génère un mot de passe temporaire"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

@bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """
    Récupère les données du tableau de bord secrétaire
    """
    try:
        from config.database import get_db
        db = get_db()
        
        # Nombre de patients
        total_patients = db.patients.count_documents({})
        
        # Rendez-vous du jour
        rdv_aujourdhui = db.rendezvous.count_documents({
            'date_rdv': {
                '$gte': datetime.combine(datetime.now().date(), datetime.min.time()),
                '$lte': datetime.combine(datetime.now().date(), datetime.max.time())
            },
            'statut': {'$in': ['demande', 'confirme']}
        })
        
        # Rendez-vous en attente de confirmation
        rdv_en_attente = db.rendezvous.count_documents({'statut': 'demande'})
        
        dashboard = {
            'total_patients': total_patients,
            'rdv_aujourdhui': rdv_aujourdhui,
            'rdv_en_attente': rdv_en_attente
        }
        
        return jsonify(dashboard), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération du dashboard: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/patients', methods=['GET'])
def get_all_patients():
    """
    Récupère tous les patients avec pagination
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')
        
        skip = (page - 1) * limit
        
        if search:
            patients = Patient.search(search)
        else:
            patients = Patient.find_all(limit=limit, skip=skip)
        
        patients_list = [patient.to_dict() for patient in patients]
        
        return jsonify({
            'patients': patients_list,
            'page': page,
            'limit': limit,
            'total': len(patients_list)
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des patients: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """
    Récupère un patient par son ID
    """
    try:
        patient = Patient.find_by_id(patient_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        return jsonify({'patient': patient.to_dict()}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération du patient: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/patients', methods=['POST'])
def create_patient():
    """
    Crée un nouveau patient
    """
    try:
        data = request.get_json()
        
        if not data.get('nom') or not data.get('prenom'):
            return jsonify({'error': 'Nom et prénom requis'}), 400
        
        # Vérifier si le patient existe déjà (par email si fourni)
        if data.get('email'):
            existing_patient = Patient.find_by_email(data['email'])
            if existing_patient:
                return jsonify({'error': 'Un patient avec cet email existe déjà'}), 400
        
        patient = Patient(
            nom=data['nom'],
            prenom=data['prenom'],
            email=data.get('email'),
            telephone=data.get('telephone'),
            date_naissance=data.get('date_naissance'),
            adresse=data.get('adresse'),
            ville=data.get('ville'),
            code_postal=data.get('code_postal'),
            sexe=data.get('sexe'),
            numero_securite_sociale=data.get('numero_securite_sociale')
        )
        
        patient_id = patient.save()
        
        return jsonify({
            'message': 'Patient créé avec succès',
            'patient': patient.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de la création du patient: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/patients/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """
    Met à jour un patient
    """
    try:
        patient = Patient.find_by_id(patient_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        data = request.get_json()
        
        if 'nom' in data:
            patient.nom = data['nom']
        if 'prenom' in data:
            patient.prenom = data['prenom']
        if 'email' in data:
            patient.email = data['email']
        if 'telephone' in data:
            patient.telephone = data['telephone']
        if 'adresse' in data:
            patient.adresse = data['adresse']
        if 'ville' in data:
            patient.ville = data['ville']
        if 'code_postal' in data:
            patient.code_postal = data['code_postal']
        if 'sexe' in data:
            patient.sexe = data['sexe']
        if 'date_naissance' in data:
            patient.date_naissance = data['date_naissance']
        
        patient.update()
        
        return jsonify({
            'message': 'Patient mis à jour avec succès',
            'patient': patient.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du patient: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/patients/<patient_id>/compte', methods=['POST'])
def create_patient_account(patient_id):
    """
    Crée un compte utilisateur pour un patient
    """
    try:
        patient = Patient.find_by_id(patient_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        if not patient.email:
            return jsonify({'error': 'Le patient doit avoir un email pour créer un compte'}), 400
        
        # Vérifier si un compte existe déjà
        if patient.user_id:
            return jsonify({'error': 'Ce patient a déjà un compte utilisateur'}), 400
        
        existing_user = User.find_by_email(patient.email)
        if existing_user:
            return jsonify({'error': 'Un compte avec cet email existe déjà'}), 400
        
        # Générer un mot de passe temporaire
        temp_password = generate_temp_password()
        
        # Créer l'utilisateur
        user = User(
            email=patient.email,
            password=temp_password,
            role='patient',
            nom=patient.nom,
            prenom=patient.prenom,
            telephone=patient.telephone,
            is_active=True
        )
        
        user_id = user.save()
        
        # Lier le patient au compte utilisateur
        # user_id est déjà une string, on doit le convertir en ObjectId
        patient.user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        patient.update()
        
        # Envoyer les identifiants par email
        try:
            email_service = EmailService()
            email_service.send_account_credentials(
                patient.email,
                patient.nom,
                patient.prenom,
                patient.email,
                temp_password
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            # Ne pas bloquer si l'email échoue
        
        # Créer une notification
        notification = Notification(
            user_id=str(user_id),
            type_notification=Notification.TYPE_COMPTE_CREE,
            titre='Compte créé',
            message='Votre compte patient a été créé. Consultez votre email pour vos identifiants.'
        )
        notification.save()
        
        return jsonify({
            'message': 'Compte patient créé avec succès. Les identifiants ont été envoyés par email.',
            'user_id': user_id,
            'password': temp_password  # Retourner pour affichage si nécessaire
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de la création du compte patient: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/patients/<patient_id>/compte', methods=['DELETE'])
def deactivate_patient_account(patient_id):
    """
    Désactive le compte utilisateur d'un patient
    """
    try:
        patient = Patient.find_by_id(patient_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        if not patient.user_id:
            return jsonify({'error': 'Ce patient n\'a pas de compte utilisateur'}), 400
        
        user = User.find_by_id(str(patient.user_id))
        if user:
            user.is_active = False
            user.update()
        
        return jsonify({'message': 'Compte patient désactivé avec succès'}), 200
        
    except Exception as e:
        print(f"Erreur lors de la désactivation du compte: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/rendezvous', methods=['GET'])
def get_all_rendezvous():
    """
    Récupère tous les rendez-vous avec filtres
    """
    try:
        date_rdv = request.args.get('date')
        statut = request.args.get('statut')
        
        from config.database import get_db
        db = get_db()
        
        query = {}
        if date_rdv:
            try:
                date_obj = datetime.fromisoformat(date_rdv.split('T')[0])
                date_debut = datetime.combine(date_obj.date(), datetime.min.time())
                date_fin = datetime.combine(date_obj.date(), datetime.max.time())
                query['date_rdv'] = {'$gte': date_debut, '$lte': date_fin}
            except:
                pass
        
        if statut:
            query['statut'] = statut
        
        rdvs_data = db.rendezvous.find(query).sort('date_rdv', 1).limit(100)
        
        rdvs = []
        for rdv_data in rdvs_data:
            patient = Patient.find_by_id(rdv_data['patient_id'])
            medecin_user = User.find_by_id(rdv_data['medecin_id'])
            
            rdv_dict = {
                '_id': str(rdv_data['_id']),
                'date_rdv': rdv_data['date_rdv'].isoformat() if isinstance(rdv_data['date_rdv'], datetime) else str(rdv_data['date_rdv']),
                'heure_rdv': rdv_data['heure_rdv'],
                'motif': rdv_data.get('motif'),
                'statut': rdv_data.get('statut'),
                'patient': patient.to_dict() if patient else None,
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

@bp.route('/rendezvous', methods=['POST'])
def create_rendezvous():
    """
    Crée un nouveau rendez-vous
    """
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        medecin_id = data.get('medecin_id')
        date_rdv = data.get('date_rdv')
        heure_rdv = data.get('heure_rdv')
        
        if not all([patient_id, medecin_id, date_rdv, heure_rdv]):
            return jsonify({'error': 'Tous les champs sont requis'}), 400
        
        # Vérifier la disponibilité
        if not RendezVous.check_disponibilite(medecin_id, date_rdv, heure_rdv):
            return jsonify({'error': 'Ce créneau n\'est pas disponible'}), 400
        
        rdv = RendezVous(
            patient_id=patient_id,
            medecin_id=medecin_id,
            date_rdv=date_rdv,
            heure_rdv=heure_rdv,
            motif=data.get('motif'),
            statut=RendezVous.STATUT_CONFIRME,
            notes=data.get('notes')
        )
        
        rdv_id = rdv.save()
        
        # Envoyer une notification au patient si il a un compte
        patient = Patient.find_by_id(patient_id)
        if patient and patient.user_id:
            medecin_user = User.find_by_id(medecin_id)
            medecin_nom = f"{medecin_user.prenom} {medecin_user.nom}" if medecin_user else "Médecin"
            
            notification = Notification(
                user_id=str(patient.user_id),
                type_notification=Notification.TYPE_RDV_CONFIRME,
                titre='Rendez-vous confirmé',
                message=f'Votre rendez-vous avec {medecin_nom} le {date_rdv} à {heure_rdv} a été confirmé.'
            )
            notification.save()
            
            # Envoyer un email de confirmation
            if patient.email:
                try:
                    email_service = EmailService()
                    email_service.send_rdv_confirmation(
                        patient.email,
                        patient.nom,
                        patient.prenom,
                        str(date_rdv),
                        heure_rdv,
                        medecin_nom
                    )
                except Exception as e:
                    print(f"Erreur lors de l'envoi de l'email: {e}")
        
        return jsonify({
            'message': 'Rendez-vous créé avec succès',
            'rendezvous': rdv.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de la création du rendez-vous: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/rendezvous/<rdv_id>', methods=['PUT'])
def update_rendezvous(rdv_id):
    """
    Met à jour un rendez-vous
    """
    try:
        rdv = RendezVous.find_by_id(rdv_id)
        if not rdv:
            return jsonify({'error': 'Rendez-vous introuvable'}), 404
        
        data = request.get_json()
        
        if 'date_rdv' in data:
            rdv.date_rdv = data['date_rdv']
        if 'heure_rdv' in data:
            rdv.heure_rdv = data['heure_rdv']
        if 'motif' in data:
            rdv.motif = data['motif']
        if 'statut' in data:
            rdv.statut = data['statut']
        if 'notes' in data:
            rdv.notes = data['notes']
        
        rdv.update()
        
        return jsonify({
            'message': 'Rendez-vous mis à jour avec succès',
            'rendezvous': rdv.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du rendez-vous: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/rendezvous/<rdv_id>/confirmer', methods=['POST'])
def confirm_rendezvous(rdv_id):
    """
    Confirme un rendez-vous en attente
    """
    try:
        rdv = RendezVous.find_by_id(rdv_id)
        if not rdv:
            return jsonify({'error': 'Rendez-vous introuvable'}), 404
        
        rdv.statut = RendezVous.STATUT_CONFIRME
        rdv.update()
        
        # Notifier le patient
        patient = Patient.find_by_id(rdv.patient_id)
        if patient and patient.user_id:
            medecin_user = User.find_by_id(rdv.medecin_id)
            medecin_nom = f"{medecin_user.prenom} {medecin_user.nom}" if medecin_user else "Médecin"
            
            notification = Notification(
                user_id=str(patient.user_id),
                type_notification=Notification.TYPE_RDV_CONFIRME,
                titre='Rendez-vous confirmé',
                message=f'Votre rendez-vous avec {medecin_nom} le {rdv.date_rdv} à {rdv.heure_rdv} a été confirmé.'
            )
            notification.save()
            
            # Envoyer un email
            if patient.email:
                try:
                    email_service = EmailService()
                    email_service.send_rdv_confirmation(
                        patient.email,
                        patient.nom,
                        patient.prenom,
                        str(rdv.date_rdv),
                        rdv.heure_rdv,
                        medecin_nom
                    )
                except Exception as e:
                    print(f"Erreur lors de l'envoi de l'email: {e}")
        
        return jsonify({'message': 'Rendez-vous confirmé avec succès'}), 200
        
    except Exception as e:
        print(f"Erreur lors de la confirmation du rendez-vous: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/rendezvous/<rdv_id>', methods=['DELETE'])
def cancel_rendezvous(rdv_id):
    """
    Annule un rendez-vous
    """
    try:
        rdv = RendezVous.find_by_id(rdv_id)
        if not rdv:
            return jsonify({'error': 'Rendez-vous introuvable'}), 404
        
        rdv.statut = RendezVous.STATUT_ANNULE
        rdv.update()
        
        # Notifier le patient
        patient = Patient.find_by_id(rdv.patient_id)
        if patient and patient.user_id:
            notification = Notification(
                user_id=str(patient.user_id),
                type_notification=Notification.TYPE_RDV_ANNULE,
                titre='Rendez-vous annulé',
                message=f'Votre rendez-vous du {rdv.date_rdv} à {rdv.heure_rdv} a été annulé.'
            )
            notification.save()
        
        return jsonify({'message': 'Rendez-vous annulé avec succès'}), 200
        
    except Exception as e:
        print(f"Erreur lors de l'annulation du rendez-vous: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500
