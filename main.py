import customtkinter as ctk
from tkinter import messagebox
import database
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TaskyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tasky")
        self.geometry("450x600")
        database.init_bd()
        self.current_user_id, self.current_user_role = None, None
        self.show_login()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_screen()
        ctk.CTkLabel(self, text="Tasky - Login", font=("Arial", 24, "bold")).pack(pady=40)
        self.entry_pseudo = ctk.CTkEntry(self, placeholder_text="Pseudo")
        self.entry_pseudo.pack(pady=10)
        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.entry_pass.pack(pady=10)
        ctk.CTkButton(self, text="Login", command=self.verify_login).pack(pady=10)
        ctk.CTkButton(self, text="Sign in", fg_color="transparent", border_width=1, command=self.show_register).pack(pady=10)

    def verify_login(self):
        user_data = database.login_check(self.entry_pseudo.get(), self.entry_pass.get())
        if user_data:
            self.current_user_id, self.current_user_role = user_data["id"], user_data["role"]
            self.show_tasks()
        else:
            messagebox.showerror("Error", "Pseudo or password wrong.")

    def show_register(self):
        self.clear_screen()
        ctk.CTkLabel(self, text="Tasky - Sign in", font=("Arial", 24, "bold")).pack(pady=40)
        self.entry_new_pseudo = ctk.CTkEntry(self, placeholder_text="Choose a pseudo")
        self.entry_new_pseudo.pack(pady=10)
        self.entry_new_pass = ctk.CTkEntry(self, placeholder_text="Choose a password", show="*")
        self.entry_new_pass.pack(pady=10)
        ctk.CTkButton(self, text="Confirm", fg_color="green", command=self.register_user).pack(pady=10)
        ctk.CTkButton(self, text="Return", fg_color="transparent", command=self.show_login).pack()

    def register_user(self):
        pseudo, password = self.entry_new_pseudo.get(), self.entry_new_pass.get()
        if not re.match(r"^(?=.*[A-Z])(?=.*\d).{12,}$", password):
            messagebox.showerror("Error", "12 chars min, 1 Uppercase, 1 Digit.")
            return
        if pseudo and password:
            if database.user_signin(pseudo, password):
                messagebox.showinfo("Success", "Account created!")
                self.show_login()
            else:
                messagebox.showerror("Error", "Pseudo already used.")

    def show_tasks(self):
        self.clear_screen()
        welcome = "Administrator Mode" if self.current_user_role == "admin" else "Tasky - My Tasks"
        ctk.CTkLabel(self, text=welcome, font=("Arial", 20, "bold")).pack(pady=20)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Logout", width=100, command=self.logout_action).pack(side="left", padx=5)
        if self.current_user_role == "admin":
            ctk.CTkButton(btn_frame, text="Users", fg_color="#ff8c00", width=100, command=self.show_users_admin).pack(side="left", padx=5)

        self.entry_task = ctk.CTkEntry(self, placeholder_text="New task...")
        self.entry_task.pack(pady=5)
        
        self.cat_data = database.get_categories()
        cat_names = [cat[1] for cat in self.cat_data]
        self.menu_category = ctk.CTkOptionMenu(self, values=cat_names)
        self.menu_category.pack(pady=5)
        
        ctk.CTkButton(self, text="Add Task", command=self.add_new_task).pack(pady=5)
        self.scrollter = ctk.CTkScrollableFrame(self, width=400, height=300)
        self.scrollter.pack(pady=20, fill="both", expand=True)
        self.load_tasks_list()

    def add_new_task(self):
        title, cat_name = self.entry_task.get(), self.menu_category.get()
        cat_id = next((c[0] for c in self.cat_data if c[1] == cat_name), None)
        if title and cat_id:
            database.add_task(title, self.current_user_id, cat_id)
            self.entry_task.delete(0, 'end')
            self.load_tasks_list()

    def load_tasks_list(self):
        for widget in self.scrollter.winfo_children(): widget.destroy()
        tasks = database.get_tasks(self.current_user_id, self.current_user_role)
        statuts = ["À faire", "En cours", "Annulée", "Terminée"]
        
        for t in tasks:
            tid, title, status, cname = t
            row = ctk.CTkFrame(self.scrollter, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=f"[{cname}] {title}", anchor="w", width=180).pack(side="left", padx=5)
            
            # Menu de statut
            s_var = ctk.StringVar(value=status)
            ctk.CTkOptionMenu(row, values=statuts, variable=s_var, width=100, font=("Arial", 10),
                             command=lambda v, i=tid: database.update_task_status(i, v)).pack(side="left", padx=2)
            
            # Actions
            ctk.CTkButton(row, text="✎", width=30, command=lambda i=tid: self.edit_task_action(i)).pack(side="left", padx=2)
            ctk.CTkButton(row, text="X", width=30, fg_color="#cc0000", command=lambda i=tid: self.delete_task_action(i)).pack(side="left", padx=2)

    def change_status_action(self, task_id, new_status):
        database.update_task_status(task_id, new_status)

    def edit_task_action(self, task_id):
        dialog = ctk.CTkInputDialog(text="New title:", title="Edit")
        new_t = dialog.get_input()
        if new_t:
            database.update_task_title(task_id, new_t)
            self.load_tasks_list()

    def delete_task_action(self, task_id):
        database.delete_task(task_id)
        self.load_tasks_list()

    def show_users_admin(self):
        self.clear_screen()
        ctk.CTkLabel(self, text="Admin - Manage Users", font=("Arial", 20, "bold")).pack(pady=20)
        ctk.CTkButton(self, text="Return", command=self.show_tasks).pack()
        self.scrollter = ctk.CTkScrollableFrame(self, width=400, height=300)
        self.scrollter.pack(pady=20, fill="both", expand=True)
        self.load_users_list()

    def load_users_list(self):
        for widget in self.scrollter.winfo_children(): widget.destroy()
        for u in database.get_all_users():
            uid, upseudo, urole = u
            row = ctk.CTkFrame(self.scrollter)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{upseudo} ({urole})").pack(side="left", padx=10)
            if uid != self.current_user_id:
                ctk.CTkButton(row, text="Delete", fg_color="#cc0000", width=60,
                             command=lambda i=uid: self.delete_user_action(i)).pack(side="right", padx=5)

    def delete_user_action(self, user_id):
        if messagebox.askyesno("Warning", "Delete user and all data?"):
            database.delete_user_and_data(user_id)
            self.load_users_list()

    def logout_action(self):
        self.current_user_id = self.current_user_role = None
        self.show_login()

if __name__ == "__main__":
    app = TaskyApp()
    app.mainloop()