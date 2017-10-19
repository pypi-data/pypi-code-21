#!C:\Users\Administrator\AppData\Local\Programs\Python\Python36\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'mxrain==0.1.3','console_scripts','mxrain'
__requires__ = 'mxrain==0.1.3'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('mxrain==0.1.3', 'console_scripts', 'mxrain')()
    )
