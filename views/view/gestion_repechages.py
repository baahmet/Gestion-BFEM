import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Couleurs inspirées du MainMenu
PRIMARY_COLOR = "#2C3E50"
ACCENT_COLOR = "#1ABC9C"
TEXT_COLOR = "#FFFFFF"
HOVER_COLOR = "#2980B9"

class GestionRepechage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Repêchages")
        self.setGeometry(200, 100, 1200, 600)
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
        self.title = QLabel("Gestion des Repêchages")
        self.title.setFont(QFont("Roboto", 20, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # Tableau des candidats repêchables
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Numéro Table", "Nom Candidat", "Total Points", "Moyenne Cycle", "Statut", "Décision Jury"])
        self.table.setStyleSheet("background-color: white; color: black; border-radius: 5px;")
        self.layout.addWidget(self.table)

        # Bouton finaliser le repêchage
        self.btn_finaliser = QPushButton("Finaliser les Repêchages")
        self.btn_finaliser.setFont(QFont("Roboto", 12))
        self.btn_finaliser.setStyleSheet(f"background-color: {ACCENT_COLOR}; color: {TEXT_COLOR}; padding: 10px; border-radius: 5px;")
        self.btn_finaliser.setCursor(Qt.PointingHandCursor)
        self.btn_finaliser.clicked.connect(self.finaliser_repechage)
        self.layout.addWidget(self.btn_finaliser, alignment=Qt.AlignCenter)

        # Charger les candidats repêchables
        self.charger_candidats_repechables()

    def charger_candidats_repechables(self):
        """Charge les candidats repêchables dans le tableau."""
        self.table.setRowCount(0)
        self.cur.execute("""
            SELECT C.numero_table, C.nom || ' ' || C.prenom, D.points_tour1, L.moyenne_cycle, D.statut, C.id_candidat
            FROM Deliberation D
            JOIN Candidats C ON D.id_candidat = C.id_candidat
            LEFT JOIN Livret_Scolaire L ON D.id_candidat = L.id_candidat
            WHERE D.statut = 'Repêchage'
        """)
        candidats = self.cur.fetchall()

        print("Candidats en repêchage récupérés :", candidats)  # Log pour vérifier les données

        for row, candidat in enumerate(candidats):
            self.table.insertRow(row)
            for col, value in enumerate(candidat[:-1]):  # Exclure l'id_candidat de l'affichage
                item = QTableWidgetItem(str(value) if value is not None else "N/A")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

            # Créer un widget pour contenir les boutons "Valider" et "Rejeter"
            widget = QWidget()
            layout = QHBoxLayout()
            widget.setLayout(layout)

            # Bouton Valider
            btn_valider = QPushButton("Valider")
            btn_valider.setStyleSheet(f"background-color: {HOVER_COLOR}; color: {TEXT_COLOR}; border-radius: 5px;")
            btn_valider.clicked.connect(lambda _, r=row, id=candidat[-1]: self.valider_repechage(r, id))
            layout.addWidget(btn_valider)

            # Bouton Rejeter
            btn_rejeter = QPushButton("Rejeter")
            btn_rejeter.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 5px;")
            btn_rejeter.clicked.connect(lambda _, r=row, id=candidat[-1]: self.rejeter_repechage(r, id))
            layout.addWidget(btn_rejeter)

            # Ajouter le widget contenant les boutons dans la cellule du tableau
            self.table.setCellWidget(row, 5, widget)

    def valider_repechage(self, row, id_candidat):
        """Valide le repêchage d'un candidat spécifique."""
        confirm = QMessageBox.question(
            self, "Confirmation", "Voulez-vous vraiment valider ce repêchage ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                # Mettre à jour le statut dans la base de données
                self.cur.execute("""
                    UPDATE Deliberation
                    SET statut = 'Admis'
                    WHERE id_candidat = ?
                """, (id_candidat,))
                self.conn.commit()

                # Mettre à jour l'interface
                self.table.item(row, 4).setText('Admis')  # Mettre à jour la colonne "Statut"
                QMessageBox.information(self, "Succès", "Le repêchage a été validé.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la validation : {e}")

    def rejeter_repechage(self, row, id_candidat):
        """Rejette le repêchage d'un candidat spécifique."""
        confirm = QMessageBox.question(
            self, "Confirmation", "Voulez-vous vraiment rejeter ce repêchage ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                # Mettre à jour le statut dans la base de données
                self.cur.execute("""
                    UPDATE Deliberation
                    SET statut = 'Échec'
                    WHERE id_candidat = ?
                """, (id_candidat,))
                self.conn.commit()

                # Mettre à jour l'interface
                self.table.item(row, 4).setText('Échec')  # Mettre à jour la colonne "Statut"
                QMessageBox.information(self, "Succès", "Le repêchage a été rejeté.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du rejet : {e}")

    def finaliser_repechage(self):
        """Finalise le processus de repêchage et verrouille les décisions."""
        try:
            # Vérifier s'il y a des candidats en repêchage non traités
            self.cur.execute("""
                SELECT COUNT(*)
                FROM Deliberation
                WHERE statut = 'Repêchage'
            """)
            nb_repechage = self.cur.fetchone()[0]

            if nb_repechage > 0:
                QMessageBox.warning(self, "Avertissement", f"Il reste {nb_repechage} candidat(s) en repêchage non traités.")
            else:
                QMessageBox.information(self, "Repêchage Finalisé", "Tous les candidats ont été traités avec succès.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la finalisation du repêchage : {e}")

    def closeEvent(self, event):
        """Ferme la connexion à la base de données lors de la fermeture de l'application."""
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error:
                pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GestionRepechage()
    window.show()
    sys.exit(app.exec_())
