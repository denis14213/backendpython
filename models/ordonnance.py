"""
Modèle Ordonnance - Gestion des ordonnances médicales
"""

from datetime import datetime
from bson import ObjectId
from config.database import get_db

class Ordonnance:
    """
    Classe représentant une ordonnance médicale
    """
    
    def __init__(self, patient_id, medecin_id, date_ordonnance, 
                 traitements=None, instructions=None, pdf_data=None, _id=None):
        """
        Initialise une ordonnance
        
        Args:
            patient_id: ID du patient
            medecin_id: ID du médecin
            date_ordonnance: Date de l'ordonnance
            traitements: Liste des traitements prescrits
            instructions: Instructions particulières
            pdf_data: Données du PDF en base64 (généré à la demande)
            _id: ID MongoDB (si existant)
        """
        self._id = _id if _id else ObjectId()
        self.patient_id = ObjectId(patient_id) if isinstance(patient_id, str) else patient_id
        self.medecin_id = ObjectId(medecin_id) if isinstance(medecin_id, str) else medecin_id
        self.date_ordonnance = date_ordonnance if isinstance(date_ordonnance, datetime) else datetime.fromisoformat(date_ordonnance) if isinstance(date_ordonnance, str) else date_ordonnance
        self.traitements = traitements or []  # Liste de dictionnaires {medicament, posologie, duree}
        self.instructions = instructions
        self.pdf_data = pdf_data  # PDF en base64 (optionnel, généré à la demande)
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_pdf=False):
        """
        Convertit l'ordonnance en dictionnaire
        
        Args:
            include_pdf: Si True, inclut les données du PDF
        
        Returns:
            Dictionnaire représentant l'ordonnance
        """
        data = {
            '_id': str(self._id),
            'patient_id': str(self.patient_id),
            'medecin_id': str(self.medecin_id),
            'date_ordonnance': self.date_ordonnance.isoformat() if isinstance(self.date_ordonnance, datetime) else self.date_ordonnance,
            'traitements': self.traitements,
            'instructions': self.instructions,
            'has_pdf': self.pdf_data is not None,  # Indique si un PDF est disponible
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
        
        # Inclure le PDF seulement si demandé
        if include_pdf and self.pdf_data:
            data['pdf_data'] = self.pdf_data
        
        return data
    
    def save(self):
        """
        Sauvegarde l'ordonnance dans la base de données
        
        Returns:
            ID de l'ordonnance créée
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        ordonnance_dict = self.to_dict(include_pdf=True)  # Inclure le PDF
        ordonnance_dict['_id'] = self._id
        ordonnance_dict['patient_id'] = self.patient_id
        ordonnance_dict['medecin_id'] = self.medecin_id
        
        result = db.ordonnances.insert_one(ordonnance_dict)
        return str(result.inserted_id)
    
    def update(self):
        """
        Met à jour l'ordonnance dans la base de données
        
        Returns:
            True si la mise à jour a réussi
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        ordonnance_dict = self.to_dict(include_pdf=True)  # Inclure le PDF lors de la mise à jour
        ordonnance_dict.pop('_id', None)
        ordonnance_dict['patient_id'] = self.patient_id
        ordonnance_dict['medecin_id'] = self.medecin_id
        
        # Inclure explicitement pdf_data si présent
        if self.pdf_data:
            ordonnance_dict['pdf_data'] = self.pdf_data
        
        result = db.ordonnances.update_one(
            {'_id': self._id},
            {'$set': ordonnance_dict}
        )
        return result.modified_count > 0
    
    @staticmethod
    def find_by_id(ordonnance_id):
        """
        Trouve une ordonnance par son ID
        
        Args:
            ordonnance_id: ID de l'ordonnance (string ou ObjectId)
            
        Returns:
            Instance Ordonnance ou None
        """
        db = get_db()
        try:
            _id = ObjectId(ordonnance_id) if isinstance(ordonnance_id, str) else ordonnance_id
            ordonnance_data = db.ordonnances.find_one({'_id': _id})
            
            if ordonnance_data:
                return Ordonnance._from_dict(ordonnance_data)
        except Exception as e:
            print(f"Erreur lors de la recherche de l'ordonnance: {e}")
        return None
    
    @staticmethod
    def find_by_patient(patient_id, limit=50):
        """
        Trouve toutes les ordonnances d'un patient
        
        Args:
            patient_id: ID du patient
            limit: Nombre maximum de résultats
            
        Returns:
            Liste d'instances Ordonnance
        """
        db = get_db()
        try:
            _id = ObjectId(patient_id) if isinstance(patient_id, str) else patient_id
            ordonnances_data = db.ordonnances.find({'patient_id': _id}).sort('date_ordonnance', -1).limit(limit)
            
            ordonnances = []
            for ordonnance_data in ordonnances_data:
                ordonnances.append(Ordonnance._from_dict(ordonnance_data))
            
            return ordonnances
        except Exception as e:
            print(f"Erreur lors de la recherche des ordonnances: {e}")
            return []
    
    @staticmethod
    def find_by_medecin(medecin_id, limit=50):
        """
        Trouve toutes les ordonnances créées par un médecin
        
        Args:
            medecin_id: ID du médecin
            limit: Nombre maximum de résultats
            
        Returns:
            Liste d'instances Ordonnance
        """
        db = get_db()
        try:
            _id = ObjectId(medecin_id) if isinstance(medecin_id, str) else medecin_id
            ordonnances_data = db.ordonnances.find({'medecin_id': _id}).sort('date_ordonnance', -1).limit(limit)
            
            ordonnances = []
            for ordonnance_data in ordonnances_data:
                ordonnances.append(Ordonnance._from_dict(ordonnance_data))
            
            return ordonnances
        except Exception as e:
            print(f"Erreur lors de la recherche des ordonnances: {e}")
            return []
    
    @staticmethod
    def _from_dict(ordonnance_data):
        """
        Crée une instance Ordonnance à partir d'un dictionnaire
        
        Args:
            ordonnance_data: Dictionnaire contenant les données de l'ordonnance
            
        Returns:
            Instance Ordonnance
        """
        ordonnance = Ordonnance(
            patient_id=ordonnance_data['patient_id'],
            medecin_id=ordonnance_data['medecin_id'],
            date_ordonnance=ordonnance_data['date_ordonnance'],
            traitements=ordonnance_data.get('traitements', []),
            instructions=ordonnance_data.get('instructions'),
            pdf_data=ordonnance_data.get('pdf_data'),
            _id=ordonnance_data['_id']
        )
        ordonnance.created_at = ordonnance_data.get('created_at')
        ordonnance.updated_at = ordonnance_data.get('updated_at')
        return ordonnance

