import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout, QLabel, QComboBox, QLineEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from views.view.saisie_notes import SaisieNotesDialog
from views.view.saisie_notes import SaisieNotes
# Couleurs inspirées du MainMenu
PRIMARY_COLOR = "#2C3E50"
ACCENT_COLOR = "#1ABC9C"
TEXT_COLOR = "#FFFFFF"
HOVER_COLOR = "#2980B9"

class GestionDeliberation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Délibérations")
        self.setGeometry(200, 100, 1400, 800)
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
        self.title = QLabel("Délibération des Candidats")
        self.title.setFont(QFont("Roboto", 20, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # Tableau des candidats
        self.setup_table()

        # Filtres et contrôles
        self.setup_controls()

        # Boutons d'action
        self.setup_action_buttons()

        # Charger les candidats
        self.charger_candidats()

    def setup_table(self):
        """Configure le tableau des candidats."""
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        headers = [
            "Numéro Table",
            "Nom Candidat",
            "Points 1er Tour",
            "Points 2nd Tour",
            "Moyenne Cycle",
            "Bonus/Malus",
            "Total Points",
            "Statut",
            "Actions"
        ]
        self.table.setHorizontalHeaderLabels(headers)
        
        self.table.setStyleSheet("background-color: white; color: black; border-radius: 5px;")
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)

    def setup_controls(self):
            """Configure les filtres et contrôles."""
            controls_layout = QHBoxLayout()

            self.statut_filter = QComboBox()
            self.statut_filter.addItems(["Tous", "Admis", "2nd Tour", "Repêchage", "Échec"])
            self.statut_filter.currentTextChanged.connect(self.appliquer_filtres)

            self.search_box = QLineEdit()
            self.search_box.setPlaceholderText("Rechercher un candidat...")
            self.search_box.textChanged.connect(self.appliquer_filtres)

            for widget in [QLabel("Filtrer par statut:"), self.statut_filter,
                        QLabel("Rechercher:"), self.search_box]:
                controls_layout.addWidget(widget)

            self.layout.addLayout(controls_layout)

    def setup_action_buttons(self):
        """Configure les boutons d'action."""
        buttons_layout = QHBoxLayout()

        self.btn_deliberer = QPushButton("Lancer la Délibération")
        self.btn_second_tour = QPushButton("Valider pour 2nd Tour")
        self.btn_gerer_2nd_tour = QPushButton("Gérer 2nd Tour")
        self.btn_finaliser = QPushButton("Finaliser")

        for btn in [self.btn_deliberer, self.btn_second_tour, 
                    self.btn_gerer_2nd_tour, self.btn_finaliser]:  # Ajout du nouveau bouton
            btn.setFont(QFont("Roboto", 12))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ACCENT_COLOR};
                    color: {TEXT_COLOR};
                    padding: 10px;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background-color: {HOVER_COLOR};
                }}
            """)
            buttons_layout.addWidget(btn)

        self.btn_deliberer.clicked.connect(self.lancer_deliberation)
        self.btn_second_tour.clicked.connect(self.valider_second_tour)
        self.btn_gerer_2nd_tour.clicked.connect(self.gerer_second_tour)  
        self.btn_finaliser.clicked.connect(self.finaliser_deliberation)

        self.layout.addLayout(buttons_layout)

    def calculer_points_et_statut(self, id_candidat):
        """Calcule les points et détermine le statut d'un candidat."""
        self.cur.execute("""
            SELECT compo_francais, dictee, etude_de_texte, instruction_civique,
                histoire_geographie, mathematiques, pc_lv2, svt,
                anglais_ecrit, anglais_oral, eps, epreuve_facultative
            FROM Notes_Tour1
            WHERE id_candidat = ?
        """, (id_candidat,))
        notes_tour1 = self.cur.fetchone()

        if not notes_tour1:
            return None, None, None, 0, "Notes manquantes"

        self.cur.execute("""
            SELECT francais_2nd_tour, mathematiques_2nd_tour, pc_lv2_2nd_tour
            FROM Notes_Tour2
            WHERE id_candidat = ?
        """, (id_candidat,))
        notes_tour2 = self.cur.fetchone()

        self.cur.execute("""
            SELECT moyenne_cycle
            FROM Livret_Scolaire
            WHERE id_candidat = ?
        """, (id_candidat,))
        moyenne_cycle = self.cur.fetchone()
        moyenne_cycle = moyenne_cycle[0] if moyenne_cycle else 0

        coefficients_tour1 = {
            "compo_francais": 2, "dictee": 1, "etude_de_texte": 1,
            "instruction_civique": 1, "histoire_geographie": 2,
            "mathematiques": 4, "pc_lv2": 2, "svt": 2,
            "anglais_ecrit": 2, "anglais_oral": 1
        }

        points_tour1 = sum(notes_tour1[i] * coef
                        for i, (matiere, coef) in enumerate(coefficients_tour1.items())
                        if notes_tour1[i] is not None)

        bonus_malus = 0

        if notes_tour1[10] is not None:
            if notes_tour1[10] > 10:
                bonus_malus += (notes_tour1[10] - 10)
            else:
                bonus_malus -= (10 - notes_tour1[10])

        if notes_tour1[11] is not None and notes_tour1[11] > 10:
            bonus_malus += (notes_tour1[11] - 10)

        points_tour2 = None
        if notes_tour2:
            coefficients_tour2 = {
                "francais_2nd_tour": 2,
                "mathematiques_2nd_tour": 4,
                "pc_lv2_2nd_tour": 2
            }
            points_tour2 = sum(notes_tour2[i] * coef
                            for i, coef in enumerate(coefficients_tour2.values())
                            if notes_tour2[i] is not None)

        total_points = points_tour1 + bonus_malus
        statut = self.determiner_statut(total_points, points_tour2, moyenne_cycle)

        return total_points, points_tour2, moyenne_cycle, bonus_malus, statut

    def determiner_statut(self, points_tour1, points_tour2, moyenne_cycle):
        """Détermine le statut d'un candidat selon les règles RM4-RM9."""
        if points_tour2 is not None:
            if points_tour2 >= 60:
                return "Admis"
            return "Échec"

        if points_tour1 >= 180:
            return "Admis"
        elif 153 <= points_tour1 < 171:
            return "2nd Tour"
        elif 171 <= points_tour1 < 180:
            return "Repêchage"
        elif 144 <= points_tour1 < 153:
            return "Repêchage"
        elif moyenne_cycle >= 12:
            return "Repêchage"
        else:
            return "Échec"

    def charger_candidats(self):
        """Charge et affiche tous les candidats."""
        self.table.setRowCount(0)
        self.cur.execute("""
            SELECT C.id_candidat, C.numero_table, C.nom || ' ' || C.prenom
            FROM Candidats C
            ORDER BY C.numero_table
        """)
        candidats = self.cur.fetchall()

        for row, (id_candidat, numero_table, nom_complet) in enumerate(candidats):
            points_tour1, points_tour2, moyenne_cycle, bonus_malus, statut = \
                self.calculer_points_et_statut(id_candidat)

            if points_tour1 is None:
                continue

            self.table.insertRow(row)

            items = [
                numero_table,
                nom_complet,
                points_tour1,
                points_tour2 if points_tour2 else "N/A",
                moyenne_cycle,
                bonus_malus,
                points_tour1 + bonus_malus,
                statut
            ]

            for col, item in enumerate(items):
                table_item = QTableWidgetItem(str(item))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, table_item)

            btn_action = QPushButton("Détails")
            btn_action.setStyleSheet(f"background-color: {HOVER_COLOR}; color: {TEXT_COLOR};")
            btn_action.clicked.connect(lambda _, r=row: self.afficher_details(r))
            self.table.setCellWidget(row, 8, btn_action)
      
    def appliquer_filtres(self):
        """Applique les filtres de recherche et de statut."""
        filtre_statut = self.statut_filter.currentText()
        texte_recherche = self.search_box.text().lower()

        for row in range(self.table.rowCount()):
            masquer = False
            
            # Vérifier le filtre de statut
            if filtre_statut != "Tous":
                statut_item = self.table.item(row, 7)
                if statut_item and statut_item.text() != filtre_statut:
                    masquer = True

            # Vérifier le filtre de recherche
            if texte_recherche:
                nom_item = self.table.item(row, 1)
                numero_item = self.table.item(row, 0)
                
                nom = nom_item.text().lower() if nom_item else ""
                numero = numero_item.text().lower() if numero_item else ""
                
                if texte_recherche not in nom and texte_recherche not in numero:
                    masquer = True

            # Appliquer le masquage
            self.table.setRowHidden(row, masquer)


    def lancer_deliberation(self):
        """Lance le processus de délibération pour tous les candidats."""
        choix = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous lancer la délibération pour tous les candidats ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if choix == QMessageBox.Yes:
            self.charger_candidats()
            QMessageBox.information(self, "Succès", "Délibération effectuée avec succès.")

    def valider_second_tour(self):
        selection = self.table.selectedItems()
        if not selection:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner des candidats.")
            return

        rows = set(item.row() for item in selection)
        for row in rows:
            if self.table.item(row, 7).text() == "2nd Tour":
                numero_table = self.table.item(row, 0).text()
                
                # Mise à jour de la base de données
                self.cur.execute("""
                    UPDATE Deliberation 
                    SET statut = '2nd Tour'
                    WHERE id_candidat IN (
                        SELECT id_candidat 
                        FROM Candidats 
                        WHERE numero_table = ?
                    )
                """, (numero_table,))
                
                # Mise à jour immédiate de l'interface
                self.table.item(row, 7).setText("2nd Tour")
        
        self.conn.commit()  # Important : commit les changements
        self.charger_candidats()  # Recharger pour refléter les changements
        QMessageBox.information(self, "Succès", "Candidats validés pour le second tour.")
    
    def gerer_second_tour(self):
        """Gère les candidats admis au second tour après délibération."""
        try:
            # Récupérer tous les candidats du second tour
            self.cur.execute("""
                SELECT C.numero_table, C.nom || ' ' || C.prenom, A.numero_anonymat,
                    D.points_tour1
                FROM Deliberation D
                JOIN Candidats C ON D.id_candidat = C.id_candidat
                LEFT JOIN Anonymats A ON C.id_candidat = A.id_candidat
                WHERE D.statut = '2nd Tour'
            """)
            candidats_2nd_tour = self.cur.fetchall()
            
            if not candidats_2nd_tour:
                QMessageBox.information(self, "Information", 
                    "Aucun candidat n'est actuellement admis au second tour.")
                return
                
            # Demander confirmation pour ouvrir la saisie des notes
            choix = QMessageBox.question(self, "Second Tour",
                "Voulez-vous procéder à la saisie des notes du second tour ?",
                QMessageBox.Yes | QMessageBox.No)
                
            if choix == QMessageBox.Yes:
                self.fenetre_saisie = SaisieNotes()
                # Ouvrir directement la fenêtre en mode second tour
                dialog = SaisieNotesDialog(self.fenetre_saisie, candidats_2nd_tour[0][2] if candidats_2nd_tour[0][2] else "", modification=False)
                dialog.tour_combo.setCurrentText("Second Tour")
                dialog.exec_()  # Utiliser exec_ au lieu de show()
                self.fenetre_saisie.charger_candidats()  # Recharger les candidats après la saisie
                self.fenetre_saisie.show()
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", 
                f"Erreur lors de la gestion du second tour : {e}")

    def finaliser_deliberation(self):
        """Finalise le processus de délibération."""
        choix = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous finaliser la délibération ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if choix == QMessageBox.Yes:
            try:
                for row in range(self.table.rowCount()):
                    numero_table = self.table.item(row, 0).text()
                    points_tour1 = float(self.table.item(row, 2).text())
                    points_tour2 = self.table.item(row, 3).text()
                    points_tour2 = float(points_tour2) if points_tour2 != "N/A" else None
                    statut = self.table.item(row, 7).text()

                    # Récupérer l'id_candidat à partir du numéro de table
                    self.cur.execute("""
                        SELECT id_candidat 
                        FROM Candidats 
                        WHERE numero_table = ?
                    """, (numero_table,))
                    id_candidat = self.cur.fetchone()[0]

                    # Insérer ou mettre à jour dans la table Deliberation
                    self.cur.execute("""
                        INSERT OR REPLACE INTO Deliberation 
                        (id_candidat, points_tour1, points_tour2, statut)
                        VALUES (?, ?, ?, ?)
                    """, (id_candidat, points_tour1, points_tour2, statut))
                
                self.conn.commit()
                QMessageBox.information(self, "Succès", "Délibération finalisée avec succès.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la finalisation : {e}")

    def afficher_details(self, row):
        """Affiche les détails d'un candidat."""
        details = "\n".join([
            f"Numéro Table: {self.table.item(row, 0).text()}",
            f"Nom: {self.table.item(row, 1).text()}",
            f"Points 1er Tour: {self.table.item(row, 2).text()}",
            f"Points 2nd Tour: {self.table.item(row, 3).text()}",
            f"Moyenne Cycle: {self.table.item(row, 4).text()}",
            f"Bonus/Malus: {self.table.item(row, 5).text()}",
            f"Total Points: {self.table.item(row, 6).text()}",
            f"Statut: {self.table.item(row, 7).text()}"
        ])

        QMessageBox.information(self, "Détails du Candidat", details)

    def closeEvent(self, event):
        """Ferme la connexion à la base de données lors de la fermeture de l'application."""
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GestionDeliberation()
    window.show()
    sys.exit(app.exec_())