'''
Created on 07.10.2009

@author: raidan
'''
from _pyio import open
from fw_patches2 import tools
from fw_patches2.Const import * #@UnusedWildImport
from fw_patches2.tools import PatchException, print_last_errors
import copy
import cx_Oracle
import os
import re
import shutil
import subprocess
import sys

print('\n >> {0} apply\n'.format(SYSTEM))

class ApplyPatch():
    '''
    Класс для выполнения патчей в БД. Позволяет также получить текущую версию (базовую или для проекта).
    Решение о выполнении конкретных патчей принимается извне.
    '''
    
    def __init__(self, rootDir, connectionString, system=None, log_dir=None, autoConfirm=False, update_svn=True, check_invalid=False):
        assert rootDir is not None, 'Expected not empty rootDir'
        assert connectionString is not None, 'Expected not empty connectionString'
        
        self.forceProjectMap = False
        self.connectionString = connectionString
        self.rootDir = rootDir
        self.patchesDir = os.path.realpath(os.path.join(self.rootDir, PATCHES_DIR))
        self.sysobjectsDir = os.path.realpath(os.path.join(self.rootDir, SYSOBJECTS_DIR))
        
        self.encoding = DEFAULT_ENCODING
        self.system = system
        
        self.autoConfirm = autoConfirm
        self.log_dir = log_dir
        
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        
        self.removeOptions = None
        self.dbOptions = None
        self.tablespaceRemap = {}
        
        self.connection = None
        
        self.check_invalid = check_invalid
        
        ########################
        if update_svn:
            tools.update_svn(self.patchesDir)
        
    def __del__(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            
        
    def _get_connection(self):
        '''
        Returning connection
        '''
        if self.connection is None:
            auth = self.connectionString
            print ('\nLOG INTO', auth)
            self.connection = cx_Oracle.connect(auth)
        
        return self.connection

        
    def get_patches_dir(self):
        '''
        Получение текущего каталога с патчами
        '''
        return self.patchesDir
        
    def option_mode(self, availableOptions, currentOptions, dbOptions, tablespaceRemap, forceProjectMap):
        '''
        Переводим систему в режим работы с опциями продукта.
        Если в currentOptions не присутствует опция (фактически, её название, т.е. строка),
        то данная опция будет вырезана из патча при его формировании.
        '''
        #print ('Use {0}/{1}/{2}/{3}'.format(availableOptions, currentOptions, dbOptions, tablespaceRemap))
        
        self.forceProjectMap = forceProjectMap
        availableOptions = copy.copy(availableOptions)
        currentOptions = copy.copy(currentOptions)
        dbOptions = copy.copy(dbOptions)
        tablespaceRemap = copy.copy(tablespaceRemap)
         
        
        self.dbOptions = dbOptions
        self.tablespaceRemap = tablespaceRemap
        
        if self.dbOptions is not None:
            for option in self.dbOptions:
                if option not in KNOWN_DBOPTIONS:
                    raise PatchException("Unable to find database option [{0}] in available options: {1}".format(option, KNOWN_DBOPTIONS))
        
        if availableOptions is None or currentOptions is None:
            self.removeOptions = None
            return
        
        for option in currentOptions:
            if not option in availableOptions:
                raise PatchException("Unable to find option [{0}] in available options: {1}".format(option, availableOptions))
        
        self.removeOptions = availableOptions
        for option in currentOptions:
            self.removeOptions.remove(option)
    

    def _pre_std(self, file, dir_=None):
        if self.log_dir is None:
            return False
        else:
            if dir_ is not None:
                idx = 0
                while True:
                    s = ''
                    if idx > 0:
                        s = str(idx)
                    real_log_dir = os.path.join(self.log_dir, dir_ + s)
                    if not os.path.exists(real_log_dir):
                        os.mkdir(real_log_dir)
                        break
                    idx += 1
                    
                
            else:
                real_log_dir = self.log_dir
                
            sys.stdout = open(os.path.join(real_log_dir, '{0}.log'.format(file)), mode='w', encoding=self.encoding) 
            sys.stderr = open(os.path.join(real_log_dir, '{0}.err'.format(file)), mode='w', encoding=self.encoding)            
        
            self.real_log_dir = real_log_dir
            
            return True
        
    def _post_std(self):
        if self.log_dir is not None:
            sys.stdout.flush()
            sys.stderr.flush()
            
            sys.stdout = self.stdout 
            sys.stderr = self.stderr 
            
    def get_current_db_version(self, project=None):
        '''
        Коннект к БД за поиском версии (системной из fw_version или проектной/опции из fw_version_project)
        '''
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if project is None:
                cursor.execute(SELECT_SIMPLE_VER)
            else:
                cursor.execute(SELECT_PROJECT_VER, proj=project.upper())
            for system, current_version, in cursor:                       
                print ('Current {0} database version = {1}'.format(system, current_version))
    
                return system, current_version
        finally:
            cursor.close()
        
        return None, None

    def get_invalids(self):
        if not self.check_invalid:
            return []
        
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("select object_name from user_objects where status = 'INVALID' order by object_name")
            names = []
            for object_name, in cursor:                       
                names.append(object_name)
            
            return names
        finally:
            cursor.close()

    def verify_patch_warning(self, patches, project=None):
        '''
        Требуем подтверждения для предупреждений в патчах (отмеченных специальными символами >>>)
        '''
        patchset = []
        for patch in patches:
            message = ''
            for line in self.filter_file(tools.loadfile(patch), project).split("\n"):
                if line.startswith(CONFIRM_MESSAGE_PREFIX):
                    message += line[len(CONFIRM_MESSAGE_PREFIX):]
                
                
            if message != '':
                patchset.append({'patch': patch, 'message': message})
        
        total = len(patchset)
        for i in range(0, total):
            rec = patchset[i]
            print('\n\n--------------------------------------')
            print('Patch {0}/{1}: {2}'.format(i + 1, total, rec['patch']))
            print(rec['message'])
            
            if self.autoConfirm:
                print('\nAuto confirm')
            else:
                confirm = input('Confirm? (y/n):')
                if confirm.upper() != 'Y':
                    print('\nDid not confirmed')
                    return False

            
        return True

    def check_database_version(self, patches, project=None):
        '''
        Для переданных патчей вычисляется их первый номер и идёт сравнение с номером текущего патча в БД.
        Данный метод вызовет исключение, если окажется, что мы пытаемся применить патч, не следующий за тем,
        который прописан в БД.
        '''
        
        assert patches != None, 'Patches required'
        
        self._pre_std('prepare')
        try:
            versions = []
            
            
            
            # Pattern for searching current_version 
            if project is None or self.forceProjectMap:
                print ('Using product')
                if self.forceProjectMap:
                    print ('Force remap non-project -> project', project)
                version_pattern = re.compile(VER_SIMPLE_PATTERN, re.IGNORECASE)
                version_pattern_proc = re.compile(VER_SIMPLE_PATTERN_PROC, re.IGNORECASE)
                version_group_matcher = 5
            else:
                print ('Using project [{0}]'.format(project))
                version_pattern = re.compile(VER_PROJECT_PATTERN + project + VER_PROJECT_PATTERN_END, re.IGNORECASE)
                version_pattern_proc = re.compile(VER_PROJECT_PATTERN_PROC + project + VER_PROJECT_PATTERN_PROC_END, re.IGNORECASE)
                version_group_matcher = 6
            for patch in patches:
                with open(patch, encoding=self.encoding) as file:
                    for line in file:
                        found = version_pattern.search(line)
                        # Found!
                        if found:
                            current_version = int(found.group(2))
                            print (' + Accepted applying patch', current_version)
                            versions.append(current_version)
                        else:
                            found_proc = version_pattern_proc.search(line)
                            if found_proc:
                                current_version = int(found_proc.group(version_group_matcher))
                                print (' + Accepted applying patch', current_version)
                                versions.append(current_version)
                    
                    
            if len(versions) == 0:
                raise PatchException(('Unable to extract current_version from files {0}. ' + 
                                    'Maybe, this is not patches?').format(patches))
                
            last = None
            for i in versions:
                if last is not None and last + 1 != i:
                    raise PatchException('Invalid patch set for versions {0}. Required full range.'.format(versions))
                last = i
            
            first_applying_ver = versions[0]
            
            
            system, db_version = self.get_current_db_version(project)
            if project is None and self.system is not None and self.system != '' and system != self.system:
                print ('\n\n<<< Error when checking system {0}. Current is {1} >>>\n'.format(self.system, system))
                raise PatchException(('\n\nINVALID SYSTEM VERSION.\nDatabase system = {0}. ' + 
                                      'Your patch is for system {1}. ' + 
                                      '\nMust be the same!').format(system, self.system))

                
            if first_applying_ver != db_version + 1:
                        print ('\n\n<<< Error when checking version {0}. Current is {1} >>>\n'.format(first_applying_ver, current_version))
                        raise PatchException(('\n\nINVALID PATCH.\nDatabase current_version = {0} ' + 
                                            'but you trying to apply version {1}. ' + 
                                            'Must be the next version.').format(db_version, first_applying_ver))
            else:
                print ('Version is correct. Ready to proceed.')
        finally:
            self._post_std()  


        if not self.verify_patch_warning(patches, project):
            print ('Patch applying is canceled')
            return False
        
        return True
    
    def filter_file(self, filebody, project=None):
        '''
        Фильтрация содержимого файла, в зависимости от необходимых опций.
        Используется для продуктов, основывающихся на Forward SDK а также для 
        переделки не-проектных патчей в проектные.
        '''
        
        
        # Опции
        if self.removeOptions is not None:
            for option in self.removeOptions:
                #print (' + FILTER option', option)
                from_ = OPTION_TEMPLATE_START.format(option)
                to_ = OPTION_TEMPLATE_END.format(option)
                
                while True:
                    fromPos = filebody.find(from_)
                    toPos = filebody.find(to_)
                    if fromPos >= 0 and toPos >= 0:
                        if toPos <= fromPos:
                            raise PatchException(('Unable to remove option from patch. ' + 
                                '{2} ({3}) found later than {0} ({1})').format(from_, fromPos, to_, toPos))
                        filebody = filebody[:fromPos] + '\n-- SKIPPED\n' + filebody[toPos + len(to_):]
                    else:
                        break
        
        
        lines = tools.basic_filter(filebody.split('\n'), self.dbOptions, self.tablespaceRemap)
        targetLines = []
        
        if self.forceProjectMap:
            if project is None:
                raise PatchException('Unable to make forceProjectMap. Project is none')
            
            version_pattern = re.compile(VER_SIMPLE_PATTERN, re.IGNORECASE)
            for line in lines:
                found = version_pattern.search(line)
                # Found!
                if found:
                    table = "FW_VERSION_PROJECT"
                    condition = " where V_PROJECT = '{0}';".format(project)
                    
                    line = " ".join([line[:found.start(1)], table, line[found.end(1):found.start(3)],
                                     condition, line[found.end(3):]])
                    #print (' + remap into project patch -> ', project)
                    #raise PatchException('brk')

                # -- >
                targetLines.append(line)
                
            # at least
            lines = targetLines
            targetLines = []
                    
        

        accept = True
        for line in lines:
            if line.strip() == DYNAMIC_END:
                accept = True
            elif line.startswith(DYNAMIC_START):
                
                condition = line[len(DYNAMIC_START):]
                if condition.startswith('?'):
                    condition = 'user_objects:object_name=' + condition[1:]
                
                # Динамические условия вида "-- ##<if>user_objects:object_name=PACK_AMS_IC_ORACLE"
                table, conditions = condition.split(':')
                sql = 'select count(*) from ' + table
                
                where = None
                for c in conditions.split(','):
                    column, value = c.split('=')
                    if where is None:
                        where = ' where '
                    else:
                        where += ' and '
                    where += ' ' + column + "='" + value + "'"
                
                if where is not None:
                    sql += where
                    
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute(sql)
                for count, in cursor:
                    if count > 0:
                        print (' ACCEPTED CONDITION', condition)
                        targetLines.append('')
                        targetLines.append('-- ACCEPTED IF CONDITION ' + condition) #  + ' : ' + str(count) + ' of ' + sql
                        accept = True
                    else:
                        print (' INACCEPTED CONDITION', condition)
                        targetLines.append('')
                        targetLines.append('-- SKIPPED IF CONDITION ' + condition)
                        accept = False
            else:
                if accept:
                    targetLines.append(line) 
                
                
        
        return '\n'.join(targetLines)
            

    def _apply(self, patches, project=None):
        '''
        Применение указанных патчей в БД.
        Предварительная проверка выполняться не будет.
        '''
        
        assert patches is not None, 'Expected patches to execute'
        
        print ('Applying patches:')
        
        # Very easy running
        totalCount = len(patches)
        currentNumber = 0
        for patch in patches:
            currentNumber = currentNumber + 1
            
            patch = os.path.realpath(patch)
            
            logfile = ''
            redirect = ''
            patchName = os.path.split(patch)[1]
            patchName0 = patchName
            if project is not None:
                patchName0 = tools.safe_filename(project) + '_' + patchName0
            if self._pre_std('execute', patchName0):
                logPath = self.real_log_dir
                shutil.copy(patch, logPath)
                patch = os.path.join(logPath, patchName) # Подменим!
                logfile = os.path.join(self.real_log_dir, 'sqlplus.log')
                redirect = ' > ' + logfile
                

            watch = tools.StopWatch()
            watch.start()                
            try:
                
                invalids_before = self.get_invalids()
                
                # Отфильтруем патч
                body = self.filter_file(tools.loadfile(patch, self.encoding), project)
                path, name = os.path.split(patch)
                patch = os.path.join(path, 'a' + name)
                tools.savefile(patch, body, self.encoding)
                
                line = SQLPLUS
                line = line.format(self.connectionString, redirect)
                
                self.stdout.write(' + [{0}/{1}] {2} ... '.format(currentNumber, totalCount, os.path.split(patch)[1]))
                self.stdout.flush()
                print ('Executing: [{0}]'.format(line))
                
                proc = subprocess.Popen(line, shell=True, stdin=subprocess.PIPE, \
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # We must tell SQLPlus to exit after applying patch
                # Also telling to property handle with errors
                # And do not forget about printing what we executing
                sql = SQL.format(patch)
                
                print ('Using script:', sql)
                print (' ------------------------------------ ')
                print ('Executing script...')
                
                # Well, actually I don't know how to print output right way
                def watcher(encoding, std):
                    for line in std:
                        if line is not None:
                            print(line.decode(encoding))

                # Do not forget about properly encoding!
                tools.WatchingThread(watcher(self.encoding, proc.communicate(sql.encode(self.encoding)))).start()
                
                
                ret = proc.wait()
                if ret != 0:
                    print_last_errors(logfile, self.stdout)    
                    raise PatchException('Failed executing script {0}. Return error code: {1}'.format(patch, ret))
                
                time = watch.stop()
                self.stdout.write('OK in {0:.2f} sec\n'.format(time))
                self.stdout.flush()
                
                invalids_after = self.get_invalids()
                if invalids_before != invalids_after:
                    diff = set(invalids_after) - set(invalids_before)
                    if len(diff) > 0:
                        print ('\n\n<<< Error when checking invalid objects. New invalid objects:\n')
                        for d in diff:
                            print(' <<< {0}\n'.format(d))
                        raise PatchException('New invalid objects after patch {0}'.format(patch))
                
                print('Executed successfully in {0:.2f} sec\n'.format(time))
            except:
                time = watch.stop()
                self.stdout.write('FAIL in {0:.2f} sec\n'.format(time))
                self.stdout.flush()
                print ('\n\n<<< Error when applying patch {0} >>>\n'.format(patch))
                raise
            finally:
                self._post_std()
                
    def check(self, patches, project=None):
        '''
        Проверка переданного списка патчей
        '''
        assert patches is not None, 'Expected patches to execute'
        assert len(patches) > 0, 'Invalid arguments, expected at least one patch for apply'  
        
        patches.sort()
        
        print ('\nChecking patch list:')
        for patch in patches:
            print (' + {0}'.format(patch))

        if not self.check_database_version(patches, project):
            print ('Did not checked')
            return False
        
        print ('Checked')
        return True
    
    def confirm(self, patches):
        if len(patches) == 0:
            print ('No patches actually found. Nothing to do')
            return False
        
        if self.system is None:
            print('\n\nThere are {0} patches will be APPLIED ON {1}'.format(len(patches), self.connectionString))
        else:
            print('\n\nThere are {0} patches for [{1}] will be APPLIED ON {2}'.format(len(patches), self.connectionString, self.system))
        
        if self.autoConfirm:
            print ('\nAuto confirm')
        else:
            confirm = input('Execute them all? (y/n):')
            if confirm.upper() != 'Y':
                print('Did not confirm')
                return False
        return True
    
    def apply(self, patches):
        '''
        Выполнение (уже проверенных) патчей'''
        if not self.confirm(patches):
            return False
        
        self._apply(patches)
        return True

    
    def check_and_apply(self, patches, project=None):
        '''
        Проверка и выполнение патчей
        '''
        return self.check(patches, project) and self.apply(patches)

