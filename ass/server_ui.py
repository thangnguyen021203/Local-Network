import tkinter as tk
from tkinter import messagebox
import re
from threading import Thread, Lock
import time
import sys

from server import Server

SERVER_COMMAND = "\n**** Invalid syntax ****\nFormat of server's commands\n1. ping hostname\n2. discover hostname\n3. clear\n\n"

SERVER_USERNAME = 'admin'
SERVER_PASSWORD = 'admin'

PING_PATTERN = r"^ping\s[\w.]+$"
DISCOVER_PATTERN = r"^discover\s[\w.]+$"
CLEAR_PATTERN = r"^clear$"

class Server_App(tk.Tk):
    def __init__(self, server_port):
        super().__init__()

        # Some declarations
        self.username, self.password = None, None
        self.server = None
        self.server_port = server_port
        self.server_on = None

        self.title("File Sharing Application")
        self.minsize(600, 400)

        self.closing = False
        self.thread = None
        self.mutex = Lock()

        # Used for manage the current page
        self.current_page_frame = None
        
        self.current_page_frame = self.main_page()
        self.current_page_frame.pack()

    def trigger(self, frame):
        """
        This function used for page redirection

        Parameters: None
        Return: None
        """
        self.current_page_frame.pack_forget()
        self.current_page_frame = frame()
        self.current_page_frame.pack()

    def check_login(self, username_entry, password_entry):
        username = username_entry.get()
        password = password_entry.get()
        
        if username == "" or password == "":
            messagebox.showerror("Lỗi đăng nhập", "Vui lòng điền đầy đủ thông tin.")
            return

        if username == SERVER_USERNAME and password == SERVER_PASSWORD:
            self.username = username
            self.password = password
            messagebox.showinfo("Đăng nhập thành công", "Chào mừng, " + self.username + "!")
        else:
            messagebox.showerror("Lỗi đăng nhập", "Sai tên đăng nhập hoặc mật khẩu.")
            return
        
        self.server = Server("192.168.31.42",3000,"serverdatabase.json") ###Liên kết
        Thread(target=self.server.listen, args=(10,), daemon=True).start()
        self.server_on = True
        
        self.current_page_frame.pack_forget()
        self.current_page_frame = self.terminal()
        self.current_page_frame.pack()

    def sign_in(self):
        sign_in_frame = tk.Frame(borderwidth = 70)

        sign_in_label = tk.Label(sign_in_frame, text="SIGN IN", 
                                 font=("San Serif", 24, "bold"), borderwidth = 10)
        sign_in_label.grid(row = 0, column = 0, columnspan = 10)

        sign_in_username_label = tk.Label(sign_in_frame, text="Username", 
                                          font=("San Serif", 13, "bold"))
        sign_in_username_label.grid(row=1, column=0, sticky="we", padx = 10, pady=10)
        sign_in_username_entry = tk.Entry(sign_in_frame, width = 50, font=("San Serif", 13))
        sign_in_username_entry.grid(row=1, column=1, columnspan = 9, sticky = "we", 
                                    padx = 10, pady = 10, ipadx=2, ipady = 2)
        sign_in_username_entry.bind('<Return>', 
        lambda event: self.check_login(sign_in_username_entry, sign_in_password_entry))

        sign_in_password_label = tk.Label(sign_in_frame, text="Password", 
                                          font=("San Serif", 13, "bold"))
        sign_in_password_label.grid(row=2, column=0, sticky="we", padx = 10, pady=10)
        sign_in_password_entry = tk.Entry(sign_in_frame, show="*", width = 50, 
                                          font=("San Serif", 13))
        sign_in_password_entry.grid(row=2, column=1, columnspan= 9, sticky = "we", 
                                    padx = 10, pady = 10, ipadx=2, ipady = 2)
        sign_in_password_entry.bind('<Return>', 
        lambda event: self.check_login(sign_in_username_entry, sign_in_password_entry))

        sign_in_button = tk.Button(sign_in_frame, text="Sign In", font=("San Serif", 13), 
                                   command = lambda: self.check_login(sign_in_username_entry, sign_in_password_entry))
        sign_in_button.grid(row = 3, column = 1)
        return_button = tk.Button(sign_in_frame, text = "Main Page", font=("San Serif", 13), 
                                  command = lambda: self.trigger(self.main_page))
        return_button.grid(row = 3, column = 6)

        return sign_in_frame

    def main_page(self):
        main_page_frame = tk.Frame(borderwidth = 50)

        main_page_label = tk.Label(main_page_frame, text="FILE SHARING APPLICATION", 
                                   font=("San Serif", 30, "bold"), borderwidth = 50)
        main_page_label.grid(row = 0, column = 0)

        b1 = tk.Button(main_page_frame, text = "Sign In", font=("San Serif", 14), 
                       command = lambda: self.trigger(self.sign_in))
        b1.grid(row = 1, column = 0, pady = 5)

        return main_page_frame

    def command_processing(self, command):
        """
        Return True when the command is in the correct format
        """
        if re.search(PING_PATTERN, command) or re.search(DISCOVER_PATTERN, command) \
            or re.search(CLEAR_PATTERN, command):
            return True
        return False

    def get_response(self, command):
        """
        Use for get response for each command and show it for user

        Return:
        response (String): The result when execute the command
        """
        if command == "clear":
            return "clear"
        opcode, hostname = command.split(" ")
        return self.server.run(opcode.upper(), hostname)
    
    def update_output(self, server_output):#???????
        while not self.closing:
            time.sleep(0.5)
            if self.closing:
                break
            self.server.queue_mutex.acquire()
            if not self.server.output_queue.empty():
                server_output.config(state=tk.NORMAL)
                output = self.server.output_queue.get()
                server_output.insert(tk.END, output)
                server_output.see(tk.END)
                server_output.config(state=tk.DISABLED)
            self.server.queue_mutex.release()

    def clear_output(self, server_output):
        server_output.config(state = tk.NORMAL)
        server_output.delete(0.1, tk.END)
        server_output.config(state = tk.DISABLED)

    # Trigger for excute command
    def execute_command(self, input_field, output_field):
        command = input_field.get()
        output_field.config(state=tk.NORMAL)
        output_field.insert(tk.END, f"{self.username}$ " + command + "\n", "color")
        output_field.see(tk.END)
        input_field.delete(0, tk.END)

        if not self.command_processing(command):
            output_field.insert(tk.END, SERVER_COMMAND, "color")
            output_field.see(tk.END)
        
        else:
            result = self.get_response(command)
            if command == "clear":
                output_field.delete(0.1, tk.END)
                output_field.insert(tk.END, 
                    "Terminal [Version 1.0.0]\nCopyright (C) phuc. All right reserved.\n\n", "color")
            else:
                output_field.insert(tk.END, result, "color")
                output_field.see(tk.END)

        output_field.config(state=tk.DISABLED)

    def log_out(self):
        self.server.close()
        self.server_on = False
        self.trigger(self.main_page)
    
    def terminal(self):
        terminal_frame = tk.Frame()

        header = tk.Label(terminal_frame, text = f"Hello, {self.username}", 
                          font=("San Serif", 11, "bold"))
        header.grid(row = 0, column = 0, padx = 5, pady = 5)

        log_out_button = tk.Button(terminal_frame, text = "Log Out", 
                                   command = self.log_out)
        log_out_button.grid(row = 0, column = 209, pady = 5)
        
        terminal_output = tk.Text(terminal_frame, background = "black")
        terminal_output.tag_configure("color", foreground="white")
        terminal_output.insert(tk.END, 
        "Terminal [Version 1.0.0]\nCopyright (C) phuc. All right reserved.\n\n", "color")     
        terminal_output.config(state = tk.DISABLED)
        terminal_output.grid(row = 1, column = 0, columnspan = 200, padx = 5, pady = 5)

        server_output = tk.Text(terminal_frame, width=40)
        server_output.grid(row=1, column = 200, columnspan = 10, padx = 5, pady = 5)
        server_output.config(state = tk.DISABLED)

        input_header = tk.Label(terminal_frame, text = ">>>")
        input_header.grid(row = 2, column = 0, sticky="e")

        input_field = tk.Entry(terminal_frame)
        input_field.grid(row = 2, column = 1, columnspan = 199, sticky="we", pady = 5)
        input_field.bind('<Return>', lambda event: self.execute_command(input_field, terminal_output))
        
        

        output_clear = tk.Button(terminal_frame, text = "Clear",
                                 command = lambda: self.clear_output(server_output), pady=5)
        output_clear.grid(row = 2, column= 206, pady = 5)

        self.thread = Thread(target=self.update_output, args=[server_output], daemon=True)
        self.thread.start()
        
        return terminal_frame

    
    def close(self):
        self.closing = True
        if self.thread:
            self.thread.join()
        if self.server_on:
            self.server.close()

        self.destroy()

def main():
    # if len(sys.argv) < 2:
    #     print("Please provide server port number!")
    # if len(sys.argv) > 2:
    #     print("Invalid syntax")

    server_port = 3000
    
    app = Server_App(server_port)
    app.protocol("WM_DELETE_WINDOW", app.close)
    app.mainloop()

if __name__ == "__main__":
    main()