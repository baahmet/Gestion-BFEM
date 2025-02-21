import sqlite3
import hashlib

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.initialize_db()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def execute_query(self, query, params=()):
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return cursor

    def fetch_all(self, query, params=()):
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query, params=()):
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def initialize_db(self):
        # Créer la table Utilisateurs si elle n'existe pas
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Utilisateurs (
                    id_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_utilisateur TEXT UNIQUE NOT NULL,
                    mot_de_passe TEXT NOT NULL,
                    role TEXT CHECK (role IN ('Jury', 'Professeur')) NOT NULL
                )
            """)
            connection.commit()

        # Vérifier si un utilisateur existe déjà
        cursor = self.execute_query("SELECT COUNT(*) FROM Utilisateurs")
        if cursor.fetchone()[0] == 0:
            # Ajouter un utilisateur administrateur par défaut avec un mot de passe haché
            hashed_password = self.hash_password("admin123")
            self.execute_query(
                "INSERT INTO Utilisateurs (nom_utilisateur, mot_de_passe, role) VALUES (?, ?, ?)",
                ("admin", hashed_password, "Jury")
            )
            print("Utilisateur administrateur ajouté : admin / admin123")

    @staticmethod
    def hash_password(password):
        """Hache un mot de passe avec SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()