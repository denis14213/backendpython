"""
Service de génération de PDF pour les ordonnances
Design professionnel et moderne
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import os

class PDFService:
    """
    Service pour la génération de PDF d'ordonnances médicales
    Design professionnel avec en-tête, pied de page et signature
    """
    
    @staticmethod
    def _header_footer(canvas_obj, doc):
        """
        Ajoute l'en-tête et le pied de page sur chaque page
        """
        canvas_obj.saveState()
        
        # En-tête - Ligne de séparation
        canvas_obj.setStrokeColor(colors.HexColor('#0284c7'))
        canvas_obj.setLineWidth(2)
        canvas_obj.line(2*cm, A4[1] - 1.5*cm, A4[0] - 2*cm, A4[1] - 1.5*cm)
        
        # Pied de page - Ligne de séparation
        canvas_obj.setStrokeColor(colors.HexColor('#cbd5e1'))
        canvas_obj.setLineWidth(1)
        canvas_obj.line(2*cm, 2*cm, A4[0] - 2*cm, 2*cm)
        
        # Numéro de page
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.HexColor('#64748b'))
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.drawRightString(A4[0] - 2*cm, 1.5*cm, text)
        
        canvas_obj.restoreState()
    
    @staticmethod
    def generate_ordonnance(ordonnance, patient, medecin_user, medecin_info):
        """
        Génère un PDF d'ordonnance professionnelle et retourne les données en base64
        
        Args:
            ordonnance: Instance Ordonnance
            patient: Instance Patient
            medecin_user: Instance User (médecin)
            medecin_info: Instance Medecin
            
        Returns:
            Données du PDF en base64 (string)
        """
        from io import BytesIO
        import base64
        
        # Créer un buffer en mémoire au lieu d'un fichier
        buffer = BytesIO()
        
        # Création du document PDF dans le buffer
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            leftMargin=2*cm, 
            rightMargin=2*cm,
            topMargin=2.5*cm, 
            bottomMargin=2.5*cm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # ==================== STYLES PERSONNALISÉS ====================
        
        # Style titre principal
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0284c7'),
            spaceAfter=5,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=28
        )
        
        # Style sous-titre
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER,
            fontName='Helvetica',
            spaceAfter=20
        )
        
        # Style section
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#0284c7'),
            borderPadding=5,
            backColor=colors.HexColor('#f0f9ff'),
            leftIndent=10
        )
        
        # Style texte normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1e293b'),
            leading=14,
            alignment=TA_LEFT
        )
        
        # ==================== EN-TÊTE CLINIQUE ====================
        
        # Logo et nom de la clinique
        story.append(Paragraph("CLINIQUE SANTÉ PLUS", title_style))
        story.append(Paragraph("Centre Médical Spécialisé - Soins de Qualité", subtitle_style))
        
        # Informations de contact dans un tableau élégant
        contact_data = [
            ["📍", "123 Avenue de la Santé, 75000 Tunis, Tunisie"],
            ["📞", "Tél: +216 1 23 45 67 89  |  Fax: +216 1 23 45 67 90"],
            ["📧", "contact@cliniquesanteplus.fr  |  www.cliniquesanteplus.fr"],
        ]
        
        contact_table = Table(contact_data, colWidths=[1*cm, 15*cm])
        contact_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#475569')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(contact_table)
        story.append(Spacer(1, 0.8*cm))
        
        # ==================== TITRE ORDONNANCE ====================
        
        # Bandeau titre
        ordonnance_title = ParagraphStyle(
            'OrdonnanceTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=24
        )
        
        title_data = [[Paragraph("ORDONNANCE MÉDICALE", ordonnance_title)]]
        title_table = Table(title_data, colWidths=[17*cm])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0284c7')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        story.append(title_table)
        story.append(Spacer(1, 0.6*cm))
        
        # ==================== INFORMATIONS PATIENT ====================
        
        story.append(Paragraph("INFORMATIONS DU PATIENT", section_style))
        story.append(Spacer(1, 0.3*cm))
        
        patient_nom = f"{patient.prenom} {patient.nom}".upper()
        date_naissance = patient.date_naissance
        if isinstance(date_naissance, datetime):
            date_naissance = date_naissance.strftime('%d/%m/%Y')
        
        patient_data = [
            ["Nom complet:", patient_nom],
            ["Date de naissance:", date_naissance or 'Non renseignée'],
            ["Adresse:", patient.adresse or 'Non renseignée'],
            ["Téléphone:", patient.telephone or 'Non renseigné'],
        ]
        
        patient_table = Table(patient_data, colWidths=[4*cm, 13*cm])
        patient_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#334155')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#0284c7')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bfdbfe')),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.5*cm))
        
        # ==================== DATE ET MÉDECIN ====================
        
        date_ordonnance = ordonnance.date_ordonnance
        if isinstance(date_ordonnance, str):
            date_ordonnance = datetime.fromisoformat(date_ordonnance.split('T')[0])
        date_str = date_ordonnance.strftime('%d/%m/%Y')
        
        medecin_nom = f"Dr. {medecin_user.prenom} {medecin_user.nom}"
        specialite = medecin_info.specialite if medecin_info else "Médecin généraliste"
        
        info_data = [
            ["Date de prescription:", date_str, "Médecin prescripteur:", medecin_nom],
            ["", "", "Spécialité:", specialite],
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 4.5*cm, 4*cm, 4.5*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#475569')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.6*cm))
        
        # ==================== PRESCRIPTIONS ====================
        
        story.append(Paragraph("PRESCRIPTIONS MÉDICALES", section_style))
        story.append(Spacer(1, 0.3*cm))
        
        traitements = ordonnance.traitements if hasattr(ordonnance, 'traitements') else []
        
        if traitements:
            # En-tête du tableau
            traitement_data = [[
                Paragraph("<b>Médicament</b>", normal_style),
                Paragraph("<b>Posologie</b>", normal_style),
                Paragraph("<b>Durée</b>", normal_style)
            ]]
            
            # Lignes de traitements
            for i, traitement in enumerate(traitements):
                bg_color = colors.white if i % 2 == 0 else colors.HexColor('#f0fdf4')
                traitement_data.append([
                    Paragraph(f"<b>{traitement.get('medicament', '')}</b>", normal_style),
                    Paragraph(traitement.get('posologie', ''), normal_style),
                    Paragraph(traitement.get('duree', ''), normal_style)
                ])
            
            traitement_table = Table(traitement_data, colWidths=[7*cm, 6*cm, 4*cm])
            traitement_table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                # Corps
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # Bordures
                ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#16a34a')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bbf7d0')),
                # Alternance de couleurs
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
            ]))
            story.append(traitement_table)
        else:
            no_treatment = Paragraph(
                "<i>Aucun traitement prescrit</i>", 
                ParagraphStyle('Italic', parent=normal_style, textColor=colors.HexColor('#64748b'))
            )
            story.append(no_treatment)
        
        story.append(Spacer(1, 0.5*cm))
        
        # ==================== INSTRUCTIONS ====================
        
        instructions = ordonnance.instructions if hasattr(ordonnance, 'instructions') else None
        if instructions:
            story.append(Paragraph("INSTRUCTIONS PARTICULIÈRES", section_style))
            story.append(Spacer(1, 0.3*cm))
            
            instructions_data = [[Paragraph(instructions, normal_style)]]
            instructions_table = Table(instructions_data, colWidths=[17*cm])
            instructions_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffbeb')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#fbbf24')),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(instructions_table)
            story.append(Spacer(1, 0.5*cm))
        
        # ==================== SIGNATURE ====================
        
        story.append(Spacer(1, 1*cm))
        
        numero_ordre = medecin_info.numero_ordre if medecin_info and medecin_info.numero_ordre else "Non renseigné"
        
        # Vérifier si signature numérique existe (en base64 dans MongoDB)
        has_signature = (medecin_info and hasattr(medecin_info, 'signature_data') and 
                        medecin_info.signature_data is not None)
        
        if has_signature:
            try:
                # Décoder la signature depuis base64
                import base64
                from io import BytesIO
                signature_bytes = base64.b64decode(medecin_info.signature_data)
                signature_buffer = BytesIO(signature_bytes)
                
                signature_img = Image(signature_buffer, width=5*cm, height=2.5*cm)
                signature_content = [
                    [Paragraph(f"<b>{medecin_nom}</b><br/>{specialite}<br/>N° Ordre: {numero_ordre}", 
                              ParagraphStyle('SigInfo', parent=normal_style, fontSize=9, alignment=TA_CENTER))],
                    [signature_img],
                    [Paragraph("✓ <i>Signature numérique authentifiée</i>", 
                              ParagraphStyle('SigAuth', parent=normal_style, fontSize=8, 
                                           textColor=colors.HexColor('#16a34a'), alignment=TA_CENTER))]
                ]
            except Exception as e:
                print(f"Erreur chargement signature: {e}")
                signature_content = [
                    [Paragraph(f"<b>{medecin_nom}</b><br/>{specialite}<br/>N° Ordre: {numero_ordre}", 
                              ParagraphStyle('SigInfo', parent=normal_style, fontSize=9, alignment=TA_CENTER))],
                    [Spacer(1, 2*cm)],
                    [Paragraph("<i>Signature et cachet</i>", 
                              ParagraphStyle('SigPlaceholder', parent=normal_style, fontSize=8, 
                                           textColor=colors.HexColor('#64748b'), alignment=TA_CENTER))]
                ]
        else:
            signature_content = [
                [Paragraph(f"<b>{medecin_nom}</b><br/>{specialite}<br/>N° Ordre: {numero_ordre}", 
                          ParagraphStyle('SigInfo', parent=normal_style, fontSize=9, alignment=TA_CENTER))],
                [Spacer(1, 2*cm)],
                [Paragraph("<i>Signature et cachet</i>", 
                          ParagraphStyle('SigPlaceholder', parent=normal_style, fontSize=8, 
                                       textColor=colors.HexColor('#64748b'), alignment=TA_CENTER))]
            ]
        
        signature_table = Table(signature_content, colWidths=[7*cm])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#0284c7')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        # Aligner à droite
        signature_wrapper = Table([[None, signature_table]], colWidths=[10*cm, 7*cm])
        signature_wrapper.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (1, 0), (1, 0), 'TOP'),
        ]))
        story.append(signature_wrapper)
        
        # ==================== PIED DE PAGE ====================
        
        story.append(Spacer(1, 1.2*cm))
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER,
            leading=10
        )
        
        footer_data = [[
            Paragraph("🔒 <b>Document Officiel Authentifié</b>", footer_style),
            Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", footer_style)
        ]]
        
        footer_table = Table(footer_data, colWidths=[8.5*cm, 8.5*cm])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#e2e8f0')),
        ]))
        story.append(footer_table)
        
        # ==================== GÉNÉRATION ====================
        
        doc.build(story, onFirstPage=PDFService._header_footer, onLaterPages=PDFService._header_footer)
        
        # Récupérer les données du buffer et convertir en base64
        pdf_data = buffer.getvalue()
        buffer.close()
        
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        return pdf_base64
