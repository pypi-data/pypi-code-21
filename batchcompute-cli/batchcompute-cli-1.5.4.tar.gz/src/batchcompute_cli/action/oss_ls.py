from ..util import config,oss_client,formater,smart_unicode
from terminal import white,blue
from ..const import CMD,WIN


def ls(osspath=None, top=None, name=None):

    def_oss_path = config.get_oss_path()
    if not osspath:
        osspath = def_oss_path

    search = name

    if top:
        top = int(top)

    # if not osspath.startswith('oss://'):
    #     osspath = def_oss_path + osspath


    (obj_arr, pre_arr, bucket_tool, region, bucket, mykey) = oss_client.list(osspath, '/')

    print('exec: %s o ls oss://%s/%s' % (CMD, bucket, smart_unicode.format_utf8(mykey)))


    t=[]
    if search:
        for item in pre_arr:
            if search in item:
                t.append(item[len(mykey):-1])
    else:
        for item in pre_arr:
            t.append(item[len(mykey):-1])
    pre_arr=t


    t2=[]
    if search:
        for item in obj_arr:
            if item.key != mykey:
                item.key = item.key[len(mykey):]
                if '/' not in item.key and search in item.key:
                    t2.append(item)
    else:
        for item in obj_arr:
            if item.key != mykey:
                item.key = item.key[len(mykey):]
                if '/' not in item.key:
                    t2.append(item)
    obj_arr = t2

    dlen = len(pre_arr)
    flen = len(obj_arr)

    if top:
        if top < dlen:
            pre_arr = pre_arr[:top]
            obj_arr= []
        elif top < dlen+flen:
            obj_arr = obj_arr[:top-dlen]

    if WIN:
        for item in pre_arr:
            print('%s/' % smart_unicode.format_utf8(item))
    else:
        for item in pre_arr:
            print('%s/' % blue(item))
    for item in obj_arr:
        size = formater.format_size(item.size)
        print('%s %s' % (smart_unicode.format_utf8(item.key), white('(%s)'%size)))

