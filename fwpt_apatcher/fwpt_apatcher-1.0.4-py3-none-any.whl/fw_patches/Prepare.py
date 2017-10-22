'''
Created on 16.09.2009

Python 3.1 required.

Usage:
    python3 Prepare.py <template.sql> [re|<patch-number>]'
    

    re -- means that last patch will be overwritten
    patch-number -- means that exactly given patch number will be overwritten
    
    if not that options provided -- patch with next version will be created
    
    You MUST have file settings.ini placed the same directory

@author: raidan
'''
from _pyio import open
from fw_patches.tools import readfile
import glob
import os
import re
import shutil
import subprocess
import time
from fw_patches.FwConst import VERSION, LAST_VERSION_DIR_POSTFIX,\
    VERSION_DIR_PREFIX, SQL_PATH, VERSION_FILE_TEMPLATE, INCLUDE_TEPLATE,\
    EXECUTE_SAFE_TEMPLATE, OUTPUT_NAME_TEMPLATE, SVN_ADD, DEFAULT_ENCODING,\
    PATCHES_DIR, SYSOBJECTS_DIR

# Our new exception
class PatchException(BaseException):
    pass

class PatchPrepare():
    def __init__(self, settingsFile='settings.conf', ignoreFileCase = True):
        print("Forward Patch Prepare system. V. {0}".format(VERSION))
        
        if settingsFile is None:
            tmp_settings = dict()
            tmp_settings['DEFAULT_ENCODING']=DEFAULT_ENCODING
            tmp_settings['prepare.patchPath']=PATCHES_DIR
            tmp_settings['prepare.sourcePath']=SYSOBJECTS_DIR
            self.settings = tmp_settings
        else:
            self.settings = readfile(settingsFile)
            
        self.encoding = self.settings['DEFAULT_ENCODING']
        
        self.all_sql_files = None
        self.destination_dir = None
        self.ignoreFileCase = ignoreFileCase
        
        self.auto_svn = True
        
        self.base_files = None
        
        self.ignoreVerXXXXX = False
        
    def setIgnoreVerXXXXX(self, ignore):
        self.ignoreVerXXXXX = ignore
        
    def setPatchesDir(self, patchesDir):
        self.all_sql_files = None
        self.settings['prepare.patchPath'] = patchesDir

    def list_all_sql_files(self):
        '''
        Method returns list of all sql files, existed in special source path
        
        return list of files and name of destination dir (where we must place our patches)
        '''
        if self.all_sql_files is None:

            patchPath = self.settings['prepare.patchPath']
            files = []
            
            # First of all -- let's find if sql's placed exactly in patchPath directory
            sql_direct = glob.glob(patchPath + '/' + SQL_PATH)
            if sql_direct:
                files = sql_direct
                dest = os.path.realpath(patchPath)
            else:

                # Checks only directory, started with year
                dirs = glob.glob(patchPath + VERSION_DIR_PREFIX)
                if len(dirs) == 0:
                    raise PatchException("Source path is empty. Cannot retrieve any file from source path " + patchPath)
                    
                # Current patch dir must ends with this symbols 
                templateDest = LAST_VERSION_DIR_POSTFIX
                dest = None
    
                
                for path in dirs:
                    if path[-5:] == templateDest:
                        if not self.ignoreVerXXXXX:
                            if dest is not None:
                                raise BaseException(('Found duplicate destination dirs: {0} and {1}. ' + 
                                                    'Expected only one which ends with {2}.').format(dest, path, templateDest))
                        dest = path
                    files.extend(glob.glob(path + '/' + SQL_PATH))
            
                if dest is None:
                    raise PatchException('Not found destination directory ends with {0} in source path {1}'.
                                            format(templateDest, patchPath))
                
            if len(files) == 0:
                raise PatchException('Files are empty. Cannot retrieve any file from source path ', patchPath)
                
            files.sort()
            self.all_sql_files, self.destination_dir = files, dest
        
        return list(self.all_sql_files), self.destination_dir

    
    def get_current_version(self, replace):
        '''
        Method returns current version of patch (last SQL for template)
        
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
        
        if replace is not None and replace != 're':
            replace_int = int(replace)
            
            # usually we applying latest
            files.reverse()
            for file in files:
                found = template.search(file)
                if found and int(found.group(1)) == replace_int:
                    required_file = file
                    break
            if required_file is None:
                raise PatchException('Unable to find patch file {0}'.format(replace))
        else:
            required_file = os.path.realpath(files.pop())
    
        versionName = os.path.split(required_file)[1]
        
        ver = int(versionName[11:16])
        if replace is None:
            # Appending
            ver += 1
            
        return ver, dest, required_file

    def get_file_body(self, filename):
        '''
        Load file body and returns it with some additional comments.
        Returns text that can be include into script
        
            filename -- the file we must include
        '''
        
        assert filename != None, 'filename cannot be empty'
        
        print ('Include file ' + filename)
        with open(filename, encoding=self.encoding) as file:
            content = file.read()
            
            # Pretty response printing
            return INCLUDE_TEPLATE.format(filename, content)
            # Pretty response done
        
    
    
    def search_in_base(self, filename, baseDir):

        if self.base_files is None:
            self.base_files = {}
            
            # gather all files in base dir
            for dirpath, dirnames, filenames in os.walk(baseDir):
                for name in filenames:
                    if self.ignoreFileCase:
                        name = name.lower()
                        
                    if not self.base_files.__contains__(name):
                        self.base_files[name] = [os.path.join(dirpath, name)]
                    else:
                        self.base_files[name].extend([os.path.join(dirpath, name)])
            
            if len(self.base_files) == 0:
                raise PatchException("Base path is empty. Cannot retrieve any file from source path " + baseDir)
            
        if self.ignoreFileCase:
            filename = filename.lower()
        
        if self.base_files.__contains__(filename):
            found_array = self.base_files[filename]
            
            #print ('found {0} = ARRAY {1}'.format(filename, found_array))
            
            if len(found_array) > 1:
                raise PatchException("File name " + filename + " in " + baseDir + " found " + 
                                     str(len(found_array)) + " times. Cannot recognize which of them we using.")
            
            return found_array[0]
        else:
            raise PatchException("Cannot found file name " + filename + " in " + baseDir)

    def prepare_impl(self, template, replace, forceOutput):
        '''
        Implementation. Actual preparing of given file.
        
            template -- template file template
        
            replace -- mode; if None -- creating new version, 
                if "re" then we replacing last added file,
                if anything else -- this is number we replacing
                
            forceOutput -- special output directory which overwrite basic settings
        '''
        assert template != None, 'template must be given'
        self.template = template
        
        print ('Preparing patch for {0}, mode {1}'.format(template, replace))
        
        ver, dest, lastfile = self.get_current_version(replace)
        
        print ('Found patch file', lastfile)
        
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
        
        baseDir = self.settings['prepare.sourcePath'] 
        templateDir = os.path.split(os.path.realpath(template))[0]
        
        # checking included includes
        result = ""
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
                    line = self.search_in_base(line[1:], baseDir)
                    assert line is not None, 'search must return exactly one item'
                
                #includeFile = os.path.join(baseDir, line)
                includeFile = line
            elif line[:2] == '!!':
                # Include safe patching
                script = line[2:].lstrip().replace("'", "''")
                line = EXECUTE_SAFE_TEMPLATE.format(script, script)
            
            if includeFile is not None:
                self.includes.append(includeFile)
                result += self.get_file_body(includeFile)
            else:
                result += line + '\n'
    
        # Another template, list of all included includes
        result = result.replace('%changed%', ', '.join([os.path.split(file)[1] for file in self.includes]))
        
        # Creating output file
        if forceOutput:
            print ('Overwriting output file to', forceOutput)
            outputName = forceOutput
        else:
            outputName = OUTPUT_NAME_TEMPLATE.format(dest, self.binds['date'], self.binds['ver'])    
    
        print ('Writing info file ' + outputName)
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
        dir = '{0}/backup'.format(filepart[0])
        if not os.path.exists(dir):
            os.mkdir(dir)
        
        #Creating current backup directory
        dir = '{0}/{1}_{2}_{3}'.format(dir, filepart[1], safeStamp, self.binds['ver'])
        if not os.path.exists(dir):
            os.mkdir(dir)
            
        #Write backup
        shutil.copy(self.template, '{0}/{1}'.format(dir, filepart[1]))
            
        for file in self.includes:
            shutil.copy(file, '{0}/{1}'.format(dir, os.path.split(file)[1])) 
