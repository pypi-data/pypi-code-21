'''
Created on 30.08.2011
@author: raidan
'''
from _pyio import open
from fw_patches2 import tools
from fw_patches2.Const import * #@UnusedWildImport
from fw_patches2.tools import PatchException
import glob
import os
import re
import shutil
import subprocess
import time

print('\n >> {0} prepare\n'.format(SYSTEM))

# Сбор патча
class PatchPrepare():
    
    def __init__(self, rootDir, ignoreFileCase=True, update_svn = True):
        assert rootDir is not None, 'Expected not empty root dir'
        
        self.ignoreFileCase = ignoreFileCase
        
        self.rootDir = rootDir
        self.patchesDir = os.path.realpath(os.path.join(self.rootDir, PATCHES_DIR))
        self.sysobjectsDir = os.path.realpath(os.path.join(self.rootDir, SYSOBJECTS_DIR))
                                           
        self.encoding = DEFAULT_ENCODING
        
        # Закэшированный список файлов
        self.all_sql_files = None
        self.destination_dir = None
        
        # Список файлов, которые могут быть включены в патч
        self.sysobjects_files = None
        
        
        # Автоматически вносить свежий патч в SVN
        self.auto_svn = True
        
        # Игнорировать наличие нескольких каталогов, оканчивающихся на XXXX
        self.ignoreVerXXXXX = False
        
        
        ########################
        if update_svn:
            tools.update_svn(self.patchesDir + ' ' + self.sysobjectsDir)
        
    def setIgnoreVerXXXXX(self, ignore):
        self.ignoreVerXXXXX = ignore

    def list_all_sql_files(self):
        '''
        Method returns list of all sql files, existed in special source path
        
        return list of files and name of destination dir (where we must place our patches)
        '''
        if self.all_sql_files is None:

            patchPath = self.patchesDir
            files = []
            
            # First of all -- let's find if sql's placed exactly in patchPath directory
            sql_direct = glob.glob(os.path.join(patchPath, SQL_PATH))
            if sql_direct:
                files = sql_direct
                dest = os.path.realpath(patchPath)
            else:

                # Checks only directory, started with year
                dirs = glob.glob(os.path.join(patchPath, VERSION_DIR_PREFIX))
                if len(dirs) == 0:
                    raise PatchException('Source path is empty. Cannot retrieve any file from source path ' + patchPath)
                    
                # Current patch dir must ends with this symbols 
                templateDest = LAST_VERSION_DIR_POSTFIX
                dest = None
    
                
                for path in dirs:
                    if path.endswith(templateDest):
                        if not self.ignoreVerXXXXX:
                            if dest is not None:
                                raise BaseException(('Found duplicate destination dirs: {0} and {1}. ' + 
                                                    'Expected only one which ends with {2}.').format(dest, path, templateDest))
                        dest = path
                    files.extend(glob.glob(os.path.join(path, SQL_PATH)))
            
                if dest is None:
                    raise PatchException('Not found destination directory ends with {0} in source path {1}'.
                                            format(templateDest, patchPath))
                
            if len(files) == 0:
                raise PatchException('Files are empty. Cannot retrieve any file from source path [{0}]'.format(patchPath))
                
            files.sort()
            self.all_sql_files, self.destination_dir = files, dest
        
        return list(self.all_sql_files), self.destination_dir

    
    def get_current_version(self, replace):
        '''
        Method returns current version of patch (last SQL for template)
        from the directory with patches
        
            replace -- we replacing version? One of these settings:
                None -- it means we return latest version + 1
                're' -- we return latest version
                123 -- version number, we return exactly given version with 
                    some of additional data
            
        return version (as integer), dest directory (where this file stores) 
            and full path for file with last version
            
        NOTE: We ALWAYS return current patch directory, no matter what
        But, required_file has a full path :)
        '''
        
        files, dest = self.list_all_sql_files()
        
        required_file = None
        # 2009-09-16_00300.sql --> 300
        template = re.compile(VERSION_FILE_TEMPLATE, re.IGNORECASE)
        
        if replace is not None and replace != RE:
            replace_int = int(replace)
            
            # usually we applying latest
            files.reverse()
            for file in files:
                found = template.search(file)
                if found and int(found.group(1)) == replace_int:
                    required_file = file
                    break
            if required_file is None:
                raise PatchException('Unable to find patch file [{0}]'.format(replace))
        else:
            required_file = os.path.realpath(files.pop())
    
        versionName = os.path.split(required_file)[1]
        
        ver = int(versionName[11:16])
        if replace is None:
            # Appending
            ver += 1
            
        return ver, dest, required_file

