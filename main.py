import customtkinter as ctk
from tkinter import messagebox
import database
import re

# Thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TaskyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("Tasky")
        self.geometry("400x500")
        
        # Initialisation de la BDD
        database.init_bd()
        
        # ID de l'utilisateur connecté
        self.current_user_id, self.current_user_role = None, None

        # Page de connexion
        self.show_login()

    def clear_screen(self):
        """Efface tout le contenu de la fenêtre pour changer de page."""
        for widget in self.winfo_children():
            widget.destroy()

    # ==========================================
    # PAGE 1 : CONNEXION (LOGIN)
    # ==========================================
    def show_login(self):
        self.clear_screen()
        
        ctk.CTkLabel(self, text="Tasky - Login", font=("Arial", 24, "bold")).pack(pady=40)

        self.entry_pseudo = ctk.CTkEntry(self, placeholder_text="Pseudo")
        self.entry_pseudo.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.entry_pass.pack(pady=10)

        # Bouton Connexion appelle la fonction verify_login
        ctk.CTkButton(self, text="Login", command=self.verify_login).pack(pady=10)
        
        # Bouton Inscription appelle show_register
        ctk.CTkButton(self, text="Sign in", fg_color="transparent", border_width=1, command=self.show_register).pack(pady=10)

    def verify_login(self):
        pseudo = self.entry_pseudo.get()
        password = self.entry_pass.get()
        
        user_data = database.login_check(pseudo, password)
        
        if user_data:
            user_id = user_data["id"]
            user_role = user_data["role"]

            self.current_user_id = user_id
            self.current_user_role = user_role

            self.show_tasks()
        else:
            messagebox.showerror("Error", "pseudo or password wrong.")

    # ==========================================
    # PAGE 2 : INSCRIPTION (SIGNIN)
    # ==========================================
    def show_register(self):
        self.clear_screen()
        
        ctk.CTkLabel(self, text="Tasky - Sign in", font=("Arial", 24, "bold")).pack(pady=40)

        self.entry_new_pseudo = ctk.CTkEntry(self, placeholder_text="Choose a pseudo")
        self.entry_new_pseudo.pack(pady=10)

        self.entry_new_pass = ctk.CTkEntry(self, placeholder_text="Choose a password", show="*")
        self.entry_new_pass.pack(pady=10)

        # Bouton Valider appelle register_user
        ctk.CTkButton(self, text="Confirm", fg_color="green", command=self.register_user).pack(pady=10)
        ctk.CTkButton(self, text="Return", fg_color="transparent", command=self.show_login).pack()

    def register_user(self):
        pseudo = self.entry_new_pseudo.get()
        password = self.entry_new_pass.get()

        regex = r"^(?=.*[A-Z])(?=.*\d).{12,}$"

        if not re.match(regex, password):
            messagebox.showerror("Error", "Password must be at least 12 characters long, contain at least one uppercase letter and one digit.")
            return

        if pseudo and password:
            success = database.user_signin(pseudo, password)
            if success:
                messagebox.showinfo("Success", "Account created ! Please log in.")
                self.show_login()
            else:
                messagebox.showerror("Error", "This pseudo is already used.")
        else:
            messagebox.showwarning("Warning", "Please fill in all fields.")

    # ==========================================
    # PAGE 3 : LISTE DES TÂCHES
    # ==========================================
    def show_tasks(self):
        self.clear_screen()

        welcome_text = "Tasky - My Tasks"

        if self.current_user_role == "admin":
            welcome_text = "Administrator Mode"
        
        ctk.CTkLabel(self, text=welcome_text, font=("Arial", 20, "bold")).pack(pady=20)

        ctk.CTkButton(self, text="Logout", fg_color="#555555", hover_color="#333333", width=100, command=self.logout_action).pack(pady=5)

        if self.current_user_role == "admin":
            ctk.CTkButton(self, text="Manage Users", fg_color="#ff8c00", hover_color="#cc7000", command=self.show_users_admin).pack(pady=5)

       # Zone d'ajout 
        self.entry_task = ctk.CTkEntry(self, placeholder_text="New task...")
        self.entry_task.pack(pady=5)
        
        # On récupère les catégories depuis la BDD : [(1, 'Travail'), (2, 'Personnel'), ...]
        self.cat_data = database.get_categories() 
        # On extrait juste les noms pour l'affichage dans le menu
        cat_names = [cat[1] for cat in self.cat_data] if self.cat_data else ["Aucune"]
        
        self.menu_category = ctk.CTkOptionMenu(self, values=cat_names)
        self.menu_category.pack(pady=5)
        # ----------------------------------------------------

        # Appel à add_new_task
        ctk.CTkButton(self, text="Add", command=self.add_new_task).pack(pady=5)
 
        self.scrollter = ctk.CTkScrollableFrame(self, width=300, height=300)
        self.scrollter.pack(pady=20)
        
        self.load_tasks_list()

    def add_new_task(self):
        title = self.entry_task.get()
        selected_cat_name = self.menu_category.get()
        
        # On cherche l'ID qui correspond au nom sélectionné
        category_id = None
        for cat in self.cat_data:
            if cat[1] == selected_cat_name:
                category_id = cat[0]
                break

        if title and category_id:
            database.add_task(title, self.current_user_id, category_id)
            self.entry_task.delete(0, 'end')
            self.load_tasks_list()

    def load_tasks_list(self):
        # Vider la zone d'affichage
        for widget in self.scrollter.winfo_children():
            widget.destroy()
            
        # Récupèrer les tâches (id, titre, statut)
        tasks = database.get_tasks(self.current_user_id, self.current_user_role)
        
        for t in tasks:
            task_id = t[0]
            title = t[1]
            status = t[2]
            category_name = t[3]
            
            # On formate le texte pour afficher la catégorie entre crochets
            display_text = f"[{category_name}] {title}" if category_name else title
            
            # --- Ligne conteneur ---
            row_frame = ctk.CTkFrame(self.scrollter, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            # --- Checkbox ---
            chk = ctk.CTkCheckBox(
                row_frame, 
                text=display_text,
                command=lambda tid=task_id, st=status: self.toggle_status(tid, st)
            )
            chk.pack(side="left", padx=10)
            if status == 1: chk.select()
                
            # --- Bouton Supprimer ---
            btn_del = ctk.CTkButton(
                row_frame, 
                text="X", 
                width=30, 
                fg_color="#cc0000", 
                hover_color="#aa0000",
                command=lambda tid=task_id: self.delete_task_action(tid)
            )
            btn_del.pack(side="right", padx=5)
            

            # --- Bouton Modifier ---
            btn_edit = ctk.CTkButton(
                row_frame, 
                text="✎",
                width=30, 
                fg_color="#1f6aa5",
                command=lambda tid=task_id: self.edit_task_action(tid)
            )
            btn_edit.pack(side="right", padx=5)


    # Éditer (Ouvre une pop-up)
    def edit_task_action(self, task_id):
        # Boîte de dialogue
        dialog = ctk.CTkInputDialog(text="New title :", title="Edit task")
        
        # Le programme attend que l'utilisateur clique sur OK
        new_title = dialog.get_input()
        
        # Si l'utilisateur a écrit quelque chose (et pas cliqué sur Annuler)
        if new_title:
            database.update_task_title(task_id, new_title)
            self.load_tasks_list()

    # Changer le statut
    def toggle_status(self, task_id, current_status):
        # Si c'était 0, ça devient 1. Si c'était 1, ça devient 0.
        new_status = 1 if current_status == 0 else 0
        database.update_task_status(task_id, new_status)
        # Recharger la liste pour que l'affichage soit synchro
        self.load_tasks_list()

    # Supprimer
    def delete_task_action(self, task_id):
        database.delete_task(task_id)
        self.load_tasks_list()

# ==========================================
    # PAGE 4 : GESTION DES UTILISATEURS (ADMIN)
    # ==========================================
    def show_users_admin(self):
        self.clear_screen()
        
        ctk.CTkLabel(self, text="Admin - Manage Users", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Bouton retour
        ctk.CTkButton(self, text="Return to Tasks", command=self.show_tasks).pack(pady=10)
        
        self.scrollter = ctk.CTkScrollableFrame(self, width=300, height=300)
        self.scrollter.pack(pady=20)
        
        self.load_users_list()

    def load_users_list(self):
        for widget in self.scrollter.winfo_children():
            widget.destroy()
            
        users = database.get_all_users()
        
        for u in users:
            u_id = u[0]
            u_pseudo = u[1]
            u_role = u[2]
            
            row_frame = ctk.CTkFrame(self.scrollter, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            display_text = f"[{u_role.upper()}] {u_pseudo} (ID: {u_id})"
            
            ctk.CTkLabel(row_frame, text=display_text).pack(side="left", padx=10)
            
            # On empêche l'admin de se supprimer lui-même
            if u_id != self.current_user_id:
                btn_del = ctk.CTkButton(
                    row_frame, 
                    text="Delete", 
                    width=50, 
                    fg_color="#cc0000", 
                    hover_color="#aa0000",
                    command=lambda uid=u_id: self.delete_user_action(uid)
                )
                btn_del.pack(side="right", padx=5)

    def delete_user_action(self, user_id):
        # Fenêtre de confirmation avant une action destructrice
        confirm = messagebox.askyesno("Warning", "Delete this user and all their tasks?")
        if confirm:
            database.delete_user_and_data(user_id)
            self.load_users_list() # Recharger la liste

    def logout_action(self):
        # 1. On efface les données de la session en cours
        self.current_user_id = None
        self.current_user_role = None
        
        # 2. On redirige vers la page de connexion
        self.show_login()

if __name__ == "__main__":
    app = TaskyApp()
    app.mainloop()