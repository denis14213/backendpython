# ⚡ Démarrage Rapide

## 🚀 En 3 étapes

### 1️⃣ Vérifier l'installation

```bash
cd backend
python check_setup.py
```

Ce script vérifie :
- ✅ Version de Python
- ✅ Dépendances installées
- ✅ Fichier .env présent
- ✅ Connexion MongoDB

### 2️⃣ Créer le premier administrateur

```bash
python init_admin.py
```

**Exemple de saisie** :
```
Email: admin@clinique.fr
Nom: Dupont
Prénom: Jean
Téléphone: +33 1 23 45 67 89
Mot de passe: Admin123!
```

### 3️⃣ Lancer le serveur

```bash
python app.py
```

Le serveur sera accessible sur : **http://localhost:5000**

## 📝 Configuration minimale (.env)

Créez un fichier `.env` dans le dossier `backend/` :

```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=clinique_db
SECRET_KEY=changez-moi-en-production-123456789
FLASK_DEBUG=True
```

## ✅ Test rapide

Une fois le serveur lancé, testez avec :

```bash
# Test de santé
curl http://localhost:5000/api/public/info

# Test de connexion
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@clinique.fr","password":"Admin123!"}'
```

## 🐛 Problèmes courants

**MongoDB ne démarre pas ?**
- Windows : Vérifiez le service dans "Services"
- Linux : `sudo systemctl start mongod`
- Mac : `brew services start mongodb-community`

**Port 5000 déjà utilisé ?**
- Changez le port dans `app.py` : `app.run(port=5001)`

**Module non trouvé ?**
- Installez les dépendances : `pip install -r requirements.txt`

---

📖 Pour plus de détails, consultez `GUIDE_DEMARRAGE.md`

