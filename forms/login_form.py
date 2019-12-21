import socket
import tkinter as tk
import threading

import client_memory
from forms.chat_form import ChatForm
from message import MessageType, packing_message, unpacking_message

class LoginForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        master.resizable(width=False, height=False)
        master.geometry('300x100')
        self.master.title("Login")

        self.sock = client_memory.sock

        self.label1 = tk.Label(self, text="Nickname")
        self.label1.grid(row=1, sticky=tk.E)

        self.nickname = tk.Entry(self)
        self.nickname.grid(row=1, column=1, pady=(10, 6))

        self.loginbtn = tk.Button(self, text="Sign in", command=self.login)
        self.loginbtn.grid(row=2, column=1, columnspan=1, pady=(10, 6))

        self.pack()

    def login(self):
        nickname = self.nickname.get()
        if not nickname:
            tk.messagebox.showerror("Error", "Nickname cannot be empty.")
            return
        # send the input nickname to server to test whether it is legal
        package = packing_message(self.sock.fileno(), MessageType.login_info, nickname)
        self.sock.send(package)
        while True:
            _, message_type, message = unpacking_message(self.sock.recv(1024))
            if message_type == MessageType.login_refuse:
                print(message)
                tk.messagebox.showerror("Error", "This nickname has been used.")
                self.nickname.delete(0, tk.END)
                return
            elif message_type == MessageType.login_confirm:
                print(message)
                client_memory.nickname = nickname
                master = tk.Toplevel(client_memory.root, takefocus=True)
                ChatForm(master)
                self.master.destroy()
                return
            else:
                continue