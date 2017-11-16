import sys
import os
from os.path import basename
dir_name = sys.argv[1]
start_path = os.getcwd()
try:
    files = os.listdir(dir_name)
    os.chdir(dir_name)
except OSError:
    print('Error! Wrong folder name.')
try:
    i = 0
    for f in files:
        if basename(f).find('.lnk') != -1:
            os.remove(os.path.abspath(f))
            i = i + 1
    os.chdir(start_path)
    print(str(i) + ' links have been deleted successfully.')
except Exception:
    print('Error! Failed to complete removing')