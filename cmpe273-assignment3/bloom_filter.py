import math
import mmh3

class BloomFilter:

    def __init__(self, no_of_keys, prob):
        self.prob = prob 
        self.size = self.calculate_size(no_of_keys, prob)
        self.hash_count = self.no_hash_functions(self.size, no_of_keys)
        self.array = [False] * self.size

    def calculate_size(self,n,p): 
        m = -(n * math.log(p))/(math.log(2)**2)
        return int(m) 

    def no_hash_functions(self, m, n): 
        k = (m/n) * math.log(2) 
        return int(k)

    def add(self, data):
        for i in range(1, self.hash_count+1):
            index = mmh3.hash(data,i) % self.size
            self.array[index] = True

    def is_member(self, data):
        member = True
        for i in range(1, self.hash_count+1):
            index = mmh3.hash(data,i) % self.size
            if self.array[index] == False:
                member = False
                break

        return member
