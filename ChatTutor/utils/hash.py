import hashlib

def get_hash(object) -> hashlib._hash:
    import json, hashlib

    return hashlib.md5(json.dumps(object).encode()).hexdigest()
