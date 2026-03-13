import sqlite3
import bcrypt

DB_NAME = "Tasky.db"

def init_bd():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Activation des clés étrangères
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Table Utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pseudo TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')

    # 2. Table Catégories
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # 3. Table Tâches (avec 2 clés étrangères)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status INTEGER DEFAULT 0,
            user_id INTEGER,
            category_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # 4. Table d'Audit (Cybersécurité)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            action TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # --- Insertion de données par défaut ---
    
    # Insérer des catégories de base si la table est vide
    cursor.execute("SELECT count(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO categories (name) VALUES (?)", 
                           [('Travail',), ('Personnel',), ('Urgent',), ('Études',)])

    # Insérer un compte Admin par défaut si inexistant
    cursor.execute("SELECT * FROM users WHERE pseudo = 'admin'")
    if not cursor.fetchone():
        pwd_admin = bcrypt.hashpw("Admin123456789!".encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (pseudo, password, role) VALUES (?, ?, ?)", 
                       ('admin', pwd_admin, 'admin'))

    conn.commit()
    conn.close()
    print("Base de données Tasky initialisée avec succès (4 tables).")

def connect_db():
    # Retourne une connexion active.
    return sqlite3.connect(DB_NAME)

def user_signin(pseudo, password):
    # Crée un nouvel utilisateur.
    try:
        conn = connect_db()
        cursor = conn.cursor()

        password_bytes = password.encode('utf-8')
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        cursor.execute("INSERT INTO users (pseudo, password) VALUES (?, ?)", (pseudo, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Retourne False si le pseudo existe déjà
        return False

def login_check(pseudo, password):
    conn = connect_db()
    cursor = conn.cursor()

    # 1. Récupération des données de l'utilisateur
    cursor.execute("SELECT id, pseudo, password, role FROM users WHERE pseudo=?", (pseudo,))
    resultat = cursor.fetchone()
    
    if resultat:
        user_id, pseudo_db, hashed_in_db, role_db = resultat
        
        # 2. Vérification cryptographique du mot de passe
        if bcrypt.checkpw(password.encode('utf-8'), hashed_in_db):
            # Cas A : Succès
            cursor.execute("INSERT INTO audit_logs (action, user_id) VALUES (?, ?)", ("Connexion réussie", user_id))
            conn.commit()
            conn.close()
            return {"id": user_id, "pseudo": pseudo_db, "role": role_db}
        else:
            # Cas B : Échec (Mauvais mot de passe)
            cursor.execute("INSERT INTO audit_logs (action, user_id) VALUES (?, ?)", ("Échec connexion (mot de passe incorrect)", user_id))
            conn.commit()
            conn.close()
            return None
    else:
        # Cas C : Échec (Pseudo inexistant)
        # On enregistre l'action avec un user_id NULL, en précisant le pseudo tenté dans le texte
        action_texte = f"Échec connexion (pseudo inconnu : {pseudo})"
        cursor.execute("INSERT INTO audit_logs (action, user_id) VALUES (?, NULL)", (action_texte,))
        conn.commit()
        conn.close()
        return None
    
def get_categories():
    # Récupère la liste des catégories pour le menu déroulant
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    conn.close()
    return categories

def add_task(title, user_id, category_id):
    # Ajoute la tâche avec sa clé étrangère category_id
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, user_id, category_id) VALUES (?, ?, ?)", (title, user_id, category_id))
    conn.commit()
    conn.close()

def get_tasks(user_id, user_role):
    # Récupère les tâches AVEC le nom de leur catégorie via une jointure
    conn = connect_db()
    cursor = conn.cursor()

    if user_role == "admin":
        # L'admin voit tout. On utilise LEFT JOIN au cas où une tâche n'aurait pas de catégorie
        query = """
            SELECT tasks.id, tasks.title, tasks.status, categories.name 
            FROM tasks 
            LEFT JOIN categories ON tasks.category_id = categories.id
        """
        cursor.execute(query)
    else:
        # L'utilisateur ne voit que les siennes
        query = """
            SELECT tasks.id, tasks.title, tasks.status, categories.name 
            FROM tasks 
            LEFT JOIN categories ON tasks.category_id = categories.id
            WHERE tasks.user_id = ?
        """
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
    
    # 1. Supprimer les logs de l'utilisateur
    cursor.execute("DELETE FROM audit_logs WHERE user_id = ?", (user_id,))
    # 2. Supprimer les tâches de l'utilisateur
    cursor.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
    # 3. Supprimer l'utilisateur lui-même
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
    conn.commit()
    conn.close()