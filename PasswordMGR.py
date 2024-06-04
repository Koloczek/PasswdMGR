import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
import os

# Function to load or generate the encryption key
def load_key():
    if os.path.exists("secret.key"):
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    return key

# Load the encryption key
key = load_key()
cipher_suite = Fernet(key)

def add():
    WebSite = entrySite.get()
    username = entryName.get()
    password = entryPassword.get()

    if username and password and WebSite:
        encrypted_passwd = cipher_suite.encrypt(password.encode())

        with open("passwords.txt", 'a') as f:
            f.write(f"{WebSite} {username} {encrypted_passwd.decode()}\n")
        messagebox.showinfo("Success", "Password added !!")
    else:
        messagebox.showerror("Error", "Please enter all of the fields")

def decrypt_password(encrypted_passwd):
    return cipher_suite.decrypt(encrypted_passwd.encode()).decode()

def get():
    WebSite = entrySite.get()
    username = entryName.get()

    passwords = {}

    try:
        with open("passwords.txt", 'r') as f:
            for k in f:
                i = k.split(' ')
                if len(i) == 3:
                    web_user_key = (i[0], i[1])  # (Website, Username)
                    passwords[web_user_key] = decrypt_password(i[2].strip())
    except Exception as e:
        print(f"ERROR: {e}")

    if passwords:
        mess = "Your passwords:\n"
        key = (WebSite, username)
        print(f"Looking for key: {key} in passwords: {passwords.keys()}")
        if key in passwords:
            mess += f"Password for {username} at {WebSite} is {passwords[key]}\n"
            messagebox.showinfo("Passwords", mess)
        else:
            mess += "Please enter USERNAME and WEBSITE in the fields"
            messagebox.showerror("Error", mess)
    else:
        messagebox.showerror("Passwords", "EMPTY LIST!!")

def getlist():
    website = {}

    try:
        with open("passwords.txt", 'r') as f:
            for k in f:
                i = k.split(' ')
                website[i[0]] = i[1]
    except:
        print("No users found!!")

    if website:
        mess = "List of users:\n"
        for name, website in website.items():
            
            mess += f"User for {name} is {website}\n"
       
        messagebox.showinfo("Users", mess)
    else:
        messagebox.showerror("Users", "Empty List !!")


def delete():
    WebSite = entrySite.get()
    username = entryName.get()

    temp_passwords = []

    try:
        with open("passwords.txt", 'r') as f:
            for k in f:
                i = k.split(' ')
                if len(i) == 3:
                    if i[0] != WebSite or i[1] != username:
                        temp_passwords.append(f"{i[0]} {i[1]} {i[2]}")
        with open("passwords.txt", 'w') as f:
            for line in temp_passwords:
                f.write(line)
        messagebox.showinfo("Success", f"User {username} at {WebSite} deleted successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error deleting user {username} at {WebSite}: {e}")

if __name__ == "__main__":
    app = tk.Tk()
    app.geometry("240x200")
    app.title("UMWS Password Manager")
   
    labelName = tk.Label(app, text="WEBSITE:")
    labelName.grid(row=0, column=0, padx=10, pady=5)
    entrySite = tk.Entry(app)
    entrySite.grid(row=0, column=1, padx=10, pady=5)

    labelName = tk.Label(app, text="USERNAME:")
    labelName.grid(row=1, column=0, padx=10, pady=5)
    entryName = tk.Entry(app)
    entryName.grid(row=1, column=1, padx=10, pady=5)

    labelPassword = tk.Label(app, text="PASSWORD:")
    labelPassword.grid(row=2, column=0, padx=10, pady=5)
    entryPassword = tk.Entry(app)
    entryPassword.grid(row=2, column=1, padx=10, pady=5)

    buttonAdd = tk.Button(app, text="Add", command=add)
    buttonAdd.grid(row=3, column=0, padx=15, pady=8, sticky="we")

    buttonGet = tk.Button(app, text="Get", command=get)
    buttonGet.grid(row=3, column=1, padx=15, pady=8, sticky="we")

    buttonList = tk.Button(app, text="UserList", command=getlist)
    buttonList.grid(row=4, column=0, padx=15, pady=8, sticky="we")

    buttonDelete = tk.Button(app, text="Delete", command=delete)
    buttonDelete.grid(row=4, column=1, padx=15, pady=8, sticky="we")

    app.mainloop()