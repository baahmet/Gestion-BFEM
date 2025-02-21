from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

def generer_guide_utilisateur():
    """Génère le guide utilisateur au format PDF"""
    doc = SimpleDocTemplate(
        "Guide_Utilisateur.pdf",
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=20,
        spaceAfter=10
    )
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=8
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceBefore=6,
        spaceAfter=6
    )

    # Contenu
    content = []
    
    # Titre principal
    content.append(Paragraph("Guide Utilisateur - Gestion des Délibérations du BFEM", title_style))
    content.append(Spacer(1, 20))

    # Sommaire
    content.append(Paragraph("📌 Sommaire", heading_style))
    sommaire = [
        "1. Introduction",
        "2. Installation et Configuration",
        "3. Utilisation du Logiciel",
        "4. Gestion des Erreurs et FAQ",
        "5. Mise à Jour"
    ]
    for item in sommaire:
        content.append(Paragraph(f"• {item}", normal_style))
    content.append(Spacer(1, 20))

    # 1. Introduction
    content.append(Paragraph("1. Introduction", heading_style))
    content.append(Paragraph("📄 Présentation du projet", subheading_style))
    content.append(Paragraph(
        "L'application Gestion des Délibérations du BFEM est un outil permettant de simplifier et "
        "automatiser le processus de délibération des candidats au BFEM. Elle offre une interface "
        "intuitive pour saisir, traiter et analyser les notes des candidats en appliquant les règles métiers "
        "spécifiques.", normal_style))

    content.append(Paragraph("✅ Fonctionnalités principales", subheading_style))
    fonctionnalites = [
        "🔹 Gestion des candidats (ajout, modification, suppression)",
        "🔹 Saisie et anonymisation des notes",
        "🔹 Application des règles métiers pour la délibération",
        "🔹 Attribution automatique du statut des candidats (admis, repêché, échec)",
        "🔹 Exportation des délibérations sous forme de PV en PDF",
        "🔹 Interface intuitive et filtrage des données"
    ]
    for fonc in fonctionnalites:
        content.append(Paragraph(fonc, normal_style))

    # 2. Installation et Configuration
    content.append(Paragraph("2. Installation et Configuration", heading_style))
    content.append(Paragraph("💻 Prérequis", subheading_style))
    content.append(Paragraph(
        "Avant d'installer l'application, assurez-vous que les éléments suivants sont disponibles sur "
        "votre système :", normal_style))
    prereqs = [
        "• Python (version 3.8 ou supérieure)",
        "• SQLite3 (pour la base de données)",
        "• Bibliothèques Python nécessaires : PyQt5, ReportLab, pandas"
    ]
    for prereq in prereqs:
        content.append(Paragraph(prereq, normal_style))

    # 3. Utilisation du logiciel
    content.append(Paragraph("3. Utilisation du logiciel", heading_style))
    content.append(Paragraph("🔍 Interface principale", subheading_style))
    sections = [
        "• Gestion des Candidats : Ajouter, modifier ou supprimer un candidat",
        "• Gestion des Notes : Saisir et modifier les notes du premier et du second tour",
        "• Délibérations : Appliquer les règles de calcul des points et statuts des candidats",
        "• Gestion des Repêchages : Examiner les candidats repêchables et valider leur statut",
        "• Génération PDF : Générer et exporter différentes listes et documents"
    ]
    for section in sections:
        content.append(Paragraph(section, normal_style))

    # 4. Gestion des erreurs et FAQ
    content.append(Paragraph("4. Gestion des erreurs et FAQ", heading_style))
    content.append(Paragraph("⚠️ Problèmes courants", subheading_style))
    
    # Tableau des problèmes courants
    problemes = [
        ["Problème", "Solution"],
        ["L'application ne se lance pas", "Vérifier que Python et les bibliothèques sont installés"],
        ["Base de données introuvable", "Vérifier que le fichier SQLite est bien présent"],
        ["Erreur lors de la génération PDF", "Vérifier que ReportLab est bien installé"]
    ]
    table = Table(problemes, colWidths=[200, 250])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    content.append(table)

    # 5. Mise à jour
    content.append(Paragraph("5. Mise à jour", heading_style))
    content.append(Paragraph("🔄 Mettre à jour le projet", subheading_style))
    content.append(Paragraph(
        "Pour obtenir les dernières améliorations et corrections de bugs, suivez ces étapes :", 
        normal_style))
    steps = [
        "1. git pull origin main",
        "2. pip install -r requirements.txt",
        "3. python main.py"
    ]
    for step in steps:
        content.append(Paragraph(step, normal_style))

    # Conclusion
    content.append(Spacer(1, 20))
    content.append(Paragraph(
        "Félicitations ! Vous êtes prêt à utiliser l'application de gestion des délibérations du BFEM !",
        normal_style
    ))

    # Génération du PDF
    doc.build(content)

if __name__ == '__main__':
    generer_guide_utilisateur()