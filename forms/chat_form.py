import sys
import socket
import _tkinter
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import datetime
import threading

import client_memory
from message import MessageType, packing_message, unpacking_message

class ChatForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        master.resizable(width=True, height=True)
        master.geometry('540x400')
        master.minsize(520, 370)
        self.master.title("Chatroom")
        
        self.sock = client_memory.sock

        self.font_color = "#000000"
        self.font_size = 10

        self.right_frame = tk.Frame(self, bg='white')
        self.right_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.input_frame = tk.Frame(self.right_frame, bg='white')

        self.input_textbox = ScrolledText(self.right_frame, height=8)
        self.input_textbox.bind("<Control-Return>", self.send_message)

        self.send_btn = tk.Button(self.input_frame, text='Send message(Ctrl+Enter)', command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT, expand=False)

        self.chat_box = ScrolledText(self.right_frame, bg='white', font = (None, self.font_size))
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        self.input_textbox.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=(0, 0), pady=(0, 0))
        self.chat_box.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.chat_box.bind("<Key>", lambda e: "break")
        self.chat_box.tag_config("default", lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_box.tag_config("me", foreground="green", spacing1='5')
        self.chat_box.tag_config("others", foreground="blue", spacing1='5')
        self.chat_box.tag_config("message", foreground="black", spacing1='0')
        self.chat_box.tag_config("system", foreground="grey", spacing1='0', justify='center', font=(None, 8))

        self.pack(expand=True, fill=tk.BOTH)

        # build a thread for receiving messages
        self.thread = threading.Thread(target = self.recv_thread)
        self.thread.setDaemon(True)
        self.thread.start()
    
    def send_message(self, _=None):
        message = self.input_textbox.get("1.0", tk.END)
        if message == '\n':
            return
        package = packing_message(self.sock.fileno(), MessageType.chat_message, message)
        self.sock.send(package)
        self.input_textbox.delete("1.0", tk.END)
        return 'break'
    
    # show received chat messages in the chat_box
    def append_to_chat_box(self, sender, message):
        package = packing_message(self.sock.fileno(), MessageType.name_request, sender)
        self.sock.send(package)
        while True:
            sender, message_type, nickname = unpacking_message(self.sock.recv(1024))
            if message_type == MessageType.name_info:
                break
        
        # use different display settings for different message senders
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if nickname == 'SERVER':
            self.chat_box.insert(tk.END, time + '\n' + message + '\n', ['system'])
        elif nickname == client_memory.nickname:
            self.chat_box.insert(tk.END, nickname + '  ' + time + '\n', ['me'])
            self.chat_box.insert(tk.END, ' ' + message, ['message'])
        else:
            self.chat_box.insert(tk.END, nickname + '  ' + time + '\n', ['others'])
            self.chat_box.insert(tk.END, ' ' + message, ['message'])

        self.chat_box.update()
        self.chat_box.see(tk.END)

    def recv_thread(self):
        while True:
            try:
                sender, message_type, message = unpacking_message(self.sock.recv(1024))
                if message_type == MessageType.chat_message and message:
                    self.append_to_chat_box(sender, message)
                else:
                    pass
            except (ConnectionAbortedError, _tkinter.TclError):
                print('Chatroom connection error.')
                break
            except ConnectionResetError:
                print('Chatroom closed.')
                break