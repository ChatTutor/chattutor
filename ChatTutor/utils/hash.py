def get_hash(object):
    import json,hashlib
    return hashlib.md5(  json.dumps(object).encode()).hexdigest()     