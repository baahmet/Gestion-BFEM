import sqlite3
import random
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QHeaderView
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Styles inspirés du MainMenu
PRIMARY_COLOR = "#2C3E50"
SECONDARY_COLOR = "#34495E"
ACCENT_COLOR = "#1ABC9C"
TEXT_COLOR = "#FFFFFF"
HOVER_COLOR = "#2980B9"

class GestionAnonymats(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Anonymats")
        self.setGeometry(300, 150, 800, 600)
        self.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: {TEXT_COLOR}; font-family: 'Roboto';")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Titre
        self.title = QLabel("Gestion des Anonymats")
        self.title.setFont(QFont("Roboto", 20, QFont.Bold))
        self.title.setStyleSheet(f"color: {TEXT_COLOR}; padding: 10px; text-align: center;")
        self.layout.addWidget(self.title, alignment=Qt.AlignCenter)

        # Bouton de génération des anonymats
        self.btn_generer = QPushButton("🔄 Générer les anonymats")
        self.btn_generer.setFont(QFont("Roboto", 12))
        self.btn_generer.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: {TEXT_COLOR};
                padding: 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{ background-color: {HOVER_COLOR}; }}
        """)
        self.btn_generer.clicked.connect(self.generer_anonymats)
        self.layout.addWidget(self.btn_generer, alignment=Qt.AlignCenter)

        # Tableau pour afficher les anonymats
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Numéro Table", "Nom Candidat", "Numéro Anonymat"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: white; border-radius: 5px; color: black;")
        self.layout.addWidget(self.table)

        # Charger les anonymats existants
        self.charger_anonymats()

    def charger_anonymats(self):
        """Charge les anonymats existants dans le tableau."""
        self.table.setRowCount(0)
        try:
            conn = sqlite3.connect("bfem_db.sqlite")
            cur = conn.cursor()
            cur.execute("""
                SELECT Candidats.numero_table, Candidats.nom || ' ' || Candidats.prenom, Anonymats.numero_anonymat
                FROM Anonymats
                JOIN Candidats ON Anonymats.id_candidat = Candidats.id_candidat
                ORDER BY Candidats.numero_table
            """)
            anonymats = cur.fetchall()
            conn.close()

            for row, anonymat in enumerate(anonymats):
                self.table.insertRow(row)
                for col, value in enumerate(anonymat):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des anonymats : {e}")

    def generer_anonymats(self):
        """Génère les anonymats pour les candidats sans anonymat."""
        try:
            conn = sqlite3.connect("bfem_db.sqlite")
            cur = conn.cursor()

            # Récupérer les candidats sans anonymat
            cur.execute("""
                SELECT id_candidat FROM Candidats
                WHERE id_candidat NOT IN (SELECT id_candidat FROM Anonymats)
            """)
            candidats = cur.fetchall()

            if not candidats:
                QMessageBox.information(self, "Info", "Tous les candidats ont déjà un anonymat.")
                conn.close()
                return

            # Récupérer les numéros d'anonymat déjà utilisés
            cur.execute("SELECT numero_anonymat FROM Anonymats")
            numeros_utilises = {row[0] for row in cur.fetchall()}

            # Générer des numéros d'anonymat uniques
            nb_candidats = len(candidats)
            numeros_disponibles = set(range(1, nb_candidats + 100))  # Marge de sécurité
            numeros_disponibles -= numeros_utilises
            numeros_anonymat = random.sample(sorted(numeros_disponibles), nb_candidats)

            # Insérer les nouveaux anonymats
            for i, (id_candidat,) in enumerate(candidats):
                cur.execute("""
                    INSERT INTO Anonymats (id_candidat, numero_anonymat, tour)
                    VALUES (?, ?, 1)
                """, (id_candidat, numeros_anonymat[i]))

            conn.commit()
            conn.close()
            QMessageBox.information(self, "Succès", "Anonymats générés avec succès.")
            self.charger_anonymats()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération des anonymats : {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GestionAnonymats()
    window.show()
    sys.exit(app.exec_())
