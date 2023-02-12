import socket
import time

class Server :
    
    def __init__(self, host, port):
        self.users = {} # user data
        self.HEADERLENGTH = 10
        
        if socket.has_dualstack_ipv6():
            self.socket = socket.create_server((host, port), family=socket.AF_INET6, dualstack_ipv6=True) # creating socket that can receive ipv6 addresses that supports dual stack, this works with ipv4 as well
        else:
            self.socket = socket.create_server((host,port))

        self.sockets_list = [self.socket] # list of sockets for select, for listening to the sockets
        
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for reconnect
        self.socket.listen()
    

    def getTime(self):
        sent_time = time.localtime()
        sent_time = time.strftime("%H:%M", sent_time).encode('utf-8')
        sent_time_header = f"{len(sent_time):<{self.HEADERLENGTH}}".encode('utf-8')

        return {"time_header": sent_time_header, "time": sent_time}


    def shareToOnlineUsers(self, message_header, message, username): # info regarding states of the users
        for user in self.users:
                if user != username and self.users[user]['online'] == 1:
                    username_encoded = username.encode('utf-8')
                    username_encoded_header = f"{len(username_encoded):<{self.HEADERLENGTH}}".encode('utf-8')

                    now = self.getTime()

                    self.users[user]['sock'].send(username_encoded_header + username_encoded + now['time_header'] + now['time'] + message_header + message)


    def receive_message(self, client_socket):
        try:
            # decoding time info
            written_time_header = client_socket.recv(self.HEADERLENGTH)
            written_time_length = int(written_time_header.decode("utf-8").strip())
            written_time = client_socket.recv(written_time_length)
            
            #decoding message info
            message_header = client_socket.recv(self.HEADERLENGTH)
            if not len(message_header): # if no message was sent, the user disconnected
                return False
            message_length = int(message_header.decode("utf-8").strip())

            return {"time_header":written_time_header, "time": written_time, "header": message_header, "data": client_socket.recv(message_length)}
        except:
            return False


    def delete_client(self, client_socket):

        user = self.getUsernameOfSocket(client_socket)

        print(f"Deleted {user}")

        delete_message = 'left the chat\n'
        delete_message = delete_message.encode('utf-8')
        delete_message_header = f"{len(delete_message):<{self.HEADERLENGTH}}".encode('utf-8')

        self.shareToOnlineUsers(delete_message_header, delete_message, user)

        self.sockets_list.remove(client_socket) # removing socket from list
        del self.users[user] # deleting user


    def logout_client(self, client_socket):
        user = self.getUsernameOfSocket(client_socket)

        print(f"Closed connection from {user}")
        self.sockets_list.remove(client_socket) # removing socket from list for select
        self.users[user]['online'] = 0 # marking the user as offline

        logout_message = 'logged out\n'
        logout_message = logout_message.encode('utf-8')
        logout_message_header = f"{len(logout_message):<{self.HEADERLENGTH}}".encode('utf-8')

        self.shareToOnlineUsers(logout_message_header, logout_message, user)


    def login_client(self, client_socket, user):
        print(f"Re-eastablished connection from {user}")

        self.sockets_list.append(client_socket) # appending the new socket to the list for select
        self.users[user]['online'] = 1 # marking the user as online
        self.users[user]['sock'] = client_socket # updating socket

        login_message = 'logged in\n'
        login_message = login_message.encode('utf-8')
        login_message_header = f"{len(login_message):<{self.HEADERLENGTH}}".encode('utf-8')

        self.shareToOnlineUsers(login_message_header, login_message, user)
        time.sleep(1)
        self.sendBufferedMessages(user)


    def register_client(self, client_socket, user, client_address):
        if user is not False:
            self.sockets_list.append(client_socket) # adding socket to the list for select
            self.users[user] = {'online': 1, 'buffer': [], 'sock': client_socket} # creating user

            join_message = 'joined the chat\n'
            join_message = join_message.encode('utf-8')
            join_message_header = f"{len(join_message):<{self.HEADERLENGTH}}".encode('utf-8')

            self.shareToOnlineUsers(join_message_header, join_message, user)

            print(f"Accepted connection from {client_address[0]}:{client_address[1]} username:{user}")
    
    
    def sendBufferedMessages(self, user):
        while len(self.users[user]['buffer']) != 0:
            for message in self.users[user]['buffer']:
                now = self.getTime() #for sending receive notification
                received_message = f"received the message you sent at {now['time'].decode('utf-8')}\n".encode('utf-8')
                received_message_header = f"{len(received_message):<{self.HEADERLENGTH}}".encode('utf-8')

                receiver = user.encode('utf-8')
                receiver_header = f"{len(receiver):<{self.HEADERLENGTH}}".encode('utf-8')

                sender = message['usr'].decode('utf-8')

                # receive motification for the sender
                self.users[sender]['sock'].send(receiver_header + receiver + now['time_header'] + now['time'] + received_message_header + received_message)
                # message sent to desired receiver
                self.users[user]['sock'].send(message['usrheader'] + message['usr'] + message['theader'] + message['t'] + message['msgheader'] + message['msg'])
                self.users[user]['buffer'].remove(message)
    
    def firstConnection(self):
        client_socket, client_address = self.socket.accept()

        # sending request for username
        user_message = 'please provide a USERNAME' 
        user_message = user_message.encode('utf-8')
        user_message_header = f"{len(user_message):<{self.HEADERLENGTH}}".encode('utf-8')
        client_socket.send(user_message_header + user_message) 
    
        # getting the username 
        username = self.receive_message(client_socket) 
        username = username['data'].decode('utf-8')

        if username in self.users: # checking if server already has the username
            self.login_client(client_socket, username)
        else:
            self.register_client(client_socket, username, client_address)


    def isCurrentUserOnline(self, username):
        return username and self.users[username]['online'] == 1


    def getUsernameOfSocket(self, notified_socket):
        for user in self.users: # getting the username of the socket 
            if self.users[user]['sock'] == notified_socket:
                username = user
                break

        return username
        

    def listenForMessage(self, notified_socket):
        
        message = self.receive_message(notified_socket)
        username = self.getUsernameOfSocket(notified_socket)

        if message is False: # checking if the user disconnected and logging them out if so
            self.logout_client(notified_socket)
            return 0

        print(f"Received message from {username} at [{message['time'].decode('utf-8')}]: {message['data'].decode('utf-8')}")

        for user in self.users: 
            username_encoded = username.encode('utf-8')
            username_header = f"{len(username_encoded):<{self.HEADERLENGTH}}".encode('utf-8')

            now = self.getTime() # for sending receive notification
            received_message = f"received the message you sent at {now['time'].decode('utf-8')}\n".encode('utf-8')
            received_message_header = f"{len(received_message):<{self.HEADERLENGTH}}".encode('utf-8')

            receiver = user.encode('utf-8')
            receiver_header = f"{len(receiver):<{self.HEADERLENGTH}}".encode('utf-8')

            if user != username and self.users[user]['online'] == 1: # sending the message to all of the online users
                # message sent to desired receiver
                self.users[user]['sock'].send(username_header + username_encoded + message['time_header'] + message['time'] + message['header'] + message['data'])
                # receive motification for the sender
                self.users[username]['sock'].send(receiver_header + receiver + now['time_header'] + now['time'] + received_message_header + received_message)
            elif user != username and self.users[user]['online'] == 0: # storing the message in the buffers of all of the offline users
                self.users[user]['buffer'].append({'usrheader':username_header, 'usr':username_encoded,'theader':message['time_header'], 't':message['time'], 'msgheader': message['header'], 'msg':message['data']})



