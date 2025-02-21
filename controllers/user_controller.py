import sqlite3
from models.database_manager import DatabaseManager

class UserController:
    def __init__(self):
        self.db_manager = DatabaseManager("bfem_db.sqlite")

    def get_all_users(self):
        """Récupère tous les utilisateurs."""
        return self.db_manager.fetch_all("SELECT nom_utilisateur, role FROM Utilisateurs")

    def add_user(self, username, password, role):
        """Ajoute un nouvel utilisateur."""
        hashed_password = self.db_manager.hash_password(password)
        try:
            self.db_manager.execute_query(
                "INSERT INTO Utilisateurs (nom_utilisateur, mot_de_passe, role) VALUES (?, ?, ?)",
                (username, hashed_password, role)
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_user(self, username):
        """Supprime un utilisateur."""
        self.db_manager.execute_query("DELETE FROM Utilisateurs WHERE nom_utilisateur = ?", (username,))
        return True