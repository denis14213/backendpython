# 🚀 Guide de Démarrage - Backend Clinique Médicale

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python 3.8+** : [Télécharger Python](https://www.python.org/downloads/)
- **MongoDB** : [Télécharger MongoDB](https://www.mongodb.com/try/download/community)
- **pip** : Généralement inclus avec Python

## 🔧 Installation

### 1. Installer les dépendances Python

```bash
cd backend
pip install -r requirements.txt
```

Si vous utilisez un environnement virtuel (recommandé) :

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate
# Sur Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configurer MongoDB

#### Option A : MongoDB Local

1. **Démarrer MongoDB** :
   - **Windows** : Le service MongoDB démarre généralement automatiquement après l'installation
   - **Linux** : `sudo systemctl start mongod`
   - **Mac** : `brew services start mongodb-community`

2. **Vérifier que MongoDB fonctionne** :
   ```bash
   mongosh
   # ou
   mongo
   ```

#### Option B : MongoDB Atlas (Cloud)

1. Créer un compte sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Créer un cluster gratuit
3. Obtenir l'URI de connexion

### 3. Configurer les variables d'environnement

1. **Créer le fichier `.env`** dans le dossier `backend/` :

```env
# Configuration MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=clinique_db

# Configuration Flask
SECRET_KEY=votre-cle-secrete-changez-en-production-123456789
FLASK_DEBUG=True
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
SESSION_TIMEOUT=3600

# Configuration Bcrypt
BCRYPT_ROUNDS=12

# Configuration Email (SMTP) - Optionnel
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app
EMAIL_FROM=noreply@clinique-medicale.fr
```

**⚠️ Important** : 
- Changez `SECRET_KEY` par une clé aléatoire en production
- Pour Gmail, utilisez un "Mot de passe d'application" (pas votre mot de passe normal)

## 🎯 Démarrage

### Étape 1 : Démarrer MongoDB

Assurez-vous que MongoDB est démarré :

```bash
# Vérifier le statut (Windows)
sc query MongoDB

# Vérifier le statut (Linux)
sudo systemctl status mongod
```

### Étape 2 : Créer le premier administrateur

```bash
cd backend
python init_admin.py
```

Vous serez invité à saisir :
- Email
- Nom
- Prénom
- Téléphone (optionnel)
- Mot de passe

**Exemple** :
```
Email: admin@clinique.fr
Nom: Dupont
Prénom: Jean
Téléphone: +33 1 23 45 67 89
Mot de passe: Admin123!
```

### Étape 3 : Lancer le serveur

```bash
python app.py
```

Vous devriez voir :
```
✅ Connexion à MongoDB réussie
✅ Index MongoDB créés avec succès
 * Running on http://127.0.0.1:5000
```

## ✅ Vérification

### Tester l'API

1. **Test de santé** :
   ```bash
   curl http://localhost:5000/api/public/info
   ```

2. **Test de connexion** (avec Postman ou curl) :
   ```bash
   curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@clinique.fr","password":"Admin123!"}' \
     -c cookies.txt
   ```

3. **Vérifier les routes disponibles** :
   - Public : `http://localhost:5000/api/public/info`
   - Public : `http://localhost:5000/api/public/medecins`
   - Public : `http://localhost:5000/api/public/specialites`

## 🐛 Dépannage

### Erreur : "Connection refused" ou "Cannot connect to MongoDB"

**Solution** :
1. Vérifier que MongoDB est démarré
2. Vérifier l'URI dans `.env`
3. Vérifier que le port 27017 n'est pas bloqué par un firewall

```bash
# Tester la connexion MongoDB
mongosh "mongodb://localhost:27017/"
```

### Erreur : "ModuleNotFoundError"

**Solution** :
```bash
# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur : "Port 5000 already in use"

**Solution** :
1. Changer le port dans `app.py` :
   ```python
   app.run(debug=True, port=5001)
   ```
2. Ou arrêter le processus utilisant le port 5000

### Erreur lors de la création de l'admin

**Solution** :
1. Vérifier que MongoDB est accessible
2. Vérifier que la base de données n'a pas de contraintes
3. Vérifier les logs pour plus de détails

## 📝 Prochaines étapes

Une fois le backend démarré :

1. **Tester les endpoints** avec Postman ou curl
2. **Créer des utilisateurs** via l'interface admin
3. **Démarrer le frontend** (voir `../frontend/README.md`)
4. **Configurer l'email** pour recevoir les notifications

## 🔗 URLs importantes

- **API Base URL** : `http://localhost:5000/api`
- **Public Info** : `http://localhost:5000/api/public/info`
- **Login** : `http://localhost:5000/api/auth/login`
- **Admin Dashboard** : `http://localhost:5000/api/admin/statistiques` (nécessite authentification)

## 📞 Support

En cas de problème :
1. Vérifier les logs dans la console
2. Vérifier la configuration MongoDB
3. Vérifier les variables d'environnement dans `.env`

---

**Bon développement ! 🎉**

