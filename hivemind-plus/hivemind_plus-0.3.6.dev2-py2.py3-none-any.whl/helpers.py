def check_equality(a, b, fields=None):
    if fields is None:
        fields = []

    if len(fields) == 0:
        return a == b
    for f in fields:
        try:
            if a[f] != b[f]:
                return False
        except KeyError:
            return False
    return True
