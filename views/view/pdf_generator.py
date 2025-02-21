import sys
import os
import sqlite3
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QMessageBox, QHBoxLayout, QLabel
)
from PyQt5.QtGui import QFont
from fpdf import FPDF
from datetime import datetime


# Couleurs et styles
PRIMARY_COLOR = "#2C3E50"
ACCENT_COLOR = "#1ABC9C"
TEXT_COLOR = "#FFFFFF"

class PDFGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Génération des PDF")
        self.setGeometry(300, 150, 600, 400)
        self.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: {TEXT_COLOR}; font-family: 'Roboto';")

        # Connexion à la base de données
        self.conn = sqlite3.connect("bfem_db.sqlite")
        self.cur = self.conn.cursor()

        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Titre
        self.title = QLabel("Générateur de PDFs - BFEM")
        self.title.setFont(QFont("Roboto", 16, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # Boutons de génération
        self.btn_candidats = QPushButton("Générer Liste des Candidats")
        self.btn_anonymats = QPushButton("Générer Liste des Anonymats")
        self.btn_resultats = QPushButton("Générer Résultats Délibérations")
        self.btn_pv = QPushButton("Générer PV de Délibération")

        for btn in [self.btn_candidats, self.btn_anonymats, self.btn_resultats, self.btn_pv]:
            btn.setFont(QFont("Roboto", 12))
            btn.setStyleSheet(f"background-color: {ACCENT_COLOR}; color: {TEXT_COLOR}; padding: 10px; border-radius: 5px;")
            btn.setCursor(Qt.PointingHandCursor)
            self.layout.addWidget(btn)

        self.btn_candidats.clicked.connect(self.generer_liste_candidats)
        self.btn_anonymats.clicked.connect(self.generer_liste_anonymats)
        self.btn_resultats.clicked.connect(self.generer_resultats_deliberation)
        self.btn_pv.clicked.connect(self.generer_pv_deliberation)
    

    def save_pdf(self, pdf, default_filename):
        """Demande à l'utilisateur où sauvegarder le PDF et le sauvegarde."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Sauvegarder le PDF",
                os.path.join(os.path.expanduser("~"), "Documents", default_filename),
                "PDF files (*.pdf)"
            )
            if filename:
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
                try:
                    pdf.output(filename)
                    QMessageBox.information(self, "Succès", "Document généré avec succès.")
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde : {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur inattendue : {str(e)}")



    def generer_liste_candidats(self):
        """Génère un PDF contenant la liste des candidats."""
        self.cur.execute("""
            SELECT numero_table, prenom, nom, date_naissance, lieu_naissance,
                sexe, type_candidat, etablissement, nationalite,
                choix_epr_facultative, epreuve_facultative, aptitude_sportive
            FROM Candidats
        """)
        candidats = self.cur.fetchall()

        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 14)
                self.cell(0, 10, 'Liste des Candidats', 0, 1, 'C')
                self.ln(10)

        pdf = PDF('L')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Définir les largeurs de colonnes proportionnelles
        w_page = pdf.w - 20  # Largeur totale disponible moins marges
        col_widths = [
            20,  # N° Table
            25,  # Prénom
            25,  # Nom
            22,  # Date Naiss.
            25,  # Lieu Naiss.
            12,  # Sexe
            22,  # Type
            35,  # Établissement
            25,  # Nationalité
            22,  # Choix Fac.
            22,  # Épr. Fac.
            22   # Aptitude
        ]

        # En-têtes avec une police plus petite
        pdf.set_font("Arial", "B", 7)  # Réduit la taille de police pour les en-têtes
        headers = [
            "N° Table",
            "Prénom",
            "Nom",
            "Date Naiss.",
            "Lieu Naiss.",
            "Sexe",
            "Type",
            "Établissement",
            "Nationalité",
            "Choix Fac.",
            "Épr. Fac.",
            "Aptitude"
        ]

        # En-têtes
        for header, width in zip(headers, col_widths):
            pdf.cell(width, 7, header, 1, 0, 'C')
        pdf.ln()

        # Contenu
        pdf.set_font("Arial", "", 8)
        for candidat in candidats:
            if pdf.get_y() + 7 > pdf.page_break_trigger:
                pdf.add_page()
                # Répéter les en-têtes
                pdf.set_font("Arial", "B", 8)
                for header, width in zip(headers, col_widths):
                    pdf.cell(width, 7, header, 1, 0, 'C')
                pdf.ln()
                pdf.set_font("Arial", "", 8)

            for value, width in zip(candidat, col_widths):
                pdf.cell(width, 7, str(value) if value else "", 1, 0, 'C')
            pdf.ln()

        self.save_pdf(pdf, "Liste_Candidats.pdf")
        QMessageBox.information(self, "Succès", "Liste des candidats générée avec succès.")
    def generer_liste_anonymats(self):
        """Génère un PDF contenant la liste des anonymats."""
        self.cur.execute("""
            SELECT C.numero_table, C.nom || ' ' || C.prenom, A.numero_anonymat
            FROM Candidats C
            JOIN Anonymats A ON C.id_candidat = A.id_candidat
        """)
        anonymats = self.cur.fetchall()
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Liste des Anonymats", 0, 1, 'C')
        pdf.ln(5)

        # Largeurs de colonnes optimisées
        w_page = pdf.w - 20
        col_widths = [w_page * 0.25, w_page * 0.5, w_page * 0.25]

        # En-têtes
        pdf.set_font("Arial", "B", 10)
        headers = ["N° Table", "Nom Candidat", "Anonymat"]
        for header, width in zip(headers, col_widths):
            pdf.cell(width, 10, header, 1, 0, 'C')
        pdf.ln()

        # Contenu
        pdf.set_font("Arial", "", 10)
        for anonymat in anonymats:
            if pdf.get_y() + 10 > pdf.page_break_trigger:
                pdf.add_page()
                pdf.set_font("Arial", "B", 10)
                for header, width in zip(headers, col_widths):
                    pdf.cell(width, 10, header, 1, 0, 'C')
                pdf.ln()
                pdf.set_font("Arial", "", 10)

            for value, width in zip(anonymat, col_widths):
                pdf.cell(width, 10, str(value), 1, 0, 'C')
            pdf.ln()

        self.save_pdf(pdf, "Liste_Anonymats.pdf")
        QMessageBox.information(self, "Succès", "Liste des anonymats générée avec succès.")

    def generer_resultats_deliberation(self):
        """Génère un PDF contenant les résultats des délibérations."""
        self.cur.execute("""
            SELECT C.numero_table, C.nom || ' ' || C.prenom, D.points_tour1, D.points_tour2,
                   D.statut, L.moyenne_cycle
            FROM Candidats C
            JOIN Deliberation D ON C.id_candidat = D.id_candidat
            LEFT JOIN Livret_Scolaire L ON C.id_candidat = L.id_candidat
        """)
        resultats = self.cur.fetchall()
        
        pdf = FPDF()
        pdf.add_page('L')  # Format paysage
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Résultats des Délibérations", 0, 1, 'C')
        pdf.ln(5)

        # Largeurs de colonnes optimisées
        w_page = pdf.w - 20
        col_widths = [
            w_page * 0.15,  # N° Table
            w_page * 0.30,  # Nom Candidat
            w_page * 0.15,  # Points Tour 1
            w_page * 0.15,  # Points Tour 2
            w_page * 0.15,  # Moyenne Cycle
            w_page * 0.10   # Statut
        ]

        # En-têtes
        pdf.set_font("Arial", "B", 10)
        headers = ["N° Table", "Nom Candidat", "Points Tour 1", "Points Tour 2", "Moyenne Cycle", "Statut"]
        for header, width in zip(headers, col_widths):
            pdf.cell(width, 10, header, 1, 0, 'C')
        pdf.ln()

        # Contenu
        pdf.set_font("Arial", "", 10)
        for resultat in resultats:
            if pdf.get_y() + 10 > pdf.page_break_trigger:
                pdf.add_page('L')
                pdf.set_font("Arial", "B", 10)
                for header, width in zip(headers, col_widths):
                    pdf.cell(width, 10, header, 1, 0, 'C')
                pdf.ln()
                pdf.set_font("Arial", "", 10)

            pdf.cell(col_widths[0], 10, str(resultat[0]), 1, 0, 'C')
            pdf.cell(col_widths[1], 10, str(resultat[1]), 1, 0, 'C')
            pdf.cell(col_widths[2], 10, str(resultat[2]), 1, 0, 'C')
            pdf.cell(col_widths[3], 10, str(resultat[3] if resultat[3] else ""), 1, 0, 'C')
            pdf.cell(col_widths[4], 10, str(resultat[5] if resultat[5] else ""), 1, 0, 'C')
            pdf.cell(col_widths[5], 10, str(resultat[4]), 1, 0, 'C')
            pdf.ln()

        self.save_pdf(pdf,"Resultats_Deliberations.pdf")
        QMessageBox.information(self, "Succès", "Résultats générés avec succès.")



    def generer_pv_deliberation(self):
        """Génère un PDF contenant le procès-verbal de délibération."""
        # Récupérer les informations du jury depuis la base de données
        self.cur.execute("""
            SELECT region, ief, localite, centre_examen, president_jury
            FROM Parametres_Jury
            WHERE id_utilisateur = (
                SELECT id_utilisateur 
                FROM Utilisateurs 
                WHERE role = 'Jury' 
                LIMIT 1
            )
        """)
        jury_info = self.cur.fetchone()
        
        if not jury_info:
            QMessageBox.warning(self, "Erreur", "Informations du jury non trouvées. Veuillez configurer les paramètres du jury.")
            return
            
        jury_info_text = (
            f"Région: {jury_info[0]}\n"
            f"IEF: {jury_info[1]}\n"
            f"Localité: {jury_info[2]}\n"
            f"Centre d'examen: {jury_info[3]}\n"
            f"Président du Jury: {jury_info[4]}"
        )

        # Récupérer les résultats des candidats
        self.cur.execute("""
            SELECT 
                C.numero_table,
                C.nom || ' ' || C.prenom as nom_complet,
                D.statut,
                CASE 
                    WHEN D.statut = 'Admis' THEN D.points_tour1
                    WHEN D.statut = '2nd Tour' THEN D.points_tour1
                    WHEN D.statut = 'Échec' AND D.points_tour2 IS NOT NULL THEN D.points_tour2
                    ELSE D.points_tour1
                END as points
            FROM Candidats C
            JOIN Deliberation D ON C.id_candidat = D.id_candidat
            ORDER BY C.numero_table
        """)
        resultats = self.cur.fetchall()
        
        if not resultats:
            QMessageBox.warning(self, "Erreur", "Aucun résultat trouvé pour générer le PV.")
            return

        # Création du PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Procès-Verbal de Délibération du BFEM", 0, 1, 'C')
        pdf.ln(5)

        # Informations du jury
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 10, jury_info_text)
        pdf.ln(5)

        # Largeurs de colonnes optimisées
        w_page = pdf.w - 20
        col_widths = [w_page * 0.15, w_page * 0.45, w_page * 0.2, w_page * 0.2]

        # En-têtes
        pdf.set_font("Arial", "B", 10)
        headers = ["N° Table", "Nom et Prénom", "Statut", "Points"]
        for header, width in zip(headers, col_widths):
            pdf.cell(width, 10, header, 1, 0, 'C')
        pdf.ln()

        # Contenu
        pdf.set_font("Arial", "", 10)
        for resultat in resultats:
            if pdf.get_y() + 10 > pdf.page_break_trigger:
                pdf.add_page()
                pdf.set_font("Arial", "B", 10)
                for header, width in zip(headers, col_widths):
                    pdf.cell(width, 10, header, 1, 0, 'C')
                pdf.ln()
                pdf.set_font("Arial", "", 10)

            for value, width in zip(resultat, col_widths):
                pdf.cell(width, 10, str(value), 1, 0, 'C')
            pdf.ln()

        # Statistiques
        pdf.ln(10)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, "Statistiques de la délibération:", 0, 1, 'L')
        pdf.set_font("Arial", "", 10)
        
        # Calcul des statistiques
        total = len(resultats)
        admis = sum(1 for r in resultats if r[2] == 'Admis')
        second_tour = sum(1 for r in resultats if r[2] == '2nd Tour')
        echec = sum(1 for r in resultats if r[2] == 'Échec')
        
        stats_text = (
            f"Total des candidats: {total}\n"
            f"Admis: {admis} ({(admis/total*100):.2f}%)\n"
            f"Admissibles au 2nd tour: {second_tour} ({(second_tour/total*100):.2f}%)\n"
            f"Échec: {echec} ({(echec/total*100):.2f}%)"
        )
        
        pdf.multi_cell(0, 10, stats_text)

        # Date et signature
        pdf.ln(20)
        pdf.cell(0, 10, f"Fait à {jury_info[2]}, le {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
        pdf.ln(10)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 10, "Signature du Président du Jury:", 0, 1, 'L')

        self.save_pdf(pdf, "PV_Deliberation.pdf")
        QMessageBox.information(self, "Succès", "Procès-verbal généré avec succès.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFGenerator()
    window.show()
    sys.exit(app.exec_())