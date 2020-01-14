from socket import *

HOST = '127.0.0.1'
#HOST = '192.168.0.11'
PORT = 1119
BUFSIZE = 1024
ADDR = (HOST,PORT)

client_socket = socket(AF_INET, SOCK_STREAM)

try:
    client_socket.connect(ADDR)
    print('client connection is success..')
    
    message = '[client] Hello!'
    client_socket.send(message.encode('utf-8'))

    data = client_socket.recv(BUFSIZE)

    print('Received Data: ', data.decode('utf-8'))

except Exception as e:
    print('connection error %s:%s'%ADDR)
    sys.exit()

print('close..')
