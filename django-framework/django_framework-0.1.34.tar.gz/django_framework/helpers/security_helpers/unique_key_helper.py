import uuid
def generate_unique_key(length = None, dashes = True, numbers_only = False):

    if numbers_only:
        myuuid = str(uuid.uuid4().fields[-1]).replace('-', '')
        myuuid2 = str(uuid.uuid4().fields[-1]).replace('-', '')
        myuuid3 = str(uuid.uuid4().fields[-1]).replace('-', '')

        myuuid = myuuid + myuuid2 + myuuid3
    else:
        myuuid = str(uuid.uuid4())
        if not dashes:
            myuuid = myuuid.replace('-', '')

    if length == None:
        return myuuid[:32]
    else:
        if 0 < length < 32:
            return myuuid[:length]
        else:
            raise ValueError('The length must be between 0 and 36')


if __name__ == '__main__':

    a = generate_unique_key(None) # pragma: no cover
    print(a) # pragma: no cover
    print(len(a)) # pragma: no cover

    a = generate_unique_key(None, True) # pragma: no cover
    print(a) # pragma: no cover
    print(len(a)) # pragma: no cover
