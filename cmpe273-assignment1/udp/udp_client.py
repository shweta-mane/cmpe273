import socket


UDP_IP = '127.0.0.1'
UDP_PORT = 4000
BUFFER_SIZE = 1024

def send():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Connected to the server.")
        print("Starting a file (upload.txt) upload...")
        fp = open("upload.txt", 'r')
        line = fp.readline()
        while line:
            data = line.strip().split(':')
            seq_no = int(data[0])
            s.sendto(f"{line}".encode(), (UDP_IP, UDP_PORT))
            ack, ip = s.recvfrom(BUFFER_SIZE)
            while True:
                if ack and int(ack.decode()) == seq_no:
                    print("received ack({}) from the server".format(ack.decode()))
                    break
                else:
                    print("resending data...")
                    s.sendto(f"{line}".encode(), (UDP_IP, UDP_PORT))
                    ack, ip = s.recvfrom(BUFFER_SIZE)

            line = fp.readline()
            
        fp.close()
        print("File upload successfully completed.")
    except socket.error:
        print("Error! {}".format(socket.error))
        exit()

send()