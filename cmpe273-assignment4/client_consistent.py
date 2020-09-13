import sys
import socket
import pickle
import bisect

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, hash_code_hex

BUFFER_SIZE = 1024
NO_VIRTUAL_NODES = 2
REPLICATION_FACTOR = 2
clients = {}
hash_keys = []

class UDPClient():
    def __init__(self, host, port, pn, vn):
        self.host = host
        self.port = int(port)  
        self.physical_node = pn  
        self.virtual_node = vn
           
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
        nodes = get_node(key)
        for i in range(len(nodes)):
            node = nodes[i]
            print(f"Sending data to= Physical Node : {node.physical_node}, Virtual Node : {node.virtual_node}")
            response = node.send(data_bytes)
            print(response)
        print("\n")
        hash_codes.add(str(response.decode()))

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}\n")
    
    # GET all users.
    for hc in hash_codes:
        print(hc)
        data_bytes, key = serialize_GET(hc)
        node = get_node(key)[0]
        print(f"Getting data from= Physical Node : {node.physical_node}, Virtual Node : {node.virtual_node}")
        response = node.send(data_bytes)
        print(response)
        print("\n")

def get_node(key_hex):
    nodes = []
    hash_code = get_hash(key_hex)
    pos = bisect.bisect_left(hash_keys, hash_code)
    if pos == len(hash_keys):
        pos = 0
    for i in range(REPLICATION_FACTOR):
        index = pos+i
        if index == len(hash_keys):
            index = 0
        hash_code = hash_keys[index]
        nodes.append(clients[hash_code])
    return nodes

def get_hash(hash_hex):
    hash_code = int(hash_hex, 16)
    hc = hash_code % 360
    return hc

if __name__ == "__main__":
    for server in NODES:
        for i in range(NO_VIRTUAL_NODES):
            server_string = str(server['host']) + ":" + str(server['port']) + ":" + str(i)
            object_bytes = pickle.dumps(server_string)
            hash_hex = hash_code_hex(object_bytes)
            hash_code = get_hash(hash_hex)
            bisect.insort(hash_keys, hash_code)
    
    node_index = 0
    for h in range(len(hash_keys)):
        server = NODES[node_index]
        client = UDPClient(server['host'], server['port'], node_index, h)
        clients[hash_keys[h]] = client
        node_index+=1
        if node_index == len(NODES):
            node_index = 0

    print(f"Replication Factor = {REPLICATION_FACTOR}")
    print(f"Virtual Node per Physical Node = {NO_VIRTUAL_NODES}\n")
    process(clients)
