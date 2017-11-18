import hashlib

def compute_hash(attributes, ignored_attributes=None):
    """
    Computes a hash code for the given dictionary that is safe for persistence round trips 
    """
    ignored_attributes = list(ignored_attributes) if ignored_attributes else []
    tuple_attributes = _convert(attributes.copy(), ignored_attributes)
    hasher = hashlib.sha256(str(tuple_attributes).encode('utf-8', errors='ignore'))
    return hasher.hexdigest()

def _convert(dictionary, ignored_attributes=None):
    ignored_attributes = ignored_attributes or []
    [dictionary.pop(k, None) for k in ignored_attributes]

    for key, value in dictionary.items():
        if isinstance(value, dict):
            dictionary[key] = _convert(value, ignored_attributes)
        elif isinstance(value, list) or isinstance(value, set):
            dictionary[key] = tuple(sorted([_convert(v, ignored_attributes)
                                            if isinstance(v, dict) else v
                                            for v in value if v is not None]))
    return tuple(sorted([(k, str(v)) for k, v in dictionary.items()]))
