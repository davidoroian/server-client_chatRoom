import socket
import select
import re
from models.server import Server
from assets.patterns import *

HEADERLENGTH = 10

port = 12234
host = socket.getaddrinfo(socket.gethostname(), port, socket.AF_INET6)[0][4][0]  # getting ipv6 address

server = Server(host, port)

error = 'Incorrect syntax, use /help\n'

help = "These are the available commands:\n" \
        "\t@[username/group] [message] - send a message to a user or a group\n" \
        "\t/help - get help\n" \
        "\t/users - lists existing usernames with status\n" \
        "\t/groups - lists your available groups\n" \
        "\t/group [groupname]- lists the users and admins in that specific group\n" \
        "\t/create group [groupname] - creates an empty group with you as admin\n" \
        "\t/add [groupname] [username]- adds a user to a group, if you are an admin there\n" \
        "\t/make admin [groupname] [username] - adds username to admin group for specific group\n"

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
                    print('in /')
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
