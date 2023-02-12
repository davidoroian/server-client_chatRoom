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
            if server.isCurrentUserOnline(username):
                server.listenForMessage(notified_socket)
            else:
                continue

    for notified_socket in exception_sockets:
        server.delete_client(notified_socket)
