import sys
import socket
import time
import threading
import tkinter as tk
import tkinter.simpledialog

from forms.login_form import LoginForm
import client_memory
from message import MessageType, packing_message, unpacking_message

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = '127.0.0.1'
PORT = 8998

try:
    root = tk.Tk()
    sock.connect((HOST, PORT))
    # send '1' to test the connection
    package = packing_message(sock.fileno(), MessageType.connect_request, '1')
    sock.send(package)
    while True:
        sender, message_type, message = unpacking_message(sock.recv(1024))
        if message_type == MessageType.connect_confirm:
            print(message)
            break
        elif message_type == MessageType.connect_refuse:
            print(message)
            raise Exception
        else:
            continue
    client_memory.sock = sock
    client_memory.root = root
    
    login = tk.Toplevel()
    LoginForm(login)
    
    root.withdraw()
    root.mainloop()
    root.destroy()
    
except Exception:
    print('Connection fail.')
    sock.close()
    sys.exit()