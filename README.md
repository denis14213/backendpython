# Backend - Plateforme de Gestion de Clinique Médicale

## 📋 Description

Backend Python Flask pour la gestion complète d'une clinique médicale avec MongoDB.

## 🏗️ Architecture

Le projet suit une architecture **MVC (Model-View-Controller)** :

```
backend/
├── app.py                 # Point d'entrée de l'application
├── config/               # Configuration (base de données)
├── models/               # Modèles de données (MongoDB)
├── controllers/          # Contrôleurs (logique métier)
├── routes/               # Routes API (endpoints)
├── middleware/           # Middleware (authentification, permissions)
├── services/             # Services (email, PDF)
└── requirements.txt      # Dépendances Python
```

## 🚀 Installation

### Prérequis

- Python 3.8+
- MongoDB (local ou distant)
- pip

### Étapes d'installation

1. **Cloner le projet** (si nécessaire)

2. **Installer les dépendances** :
```bash
cd backend
pip install -r requirements.txt
```

3. **Configurer les variables d'environnement** :
   - Créer un fichier `.env` à la racine du dossier `backend`
   - Copier le contenu de `.env.example` et remplir les valeurs

4. **Initialiser MongoDB** :
   - Démarrer MongoDB localement ou configurer l'URI dans `.env`

5. **Créer le premier administrateur** :
```bash
python init_admin.py
```

6. **Lancer l'application** :
```bash
python app.py
```

L'API sera accessible sur `http://localhost:5000`

## 📁 Structure des Modules

### Models (Modèles)

- `user.py` - Utilisateurs (admin, médecin, secrétaire, patient)
- `patient.py` - Patients de la clinique
- `medecin.py` - Informations spécifiques aux médecins
- `rendezvous.py` - Rendez-vous médicaux
- `dossier_medical.py` - Dossiers médicaux
- `ordonnance.py` - Ordonnances médicales
- `document_medical.py` - Documents médicaux (radiographies, analyses)
- `notification.py` - Notifications utilisateurs

### Controllers (Contrôleurs)

- `auth_controller.py` - Authentification (login, logout, mot de passe)
- `admin_controller.py` - Gestion complète (utilisateurs, statistiques)
- `medecin_controller.py` - Espace médecin (dossiers, ordonnances)
- `secretaire_controller.py` - Espace secrétaire (patients, RDV)
- `patient_controller.py` - Espace patient (inscription, dashboard)
- `public_controller.py` - Informations publiques (médecins, spécialités)

### Routes

Les routes sont organisées par module :
- `/api/public` - Routes publiques
- `/api/auth` - Authentification
- `/api/admin` - Administration (nécessite rôle admin)
- `/api/medecin` - Médecin (nécessite rôle medecin)
- `/api/secretaire` - Secrétaire (nécessite rôle secretaire)
- `/api/patient` - Patient (nécessite authentification)

## 🔐 Sécurité

- **Mots de passe** : Hashés avec bcrypt
- **Sessions** : Gérées par Flask-Session
- **RBAC** : Permissions basées sur les rôles
- **CORS** : Configuré pour le frontend React

## 📧 Email

Le service d'email envoie automatiquement :
- Identifiants de connexion lors de la création de compte
- Confirmations de rendez-vous
- Notifications importantes

**Note** : Configurer SMTP dans `.env` pour activer l'envoi d'emails.

## 📄 Génération PDF

Le service PDF génère des ordonnances au format PDF utilisant ReportLab.

## 🗄️ Base de Données

MongoDB avec les collections suivantes :
- `users` - Utilisateurs
- `patients` - Patients
- `medecins` - Médecins
- `rendezvous` - Rendez-vous
- `dossiers_medicaux` - Dossiers médicaux
- `ordonnances` - Ordonnances
- `documents_medicaux` - Documents médicaux
- `notifications` - Notifications

Les index sont créés automatiquement pour optimiser les performances.

## 🔧 Configuration

Variables d'environnement importantes dans `.env` :

- `MONGODB_URI` - URI de connexion MongoDB
- `MONGODB_DB_NAME` - Nom de la base de données
- `SECRET_KEY` - Clé secrète Flask
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - Configuration email

## 📝 Notes

- Tous les commentaires dans le code sont en français
- L'architecture respecte le pattern MVC
- Les erreurs sont gérées et retournées en JSON
- Les dates sont gérées en UTC

## 🐛 Dépannage

**Erreur de connexion MongoDB** :
- Vérifier que MongoDB est démarré
- Vérifier l'URI dans `.env`

**Erreur d'import** :
- Vérifier que toutes les dépendances sont installées
- Vérifier que vous êtes dans le bon répertoire

**Erreur d'authentification** :
- Vérifier que le premier admin a été créé avec `init_admin.py`
# backendpython
