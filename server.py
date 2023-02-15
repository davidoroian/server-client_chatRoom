import socket
import select
import re
from models.server import Server
from assets.patterns import *
from assets.strings import *

HEADERLENGTH = 10

port = 12234
host = socket.getaddrinfo(socket.gethostname(), port, socket.AF_INET6)[0][4][0]  # getting ipv6 address

server = Server(host, port)

print('Server started')

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
                        server.sendSystemMessage(error, username)
                elif message_decoded.startswith('/'):
                    if pat_help.match(message_decoded): # sending help syntax
                        server.sendSystemMessage(help, username)
                    elif pat_users.match(message_decoded): # sending available users
                        server.sendUsers(username)
                    elif pat_group_create.match(message_decoded): # creating a group
                        m = pat_group_create.match(message_decoded)
                        server.createGroup(m.group(1), username)
                    elif pat_group.match(message_decoded): # sending group info
                        m = pat_group.match(message_decoded)
                        server.sendGroupInfo(m.group(1), username)
                    elif pat_groups.match(message_decoded): # sending group info
                        server.sendGroupsInfo(username)
                    elif pat_group_add.match(message_decoded): # adding member to group
                        m = pat_group_add.match(message_decoded)
                        server.addToGroup(username, m.group(1), m.group(2))
                    else:
                        server.sendSystemMessage(error, username)
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
