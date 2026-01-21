"""
Contrôleur Patient - Espace patient
"""

from flask import Blueprint, request, jsonify, session, send_file
import os
from models.user import User
from models.patient import Patient
from models.rendezvous import RendezVous
from models.dossier_medical import DossierMedical
from models.ordonnance import Ordonnance
from models.document_medical import DocumentMedical
from models.notification import Notification
from datetime import datetime
import os

bp = Blueprint('patient', __name__)

@bp.route('/inscription', methods=['POST'])
def register():
    """
    Inscription d'un nouveau patient
    """
    try:
        data = request.get_json()
        
        if not all([data.get('email'), data.get('password'), data.get('nom'), data.get('prenom')]):
            return jsonify({'error': 'Tous les champs sont requis'}), 400
        
        # Vérifier si l'email existe déjà
        existing_user = User.find_by_email(data['email'])
        if existing_user:
            return jsonify({'error': 'Cet email est déjà utilisé'}), 400
        
        # Créer l'utilisateur
        user = User(
            email=data['email'],
            password=data['password'],
            role='patient',
            nom=data['nom'],
            prenom=data['prenom'],
            telephone=data.get('telephone'),
            is_active=True
        )
        
        user_id = user.save()
        
        # Créer le patient
        patient = Patient(
            nom=data['nom'],
            prenom=data['prenom'],
            email=data['email'],
            telephone=data.get('telephone'),
            date_naissance=data.get('date_naissance'),
            adresse=data.get('adresse'),
            ville=data.get('ville'),
            code_postal=data.get('code_postal'),
            sexe=data.get('sexe'),
            numero_securite_sociale=data.get('numero_securite_sociale'),
            user_id=user_id
        )
        
        patient.save()
        
        # Connexion automatique
        session['user_id'] = user_id
        session['user_role'] = 'patient'
        session['user_email'] = user.email
        session.permanent = True
        
        return jsonify({
            'message': 'Inscription réussie',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de l'inscription: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """
    Récupère les données du tableau de bord patient
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        patient = Patient.find_by_user_id(user_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        # Prochains rendez-vous
        rdvs = RendezVous.find_by_patient(str(patient._id), statut=RendezVous.STATUT_CONFIRME)
        prochains_rdv = [rdv.to_dict() for rdv in rdvs[:5]]  # 5 prochains
        
        # Dernières ordonnances
        ordonnances = Ordonnance.find_by_patient(str(patient._id), limit=5)
        dernieres_ordonnances = [ord.to_dict() for ord in ordonnances]
        
        # Derniers documents
        documents = DocumentMedical.find_by_patient(str(patient._id), limit=5)
        derniers_documents = [doc.to_dict() for doc in documents]
        
        # Notifications non lues
        notifications_count = Notification.count_unread(user_id)
        
        # Compter les dossiers
        dossiers = DossierMedical.find_by_patient(str(patient._id))
        
        dashboard = {
            'patient': patient.to_dict(),
            'prochains_rendezvous': prochains_rdv,
            'dernieres_ordonnances': dernieres_ordonnances,
            'derniers_documents': derniers_documents,
            'notifications_non_lues': notifications_count,
            'dossiers': {
                'total': len(dossiers)
            },
            'ordonnances': {
                'total': len(ordonnances)
            }
        }
        
        return jsonify(dashboard), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération du dashboard: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/rendezvous', methods=['GET'])
def get_my_rendezvous():
    """
    Récupère les rendez-vous du patient
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        patient = Patient.find_by_user_id(user_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        statut = request.args.get('statut')
        rdvs = RendezVous.find_by_patient(str(patient._id), statut=statut)
        
        rdvs_list = []
        for rdv in rdvs:
            from models.user import User
            medecin_user = User.find_by_id(rdv.medecin_id)
            medecin = None
            if medecin_user:
                from models.medecin import Medecin
                medecin_info = Medecin.find_by_user_id(rdv.medecin_id)
                medecin = {
                    'nom': medecin_user.nom,
                    'prenom': medecin_user.prenom,
                    'specialite': medecin_info.specialite if medecin_info else None
                }
            rdv_dict = rdv.to_dict()
            rdv_dict['medecin'] = medecin
            rdvs_list.append(rdv_dict)
        
        return jsonify({'rendezvous': rdvs_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des rendez-vous: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/rendezvous', methods=['POST'])
def create_rendezvous():
    """
    Crée une demande de rendez-vous
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        patient = Patient.find_by_user_id(user_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        data = request.get_json()
        medecin_id = data.get('medecin_id')
        date_rdv = data.get('date_rdv')
        heure_rdv = data.get('heure_rdv')
        
        if not all([medecin_id, date_rdv, heure_rdv]):
            return jsonify({'error': 'Tous les champs sont requis'}), 400
        
        # Vérifier la disponibilité
        if not RendezVous.check_disponibilite(medecin_id, date_rdv, heure_rdv):
            return jsonify({'error': 'Ce créneau n\'est pas disponible'}), 400
        
        rdv = RendezVous(
            patient_id=str(patient._id),
            medecin_id=medecin_id,
            date_rdv=date_rdv,
            heure_rdv=heure_rdv,
            motif=data.get('motif'),
            statut=RendezVous.STATUT_DEMANDE,
            notes=data.get('notes')
        )
        
        rdv_id = rdv.save()
        
        return jsonify({
            'message': 'Demande de rendez-vous créée avec succès',
            'rendezvous': rdv.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de la création du rendez-vous: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/rendezvous/<rdv_id>', methods=['DELETE'])
def cancel_rendezvous(rdv_id):
    """
    Annule un rendez-vous
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        patient = Patient.find_by_user_id(user_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        rdv = RendezVous.find_by_id(rdv_id)
        if not rdv:
            return jsonify({'error': 'Rendez-vous introuvable'}), 404
        
        if str(rdv.patient_id) != str(patient._id):
            return jsonify({'error': 'Accès refusé'}), 403
        
        rdv.statut = RendezVous.STATUT_ANNULE
        rdv.update()
        
        return jsonify({'message': 'Rendez-vous annulé avec succès'}), 200
        
    except Exception as e:
        print(f"Erreur lors de l'annulation du rendez-vous: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/dossiers', methods=['GET'])
def get_my_dossiers():
    """
    Récupère les dossiers médicaux du patient (résumé)
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        patient = Patient.find_by_user_id(user_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        dossiers = DossierMedical.find_by_patient(str(patient._id))
        
        dossiers_list = []
        for dossier in dossiers:
            from models.user import User
            medecin_user = User.find_by_id(dossier.medecin_id)
            dossier_dict = {
                '_id': str(dossier._id),
                'date_consultation': dossier.date_consultation.isoformat() if isinstance(dossier.date_consultation, datetime) else dossier.date_consultation,
                'medecin': {
                    'nom': medecin_user.nom if medecin_user else 'N/A',
                    'prenom': medecin_user.prenom if medecin_user else 'N/A'
                } if medecin_user else None,
                'diagnostic': dossier.diagnostic,
                'observations': dossier.observations,
                'examen_clinique': dossier.examen_clinique,
                'poids': dossier.poids,
                'taille': dossier.taille,
                'tension_arterielle': dossier.tension_arterielle,
                'temperature': dossier.temperature
            }
            dossiers_list.append(dossier_dict)
        
        return jsonify({'dossiers': dossiers_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des dossiers: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/ordonnances', methods=['GET'])
def get_my_ordonnances():
    """
    Récupère les ordonnances du patient
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        patient = Patient.find_by_user_id(user_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        ordonnances = Ordonnance.find_by_patient(str(patient._id))
        
        ordonnances_list = []
        for ord in ordonnances:
            from models.user import User
            medecin_user = User.find_by_id(ord.medecin_id)
            ord_dict = ord.to_dict()
            ord_dict['medecin'] = {
                'nom': medecin_user.nom if medecin_user else 'N/A',
                'prenom': medecin_user.prenom if medecin_user else 'N/A'
            } if medecin_user else None
            ordonnances_list.append(ord_dict)
        
        return jsonify({'ordonnances': ordonnances_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des ordonnances: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/documents', methods=['GET'])
def get_my_documents():
    """
    Récupère les documents médicaux du patient
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        patient = Patient.find_by_user_id(user_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        documents = DocumentMedical.find_by_patient(str(patient._id))
        
        documents_list = [doc.to_dict() for doc in documents]
        
        return jsonify({'documents': documents_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des documents: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/ordonnances/<ordonnance_id>/pdf', methods=['GET'])
def download_ordonnance_pdf(ordonnance_id):
    """
    Télécharge le PDF d'une ordonnance (depuis MongoDB)
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        patient = Patient.find_by_user_id(user_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        ordonnance = Ordonnance.find_by_id(ordonnance_id)
        if not ordonnance:
            return jsonify({'error': 'Ordonnance introuvable'}), 404
        
        # Vérifier que l'ordonnance appartient au patient
        if str(ordonnance.patient_id) != str(patient._id):
            return jsonify({'error': 'Accès refusé'}), 403
        
        # Vérifier si le PDF existe déjà
        if ordonnance.pdf_data:
            pdf_base64 = ordonnance.pdf_data
        else:
            # Générer le PDF
            from models.user import User
            from models.medecin import Medecin
            from services.pdf_service import PDFService
            
            medecin_user = User.find_by_id(ordonnance.medecin_id)
            medecin_info = Medecin.find_by_user_id(ordonnance.medecin_id)
            
            # Générer le PDF (retourne base64)
            pdf_base64 = PDFService.generate_ordonnance(
                ordonnance=ordonnance,
                patient=patient,
                medecin_user=medecin_user,
                medecin_info=medecin_info
            )
            
            # Sauvegarder le PDF dans l'ordonnance
            ordonnance.pdf_data = pdf_base64
            ordonnance.update()
        
        # Décoder et envoyer le PDF
        import base64
        from flask import Response
        pdf_content = base64.b64decode(pdf_base64)
        
        response = Response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="ordonnance_{ordonnance_id}.pdf"'
        response.headers['Content-Length'] = str(len(pdf_content))
        
        return response
        
    except Exception as e:
        print(f"Erreur lors de la génération du PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/documents/<document_id>/download', methods=['GET'])
def download_document(document_id):
    """
    Télécharge un document médical (depuis MongoDB)
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        patient = Patient.find_by_user_id(user_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        document = DocumentMedical.find_by_id(document_id)
        if not document:
            return jsonify({'error': 'Document introuvable'}), 404
        
        # Vérifier que le document appartient au patient
        if str(document.patient_id) != str(patient._id):
            return jsonify({'error': 'Accès refusé'}), 403
        
        if not document.file_data:
            return jsonify({'error': 'Fichier introuvable'}), 404
        
        # Décoder le base64
        import base64
        from flask import Response
        file_content = base64.b64decode(document.file_data)
        
        # Créer la réponse avec le fichier
        response = Response(file_content)
        response.headers['Content-Type'] = document.file_type or 'application/octet-stream'
        response.headers['Content-Disposition'] = f'attachment; filename="{document.nom_fichier}"'
        response.headers['Content-Length'] = str(document.file_size)
        
        return response
        
    except Exception as e:
        print(f"Erreur lors du téléchargement du document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/notifications', methods=['GET'])
def get_notifications():
    """
    Récupère les notifications du patient
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        is_read = request.args.get('is_read')
        is_read_bool = None
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
        
        notifications = Notification.find_by_user(user_id, is_read=is_read_bool)
        
        notifications_list = [notif.to_dict() for notif in notifications]
        
        return jsonify({'notifications': notifications_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des notifications: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/notifications/<notif_id>/read', methods=['POST'])
def mark_notification_read(notif_id):
    """
    Marque une notification comme lue
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        from models.notification import Notification
        from bson import ObjectId
        
        notif = Notification.find_by_id(notif_id)
        if not notif:
            return jsonify({'error': 'Notification introuvable'}), 404
        
        if str(notif.user_id) != user_id:
            return jsonify({'error': 'Accès refusé'}), 403
        
        notif.mark_as_read()
        
        return jsonify({'message': 'Notification marquée comme lue'}), 200
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la notification: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/profil', methods=['GET'])
def get_profil():
    """
    Récupère le profil du patient
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        patient = Patient.find_by_user_id(user_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        return jsonify({'patient': patient.to_dict()}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération du profil: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/profil', methods=['PUT'])
def update_profil():
    """
    Met à jour le profil du patient
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        patient = Patient.find_by_user_id(user_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        data = request.get_json()
        
        if 'telephone' in data:
            patient.telephone = data['telephone']
        if 'adresse' in data:
            patient.adresse = data['adresse']
        if 'ville' in data:
            patient.ville = data['ville']
        if 'code_postal' in data:
            patient.code_postal = data['code_postal']
        
        patient.update()
        
        return jsonify({
            'message': 'Profil mis à jour avec succès',
            'patient': patient.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du profil: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500
