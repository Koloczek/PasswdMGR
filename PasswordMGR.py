import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet

key = Fernet.generate_key()
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
                
                passwords[i[1]] = decrypt_password(i[2].strip())
    except Exception as e:
       print(f"ERROR: {e}")

    if passwords:
        mess = "Your passwords:\n"
        for user in passwords:
            if user == username:
                mess += f"Password for {username} is {passwords[i]}\n"
                break
        else:
            mess += "No Such Username Exists !!"
        messagebox.showinfo("Passwords", mess)
    else:
        messagebox.showinfo("Passwords", "EMPTY LIST!!")


def getlist():
    # creating a dictionary
    passwords = {}

    # adding a try block, this will catch errors such as an empty file or others
    try:
        with open("passwords.txt", 'r') as f:
            for k in f:
                i = k.split(' ')
                passwords[i[1]] = i[2]
    except:
        print("No passwords found!!")

    if passwords:
        mess = "List of passwords:\n"
        for name, password in passwords.items():
            # generating a proper message
            mess += f"Password for {name} is {password}\n"
        # Showing the message
        messagebox.showinfo("Passwords", mess)
    else:
        messagebox.showinfo("Passwords", "Empty List !!")


def delete():
    # accepting input from the user
    username = entryName.get()

    # creating a temporary list to store the data
    temp_passwords = []

    # reading data from the file and excluding the specified username
    try:
        with open("passwords.txt", 'r') as f:
            for k in f:
                i = k.split(' ')
                if i[0] != username:
                    temp_passwords.append(f"{i[0]} {i[1]}")

        # writing the modified data back to the file
        with open("passwords.txt", 'w') as f:
            for line in temp_passwords:
                f.write(line)

        messagebox.showinfo(
            "Success", f"User {username} deleted successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error deleting user {username}: {e}")


if __name__ == "__main__":
    app = tk.Tk()
    app.geometry("560x270")
    app.title("UMWS Password Manager")

    # Username block
    labelName = tk.Label(app, text="WEBSITE:")
    labelName.grid(row=0, column=0, padx=10, pady=5)
    entrySite = tk.Entry(app)
    entrySite.grid(row=0, column=1, padx=10, pady=5)

    # Username block
    labelName = tk.Label(app, text="USERNAME:")
    labelName.grid(row=1, column=0, padx=10, pady=5)
    entryName = tk.Entry(app)
    entryName.grid(row=1, column=1, padx=10, pady=5)

    # Password block
    labelPassword = tk.Label(app, text="PASSWORD:")
    labelPassword.grid(row=2, column=0, padx=10, pady=5)
    entryPassword = tk.Entry(app)
    entryPassword.grid(row=2, column=1, padx=10, pady=5)

    # Add button
    buttonAdd = tk.Button(app, text="Add", command=add)
    buttonAdd.grid(row=3, column=0, padx=15, pady=8, sticky="we")

    # Get button
    buttonGet = tk.Button(app, text="Get", command=get)
    buttonGet.grid(row=3, column=1, padx=15, pady=8, sticky="we")

    # List Button
    buttonList = tk.Button(app, text="List", command=getlist)
    buttonList.grid(row=4, column=0, padx=15, pady=8, sticky="we")

    # Delete button
    buttonDelete = tk.Button(app, text="Delete", command=delete)
    buttonDelete.grid(row=4, column=1, padx=15, pady=8, sticky="we")

    app.mainloop()