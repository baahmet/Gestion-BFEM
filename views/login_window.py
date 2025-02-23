from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from controllers.auth_controller import AuthController

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion")
        self.setGeometry(400, 300, 300, 150)
        
        # Appliquer un style global à la fenêtre
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F6FA;
                border-radius: 10px;
            }
            QLabel {
                color: #2C3E50;
                font-size: 14px;
                font-family: 'Roboto';
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                font-family: 'Roboto';
            }
            QLineEdit:focus {
                border: 1px solid #1ABC9C;
            }
            QPushButton {
                background-color: #1ABC9C;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Roboto';
            }
            QPushButton:hover {
                background-color: #16A085;
            }
            QPushButton:pressed {
                background-color: #148F77;
            }
        """)
        
        self.auth_controller = AuthController()
        self.role = None  # Attribut pour stocker le rôle après l'authentification
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Ajouter des marges
        
        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("Nom d'utilisateur:", self.username_input)
        form_layout.addRow("Mot de passe:", self.password_input)
        layout.addLayout(form_layout)
        
        self.login_button = QPushButton("Se connecter")
        self.login_button.clicked.connect(self.authenticate)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)
    
    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return
        
        # Authentifier l'utilisateur
        self.role = self.auth_controller.authenticate(username, password)
        
        if self.role:
            self.accept()  # Fermer la fenêtre de connexion
        else:
            QMessageBox.warning(self, "Erreur", "Nom d'utilisateur ou mot de passe incorrect.")
            self.role = None  # Réinitialiser le rôle en cas d'échec
    
    def clear_fields(self):
        """Efface les champs de connexion"""
        self.username_input.clear()
        self.password_input.clear()