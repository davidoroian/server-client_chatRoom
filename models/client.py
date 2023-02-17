import socket
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
import threading
import errno
import sys
import time
import tqdm
from assets.patterns import pat_send_file, pat_size
import os

class Client:

    def __init__(self, host, port):
        self.HEADERLENGTH = 10
        self.BUFFERSIZE = 4096
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) # creating socket that can receive ipv6 addresses, this works with ipv4 as well
        self.sock.connect((host, port))
        self.sock.setblocking(False) # for getting rid of 'hang'

        self.transfer = {} # for file transfer
        self.receiving = False # receiving a file
        self.openfile = 0
        self.total = 0

        msg = tkinter.Tk()
        msg.withdraw()

        self.my_username = simpledialog.askstring("Username", "Please choose a username", parent=msg)

        self.gui_done = False # gui is not fully created
        self.running = True # client is running 
        self.ready = False # server does not know I am ready

        gui_thread = threading.Thread(target=self.gui_loop) # for creating gui
        receive_thread = threading.Thread(target=self.receive) # for receiving and sending data

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self): # creating gui
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled') # client is not able to modify the message area

        self.message_label = tkinter.Label(
            self.win, text="Chat:", bg="lightgray")
        self.message_label.config(font=("Arial", 12))
        self.message_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(
            self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True # gui has been created

        self.win.protocol("VM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self): # writing messages
        message = f"{self.input_area.get('1.0', 'end')}"

        if message: # if client wants to send a file
            if pat_send_file.match(message):
                message = message[:-1]
                m = pat_send_file.match(message)
                self.transfer = {'username': m.group(2), 'file': m.group(1), 'size': os.path.getsize(m.group(1))}

                try:
                    message = message + ' ' + str(os.path.getsize(m.group(1))) + '\n' #sending the filesize as well
                except:
                    print("An error regarding the file occurred")
                    return 0

                # getting and encoding time info
                written_time = time.localtime()
                written_time = time.strftime("%H:%M", written_time).encode('utf-8')
                written_time_header = f"{len(written_time):<{self.HEADERLENGTH}}".encode('utf-8')

                # encoding message
                message = message.encode('utf-8')
                message_header = f"{len(message):<{self.HEADERLENGTH}}".encode('utf-8') 
                self.sock.send(written_time_header + written_time + message_header + message) # seding data
                self.input_area.delete('1.0', 'end') # clearing out input area
            else:
                if message[:-1].endswith('/accept'):
                    self.receiving = True
                    print(f"Starting to receive file {self.transfer['file']} of size {self.transfer['size']} from {self.transfer['username']}")
                # getting and encoding time info
                written_time = time.localtime()
                written_time = time.strftime("%H:%M", written_time).encode('utf-8')
                written_time_header = f"{len(written_time):<{self.HEADERLENGTH}}".encode('utf-8')

                # encoding message
                message = message.encode('utf-8')
                message_header = f"{len(message):<{self.HEADERLENGTH}}".encode('utf-8') 
                self.sock.send(written_time_header + written_time + message_header + message) # seding data
                self.input_area.delete('1.0', 'end') # clearing out input area

    def receive(self): # receiving messages
        while self.running: # always listen for messages
            try:
                if self.receiving and self.openfile == 0:
                    progress = tqdm.tqdm(range(int(self.transfer['size'])), f"Receiving {self.transfer['file']}", unit="B", unit_scale=True, unit_divisor=1024)
                    f = open(self.transfer['file'], "wb")
                    self.openfile = 1

                username_header = self.sock.recv(self.HEADERLENGTH)
                if not len(username_header):
                    print("connection closed by the server")
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip()) # getting first set of data which is user data
                username = self.sock.recv(username_length).decode('utf-8')

                if self.receiving :
                    written_time_header = self.sock.recv(self.HEADERLENGTH)
                    written_time_length = int(written_time_header.decode('utf-8').strip())
                    written_time = self.sock.recv(written_time_length).decode('utf-8')

                    bytes_written_header = self.sock.recv(self.HEADERLENGTH)
                    bytes_written_length = int(bytes_written_header.decode('utf-8').strip())
                    bytes_written = self.sock.recv(bytes_written_length)

                    f.write(bytes_written)

                    self.total += len(bytes_written)
                    if self.total == self.transfer['size'] or not bytes_written:
                        self.text_area.config(state='normal') # enable message area for modification
                        self.text_area.insert('end', f"Received entire file {self.transfer['file']}") # writing message
                        self.text_area.yview('end') # message area scrolls down on its own
                        self.text_area.config(state='disabled') # locking the message area back

                        current_time = time.localtime()
                        current_time = time.strftime("%H:%M", current_time).encode('utf-8')
                        current_time_header = f"{len(current_time):<{self.HEADERLENGTH}}".encode('utf-8')

                        # encoding message
                        message = f"@{self.transfer['username']} Received entire file".encode('utf-8')
                        message_header = f"{len(message):<{self.HEADERLENGTH}}".encode('utf-8') 
                        self.sock.send(current_time_header + current_time + message_header + message) # seding data
                        
                        f.close()
                        self.receiving = False
                        self.total = 0
                        self.openfile = 0
                        self.transfer = {}
                elif username == 'please provide a USERNAME': # when you first start the client
                    written_time = time.localtime()
                    written_time = time.strftime("%H:%M", written_time).encode('utf-8')
                    written_time_header = f"{len(written_time):<{self.HEADERLENGTH}}".encode('utf-8')

                    username = self.my_username.encode('utf-8')
                    username_header = f"{len(username):<{self.HEADERLENGTH}}".encode('utf-8')
                    self.sock.send(written_time_header + written_time + username_header + username) # sending user data back to server
                elif username == 'WAITING FOR GUI' and not self.ready: # server is waiting for the client to finish GUI
                    while not self.gui_done: # waiting for GUI to finish
                        time.sleep(0.100)
                    
                    written_time = time.localtime()
                    written_time = time.strftime("%H:%M", written_time).encode('utf-8')
                    written_time_header = f"{len(written_time):<{self.HEADERLENGTH}}".encode('utf-8')

                    gui_message = 'GUI DONE'.encode('utf-8')
                    gui_message_header = f"{len(gui_message):<{self.HEADERLENGTH}}".encode('utf-8')
                    self.sock.send(written_time_header + written_time + gui_message_header + gui_message) # sending gui info back to server
                elif username == 'YOU ARE READY' and not self.ready:
                    self.ready = True
                else:
                    self.text_area.config(state='normal') # enable message area for modification

                    # getting second set of data, for the time
                    written_time_header = self.sock.recv(self.HEADERLENGTH)
                    written_time_length = int(written_time_header.decode('utf-8').strip())
                    written_time = self.sock.recv(written_time_length).decode('utf-8')

                    # getting third set of data, the actual message
                    message_header = self.sock.recv(self.HEADERLENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = self.sock.recv(message_length).decode('utf-8')

                    if message.startswith('/accept') and username == self.transfer['username']:
                        self.text_area.insert('end', f"File {self.transfer['file']} was accepted by {self.transfer['username']}, starting transfer") # writing message
                        self.text_area.yview('end') # message area scrolls down on its own
                        self.text_area.config(state='disabled') # locking the message area back

                        progress = tqdm.tqdm(range(self.transfer['size']), f"Sending {self.transfer['file']}", unit="B", unit_scale=True, unit_divisor=1024)

                        #sending file
                        with open(self.transfer['file'], "rb") as f:
                            while True:
                                bytes_read = f.read(self.BUFFERSIZE)
                                if not bytes_read:
                                    break #all file has been read

                                written_time = time.localtime()
                                written_time = time.strftime("%H:%M", written_time).encode('utf-8')
                                written_time_header = f"{len(written_time):<{self.HEADERLENGTH}}".encode('utf-8')

                                
                                bytes_read_header = f"{len(bytes_read):<{self.HEADERLENGTH}}".encode('utf-8')
                                self.sock.sendall(written_time_header + written_time + bytes_read_header + bytes_read) # sending read bytes back to server
                                progress.update(len(bytes_read))
                                
                        self.text_area.config(state='normal') # enable message area for modification
                        self.text_area.insert('end', f"File {self.transfer['file']} has been sent to {self.transfer['username']}") # writing message
                        self.text_area.yview('end') # message area scrolls down on its own
                        self.text_area.config(state='disabled') # locking the message area back
                    elif message.startswith('/decline') and username == self.transfer['username']:
                        self.text_area.insert('end', f"{username} refused receiving file {self.transfer['file']}") # writing message
                        self.text_area.yview('end') # message area scrolls down on its own
                        self.text_area.config(state='disabled') # locking the message area back
                        self.transfer = {}
                    elif pat_size.match(message):
                        m = pat_size.match(message)
                        self.transfer = {'username': m.group(1), 'file': os.path.basename(m.group(2)), 'size': m.group(3)}
                        print(self.transfer['file'])
                        self.text_area.insert('end', f"{username} [{written_time}] > {message}") # writing message
                        self.text_area.yview('end') # message area scrolls down on its own
                        self.text_area.config(state='disabled') # locking the message area back
                    else:
                        self.text_area.insert('end', f"{username} [{written_time}] > {message}") # writing message
                        self.text_area.yview('end') # message area scrolls down on its own
                        self.text_area.config(state='disabled') # locking the message area back

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error', str(e))
                    sys.exit()
                continue

            except Exception as e:
                print('General error', str(e))
                sys.exit()

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        sys.exit(0)