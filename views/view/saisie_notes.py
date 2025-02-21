import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QDialog,
    QLabel, QLineEdit, QFormLayout, QComboBox, QSpinBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Couleurs inspirées du MainMenu
PRIMARY_COLOR = "#2C3E50"
ACCENT_COLOR = "#1ABC9C"
TEXT_COLOR = "#FFFFFF"
HOVER_COLOR = "#2980B9"

class SaisieNotes(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Saisie des Notes")
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
        self.title = QLabel("Saisie et Modification des Notes")
        self.title.setFont(QFont("Roboto", 20, QFont.Bold))
        self.title.setStyleSheet(f"color: {TEXT_COLOR}; padding: 10px; text-align: center;")
        self.layout.addWidget(self.title, alignment=Qt.AlignCenter)

        # Tableau des candidats et leurs notes
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Numéro Table", "Nom Candidat", "Anonymat", "1er Tour", "2nd Tour", "EPS & Fac", "Actions"])
        self.table.setStyleSheet("background-color: white; color: black; border-radius: 5px;")
        self.layout.addWidget(self.table)

        # Bouton de saisie des notes
        self.btn_saisir = QPushButton("Saisir les Notes")
        self.btn_saisir.setFont(QFont("Roboto", 12))
        self.btn_saisir.setStyleSheet(f"background-color: {ACCENT_COLOR}; color: {TEXT_COLOR}; padding: 10px; border-radius: 5px;")
        self.btn_saisir.setCursor(Qt.PointingHandCursor)
        self.btn_saisir.clicked.connect(self.ouvrir_saisie_notes)
        self.layout.addWidget(self.btn_saisir, alignment=Qt.AlignCenter)

        # Charger la liste des candidats
        self.charger_candidats()

    def charger_candidats(self):
        """Charge les candidats et leurs notes depuis la base de données."""
        self.table.setRowCount(0)
        self.cur.execute("""
            SELECT C.numero_table, C.nom || ' ' || C.prenom, A.numero_anonymat,
                   COALESCE(N1.notes_tour1, 'Non Saisi'),
                   COALESCE(N2.notes_tour2, 'Non Saisi'),
                   COALESCE(N1.eps || ' / ' || N1.epreuve_facultative, 'Non Saisi')
            FROM Candidats C
            LEFT JOIN Anonymats A ON C.id_candidat = A.id_candidat
            LEFT JOIN (
                SELECT anonymat,
                    compo_francais || ',' || dictee || ',' || etude_de_texte || ',' ||
                    instruction_civique || ',' || histoire_geographie || ',' ||
                    mathematiques || ',' || pc_lv2 || ',' || svt || ',' ||
                    anglais_ecrit || ',' || anglais_oral AS notes_tour1,
                    eps, epreuve_facultative
                FROM Notes_Tour1
            ) N1 ON A.numero_anonymat = N1.anonymat
            LEFT JOIN (
                SELECT anonymat,
                    francais_2nd_tour || ',' || mathematiques_2nd_tour || ',' || pc_lv2_2nd_tour AS notes_tour2
                FROM Notes_Tour2
            ) N2 ON A.numero_anonymat = N2.anonymat
        """)
        candidats = self.cur.fetchall()
        for row, candidat in enumerate(candidats):
            self.table.insertRow(row)
            for col, value in enumerate(candidat):
                formatted_value = str(value).replace(',', ' | ') if isinstance(value, str) else str(value)
                item = QTableWidgetItem(formatted_value)
                item.setTextAlignment(Qt.AlignCenter)  # Centrer le texte
                self.table.setItem(row, col, item)

            # Bouton Modifier
            btn_modifier = QPushButton("Modifier")
            btn_modifier.setStyleSheet(f"background-color: {HOVER_COLOR}; color: {TEXT_COLOR}; border-radius: 5px;")
            btn_modifier.clicked.connect(lambda _, r=row: self.ouvrir_modification_notes(r))
            self.table.setCellWidget(row, 6, btn_modifier)

    def ouvrir_saisie_notes(self):
        """Ouvre la boîte de dialogue pour saisir les notes."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un candidat.")
            return
        anonymat = self.table.item(selected_row, 2).text()
        dialog = SaisieNotesDialog(self, anonymat, modification=False)
        if dialog.exec_():
            self.charger_candidats()

    def ouvrir_modification_notes(self, row):
        """Ouvre la boîte de dialogue pour modifier les notes d'un candidat."""
        anonymat = self.table.item(row, 2).text()
        dialog = SaisieNotesDialog(self, anonymat, modification=True)
        if dialog.exec_():
            self.charger_candidats()

class SaisieNotesDialog(QDialog):
    def __init__(self, parent, anonymat, modification=False):
        super().__init__(parent)
        self.setWindowTitle("Saisie des Notes")
        self.setModal(True)
        self.anonymat = anonymat
        self.modification = modification
        self.conn = parent.conn
        self.cur = parent.cur

        # Récupérer les informations du candidat
        self.cur.execute("""
            SELECT c.aptitude_sportive, c.choix_epr_facultative
            FROM Candidats c
            JOIN Anonymats a ON c.id_candidat = a.id_candidat
            WHERE a.numero_anonymat = ?
        """, (self.anonymat,))
        candidat_info = self.cur.fetchone()
        self.aptitude_sportive = candidat_info[0]  # True si apte, False si inapte
        self.choix_epr_facultative = candidat_info[1]  # True si épreuve facultative choisie, False sinon

        # Layout
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        # Sélection du tour
        self.tour_combo = QComboBox()
        self.tour_combo.addItems(["Premier Tour", "Second Tour"])
        self.tour_combo.currentIndexChanged.connect(self.update_notes_fields_visibility)
        self.layout.addRow("Tour:", self.tour_combo)

        # Champs de saisie des notes
        self.notes = {}
        self.matieres_tour1 = [
            "compo_francais", "dictee", "etude_de_texte", "instruction_civique", "histoire_geographie",
            "mathematiques", "pc_lv2", "svt", "anglais_ecrit", "anglais_oral", "eps", "epreuve_facultative"
        ]
        self.matieres_tour2 = [
            "francais_2nd_tour", "mathematiques_2nd_tour", "pc_lv2_2nd_tour"
        ]

        # Initialiser tous les champs
        self.init_all_notes_fields()

        # Masquer ou désactiver les champs selon RM15
        self.adapter_champs_selon_rm15()

        # Bouton Enregistrer
        self.btn_enregistrer = QPushButton("Enregistrer" if not self.modification else "Modifier")
        self.btn_enregistrer.setFont(QFont("Roboto", 12))
        self.btn_enregistrer.setStyleSheet(f"background-color: {ACCENT_COLOR}; color: {TEXT_COLOR}; padding: 10px; border-radius: 5px;")
        self.btn_enregistrer.setCursor(Qt.PointingHandCursor)
        self.btn_enregistrer.clicked.connect(self.enregistrer_notes)
        self.layout.addRow(self.btn_enregistrer)

        # Mettre à jour la visibilité des champs pour le premier tour
        self.update_notes_fields_visibility()

        # Charger les notes existantes si en mode modification
        if self.modification:
            self.charger_notes_existantes()

    def init_all_notes_fields(self):
        """Initialise tous les champs de saisie des notes."""
        for matiere in self.matieres_tour1 + self.matieres_tour2:
            spinbox = QSpinBox()
            spinbox.setRange(0, 20)
            self.notes[matiere] = spinbox
            self.layout.addRow(f"{matiere.replace('_', ' ').capitalize()}:", spinbox)
            spinbox.hide()  # Masquer tous les champs au démarrage

    def adapter_champs_selon_rm15(self):
        """Masque ou désactive les champs selon la règle RM15."""
        # Masquer ou désactiver l'EPS si le candidat est inapte
        if not self.aptitude_sportive:
            self.notes["eps"].setEnabled(False)
            self.notes["eps"].setStyleSheet("background-color: #f0f0f0; color: #a0a0a0;")  # Griser le champ

        # Masquer ou désactiver l'épreuve facultative si non choisie
        if not self.choix_epr_facultative:
            self.notes["epreuve_facultative"].setEnabled(False)
            self.notes["epreuve_facultative"].setStyleSheet("background-color: #f0f0f0; color: #a0a0a0;")  # Griser le champ

    def update_notes_fields_visibility(self):
        """Met à jour la visibilité des champs de saisie des notes en fonction du tour sélectionné."""
        tour_selected = self.tour_combo.currentText() == "Premier Tour"
        for matiere in self.matieres_tour1:
            self.notes[matiere].setVisible(tour_selected)
        for matiere in self.matieres_tour2:
            self.notes[matiere].setVisible(not tour_selected)

    def charger_notes_existantes(self):
        """Charge les notes existantes pour le candidat sélectionné."""
        tour_selected = self.tour_combo.currentText() == "Premier Tour"
        table = "Notes_Tour1" if tour_selected else "Notes_Tour2"
        self.cur.execute(f"""
            SELECT * FROM {table} WHERE anonymat = ?
        """, (self.anonymat,))
        notes_existantes = self.cur.fetchone()
        if notes_existantes:
            for matiere, spinbox in self.notes.items():
                if matiere in notes_existantes:
                    spinbox.setValue(notes_existantes[matiere])

    def enregistrer_notes(self):
        """Enregistre ou met à jour les notes en base de données."""
        try:
            # Récupérer l'id_candidat à partir de l'anonymat
            self.cur.execute("SELECT id_candidat FROM Anonymats WHERE numero_anonymat = ?", (self.anonymat,))
            result = self.cur.fetchone()
            if not result:
                QMessageBox.critical(self, "Erreur", "Aucun candidat trouvé pour cet anonymat.")
                return
            id_candidat = result[0]

            # Préparer les données pour l'insertion ou la mise à jour
            tour_selected = self.tour_combo.currentText() == "Premier Tour"
            notes_data = {}

            if tour_selected:
                # Premier tour : inclure toutes les matières appropriées
                for matiere in self.matieres_tour1:
                    # Gérer spécifiquement l'EPS et l'épreuve facultative
                    if matiere == "eps" and not self.aptitude_sportive:
                        continue
                    if matiere == "epreuve_facultative" and not self.choix_epr_facultative:
                        continue
                    notes_data[matiere] = self.notes[matiere].value()
            else:
                # Second tour : uniquement les matières du second tour
                for matiere in self.matieres_tour2:
                    notes_data[matiere] = self.notes[matiere].value()

            # Déterminer la table à utiliser
            table = "Notes_Tour1" if tour_selected else "Notes_Tour2"

            # Vérifier si des notes existent déjà pour ce tour
            self.cur.execute(f"SELECT COUNT(*) FROM {table} WHERE anonymat = ?", (self.anonymat,))
            if self.cur.fetchone()[0] > 0:
                # Mettre à jour les notes existantes
                set_clause = ", ".join([f"{matiere} = ?" for matiere in notes_data.keys()])
                values = list(notes_data.values())
                values.append(self.anonymat)
                self.cur.execute(f"""
                    UPDATE {table}
                    SET {set_clause}
                    WHERE anonymat = ?
                """, values)
            else:
                # Insérer de nouvelles notes
                columns = ", ".join(notes_data.keys())
                placeholders = ", ".join(["?"] * len(notes_data))
                values = list(notes_data.values())
                values.insert(0, self.anonymat)
                values.insert(1, id_candidat)
                self.cur.execute(f"""
                    INSERT INTO {table} (anonymat, id_candidat, {columns})
                    VALUES (?, ?, {placeholders})
                """, values)

            # Valider la transaction
            self.conn.commit()

            # Afficher un message de succès
            QMessageBox.information(self, "Succès", "Notes enregistrées avec succès.")
            self.accept()
        except sqlite3.Error as e:
            # Afficher un message d'erreur en cas d'échec
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement : {e}")
        except ValueError as ve:
            # Afficher un message d'erreur pour les valeurs invalides
            QMessageBox.critical(self, "Erreur", f"Valeur invalide : {ve}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SaisieNotes()
    window.show()
    sys.exit(app.exec_())
