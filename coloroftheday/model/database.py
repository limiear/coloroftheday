import shelve

def open():
    return shelve.open('cache', writeback=True)

def sync(cache):
    return cache.sync()

def close(cache):
    return cache.close()

def has_path(cache, path):
    keys = path.split('/')
    for key in keys:
        if not cache.has_key(key):
            return False
        cache = cache[key]
    return True

def get(cache, path):
    keys = path.split('/')
    cache_tmp = cache
    for key in keys:
        if not cache_tmp.has_key(key):
            cache_tmp[key] = {}
            sync(cache)
        cache_tmp = cache_tmp[key]
    return cache_tmp

def set(cache, path, value):
    keys = path.split('/')
    cache_tmp = cache
    for key in keys[:-1]:
        if not cache_tmp.has_key(key):
            cache_tmp[key] = {}
            sync(cache)
        cache_tmp = cache_tmp[key]
    cache_tmp[keys[-1]] = value
    sync(cache)
