import customtkinter as ctk
import tkinter.messagebox as messagebox
import hashlib
import os
import sqlite3
import time
from cryptography.fernet import Fernet

DB_FILENAME = "password_manager.db"

def hash_master_password(password: str) -> str:
    return hashlib.sha512(password.encode()).hexdigest()

def load_key():
    if os.path.exists("secret.key"):
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    return key

key = load_key()
cipher_suite = Fernet(key)

def encrypt_password(plain_text_password: str) -> str:
    return cipher_suite.encrypt(plain_text_password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

def initialize_database():
    first_run = False

    if not os.path.exists(DB_FILENAME):
        first_run = True

    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    if first_run:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_password (
                id INTEGER PRIMARY KEY,
                password_hash TEXT,
                attempt_count INTEGER DEFAULT 0,
                lock_until REAL
            )
        """)
        conn.commit()

    return conn, cursor

conn, cursor = initialize_database()

cursor.execute("SELECT password_hash FROM master_password LIMIT 1")
row = cursor.fetchone()
MASTER_PASSWORD_SET = True if (row and row[0]) else False

class SetMasterPasswordWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Set Master Password")
        self.geometry("400x250")

        ctk.CTkLabel(self, text="Set your new Master Password:").pack(pady=(10, 5))
        ctk.CTkLabel(self, text="Enter Master Password:").pack()
        self.entry_pass1 = ctk.CTkEntry(self, show="*")
        self.entry_pass1.pack(pady=5)

        ctk.CTkLabel(self, text="Confirm Master Password:").pack()
        self.entry_pass2 = ctk.CTkEntry(self, show="*")
        self.entry_pass2.pack(pady=5)

        btn_set = ctk.CTkButton(self, text="Set Master Password", command=self.set_master_password)
        btn_set.pack(pady=(10, 5))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_master_password(self):
        p1 = self.entry_pass1.get()
        p2 = self.entry_pass2.get()

        if not p1 or not p2:
            messagebox.showerror("Error", "Fields cannot be empty!")
            return
        if p1 != p2:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        hashed = hash_master_password(p1)
        try:
            cursor.execute("""
                INSERT INTO master_password (id, password_hash, attempt_count, lock_until)
                VALUES (?, ?, ?, ?)
            """, (1, hashed, 0, None))
            conn.commit()

            messagebox.showinfo("Success", "Master Password has been set!")
            self.destroy()
            main_app = MainApp()
            main_app.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save Master Password: {e}")

    def on_closing(self):
        conn.close()
        self.destroy()
        exit(0)

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login - Master Password")
        self.geometry("400x200")

        ctk.CTkLabel(self, text="Enter Master Password:").pack(pady=(15, 5))
        self.entry_master = ctk.CTkEntry(self, show="*")
        self.entry_master.pack(pady=5)

        btn_ok = ctk.CTkButton(self, text="OK", command=self.check_password)
        btn_ok.pack(pady=(10, 5))

        self.entry_master.bind("<Return>", lambda e: self.check_password())
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def check_password(self):
        user_input = self.entry_master.get().strip()
        if not user_input:
            messagebox.showerror("Error", "Password cannot be empty!")
            return

        cursor.execute("SELECT password_hash, attempt_count, lock_until FROM master_password LIMIT 1")
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "No Master Password found in DB!")
            conn.close()
            self.destroy()
            exit(0)

        stored_hash, attempt_count, lock_until = result

        now = time.time()
        if lock_until is not None and now < lock_until:
            remaining = int(lock_until - now)
            mins = remaining // 60
            secs = remaining % 60
            messagebox.showerror(
                "Locked",
                f"Too many failed attempts. Please wait {mins}m {secs}s before next try."
            )
            return

        if hash_master_password(user_input) == stored_hash:
            cursor.execute("""
                UPDATE master_password
                SET attempt_count = 0,
                    lock_until = NULL
                WHERE id = 1
            """)
            conn.commit()

            messagebox.showinfo("Success", "Login successful!")
            self.destroy()
            main_app = MainApp()
            main_app.mainloop()
        else:
            attempt_count += 1
            if attempt_count >= 3:
                lock_time = now + (15 * 60)
                cursor.execute("""
                    UPDATE master_password
                    SET attempt_count = 0,
                        lock_until = ?
                    WHERE id = 1
                """, (lock_time,))
                conn.commit()
                messagebox.showerror(
                    "Locked",
                    "You have entered incorrect password 3 times!\n"
                    "Login is locked for 15 minutes."
                )
            else:
                cursor.execute("""
                    UPDATE master_password
                    SET attempt_count = ?
                    WHERE id = 1
                """, (attempt_count,))
                conn.commit()
                attempts_left = 3 - attempt_count
                messagebox.showerror("Error", f"Invalid Master Password! Attempts left: {attempts_left}")

    def on_closing(self):
        conn.close()
        self.destroy()
        exit(0)

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Password Manager - SQLite")
        self.geometry("500x350")

        self.remaining_time = 180  # 3 minuty w sekundach
        self.countdown_label = ctk.CTkLabel(self, text=f"Session time left: {self.remaining_time}s")
        self.countdown_label.grid(row=5, column=1, sticky="e", padx=5, pady=5)

        # Nasłuchiwanie ruchu myszki, klawiatury -> reset timera
        self.bind("<Motion>", self.reset_inactivity_timer)
        self.bind("<Key>", self.reset_inactivity_timer)

        self.update_timer()

        ctk.CTkLabel(self, text="WEBSITE:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.entry_site = ctk.CTkEntry(self, width=200)
        self.entry_site.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(self, text="USERNAME:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_username = ctk.CTkEntry(self, width=200)
        self.entry_username.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(self, text="PASSWORD:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry_password = ctk.CTkEntry(self, width=200)
        self.entry_password.grid(row=2, column=1, padx=10, pady=5)

        btn_add = ctk.CTkButton(self, text="Add", command=self.add_password)
        btn_add.grid(row=3, column=0, padx=15, pady=8, sticky="we")

        btn_get = ctk.CTkButton(self, text="Get", command=self.get_password)
        btn_get.grid(row=3, column=1, padx=15, pady=8, sticky="we")

        btn_list = ctk.CTkButton(self, text="UserList", command=self.get_list)
        btn_list.grid(row=4, column=0, padx=15, pady=8, sticky="we")

        btn_delete = ctk.CTkButton(self, text="Delete", command=self.delete_entry)
        btn_delete.grid(row=4, column=1, padx=15, pady=8, sticky="we")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def reset_inactivity_timer(self, event=None):
        self.remaining_time = 180 # tu ustawiamy czas

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.countdown_label.configure(text=f"Session time left: {self.remaining_time}s")
            self.after(1000, self.update_timer)
        else:
            # Czas się skończył = automatyczne wylogowanie
            messagebox.showinfo("Session Timeout", "Your session has expired. Please re-enter your Master Password.")
            self.destroy()

            # Otwieramy ponownie okno logowania
            login_window = LoginWindow()
            login_window.mainloop()

    def validate_input(self, website, username, password):
        if not website or not username or not password:
            messagebox.showerror("Error", "Fields cannot be empty!")
            return False
        if website == username == password:
            messagebox.showerror("Error", "Website, Username and Password cannot all be identical!")
            return False

        cursor.execute("SELECT id FROM passwords WHERE website=? AND username=?", (website, username))
        existing = cursor.fetchone()
        if existing:
            messagebox.showerror("Error", "Entry with this WEBSITE and USERNAME already exists!")
            return False
        return True

    def add_password(self):
        website = self.entry_site.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not self.validate_input(website, username, password):
            return

        encrypted_passwd = encrypt_password(password)
        try:
            cursor.execute("""
                INSERT INTO passwords (website, username, password)
                VALUES (?, ?, ?)
            """, (website, username, encrypted_passwd))
            conn.commit()
            messagebox.showinfo("Success", "Password added!")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding record: {e}")

    def get_password(self):
        website = self.entry_site.get().strip()
        username = self.entry_username.get().strip()

        if not website or not username:
            messagebox.showerror("Error", "Please enter both WEBSITE and USERNAME")
            return

        try:
            cursor.execute(
                "SELECT password FROM passwords WHERE website=? AND username=?",
                (website, username)
            )
            result = cursor.fetchone()
            if result:
                encrypted_pass = result[0]
                decrypted_pass = decrypt_password(encrypted_pass)
                msg = f"Password for {username} at {website}:\n{decrypted_pass}"
                messagebox.showinfo("Password", msg)
            else:
                messagebox.showerror("Error", "No password found for given WEBSITE and USERNAME")
        except Exception as e:
            messagebox.showerror("Error", f"Error retrieving password: {e}")

    def get_list(self):
        try:
            cursor.execute("SELECT website, username FROM passwords")
            results = cursor.fetchall()
            if results:
                msg = "List of stored credentials:\n\n"
                for site, user in results:
                    msg += f"Website: {site}, User: {user}\n"
                messagebox.showinfo("UserList", msg)
            else:
                messagebox.showinfo("UserList", "Empty list!")
        except Exception as e:
            messagebox.showerror("Error", f"Error retrieving list: {e}")

    def delete_entry(self):
        website = self.entry_site.get().strip()
        username = self.entry_username.get().strip()

        if not website or not username:
            messagebox.showerror("Error", "Please enter both WEBSITE and USERNAME to delete")
            return

        try:
            cursor.execute(
                "DELETE FROM passwords WHERE website=? AND username=?",
                (website, username)
            )
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", f"Deleted entry for {username} at {website}")
            else:
                messagebox.showerror("Error", "No entry found to delete for given WEBSITE and USERNAME")
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting entry: {e}")

    def on_closing(self):
        conn.close()
        self.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    if not MASTER_PASSWORD_SET:
        app = SetMasterPasswordWindow()
        app.mainloop()
    else:
        login = LoginWindow()
        login.mainloop()