#####################
    def include_file_body(self, filename):
        '''
        Load file body and returns it with some additional comments.
        Returns text that can be include into script
        
            filename -- the file we must include
        '''
        
        assert filename != None, 'filename cannot be empty'
        
        simpleFilename = filename
        if simpleFilename.startswith(self.sysobjectsDir):
                simpleFilename = '...' + simpleFilename[len(self.sysobjectsDir):]
        
        print (' + Include file', simpleFilename)
        return INCLUDE_TEPLATE.format(simpleFilename, tools.loadfile(filename, self.encoding))        
    
    
    def search_in_sysobjects(self, filename):
        baseDir = self.sysobjectsDir
        
        if self.sysobjects_files is None:
            self.sysobjects_files = {}
            
            # gather all files in base dir
            for dirpath, _, filenames in os.walk(baseDir):
                for name in filenames:
                    if self.ignoreFileCase:
                        name = name.lower()
                        
                    if name in self.sysobjects_files:
                        self.sysobjects_files[name].extend([os.path.join(dirpath, name)])
                    else:
                        self.sysobjects_files[name] = [os.path.join(dirpath, name)]
            
            if len(self.sysobjects_files) == 0:
                raise PatchException('Base path is empty. Cannot retrieve any file from source path [{0}]'.format(baseDir))
            
        if self.ignoreFileCase:
            filename = filename.lower()
        
        if filename in self.sysobjects_files:
            found_array = self.sysobjects_files[filename]
            
            #print ('found {0} = ARRAY {1}'.format(filename, found_array))
            
            if len(found_array) > 1:
                raise PatchException('File name [{0}] in [{1}] found {2} times. Cannot recognize which of them we using.'.format(
                                     filename, baseDir, len(found_array)))
            
            return found_array[0]
        else:
            raise PatchException('Cannot find file name [{0}] in [{1}]'.format(filename, baseDir))
        
    

    def prepare(self, template, replace, forceOutput):
        '''
        Implementation. Actual preparing of given file.
        
            template -- template file template
        
            replace -- mode; if None -- creating new version, 
                if 're' then we replacing last added file,
                if anything else -- this is number we replacing
                
            forceOutput -- special output directory which overwrite basic settings
        '''
        assert template != None, 'template must be given'
        self.template = template
        
        if replace == '':
            replace = None
        
        print ('\nPreparing patch for {0}, mode {1}'.format(template, replace))
        
        ver, dest, lastfile = self.get_current_version(replace)
        
        print ('Using last patch\n', lastfile)
        
        # reading last version
        # preparing map, version must be 5 digits width
        self.binds = {'date': time.strftime('%Y-%m-%d', time.localtime()),
                 'ver': '{0:0>5}'.format(ver),
                 'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}
        
        # reading template file
        with open(template, encoding=self.encoding) as file:
            source = file.read()
        
        # bind keys in template
        # don't care if not so hot and fast
        for m in self.binds:
            source = source.replace('%' + m + '%', self.binds[m])
        
        templateDir = os.path.split(os.path.realpath(template))[0]
        
        # checking included includes
        result = ''
        self.includes = []
        for line in source.split('\n'):
            includeFile = None
            if line[:3] == '@@@':
                # include file in current directory
                includeFile = os.path.join(templateDir, line[3:].lstrip())
            elif line[:2] == '@@':
                # include file in BASE_PATH directory
                line = line[2:].lstrip()
                
                # That means we must search file in our directory
                if line[:1] == '?':
                    # Time to search
                    line = self.search_in_sysobjects(line[1:])
                    assert line is not None, 'search must return exactly one item'
                
                #includeFile = os.path.join(baseDir, line)
                includeFile = line
            elif line[:2] == '!!':
                # Include safe patching
                script = line[2:].lstrip().replace("'", "''")
                line = EXECUTE_SAFE_TEMPLATE.format(script, script)
            
            if includeFile is not None:
                self.includes.append(includeFile)
                result += self.include_file_body(includeFile)
            else:
                result += line + '\n'
    
        # Another template, list of all included includes
        result = result.replace('%changed%', ', '.join([os.path.split(file)[1] for file in self.includes]))
        
        # Creating output file
        if forceOutput:
            print ('Overwriting output file to', forceOutput)
            outputName = forceOutput
        else:
            outputName = os.path.join(dest, '{0}_{1}.sql'.format(self.binds['date'], self.binds['ver']))    
    
        print ('\nPATCH', outputName)
        with open(outputName, mode='w', encoding=self.encoding) as file:
            file.write(result)
    
        # Create backups
        self.make_backup()
    
        print ('DONE.')
        
        if self.auto_svn and replace is None:
            # Set up new patch into subversion system
            proc = subprocess.Popen(SVN_ADD.format(outputName), shell=True,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            ret = proc.wait()
            if ret != 0:
                print ('Maybe file already under subversion control')
            else:
                print ('Placed under subversion control')
        
        return outputName
    
        
    def make_backup(self):
        '''
        Make actual backup for processed template
        '''
        
        print ('Creating backups...');
        
        # Save our template
        safeStamp = self.binds['timestamp'].translate({ord(':'):ord('_'), ord(' '):ord('_')})
        filepart = os.path.split(os.path.realpath(self.template))
        
        # Creating backup directory, to the same directory where our template file placed
        dir_ = os.path.join(filepart[0], 'backup')
        if not os.path.exists(dir_):
            os.mkdir(dir_)
        
        #Creating current backup directory
        dir_ = os.path.join(dir_, '{0}_{1}_{2}'.format(filepart[1], safeStamp, self.binds['ver']))
        if not os.path.exists(dir_):
            os.mkdir(dir_)
            
        #Write backup
        shutil.copy(self.template, os.path.join(dir_, filepart[1]))
            
        for file in self.includes:
            shutil.copy(file, os.path.join(dir_, os.path.split(file)[1])) 
