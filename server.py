import socket
import threading

from server_memory import conn_name_dict, conn_list, client_conn_dict, conn_client_dict
from message import MessageType, packing_message, unpacking_message

def broadcast(conn_num, message):
    for c in conn_list:
        package = packing_message(conn_client_dict[conn_num], MessageType.chat_message, message)
        c.send(package)
 
def child_connection(connection, conn_num):
    try:
        # judge whether the nickname is legal
        while True:
            sender, message_type, message = unpacking_message(connection.recv(1024))
            if message_type == MessageType.login_info:
                if message in conn_name_dict.values():
                    package = packing_message(0, MessageType.login_refuse, 'Illegal nickname')
                    connection.send(package)
                else:
                    package = packing_message(0, MessageType.login_confirm, 'Legal nickname')
                    connection.send(package)
                    nickname = message
                    break
            else:
                continue
        conn_list.append(connection)
        conn_name_dict[conn_num] = nickname
        client_conn_dict[sender] = conn_num
        conn_client_dict[conn_num] = sender

        print('    [ User', conn_num, ']', nickname + '\n')
        broadcast(0, '' + conn_name_dict[conn_num] + ' enters chatroom\n')
    except Exception:
        connection.close()
        return
    # endlessly receiving message, check its type and deal with it
    while True:
        try:
            sender, message_type, message = unpacking_message(connection.recv(1024))
            # broadcast chat message
            if message_type == MessageType.chat_message and message:
                print(conn_name_dict[conn_num] + ': ' + message)
                broadcast(conn_num, message)
            # answer request for nickname
            elif message_type == MessageType.name_request:
                package = packing_message(0, MessageType.name_info, conn_name_dict[client_conn_dict[message]])
                connection.send(package)
            else:
                continue
        except (OSError, ConnectionResetError):
            try:
                conn_list.remove(connection)
            except:
                pass
            print('---', conn_name_dict[conn_num], 'exit,', len(conn_list), 'person left ---\n')
            broadcast(0, '' + conn_name_dict[conn_num] + ' leaves chatroom\n')

            del conn_name_dict[conn_num]
            sender = conn_client_dict[conn_num]
            del client_conn_dict[sender]
            del conn_client_dict[conn_num]

            connection.close()
            return


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = '127.0.0.1'
PORT = 8998

sock.bind((HOST, PORT))
sock.listen()
print('Server', 'listening on', HOST, '...\n')

while True:
    connection, addr = sock.accept()
    print('--- New connection', connection.fileno(), connection.getsockname(), '---')

    sender, message_type, message = unpacking_message(connection.recv(1024))
    if message == '1':
        package = packing_message(0, MessageType.connect_confirm, 'Welcome to chatroom!')
        connection.send(package)
        # build a new thread for the new connection
        new_thread = threading.Thread(target = child_connection, args = (connection, connection.fileno()))
        new_thread.setDaemon(True)
        new_thread.start()
            
    else:
        package = packing_message(0, MessageType.connect_confirm, 'Please leave!')
        connection.send(package)
        connection.close()