import sys
from PyQt5.QtWidgets import QApplication, QDialog
from views.login_window import LoginWindow
from views.main_menu import MainMenu

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    
    # Si la connexion réussit, ouvrir le menu principal
    if login_window.exec_() == QDialog.Accepted:
        role = login_window.authenticate()
        if role:
            main_menu = MainMenu(role)
            main_menu.show()
            sys.exit(app.exec_())