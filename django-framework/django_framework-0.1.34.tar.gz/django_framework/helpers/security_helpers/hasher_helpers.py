import hashlib

SALT_STR = "ThisBe@Saltz"
def md5_hasher(uid, saltz = None, label = False):
    md5_ = '**md5$'
    uid = str(uid)
    if uid.find(md5_) == -1:
        if saltz == None:
            saltz = SALT_STR

        hashed = hashlib.md5(uid+ saltz).hexdigest()
    else:
        hashed = uid

    if label:
        return md5_ + hashed
    else:
        return hashed

if __name__ == '__main__': # pragma: no cover

    print(md5_hasher('Chai2013')) # pragma: no cover
    print(md5_hasher('dogs36')) # pragma: no cover
    print(md5_hasher('robert1')) # pragma: no cover
#     print(get_anon_id('E869C3AE73744AB38D6CE47FD0B915'))
