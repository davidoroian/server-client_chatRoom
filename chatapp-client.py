import socket
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
import threading
import errno
import sys
import time

HEADERLENGTH = 10

port = 12234
# host = socket.getaddrinfo(socket.gethostname(), port, socket.AF_INET6)[0][4][0] #ipv6
host = socket.gethostname()  # ipv4


class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.setblocking(False)

        msg = tkinter.Tk()
        msg.withdraw()

        self.my_username = simpledialog.askstring("Username", "Please choose an username", parent=msg)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

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

        self.gui_done = True

        self.win.protocol("VM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):
        message = f"{self.input_area.get('1.0', 'end')}"

        if message:
            written_time = time.localtime()
            written_time = time.strftime("%H:%M", written_time).encode('utf-8')
            written_time_header = f"{len(written_time):<{HEADERLENGTH}}".encode('utf-8')

            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADERLENGTH}}".encode('utf-8')
            self.sock.send(written_time_header + written_time + message_header + message)
            self.input_area.delete('1.0', 'end')

    def receive(self):
        while self.running:
            try:
                username_header = self.sock.recv(HEADERLENGTH)
                if not len(username_header):
                    print("connection closed by the server")
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())
                username = self.sock.recv(username_length).decode('utf-8')

                if username == 'please provide a USERNAME':
                    written_time = time.localtime()
                    written_time = time.strftime("%H:%M", written_time).encode('utf-8')
                    written_time_header = f"{len(written_time):<{HEADERLENGTH}}".encode('utf-8')

                    username = self.my_username.encode('utf-8')
                    username_header = f"{len(username):<{HEADERLENGTH}}".encode('utf-8')
                    self.sock.send(written_time_header + written_time + username_header + username)
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')

                        written_time_header = self.sock.recv(HEADERLENGTH)
                        written_time_length = int(written_time_header.decode('utf-8').strip())
                        written_time = self.sock.recv(written_time_length).decode('utf-8')

                        message_header = self.sock.recv(HEADERLENGTH)
                        message_length = int(message_header.decode('utf-8').strip())
                        message = self.sock.recv(message_length).decode('utf-8')

                        self.text_area.insert('end', f"{username} [{written_time}] > {message}")
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')

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

client = Client(host, port)