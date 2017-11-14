
# -*- coding:utf-8 -*-

from ..util import client, util, config
from terminal import white, green,red, confirm

PROGRESS_LEN = 50


def del_image(imageId, yes=False):
    arr = imageId.split(',')

    t = util.parse_id_arr(arr, 'images',True)

    if yes:
        __batch_del(t)
    else:
        try:
            if confirm("Delete all these images:\n%s \nAre you sure" % red('\n'.join(t)), default=False):
                __batch_del(t)
        except KeyboardInterrupt:
            print('')
            return


def __batch_del(arr):
    for item in arr:
        __del_image(item)

def __del_image(imageId):
    print(white('exec: bcs delete_image %s' % imageId))
    client.delete_image(imageId)
    print(green('done'))
