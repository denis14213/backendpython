"""
Modèle Medecin - Informations spécifiques aux médecins
"""

from datetime import datetime
from bson import ObjectId
from config.database import get_db

class Medecin:
    """
    Classe représentant un médecin avec ses informations professionnelles
    """
    
    def __init__(self, user_id, specialite, numero_ordre=None, 
                 horaires_travail=None, signature_data=None, signature_type=None, _id=None):
        """
        Initialise un médecin
        
        Args:
            user_id: ID de l'utilisateur associé
            specialite: Spécialité médicale
            numero_ordre: Numéro d'ordre du médecin
            horaires_travail: Horaires de travail (dict)
            signature_data: Signature numérique en base64
            signature_type: Type MIME de la signature (image/png, image/jpeg)
            _id: ID MongoDB (si existant)
        """
        self._id = _id if _id else ObjectId()
        self.user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        self.specialite = specialite
        self.numero_ordre = numero_ordre
        self.horaires_travail = horaires_travail or {}
        self.signature_data = signature_data  # Signature en base64
        self.signature_type = signature_type  # Type MIME
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """
        Convertit le médecin en dictionnaire
        
        Returns:
            Dictionnaire représentant le médecin
        """
        data = {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'specialite': self.specialite,
            'numero_ordre': self.numero_ordre,
            'horaires_travail': self.horaires_travail,
            'has_signature': self.signature_data is not None,  # Indique si une signature existe
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
        return data
    
    def save(self):
        """
        Sauvegarde le médecin dans la base de données
        
        Returns:
            ID du médecin créé
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        medecin_dict = self.to_dict()
        medecin_dict['_id'] = self._id
        medecin_dict['user_id'] = self.user_id
        
        result = db.medecins.insert_one(medecin_dict)
        return str(result.inserted_id)
    
    def update(self):
        """
        Met à jour le médecin dans la base de données
        
        Returns:
            True si la mise à jour a réussi
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        medecin_dict = self.to_dict()
        medecin_dict.pop('_id', None)
        medecin_dict['user_id'] = self.user_id
        
        # Inclure explicitement signature_data et signature_type si présents
        if self.signature_data:
            medecin_dict['signature_data'] = self.signature_data
            medecin_dict['signature_type'] = self.signature_type
        
        result = db.medecins.update_one(
            {'_id': self._id},
            {'$set': medecin_dict}
        )
        return result.modified_count > 0
    
    @staticmethod
    def find_by_user_id(user_id):
        """
        Trouve un médecin par l'ID de son compte utilisateur
        
        Args:
            user_id: ID du compte utilisateur
            
        Returns:
            Instance Medecin ou None
        """
        db = get_db()
        try:
            _id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            medecin_data = db.medecins.find_one({'user_id': _id})
            
            if medecin_data:
                return Medecin._from_dict(medecin_data)
        except Exception as e:
            print(f"Erreur lors de la recherche du médecin: {e}")
        return None
    
    @staticmethod
    def find_by_specialite(specialite):
        """
        Trouve tous les médecins d'une spécialité
        
        Args:
            specialite: Spécialité médicale
            
        Returns:
            Liste d'instances Medecin
        """
        db = get_db()
        medecins_data = db.medecins.find({'specialite': specialite})
        
        medecins = []
        for medecin_data in medecins_data:
            medecins.append(Medecin._from_dict(medecin_data))
        
        return medecins
    
    @staticmethod
    def find_all():
        """
        Trouve tous les médecins
        
        Returns:
            Liste d'instances Medecin
        """
        db = get_db()
        medecins_data = db.medecins.find()
        
        medecins = []
        for medecin_data in medecins_data:
            medecins.append(Medecin._from_dict(medecin_data))
        
        return medecins
    
    @staticmethod
    def _from_dict(medecin_data):
        """
        Crée une instance Medecin à partir d'un dictionnaire
        
        Args:
            medecin_data: Dictionnaire contenant les données du médecin
            
        Returns:
            Instance Medecin
        """
        medecin = Medecin(
            user_id=medecin_data['user_id'],
            specialite=medecin_data['specialite'],
            numero_ordre=medecin_data.get('numero_ordre'),
            horaires_travail=medecin_data.get('horaires_travail', {}),
            signature_data=medecin_data.get('signature_data'),
            signature_type=medecin_data.get('signature_type'),
            _id=medecin_data['_id']
        )
        medecin.created_at = medecin_data.get('created_at')
        medecin.updated_at = medecin_data.get('updated_at')
        return medecin

