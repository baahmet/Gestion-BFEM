from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidget, QFormLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from controllers.user_controller import UserController

# Couleurs inspirées du MainMenu
PRIMARY_COLOR = "#2C3E50"
ACCENT_COLOR = "#1ABC9C"
TEXT_COLOR = "#FFFFFF"
HOVER_COLOR = "#16A085"

class UserManagement(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Utilisateurs")
        self.setGeometry(350, 200, 600, 400)

        # Appliquer un style global à la fenêtre
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {PRIMARY_COLOR};
                color: {TEXT_COLOR};
                font-family: 'Roboto';
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
            }}
            QLineEdit {{
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT_COLOR};
            }}
            QListWidget {{
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};
            }}
            QPushButton:pressed {{
                background-color: #148F77;
            }}
        """)

        self.user_controller = UserController()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Ajouter des marges

        self.user_list = QListWidget()
        layout.addWidget(self.user_list)

        self.load_users()

        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez un nom d'utilisateur")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez un mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText("Entrez un rôle (Jury/Professeur)")

        form_layout.addRow("Nom d'utilisateur:", self.username_input)
        form_layout.addRow("Mot de passe:", self.password_input)
        form_layout.addRow("Rôle (Jury/Professeur):", self.role_input)
        layout.addLayout(form_layout)

        self.add_button = QPushButton("Ajouter Utilisateur")
        self.add_button.clicked.connect(self.add_user)
        layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Supprimer Utilisateur")
        self.delete_button.clicked.connect(self.delete_user)
        layout.addWidget(self.delete_button)

        self.central_widget.setLayout(layout)

    def load_users(self):
        self.user_list.clear()
        users = self.user_controller.get_all_users()
        for user in users:
            self.user_list.addItem(f"{user[0]} - {user[1]}")

    def add_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_input.text()

        if self.user_controller.add_user(username, password, role):
            QMessageBox.information(self, "Succès", "Utilisateur ajouté avec succès")
            self.load_users()
        else:
            QMessageBox.warning(self, "Erreur", "Nom d'utilisateur déjà utilisé")

    def delete_user(self):
        selected_user = self.user_list.currentItem()
        if selected_user:
            username = selected_user.text().split(" - ")[0]
            if self.user_controller.delete_user(username):
                QMessageBox.information(self, "Succès", "Utilisateur supprimé avec succès")
                self.load_users()
