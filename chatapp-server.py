import socket
import select
import time

HEADERLENGTH = 10

port = 12234
host = socket.getaddrinfo(socket.gethostname(), port,
                          socket.AF_INET6)[0][4][0]  # ipv6
# host = socket.gethostname() #ipv4

# if socket.has_dualstack_ipv6():
#     server_socket = socket.create_server((host, port), family=socket.AF_INET6, dualstack_ipv6=True)
# else:
#     client_socket = socket.create_server((host,port))

server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server_socket.setsockopt(
    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for reconnect

server_socket.bind((host, port))
server_socket.listen()

sockets_list = [server_socket]
users = {}

def getTime():
    sent_time = time.localtime()
    sent_time = time.strftime("%H:%M", sent_time).encode('utf-8')
    sent_time_header = f"{len(sent_time):<{HEADERLENGTH}}".encode('utf-8')

    return {"time_header": sent_time_header, "time": sent_time}


def shareToOnlineUsers(message_header, message, username):
    for user in users:
            if user != username and users[user]['online'] == 1:
                username_encoded = username.encode('utf-8')
                username_encoded_header = f"{len(username_encoded):<{HEADERLENGTH}}".encode('utf-8')

                now = getTime()

                users[user]['sock'].send(username_encoded_header + username_encoded + now['time_header'] + now['time'] + message_header + message)


def receive_message(client_socket):
    try:
        written_time_header = client_socket.recv(HEADERLENGTH)
        written_time_length = int(written_time_header.decode("utf-8").strip())
        written_time = client_socket.recv(written_time_length)
        
        message_header = client_socket.recv(HEADERLENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())
        return {"time_header":written_time_header, "time": written_time, "header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False


def delete_client(client_socket, user):
    print(f"Deleted {user}")

    delete_message = 'left the chat\n'
    delete_message = delete_message.encode('utf-8')
    delete_message_header = f"{len(delete_message):<{HEADERLENGTH}}".encode('utf-8')

    shareToOnlineUsers(delete_message_header, delete_message, user)

    sockets_list.remove(client_socket)
    del users[user]


def logout_client(client_socket, user):
    print(f"Closed connection from {user}")
    sockets_list.remove(client_socket)
    users[user]['online'] = 0

    logout_message = 'logged out\n'
    logout_message = logout_message.encode('utf-8')
    logout_message_header = f"{len(logout_message):<{HEADERLENGTH}}".encode('utf-8')

    shareToOnlineUsers(logout_message_header, logout_message, user)


def login_client(client_socket, user):
    print(f"Re-eastablished connection from {user}")

    sockets_list.append(client_socket)
    users[user]['online'] = 1
    users[user]['sock'] = client_socket

    login_message = 'logged in\n'
    login_message = login_message.encode('utf-8')
    login_message_header = f"{len(login_message):<{HEADERLENGTH}}".encode('utf-8')

    shareToOnlineUsers(login_message_header, login_message, user)


def register_client(client_socket, user):
    if user is not False:
        sockets_list.append(client_socket)
        users[user] = {'online': 1, 'buffer': [], 'sock': client_socket}

        join_message = 'joined the chat\n'
        join_message = join_message.encode('utf-8')
        join_message_header = f"{len(first_message):<{HEADERLENGTH}}".encode('utf-8')

        shareToOnlineUsers(join_message_header, join_message, user)

        print(f"Accepted connection from {client_address[0]}:{client_address[1]} username:{user}")


while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    for user in users:
        if len(users[username]['buffer']) != 0 and users[username]['online']==1:
            for message in users[username]['buffer']:
                now = getTime() #for sending receive notification
                received_message = f"received the message you sent at {now['time'].decode('utf-8')}\n".encode('utf-8')
                received_message_header = f"{len(received_message):<{HEADERLENGTH}}".encode('utf-8')

                receiver = username.encode('utf-8')
                receiver_header = f"{len(receiver):<{HEADERLENGTH}}".encode('utf-8')

                sender = message['usr'].decode('utf-8')

                users[sender]['sock'].send(receiver_header + receiver + now['time_header'] + now['time'] + received_message_header + received_message)
                users[username]['sock'].send(message['usrheader'] + message['usr'] + message['theader'] + message['t'] + message['msgheader'] + message['msg'])
                users[username]['buffer'].remove(message)

    for notified_socket in read_sockets:
        if notified_socket == server_socket: # client is new or came back to the chatroom
            client_socket, client_address = server_socket.accept()

            first_message = 'please provide a USERNAME' 
            first_message = first_message.encode('utf-8')
            first_message_header = f"{len(first_message):<{HEADERLENGTH}}".encode('utf-8')

            client_socket.send(first_message_header + first_message) # sending request for username
        
            username = receive_message(client_socket) # getting the username message
            username = username['data'].decode('utf-8')

            exists = False
            for user in users: # checking if the username already exists
                if user == username:
                    exists = True

            if exists:
                login_client(client_socket, username)
            else:
                register_client(client_socket, username)

        else:
            message = receive_message(notified_socket)
            username = None

            for user in users:
                if users[user]['sock'] == notified_socket:
                    username = user
                    break

            if username and users[username]['online'] == 1:

                if message is False:
                    logout_client(notified_socket, username)
                    continue

                print(f"Received message from {username} at [{message['time'].decode('utf-8')}]: {message['data'].decode('utf-8')}")

                for user in users:
                    username_encoded = username.encode('utf-8')
                    username_header = f"{len(username_encoded):<{HEADERLENGTH}}".encode('utf-8')

                    now = getTime() #for sending receive notification
                    received_message = f"received the message you sent at {now['time'].decode('utf-8')}\n".encode('utf-8')
                    received_message_header = f"{len(received_message):<{HEADERLENGTH}}".encode('utf-8')

                    receiver = user.encode('utf-8')
                    receiver_header = f"{len(receiver):<{HEADERLENGTH}}".encode('utf-8')

                    if user != username and users[user]['online'] == 1:
                        users[user]['sock'].send(username_header + username_encoded + message['time_header'] + message['time'] + message['header'] + message['data'])
                        users[username]['sock'].send(receiver_header + receiver + now['time_header'] + now['time'] + received_message_header + received_message)
                    elif user != username and users[user]['online'] == 0:
                        users[user]['buffer'].append({'usrheader':username_header, 'usr':username_encoded,'theader':message['time_header'], 't':message['time'], 'msgheader': message['header'], 'msg':message['data']})
            else:
                continue

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        for user in users:
                if users[user]['sock'] == notified_socket:
                    del users[user]
                    break
