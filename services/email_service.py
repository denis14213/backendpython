"""
Service d'envoi d'emails pour la plateforme
Gère l'envoi des identifiants, notifications, etc.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """
    Service pour l'envoi d'emails
    """
    
    def __init__(self):
        """
        Initialise le service email avec la configuration
        """
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM', 'noreply@clinique.com')
    
    def send_email(self, to_email, subject, body_html, body_text=None):
        """
        Envoie un email
        
        Args:
            to_email: Email du destinataire
            subject: Sujet de l'email
            body_html: Corps de l'email en HTML
            body_text: Corps de l'email en texte (optionnel)
            
        Returns:
            True si l'email a été envoyé avec succès, False sinon
        """
        try:
            # Création du message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = to_email
            
            # Ajout du contenu texte et HTML
            if body_text:
                part1 = MIMEText(body_text, 'plain', 'utf-8')
                msg.attach(part1)
            
            part2 = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(part2)
            
            # Connexion et envoi
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email envoyé avec succès à {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de l'email à {to_email}: {e}")
            return False
    
    def send_account_credentials(self, to_email, nom, prenom, email, password):
        """
        Envoie les identifiants de compte à un nouvel utilisateur
        
        Args:
            to_email: Email du destinataire
            nom: Nom de l'utilisateur
            prenom: Prénom de l'utilisateur
            email: Email de connexion
            password: Mot de passe temporaire
            
        Returns:
            True si l'email a été envoyé avec succès
        """
        subject = "Vos identifiants de connexion - Clinique Médicale"
        
        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .credentials {{ background-color: white; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .warning {{ color: #d32f2f; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Bienvenue à la Clinique Médicale</h1>
                </div>
                <div class="content">
                    <p>Bonjour {prenom} {nom},</p>
                    <p>Votre compte a été créé avec succès. Voici vos identifiants de connexion :</p>
                    
                    <div class="credentials">
                        <p><strong>Email :</strong> {email}</p>
                        <p><strong>Mot de passe temporaire :</strong> {password}</p>
                    </div>
                    
                    <p class="warning">⚠️ Pour des raisons de sécurité, nous vous recommandons fortement de changer votre mot de passe lors de votre première connexion.</p>
                    
                    <p>Vous pouvez maintenant vous connecter à votre espace en utilisant ces identifiants.</p>
                    
                    <p>Cordialement,<br>L'équipe de la Clinique Médicale</p>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        body_text = f"""
        Bienvenue à la Clinique Médicale
        
        Bonjour {prenom} {nom},
        
        Votre compte a été créé avec succès. Voici vos identifiants de connexion :
        
        Email : {email}
        Mot de passe temporaire : {password}
        
        Pour des raisons de sécurité, nous vous recommandons fortement de changer votre mot de passe lors de votre première connexion.
        
        Vous pouvez maintenant vous connecter à votre espace en utilisant ces identifiants.
        
        Cordialement,
        L'équipe de la Clinique Médicale
        """
        
        return self.send_email(to_email, subject, body_html, body_text)
    
    def send_rdv_confirmation(self, to_email, nom, prenom, date_rdv, heure_rdv, medecin_nom):
        """
        Envoie une confirmation de rendez-vous
        
        Args:
            to_email: Email du destinataire
            nom: Nom du patient
            prenom: Prénom du patient
            date_rdv: Date du rendez-vous
            heure_rdv: Heure du rendez-vous
            medecin_nom: Nom du médecin
            
        Returns:
            True si l'email a été envoyé avec succès
        """
        subject = "Confirmation de votre rendez-vous - Clinique Médicale"
        
        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .rdv-info {{ background-color: white; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Rendez-vous confirmé</h1>
                </div>
                <div class="content">
                    <p>Bonjour {prenom} {nom},</p>
                    <p>Votre rendez-vous a été confirmé avec succès.</p>
                    
                    <div class="rdv-info">
                        <p><strong>Date :</strong> {date_rdv}</p>
                        <p><strong>Heure :</strong> {heure_rdv}</p>
                        <p><strong>Médecin :</strong> {medecin_nom}</p>
                    </div>
                    
                    <p>Nous vous attendons à la date et l'heure indiquées.</p>
                    <p>En cas d'empêchement, merci de nous contacter au plus tôt.</p>
                    
                    <p>Cordialement,<br>L'équipe de la Clinique Médicale</p>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body_html)
    
    def send_password_reset(self, to_email, nom, prenom, reset_token):
        """
        Envoie un lien de réinitialisation de mot de passe
        
        Args:
            to_email: Email du destinataire
            nom: Nom de l'utilisateur
            prenom: Prénom de l'utilisateur
            reset_token: Token de réinitialisation
            
        Returns:
            True si l'email a été envoyé avec succès
        """
        subject = "Réinitialisation de votre mot de passe - Clinique Médicale"
        
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        
        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #FF9800; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #FF9800; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .warning {{ color: #d32f2f; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Réinitialisation de mot de passe</h1>
                </div>
                <div class="content">
                    <p>Bonjour {prenom} {nom},</p>
                    <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
                    <p>Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe :</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Réinitialiser mon mot de passe</a>
                    </div>
                    
                    <p class="warning">⚠️ Ce lien est valide pendant 1 heure uniquement.</p>
                    <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
                    
                    <p>Cordialement,<br>L'équipe de la Clinique Médicale</p>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body_html)

