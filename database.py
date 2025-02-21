import sqlite3
import hashlib

def obtenir_jury_connecte():
    """ Vérifie si un utilisateur Jury est connecté et retourne son ID et son nom. """
    conn = sqlite3.connect("bfem_db.sqlite")
    cur = conn.cursor()
    cur.execute("SELECT id_utilisateur, nom_utilisateur FROM Utilisateurs WHERE role = 'Jury' LIMIT 1")
    utilisateur = cur.fetchone()
    conn.close()
    print("🔍 Étape Debug - Utilisateurs Jury trouvés :", utilisateur)
    return utilisateur if utilisateur else None

def hash_password(password):
    """Hache un mot de passe avec SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_database():
    connection = sqlite3.connect("Bfem_db.sqlite")
    cursor = connection.cursor()

    # Activer les clés étrangères
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Utilisateurs (
            id_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_utilisateur TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL,
            role TEXT CHECK (role IN ('Jury', 'Professeur')) NOT NULL
        )
    ''')

    # Vérifier si un utilisateur existe déjà
    cursor.execute("SELECT COUNT(*) FROM Utilisateurs")
    if cursor.fetchone()[0] == 0:
        # Ajouter un utilisateur administrateur par défaut avec un mot de passe haché
        hashed_password = hash_password("admin123")  # Hacher le mot de passe
        cursor.execute("INSERT INTO Utilisateurs (nom_utilisateur, mot_de_passe, role) VALUES (?, ?, ?)",
                       ("admin", hashed_password, "Jury"))
        print("Utilisateur administrateur ajouté : admin / admin123")

    # Table du paramétrage du jury
    cursor.execute('''CREATE TABLE IF NOT EXISTS Parametres_Jury (
            id_jury INTEGER PRIMARY KEY AUTOINCREMENT,
            id_utilisateur INTEGER NOT NULL,
            region TEXT NOT NULL,
            ief TEXT NOT NULL,
            localite TEXT NOT NULL,
            centre_examen TEXT NOT NULL,
            president_jury TEXT NOT NULL,
            telephone TEXT NOT NULL,
            FOREIGN KEY (id_utilisateur) REFERENCES Utilisateurs(id_utilisateur) ON DELETE CASCADE
        )
        ''')

    # Table des candidats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Candidats (
            id_candidat INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_table INTEGER UNIQUE NOT NULL,
            prenom TEXT NOT NULL,
            nom TEXT NOT NULL,
            date_naissance DATE NOT NULL,
            lieu_naissance TEXT NOT NULL,
            sexe CHAR(1) CHECK (sexe IN ('M', 'F')),
            type_candidat TEXT,
            etablissement TEXT,
            nationalite TEXT NOT NULL,
            choix_epr_facultative BOOLEAN NOT NULL,
            epreuve_facultative TEXT CHECK (epreuve_facultative IN ('Neutre', 'COUTURE', 'DESSIN', 'MUSIQUE')),
            aptitude_sportive BOOLEAN NOT NULL
        )
    ''')

    # Table Anonymats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Anonymats (
        id_anonymat INTEGER PRIMARY KEY AUTOINCREMENT,
        id_candidat INTEGER UNIQUE NOT NULL,
        numero_anonymat INTEGER UNIQUE NOT NULL,
        tour INTEGER CHECK (tour IN (1, 2)) NOT NULL,
        FOREIGN KEY (id_candidat) REFERENCES Candidats(id_candidat) ON DELETE CASCADE
    )
    ''')

    # Table du livret scolaire
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Livret_Scolaire (
            id_livret INTEGER PRIMARY KEY AUTOINCREMENT,
            id_candidat INTEGER NOT NULL,
            nombre_de_fois INTEGER CHECK (nombre_de_fois >= 1),
            moyenne_6e REAL CHECK (moyenne_6e BETWEEN 0 AND 20),
            moyenne_5e REAL CHECK (moyenne_5e BETWEEN 0 AND 20),
            moyenne_4e REAL CHECK (moyenne_4e BETWEEN 0 AND 20),
            moyenne_3e REAL CHECK (moyenne_3e BETWEEN 0 AND 20),
            moyenne_cycle REAL CHECK (moyenne_cycle BETWEEN 0 AND 20),
            FOREIGN KEY (id_candidat) REFERENCES Candidats(id_candidat) ON DELETE CASCADE
        )
    ''')

    # Table des notes (1er et 2nd tour)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Notes_Tour1 (
        id_note INTEGER PRIMARY KEY AUTOINCREMENT,
        id_candidat INTEGER NOT NULL,
        compo_francais REAL CHECK (compo_francais BETWEEN 0 AND 20),
        dictee REAL CHECK (dictee BETWEEN 0 AND 20),
        etude_de_texte REAL CHECK (etude_de_texte BETWEEN 0 AND 20),
        instruction_civique REAL CHECK (instruction_civique BETWEEN 0 AND 20),
        histoire_geographie REAL CHECK (histoire_geographie BETWEEN 0 AND 20),
        mathematiques REAL CHECK (mathematiques BETWEEN 0 AND 20),
        pc_lv2 REAL CHECK (pc_lv2 BETWEEN 0 AND 20),
        svt REAL CHECK (svt BETWEEN 0 AND 20),
        anglais_ecrit REAL CHECK (anglais_ecrit BETWEEN 0 AND 20),
        anglais_oral REAL CHECK (anglais_oral BETWEEN 0 AND 20),
        -- EPS et Épreuve facultative uniquement si applicable (RM15)
        eps REAL CHECK (eps BETWEEN 0 AND 20),
        epreuve_facultative REAL CHECK (epreuve_facultative BETWEEN 0 AND 20),
        anonymat TEXT UNIQUE NOT NULL,
        FOREIGN KEY (id_candidat) REFERENCES Candidats(id_candidat) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Notes_Tour2 (
        id_note INTEGER PRIMARY KEY AUTOINCREMENT,
        id_candidat INTEGER NOT NULL,
        francais_2nd_tour REAL CHECK (francais_2nd_tour BETWEEN 0 AND 20),
        mathematiques_2nd_tour REAL CHECK (mathematiques_2nd_tour BETWEEN 0 AND 20),
        pc_lv2_2nd_tour REAL CHECK (pc_lv2_2nd_tour BETWEEN 0 AND 20),
        anonymat TEXT UNIQUE NOT NULL,
        FOREIGN KEY (id_candidat) REFERENCES Candidats(id_candidat) ON DELETE CASCADE
    )
    ''')

    # Table de délibération
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Deliberation (
        id_deliberation INTEGER PRIMARY KEY AUTOINCREMENT,
        id_candidat INTEGER UNIQUE NOT NULL,
        points_tour1 REAL NOT NULL,
        points_tour2 REAL,
        statut TEXT CHECK (statut IN ('Admis', 'Échec', '2nd Tour', 'Repêchage')),
        FOREIGN KEY (id_candidat) REFERENCES Candidats(id_candidat) ON DELETE CASCADE
    )
    ''')

    # Commit et fermeture
    connection.commit()
    connection.close()
    print("Base de données et tables créées avec succès !")

# Exécution du script
if __name__ == "__main__":
    create_database()
