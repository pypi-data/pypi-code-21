from dogpile.cache import make_region
from dogpile.cache.api import NO_VALUE


def get_region():
    import getpass
    db_file = '/tmp/ext_cloud_' + getpass.getuser() + '.dbm'
    return make_region().configure('dogpile.cache.dbm', expiration_time=3600, arguments={"filename": db_file})
