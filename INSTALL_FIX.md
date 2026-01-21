# 🔧 Solution pour l'erreur d'installation Pillow

## Problème

L'erreur se produit car **Pillow 10.2.0 n'est pas compatible avec Python 3.13**.

## Solution

### Option 1 : Installer Pillow séparément (Recommandé)

```bash
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer Pillow avec la dernière version compatible
pip install Pillow --upgrade

# Puis installer les autres dépendances
pip install -r requirements.txt
```

### Option 2 : Installer sans Pillow d'abord

```bash
# Installer toutes les dépendances sauf Pillow
pip install Flask==3.0.0 Flask-CORS==4.0.0 Flask-Session==0.5.0 pymongo==4.6.0 bcrypt==4.1.1 python-dotenv==1.0.0 email-validator==2.1.0 Werkzeug==3.0.1 Jinja2==3.1.2 reportlab==4.0.7 python-dateutil==2.8.2 pytz==2024.1

# Puis installer Pillow séparément
pip install Pillow
```

### Option 3 : Utiliser une version spécifique de Pillow compatible

```bash
pip install Pillow==10.4.0
```

## Vérification

Après l'installation, vérifiez que tout fonctionne :

```bash
python -c "import PIL; print('Pillow version:', PIL.__version__)"
```

## Note

Le fichier `requirements.txt` a été mis à jour pour utiliser `Pillow>=10.4.0` qui est compatible avec Python 3.13.

Si vous continuez à avoir des problèmes, vous pouvez :
1. Utiliser Python 3.11 ou 3.12 (plus stable avec ces packages)
2. Ou installer Pillow manuellement avec la dernière version

