"""
Modèle User - Gestion des utilisateurs du système
"""

from datetime import datetime
from bson import ObjectId
from config.database import get_db
import bcrypt

class User:
    """
    Classe représentant un utilisateur du système
    """
    
    def __init__(self, email, password, role, nom=None, prenom=None, telephone=None, is_active=True, _id=None):
        """
        Initialise un utilisateur
        
        Args:
            email: Email de l'utilisateur (unique)
            password: Mot de passe en clair (sera hashé)
            role: Rôle de l'utilisateur (admin, medecin, secretaire)
            nom: Nom de famille
            prenom: Prénom
            telephone: Numéro de téléphone
            is_active: Statut actif/inactif
            _id: ID MongoDB (si existant)
        """
        self._id = _id if _id else ObjectId()
        self.email = email
        self.password_hash = self._hash_password(password) if password else None
        self.role = role
        self.nom = nom
        self.prenom = prenom
        self.telephone = telephone
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def _hash_password(self, password):
        """
        Hash le mot de passe avec bcrypt
        
        Args:
            password: Mot de passe en clair
            
        Returns:
            Mot de passe hashé
        """
        import os
        rounds = int(os.getenv('BCRYPT_ROUNDS', 12))
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=rounds))
    
    def verify_password(self, password):
        """
        Vérifie si le mot de passe correspond
        
        Args:
            password: Mot de passe à vérifier
            
        Returns:
            True si le mot de passe est correct, False sinon
        """
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)
    
    def to_dict(self, include_password=False):
        """
        Convertit l'utilisateur en dictionnaire
        
        Args:
            include_password: Si True, inclut le hash du mot de passe
            
        Returns:
            Dictionnaire représentant l'utilisateur
        """
        data = {
            '_id': str(self._id),
            'email': self.email,
            'role': self.role,
            'nom': self.nom,
            'prenom': self.prenom,
            'telephone': self.telephone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
        
        if include_password:
            data['password_hash'] = self.password_hash
        
        return data
    
    def save(self):
        """
        Sauvegarde l'utilisateur dans la base de données
        
        Returns:
            ID de l'utilisateur créé
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        user_dict = self.to_dict(include_password=True)
        user_dict['_id'] = self._id
        
        result = db.users.insert_one(user_dict)
        return str(result.inserted_id)
    
    def update(self):
        """
        Met à jour l'utilisateur dans la base de données
        
        Returns:
            True si la mise à jour a réussi
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        user_dict = self.to_dict(include_password=True)
        # Ne pas inclure _id dans la mise à jour
        user_dict.pop('_id', None)
        
        result = db.users.update_one(
            {'_id': self._id},
            {'$set': user_dict}
        )
        return result.modified_count > 0
    
    @staticmethod
    def find_by_email(email):
        """
        Trouve un utilisateur par son email
        
        Args:
            email: Email de l'utilisateur
            
        Returns:
            Instance User ou None
        """
        db = get_db()
        user_data = db.users.find_one({'email': email})
        
        if user_data:
            user = User(
                email=user_data['email'],
                password=None,  # Ne pas charger le mot de passe
                role=user_data['role'],
                nom=user_data.get('nom'),
                prenom=user_data.get('prenom'),
                telephone=user_data.get('telephone'),
                is_active=user_data.get('is_active', True),
                _id=user_data['_id']
            )
            user.password_hash = user_data.get('password_hash')
            user.created_at = user_data.get('created_at')
            user.updated_at = user_data.get('updated_at')
            return user
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """
        Trouve un utilisateur par son ID
        
        Args:
            user_id: ID de l'utilisateur (string ou ObjectId)
            
        Returns:
            Instance User ou None
        """
        db = get_db()
        try:
            _id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            user_data = db.users.find_one({'_id': _id})
            
            if user_data:
                user = User(
                    email=user_data['email'],
                    password=None,
                    role=user_data['role'],
                    nom=user_data.get('nom'),
                    prenom=user_data.get('prenom'),
                    telephone=user_data.get('telephone'),
                    is_active=user_data.get('is_active', True),
                    _id=user_data['_id']
                )
                user.password_hash = user_data.get('password_hash')
                user.created_at = user_data.get('created_at')
                user.updated_at = user_data.get('updated_at')
                return user
        except Exception as e:
            print(f"Erreur lors de la recherche de l'utilisateur: {e}")
        return None
    
    @staticmethod
    def find_all(role=None, is_active=None):
        """
        Trouve tous les utilisateurs avec filtres optionnels
        
        Args:
            role: Filtrer par rôle
            is_active: Filtrer par statut actif
            
        Returns:
            Liste d'instances User
        """
        db = get_db()
        query = {}
        
        if role:
            query['role'] = role
        if is_active is not None:
            query['is_active'] = is_active
        
        users_data = db.users.find(query)
        users = []
        
        for user_data in users_data:
            user = User(
                email=user_data['email'],
                password=None,
                role=user_data['role'],
                nom=user_data.get('nom'),
                prenom=user_data.get('prenom'),
                telephone=user_data.get('telephone'),
                is_active=user_data.get('is_active', True),
                _id=user_data['_id']
            )
            user.created_at = user_data.get('created_at')
            user.updated_at = user_data.get('updated_at')
            users.append(user)
        
        return users
    
    def reset_password(self, new_password):
        """
        Réinitialise le mot de passe de l'utilisateur
        
        Args:
            new_password: Nouveau mot de passe en clair
        """
        self.password_hash = self._hash_password(new_password)
        self.update()

