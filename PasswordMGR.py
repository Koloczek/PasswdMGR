from CTkListbox import *
import customtkinter as ctk
import tkinter.messagebox as messagebox
import hashlib
import os
import sqlite3
import time
import random
import string
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

def center_window(win, window_width=400, window_height=200, topmost=False):
    win.resizable(False, False)

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    win.geometry(f"{window_width}x{window_height}+{x}+{y}")

    if topmost:
        win.lift()
        win.attributes("-topmost", True)

class SelectListBox(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Create a CTkListbox widget
        self.listbox = CTkListbox(self, **kwargs)  # Set height and width as per your need
        self.listbox.pack(padx=10, pady=10, fill="both", expand=True)

        self.populate_listbox()

    def populate_listbox(self):
        # Clear the existing items in the listbox
        self.listbox.delete(0, ctk.END)

        # Fetch data from the database and populate the listbox
        cursor.execute("SELECT website, username FROM passwords")
        results = cursor.fetchall()

        if results:
            for website, username in results:
                self.listbox.insert(ctk.END, f"Website: {website}, User: {username}")
        else:
            self.listbox.insert(ctk.END, "No entries found")

    def refresh_listbox(self):
        """Refresh the listbox data after adding a new entry."""
        self.populate_listbox()


class CTkMessageBox(ctk.CTkToplevel):
    def __init__(self, title, message, button_text="OK"):
        super().__init__()
        self.title(title)

        self.geometry("300x150")
        #self.resizable(False, False)

        self.label_message = ctk.CTkLabel(self, text=message, wraplength=250, font=("Arial", 12))
        self.label_message.pack(pady=20, padx=10)

        self.button = ctk.CTkButton(self, text=button_text, command=self.close)
        self.button.pack(pady=10)

        center_window(self,300, 150, topmost=True)
        self.grab_set()  # Make the messagebox modal
        self.focus_set()


    def close(self):
        self.destroy()


class SetMasterPasswordWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        center_window(self, 400, 250)
        self.title("Set Master Password")

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
            CTkMessageBox("Error", "Fields cannot be empty!")
            return
        if p1 != p2:
            CTkMessageBox("Error", "Passwords do not match!")
            return

        hashed = hash_master_password(p1)
        try:
            cursor.execute("""
                INSERT INTO master_password (id, password_hash, attempt_count, lock_until)
                VALUES (?, ?, ?, ?)
            """, (1, hashed, 0, None))
            conn.commit()

            CTkMessageBox("Success", "Master Password has been set!")
            self.destroy()
            main_app = MainApp()
            main_app.mainloop()
        except Exception as e:
            CTkMessageBox("Error", f"Failed to save Master Password: {e}")

    def on_closing(self):
        conn.close()
        self.destroy()
        exit(0)

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login - Master Password")
        center_window(self, 400, 200, topmost=True)

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
            CTkMessageBox("Error", "Password cannot be empty!")
            return

        cursor.execute("SELECT password_hash, attempt_count, lock_until FROM master_password LIMIT 1")
        result = cursor.fetchone()
        if not result:
            CTkMessageBox("Error", "No Master Password found in DB!")
            conn.close()
            self.destroy()
            exit(0)

        stored_hash, attempt_count, lock_until = result

        now = time.time()
        if lock_until is not None and now < lock_until:
            remaining = int(lock_until - now)
            mins = remaining // 60
            secs = remaining % 60
            CTkMessageBox(
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

            CTkMessageBox("Success", "Login successful!")
            time.sleep(1)
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
                CTkMessageBox(
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
                CTkMessageBox("Error", f"Invalid Master Password! Attempts left: {attempts_left}")

    def on_closing(self):
        conn.close()
        self.destroy()
        exit(0)

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Password Manager - SQLite")
        center_window(self, 900, 500)


        self.remaining_time = 180  # 3 minuty w sekundach
        self.countdown_label = ctk.CTkLabel(self, text=f"Session time left: {self.remaining_time}s")

        self.bind("<Motion>", self.reset_inactivity_timer)
        self.bind("<Key>", self.reset_inactivity_timer)

        self.update_timer()

        self.grid_columnconfigure(0, weight=1)  # listbox
        self.grid_columnconfigure(1, weight=0)  # label
        self.grid_columnconfigure(2, weight=1)  # entry
        for r in range(12):
            self.grid_rowconfigure(r, weight=0)
        self.grid_rowconfigure(11, weight=1)

        # Lewa strona
        self.listbox = SelectListBox(self, width=250)
        self.listbox.grid(row=0, column=0, rowspan=12, sticky="nsew", padx=10, pady=10)

        # Prawa strona
        # Wiersz 0
        ctk.CTkLabel(self, text="WEBSITE:").grid(row=0, column=1, padx=10, pady=5, sticky="e")
        self.entry_site = ctk.CTkEntry(self)
        self.entry_site.grid(row=0, column=2, padx=10, pady=5, sticky="we")

        # Wiersz 1
        ctk.CTkLabel(self, text="USERNAME:").grid(row=1, column=1, padx=10, pady=5, sticky="e")
        self.entry_username = ctk.CTkEntry(self)
        self.entry_username.grid(row=1, column=2, padx=10, pady=5, sticky="we")

        # Wiersz 2
        ctk.CTkLabel(self, text="PASSWORD:").grid(row=2, column=1, padx=10, pady=5, sticky="e")
        self.entry_password = ctk.CTkEntry(self)
        self.entry_password.grid(row=2, column=2, padx=10, pady=5, sticky="we")

        btn_add = ctk.CTkButton(self, text="Add", command=self.add_password)
        btn_add.grid(row=3, column=1, columnspan=2, padx=15, pady=8, sticky="we")

        btn_get = ctk.CTkButton(self, text="Get", command=self.get_password)
        btn_get.grid(row=4, column=1, columnspan=2, padx=15, pady=8, sticky="we")

        btn_delete = ctk.CTkButton(self, text="Delete", command=self.delete_entry)
        btn_delete.grid(row=5, column=1, columnspan=2, padx=15, pady=8, sticky="we")

        btn_copy = ctk.CTkButton(self, text="Copy to Clipboard", command=self.copy_password)
        btn_copy.grid(row=6, column=1, columnspan=2, padx=15, pady=8, sticky="we")

        ctk.CTkLabel(self, text="Generate Password:").grid(row=7, column=1, columnspan=2, pady=(20, 5), sticky="we")

        frame = ctk.CTkFrame(self)
        frame.grid(row=8, column=1, columnspan=2, padx=10, pady=5, sticky="we")

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        self.label_length = ctk.CTkLabel(frame, text="Length:")
        self.label_length.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="e")

        self.suwak_dlugosc = ctk.CTkSlider(frame, from_=4, to=32, number_of_steps=28, command=self.update_label)
        self.suwak_dlugosc.set(12)
        self.suwak_dlugosc.grid(row=0, column=1, padx=(5, 5), pady=5, sticky="we")

        self.label_value = ctk.CTkLabel(frame, text="12")
        self.label_value.grid(row=0, column=2, padx=(5, 10), pady=5, sticky="w")

        # Pole na wygenerowane hasło przesuwamy do row=9
        self.generated_password = ctk.CTkEntry(self)
        self.generated_password.grid(row=9, column=1, columnspan=2, pady=5, padx=10, sticky="we")

        # Przycisk "Generate" przesuwamy do row=10
        btn_generate = ctk.CTkButton(self, text="Generate", command=self.generate_password)
        btn_generate.grid(row=10, column=1, columnspan=2, pady=10, padx=10, sticky="we")

        self.countdown_label.grid(row=11, column=1, columnspan=2, sticky="e", padx=5, pady=5)

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
            CTkMessageBox("Session Timeout", "Your session has expired. Please re-enter your Master Password.")
            self.destroy()

            # Otwieramy ponownie okno logowania
            login_window = LoginWindow()
            login_window.mainloop()

    def update_label(self, value):
        self.label_value.configure(text=str(int(float(value))))

    def generate_password(self):

        dlugosc = int(self.suwak_dlugosc.get())
        litery = string.ascii_letters
        cyfry = string.digits
        znaki_specjalne = string.punctuation

        haslo = [
            random.choice(litery),
            random.choice(cyfry),
            random.choice(znaki_specjalne),
        ]
        wszystkie_znaki = litery + cyfry + znaki_specjalne
        haslo += random.choices(wszystkie_znaki, k=dlugosc - len(haslo))
        random.shuffle(haslo)

        self.generated_password.delete(0, ctk.END)
        self.generated_password.insert(0, "".join(haslo))

    def validate_input(self, website, username, password):
        if not website or not username or not password:
            CTkMessageBox("Error", "Fields cannot be empty!")
            return False
        if website == username == password:
            CTkMessageBox("Error", "Website, Username and Password cannot all be identical!")
            return False

        cursor.execute("SELECT id FROM passwords WHERE website=? AND username=?", (website, username))
        existing = cursor.fetchone()
        if existing:
            CTkMessageBox("Error", "Entry with this WEBSITE and USERNAME already exists!")
            return False
        return True


    def refresh_listbox(self):
        """Method to refresh the listbox with the latest data from the database"""
        # Fetch data from the database
        try:
            cursor.execute("SELECT website, username FROM passwords")
            results = cursor.fetchall()

            # Clear the listbox
            self.listbox.listbox.delete(0, ctk.END)

            # Add the fetched data to the listbox
            for website, username in results:
                list_item = f"Website: {website}, User: {username}"
                self.listbox.listbox.insert(ctk.END, list_item)
        except Exception as e:
            CTkMessageBox("Error", f"Error refreshing list: {e}")


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
            CTkMessageBox("Success", "Password added!")

            # Refresh the listbox after adding a new entry
            self.refresh_listbox()

        except Exception as e:
            CTkMessageBox("Error", f"Error adding record: {e}")

    def get_password(self):
        # Get the selected item from the listbox
        selected_item = self.listbox.listbox.get(self.listbox.listbox.curselection())

        if not selected_item:
            CTkMessageBox("Error", "No item selected from the list!")
            return

        # Extract website and username from the selected item
        try:
            website, username = selected_item.replace("Website: ", "").split(", User: ")
        except ValueError:
            CTkMessageBox("Error", "Invalid item selected. Could not parse website and username.")
            return

        # Fetch the encrypted password from the database
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
                CTkMessageBox("Password", msg)
            else:
                CTkMessageBox("Error", "No password found for given WEBSITE and USERNAME")
        except Exception as e:
            CTkMessageBox("Error", f"Error retrieving password: {e}")

    def copy_password(self):
        # Podobnie jak w get_password(), najpierw sprawdzamy zaznaczenie
        selected_item = self.listbox.listbox.get(self.listbox.listbox.curselection())

        if not selected_item:
            CTkMessageBox("Error", "No item selected from the list!")
            return

        try:
            # Wyciągamy website i username
            website, username = selected_item.replace("Website: ", "").split(", User: ")
        except ValueError:
            CTkMessageBox("Error", "Invalid item selected. Could not parse website and username.")
            return

        # Pobieramy zaszyfrowane hasło z bazy
        try:
            cursor.execute(
                "SELECT password FROM passwords WHERE website=? AND username=?",
                (website, username)
            )
            result = cursor.fetchone()
            if result:
                encrypted_pass = result[0]
                decrypted_pass = decrypt_password(encrypted_pass)

                # Kopiujemy odszyfrowane hasło do schowka
                # (w tkinter: self.clipboard_clear(); self.clipboard_append())
                self.clipboard_clear()
                self.clipboard_append(decrypted_pass)

                CTkMessageBox("Clipboard", "Password copied to clipboard!")
            else:
                CTkMessageBox("Error", "No password found for the given WEBSITE and USERNAME.")
        except Exception as e:
            CTkMessageBox("Error", f"Error retrieving password: {e}")


    def delete_entry(self):
        # Get the selected item from the listbox
        selected_item = self.listbox.listbox.get(self.listbox.listbox.curselection())

        if not selected_item:
            CTkMessageBox("Error", "No item selected from the list!")
            return

        # Extract website and username from the selected item
        try:
            website, username = selected_item.replace("Website: ", "").split(", User: ")
        except ValueError:
            CTkMessageBox("Error", "Invalid item selected. Could not parse website and username.")
            return



        # Delete the corresponding entry from the database
        try:
            cursor.execute(
                "DELETE FROM passwords WHERE website=? AND username=?",
                (website, username)
            )
            conn.commit()

            if cursor.rowcount > 0:
                # If the entry was deleted from the database, remove it from the listbox
                self.listbox.listbox.delete(self.listbox.listbox.curselection())
                CTkMessageBox("Success", f"Deleted entry for {username} at {website}")
            else:
                CTkMessageBox("Error", "No entry found to delete for the given WEBSITE and USERNAME")
        except Exception as e:
            CTkMessageBox("Error", f"Error deleting entry: {e}")

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
