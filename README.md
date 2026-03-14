# Tasky - Gestionnaire de Tâches

Tasky est une application de bureau (Client Lourd) développée en Python permettant la gestion de tâches quotidiennes. Ce projet a été réalisé dans le cadre de l'épreuve E6 du BTS SIO.

## Fonctionnalités

L'application implémente un cycle CRUD complet et la gestion multi-utilisateurs locale :

* **Authentification :** Système d'inscription et de connexion. Les données de chaque utilisateur sont isolées.
* **Création :** Ajout de nouvelles tâches associées à l'utilisateur connecté.
* **Lecture :** Affichage de la liste des tâches avec persistance des données.
* **Mise à jour :** Modification du statut (À faire / Fait) et édition du titre de la tâche.
* **Suppression :** Retrait définitif d'une tâche de la base de données.
* **Persistance :** Sauvegarde automatique dans une base de données locale SQLite.

## Environnement Technique

* **Langage :** Python 3.x
* **Interface Graphique :** CustomTkinter (Wrapper moderne de Tkinter)
* **Base de Données :** SQLite3 (Intégré à Python)
* **Déploiement :** PyInstaller (Compilation en exécutable Windows)

## Architecture du Code

Le projet suit une architecture modulaire séparant la logique métier de l'interface utilisateur :

* **main.py (Frontend) :** Gère l'affichage, la navigation entre les vues et les interactions utilisateur.
* **database.py (Backend) :** Contient la logique d'accès aux données, les requêtes préparées et la gestion des transactions.

## Installation et Exécution (Code Source)

Prérequis : Python doit être installé sur la machine.

1.  Cloner le dépôt :
    ```bash
    git clone https://github.com/zarathmgd/Tasky.git
    cd Tasky
    ```

2.  Installer les dépendances nécessaires :
    ```bash
    pip install -r requirements.txt
    ```

3.  Lancer l'application :
    ```bash
    python main.py
    ```

## Utilisation de l'exécutable (Windows)

Une version compilée autonome est disponible pour le déploiement.

1.  Accédez à la section **Releases** de ce dépôt.
2.  Téléchargez le fichier **Tasky.exe**.
3.  Lancez l'application. Une base de données vide sera automatiquement créée.

## Auteur

Projet développé par [Ton Prénom] [Ton Nom] - BTS SIO.
