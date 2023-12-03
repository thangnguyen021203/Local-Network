import tkinter
from tkinter import messagebox

window = tkinter.Tk() 
window.title("Login form")
window.geometry('1180x960')
window.configure(bg='#333333')


def login():
    username = "thang"
    password = "123"

    if username_entry.get() == username and password_entry.get() == password:
        messagebox.showinfo(title="Login Success", message="You successfully logged in")
    else:
        messagebox.showerror(title="Error", message="Invalid login.")

frame = tkinter.Frame(bg='#333333') 

# Creating widgets
login_label = tkinter.Label(frame, text="Login", bg='#333333', foreground='#4287f5', font=("Arial",30))
username_label = tkinter.Label(frame, text = "Username", bg='#333333', foreground='#FFFFFF',font=("Arial",16))
username_entry = tkinter.Entry(frame)
password_label = tkinter.Label(frame, text = "Password", bg='#333333', foreground='#FFFFFF',font=("Arial",16))
password_entry = tkinter.Entry(frame, show="*")
login_button = tkinter.Button(frame, text = "Login", bg='#4287f5', fg='#FFFFFF',font=("Arial",16), command=login)
 
#Placing widgets on the screen
login_label.grid(row=0, column=0, columnspan=2, sticky="news", pady=40)
username_label.grid(row = 1, column=0)
username_entry.grid(row=1, column=1, pady=20)
password_label.grid(row=2, column=0)
password_entry.grid(row=2, column=1, pady=20)
login_button.grid(row=3, column=0, columnspan=2, pady=30)

frame.pack()

window.mainloop()
