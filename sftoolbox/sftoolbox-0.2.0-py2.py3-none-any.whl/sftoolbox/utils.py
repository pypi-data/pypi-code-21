import hashlib


def human_readable(value):
    """make the given string nice and human readable
    """
    label = value.replace('.', ' ').replace('_', ' ')
    label = label.title()
    label = label.strip()
    return label


def get_hash_from_file(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return str(hasher.hexdigest())
