from terminal import red,confirm,blue,white,green
from ..util import config,oss_client,smart_unicode

def delete(osspath, yes=False):

    # if osspath.find('oss://') != 0:
    #     osspath = '%s%s' % (config.get_oss_path(), osspath)

    # list
    (arr, pre_arr, bucket_tool, region, bucket, key) = oss_client.list(osspath)

    t=[]
    show_keys=[]
    klen = len(key)

    if len(arr)>0:
        for k in arr:
            t.append(k.key)
            if k.key!=key:
                show_keys.append(k.key[klen:])
            else:
                show_keys.append('.(%s)' % (key))
    tlen = len(t)


    if tlen > 0:
        msg = "%s %s\n%s\n  %s\n%s" % (blue('Delete oss path' ),
                                smart_unicode.format_utf8(osspath),
                                   'Found %s files' % tlen,
                               smart_unicode.format_utf8('\n  '.join(show_keys)),
                               (('Delete all these %s files' % tlen) if tlen > 1 else 'Delete this file'))
    else:
        print('Not found')
        return

    if yes or confirm(msg):
        if tlen>0:
            bucket_tool.batch_delete_objects(t)
        bucket_tool.delete_object(key)
        print(green('done'))

