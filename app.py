"""
Application principale Flask pour la gestion de clinique médicale
Point d'entrée de l'application backend
"""

from flask import Flask
from flask_cors import CORS
from flask_session import Session
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Importation des routes
from routes import auth_routes, admin_routes, medecin_routes, secretaire_routes, patient_routes, public_routes

# Importation de la configuration de la base de données
from config.database import init_db

def create_app():
    """
    Factory function pour créer et configurer l'application Flask
    """
    app = Flask(__name__)
    
    # Configuration de l'application
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv('SESSION_TIMEOUT', 3600))
    
    # Configuration CORS pour permettre les requêtes depuis le frontend React
    # En production, utiliser l'URL du frontend déployé
    frontend_urls = os.getenv('FRONTEND_URL', 'http://localhost:3000').split(',')
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3003",
        "http://localhost:5173"
    ] + frontend_urls
    
    CORS(app, 
         supports_credentials=True, 
         origins=allowed_origins,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
    # Initialisation de la session
    Session(app)
    
    # Initialisation de la base de données MongoDB
    init_db()
    
    # Enregistrement des routes
    app.register_blueprint(public_routes.bp, url_prefix='/api/public')
    app.register_blueprint(auth_routes.bp, url_prefix='/api/auth')
    app.register_blueprint(admin_routes.bp, url_prefix='/api/admin')
    app.register_blueprint(medecin_routes.bp, url_prefix='/api/medecin')
    app.register_blueprint(secretaire_routes.bp, url_prefix='/api/secretaire')
    app.register_blueprint(patient_routes.bp, url_prefix='/api/patient')
    
    # Route de health check pour Render
    @app.route('/health')
    @app.route('/api/health')
    def health_check():
        """Health check endpoint pour vérifier que l'API fonctionne"""
        return {
            'status': 'ok',
            'message': 'API is running',
            'environment': os.getenv('FLASK_ENV', 'development')
        }, 200
    
    # Route racine
    @app.route('/')
    def index():
        """Route racine"""
        return {
            'message': 'Clinique Santé Plus API',
            'version': '1.0.0',
            'status': 'running'
        }, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true', port=5000)

