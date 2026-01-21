"""
Modèle DocumentMedical - Gestion des documents médicaux (radiographies, analyses, etc.)
"""

from datetime import datetime
from bson import ObjectId
from config.database import get_db

class DocumentMedical:
    """
    Classe représentant un document médical
    """
    
    TYPE_RADIO = 'radiographie'
    TYPE_ANALYSE = 'analyse'
    TYPE_ECHO = 'echographie'
    TYPE_SCANNER = 'scanner'
    TYPE_IRM = 'irm'
    TYPE_AUTRE = 'autre'
    
    def __init__(self, patient_id, dossier_id, type_document, nom_fichier,
                 file_data=None, file_type=None, file_size=None, description=None, 
                 date_examen=None, medecin_id=None, _id=None):
        """
        Initialise un document médical
        
        Args:
            patient_id: ID du patient
            dossier_id: ID du dossier médical associé (optionnel)
            type_document: Type de document (radiographie, analyse, etc.)
            nom_fichier: Nom du fichier
            file_data: Données du fichier en base64
            file_type: Type MIME du fichier (image/png, application/pdf, etc.)
            file_size: Taille du fichier en octets
            description: Description du document
            date_examen: Date de l'examen
            medecin_id: ID du médecin prescripteur (optionnel)
            _id: ID MongoDB (si existant)
        """
        self._id = _id if _id else ObjectId()
        self.patient_id = ObjectId(patient_id) if isinstance(patient_id, str) else patient_id
        self.dossier_id = ObjectId(dossier_id) if dossier_id and isinstance(dossier_id, str) else dossier_id
        self.type_document = type_document
        self.nom_fichier = nom_fichier
        self.file_data = file_data  # Données en base64
        self.file_type = file_type  # Type MIME
        self.file_size = file_size  # Taille en octets
        self.description = description
        self.date_examen = date_examen if isinstance(date_examen, datetime) else (datetime.fromisoformat(date_examen) if isinstance(date_examen, str) else date_examen) if date_examen else datetime.utcnow()
        self.medecin_id = ObjectId(medecin_id) if medecin_id and isinstance(medecin_id, str) else medecin_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_file_data=False):
        """
        Convertit le document médical en dictionnaire
        
        Args:
            include_file_data: Si True, inclut les données du fichier (base64)
        
        Returns:
            Dictionnaire représentant le document
        """
        data = {
            '_id': str(self._id),
            'patient_id': str(self.patient_id),
            'dossier_id': str(self.dossier_id) if self.dossier_id else None,
            'type_document': self.type_document,
            'nom_fichier': self.nom_fichier,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'description': self.description,
            'date_examen': self.date_examen.isoformat() if isinstance(self.date_examen, datetime) else self.date_examen,
            'medecin_id': str(self.medecin_id) if self.medecin_id else None,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
        
        # Inclure les données du fichier seulement si demandé (pour le téléchargement)
        if include_file_data:
            data['file_data'] = self.file_data
        
        return data
    
    def save(self):
        """
        Sauvegarde le document médical dans la base de données
        
        Returns:
            ID du document créé
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        doc_dict = self.to_dict(include_file_data=True)  # Inclure les données du fichier
        doc_dict['_id'] = self._id
        doc_dict['patient_id'] = self.patient_id
        if self.dossier_id:
            doc_dict['dossier_id'] = self.dossier_id
        if self.medecin_id:
            doc_dict['medecin_id'] = self.medecin_id
        
        result = db.documents_medicaux.insert_one(doc_dict)
        return str(result.inserted_id)
    
    def update(self):
        """
        Met à jour le document médical dans la base de données
        
        Returns:
            True si la mise à jour a réussi
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        doc_dict = self.to_dict()
        doc_dict.pop('_id', None)
        doc_dict['patient_id'] = self.patient_id
        if doc_dict.get('dossier_id'):
            doc_dict['dossier_id'] = ObjectId(doc_dict['dossier_id'])
        if doc_dict.get('medecin_id'):
            doc_dict['medecin_id'] = ObjectId(doc_dict['medecin_id'])
        
        result = db.documents_medicaux.update_one(
            {'_id': self._id},
            {'$set': doc_dict}
        )
        return result.modified_count > 0
    
    def delete(self):
        """
        Supprime le document médical de la base de données
        
        Returns:
            True si la suppression a réussi
        """
        db = get_db()
        result = db.documents_medicaux.delete_one({'_id': self._id})
        return result.deleted_count > 0
    
    @staticmethod
    def find_by_id(doc_id):
        """
        Trouve un document médical par son ID
        
        Args:
            doc_id: ID du document (string ou ObjectId)
            
        Returns:
            Instance DocumentMedical ou None
        """
        db = get_db()
        try:
            _id = ObjectId(doc_id) if isinstance(doc_id, str) else doc_id
            doc_data = db.documents_medicaux.find_one({'_id': _id})
            
            if doc_data:
                return DocumentMedical._from_dict(doc_data)
        except Exception as e:
            print(f"Erreur lors de la recherche du document médical: {e}")
        return None
    
    @staticmethod
    def find_by_patient(patient_id, type_document=None, limit=50):
        """
        Trouve tous les documents médicaux d'un patient
        
        Args:
            patient_id: ID du patient
            type_document: Filtrer par type de document (optionnel)
            limit: Nombre maximum de résultats
            
        Returns:
            Liste d'instances DocumentMedical
        """
        db = get_db()
        try:
            _id = ObjectId(patient_id) if isinstance(patient_id, str) else patient_id
            query = {'patient_id': _id}
            
            if type_document:
                query['type_document'] = type_document
            
            docs_data = db.documents_medicaux.find(query).sort('date_examen', -1).limit(limit)
            
            docs = []
            for doc_data in docs_data:
                docs.append(DocumentMedical._from_dict(doc_data))
            
            return docs
        except Exception as e:
            print(f"Erreur lors de la recherche des documents médicaux: {e}")
            return []
    
    @staticmethod
    def find_by_dossier(dossier_id, limit=50):
        """
        Trouve tous les documents médicaux d'un dossier
        
        Args:
            dossier_id: ID du dossier médical
            limit: Nombre maximum de résultats
            
        Returns:
            Liste d'instances DocumentMedical
        """
        db = get_db()
        try:
            _id = ObjectId(dossier_id) if isinstance(dossier_id, str) else dossier_id
            docs_data = db.documents_medicaux.find({'dossier_id': _id}).sort('date_examen', -1).limit(limit)
            
            docs = []
            for doc_data in docs_data:
                docs.append(DocumentMedical._from_dict(doc_data))
            
            return docs
        except Exception as e:
            print(f"Erreur lors de la recherche des documents médicaux: {e}")
            return []
    
    @staticmethod
    def _from_dict(doc_data):
        """
        Crée une instance DocumentMedical à partir d'un dictionnaire
        
        Args:
            doc_data: Dictionnaire contenant les données du document
            
        Returns:
            Instance DocumentMedical
        """
        doc = DocumentMedical(
            patient_id=doc_data['patient_id'],
            dossier_id=doc_data.get('dossier_id'),
            type_document=doc_data['type_document'],
            nom_fichier=doc_data['nom_fichier'],
            file_data=doc_data.get('file_data'),
            file_type=doc_data.get('file_type'),
            file_size=doc_data.get('file_size'),
            description=doc_data.get('description'),
            date_examen=doc_data.get('date_examen'),
            medecin_id=doc_data.get('medecin_id'),
            _id=doc_data['_id']
        )
        doc.created_at = doc_data.get('created_at')
        doc.updated_at = doc_data.get('updated_at')
        return doc

