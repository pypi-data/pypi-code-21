def sortdict(input_list=[], key=None):
    try:
        return sorted(input_list, key=lambda k: k[key])
    except Exception as e:
        return e
