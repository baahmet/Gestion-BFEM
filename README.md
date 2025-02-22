

# 📘 Gestion des Délibérations du BFEM

**Une application Python pour automatiser la gestion des délibérations du Brevet de Fin d'Études Moyennes (BFEM).**

Ce projet est conçu pour simplifier et automatiser le processus de gestion des délibérations du BFEM. Il permet de gérer les candidats, saisir les notes, générer des anonymats, suivre les délibérations, et produire des documents officiels tels que les PV et les relevés de notes. L'application inclut également une gestion des utilisateurs avec des rôles distincts (Jury et Professeur) et une fonctionnalité d'importation de données depuis un fichier Excel.

---

## 📌 Fonctionnalités

- **🔹 Gestion des candidats** : Ajout, modification, suppression et consultation des candidats.
- **🔹 Saisie des notes** : Saisie des notes avec anonymisation pour garantir la confidentialité.
- **🔹 Délibération** : Calcul des résultats selon les règles officielles du BFEM.
- **🔹 Génération de documents** : Production des PV (Procès-Verbaux) et des relevés de notes en format PDF.
- **🔹 Statistiques** : Visualisation des statistiques des résultats (moyennes, taux de réussite, etc.).
- **🔹 Gestion des repêchages** : Suivi des candidats en repêchage.
- **🔹 Importation de données** : Importation des données des candidats depuis un fichier Excel.
- **🔹 Gestion des utilisateurs** :
  - **Jury** : Accès complet à toutes les fonctionnalités. Le jury peut :
    - Créer des comptes pour les professeurs.
    - Modifier son propre compte.
    - Configurer les paramètres du jury.
  - **Professeur** : Accès limité à la saisie des notes et à la consultation des candidats.
- **🔹 Paramétrage du jury** : Configuration des paramètres du jury (nombre de membres, règles de délibération, etc.).

---

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- Pip (gestionnaire de paquets Python)

### Étapes d'installation
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/ton-utilisateur/Gestion-BFEM.git
   cd Gestion-BFEM
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration initiale** :
   - Un compte **Jury** par défaut est créé avec les identifiants suivants :
     - **Nom d'utilisateur** : `admin`
     - **Mot de passe** : `admin123`
   - Vous pouvez modifier ces identifiants après la première connexion.

4. Lancez l'application :
   ```bash
   python main.py
   ```

---

## 🛠 Utilisation

### Interface Graphique
L'application dispose d'une interface graphique intuitive pour :
- Gérer les candidats.
- Saisir les notes.
- Générer les anonymats.
- Suivre les délibérations.
- Produire les PV et relevés de notes.
- Importer des données depuis un fichier Excel.
- Gérer les utilisateurs (Jury et Professeur).

### Rôles et Accès
- **Jury** : Accès complet à toutes les fonctionnalités. Le jury peut :
  - Créer des comptes pour les professeurs.
  - Modifier son propre compte.
  - Configurer les paramètres du jury.
- **Professeur** : Accès limité à la saisie des notes et à la consultation des candidats.

---

## 📂 Structure du Projet

```
Gestion-BFEM/
├── database/               # Fichiers de base de données
├── views/                  # Interfaces graphiques
├── main.py                 # Point d'entrée de l'application
├── requirements.txt        # Dépendances du projet
├── README.md               # Documentation du projet
├── config.json             # Fichier de configuration (stocke les identifiants par défaut)
└── Guide_Utilisateur.pdf   # Guide d'utilisation
```

---

### Fichier de Configuration (`config.json`)
Le fichier `config.json` est utilisé pour stocker les identifiants par défaut du jury. Voici un exemple de contenu :

```json
{
  "default_username": "admin",
  "default_password": "admin123"
}
```

#### Comment créer le fichier `config.json` :
1. Créez un fichier `config.json` à la racine du projet.
2. Ajoutez le contenu JSON ci-dessus.
3. L'application utilisera ces identifiants pour la connexion initiale.

---

## 📄 Documentation

- **Guide Utilisateur** : Consultez le fichier `Guide_Utilisateur.pdf` pour une prise en main détaillée de l'application.
- **Code Source** : Le code est documenté avec des commentaires pour faciliter la compréhension et la maintenance.

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer :

1. **Signaler un bug** : Ouvrez une [issue](https://github.com/ton-utilisateur/Gestion-BFEM/issues) en décrivant le problème.
2. **Proposer une amélioration** : Soumettez une [pull request](https://github.com/ton-utilisateur/Gestion-BFEM/pulls) avec vos modifications.
3. **Améliorer la documentation** : Aidez-nous à améliorer le `README.md` ou le guide utilisateur.

---

## 📜 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👥 Créateurs

- **Mohamet Lamine Ba**
- **Mouhamadou Al Bachir Ba**

---

## 📞 Contact

Pour toute question ou suggestion, contactez-nous à [baahmet126@gmail.com](mailto:baahmet126@gmail.com).

---

