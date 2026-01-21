"""
Modèle RendezVous - Gestion des rendez-vous médicaux
"""

from datetime import datetime
from bson import ObjectId
from config.database import get_db

class RendezVous:
    """
    Classe représentant un rendez-vous médical
    """
    
    STATUT_DEMANDE = 'demande'
    STATUT_CONFIRME = 'confirme'
    STATUT_ANNULE = 'annule'
    STATUT_TERMINE = 'termine'
    
    def __init__(self, patient_id, medecin_id, date_rdv, heure_rdv, 
                 motif=None, statut=None, notes=None, _id=None):
        """
        Initialise un rendez-vous
        
        Args:
            patient_id: ID du patient
            medecin_id: ID du médecin
            date_rdv: Date du rendez-vous
            heure_rdv: Heure du rendez-vous (format HH:MM)
            motif: Motif de consultation
            statut: Statut du rendez-vous (demande, confirme, annule, termine)
            notes: Notes additionnelles
            _id: ID MongoDB (si existant)
        """
        self._id = _id if _id else ObjectId()
        self.patient_id = ObjectId(patient_id) if isinstance(patient_id, str) else patient_id
        self.medecin_id = ObjectId(medecin_id) if isinstance(medecin_id, str) else medecin_id
        self.date_rdv = date_rdv if isinstance(date_rdv, datetime) else datetime.fromisoformat(date_rdv) if isinstance(date_rdv, str) else date_rdv
        self.heure_rdv = heure_rdv
        self.motif = motif
        self.statut = statut or self.STATUT_DEMANDE
        self.notes = notes
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """
        Convertit le rendez-vous en dictionnaire
        
        Returns:
            Dictionnaire représentant le rendez-vous
        """
        data = {
            '_id': str(self._id),
            'patient_id': str(self.patient_id),
            'medecin_id': str(self.medecin_id),
            'date_rdv': self.date_rdv.isoformat() if isinstance(self.date_rdv, datetime) else self.date_rdv,
            'heure_rdv': self.heure_rdv,
            'motif': self.motif,
            'statut': self.statut,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
        return data
    
    def save(self):
        """
        Sauvegarde le rendez-vous dans la base de données
        
        Returns:
            ID du rendez-vous créé
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        rdv_dict = self.to_dict()
        rdv_dict['_id'] = self._id
        rdv_dict['patient_id'] = self.patient_id
        rdv_dict['medecin_id'] = self.medecin_id
        
        result = db.rendezvous.insert_one(rdv_dict)
        return str(result.inserted_id)
    
    def update(self):
        """
        Met à jour le rendez-vous dans la base de données
        
        Returns:
            True si la mise à jour a réussi
        """
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        rdv_dict = self.to_dict()
        rdv_dict.pop('_id', None)
        rdv_dict['patient_id'] = self.patient_id
        rdv_dict['medecin_id'] = self.medecin_id
        
        result = db.rendezvous.update_one(
            {'_id': self._id},
            {'$set': rdv_dict}
        )
        return result.modified_count > 0
    
    def delete(self):
        """
        Supprime le rendez-vous de la base de données
        
        Returns:
            True si la suppression a réussi
        """
        db = get_db()
        result = db.rendezvous.delete_one({'_id': self._id})
        return result.deleted_count > 0
    
    @staticmethod
    def find_by_id(rdv_id):
        """
        Trouve un rendez-vous par son ID
        
        Args:
            rdv_id: ID du rendez-vous (string ou ObjectId)
            
        Returns:
            Instance RendezVous ou None
        """
        db = get_db()
        try:
            _id = ObjectId(rdv_id) if isinstance(rdv_id, str) else rdv_id
            rdv_data = db.rendezvous.find_one({'_id': _id})
            
            if rdv_data:
                return RendezVous._from_dict(rdv_data)
        except Exception as e:
            print(f"Erreur lors de la recherche du rendez-vous: {e}")
        return None
    
    @staticmethod
    def find_by_patient(patient_id, statut=None):
        """
        Trouve tous les rendez-vous d'un patient
        
        Args:
            patient_id: ID du patient
            statut: Filtrer par statut (optionnel)
            
        Returns:
            Liste d'instances RendezVous
        """
        db = get_db()
        try:
            _id = ObjectId(patient_id) if isinstance(patient_id, str) else patient_id
            query = {'patient_id': _id}
            if statut:
                query['statut'] = statut
            
            rdvs_data = db.rendezvous.find(query).sort('date_rdv', -1)
            
            rdvs = []
            for rdv_data in rdvs_data:
                rdvs.append(RendezVous._from_dict(rdv_data))
            
            return rdvs
        except Exception as e:
            print(f"Erreur lors de la recherche des rendez-vous: {e}")
            return []
    
    @staticmethod
    def find_by_medecin(medecin_id, date_debut=None, date_fin=None, statut=None):
        """
        Trouve tous les rendez-vous d'un médecin
        
        Args:
            medecin_id: ID du médecin
            date_debut: Date de début (optionnel)
            date_fin: Date de fin (optionnel)
            statut: Filtrer par statut (optionnel)
            
        Returns:
            Liste d'instances RendezVous
        """
        db = get_db()
        try:
            _id = ObjectId(medecin_id) if isinstance(medecin_id, str) else medecin_id
            query = {'medecin_id': _id}
            
            if date_debut or date_fin:
                date_query = {}
                if date_debut:
                    if isinstance(date_debut, str):
                        date_debut = datetime.fromisoformat(date_debut)
                    date_query['$gte'] = date_debut
                if date_fin:
                    if isinstance(date_fin, str):
                        date_fin = datetime.fromisoformat(date_fin)
                    date_query['$lte'] = date_fin
                query['date_rdv'] = date_query
            
            if statut:
                query['statut'] = statut
            
            rdvs_data = db.rendezvous.find(query).sort('date_rdv', 1)
            
            rdvs = []
            for rdv_data in rdvs_data:
                rdvs.append(RendezVous._from_dict(rdv_data))
            
            return rdvs
        except Exception as e:
            print(f"Erreur lors de la recherche des rendez-vous: {e}")
            return []
    
    @staticmethod
    def find_by_date(date_rdv, medecin_id=None):
        """
        Trouve tous les rendez-vous d'une date donnée
        
        Args:
            date_rdv: Date du rendez-vous
            medecin_id: ID du médecin (optionnel)
            
        Returns:
            Liste d'instances RendezVous
        """
        db = get_db()
        try:
            if isinstance(date_rdv, str):
                date_rdv = datetime.fromisoformat(date_rdv.split('T')[0])
            elif not isinstance(date_rdv, datetime):
                date_rdv = datetime.combine(date_rdv, datetime.min.time())
            
            # Recherche pour toute la journée
            date_debut = datetime.combine(date_rdv.date(), datetime.min.time())
            date_fin = datetime.combine(date_rdv.date(), datetime.max.time())
            
            query = {
                'date_rdv': {
                    '$gte': date_debut,
                    '$lte': date_fin
                }
            }
            
            if medecin_id:
                _id = ObjectId(medecin_id) if isinstance(medecin_id, str) else medecin_id
                query['medecin_id'] = _id
            
            rdvs_data = db.rendezvous.find(query).sort('heure_rdv', 1)
            
            rdvs = []
            for rdv_data in rdvs_data:
                rdvs.append(RendezVous._from_dict(rdv_data))
            
            return rdvs
        except Exception as e:
            print(f"Erreur lors de la recherche des rendez-vous: {e}")
            return []
    
    @staticmethod
    def check_disponibilite(medecin_id, date_rdv, heure_rdv):
        """
        Vérifie si un créneau est disponible pour un médecin
        
        Args:
            medecin_id: ID du médecin
            date_rdv: Date du rendez-vous
            heure_rdv: Heure du rendez-vous
            
        Returns:
            True si disponible, False sinon
        """
        db = get_db()
        try:
            if isinstance(date_rdv, str):
                date_rdv = datetime.fromisoformat(date_rdv.split('T')[0])
            elif not isinstance(date_rdv, datetime):
                date_rdv = datetime.combine(date_rdv, datetime.min.time())
            
            _id = ObjectId(medecin_id) if isinstance(medecin_id, str) else medecin_id
            
            # Recherche des rendez-vous confirmés à cette date et heure
            existing_rdv = db.rendezvous.find_one({
                'medecin_id': _id,
                'date_rdv': date_rdv,
                'heure_rdv': heure_rdv,
                'statut': {'$in': [RendezVous.STATUT_CONFIRME, RendezVous.STATUT_DEMANDE]}
            })
            
            return existing_rdv is None
        except Exception as e:
            print(f"Erreur lors de la vérification de disponibilité: {e}")
            return False
    
    @staticmethod
    def _from_dict(rdv_data):
        """
        Crée une instance RendezVous à partir d'un dictionnaire
        
        Args:
            rdv_data: Dictionnaire contenant les données du rendez-vous
            
        Returns:
            Instance RendezVous
        """
        rdv = RendezVous(
            patient_id=rdv_data['patient_id'],
            medecin_id=rdv_data['medecin_id'],
            date_rdv=rdv_data['date_rdv'],
            heure_rdv=rdv_data['heure_rdv'],
            motif=rdv_data.get('motif'),
            statut=rdv_data.get('statut', RendezVous.STATUT_DEMANDE),
            notes=rdv_data.get('notes'),
            _id=rdv_data['_id']
        )
        rdv.created_at = rdv_data.get('created_at')
        rdv.updated_at = rdv_data.get('updated_at')
        return rdv

