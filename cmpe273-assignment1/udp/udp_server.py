import socket


UDP_IP = '127.0.0.1'
UDP_PORT = 4000
BUFFER_SIZE = 1024
MESSAGE = "1"

def listen_forever():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", UDP_PORT))
    print("Server started at port " + str(UDP_PORT))

    while True:
        # get the data sent to us
        data, ip = s.recvfrom(BUFFER_SIZE)
        line = data.decode(encoding="utf-8").strip()
        line_data = line.split(':')
        ack = int(line_data[0])
        if (ack == 1):
            print("Accepting a file upload...")
            fp = open("upload_server.txt", 'w')
        else:
            fp = open("upload_server.txt", 'a')
        fp.write(line + '\n')
        fp.close()
        s.sendto(str(ack).encode(), ip)
        if (ack == 10000):
            print("Upload successfully completed.")
    
listen_forever()