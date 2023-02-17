import socket
from models.client import Client

HEADERLENGTH = 10

port = 12234
host = socket.getaddrinfo(socket.gethostname(), port, socket.AF_INET6)[0][4][0] #ipv6
#host = socket.gethostname()  # ipv4

client = Client(host, port) # generating client 