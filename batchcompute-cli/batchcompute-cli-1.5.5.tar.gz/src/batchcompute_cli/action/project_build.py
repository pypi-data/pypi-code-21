from ..util import util
import json
import os
import tarfile
import glob
from terminal import green

BUILD_SCRIPT = 'build_script'
TAR_SRC_KEY = 'tar_src'

def build():

    type = util.check_is_job_project()

    with open('./project.json', 'r') as f:
        obj = json.loads(f.read())

    bs = obj.get(BUILD_SCRIPT)
    tar = obj.get(TAR_SRC_KEY)
    if bs:
        os.system(bs)

    if tar:
        build_tar(tar, type)


    if not bs and not tar:
        raise Exception('Cannot found %s or %s in project.json' % (BUILD_SCRIPT, TAR_SRC_KEY))
    else:
        print(green('Done'))



def build_tar(tar, type):

    dist = os.path.join(os.getcwd(), 'worker.tar.gz')

    arr=[]
    # cd src
    os.chdir(tar['base'])

    if tar.get('files'):
        for n in tar['files']:
            arr = arr + glob.glob(n)
        with tarfile.open(dist, "w|gz") as tar:
            for n in arr:
                print('add %s' % n)
                tar.add(n)
    else:
        src = os.path.join(os.getcwd())

        with tarfile.open(dist, 'w|gz') as tar:
            for root,dir,files in os.walk(src):
                for file in files:
                    fullpath=os.path.join(root,file)
                    print(fullpath)
                    tar.add(fullpath,arcname=file)



