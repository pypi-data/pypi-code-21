'''
Created on 03.05.2012

@author: raidan
'''
from datetime import datetime
from datetime import timedelta
import os
from fw_patches2.Const import LAST_VERSION_DIR_POSTFIX
import subprocess
import sys

def handle_dirs(root, username, password):
    
    def svn(root, cmd):
        command = '{0} --username {1} --password {2} --no-auth-cache --non-interactive'.format(cmd, username, password)
        proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                cwd=root)
        ret = proc.wait()
        if ret != 0:
            raise BaseException('Unable to call svn')
    
    svn(root, 'svn update')
    
    prev_month = datetime.strftime(datetime.now().replace(day=1) - timedelta(days=1), '%Y-%m')
    print(prev_month)
    
    today = datetime.strftime(datetime.now(), '%Y-%m')
    print(today)
    
    prev_dir = None
    for dir_ in os.listdir(root):
        if dir_.startswith(today):
            print("Already have current month")
            return
        if dir_.startswith(prev_month):
            if prev_dir is not None:
                raise BaseException('Found more than one dir_ with prefix {0}: {1} and {2}'.format(
                            prev_month, prev_dir, dir_))
            prev_dir = dir_
    
    if not prev_dir:
        print("Not found prev month")
        return
    
    if not prev_dir.endswith(LAST_VERSION_DIR_POSTFIX):
        print("Last dir is not ends with", LAST_VERSION_DIR_POSTFIX)
        return
    
    files_to_move = []
    all_files = []
    for file_ in os.listdir(os.path.join(root, prev_dir)):
        if file_.startswith(today):
            files_to_move.append(file_)
        else:
            all_files.append(file_)
    
    files_to_move.sort()
    all_files.sort()
    
    if len(all_files) == 0:
        print("No files in dir!")
        return
    
    print ("OK, processing...")
    
    # Yes, it's bad
    last_patch = int(all_files[-1][-9:-4])
    next_patch = last_patch + 1
    
    prev_dir_rename = prev_dir[:-len(LAST_VERSION_DIR_POSTFIX)] + '{0:{fill}6}'.format(last_patch, fill='0')
    print ('Last dir renaming: {0} -> {1}'.format(prev_dir, prev_dir_rename))
    
    next_dir = '{0}-{1}-{2}'.format(today, '{0:{fill}6}'.format(next_patch, fill='0'), LAST_VERSION_DIR_POSTFIX)
    print ('Next dir: {0}'.format(next_dir))
    
    svn(root, 'svn rename {0} {1}'.format(prev_dir, prev_dir_rename))
    svn(root, 'svn commit -m "Moving month {0}"'.format(prev_month))
    
    os.mkdir(os.path.join(root, next_dir))
    svn(root, 'svn add {0}'.format(next_dir))
    
    for f in files_to_move:
        print ('+ moving file', f)
        svn(root, 'svn move {0}/{1} {2}/{1}'.format(prev_dir_rename, f, next_dir))
    
    svn(root, 'svn commit -m "Confirming month {0}"'.format(prev_month))
    
    print ('ALL DONE')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print ('Usage: python -m fw_patches2.module_patchdir <DIR> <SVN_USER> <SVN_PASSWORD>')
    else:
        handle_dirs(sys.argv[1], sys.argv[2], sys.argv[3])
