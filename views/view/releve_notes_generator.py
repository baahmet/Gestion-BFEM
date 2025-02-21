import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QComboBox, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from fpdf import FPDF

# Couleurs inspirées du MainMenu
PRIMARY_COLOR = "#2C3E50"
ACCENT_COLOR = "#1ABC9C"
TEXT_COLOR = "#FFFFFF"
HOVER_COLOR = "#2980B9"

class ReleveNotesGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Générateur de Relevés de Notes")
        self.setGeometry(300, 150, 1200, 600)
        self.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: {TEXT_COLOR}; font-family: 'Roboto';")

        # Connexion à la base de données
        self.conn = sqlite3.connect("bfem_db.sqlite")
        self.cur = self.conn.cursor()

        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Titre
        self.title = QLabel("Générateur de Relevés de Notes")
        self.title.setFont(QFont("Roboto", 20, QFont.Bold))
        self.title.setStyleSheet(f"color: {TEXT_COLOR}; padding: 10px; text-align: center;")
        self.layout.addWidget(self.title, alignment=Qt.AlignCenter)

        # Sélection du tour
        self.tour_combo = QComboBox()
        self.tour_combo.addItems(["Premier Tour", "Second Tour"])
        self.tour_combo.setFont(QFont("Roboto", 12))
        self.tour_combo.setStyleSheet(f"background-color: {ACCENT_COLOR}; color: {TEXT_COLOR}; padding: 10px; border-radius: 5px;")
        self.tour_combo.currentIndexChanged.connect(self.charger_candidats)
        self.layout.addWidget(self.tour_combo)

        # Tableau des candidats
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Numéro Table", "Nom Candidat", "Anonymat"])
        self.table.setStyleSheet("background-color: white; color: black; border-radius: 5px;")
        self.layout.addWidget(self.table)

        # Bouton pour générer le relevé de notes
        self.btn_generer = QPushButton("Générer le Relevé de Notes")
        self.btn_generer.setFont(QFont("Roboto", 12))
        self.btn_generer.setStyleSheet(f"background-color: {ACCENT_COLOR}; color: {TEXT_COLOR}; padding: 10px; border-radius: 5px;")
        self.btn_generer.setCursor(Qt.PointingHandCursor)
        self.btn_generer.clicked.connect(self.generer_releve_notes)
        self.layout.addWidget(self.btn_generer, alignment=Qt.AlignCenter)

        # Charger la liste des candidats
        self.charger_candidats()

    def charger_candidats(self):
        """Charge les candidats et leurs anonymats en fonction du tour sélectionné."""
        self.table.setRowCount(0)
        tour_selected = self.tour_combo.currentText() == "Premier Tour"
        table = "Notes_Tour1" if tour_selected else "Notes_Tour2"

        self.cur.execute(f"""
            SELECT C.numero_table, C.nom || ' ' || C.prenom, A.numero_anonymat
            FROM Candidats C
            JOIN Anonymats A ON C.id_candidat = A.id_candidat
            WHERE EXISTS (
                SELECT 1 FROM {table} WHERE anonymat = A.numero_anonymat
            )
        """)
        candidats = self.cur.fetchall()
        for row, candidat in enumerate(candidats):
            self.table.insertRow(row)
            for col, value in enumerate(candidat):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def generer_releve_notes(self):
        """Génère le relevé de notes en PDF pour le candidat sélectionné."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un candidat.")
            return

        # Récupérer les informations du candidat
        numero_table = self.table.item(selected_row, 0).text()
        nom_candidat = self.table.item(selected_row, 1).text()
        anonymat = self.table.item(selected_row, 2).text()

        # Récupérer les notes en fonction du tour sélectionné
        tour_selected = self.tour_combo.currentText() == "Premier Tour"
        table = "Notes_Tour1" if tour_selected else "Notes_Tour2"

        self.cur.execute(f"""
            SELECT * FROM {table} WHERE anonymat = ?
        """, (anonymat,))
        notes = self.cur.fetchone()

        if not notes:
            QMessageBox.warning(self, "Erreur", "Aucune note trouvée pour ce candidat.")
            return

        # Créer le PDF
        pdf = FPDF()
        pdf.add_page()

        # Ajouter un logo (si disponible)
        try:
            pdf.image("logo.png", x=10, y=8, w=30)  # Remplacez "logo.png" par le chemin de votre logo
        except:
            pass

        # Titre du relevé de notes
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Relevé de Notes - {nom_candidat}", 0, 1, "C")
        pdf.ln(10)

        # Informations du candidat
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Numéro de Table: {numero_table}", 0, 1)
        pdf.cell(0, 10, f"Anonymat: {anonymat}", 0, 1)
        pdf.ln(10)

        # Tableau des notes
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Notes:", 0, 1)
        pdf.ln(5)

        # En-têtes du tableau
        pdf.set_font("Arial", "B", 10)
        headers = ["Matière", "Note"]
        col_widths = [100, 50]
        for header, width in zip(headers, col_widths):
            pdf.cell(width, 10, header, 1, 0, "C")
        pdf.ln()

        # Contenu du tableau
        pdf.set_font("Arial", "", 10)
        for matiere, note in zip(self.cur.description, notes):
            if matiere[0] not in ["anonymat", "id_candidat"]:  # Ignorer les colonnes non pertinentes
                pdf.cell(col_widths[0], 10, matiere[0].replace("_", " ").capitalize(), 1, 0, "L")
                pdf.cell(col_widths[1], 10, str(note), 1, 0, "C")
                pdf.ln()

        # Sauvegarder le PDF
        filename = f"Relevé_Notes_{nom_candidat}_{'1er_Tour' if tour_selected else '2nd_Tour'}.pdf"
        pdf.output(filename)
        QMessageBox.information(self, "Succès", f"Relevé de notes généré avec succès : {filename}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReleveNotesGenerator()
    window.show()
    sys.exit(app.exec_())