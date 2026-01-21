"""
Modèle Notification - Gestion des notifications utilisateurs
"""

from datetime import datetime
from bson import ObjectId
from config.database import get_db

class Notification:
    """
    Classe représentant une notification
    """
    
    TYPE_RDV_CONFIRME = 'rdv_confirme'
    TYPE_RDV_ANNULE = 'rdv_annule'
    TYPE_RDV_RAPPEL = 'rdv_rappel'
    TYPE_COMPTE_CREE = 'compte_cree'
    TYPE_DOCUMENT_DISPONIBLE = 'document_disponible'
    TYPE_ORDONNANCE_DISPONIBLE = 'ordonnance_disponible'
    TYPE_ORDONNANCE_CREE = 'ordonnance_cree'
    TYPE_DOSSIER_CREE = 'dossier_cree'
    TYPE_AUTRE = 'autre'
    
    def __init__(self, user_id, type_notification, titre, message,
                 is_read=False, lien=None, _id=None):
        """
        Initialise une notification
        
        Args:
            user_id: ID de l'utilisateur destinataire
            type_notification: Type de notification
            titre: Titre de la notification
            message: Message de la notification
            is_read: Statut de lecture
            lien: Lien associé (optionnel)
            _id: ID MongoDB (si existant)
        """
        self._id = _id if _id else ObjectId()
        self.user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        self.type_notification = type_notification
        self.titre = titre
        self.message = message
        self.is_read = is_read
        self.lien = lien
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """
        Convertit la notification en dictionnaire
        
        Returns:
            Dictionnaire représentant la notification
        """
        data = {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'type_notification': self.type_notification,
            'titre': self.titre,
            'message': self.message,
            'is_read': self.is_read,
            'lien': self.lien,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
        return data
    
    def save(self):
        """
        Sauvegarde la notification dans la base de données
        
        Returns:
            ID de la notification créée
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        notif_dict = self.to_dict()
        notif_dict['_id'] = self._id
        notif_dict['user_id'] = self.user_id
        
        result = db.notifications.insert_one(notif_dict)
        return str(result.inserted_id)
    
    def mark_as_read(self):
        """
        Marque la notification comme lue
        
        Returns:
            True si la mise à jour a réussi
        """
        db = get_db()
        self.is_read = True
        self.updated_at = datetime.utcnow()
        
        result = db.notifications.update_one(
            {'_id': self._id},
            {'$set': {'is_read': True, 'updated_at': self.updated_at}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def find_by_id(notif_id):
        """
        Trouve une notification par son ID
        
        Args:
            notif_id: ID de la notification (string ou ObjectId)
            
        Returns:
            Instance Notification ou None
        """
        db = get_db()
        try:
            _id = ObjectId(notif_id) if isinstance(notif_id, str) else notif_id
            notif_data = db.notifications.find_one({'_id': _id})
            
            if notif_data:
                return Notification._from_dict(notif_data)
        except Exception as e:
            print(f"Erreur lors de la recherche de la notification: {e}")
        return None
    
    @staticmethod
    def find_by_user(user_id, is_read=None, limit=50):
        """
        Trouve toutes les notifications d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            is_read: Filtrer par statut de lecture (optionnel)
            limit: Nombre maximum de résultats
            
        Returns:
            Liste d'instances Notification
        """
        db = get_db()
        try:
            _id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            query = {'user_id': _id}
            
            if is_read is not None:
                query['is_read'] = is_read
            
            notifs_data = db.notifications.find(query).sort('created_at', -1).limit(limit)
            
            notifs = []
            for notif_data in notifs_data:
                notifs.append(Notification._from_dict(notif_data))
            
            return notifs
        except Exception as e:
            print(f"Erreur lors de la recherche des notifications: {e}")
            return []
    
    @staticmethod
    def count_unread(user_id):
        """
        Compte les notifications non lues d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Nombre de notifications non lues
        """
        db = get_db()
        try:
            _id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            count = db.notifications.count_documents({'user_id': _id, 'is_read': False})
            return count
        except Exception as e:
            print(f"Erreur lors du comptage des notifications: {e}")
            return 0
    
    @staticmethod
    def _from_dict(notif_data):
        """
        Crée une instance Notification à partir d'un dictionnaire
        
        Args:
            notif_data: Dictionnaire contenant les données de la notification
            
        Returns:
            Instance Notification
        """
        notif = Notification(
            user_id=notif_data['user_id'],
            type_notification=notif_data['type_notification'],
            titre=notif_data['titre'],
            message=notif_data['message'],
            is_read=notif_data.get('is_read', False),
            lien=notif_data.get('lien'),
            _id=notif_data['_id']
        )
        notif.created_at = notif_data.get('created_at')
        notif.updated_at = notif_data.get('updated_at')
        return notif
