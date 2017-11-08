from ..util import formater,oss_client,config
import os
import sys
import time
from terminal import green,blue

def upload(localpath, osspath=None, use_put_object=False):

    osspath = osspath or config.get_oss_path()

    if '*' in localpath:
        raise Exception('Invalid filename')

    # if not osspath.find('oss://'):
    #     raise Exception('Invalid osspath')

    abs_path = formater.get_abs_path(localpath)


    if not os.path.exists(abs_path):
        raise Exception('Not found %s' % abs_path)


    start_time = time.time()
    if os.path.isdir(abs_path):
        # folder
        if not osspath.endswith('/'):
            osspath+='/'
        # d - d
        upload_folder_2_folder(abs_path, osspath, use_put_object)
    else:
        # file
        if osspath.endswith('/'):
            osspath += os.path.basename(abs_path)
        oss_client.upload_file(abs_path, osspath, upload_progress_callback, use_put_object)

    print('%s (%s)' % (green('done'), formater.from_sec(time.time() - start_time)))


def upload_folder_2_folder(abs_path, osspath, use_put_object=False):
    print('%s: %s to %s' % (blue('upload folder'),abs_path, osspath) )

    arr = os.listdir(abs_path)
    for k in arr:
        filename = os.path.join(abs_path, k)
        if os.path.isdir(filename):
            upload_folder_2_folder(filename, osspath+k+'/', use_put_object)
        else:
            print('  %s => %s' % (filename, osspath+k))
            oss_client.upload_file(filename, osspath+k,  upload_progress_callback, use_put_object)



def upload_progress_callback(a,b):
    if a!= b:
        p = int(a*50/b)
        s = ('%s %s%%\r' % ('#' * p , round(a*10000/b)/100) )
    else:
        s = ('%s 100%%\n' % ('#' * 50))
    sys.stdout.write(s)
    sys.stdout.flush()