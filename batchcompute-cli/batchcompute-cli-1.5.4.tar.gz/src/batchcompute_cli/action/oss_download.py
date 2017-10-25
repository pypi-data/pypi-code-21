from ..util import config,oss_client,formater
import json
import os
import tarfile
import time
from terminal import green,blue
import sys

def download(osspath, localpath='./',recursion=False):

    to_path = formater.get_abs_path(localpath)

    # if osspath.find('oss://') != 0:
    #     osspath = '%s%s' % (config.get_oss_path(), osspath)

    start_time = time.time()
    if osspath.endswith('/'):
        # folder
        mkdirs(to_path)
        download_2_folder(osspath, to_path)
    else:
        # file
        ind = osspath[:-1].rfind('/')

        filename = osspath[ind+1:]

        if os.path.isdir(to_path):
            to_path = os.path.join(to_path, filename)

        print('%s ==> %s' % (osspath, to_path))
        oss_client.download_file(osspath, to_path, download_progress_callback)

    print('%s (%s)' % (green('done'), formater.from_sec(time.time() - start_time) ))

def download_2_folder(osspath, to_path):
    print('%s : %s' %(blue('Download folder'), osspath))

    (arr, pre_arr, bucket_tool, region, bucket, key) = oss_client.list(osspath)

    for k in arr:
        real_path = k.key[len(key):]

        if real_path=='' or real_path.endswith('/'):
            # folder
            continue
        else:
            #file
            target = os.path.join(to_path,real_path)
            target_dir = target[:target.rfind('/')]
            print('  mkdirs: %s' % target_dir  )
            mkdirs(os.path.join(to_path, target_dir))

            print('  %s ==> %s' % (k.key, target))
            bucket_tool.get_object_to_file(k.key, target, progress_callback=download_progress_callback)


def download_progress_callback(a,b):
    if a!= b:
        p = int(a*50/b)
        s = ('%s %s%%\r' % ('#' * p , p*2) )
    else:
        s = ('%s 100%%\n' % ('#' * 50) )

    sys.stdout.write(s)
    sys.stdout.flush()

def mkdirs(a):
    if not os.path.exists(a):
        os.makedirs(a)