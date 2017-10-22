'''
Created on 06.03.2012

@author: raidan
'''
from fw_patches2 import tools
from fw_patches2.tools import import_python_lib, _extract_option
import os
import sys


def wrap_module(config, ui, install):
    ui = tools.check_ui(ui)
        
    thisDir, thisName = os.path.split(os.path.realpath(sys.argv[0]))
    targetLog = os.path.join(thisDir, thisName + '.log')
    if os.path.exists(targetLog):
        os.remove(targetLog)

    
    if config is None:
        config = '\n'.join(sys.argv[1:])
        
    config, myDir = _extract_option(config, '--dir')
    if myDir is None:
        myDir = thisDir
        
    config, optionsOnly = _extract_option(config, '--options-only')
    
    config, test = _extract_option(config, '--test')
    config, notest = _extract_option(config, '--notest')
    if notest:
        test = None
    
    noconfirm = tools._arg_option('--noconfirm')
        
    myDir = os.path.realpath(os.path.join(myDir, '..'))
    sdkDir = os.path.realpath(os.path.join(myDir, 'sdk'))
    
    config, compress = _extract_option(config, '--compressIntoScript')
    
    config = config.strip()

    sysInstall = config + '''
--onlySYS
--script={0}
--target_log={1}
--dir={2}
'''.format(thisName + '_sys', 
           targetLog, 
           myDir)
    if noconfirm:
        sysInstall = sysInstall + "--noconfirm\n"
        
    
    sdkInstall = config + '''
--noconfirm
--noautoscript
--noSYS
--use_db_options={0}
--options={1}
--ts_remap={2}
--dir={3}
--script={4}
--target_log={5}
'''.format(','.join(install.database_options()), 
                   ','.join(install.include_sdk_options()), 
                   ','.join([k + ':' + v for k, v in install.partition_map().items()]),
                   sdkDir,
                   thisName + '_sdk',
                   targetLog)

    if test:
        sdkInstall = sdkInstall + "--test\n"

    productInstall = config + '''
--use_db_options={0}
--noSYS
--noSVN
--target_log={1}
--dir={2}
'''.format(','.join(install.database_options()), 
           targetLog,
           myDir)
    if optionsOnly:
        productInstall = productInstall + "--options-only\n"
    else:
        productInstall = productInstall + "--noconfirm\n"
        
    if test:
        productInstall = productInstall + "--test\n"
    
    if compress is not None:
        productInstall = productInstall + "--compressIntoScript={0}\n".format(compress)
        
    
    
    def call():
        if optionsOnly or compress is not None:
            print ("INSTALLING PRODUCT")
            install.impl(productInstall)
        else:
            print ("INSTALLING FULL STACK")
            if install.impl(sysInstall):
                import_python_lib(os.path.join(sdkDir, 'install', 'install_sdk.py')).impl(sdkInstall)
                install.impl(productInstall)
    
    tools.execute(lambda: call(), ui)
