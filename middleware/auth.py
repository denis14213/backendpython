"""
Middleware d'authentification et de gestion des permissions
"""

from functools import wraps
from flask import session, jsonify, request
from models.user import User

def login_required(f):
    """
    Décorateur pour vérifier que l'utilisateur est connecté
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentification requise'}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """
    Décorateur pour vérifier que l'utilisateur a un rôle autorisé
    
    Args:
        *allowed_roles: Rôles autorisés
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'Authentification requise'}), 401
            
            user = User.find_by_id(user_id)
            if not user:
                return jsonify({'error': 'Utilisateur introuvable'}), 404
            
            if not user.is_active:
                return jsonify({'error': 'Compte désactivé'}), 403
            
            if user.role not in allowed_roles:
                return jsonify({'error': 'Accès refusé. Permissions insuffisantes'}), 403
            
            # Ajouter l'utilisateur au contexte de la requête
            request.current_user = user
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """
    Récupère l'utilisateur actuellement connecté depuis la session
    
    Returns:
        Instance User ou None
    """
    user_id = session.get('user_id')
    if user_id:
        return User.find_by_id(user_id)
    return None

