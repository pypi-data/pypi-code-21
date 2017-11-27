from __future__ import absolute_import, division, print_function

import sys
import autest.glb as glb

if sys.platform == 'win32':
    if sys.version_info >= (3, ):
        from winreg import *
    else:
        from _winreg import *

    glb.Locals['HKEY_CLASSES_ROOT'] = HKEY_CLASSES_ROOT
    glb.Locals['HKEY_CURRENT_USER'] = HKEY_CURRENT_USER
    glb.Locals['HKEY_LOCAL_MACHINE'] = HKEY_LOCAL_MACHINE
    glb.Locals['HKEY_USERS'] = HKEY_USERS
    glb.Locals['HKEY_CURRENT_CONFIG'] = HKEY_CURRENT_CONFIG

    def has_regkey(root, keys):

        try:
            for fullkey in keys:
                path, key = fullkey.rsplit('\\', 1)
                # get path container
                try:
                    # normal case is that we want to get a key
                    with OpenKey(root, path) as rpath:
                        # get key value
                        QueryValueEx(rpath, key)
                    return True
                except WindowsError as e:
                    try:
                        # maybe this was just checking for a path
                        with OpenKey(root, fullkey) as rpath:
                            pass
                        return True
                    except WindowsError as e:
                        pass

        except WindowsError as e:
            pass

        return False

    def reg_key_equal(key, value):
        pass

else:
    glb.Locals['HKEY_CLASSES_ROOT'] = 1
    glb.Locals['HKEY_CURRENT_USER'] = 2
    glb.Locals['HKEY_LOCAL_MACHINE'] = 3
    glb.Locals['HKEY_USERS'] = 4
    glb.Locals['HKEY_CURRENT_CONFIG'] = 5

    def has_regkey(root, key):
        return False

    def reg_key_equal(key, value):
        return False
