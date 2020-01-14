from socket import *
import time

HOST = ''
PORT = 1119
BUFSIZE = 1024
ADDR = (HOST,PORT)

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(ADDR)
print('Server launched..')

server_socket.listen(1)
print('Waiting connection..')

client_socket, addr = server_socket.accept()
print('Connected by: ', str(addr))
            

while True:

    data = client_socket.recv(BUFSIZE)
    print('Received Data: ', data.decode('utf-8'))
    time.sleep(1)
    
    if not data:
        break



