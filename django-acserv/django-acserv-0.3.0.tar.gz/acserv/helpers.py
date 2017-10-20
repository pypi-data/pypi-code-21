import base64


def proto_to_base64(m):
    chunk = m.SerializeToString()
    return base64.urlsafe_b64encode(chunk).decode('utf-8')


def base64_to_proto(s, cls):
    chunk = base64.urlsafe_b64decode(s)
    m = cls()
    m.ParseFromString(chunk)
    return m
