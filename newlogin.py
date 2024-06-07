from tkinter import *
import os

# Designing window for registration
def destroyPackWidget(parent):
    for e in parent.pack_slaves():
        e.destroy()

def register():
    global root, register_screen
    destroyPackWidget(root)
    register_screen = root
    register_screen.title("Register")
    register_screen.geometry("400x300")
    
    global username
    global password
    global username_entry
    global password_entry
    username = StringVar()
    password = StringVar()

    Label(register_screen, text="Register", bg="#b3e0ff", font=("Arial", 12)).pack(pady=80)
    
    Label(register_screen, text="Username * ", bg="#e6f7ff", font=("Arial", 12)).pack()
    username_entry = Entry(register_screen, textvariable=username)
    username_entry.pack(pady=10)
    
    Label(register_screen, text="Password * ", bg="#e6f7ff", font=("Arial", 12)).pack()
    password_entry = Entry(register_screen, textvariable=password, show='*')
    password_entry.pack(pady=10)
    
    Button(register_screen, text="Register", width=15, height=1, bg="#99ccff", font=("Arial", 12), command=register_user).pack(pady=20)

# Designing window for login
def login():
    global login_screen
    login_screen = Toplevel(main_screen)
    login_screen.title("Login")
    login_screen.geometry("400x300")
    
    Label(login_screen, text="Login", bg="#b3e0ff", font=("Arial", 16)).pack(pady=80)
    
    global username_verify
    global password_verify
    global username_login_entry
    global password_login_entry
    
    username_verify = StringVar()
    password_verify = StringVar()

    Label(login_screen, text="Username * ", bg="#e6f7ff", font=("Arial", 12)).pack()
    username_login_entry = Entry(login_screen, textvariable=username_verify)
    username_login_entry.pack(pady=10)
    
    Label(login_screen, text="Password * ", bg="#e6f7ff", font=("Arial", 12)).pack()
    password_login_entry = Entry(login_screen, textvariable=password_verify, show='*')
    password_login_entry.pack(pady=10)
    
    Button(login_screen, text="Login", width=15, height=1, bg="#99ccff", font=("Arial", 12), command=login_verify).pack(pady=20)

# Implementing event on register button
def btnSucess_Click():
    global root
    destroyPackWidget(root)

def register_user():
    global root, username, password
    username_info = username.get()
    password_info = password.get()

    file = open(username_info, "w")
    file.write(username_info + "\n")
    file.write(password_info)
    file.close()

    username_entry.delete(0, END)
    password_entry.delete(0, END)

    Label(root, text="Registration Success", fg="green", font=("calibri", 14)).pack(pady=10)
    Button(root, text="Click Here to proceed", bg="#99ccff", font=("Arial", 12), command=btnSucess_Click).pack(pady=20)

# Implementing event on login button
def login_verify():
    username1 = username_verify.get()
    password1 = password_verify.get()

    username_login_entry.delete(0, END)
    password_login_entry.delete(0, END)

    list_of_files = os.listdir()
    if username1 in list_of_files:
        file1 = open(username1, "r")
        verify = file1.read().splitlines()
        if password1 in verify:
            login_success()
        else:
            password_not_recognised()
    else:
        user_not_found()

# Designing popup for login success
def login_success():
    global login_success_screen
    login_success_screen = Toplevel(login_screen)
    login_success_screen.title("Success")
    login_success_screen.geometry("200x150")
    Label(login_success_screen, text="Login Success", font=("Arial", 14)).pack(pady=20)
    Button(login_success_screen, text="OK", font=("Arial", 12), command=delete_login_success).pack(pady=20)

# Designing popup for login invalid password
def password_not_recognised():
    global password_not_recog_screen
    password_not_recog_screen = Toplevel(login_screen)
    password_not_recog_screen.title("Error")
    password_not_recog_screen.geometry("200x150")
    Label(password_not_recog_screen, text="Invalid Password", font=("Arial", 14)).pack(pady=20)
    Button(password_not_recog_screen, text="OK", font=("Arial", 12), command=delete_password_not_recognised).pack(pady=20)

# Designing popup for user not found
def user_not_found():
    global user_not_found_screen
    user_not_found_screen = Toplevel(login_screen)
    user_not_found_screen.title("Error")
    user_not_found_screen.geometry("200x150")
    Label(user_not_found_screen, text="User Not Found", font=("Arial", 14)).pack(pady=20)
    Button(user_not_found_screen, text="OK", font=("Arial", 12), command=delete_user_not_found_screen).pack(pady=20)

# Deleting popups
def delete_login_success():
    login_success_screen.destroy()

def delete_password_not_recognised():
    password_not_recog_screen.destroy()

def delete_user_not_found_screen():
    user_not_found_screen.destroy()

# Designing Main(first) window
def main_account_screen(frmmain):
    global main_screen
    main_screen = frmmain
    main_screen.geometry("400x300")
    main_screen.title("Account Login")
    
    Label(main_screen, text="Select Your Choice", bg="#b3e0ff", font=("Arial", 16)).pack(pady=80)
    
    Button(main_screen, text="Login", width=15, height=1, bg="#99ccff", font=("Arial", 12), command=login).pack(pady=20)
    
    Button(main_screen, text="Register", width=15, height=1, bg="#99ccff", font=("Arial", 12), command=register).pack(pady=20)

root = Tk()
main_account_screen(root)
root.mainloop()
