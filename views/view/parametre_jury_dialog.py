import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMessageBox, QWidget, QVBoxLayout, QPushButton,
    QLabel, QLineEdit, QFormLayout, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from database import obtenir_jury_connecte

class ParametreJuryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Style de la fenêtre principale
        self.setStyleSheet("""
            QDialog {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #1a237e, stop: 1 #0d47a1);
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #bbdefb;
                border-radius: 5px;
                background-color: #e3f2fd;
                color: #1a237e;
                font-size: 12px;
            }
            QLineEdit:disabled {
                background-color: #cfd8dc;
                border: 2px solid #b0bec5;
            }
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #43a047;
            }
            QPushButton:pressed {
                background-color: #388e3c;
            }
        """)
        self.conn = None

        jury_info = obtenir_jury_connecte()
        if jury_info:
            self.user_id, self.username = jury_info
            self.conn = None
            self.cur = None
            self.setup_ui()
            self.connect_to_db()
            self.load_existing_data()
        else:
            QMessageBox.critical(self, "Erreur", "Aucun utilisateur Jury connecté")
            self.close()

    def setup_ui(self):
        self.setWindowTitle("Paramètres du Jury")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Main layout avec marges
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        # Header
        header_label = QLabel("PARAMÈTRES DU JURY")
        header_label.setFont(QFont('Arial', 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #283593;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
        """)
        main_layout.addWidget(header_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        main_layout.addLayout(form_layout)

        # Create input fields with placeholders
        self.fields = {
            'region': self.create_line_edit("Entrez la région"),
            'ief': self.create_line_edit("Entrez l'IEF"),
            'localite': self.create_line_edit("Entrez la localité"),
            'centre_examen': self.create_line_edit("Entrez le centre d'examen"),
            'telephone': self.create_line_edit("Entrez le numéro de téléphone")
        }

        # Style spécial pour les labels du formulaire
        label_style = """
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 13px;
            }
        """

        # Créer le champ président non modifiable
        self.president_field = QLineEdit()
        self.president_field.setReadOnly(True)
        self.president_field.setText(self.username)
        self.president_field.setStyleSheet("""
            QLineEdit {
                background-color: #cfd8dc;
                color: #37474f;
                border: 2px solid #b0bec5;
                font-weight: bold;
            }
        """)

        # Add fields to form layout with styled labels
        labels = ["Région:", "IEF:", "Localité:", "Centre d'Examen:", "Président:", "Téléphone:"]
        fields = [self.fields['region'], self.fields['ief'], self.fields['localite'],
                 self.fields['centre_examen'], self.president_field, self.fields['telephone']]
        
        for label_text, field in zip(labels, fields):
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            form_layout.addRow(label, field)

        # Button layout
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)
        self.save_button = QPushButton("ENREGISTRER")
        self.save_button.setMinimumHeight(40)
        button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.enregistrer_jury)
        main_layout.addLayout(button_layout)

    def create_line_edit(self, placeholder):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setMinimumHeight(35)
        return line_edit

    def connect_to_db(self):
        try:
            self.conn = sqlite3.connect('bfem_db.sqlite', timeout=10)
            self.cur = self.conn.cursor()
            self.create_table_if_not_exists()
        except sqlite3.Error as e:
            self.show_error("Erreur de connexion", f"Impossible de se connecter à la base de données: {str(e)}")

    def create_table_if_not_exists(self):
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS Parametres_Jury (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_utilisateur INTEGER NOT NULL,
                    region TEXT NOT NULL,
                    ief TEXT NOT NULL,
                    localite TEXT NOT NULL,
                    centre_examen TEXT NOT NULL,
                    president_jury TEXT NOT NULL,
                    telephone TEXT NOT NULL,
                    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateurs(id_utilisateur)
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            self.show_error("Erreur de création", f"Impossible de créer la table: {str(e)}")

    def load_existing_data(self):
        try:
            self.cur.execute("""
                SELECT region, ief, localite, centre_examen, telephone
                FROM Parametres_Jury 
                WHERE id_utilisateur = ?
            """, (self.user_id,))
            result = self.cur.fetchone()
            
            if result:
                self.fields['region'].setText(result[0])
                self.fields['ief'].setText(result[1])
                self.fields['localite'].setText(result[2])
                self.fields['centre_examen'].setText(result[3])
                self.fields['telephone'].setText(result[4])
        except sqlite3.Error as e:
            self.show_error("Erreur de chargement", f"Impossible de charger les données existantes: {str(e)}")

    def validate_inputs(self):
        for field_name, field in self.fields.items():
            if not field.text().strip():
                self.show_error("Validation", f"Le champ {field_name} ne peut pas être vide")
                return False
        
        # Validate phone number format
        phone = self.fields['telephone'].text().strip()
        if not phone.isdigit() or len(phone) < 9:
            self.show_error("Validation", "Le numéro de téléphone doit contenir au moins 9 chiffres")
            return False
        
        return True

    def enregistrer_jury(self):
        if not self.validate_inputs():
            return

        data = (
            self.user_id,
            self.fields['region'].text(),
            self.fields['ief'].text(),
            self.fields['localite'].text(),
            self.fields['centre_examen'].text(),
            self.username,  # Utiliser le nom du jury connecté
            self.fields['telephone'].text()
        )

        try:
            self.cur.execute("""
                INSERT INTO Parametres_Jury (
                    id_utilisateur, region, ief, localite, 
                    centre_examen, president_jury, telephone
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, data)
            self.conn.commit()
            QMessageBox.information(self, "Succès", "Paramètres du jury enregistrés avec succès.")
            self.accept()
        except sqlite3.Error as e:
            self.show_error("Erreur d'enregistrement", 
                          f"Erreur lors de l'enregistrement des paramètres du jury: {str(e)}")

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        self.close_connection()
        super().closeEvent(event)

    def close_connection(self):
      if hasattr(self, 'conn') and self.conn:  # Vérifie si self.conn existe
        self.conn.close()
