from socket import socket, AF_INET, SOCK_STREAM
from random import randint

for i in range(5):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(('localhost', 19000))
    r = randint(0,100)

    s.send(b'Hello' )
    print(s.recv(8192))
