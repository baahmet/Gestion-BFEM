import sys
import traceback
import os
import pandas as pd
import sqlite3
import random
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QDesktopWidget, QPushButton,
    QLabel, QMessageBox, QFrame, QSpacerItem, QSizePolicy, QGridLayout, QToolBar,
    QAction, QMenu, QApplication
)
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QLinearGradient, QPainter, QPixmap
from PyQt5.QtCore import Qt, QSize, QDateTime, QPropertyAnimation, QEasingCurve
from views.user_management import UserManagement
from views.login_window import LoginWindow
from views.view.gestion_candidats import GestionCandidats
from views.view.parametre_jury_dialog import ParametreJuryDialog
from views.view.gestion_anonymats import GestionAnonymats
from views.view.saisie_notes import SaisieNotes
from views.view.gestion_deliberations import GestionDeliberation
from views.view.gestion_repechages import GestionRepechage
from views.view.statistiques import Statistiques
from views.view.pdf_generator import PDFGenerator
from views.view.releve_notes_generator import ReleveNotesGenerator
from database import obtenir_jury_connecte

# Constantes pour les styles
PRIMARY_COLOR = "#2C3E50"
SECONDARY_COLOR = "#34495E"
ACCENT_COLOR = "#1ABC9C"
BACKGROUND_COLOR = "#F5F6FA"
TEXT_COLOR = "#FFFFFF"
HOVER_COLOR = "#2980B9"
DISABLED_COLOR = "#7F8C8D"
SHADOW_COLOR = "#000000"

class NavBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setStyleSheet(f"""
            QToolBar {{
                background-color: {PRIMARY_COLOR};
                border: none;
                padding: 8px;
            }}
            QToolButton {{
                color: {TEXT_COLOR};
                background: transparent;
                border: none;
                padding: 8px;
                font-size: 14px;
                font-family: 'Roboto';
            }}
            QToolButton:hover {{
                background-color: {SECONDARY_COLOR};
                border-radius: 4px;
            }}
            QMenu {{
                background-color: {PRIMARY_COLOR};
                color: {TEXT_COLOR};
                border: 1px solid {SECONDARY_COLOR};
                font-family: 'Roboto';
            }}
            QMenu::item {{
                padding: 8px 25px;
            }}
            QMenu::item:selected {{
                background-color: {SECONDARY_COLOR};
            }}
        """)

        # Logo et titre
        logo_label = QLabel()
        logo_label.setPixmap(QIcon("icons/logo.png").pixmap(32, 32))
        self.addWidget(logo_label)

        title_label = QLabel("BFEM")
        title_label.setStyleSheet(f"color: black; font-size: 18px; font-weight: bold; padding: 0 10px;")
        self.addWidget(title_label)

        self.addSeparator()

        # Menu Fichier
        file_menu = QMenu()
        file_menu.addAction("Nouveau", lambda: None)
        file_menu.addAction("Ouvrir...", lambda: None)
        file_menu.addSeparator()
        file_menu.addAction("Exporter...", lambda: None)

        file_button = QPushButton("Fichier")
        file_button.setStyleSheet(f"""
            QPushButton {{
                color: {TEXT_COLOR};
                background: transparent;
                border: none;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {SECONDARY_COLOR};
                border-radius: 4px;
            }}
        """)
        file_button.setMenu(file_menu)
        self.addWidget(file_button)

        # Autres actions
        self.addAction(QIcon("icons/settings.png"), "Paramètres")
        self.addAction(QIcon("icons/help.png"), "Aide")

        # Bouton profil à droite
        self.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.addWidget(spacer)

        # Bouton de déconnexion
        self.logout_button = QPushButton(QIcon("icons/logout.png"), "Déconnexion")
        self.logout_button.setStyleSheet(f"""
            QPushButton {{
                color: {TEXT_COLOR};
                background: transparent;
                border: none;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {SECONDARY_COLOR};
                border-radius: 4px;
            }}
        """)
        self.addWidget(self.logout_button)

        # Connecter le bouton de déconnexion à la méthode logout
        if parent is not None:
            self.logout_button.clicked.connect(parent.logout)

