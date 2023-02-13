import socket
import select
import re
from models.server import Server

HEADERLENGTH = 10

port = 12234
host = socket.getaddrinfo(socket.gethostname(), port, socket.AF_INET6)[0][4][0]  # getting ipv6 address

server = Server(host, port)

string_dm = r'@(\w+)\s(.+)'
pat_dm = re.compile(string_dm)

string_help = r'/help'
pat_help = re.compile(string_help)

string_users = r'/users'
pat_users = re.compile(string_users)

error = 'Incorrect syntax, use /help\n'

while True:
    read_sockets, _, exception_sockets = select.select(server.sockets_list, [], server.sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server.socket: # client_socket is new, user is new or came back to the chatroom
            server.firstConnection()  
        else: # listening for and receiving messages
            username = server.getUsernameOfSocket(notified_socket)
            if server.isCurrentUserOnline(username): # client is online
                message = server.listenForMessage(notified_socket)
                if not message: # if client logged out we go to next socket
                    continue
                message_decoded = message['data'].decode('utf-8')
                if message_decoded.startswith('@'):
                    if pat_dm.match(message_decoded): # sending a dm
                        m = pat_dm.match(message_decoded)
                        server.dm(username, m.group(2) + '\n', m.group(1))
                    else:
                        server.sendError(error, username)
                elif message_decoded.startswith('/'):
                    if pat_help.match(message_decoded): # sending help syntax
                        server.sendHelp(username)
                    elif pat_users.match(message_decoded): # sending available users
                        server.sendUsers(username)
                    else:
                        server.sendError(error, username)
                else:
                    server.sendMessageToAllUsers(notified_socket, message)
            elif server.isCurrentUserWaitingForGui(username): # client is waiting for GUI
                message = server.listenForMessage(notified_socket)
                if not message: # if GUI is not done go to next socket
                    continue
                if message['data'].decode('utf-8') == 'GUI DONE':
                    server.login_client(username)
            else:
                continue

    for notified_socket in exception_sockets:
        server.delete_client(notified_socket)
