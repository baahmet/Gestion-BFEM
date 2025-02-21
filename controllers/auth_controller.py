from models.database_manager import DatabaseManager

class AuthController:
    def __init__(self):
        self.db_manager = DatabaseManager("bfem_db.sqlite")

    def authenticate(self, username, password):
        """Authentifie un utilisateur et retourne son rôle."""
        hashed_password = self.db_manager.hash_password(password)
        user = self.db_manager.fetch_one(
            "SELECT role FROM Utilisateurs WHERE nom_utilisateur = ? AND mot_de_passe = ?",
            (username, hashed_password))
        return user[0] if user else None