class Footer(QFrame):
    """Pied de page personnalisé avec un design moderne"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {PRIMARY_COLOR};
                color: {TEXT_COLOR};
                padding: 10px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-family: 'Roboto';
            }}
            QPushButton {{
                color: {ACCENT_COLOR};
                background: transparent;
                border: none;
                font-family: 'Roboto';
            }}
            QPushButton:hover {{
                color: {HOVER_COLOR};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)

        # Copyright
        copyright_label = QLabel("© 2025 Système de Gestion BFEM")
        layout.addWidget(copyright_label)

        # Liens utiles
        layout.addStretch()
        for text in ["Aide", "Contact", "Mentions légales"]:
            btn = QPushButton(text)
            layout.addWidget(btn)

        # Date et heure
        self.time_label = QLabel()
        self.update_time()
        layout.addStretch()
        layout.addWidget(self.time_label)

    def update_time(self):
        """Mise à jour de l'heure"""
        current_time = QDateTime.currentDateTime().toString("dd/MM/yyyy hh:mm")
        self.time_label.setText(current_time)

class MainMenu(QMainWindow):
    def __init__(self, role: str):
        super().__init__()
        self.role = role
        self.setup_ui()
        self.center()

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.setWindowTitle("Gestion BFEM - Menu Principal")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #F5F6FA;")

        # Ajouter la barre de navigation
        self.navbar = NavBar(self)
        self.addToolBar(self.navbar)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Créer le layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # En-tête
        header = QFrame()
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1ABC9C, stop:1 #2980B9);
            border-radius: 10px;
            padding: 20px;
        """)
        header_layout = QHBoxLayout(header)

        title = QLabel("Système de Gestion BFEM")
        title.setFont(QFont("Roboto", 24, QFont.Bold))
        title.setStyleSheet("color: white;")

        user_info = QLabel(f"Connecté en tant que : {self.role}")
        user_info.setFont(QFont("Roboto", 12))
        user_info.setStyleSheet("color: white;")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(user_info)

        # Ajouter l'en-tête au layout principal
        main_layout.addWidget(header)

        # Section des boutons (grille)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        self.buttons = {
            'users': MenuButton("Gestion des Utilisateurs", "icons/users.png"),
            'jury': MenuButton("Paramétrage du Jury", "icons/jury.png"),
            'candidates': MenuButton("Gestion des Candidats", "icons/candidates.png"),
            'anonymity': MenuButton("Génération des Anonymats", "icons/anonymity.png"),
            'grades': MenuButton("Saisie des Notes", "icons/grades.png"),
            'deliberation': MenuButton("Suivi des Délibérations", "icons/deliberation.png"),
            'rescue': MenuButton("Gestion des Repêchages", "icons/rescue.png"),
            'stats': MenuButton("Statistiques des Résultats", "icons/stats.png"),
            'pdf': MenuButton("Impression des PV et Relevés", "icons/pdf.png"),
            'notes_generator': MenuButton("Générateur de relevés (1er et 2nd tour)", "icons/notes.png"),
            'import_data': MenuButton("Intégrer données de test (Excel BD BFEM)", "icons/import.png"),
            'quit': MenuButton("Quitter le programme", "icons/quit.png")
        }

        positions = [(i, j) for i in range(4) for j in range(3)]
        for position, (key, button) in zip(positions, self.buttons.items()):
            grid_layout.addWidget(button, *position)

        # Ajouter la grille au layout principal
        main_layout.addLayout(grid_layout)
        
        # Ajouter un espacement avant le footer
        main_layout.addStretch()

        # Pied de page avec le bouton d'aide intégré
        self.footer = Footer()
        # Connecter le bouton d'aide existant
        for child in self.footer.findChildren(QPushButton):
            if child.text() == "Aide":
                child.clicked.connect(self.ouvrir_guide)
        main_layout.addWidget(self.footer)

        # Gestion des accès selon le rôle
        self.manage_role_access()

        # Connexion des signaux
        self.connect_signals()
    
        

    def ouvrir_guide(self):
        """Ouvre le Guide Utilisateur en PDF."""
        chemin_pdf = os.path.abspath("Guide_Utilisateur.pdf")
        
        if not os.path.exists(chemin_pdf):
            try:
                from guide_generator import generer_guide_utilisateur
                generer_guide_utilisateur()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de générer le guide : {str(e)}")
                return
                
        try:
            if sys.platform == "win32":  # Windows
                os.startfile(chemin_pdf)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", chemin_pdf], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", chemin_pdf], check=True)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le PDF : {str(e)}")

    def center(self):
        """Centre la fenêtre sur l'écran"""
        screen = QDesktopWidget().screenGeometry()  # Géométrie de l'écran
        window = self.geometry()  # Géométrie de la fenêtre

        # Calculer la position pour centrer la fenêtre
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2

        self.move(x, y)  # Déplacer la fenêtre au centre

    def manage_role_access(self):
        """Gestion des accès selon le rôle de l'utilisateur"""
        if self.role == "Professeur":
            restricted_buttons = ['jury', 'deliberation', 'rescue', 'stats', 'pdf']
            for button_key in restricted_buttons:
                self.buttons[button_key].setEnabled(False)
                self.buttons[button_key].setToolTip("Accès restreint")

            self.buttons['candidates'].setText("Liste des Candidats (Lecture seule)")

    def connect_signals(self):
        """Connexion des signaux aux slots"""
        self.buttons['users'].clicked.connect(self.open_user_management)
        self.buttons['candidates'].clicked.connect(self.open_gestion_candidats)
        self.buttons['jury'].clicked.connect(self.open_parametre_jury)
        self.buttons['anonymity'].clicked.connect(self.open_gestion_anonymats)
        self.buttons['grades'].clicked.connect(self.open_saisie_notes)
        self.buttons['deliberation'].clicked.connect(self.open_suivi_deliberation)
        self.buttons['rescue'].clicked.connect(self.open_suivi_repechage)
        self.buttons['stats'].clicked.connect(self.open_statistiques)
        self.buttons['pdf'].clicked.connect(self.open_pdf_generator)
        self.buttons['notes_generator'].clicked.connect(self.open_notes_generator)
        self.buttons['import_data'].clicked.connect(self.import_test_data)
        self.buttons['quit'].clicked.connect(self.quit_application)

    def open_user_management(self):
        """Ouvre la fenêtre de gestion des utilisateurs"""
        if self.role != "Jury":
            QMessageBox.warning(
                self,
                "Accès Refusé",
                "Seuls les utilisateurs avec le rôle 'Jury' peuvent accéder à cette fonctionnalité.",
                QMessageBox.Ok
            )
            return

        self.user_management_window = UserManagement()
        self.user_management_window.show()

    def open_gestion_candidats(self):
        """Ouvre la fenêtre de gestion des candidats"""
        self.gestion_candidats_window = GestionCandidats()
        self.gestion_candidats_window.show()

    def open_parametre_jury(self):
        """Ouvre la fenêtre de paramétrage du jury"""
        self.parametre_jury_window = ParametreJuryDialog()
        self.parametre_jury_window.show()

    def open_gestion_anonymats(self):
        """Ouvre la fenêtre de gestion Anonymats"""
        self.gestion_anonymats_window = GestionAnonymats()
        self.gestion_anonymats_window.show()

    def open_saisie_notes(self):
        """Ouvre la fenêtre de saisie des notes"""
        self.open_saisie_notes_window = SaisieNotes()
        self.open_saisie_notes_window.show()

    def open_suivi_deliberation(self):
        """Ouvre la fenêtre de suivi des délibérations"""
        self.open_suivi_deliberation_window = GestionDeliberation()
        self.open_suivi_deliberation_window.show()

    def open_suivi_repechage(self):
        """Ouvre la fenêtre de suivi des repêchages"""
        self.open_suivi_repechage_window = GestionRepechage()
        self.open_suivi_repechage_window.show()

    def open_statistiques(self):
        """Ouvre la fenêtre des statistiques des résultats"""
        self.open_statistiques_window = Statistiques()
        self.open_statistiques_window.show()

    def open_pdf_generator(self):
        """Ouvre la fenêtre de l'impression des résultats"""
        self.open_pdf_generator_window = PDFGenerator()
        self.open_pdf_generator_window.show()

    def open_notes_generator(self):
        """Ouvre le générateur de relevés de notes"""
        self.open_notes_generator_window = ReleveNotesGenerator()
        self.open_notes_generator_window.show()

    def import_test_data(self):
        """Importe les données de test depuis le fichier Excel avec gestion des anonymats."""
        conn = None
        try:
            # Chemin du fichier Excel
            file_path = os.path.join(os.getcwd(), "BD_BFEM.xlsx")

            if not os.path.exists(file_path):
                QMessageBox.critical(self, "Erreur", f"Le fichier n'existe pas à l'emplacement spécifié: {file_path}")
                return

            # Charger le fichier Excel
            data = pd.read_excel(file_path, sheet_name=None)
            feuille_candidats = "Feuille 1"

            if feuille_candidats not in data:
                QMessageBox.critical(self, "Erreur", f"La feuille '{feuille_candidats}' est introuvable dans le fichier Excel.")
                return

            # Connexion à la base de données
            conn = sqlite3.connect('bfem_db.sqlite')
            cur = conn.cursor()

            # Vérifier et créer les tables si nécessaire
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Notes_Tour1 (
                    id_candidat INTEGER,
                    anonymat INTEGER,
                    compo_francais REAL,
                    dictee REAL,
                    etude_de_texte REAL,
                    instruction_civique REAL,
                    histoire_geographie REAL,
                    mathematiques REAL,
                    pc_lv2 REAL,
                    svt REAL,
                    anglais_ecrit REAL,
                    anglais_oral REAL,
                    eps REAL,
                    epreuve_facultative REAL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS Anonymats (
                    id_candidat INTEGER,
                    numero_anonymat INTEGER,
                    tour INTEGER
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS Livret_Scolaire (
                    id_candidat INTEGER,
                    nombre_de_fois INTEGER,
                    moyenne_6e REAL,
                    moyenne_5e REAL,
                    moyenne_4e REAL,
                    moyenne_3e REAL,
                    moyenne_cycle REAL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS Candidats (
                    id_candidat INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_table INTEGER,
                    prenom TEXT,
                    nom TEXT,
                    date_naissance TEXT,
                    lieu_naissance TEXT,
                    sexe TEXT,
                    type_candidat TEXT,
                    etablissement TEXT,
                    nationalite TEXT,
                    choix_epr_facultative BOOLEAN,
                    epreuve_facultative TEXT,
                    aptitude_sportive BOOLEAN
                )
            """)

            # Nettoyer les tables existantes
            cur.execute("DELETE FROM Notes_Tour1")
            cur.execute("DELETE FROM Anonymats")
            cur.execute("DELETE FROM Livret_Scolaire")
            cur.execute("DELETE FROM Candidats")

            # Convertir les dates en format string
            df = data[feuille_candidats].copy()
            df['Date de nais.'] = pd.to_datetime(df['Date de nais.']).dt.strftime('%Y-%m-%d')

            # Fonction pour normaliser l'épreuve facultative
            def normaliser_epreuve_facultative(valeur):
                if pd.isna(valeur) or valeur == '':
                    return 'Neutre'
                valeur = str(valeur).upper().strip()
                mapping = {
                    'COUT': 'COUTURE',
                    'DESS': 'DESSIN',
                    'MUSI': 'MUSIQUE'
                }
                for key, mapped_value in mapping.items():
                    if valeur.startswith(key):
                        return mapped_value
                return 'Neutre'

            # Insérer les candidats
            for index, row in df.iterrows():
                numero_table = row['N° de table']
                choix_epr_facultative = row.get('choix_epr_facultative', False)
                epreuve_facultative = normaliser_epreuve_facultative(row['Epreuve Facultative'])

                # Insérer le candidat
                cur.execute("""
                    INSERT INTO Candidats (
                        numero_table, prenom, nom, date_naissance, lieu_naissance,
                        sexe, type_candidat, etablissement, nationalite,
                        choix_epr_facultative, epreuve_facultative, aptitude_sportive
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    numero_table, row['Prenom (s)'], row['NOM'], row['Date de nais.'],
                    row['Lieu de nais.'], row['Sexe'], row['Type de candidat'], row['Etablissement'],
                    row['Nationnallité'], choix_epr_facultative, epreuve_facultative,
                    row['Etat Sportif']
                ))

            # Trier les candidats par numéro de table
            df = df.sort_values(by='N° de table')

            # Générer les anonymats
            numeros_utilises = set()
            for index, row in df.iterrows():
                numero_table = row['N° de table']
                while True:
                    anonymat = random.randint(1000, 9999)
                    if anonymat not in numeros_utilises:
                        numeros_utilises.add(anonymat)
                        break

                # Récupérer l'ID du candidat
                cur.execute("SELECT id_candidat FROM Candidats WHERE numero_table = ?", (numero_table,))
                result = cur.fetchone()
                if result:
                    id_candidat = result[0]
                else:
                    print(f"Aucun candidat trouvé pour le numéro de table {numero_table}")
                    continue

                # Insérer l'anonymat
                cur.execute("""
                    INSERT INTO Anonymats (id_candidat, numero_anonymat, tour)
                    VALUES (?, ?, 1)
                """, (id_candidat, anonymat))

                # Insérer les données du livret scolaire
                moyennes = [
                    float(row['Moy_6e']) if pd.notna(row['Moy_6e']) else 0,
                    float(row['Moy_5e']) if pd.notna(row['Moy_5e']) else 0,
                    float(row['Moy_4e']) if pd.notna(row['Moy_4e']) else 0,
                    float(row['Moy_3e']) if pd.notna(row['Moy_3e']) else 0
                ]
                moyenne_cycle = sum(moyennes) / len([m for m in moyennes if m > 0]) if any(m > 0 for m in moyennes) else 0

                cur.execute("""
                    INSERT INTO Livret_Scolaire (
                        id_candidat, nombre_de_fois, moyenne_6e, moyenne_5e, moyenne_4e, moyenne_3e, moyenne_cycle
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    numero_table, row['Nb fois'],
                    float(row['Moy_6e']) if pd.notna(row['Moy_6e']) else None,
                    float(row['Moy_5e']) if pd.notna(row['Moy_5e']) else None,
                    float(row['Moy_4e']) if pd.notna(row['Moy_4e']) else None,
                    float(row['Moy_3e']) if pd.notna(row['Moy_3e']) else None,
                    moyenne_cycle
                ))

                # Insérer les notes du premier tour
                cur.execute("""
                    INSERT INTO Notes_Tour1 (
                        id_candidat, anonymat, compo_francais, dictee, etude_de_texte, instruction_civique,
                        histoire_geographie, mathematiques, pc_lv2, svt, anglais_ecrit, anglais_oral,
                        eps, epreuve_facultative
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_candidat,
                    anonymat,
                    float(row['Note CF']) if pd.notna(row['Note CF']) else None,
                    float(row['Note Ort']) if pd.notna(row['Note Ort']) else None,
                    float(row['Note TSQ']) if pd.notna(row['Note TSQ']) else None,
                    float(row['Note IC']) if pd.notna(row['Note IC']) else None,
                    float(row['Note HG']) if pd.notna(row['Note HG']) else None,
                    float(row['Note MATH']) if pd.notna(row['Note MATH']) else None,
                    float(row['Note PC/LV2']) if pd.notna(row['Note PC/LV2']) else None,
                    float(row['Note SVT']) if pd.notna(row['Note SVT']) else None,
                    float(row['Note ANG1']) if pd.notna(row['Note ANG1']) else None,
                    float(row['Note ANG2']) if pd.notna(row['Note ANG2']) else None,
                    float(row['Note EPS']) if pd.notna(row['Note EPS']) else None,
                    float(row['Note Ep Fac']) if pd.notna(row['Note Ep Fac']) else None
                ))

            # Valider les modifications
            conn.commit()
            QMessageBox.information(self, "Import des données", "Données importées avec succès !")

        except Exception as e:
            error_message = f"Erreur lors de l'importation des données : {str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_message)
        finally:
            if conn:
                conn.close()

    def quit_application(self):
        """Quitte l'application"""
        reply = QMessageBox.question(
            self,
            "Quitter",
            "Êtes-vous sûr de vouloir quitter l'application ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()

    def logout(self):
        """Déconnexion de l'utilisateur"""
        reply = QMessageBox.question(
            self,
            "Déconnexion",
            "Êtes-vous sûr de vouloir vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.close()  # Fermer la fenêtre principale
            self.login_window = LoginWindow()  # Créer une nouvelle instance de LoginWindow
            self.login_window.clear_fields()  # Effacer les champs de connexion
            self.login_window.show()  # Afficher la fenêtre de connexion

class MenuButton(QPushButton):
    """Classe personnalisée pour les boutons du menu"""
    def __init__(self, text, icon_path=None):
        super().__init__(text)
        self.setFont(QFont("Roboto", 11))
        self.setMinimumHeight(60)

        # Charger l'icône si le chemin est fourni
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))

        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2C3E50, stop:1 #34495E);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                text-align: left;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34495E, stop:1 #2980B9);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980B9, stop:1 #1ABC9C);
            }
            QPushButton:disabled {
                background-color: #7F8C8D;
                color: #BDC3C7;
            }
        """)
