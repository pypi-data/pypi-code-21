'''
Created on 25.08.2010

@author: raidan
'''
from fw_patches2 import tools
from fw_patches2.Const import * #@UnusedWildImport
from fw_patches2.Prepare import PatchPrepare
from fw_patches2.tools import PatchException, print_last_errors
import getopt
import glob
import os
import subprocess
import sys
import re

print('\n >> {0} generate\n'.format(SYSTEM))

class GenerateScript():
    def __init__(self, schemaVersion):

        self.setScriptPrefix(INSTALL_SCRIPTS_DIR)
        self.setSourcePrefix(SYSOBJECTS_DIR)
        self.setSysScripts()
        self.setScripts()
        self.setTestScripts()
        self.setPostScripts()
        self.setMigrateScripts()
        
        self.system = schemaVersion
        self.generatedFiles = None
        
    def autoInit(self, args=None):
        '''
        Подготовка класса к генерации (анализ переданных извне переменных)
        '''
        if args is None:
            args = sys.argv[1:]
        else:
            args = [x.strip() for x in args.strip().split('\n')]
            args.extend(sys.argv[1:])
            
        print("Available args:", args)
        try:
            optlist = getopt.getopt(args, '', ['dir=', 'script=', 'database=', 'sys=', 'schema=',
                                               'schema_passw=', 'dbtype=', 'use_db_options=',
                                               'ts_remap=', 'test', 'migrate', 'options=',
                                               'options-only', 'noSYS', 'onlySYS', 'notest',
                                               'confirm', 'autoscript', 'noconfirm',
                                               'noautoscript', 'noSVN', 'target_log=',
                                               'compressIntoScript=', 'project=', 'force', 'startAQ'])
        except Exception as e:
            print (e) # will print something like "option -a not recognized"
            sys.exit(2)

        optmap = dict(optlist[0])
        
        # dirName
        autoscript = '--autoscript' in optmap and '--noautoscript' not in optmap
        
        if '--dir' in optmap:
            self.dirName = os.path.realpath(optmap.get('--dir'))
            print ("Using root dir", self.dirName)
        elif autoscript:
            _file_path, _ = os.path.split(sys.argv[0])
            self.dirName = os.path.realpath(os.path.join(_file_path, '..'))
            print ("Using auto root dir", self.dirName)
        else:
            raise PatchException("Unable to guess which dir we are using. No --dir and no --autoscript")
            
        

        self.schema = optmap.get('--schema')
        self.password = optmap.get('--schema_passw')

        if '--force' in optmap:
            self.mode = 'FORCE'
        else:
            self.mode = 'NORMAL'

        database = optmap.get('--database')
        
        self.sysAccount = '"{0}"@{1} as sysdba'.format(optmap.get('--sys'), database)
        self.account = '{0}/{1}@{2}'.format(self.schema, self.password, database)
        self.hasTest = '--test' in optmap and not '--notest' in optmap
        self.noSYS = '--noSYS' in optmap
        self.onlySYS = '--onlySYS' in optmap
        self.startAQ = '--startAQ' in optmap
        self.type = None
        if '--dbtype' in optmap:
            tmp = optmap.get('--dbtype')
            if tmp != "":
                self.type = tmp
        
        self.typedScripts = None
        self.hasMigrate = False
        if '--migrate' in optmap:
            self.hasMigrate = True
        
        self.optionsMap = dict()
        self.optionsTestMap = dict()
        self.optionsVersionMap = dict()
        self.options = None
        if '--options' in optmap:
            tmp = optmap.get('--options')
            if tmp != "":
                self.options = tmp.split(',')
            
        self.optionsOnly = False
        if '--options-only' in optmap:
            self.optionsOnly = True
            
        self.dbOptions = []
        if '--use_db_options' in optmap:
            tmp = optmap.get('--use_db_options')
            for item in tmp.split(","):
                self.dbOptions.append(item)
                
        self.projectScript = None
        self.projectVersion = None
        self.project = None
        if '--project' in optmap:
            self.project = optmap.get('--project')

        self.tablespaceRemap = {}
        if '--ts_remap' in optmap:
            tmp = optmap.get('--ts_remap')
            for map_ in tmp.split(","):
                from_, to_ = map_.split(':')
                self.tablespaceRemap[from_] = to_
        
        if '--confirm' in optmap and not '--noconfirm' in optmap:
            if self.optionsOnly:
                confirm = input('\n\nAre you sure to install option {3} {0}/{1}@{2}? (y/n): '.
                         format(self.schema, self.password, database, self.options))
            else:
                confirm = input('\n\nAre you sure to drop and create {0}/{1}@{2}? (y/n): '.
                         format(self.schema, self.password, database))
            if confirm.upper() != 'Y':
                print('Did not sure')
                return False


        self.noSVN = '--noSVN' in optmap
        
        self.stdout = sys.stdout
        
        logName = None
        fmode = 'w'
        if '--script' in optmap:
            _dir, _ = os.path.split(sys.argv[0])
            #logName = os.path.join(self.dirName, INSTALL_DIR, os.path.split(optmap.get('--script'))[1] + ".log")
            logName = os.path.join(_dir, optmap.get('--script') + ".log")
        elif autoscript:
            logName = sys.argv[0] + ".log"
        
        if "--target_log" in optmap:
            logName = optmap.get('--target_log')
            fmode = 'a'
        
        
        self.logName = None
        if logName is not None:
            logName = os.path.realpath(logName)
            print("\n\n------------------------------\nExecuting script. See log in", logName)
            self.logName = logName
            sys.stdout = open(logName, mode=fmode, encoding=DEFAULT_ENCODING)
            
        self.compressIntoScript = None
        if '--compressIntoScript' in optmap:
            self.compressIntoScript = os.path.realpath(optmap.get('--compressIntoScript'))
         
        return True
    
    def setScriptPrefix(self, scriptPrefix):
        self.scriptPrefix = scriptPrefix
    
    def setSourcePrefix(self, sourcePrefix):
        self.sourcePrefix = sourcePrefix
        
    def setSysScripts(self, *sysScriptNames):
        self.sysScriptNames = sysScriptNames
        
    def setScripts(self, *scriptNames):
        self.scriptNames = scriptNames
        
    def setTestScripts(self, *testScriptNames):
        self.testScriptNames = testScriptNames
        
    def setPostScripts(self, *postScriptNames):
        self.postScriptNames = postScriptNames
        
    def setAutoGenerateDirs(self, *dirs):
        self.dirs = dirs
     
    def setAutoGenerateDirArray(self, dirs):
        self.dirs = dirs
        
    def setTypedScripts(self, type_, *typedScripts):
        if self.type == type_:
            print('Using typed {0}'.format(type_), file=self.stdout)
            self.typedScripts = typedScripts
            
    def setMigrateScripts(self, *migrateScriptNames):
        self.migrateScriptNames = migrateScriptNames
        
    def addOptionScripts(self, optionName, *optionScriptNames):
        if self.options is None:
            return
        
        if optionName in self.options:
            print(' + option {0}'.format(optionName), file=self.stdout)
            self.optionsMap[optionName] = optionScriptNames
            
    def addOptionTestScripts(self, optionName, *optionScriptNames):
        if self.options is None:
            return
        
        if optionName in self.options:
            self.optionsTestMap[optionName] = optionScriptNames
            
    def addOptionVersionScript(self, optionName, versionScript):
        if self.options is None:
            return
        
        if optionName in self.options:
            self.optionsVersionMap[optionName] = versionScript

    def addProjectScripts(self, projectName, *projectScriptNames):
        if self.project is None:
            return

        if projectName == self.project:
            print(' + project {0}'.format(projectName), file=self.stdout)
            self.projectScript = projectScriptNames

    def addProjectVersionScript(self, projectName, versionScript):
        if self.project is None:
            return

        if projectName == self.project:
            self.projectVersion = versionScript


                    ############################
    def generate(self, readonly=False):

                
        curdir = os.curdir
        '''
        Генерация и выполнение скриптов для разворачивания схемы
        '''
        try:
            os.chdir(self.dirName)
            print ("CHDIR", self.dirName, file=self.stdout)
            self._auto_generate()
            
            if not self.compressIntoScript:
                if not self.optionsOnly and not self.noSYS and self.sysScriptNames:
                    self._run_scripts(readonly, self.sysAccount, 'SYS', self.sysScriptNames)
                    
                if not self.onlySYS:
                    if not self.optionsOnly and self.scriptNames:
                        self._run_scripts(readonly, self.account, 'INIT', self.scriptNames)
                        
                    if not self.optionsOnly and self.typedScripts:
                        self._run_scripts(readonly, self.account, 'TYPED', self.typedScripts)
                       
                    for k, v in self.optionsMap.items():
                        self._run_scripts(readonly, self.account, 'OPTION "' + k + '"', v)
                    
                    if not self.optionsOnly and self.hasTest:
                        if self.testScriptNames:
                            self._run_scripts(readonly, self.account, 'TEST', self.testScriptNames)
                        if self.optionsTestMap is not None:
                            for k, v in self.optionsTestMap.items():
                                self._run_scripts(readonly, self.account, 'TEST OPTION "' + k + '"', v)
                        if self.projectScript is not None:
                            self._run_scripts(readonly, self.account, 'PROJECT "' + self.project, self.projectScript)
                    
                    if not self.optionsOnly and  self.hasMigrate and self.migrateScriptNames:
                        self._run_scripts(readonly, self.account, 'MIGRATE', self.migrateScriptNames)
                        
                    if self.postScriptNames:
                        self._run_scripts(readonly, self.account, 'POST', self.postScriptNames)

                    if self.startAQ:
                        self._run_scripts( readonly, self.account, 'START AQ', START_AQ_SCRIPT)
        finally:
            self._remove_auto_generate()
            sys.stdout = self.stdout
            os.chdir(curdir)
        
    def _run_scripts(self, readonly, account, descr, list_):
        '''
        Запуск указанного списка скриптов с помощью SQLPLUS
        '''
        if list_ is None:
            return
        
        for pos, file in enumerate(list_):
            print("Executing '{3}' {0} of {1}: '{2}'".format(pos , len(list_), file, descr), file=self.stdout)
            
            line = (SQLPLUS_GENERATE.format(self.scriptPrefix + file, account=account)).format(schema=self.schema, password=self.password, mode=self.mode)
            print ("\n------\nExecute: {0}\n".format(line))
            if not readonly:
                proc = subprocess.Popen(line, bufsize=10, shell=True, stdin=subprocess.PIPE, stdout=sys.stdout)
                proc.communicate()
                ret = proc.wait()
                if ret != 0:
                    print_last_errors(self.logName, self.stdout)    
                    raise BaseException('Failed executing script {0}. Return error code: {1}'.format(
                                        line, ret))
                
                            
    def _update_schema_version(self):
        '''
        Обновление файла, хранящего текущий номер патча.
        Нужен для того, чтобы при создании инсталляции знать, какой патч эта инсталляция в себя уже включает.
        '''
        prepare = PatchPrepare(self.dirName, update_svn=not self.noSVN)
        ver, _, _ = prepare.get_current_version(RE)
        
        target = os.path.join(self.dirName, SYSOBJECTS_DIR , INIT_DIR, SCHEMA_VERSION)
        with open(target, mode='w', encoding=DEFAULT_ENCODING) as file:
            print ("Using last version {0}, SYSTEM '{1}'".format(ver, self.system))
            file.write(SCHEMA_VERSION_TEMPLATE.format(self.system, ver))
            
        if self.options is not None:
            for option in self.options:
                self._update_schema_option_version(option)

        if self.project is not None:
            self._update_schema_project_version(self.project)
            
    def _update_schema_option_version(self, option):
        '''
        Обновление файла, хранящего текущий номер патча опции.
        Нужен для того, чтобы при создании инсталляции знать, какой патч эта инсталляция в себя уже включает.
        '''
        if not option in self.optionsVersionMap:
            return

        prepare = PatchPrepare(os.path.join(self.dirName, 'option_{0}'.format(option)))
        ver, _, _ = prepare.get_current_version(RE)
        
        target = os.path.join(self.dirName, SYSOBJECTS_DIR) + '/' + self.optionsVersionMap[option] 
        with open(target, mode='w', encoding=DEFAULT_ENCODING) as file:
            projname = option.upper()
            print ("Using last version {0}, PROJECT '{1}'".format(ver, projname))
            file.write(SCHEMA_VERSION_PROJECT_TEMPLATE.format(projname, ver))

    def _update_schema_project_version(self, project):
        '''
        Обновление файла, хранящего текущий номер патча проекта.
        '''
        if self.projectVersion is None:
            return

        prepare = PatchPrepare(os.path.join(self.dirName, 'projects/{0}'.format(project)))
        ver, _, _ = prepare.get_current_version(RE)

        target = os.path.join(self.dirName, SYSOBJECTS_DIR) + '/' + self.projectVersion
        with open(target, mode='w', encoding=DEFAULT_ENCODING) as file:
            projname = project.upper()
            print("Using last version {0}, PROJECT '{1}'".format(ver, projname))
            file.write(SCHEMA_VERSION_PROJECT_TEMPLATE.format(projname, ver))

    def _filter_db(self, filename):
        '''
        Анализ содержимого файлов и выкидывание всего, что не подходит под опции текущей инсталляции
        '''
        filebody = tools.loadfile(filename)
        lines = tools.basic_filter(filebody.split('\n'), self.dbOptions, self.tablespaceRemap)
        _file_path, _file_name = os.path.split(filename)
        
        filename_ret = os.path.join(_file_path, "_auto_generate_temp_" + _file_name)
        tools.savefile(filename_ret, '\n'.join(lines))
        
        return filename_ret
    
    def _auto_generate(self):
        '''
        Создание списка файлов (на основе пераданных настроек)
        '''
        print("Preparing auto generated scripts...", file=self.stdout)
        
        self._update_schema_version()
        
        self.generatedFiles = []
        
        sysobject_dir = os.path.realpath(os.path.join(self.dirName, self.sourcePrefix))
        print('Using sysobjects dir', sysobject_dir)
        
        full_refs = []
        full_excludes = []
        for dir_ in self.dirs:
            parts = dir_.split(":")
            
            partDir, partName = os.path.split(parts[0])
            target = os.path.realpath(os.path.join(sysobject_dir, partDir, partName))
            
            print('\n + target ', target, os.path.exists(target))
            if not os.path.exists(os.path.split(target)[0]):
                print ("Ignore target, directory not exists for", target)
                continue
            
            with open(target, mode='w', encoding=DEFAULT_ENCODING) as file:
                file.write("")

            self.generatedFiles.append(target)
            
            refs = []
            excludes = []
            subdirs = parts[1].split(",")
            for sub in subdirs:
                sub = sub.lstrip()
                
                exclude = False
                rootOnly = False
                checkDB = False
                skipCompress = False
                if sub[:1] == EXCLUDE_PREFIX:
                    sub = sub[1:]
                    exclude = True
                if sub[:1] == ROOT_PREFIX:
                    sub = sub[1:]
                    rootOnly = True
                if sub[:1] == CHECK_DBOPTION_PREFIX:
                    sub = sub[1:]
                    checkDB = True
                if sub[:1] == SKIP_COMPRESS:
                    sub = sub[1:]
                    skipCompress = True
                    
                
                # sub выглядит как init/data/flexy@/*.sql
                # Говнокод во все поля :(
                mapDir, currentTemplate = os.path.split(sub)
                currentDir = os.path.realpath(os.path.join(sysobject_dir, mapDir))
                print ("  + scanning {0} ({1}/{2}), exclude {3}, root only {4}".format(currentDir, mapDir, currentTemplate, exclude, rootOnly))

                for dirpath, _, _ in os.walk(currentDir):
                    if '.svn' in dirpath:
                        continue
                    
                    print (' dir_ ', dirpath)
                    for found in glob.glob(os.path.join(dirpath, currentTemplate)):
                        if found == target:
                            continue
                        
                        if rootOnly and os.path.split(found)[0] != currentDir:
                            continue
                        
                        filename = found[len(self.dirName) + 1:]
                        full_filename = os.path.realpath(filename)
                        
                        if exclude:
                            excludes.append(filename)
                            if not skipCompress:
                                full_excludes.append(full_filename)
                            print ('  - remove file ', filename)
                        else:
                            if checkDB:
                                print ('  ! scan file ', filename, found)
                                filename = self._filter_db(filename)
                                full_filename = os.path.realpath(filename)
                                if os.path.realpath(filename) == target:
                                    raise BaseException("Unexpected error. " + 
                                                        "Auto generated name is equals with target: " + target) 
                                self.generatedFiles.append(full_filename)
                                
                            if filename in refs:
                                refs.remove(filename)
                            refs.append(filename)
                            
                            if not skipCompress:
                                if full_filename in full_refs:
                                    full_refs.remove(full_filename)
                                full_refs.append(full_filename)
                            print ('  + add file ', filename, found)

            for e in excludes:
                if e in refs:
                    refs.remove(e)
            
                                
            with open(target, mode='a', encoding=DEFAULT_ENCODING) as file:
                for ref in refs:
                    file.write('@{0}\n'.format(ref))
                    
            print ('\nAUTOGENERATE DONE')
            sys.stdout.flush()
            
        if self.compressIntoScript is not None:
            for e in full_excludes:
                if e in full_refs:
                    full_refs.remove(e)
                    
            print('Compressing into one big script...')
            with open(self.compressIntoScript, mode='w', encoding=DEFAULT_ENCODING) as file:
                for filename in full_refs:
                    file.write('\n\n------ {0}\n'.format(filename))
                    with open(filename, mode='r', encoding=DEFAULT_ENCODING) as read_file:
                        file.write(self._filter_compressing_file(read_file.read()))
                    file.write('\n')
        

    def _filter_compressing_file(self, filebody):
        
        type_line_pattern = re.compile(AUTO_TYPE, re.IGNORECASE)
        
        lines = filebody.split('\n')
        drop_lines = []
        for line in lines:
            found = type_line_pattern.search(line)
            if found:
                drop_lines.append("exec execute_('drop type {0} force')\n".format(found.group(1)))
        
        
        if len(drop_lines) > 0:
            return '--- Auto drop types!\n' + '\n'.join(drop_lines) + '---\n\n' + filebody
        else:
            return filebody

    def _remove_auto_generate(self):
        '''
        Удаление файлов, которые мы нагенерили методом _auto_generate
        '''
        print('Removing generated files', file=self.stdout)
        if not self.generatedFiles is None:
            for target in self.generatedFiles:
                print(' - removing file:', target)
                try:
                    os.remove(target)
                except:
                    print ('Error on removing file', target)
