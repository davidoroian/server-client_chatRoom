import socket
import select
import time
from models.server import Server

HEADERLENGTH = 10

port = 12234
host = socket.getaddrinfo(socket.gethostname(), port, socket.AF_INET6)[0][4][0]  # getting ipv6 address

server = Server(host, port)

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
