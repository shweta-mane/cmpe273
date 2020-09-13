import socket
import asyncio


TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 1024

async def listen_forever():
    while True:
        conn, addr = await loop.sock_accept(s)
        loop.create_task(process_client_request(conn))
        
async def process_client_request(conn):
    data = conn.recv(BUFFER_SIZE)
    print(f"Client Connected:{data.decode()}")
    conn.send("client connected".encode())
    while True:
        data = (await loop.sock_recv(conn, BUFFER_SIZE))
        if not data:
            break
        print(f"received data:{data.decode()}")
        await loop.sock_sendall(conn, "pong".encode())
    

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(5)
s.setblocking(0)
print(f"Server started at port:{TCP_PORT}")

loop = asyncio.get_event_loop()
loop.run_until_complete(listen_forever())

