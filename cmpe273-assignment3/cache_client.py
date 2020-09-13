import sys
import socket

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
from node_ring import NodeRing
from lru_cache import lru_cache
from bloom_filter import BloomFilter

BUFFER_SIZE = 1024
bloomfilter = BloomFilter(20, 0.05)

class UDPClient():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)       

    def send(self, request):
        print('Connecting to server at {}:{}'.format(self.host, self.port))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(request, (self.host, self.port))
            response, ip = s.recvfrom(BUFFER_SIZE)
            return response
        except socket.error:
            print("Error! {}".format(socket.error))
            exit()


def process(udp_clients):
    client_ring = NodeRing(udp_clients)
    hash_codes = set()
    # PUT all users.
    print("\nPut All Users\n")
    for u in USERS:
        response = put(u, client_ring)
        print(response)
        hash_codes.add(response)

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")
    
    print("\nGet All Users\n")
    # GET all users.
    for hc in hash_codes:
        print(hc)
        response = get(hc, client_ring)
        print(response)

    print("\nDelete All Users\n")
    # DELETE all users.
    for hc in hash_codes:
        print(hc)
        response = delete(hc, client_ring)
        print(response)

def lru_cache_get(func):
    def wrapper_get(*args, **kwargs):
        hc = args[1]
        user = lru_cache.get(hc)
        if user == -1:
            user = func(*args, **kwargs)
            lru_cache.put(hc, user)
        return user

    return wrapper_get

def put(u, client_ring):
    data_bytes, key = serialize_PUT(u)
    bloomfilter.add(key)
    response = client_ring.get_node(key).send(data_bytes)
    response = str(response.decode())

    return response

@lru_cache(5)
def get(hc, client_ring):
    data_bytes, key = serialize_GET(hc)
    if bloomfilter.is_member(key):
        return client_ring.get_node(key).send(data_bytes)
    else:
        return None

def delete(hc, client_ring):
    data_bytes, key = serialize_DELETE(hc)
    if bloomfilter.is_member(key):
        return client_ring.get_node(key).send(data_bytes)
    else:
        return None

if __name__ == "__main__":
    clients = [
        UDPClient(server['host'], server['port'])
        for server in NODES
    ] 
    process(clients)
