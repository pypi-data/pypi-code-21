import base64


def generate_salt():
    import bcrypt
    return bcrypt.gensalt(14)


def make_hash_length_less_than_72(string):
    import hashlib
    return base64.b64encode(hashlib.sha256(string.encode()).digest())


def remove_null_bytes(string):
    return base64.b64encode(string)


def hash_password(password, salt):
    import bcrypt
    """
        This implementation of bcrypt ignores strings over 72 characters.
        Therefore, the string is shortened by pre-hashing it.
        Also, any null bytes are removed from the shortened password string.
    """
    shorten_password = make_hash_length_less_than_72(password)
    shorten_password_without_null_bytes = remove_null_bytes(shorten_password)
    return bcrypt.hashpw(shorten_password_without_null_bytes, salt)
