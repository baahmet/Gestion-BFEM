import sys
from PyQt5.QtWidgets import QApplication, QDialog
from views.login_window import LoginWindow
from views.main_menu import MainMenu

if __name__ == "__main__":
    # Créer une instance de l'application PyQt
    app = QApplication(sys.argv)

    # Créer et afficher la fenêtre de connexion
    login_window = LoginWindow()
    if login_window.exec_() == QDialog.Accepted:
        role = login_window.role  # Récupérer le rôle après l'authentification
        if role:
            # Ouvrir la fenêtre principale avec le rôle
            main_menu = MainMenu(role)
            main_menu.show()
        else:
            print("Erreur : Aucun rôle n'a été retourné après l'authentification.")
            sys.exit(1)  # Quitter l'application avec un code d'erreur
    else:
        print("L'utilisateur a annulé la connexion.")
        sys.exit(0)  # Quitter l'application normalement

    # Exécuter l'application
    sys.exit(app.exec_())