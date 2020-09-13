import socket
import time 
import sys


TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 1024
MESSAGE = "ping"

def send(id, delay, messages):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(f"{id}".encode())
    data = s.recv(BUFFER_SIZE)
    count = 0
    while count < messages:
        print("sending data:", MESSAGE)
        s.send(f"{id}:{MESSAGE}".encode())
        data = s.recv(BUFFER_SIZE)
        print("received data:", data.decode())
        count+=1
        time.sleep(delay)
    s.close()

clientID = sys.argv[1]
delay = sys.argv[2]
messages = sys.argv[3]
send(clientID, int(delay), int(messages))