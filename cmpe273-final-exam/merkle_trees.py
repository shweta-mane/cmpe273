import hashlib
from dataclasses import dataclass

class Node(object):
    def __init__(self, val=None, left=None, right=None):
        # Hash value of the node via hashlib.sha256(xxxxxx.encode()).hexdigest()
        self.val = val
        # Left node
        self.left = left
        # Right node
        self.right = right

    def __str__(self):
        return f':val={self.val},left={self.left},right={self.right}:'


class MerkleTrees(object):
    def __init__(self):
        self.root = None
        # txns dict: { hash_val -> 'file_path' } 
        self.txns = None
        
    def get_root_hash(self):
        return self.root.val if self.root else None

    def build(self, txns):
        """
        Construct a Merkle tree using the ordered txns from a given txns dictionary.
        """
        # save the original txns(files) dict while building a Merkle tree.
        self.txns = txns
        txns_list = list(txns.keys())
        if len(txns_list)%2 != 0:
            txns_list.append(txns_list[-1])
        
        parents = []
        for index in range(0, len(txns_list)-1, 2):
            left = txns_list[index]
            right = txns_list[index+1]
            combine = left + right
            root = hashlib.sha256(combine.encode()).hexdigest()
            current_node = Node(root, Node(left), Node(right))
            parents.append(current_node)

        parent1 = parents[0]
        parent2 = parents[1]
        combine = parent1.val + parent2.val
        root_hash = hashlib.sha256(combine.encode()).hexdigest()
        root_node = Node(root_hash, parent1, parent2)
        self.root = root_node


    def print_level_order(self):
        """
          1             1
         / \     -> --------------------    
        2   3       2 3
        """
        print(self.root.val)
        print("--------------------------")

        left = self.root.left
        right = self.root.right
        print(left.val, right.val)
        print("---------------------------")
        print(left.left.val, left.right.val, right.left.val, right.right.val)

        
    @staticmethod
    def compare(x, y):
        """
        Compare a given two merkle trees x and y.
        x: A Merkle Tree
        y: A Merkle Tree
        Pre-conditions: You can assume that number of nodes and heights of the given trees are equal.
        
        Return: A list of pairs as Python tuple type(xxxxx, yyyy) that hashes are not match.
        https://realpython.com/python-lists-tuples/#python-tuples
        """
        diff = []
        if x.get_root_hash() == y.get_root_hash():
            return diff
        
        x_txns_list = list(x.txns.keys())
        y_txns_list = list(y.txns.keys())

        for index in range(len(x_txns_list)):
            x_txn = str(x_txns_list[index])
            y_txn = str(y_txns_list[index])
            if x_txn != y_txn:
                d = (x_txn, y_txn)
                diff.append(d)
        
        return diff

