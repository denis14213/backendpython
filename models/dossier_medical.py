"""
Modèle DossierMedical - Gestion des dossiers médicaux des patients
"""

from datetime import datetime
from bson import ObjectId
from config.database import get_db

class DossierMedical:
    """
    Classe représentant un dossier médical
    """
    
    def __init__(self, patient_id, medecin_id, date_consultation, 
                 observations=None, diagnostic=None, examen_clinique=None,
                 poids=None, taille=None, tension_arterielle=None, 
                 temperature=None, _id=None):
        """
        Initialise un dossier médical
        
        Args:
            patient_id: ID du patient
            medecin_id: ID du médecin
            date_consultation: Date de la consultation
            observations: Observations du médecin
            diagnostic: Diagnostic posé
            examen_clinique: Résultats de l'examen clinique
            poids: Poids du patient (kg)
            taille: Taille du patient (cm)
            tension_arterielle: Tension artérielle
            temperature: Température corporelle
            _id: ID MongoDB (si existant)
        """
        self._id = _id if _id else ObjectId()
        self.patient_id = ObjectId(patient_id) if isinstance(patient_id, str) else patient_id
        self.medecin_id = ObjectId(medecin_id) if isinstance(medecin_id, str) else medecin_id
        self.date_consultation = date_consultation if isinstance(date_consultation, datetime) else datetime.fromisoformat(date_consultation) if isinstance(date_consultation, str) else date_consultation
        self.observations = observations
        self.diagnostic = diagnostic
        self.examen_clinique = examen_clinique
        self.poids = poids
        self.taille = taille
        self.tension_arterielle = tension_arterielle
        self.temperature = temperature
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """
        Convertit le dossier médical en dictionnaire
        
        Returns:
            Dictionnaire représentant le dossier médical
        """
        data = {
            '_id': str(self._id),
            'patient_id': str(self.patient_id),
            'medecin_id': str(self.medecin_id),
            'date_consultation': self.date_consultation.isoformat() if isinstance(self.date_consultation, datetime) else self.date_consultation,
            'observations': self.observations,
            'diagnostic': self.diagnostic,
            'examen_clinique': self.examen_clinique,
            'poids': self.poids,
            'taille': self.taille,
            'tension_arterielle': self.tension_arterielle,
            'temperature': self.temperature,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
        return data
    
    def save(self):
        """
        Sauvegarde le dossier médical dans la base de données
        
        Returns:
            ID du dossier créé
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        dossier_dict = self.to_dict()
        dossier_dict['_id'] = self._id
        dossier_dict['patient_id'] = self.patient_id
        dossier_dict['medecin_id'] = self.medecin_id
        
        result = db.dossiers_medicaux.insert_one(dossier_dict)
        return str(result.inserted_id)
    
    def update(self):
        """
        Met à jour le dossier médical dans la base de données
        
        Returns:
            True si la mise à jour a réussi
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        dossier_dict = self.to_dict()
        dossier_dict.pop('_id', None)
        dossier_dict['patient_id'] = self.patient_id
        dossier_dict['medecin_id'] = self.medecin_id
        
        result = db.dossiers_medicaux.update_one(
            {'_id': self._id},
            {'$set': dossier_dict}
        )
        return result.modified_count > 0
    
    @staticmethod
    def find_by_id(dossier_id):
        """
        Trouve un dossier médical par son ID
        
        Args:
            dossier_id: ID du dossier (string ou ObjectId)
            
        Returns:
            Instance DossierMedical ou None
        """
        db = get_db()
        try:
            _id = ObjectId(dossier_id) if isinstance(dossier_id, str) else dossier_id
            dossier_data = db.dossiers_medicaux.find_one({'_id': _id})
            
            if dossier_data:
                return DossierMedical._from_dict(dossier_data)
        except Exception as e:
            print(f"Erreur lors de la recherche du dossier médical: {e}")
        return None
    
    @staticmethod
    def find_by_patient(patient_id, limit=50):
        """
        Trouve tous les dossiers médicaux d'un patient
        
        Args:
            patient_id: ID du patient
            limit: Nombre maximum de résultats
            
        Returns:
            Liste d'instances DossierMedical
        """
        db = get_db()
        try:
            _id = ObjectId(patient_id) if isinstance(patient_id, str) else patient_id
            dossiers_data = db.dossiers_medicaux.find({'patient_id': _id}).sort('date_consultation', -1).limit(limit)
            
            dossiers = []
            for dossier_data in dossiers_data:
                dossiers.append(DossierMedical._from_dict(dossier_data))
            
            return dossiers
        except Exception as e:
            print(f"Erreur lors de la recherche des dossiers médicaux: {e}")
            return []
    
    @staticmethod
    def find_by_medecin(medecin_id, limit=50):
        """
        Trouve tous les dossiers médicaux créés par un médecin
        
        Args:
            medecin_id: ID du médecin
            limit: Nombre maximum de résultats
            
        Returns:
            Liste d'instances DossierMedical
        """
        db = get_db()
        try:
            _id = ObjectId(medecin_id) if isinstance(medecin_id, str) else medecin_id
            dossiers_data = db.dossiers_medicaux.find({'medecin_id': _id}).sort('date_consultation', -1).limit(limit)
            
            dossiers = []
            for dossier_data in dossiers_data:
                dossiers.append(DossierMedical._from_dict(dossier_data))
            
            return dossiers
        except Exception as e:
            print(f"Erreur lors de la recherche des dossiers médicaux: {e}")
            return []
    
    @staticmethod
    def _from_dict(dossier_data):
        """
        Crée une instance DossierMedical à partir d'un dictionnaire
        
        Args:
            dossier_data: Dictionnaire contenant les données du dossier
            
        Returns:
            Instance DossierMedical
        """
        dossier = DossierMedical(
            patient_id=dossier_data['patient_id'],
            medecin_id=dossier_data['medecin_id'],
            date_consultation=dossier_data['date_consultation'],
            observations=dossier_data.get('observations'),
            diagnostic=dossier_data.get('diagnostic'),
            examen_clinique=dossier_data.get('examen_clinique'),
            poids=dossier_data.get('poids'),
            taille=dossier_data.get('taille'),
            tension_arterielle=dossier_data.get('tension_arterielle'),
            temperature=dossier_data.get('temperature'),
            _id=dossier_data['_id']
        )
        dossier.created_at = dossier_data.get('created_at')
        dossier.updated_at = dossier_data.get('updated_at')
        return dossier

