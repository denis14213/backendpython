"""
Contrôleur Médecin - Gestion des dossiers médicaux, ordonnances, rendez-vous
"""

from flask import Blueprint, request, jsonify, session, send_file
from models.user import User
from models.patient import Patient
from models.rendezvous import RendezVous
from models.dossier_medical import DossierMedical
from models.ordonnance import Ordonnance
from models.document_medical import DocumentMedical
from models.medecin import Medecin
from models.notification import Notification
from services.pdf_service import PDFService
from datetime import datetime
from bson import ObjectId
import os
import uuid
from werkzeug.utils import secure_filename

bp = Blueprint('medecin', __name__)

# Configuration pour l'upload de fichiers (stockage MongoDB)
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename):
    """Vérifie si le fichier a une extension autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """
    Récupère les statistiques du dashboard médecin
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        # Récupérer les rendez-vous du jour
        today = datetime.utcnow().date()
        rdvs_today = RendezVous.find_by_date(today, medecin_id=user_id)
        
        # Récupérer les rendez-vous à venir
        from datetime import timedelta
        next_week = today + timedelta(days=7)
        rdvs_upcoming = []
        for i in range(7):
            date = today + timedelta(days=i)
            rdvs = RendezVous.find_by_date(date, medecin_id=user_id)
            rdvs_upcoming.extend([rdv for rdv in rdvs if rdv.statut in ['confirme', 'demande']])
        
        # Récupérer le nombre de patients
        dossiers = DossierMedical.find_by_medecin(user_id, limit=1000)
        patient_ids = list(set([str(dossier.patient_id) for dossier in dossiers]))
        
        return jsonify({
            'rdvs_aujourdhui': len([rdv for rdv in rdvs_today if rdv.statut in ['confirme', 'demande']]),
            'rdvs_prochains': len(rdvs_upcoming),
            'nb_patients': len(patient_ids),
            'rdvs_today': [rdv.to_dict() for rdv in rdvs_today[:5]]
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération du dashboard: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/rendezvous', methods=['GET'])
def get_my_rendezvous():
    """
    Récupère les rendez-vous du médecin
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        # Récupérer les rendez-vous du médecin
        rdvs = RendezVous.find_by_medecin(user_id)
        
        rdvs_list = []
        for rdv in rdvs:
            rdv_dict = rdv.to_dict()
            # Ajouter les informations du patient
            if rdv.patient_id:
                patient = Patient.find_by_id(rdv.patient_id)
                if patient:
                    rdv_dict['patient'] = patient.to_dict()
            rdvs_list.append(rdv_dict)
        
        return jsonify({'rendezvous': rdvs_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des rendez-vous: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/patients', methods=['GET'])
def get_my_patients():
    """
    Récupère les patients du médecin (ceux avec qui il a eu des consultations)
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        # Récupérer les dossiers médicaux du médecin pour obtenir les patients
        dossiers = DossierMedical.find_by_medecin(user_id, limit=1000)
        
        # Extraire les IDs de patients uniques
        patient_ids = list(set([str(dossier.patient_id) for dossier in dossiers]))
        
        patients_list = []
        for patient_id in patient_ids:
            patient = Patient.find_by_id(patient_id)
            if patient:
                patients_list.append(patient.to_dict())
        
        return jsonify({'patients': patients_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des patients: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/patients/<patient_id>', methods=['GET'])
def get_patient_details(patient_id):
    """
    Récupère les détails d'un patient
    """
    try:
        patient = Patient.find_by_id(patient_id)
        if not patient:
            return jsonify({'error': 'Patient introuvable'}), 404
        
        return jsonify({'patient': patient.to_dict()}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération du patient: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/patients/<patient_id>/dossiers', methods=['GET'])
def get_patient_dossiers(patient_id):
    """
    Récupère les dossiers médicaux d'un patient
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        dossiers = DossierMedical.find_by_patient(patient_id)
        
        # Filtrer pour ne garder que ceux du médecin
        dossiers_medecin = [d for d in dossiers if str(d.medecin_id) == user_id]
        
        dossiers_list = []
        for dossier in dossiers_medecin:
            dossier_dict = dossier.to_dict()
            # Ajouter les informations du médecin
            if dossier.medecin_id:
                user = User.find_by_id(dossier.medecin_id)
                if user:
                    dossier_dict['medecin'] = {
                        'nom': user.nom,
                        'prenom': user.prenom
                    }
            dossiers_list.append(dossier_dict)
        
        return jsonify({'dossiers': dossiers_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des dossiers: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/dossiers', methods=['POST'])
def create_dossier():
    """
    Crée un nouveau dossier médical
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        data = request.get_json()
        patient_id = data.get('patient_id')
        date_consultation_str = data.get('date_consultation')
        
        if not patient_id:
            return jsonify({'error': 'ID patient requis'}), 400
        
        # Parser la date
        try:
            date_consultation = datetime.fromisoformat(date_consultation_str.split('T')[0])
        except:
            date_consultation = datetime.utcnow()
        
        # Convertir les valeurs vides en None pour les champs numériques
        poids = data.get('poids')
        if poids == '' or poids is None:
            poids = None
        else:
            try:
                poids = float(poids)
            except (ValueError, TypeError):
                poids = None
        
        taille = data.get('taille')
        if taille == '' or taille is None:
            taille = None
        else:
            try:
                taille = float(taille)
            except (ValueError, TypeError):
                taille = None
        
        temperature = data.get('temperature')
        if temperature == '' or temperature is None:
            temperature = None
        else:
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = None
        
        tension_arterielle = data.get('tension_arterielle')
        if tension_arterielle == '':
            tension_arterielle = None
        
        dossier = DossierMedical(
            patient_id=patient_id,
            medecin_id=user_id,
            date_consultation=date_consultation,
            observations=data.get('observations') or None,
            diagnostic=data.get('diagnostic') or None,
            examen_clinique=data.get('examen_clinique') or None,
            poids=poids,
            taille=taille,
            tension_arterielle=tension_arterielle,
            temperature=temperature
        )
        
        dossier_id = dossier.save()
        
        # Créer une notification pour le patient
        patient = Patient.find_by_id(patient_id)
        if patient and patient.user_id:
            notification = Notification(
                user_id=str(patient.user_id),
                type_notification=Notification.TYPE_DOSSIER_CREE,
                titre='Nouveau dossier médical créé',
                message=f'Un nouveau dossier médical a été créé suite à votre consultation du {date_consultation.strftime("%d/%m/%Y")}.'
            )
            notification.save()
        
        return jsonify({
            'message': 'Dossier médical créé avec succès',
            'dossier': dossier.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de la création du dossier: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/dossiers/<dossier_id>', methods=['PUT'])
def update_dossier(dossier_id):
    """
    Met à jour un dossier médical
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        dossier = DossierMedical.find_by_id(dossier_id)
        if not dossier:
            return jsonify({'error': 'Dossier introuvable'}), 404
        
        # Vérifier que le médecin est le propriétaire
        if str(dossier.medecin_id) != user_id:
            return jsonify({'error': 'Accès refusé'}), 403
        
        data = request.get_json()
        
        if 'observations' in data:
            dossier.observations = data['observations']
        if 'diagnostic' in data:
            dossier.diagnostic = data['diagnostic']
        if 'examen_clinique' in data:
            dossier.examen_clinique = data['examen_clinique']
        if 'poids' in data:
            dossier.poids = data['poids']
        if 'taille' in data:
            dossier.taille = data['taille']
        if 'tension_arterielle' in data:
            dossier.tension_arterielle = data['tension_arterielle']
        if 'temperature' in data:
            dossier.temperature = data['temperature']
        
        dossier.update()
        
        return jsonify({
            'message': 'Dossier médical mis à jour avec succès',
            'dossier': dossier.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du dossier: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/ordonnances', methods=['POST'])
def create_ordonnance():
    """
    Crée une nouvelle ordonnance
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        data = request.get_json()
        patient_id = data.get('patient_id')
        date_ordonnance_str = data.get('date_ordonnance')
        traitements = data.get('traitements', [])
        instructions = data.get('instructions')
        
        if not patient_id:
            return jsonify({'error': 'ID patient requis'}), 400
        
        # Parser la date
        try:
            date_ordonnance = datetime.fromisoformat(date_ordonnance_str.split('T')[0])
        except:
            date_ordonnance = datetime.utcnow()
        
        ordonnance = Ordonnance(
            patient_id=patient_id,
            medecin_id=user_id,
            date_ordonnance=date_ordonnance,
            traitements=traitements,
            instructions=instructions
        )
        
        ordonnance_id = ordonnance.save()
        
        # Créer une notification pour le patient
        patient = Patient.find_by_id(patient_id)
        if patient and patient.user_id:
            notification = Notification(
                user_id=str(patient.user_id),
                type_notification=Notification.TYPE_ORDONNANCE_DISPONIBLE,
                titre='Nouvelle ordonnance disponible',
                message=f'Une nouvelle ordonnance vous a été prescrite le {date_ordonnance.strftime("%d/%m/%Y")}.'
            )
            notification.save()
        
        return jsonify({
            'message': 'Ordonnance créée avec succès',
            'ordonnance': ordonnance.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de la création de l'ordonnance: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/ordonnances', methods=['GET'])
def get_all_ordonnances():
    """
    Récupère toutes les ordonnances du médecin
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        ordonnances = Ordonnance.find_by_medecin(user_id)
        
        ordonnances_list = []
        for ord in ordonnances:
            ord_dict = ord.to_dict()
            # Ajouter les informations du patient
            if ord.patient_id:
                patient = Patient.find_by_id(ord.patient_id)
                if patient:
                    ord_dict['patient'] = patient.to_dict()
            ordonnances_list.append(ord_dict)
        
        return jsonify({'ordonnances': ordonnances_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération des ordonnances: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/ordonnances/<ordonnance_id>/pdf', methods=['GET'])
def generate_ordonnance_pdf(ordonnance_id):
    """
    Génère et télécharge le PDF d'une ordonnance (depuis MongoDB)
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        ordonnance = Ordonnance.find_by_id(ordonnance_id)
        if not ordonnance:
            return jsonify({'error': 'Ordonnance introuvable'}), 404
        
        # Vérifier que le médecin est le propriétaire
        if str(ordonnance.medecin_id) != user_id:
            return jsonify({'error': 'Accès refusé'}), 403
        
        # Vérifier si le PDF existe déjà dans la base
        if ordonnance.pdf_data:
            # Utiliser le PDF existant
            pdf_base64 = ordonnance.pdf_data
        else:
            # Générer le PDF
            from models.user import User
            from models.medecin import Medecin
            from services.pdf_service import PDFService
            
            patient = Patient.find_by_id(ordonnance.patient_id)
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

@bp.route('/documents', methods=['POST'])
def upload_document():
    """
    Upload un document médical pour un patient (stocké en base64 dans MongoDB)
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        # Vérifier qu'un fichier a été envoyé
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Type de fichier non autorisé'}), 400
        
        # Récupérer les données du formulaire
        patient_id = request.form.get('patient_id')
        dossier_id = request.form.get('dossier_id')
        type_document = request.form.get('type_document', DocumentMedical.TYPE_AUTRE)
        description = request.form.get('description')
        date_examen_str = request.form.get('date_examen')
        
        if not patient_id:
            return jsonify({'error': 'ID patient requis'}), 400
        
        # Lire le fichier et le convertir en base64
        import base64
        file_content = file.read()
        file_size = len(file_content)
        
        # Vérifier la taille du fichier (max 10 MB)
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'Fichier trop volumineux (max 10 MB)'}), 400
        
        # Convertir en base64
        file_data_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Obtenir le type MIME
        file_type = file.content_type or 'application/octet-stream'
        
        # Parser la date d'examen
        date_examen = None
        if date_examen_str:
            try:
                date_examen = datetime.fromisoformat(date_examen_str.split('T')[0])
            except:
                date_examen = datetime.utcnow()
        else:
            date_examen = datetime.utcnow()
        
        # Créer le document médical
        document = DocumentMedical(
            patient_id=patient_id,
            dossier_id=dossier_id if dossier_id else None,
            type_document=type_document,
            nom_fichier=file.filename,
            file_data=file_data_base64,
            file_type=file_type,
            file_size=file_size,
            description=description,
            date_examen=date_examen,
            medecin_id=user_id
        )
        
        document_id = document.save()
        
        # Créer une notification pour le patient
        patient = Patient.find_by_id(patient_id)
        if patient and patient.user_id:
            notification = Notification(
                user_id=str(patient.user_id),
                type_notification=Notification.TYPE_DOCUMENT_DISPONIBLE,
                titre='Nouveau document médical disponible',
                message=f'Un nouveau document médical ({type_document}) a été ajouté à votre dossier.'
            )
            notification.save()
        
        return jsonify({
            'message': 'Document uploadé avec succès',
            'document': document.to_dict()  # Sans les données du fichier
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de l'upload du document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/documents/<document_id>', methods=['GET'])
def download_document(document_id):
    """
    Télécharge un document médical (depuis MongoDB)
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        document = DocumentMedical.find_by_id(document_id)
        if not document:
            return jsonify({'error': 'Document introuvable'}), 404
        
        # Vérifier que le médecin a accès (soit le créateur, soit via un dossier)
        if str(document.medecin_id) != user_id:
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

@bp.route('/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """
    Supprime un document médical
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        document = DocumentMedical.find_by_id(document_id)
        if not document:
            return jsonify({'error': 'Document introuvable'}), 404
        
        # Vérifier que le médecin est le créateur
        if str(document.medecin_id) != user_id:
            return jsonify({'error': 'Accès refusé'}), 403
        
        # Supprimer le document de la base de données
        document.delete()
        
        return jsonify({'message': 'Document supprimé avec succès'}), 200
        
    except Exception as e:
        print(f"Erreur lors de la suppression du document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/rendezvous/<rdv_id>/accepter', methods=['POST'])
def accepter_rendezvous(rdv_id):
    """
    Accepte un rendez-vous
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        rdv = RendezVous.find_by_id(rdv_id)
        if not rdv:
            return jsonify({'error': 'Rendez-vous introuvable'}), 404
        
        # Vérifier que le médecin est le propriétaire
        if str(rdv.medecin_id) != user_id:
            return jsonify({'error': 'Accès refusé'}), 403
        
        rdv.statut = RendezVous.STATUT_CONFIRME
        rdv.update()
        
        # Créer une notification pour le patient
        if rdv.patient_id:
            patient = Patient.find_by_id(rdv.patient_id)
            if patient and patient.user_id:
                notification = Notification(
                    user_id=str(patient.user_id),
                    type_notification=Notification.TYPE_RDV_CONFIRME,
                    titre='Rendez-vous confirmé',
                    message=f'Votre rendez-vous du {rdv.date_rdv} à {rdv.heure_rdv} a été confirmé.'
                )
                notification.save()
        
        return jsonify({
            'message': 'Rendez-vous accepté avec succès',
            'rendezvous': rdv.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de l'acceptation du rendez-vous: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/rendezvous/<rdv_id>/refuser', methods=['POST'])
def refuser_rendezvous(rdv_id):
    """
    Refuse un rendez-vous
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        rdv = RendezVous.find_by_id(rdv_id)
        if not rdv:
            return jsonify({'error': 'Rendez-vous introuvable'}), 404
        
        # Vérifier que le médecin est le propriétaire
        if str(rdv.medecin_id) != user_id:
            return jsonify({'error': 'Accès refusé'}), 403
        
        data = request.get_json() or {}
        motif_refus = data.get('motif_refus', 'Indisponibilité du médecin')
        
        rdv.statut = RendezVous.STATUT_ANNULE
        rdv.update()
        
        # Créer une notification pour le patient
        if rdv.patient_id:
            patient = Patient.find_by_id(rdv.patient_id)
            if patient and patient.user_id:
                notification = Notification(
                    user_id=str(patient.user_id),
                    type_notification=Notification.TYPE_RDV_ANNULE,
                    titre='Rendez-vous refusé',
                    message=f'Votre rendez-vous du {rdv.date_rdv} à {rdv.heure_rdv} a été refusé. Motif: {motif_refus}'
                )
                notification.save()
        
        return jsonify({
            'message': 'Rendez-vous refusé avec succès',
            'rendezvous': rdv.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Erreur lors du refus du rendez-vous: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/signature', methods=['POST'])
def upload_signature():
    """
    Upload la signature numérique du médecin (stockée en base64 dans MongoDB)
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        # Vérifier qu'un fichier a été envoyé
        if 'signature' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['signature']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        # Vérifier le type de fichier
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Type de fichier non autorisé (PNG, JPG uniquement)'}), 400
        
        # Lire le fichier et convertir en base64
        import base64
        file_content = file.read()
        file_size = len(file_content)
        
        # Vérifier la taille (max 2MB)
        if file_size > 2 * 1024 * 1024:
            return jsonify({'error': 'Fichier trop volumineux (max 2MB)'}), 400
        
        # Convertir en base64
        signature_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Mettre à jour le médecin
        medecin = Medecin.find_by_user_id(user_id)
        if not medecin:
            return jsonify({'error': 'Médecin introuvable'}), 404
        
        # Stocker la signature en base64 au lieu du chemin
        medecin.signature_data = signature_base64
        medecin.signature_type = file.content_type
        medecin.update()
        
        return jsonify({
            'message': 'Signature uploadée avec succès',
            'has_signature': True
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de l'upload de la signature: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/signature', methods=['GET'])
def get_signature():
    """
    Récupère la signature du médecin
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        medecin = Medecin.find_by_user_id(user_id)
        if not medecin:
            return jsonify({'error': 'Médecin introuvable'}), 404
        
        has_signature = hasattr(medecin, 'signature_data') and medecin.signature_data is not None
        
        return jsonify({
            'has_signature': has_signature
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération de la signature: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/patients/search', methods=['GET'])
def search_patients():
    """
    Recherche des patients
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        query = request.args.get('q', '')
        if not query:
            return jsonify({'patients': []}), 200
        
        patients = Patient.search(query)
        
        # Filtrer pour ne garder que les patients du médecin
        dossiers = DossierMedical.find_by_medecin(user_id, limit=1000)
        patient_ids_medecin = set([str(dossier.patient_id) for dossier in dossiers])
        
        patients_filtered = [p for p in patients if str(p._id) in patient_ids_medecin]
        
        patients_list = [patient.to_dict() for patient in patients_filtered]
        
        return jsonify({'patients': patients_list}), 200
        
    except Exception as e:
        print(f"Erreur lors de la recherche de patients: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500
