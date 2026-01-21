"""
Contrôleur d'authentification
Gère la connexion, déconnexion, réinitialisation de mot de passe
"""

from flask import Blueprint, request, jsonify, session
from models.user import User
from services.email_service import EmailService
import secrets
import string

bp = Blueprint('auth', __name__)

def generate_temp_password(length=12):
    """
    Génère un mot de passe temporaire aléatoire
    
    Args:
        length: Longueur du mot de passe
        
    Returns:
        Mot de passe généré
    """
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

@bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint de connexion
    
    Body JSON:
        email: Email de l'utilisateur
        password: Mot de passe
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        # Recherche de l'utilisateur
        user = User.find_by_email(email)
        
        if not user:
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Compte désactivé. Contactez l\'administrateur'}), 403
        
        # Vérification du mot de passe
        if not user.verify_password(password):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        # Création de la session
        session['user_id'] = str(user._id)
        session['user_role'] = user.role
        session['user_email'] = user.email
        session.permanent = True
        
        return jsonify({
            'message': 'Connexion réussie',
            'user': {
                '_id': str(user._id),
                'email': user.email,
                'role': user.role,
                'nom': user.nom,
                'prenom': user.prenom
            }
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la connexion: {e}")
        return jsonify({'error': 'Erreur serveur lors de la connexion'}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    """
    Endpoint de déconnexion
    """
    try:
        session.clear()
        return jsonify({'message': 'Déconnexion réussie'}), 200
    except Exception as e:
        print(f"Erreur lors de la déconnexion: {e}")
        return jsonify({'error': 'Erreur serveur lors de la déconnexion'}), 500

@bp.route('/me', methods=['GET'])
def get_current_user_info():
    """
    Endpoint pour récupérer les informations de l'utilisateur connecté
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Non authentifié'}), 401
        
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Endpoint pour demander la réinitialisation du mot de passe
    
    Body JSON:
        email: Email de l'utilisateur
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email requis'}), 400
        
        user = User.find_by_email(email)
        if not user:
            # Pour des raisons de sécurité, on ne révèle pas si l'email existe
            return jsonify({'message': 'Si cet email existe, un lien de réinitialisation a été envoyé'}), 200
        
        # Génération d'un token de réinitialisation (simplifié)
        reset_token = secrets.token_urlsafe(32)
        
        # En production, stocker le token dans la base de données avec une expiration
        # Pour l'instant, on génère simplement un nouveau mot de passe temporaire
        temp_password = generate_temp_password()
        user.reset_password(temp_password)
        
        # Envoi de l'email avec le nouveau mot de passe
        email_service = EmailService()
        email_service.send_password_reset(email, user.nom or '', user.prenom or '', reset_token)
        
        return jsonify({'message': 'Si cet email existe, un lien de réinitialisation a été envoyé'}), 200
        
    except Exception as e:
        print(f"Erreur lors de la demande de réinitialisation: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@bp.route('/change-password', methods=['POST'])
def change_password():
    """
    Endpoint pour changer le mot de passe (utilisateur connecté)
    
    Body JSON:
        current_password: Mot de passe actuel
        new_password: Nouveau mot de passe
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentification requise'}), 401
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Mot de passe actuel et nouveau mot de passe requis'}), 400
        
        if len(new_password) < 8:
            return jsonify({'error': 'Le nouveau mot de passe doit contenir au moins 8 caractères'}), 400
        
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404
        
        # Vérification du mot de passe actuel
        if not user.verify_password(current_password):
            return jsonify({'error': 'Mot de passe actuel incorrect'}), 401
        
        # Mise à jour du mot de passe
        user.reset_password(new_password)
        
        return jsonify({'message': 'Mot de passe modifié avec succès'}), 200
        
    except Exception as e:
        print(f"Erreur lors du changement de mot de passe: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

