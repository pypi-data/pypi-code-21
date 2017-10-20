from ..util import oss_client,config
# from terminal import white
# from ..const import CMD
from ..const import STRING
def cat(osspath, byte_range=None):
    # str or list

    #def_oss_path = config.get_oss_path()

    arr = osspath
    if isinstance(osspath, STRING):
        arr = [osspath]

    for osspath in arr:
        # if not osspath.startswith('oss://'):
        #     osspath = def_oss_path + osspath

        #print(white('exec: %s o ls %s' % (CMD,osspath)))

        print(oss_client.get_data(osspath, byte_range=byte_range))

def trans_byte_range(s):
    arr = s.split(':')
    if len(arr)==2:
        return map(lambda x: int(x), arr)
    elif len(arr)==1:
        return [0,int(arr[0])]
    else:
        return None

