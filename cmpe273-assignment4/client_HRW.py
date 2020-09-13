import sys
import socket
import pickle

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, hash_code_hex
from node_ring import NodeRing

BUFFER_SIZE = 1024
clients = []

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
    hash_codes = set()
    # PUT all users.
    for u in USERS:
        data_bytes, key = serialize_PUT(u)
        response = get_node(key).send(data_bytes)
        print(response)
        print("\n")
        hash_codes.add(str(response.decode()))


    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}\n")
    
    # GET all users.
    for hc in hash_codes:
        print(hc)
        data_bytes, key = serialize_GET(hc)
        response = get_node(key).send(data_bytes)
        print(response)
        print("\n")

def get_node(key_hex):
    highest_weight, champion = -1, None
    node_index = 0
    for i in range (len(clients)):
        node = clients[i]
        weight = compute_node_weight(node, key_hex)
        print(f"Weight For Node {i} = {weight}")
        if weight > highest_weight:
            champion, highest_weight = node, weight
            node_index= i
    print(f"Selected Node {node_index}")
    return champion
    

def compute_node_weight(node, key_hex):
    a = 9876543210
    b = 123456
    node_string = str(node.host) + ":" + str(node.port)
    object_bytes = pickle.dumps(node_string)
    node_hash_hex = hash_code_hex(object_bytes)
    key = int(key_hex, 16)
    node_hash = int(node_hash_hex, 16)
    return (a * ((a * node_hash + b) ^ key) + b) % (2^31)

if __name__ == "__main__":
    for server in NODES:
        client = UDPClient(server['host'], server['port'])
        clients.append(client)
    process(clients)
