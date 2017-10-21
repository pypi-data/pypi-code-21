import hashlib, json

def json_pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))
    
def json_hash(obj):
    json_data = json_pretty(obj).encode('utf8')
    return hashlib.sha1(json_data).hexdigest().lower()