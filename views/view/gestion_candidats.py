import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QDialog,
    QLabel, QLineEdit, QDateEdit, QComboBox, QFormLayout, QSpinBox,
    QFrame
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from views.view.gestion_livet_dialog import GestionLivretDialog

# Constantes de couleurs (reprises du menu principal)
PRIMARY_COLOR = "#2C3E50"
SECONDARY_COLOR = "#34495E"
ACCENT_COLOR = "#1ABC9C"
BACKGROUND_COLOR = "#F5F6FA"
TEXT_COLOR = "#FFFFFF"
HOVER_COLOR = "#2980B9"
DISABLED_COLOR = "#7F8C8D"

# Style global de l'application
APP_STYLE = f"""
    QMainWindow {{
        background-color: {BACKGROUND_COLOR};
        font-family: 'Roboto', sans-serif;
    }}
    QFrame {{
        background-color: {BACKGROUND_COLOR};
    }}
    QTableWidget {{
        background-color: white;
        border: 1px solid {SECONDARY_COLOR};
        border-radius: 8px;
        gridline-color: {SECONDARY_COLOR};
    }}
    QHeaderView::section {{
        background-color: {PRIMARY_COLOR};
        color: {TEXT_COLOR};
        padding: 8px;
        border: none;
        font-family: 'Roboto';
        font-size: 14px;
    }}
    QTableWidget::item {{
        padding: 8px;
        font-family: 'Roboto';
    }}
    QTableWidget::item:selected {{
        background-color: {ACCENT_COLOR};
        color: {TEXT_COLOR};
    }}
    QPushButton {{
        background-color: {ACCENT_COLOR};
        color: {TEXT_COLOR};
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        font-family: 'Roboto';
        font-size: 14px;
        min-width: 120px;
    }}
    QPushButton:hover {{
        background-color: {HOVER_COLOR};
    }}
    QPushButton:pressed {{
        background-color: {SECONDARY_COLOR};
    }}
    QLineEdit, QDateEdit, QComboBox, QSpinBox {{
        background-color: white;
        border: 1px solid {SECONDARY_COLOR};
        border-radius: 4px;
        padding: 8px;
        font-family: 'Roboto';
        font-size: 14px;
    }}
    QLabel {{
        color: {PRIMARY_COLOR};
        font-family: 'Roboto';
        font-size: 14px;
    }}
"""

COLUMNS = [
    "ID", "Numéro Table", "Prénom", "Nom", "Date Naissance", "Lieu Naissance",
    "Sexe", "Type Candidat", "Établissement", "Nationalité", "Choix Épreuve Facultative",
    "Épreuve Facultative", "Aptitude Sportive"
]

class GestionCandidats(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Candidats")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(APP_STYLE)

        # Connexion à la base de données
        self.conn = sqlite3.connect("bfem_db.sqlite")
        self.cur = self.conn.cursor()

        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal avec marges
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        self.central_widget.setLayout(self.layout)

        # En-tête avec QFrame
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_COLOR}, stop:1 {HOVER_COLOR});
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }}
        """)
        header_layout = QHBoxLayout(self.header_frame)
        
        title = QLabel("Gestion des Candidats")
        title.setFont(QFont("Roboto", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        self.layout.addWidget(self.header_frame)

        # Tableau des candidats
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.layout.addWidget(self.table)

        # Conteneur pour les boutons
        self.button_frame = QFrame()
        self.button_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {PRIMARY_COLOR};
                border-radius: 8px;
                padding: 15px;
                margin-top: 20px;
            }}
        """)
        self.btn_layout = QHBoxLayout(self.button_frame)
        self.btn_layout.setSpacing(15)

        # Création des boutons
        self.btn_ajouter = QPushButton("Ajouter un Candidat")
        self.btn_modifier = QPushButton("Modifier un Candidat")
        self.btn_supprimer = QPushButton("Supprimer un Candidat")
        self.btn_livret = QPushButton("Gérer le Livret Scolaire")

        for btn in [self.btn_ajouter, self.btn_modifier, self.btn_supprimer, self.btn_livret]:
            self.btn_layout.addWidget(btn)

        self.layout.addWidget(self.button_frame)

        # Connexion des boutons
        self.btn_ajouter.clicked.connect(self.ajouter_candidat)
        self.btn_modifier.clicked.connect(self.modifier_candidat)
        self.btn_supprimer.clicked.connect(self.supprimer_candidat)
        self.btn_livret.clicked.connect(self.gerer_livret)

        # Charger les candidats
        self.charger_candidats()

    def charger_candidats(self):
        """Charge les candidats depuis la base de données"""
        self.table.setRowCount(0)
        try:
            self.cur.execute("SELECT * FROM Candidats")
            for row_idx, row_data in enumerate(self.cur.fetchall()):
                self.table.insertRow(row_idx)
                for col_idx, cell_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des candidats : {e}")

    def ajouter_candidat(self):
        dialog = AjouterCandidatDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.charger_candidats()

    def modifier_candidat(self):
        if self.table.currentRow() == -1:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un candidat à modifier.")
            return
        id_candidat = self.table.item(self.table.currentRow(), 0).text()
        dialog = ModifierCandidatDialog(self, id_candidat)
        if dialog.exec_() == QDialog.Accepted:
            self.charger_candidats()

    def supprimer_candidat(self):
        if self.table.currentRow() == -1:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un candidat à supprimer.")
            return
        if QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment supprimer ce candidat ?") == QMessageBox.Yes:
            try:
                id_candidat = self.table.item(self.table.currentRow(), 0).text()
                self.cur.execute("DELETE FROM Candidats WHERE id_candidat = ?", (id_candidat,))
                self.conn.commit()
                self.charger_candidats()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")

    def gerer_livret(self):
        if self.table.currentRow() == -1:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un candidat.")
            return
        id_candidat = self.table.item(self.table.currentRow(), 0).text()
        dialog = GestionLivretDialog(self, id_candidat)
        dialog.exec_()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

class BaseCandidatDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setStyleSheet(APP_STYLE)


 
class AjouterCandidatDialog(QDialog):
    """Fenêtre de dialogue pour ajouter un nouveau candidat."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un Candidat")
        self.setModal(True)
        self.setStyleSheet(APP_STYLE)  # Appliquer le style CSS

        # Connexion à la base de données
        self.conn = sqlite3.connect("bfem_db.sqlite")
        self.cur = self.conn.cursor()

        # Layout principal
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        # Champs de saisie
        self.numero_table = QSpinBox()
        self.numero_table.setMinimum(1)
        self.prenom = QLineEdit()
        self.nom = QLineEdit()
        self.date_naissance = QDateEdit()
        self.date_naissance.setDate(QDate.currentDate())
        self.lieu_naissance = QLineEdit()
        self.sexe = QComboBox()
        self.sexe.addItems(["M", "F"])
        self.type_candidat = QComboBox()
        self.type_candidat.addItems(["Individuel", "Officiel"])
        self.etablissement = QLineEdit()
        self.nationalite = QLineEdit()
        self.choix_epr_facultative = QComboBox()
        self.choix_epr_facultative.addItems(["Oui", "Non"])
        self.epreuve_facultative = QComboBox()
        self.epreuve_facultative.addItems(["Neutre", "COUTURE", "DESSIN", "MUSIQUE"])
        self.aptitude_sportive = QComboBox()
        self.aptitude_sportive.addItems(["Apte", "Inapte"])

        # Ajouter les champs au layout
        self.layout.addRow("Numéro Table:", self.numero_table)
        self.layout.addRow("Prénom:", self.prenom)
        self.layout.addRow("Nom:", self.nom)
        self.layout.addRow("Date de Naissance:", self.date_naissance)
        self.layout.addRow("Lieu de Naissance:", self.lieu_naissance)
        self.layout.addRow("Sexe:", self.sexe)
        self.layout.addRow("Type Candidat:", self.type_candidat)
        self.layout.addRow("Établissement:", self.etablissement)
        self.layout.addRow("Nationalité:", self.nationalite)
        self.layout.addRow("Choix Épreuve Facultative:", self.choix_epr_facultative)
        self.layout.addRow("Épreuve Facultative:", self.epreuve_facultative)
        self.layout.addRow("Aptitude Sportive:", self.aptitude_sportive)

        # Boutons
        self.btn_ajouter = QPushButton("Ajouter")
        self.btn_annuler = QPushButton("Annuler")
        self.btn_ajouter.clicked.connect(self.ajouter)
        self.btn_annuler.clicked.connect(self.reject)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.btn_ajouter)
        self.btn_layout.addWidget(self.btn_annuler)
        self.layout.addRow(self.btn_layout)

    def ajouter(self):
        """Ajoute le candidat à la base de données avec vérification du numéro de table unique."""
        numero_table = self.numero_table.value()
        prenom = self.prenom.text().strip()
        nom = self.nom.text().strip()
        date_naissance = self.date_naissance.date().toString("yyyy-MM-dd")
        lieu_naissance = self.lieu_naissance.text().strip()
        sexe = self.sexe.currentText()
        type_candidat = self.type_candidat.currentText()
        etablissement = self.etablissement.text().strip()
        nationalite = self.nationalite.text().strip()
        choix_epr_facultative = self.choix_epr_facultative.currentText() == "Oui"
        epreuve_facultative = self.epreuve_facultative.currentText()
        aptitude_sportive = self.aptitude_sportive.currentText()

        # Vérifier si le numéro de table existe déjà
        self.cur.execute("SELECT COUNT(*) FROM Candidats WHERE numero_table = ?", (numero_table,))
        if self.cur.fetchone()[0] > 0:
            QMessageBox.warning(self, "Erreur", "Le numéro de table existe déjà. Veuillez en choisir un autre.")
            return

        # Insertion dans la base de données
        try:
            self.cur.execute(
                "INSERT INTO Candidats (numero_table, prenom, nom, date_naissance, lieu_naissance, "
                "sexe, type_candidat, etablissement, nationalite, choix_epr_facultative, epreuve_facultative, aptitude_sportive) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (numero_table, prenom, nom, date_naissance, lieu_naissance, sexe, type_candidat,
                 etablissement, nationalite, choix_epr_facultative, epreuve_facultative, aptitude_sportive)
            )
            self.conn.commit()
            QMessageBox.information(self, "Succès", "Candidat ajouté avec succès")
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Erreur", "Le numéro de table doit être unique.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur de base de données", f"Erreur lors de l'ajout : {e}")

class ModifierCandidatDialog(AjouterCandidatDialog):
    """Fenêtre de dialogue pour modifier un candidat existant."""

    def __init__(self, parent=None, id_candidat=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier un Candidat")
        self.id_candidat = id_candidat

        # Charger les informations du candidat
        self.parent().cur.execute("SELECT * FROM Candidats WHERE id_candidat = ?", (self.id_candidat,))
        candidat = self.parent().cur.fetchone()

        # Pré-remplir les champs
        self.numero_table.setValue(candidat[1])
        self.prenom.setText(candidat[2])
        self.nom.setText(candidat[3])
        self.date_naissance.setDate(QDate.fromString(candidat[4], "yyyy-MM-dd"))
        self.lieu_naissance.setText(candidat[5])
        self.sexe.setCurrentText(candidat[6])
        self.type_candidat.setCurrentText(candidat[7])
        self.etablissement.setText(candidat[8])
        self.nationalite.setText(candidat[9])
        self.choix_epr_facultative.setCurrentText("Oui" if candidat[10] else "Non")
        self.epreuve_facultative.setCurrentText(candidat[11] if candidat[11] else "")
        self.aptitude_sportive.setCurrentText(candidat[12] if candidat[12] else "")

    def ajouter(self):
        """Modifie le candidat dans la base de données."""
        try:
            numero_table = self.numero_table.value()
            prenom = self.prenom.text().strip()
            nom = self.nom.text().strip()
            date_naissance = self.date_naissance.date().toString("yyyy-MM-dd")
            lieu_naissance = self.lieu_naissance.text().strip()
            sexe = self.sexe.currentText()
            type_candidat = self.type_candidat.currentText()
            etablissement = self.etablissement.text().strip()
            nationalite = self.nationalite.text().strip()
            choix_epr_facultative = self.choix_epr_facultative.currentText() == "Oui"
            epreuve_facultative = self.epreuve_facultative.currentText()
            aptitude_sportive = self.aptitude_sportive.currentText()

            if not prenom or not nom:
                QMessageBox.warning(self, "Champs manquants", "Veuillez remplir tous les champs obligatoires.")
                return

            # Mise à jour dans la base de données
            self.parent().cur.execute(
                "UPDATE Candidats SET numero_table = ?, prenom = ?, nom = ?, date_naissance = ?, "
                "lieu_naissance = ?, sexe = ?, type_candidat = ?, etablissement = ?, nationalite = ?, "
                "choix_epr_facultative = ?, epreuve_facultative = ?, aptitude_sportive = ? WHERE id_candidat = ?",
                (numero_table, prenom, nom, date_naissance, lieu_naissance, sexe, type_candidat,
                 etablissement, nationalite, choix_epr_facultative, epreuve_facultative, aptitude_sportive, self.id_candidat)
            )
            self.parent().conn.commit()
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Erreur", "Le numéro de table doit être unique.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur de base de données", f"Erreur lors de la modification : {e}")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GestionCandidats()
    window.show()
    sys.exit(app.exec_())