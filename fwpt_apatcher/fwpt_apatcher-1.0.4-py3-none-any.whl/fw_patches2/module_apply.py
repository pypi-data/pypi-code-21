'''
Created on 30.08.2011

@author: raidan
'''
from fw_patches2 import tools, Const
from fw_patches2.ApplyPatch import ApplyPatch
from fw_patches2.Const import SDK_DIR, OSS_DIR
from fw_patches2.Prepare import PatchPrepare
from fw_patches2.tools import PatchException
from os import path
import glob
import os
import time
from optparse import OptionParser

patch_list = []

# TODO: сделать красивый вывод на экран
def show_message(message, level=0):
    _str = ' ' * level
    print (_str, message)

def impl():
    parser = OptionParser()
    parser.add_option("--log", action="store_true", dest="log", default=False,
                      help="Name for file we use for logging")
    
    parser.add_option("--auto", action="store_true", dest="auto", default=False,
                      help="Auto execute all scripts")
    parser.add_option("--noauto", action="store_false", dest="auto",
                      help="Turn off auto execute")
    
    parser.add_option("--confirmAll", action="store_true", dest="confirmAll", default=False,
                      help="Say yes to all confirms")
    
    parser.add_option("--separate", action="store_true", dest="separate", default=False,
                      help="Separate checking and execution for every subproject")
    
    parser.add_option("--nosvn", action="store_true", dest="nosvn", default=False,
                      help="Turn off SVN update")
    
    parser.add_option("--core_db_options", dest="core_db_options",
                      help="Core database options like partition")
    
    parser.add_option("--root", dest="root", default="..",
                      help="Root directory for execution")
    
    parser.add_option("--project", dest="project",
                      help="Project name we using for execute")
    
    parser.add_option("--apply", dest="apply", default="re",
                      help="Default mode to use")
    
    parser.add_option("--connection", dest="connection",
                      help="Connection name to use")
    
    parser.add_option("--direct", dest="direct",
                      help="Direct name")
    
    parser.add_option("--remap_tablespace", dest="remap_tablespace", 
                      help="Tablespace remapping")
    
    parser.add_option("--check_invalid", dest="check_invalid", default=False,
                      help="Check new invalid objects")
    
    (options, _) = parser.parse_args()

    root = options.root
    project = options.project
    connection = options.connection
    core_db_options = None
    if options.core_db_options is not None:
        core_db_options = options.core_db_options.split(',')
    apply=options.apply
    if apply == '':
        apply = 're'
        
    connectionString = None
    
    # ++ check_patches
    def check_patches(_core_db, patcher, applier, project, apply, sdk_options=None,
                      include_sdk_options=None, database_options=None, partition_map=None,
                      force_project_map=False):
        
        # ---
        applier.option_mode(sdk_options, include_sdk_options, database_options, partition_map, force_project_map)
        
        print('Running patches for project {0}: {1}'.format(project, apply))
        files = []
        if apply in ['all', 're']:
            ver, _, lastfile = patcher.get_current_version('re')
            if apply != 'all':
                files.append(lastfile)
            else:
                system, db_version = _core_db.get_current_db_version(project)
                if applier.system is not None and system != applier.system:
                    raise BaseException(('\n\nERROR.\nDatabase system is {}, but ' + 
                            'you applying patches for {}.\nPlease ' + 
                            'ensure you done things right.').format(system, applier.system))
                if db_version is None or system is None:
                    if project is not None:
                        print ("You don't have required option: {}".format(project))
                        return True
                    else:
                        raise BaseException('\n\nERROR.\nUnable to find required core version in database')
                else:
                    if db_version == ver:
                        print ('You already have the newest version: {}'.format(ver))
                        return True
                    elif db_version > ver:
                        raise BaseException(('Misconfiguration. Database version is {}, but ' + 
                                'you have only {} in the repository dir. Please ' + 
                                'update your local repository.').format(db_version, ver))
                    # create range for standard processing
                apply = str(db_version + 1) + '-' + str(ver)
        
        if apply not in ['all', 're']:
            if '-' in apply:
                vfrom, vto = apply.split('-', 1)
                print ('Range of versions for apply. From {0} to {1} including both'.format(vfrom, vto))
            
                vfrom, vto = int(vfrom), int(vto)
            else:
                print ('Using version for apply', apply)
                vfrom = vto = int(apply)        
            
            # Before applying -- calculate all required patches
            for rec in range(vfrom, vto + 1):
                ver, _, lastfile = patcher.get_current_version(rec) 
                files.append(lastfile)
            
            if len (files) == 0:
                raise BaseException('Unable to find any patch file from', apply)
        
        if options.separate:
            # Раздельное выполнение
            return applier.check_and_apply(files, project)
        else:
            if applier.check(files, project):
                patch_list.append([project, files, sdk_options, include_sdk_options, database_options,
                                   partition_map, force_project_map])
                return True
            return False
            
    
    # -- check_patches
    
    # Конфиг по умолчанию
    file = 'config.txt'
    if path.isfile(file):
        map_ = tools.readfile(file)
        if connection is None:
            connection = 'db.default'
        else:
            connection = 'db.' + connection

        show_message('Using connection ID [{0}]'.format(connection))
        if connection not in map_:
            raise PatchException('Unable to find connection name [{0}] in {1}'.format(connection, path.realpath(file)))
        connectionString = map_[connection]
        
        
        if root is None:
            if 'root' not in map_:
                raise PatchException('Unable to find root directory in args or {0}'.format(connection, path.realpath(file)))
            root = map_['root']
    
    if connectionString is None:
        raise PatchException("Expected connection string to apply patches")
    
    if root is None:
        raise PatchException("Expected root dir to project to apply patches")

    # Настраиваем файл логов
    log_dir = None
    if options.log:
        log_dir = 'apply_log'
        if not path.exists(log_dir):
            os.mkdir(log_dir)
            
        safeStamp = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime())
        log_dir = path.join(log_dir, "{0}_{1}".format(safeStamp, apply))
        if not path.exists(log_dir):
            os.mkdir(log_dir)

    if not options.nosvn:
        show_message('Updating SVN from [{0}]'.format(root))
        tools.update_svn(root)
    
    patcher = PatchPrepare(root, update_svn=False)
    applier = ApplyPatch(rootDir=root, connectionString=connectionString, log_dir=log_dir, \
                         autoConfirm=options.confirmAll, update_svn=False, check_invalid=options.check_invalid)
    
    if options.direct is not None:
        show_message('Execute direct patch [{0}]'.format(options.direct))
        applier._apply([options.direct])
        return
    
    partition_map = None
    is_sdk = False
    if options.auto:
        show_message('Using auto patches for [{0}]'.format(root))
        
        install_dir = path.join(applier.get_patches_dir(), '..', 'install')
                
        project = None
        
        # Вычислим, что нам нужно выполнить для корректной работы
        install = None
        for found in glob.glob(path.join(install_dir, 'install_*.py')):
            if install is not None:
                raise PatchException('Too many install_*.py files in directory {0}'.format(install_dir))
            install = tools.import_python_lib(found)
        print ('Configuring', install.product())
        project = install.product()
        if core_db_options is None:
            core_db_options = install.database_options()
        
        # Не нужно ли выполнить патчи OSS?
        oss_dir = path.realpath(path.join(applier.get_patches_dir(), '..', OSS_DIR))
        
        # Не нужно ли выполнить патчи SDK?
        # Проверим их нахождение внутри OSS
        sdk_dir = path.realpath(path.join(applier.get_patches_dir(), '..', SDK_DIR))
        if not path.exists(sdk_dir):
            sdk_dir = path.realpath(path.join(oss_dir, SDK_DIR))
            
        if path.exists(sdk_dir):
            # SDK first
            project = None
            print ('\n\n------------------------ ')
            print ('Applying SDK patches first')
            
            # Какие опции включаем?
            include_sdk_options = install.include_sdk_options()
            database_options = install.database_options()
            partition_map = install.partition_map()
            if options.remap_tablespace is not None:
                # Скорректируем
                if partition_map is not None:
                    new_map = {}
                    for key in partition_map:
                        new_map[partition_map[key]] = options.remap_tablespace
                    partition_map = new_map
                    print ('\nCurrent remap:', partition_map)
                
                partition_map[Const.TABLESPACE_BIG] = options.remap_tablespace 
                partition_map[Const.TABLESPACE_ARCHIVE] = options.remap_tablespace
                partition_map[Const.TABLESPACE_NORMAL] = options.remap_tablespace
                
            print ('\nTarget tablespace remap:', partition_map)
                
            
            install_sdk = tools.import_python_lib(path.join(sdk_dir, 'install', 'install_sdk.py'))
            
            # Какие опции доступны?
            sdk_options = install_sdk.list_sdk_options()
            
            # Устанавливаем в режиме проекта
            patcher_sdk = PatchPrepare(sdk_dir, update_svn=False)
            applier_sdk = ApplyPatch(rootDir=sdk_dir, connectionString=connectionString, \
                                     log_dir=log_dir, autoConfirm=options.confirmAll, update_svn=False, check_invalid=options.check_invalid)
            
            # Выполним патчи SDK с фильтрами
            if not check_patches(applier, patcher_sdk, applier_sdk, install_sdk.product(), 'all',
                                 sdk_options, include_sdk_options, database_options, partition_map):
                return
        else:
            is_sdk = True
            
        if path.exists(oss_dir):
            # OSS next
            print ('\n\n------------------------ ')
            print ('Applying OSS patches next')
            
            install_oss = tools.import_python_lib(path.join(oss_dir, 'install', 'install_oss.py'))
            assert include_sdk_options is not None
            assert database_options is not None
            assert partition_map is not None
            
            patcher_oss = PatchPrepare(oss_dir, update_svn=False)
            applier_oss = ApplyPatch(rootDir=oss_dir, connectionString=connectionString, \
                                     log_dir=log_dir, autoConfirm=options.confirmAll, update_svn=False, check_invalid=options.check_invalid)
                
            # Сначала прогоняем core патчи для OSS, потом патчи его плагинов
            print ('\n\n------------------------ ')
            print ('Applying OSS core patches')
            if not check_patches(applier, patcher_oss, applier_oss, install_oss.product(), 'all',
                                 sdk_options, include_sdk_options, database_options, partition_map, True):
                return
            
            sub_options = install.include_sub_options()
            print ('Searching for sub-options:', sub_options)
            
            if sub_options is None or len(sub_options) == 0:
                print ('No sub-options')
            
            else:
                print ('\nApplying sub-options')
                for option in sub_options:
                    print('\n\n')
                    system, version = applier.get_current_db_version(option)
                    if version is None:
                        raise PatchException('Misconfiguration. Required sub-option not found in schema: {0}'.format(option))
                    
                    print ('\n------------------------ ')
                    print ('SUB-OPTION {0}/{1}'.format(system, version))
                    new_root = path.join(oss_dir, 'option_{0}'.format(option))
                    patcher_suboption = PatchPrepare(new_root, update_svn=False)
                    applier_suboption = ApplyPatch(rootDir=new_root, connectionString=connectionString, \
                                             log_dir=log_dir, autoConfirm=options.confirmAll, update_svn=False, check_invalid=options.check_invalid)
                    if not check_patches(applier, patcher_suboption, applier_suboption, option, 'all'):
                        return
            

    print ('\n\n------------------------ ')
    print ('Applying core patches')
    if not check_patches(applier, patcher, applier, project, apply, database_options=core_db_options,
                         partition_map=partition_map):
        return
    
    if options.auto and not is_sdk:
        # Вычислим, нет ли у нас тучи опций?
        assert install is not None, "expected ready install object"
        product_options = install.available_options()
        print ('Searching for product options:', product_options)
        if product_options is None or len(product_options) == 0:
            print ('No options')
        
        else:
            print ('\nApplying product options at least')
            for option in product_options:
                print('\n\n')
                system, version = applier.get_current_db_version(option)
                if version is None:
                    print ('Option [{0}] is not available for this installation'.format(option))
                    continue
                
                print ('\n------------------------ ')
                print ('OPTION {0}/{1}'.format(system, version))
                new_root = path.join(root, 'option_{0}'.format(option))
                patcher_project = PatchPrepare(new_root, update_svn=False)
                applier_project = ApplyPatch(rootDir=new_root, connectionString=connectionString, \
                                         log_dir=log_dir, autoConfirm=options.confirmAll, update_svn=False, check_invalid=options.check_invalid)
                if not check_patches(applier, patcher_project, applier_project, option, 'all', \
                                     partition_map=partition_map):
                    return
    
    # Запускаем
    if not options.separate:
        if not applier.confirm([item for files in patch_list for item in files[1]]):
            return
        
        print ('\n\n--------------------------------------------------------------------------------')
        for project, files, sdk_options, include_sdk_options, database_options, partition_map, force_project_map in patch_list:
            if project is None:
                print ("\n\nUSING CORE\n")
            else:
                print ("\n\nUSING [{0}]\n".format(project))
            applier.option_mode(sdk_options, include_sdk_options, database_options, partition_map, force_project_map)
            applier._apply(files, project)

def apply():        
    tools.execute(impl)


if __name__ == '__main__':
    apply()
