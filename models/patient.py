"""
Modèle Patient - Gestion des patients de la clinique
"""

from datetime import datetime
from bson import ObjectId
from config.database import get_db

class Patient:
    """
    Classe représentant un patient
    """
    
    def __init__(self, nom, prenom, email=None, telephone=None, date_naissance=None, 
                 adresse=None, ville=None, code_postal=None, sexe=None, 
                 numero_securite_sociale=None, user_id=None, _id=None):
        """
        Initialise un patient
        
        Args:
            nom: Nom de famille
            prenom: Prénom
            email: Email (optionnel, peut être lié à un compte utilisateur)
            telephone: Numéro de téléphone
            date_naissance: Date de naissance
            adresse: Adresse postale
            ville: Ville
            code_postal: Code postal
            sexe: Sexe (M/F)
            numero_securite_sociale: Numéro de sécurité sociale
            user_id: ID du compte utilisateur associé (si existe)
            _id: ID MongoDB (si existant)
        """
        self._id = _id if _id else ObjectId()
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.telephone = telephone
        self.date_naissance = date_naissance
        self.adresse = adresse
        self.ville = ville
        self.code_postal = code_postal
        self.sexe = sexe
        self.numero_securite_sociale = numero_securite_sociale
        self.user_id = ObjectId(user_id) if user_id and isinstance(user_id, str) else user_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """
        Convertit le patient en dictionnaire
        
        Returns:
            Dictionnaire représentant le patient
        """
        data = {
            '_id': str(self._id),
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'telephone': self.telephone,
            'date_naissance': self.date_naissance.isoformat() if isinstance(self.date_naissance, datetime) else self.date_naissance,
            'adresse': self.adresse,
            'ville': self.ville,
            'code_postal': self.code_postal,
            'sexe': self.sexe,
            'numero_securite_sociale': self.numero_securite_sociale,
            'user_id': str(self.user_id) if self.user_id else None,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
        return data
    
    def save(self):
        """
        Sauvegarde le patient dans la base de données
        
        Returns:
            ID du patient créé
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        patient_dict = self.to_dict()
        patient_dict['_id'] = self._id
        if self.user_id:
            patient_dict['user_id'] = self.user_id
        
        result = db.patients.insert_one(patient_dict)
        return str(result.inserted_id)
    
    def update(self):
        """
        Met à jour le patient dans la base de données
        
        Returns:
            True si la mise à jour a réussi
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        patient_dict = self.to_dict()
        patient_dict.pop('_id', None)
        if patient_dict.get('user_id'):
            patient_dict['user_id'] = ObjectId(patient_dict['user_id'])
        
        result = db.patients.update_one(
            {'_id': self._id},
            {'$set': patient_dict}
        )
        return result.modified_count > 0
    
    @staticmethod
    def find_by_id(patient_id):
        """
        Trouve un patient par son ID
        
        Args:
            patient_id: ID du patient (string ou ObjectId)
            
        Returns:
            Instance Patient ou None
        """
        db = get_db()
        try:
            _id = ObjectId(patient_id) if isinstance(patient_id, str) else patient_id
            patient_data = db.patients.find_one({'_id': _id})
            
            if patient_data:
                return Patient._from_dict(patient_data)
        except Exception as e:
            print(f"Erreur lors de la recherche du patient: {e}")
        return None
    
    @staticmethod
    def find_by_email(email):
        """
        Trouve un patient par son email
        
        Args:
            email: Email du patient
            
        Returns:
            Instance Patient ou None
        """
        db = get_db()
        patient_data = db.patients.find_one({'email': email})
        
        if patient_data:
            return Patient._from_dict(patient_data)
        return None
    
    @staticmethod
    def find_by_user_id(user_id):
        """
        Trouve un patient par l'ID de son compte utilisateur
        
        Args:
            user_id: ID du compte utilisateur
            
        Returns:
            Instance Patient ou None
        """
        db = get_db()
        try:
            _id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            patient_data = db.patients.find_one({'user_id': _id})
            
            if patient_data:
                return Patient._from_dict(patient_data)
        except Exception as e:
            print(f"Erreur lors de la recherche du patient: {e}")
        return None
    
    @staticmethod
    def search(query_text):
        """
        Recherche de patients par nom, prénom, email ou téléphone
        
        Args:
            query_text: Texte de recherche
            
        Returns:
            Liste d'instances Patient
        """
        db = get_db()
        regex_query = {'$regex': query_text, '$options': 'i'}
        
        patients_data = db.patients.find({
            '$or': [
                {'nom': regex_query},
                {'prenom': regex_query},
                {'email': regex_query},
                {'telephone': regex_query}
            ]
        })
        
        patients = []
        for patient_data in patients_data:
            patients.append(Patient._from_dict(patient_data))
        
        return patients
    
    @staticmethod
    def find_all(limit=100, skip=0):
        """
        Trouve tous les patients avec pagination
        
        Args:
            limit: Nombre maximum de résultats
            skip: Nombre de résultats à ignorer
            
        Returns:
            Liste d'instances Patient
        """
        db = get_db()
        patients_data = db.patients.find().skip(skip).limit(limit).sort('created_at', -1)
        
        patients = []
        for patient_data in patients_data:
            patients.append(Patient._from_dict(patient_data))
        
        return patients
    
    @staticmethod
    def _from_dict(patient_data):
        """
        Crée une instance Patient à partir d'un dictionnaire
        
        Args:
            patient_data: Dictionnaire contenant les données du patient
            
        Returns:
            Instance Patient
        """
        patient = Patient(
            nom=patient_data['nom'],
            prenom=patient_data['prenom'],
            email=patient_data.get('email'),
            telephone=patient_data.get('telephone'),
            date_naissance=patient_data.get('date_naissance'),
            adresse=patient_data.get('adresse'),
            ville=patient_data.get('ville'),
            code_postal=patient_data.get('code_postal'),
            sexe=patient_data.get('sexe'),
            numero_securite_sociale=patient_data.get('numero_securite_sociale'),
            user_id=patient_data.get('user_id'),
            _id=patient_data['_id']
        )
        patient.created_at = patient_data.get('created_at')
        patient.updated_at = patient_data.get('updated_at')
        return patient

