from collections import OrderedDict 
import time

cache = OrderedDict()

def lru_cache(size):
    def Inner(func):
        def wrapper(*args):
            key = args[0]
            if key in cache:
                cache.move_to_end(key)
                data = cache[key]
                print('[cache-hit] ' + func.__name__ + '(' + str(key) + ')')
            else:
                data = func(*args)
                cache[key] = data
                print('[' + str(time.clock()) + '] ' + func.__name__ + '(' + str(key) + ')')
                cache.move_to_end(key)
                if len(cache) > size:
                    cache.popitem(last = False)
            return data
        return wrapper
    return Inner