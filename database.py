import sqlite3
import bcrypt

DB_NAME = "Tasky.db"

def init_bd():
    # Création du fichier et curseur
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Activation PRAGMA pour gérer les DELETE en cascade ou liens FK
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Table Users (Standard de stockage avec rôles)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pseudo TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')

    # Table Catégories (Référentiel fixe)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Table Tâches (Lien vers User et Catégorie)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'À faire',
            user_id INTEGER,
            category_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # Table d'Audit (Traçabilité des accès pour la cybersécurité)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            action TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Insertion des catégories si vide
    cursor.execute("SELECT count(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO categories (name) VALUES (?)", 
                           [('Travail',), ('Personnel',), ('Urgent',), ('Études',)])

    # Création du compte Admin avec hash Bcrypt (Salage auto)
    cursor.execute("SELECT * FROM users WHERE pseudo = 'admin'")
    if not cursor.fetchone():
        pwd_admin = bcrypt.hashpw("Admin123456789!".encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (pseudo, password, role) VALUES (?, ?, ?)", 
                       ('admin', pwd_admin, 'admin'))

    conn.commit()
    conn.close()

def connect_db():
    # Helper pour ouvrir une connexion
    return sqlite3.connect(DB_NAME)

def user_signin(pseudo, password):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        # Hachage sécurisé du mot de passe
        password_bytes = password.encode('utf-8')
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        cursor.execute("INSERT INTO users (pseudo, password) VALUES (?, ?)", (pseudo, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_check(pseudo, password):
    conn = connect_db()
    cursor = conn.cursor()
    # Requête paramétrée contre l'injection SQL
    cursor.execute("SELECT id, pseudo, password, role FROM users WHERE pseudo=?", (pseudo,))
    resultat = cursor.fetchone()
    
    if resultat:
        user_id, pseudo_db, hashed_in_db, role_db = resultat
        # Vérification sécurisée du hash
        if bcrypt.checkpw(password.encode('utf-8'), hashed_in_db):
            cursor.execute("INSERT INTO audit_logs (action, user_id) VALUES (?, ?)", ("Connexion réussie", user_id))
            conn.commit()
            conn.close()
            return {"id": user_id, "pseudo": pseudo_db, "role": role_db}
        else:
            # Log de l'échec (audit)
            cursor.execute("INSERT INTO audit_logs (action, user_id) VALUES (?, ?)", ("Échec connexion (MDP incorrect)", user_id))
            conn.commit()
            conn.close()
            return None
    else:
        cursor.execute("INSERT INTO audit_logs (action, user_id) VALUES (?, NULL)", (f"Pseudo inconnu : {pseudo}",))
        conn.commit()
        conn.close()
        return None

def get_categories():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    conn.close()
    return categories

def add_task(title, user_id, category_id):
    conn = connect_db()
    cursor = conn.cursor()
    # On fige le statut par défaut à l'insertion
    cursor.execute("INSERT INTO tasks (title, user_id, category_id, status) VALUES (?, ?, ?, 'À faire')", 
                   (title, user_id, category_id))
    conn.commit()
    conn.close()

def get_tasks(user_id, user_role):
    conn = connect_db()
    cursor = conn.cursor()
    # Jointure pour récupérer le nom de la catégorie au lieu de son ID
    if user_role == "admin":
        query = "SELECT t.id, t.title, t.status, c.name FROM tasks t LEFT JOIN categories c ON t.category_id = c.id"
        cursor.execute(query)
    else:
        query = "SELECT t.id, t.title, t.status, c.name FROM tasks t LEFT JOIN categories c ON t.category_id = c.id WHERE t.user_id = ?"
        cursor.execute(query, (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_task_title(task_id, new_title):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (new_title, task_id))
    conn.commit()
    conn.close()

def update_task_status(task_id, new_status):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, pseudo, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def delete_user_and_data(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    # Suppression manuelle des dépendances (Cascade manuelle)
    cursor.execute("DELETE FROM audit_logs WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()