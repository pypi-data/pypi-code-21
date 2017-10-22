'''
Created on 07.10.2009

@author: raidan
'''
from _pyio import open
from fw_patches.tools import readfile, WatchingThread, StopWatch, loadfile,\
    filter_ts, savefile
import shutil
import os
import sys
import cx_Oracle
import re
import subprocess
from fw_patches.FwConst import VERSION, VER_SIMPLE_PATTERN, VER_PROJECT_PATTERN, VER_PROJECT_PATTERN_END, \
    SQL, SELECT_SIMPLE_VER, SELECT_PROJECT_VER, CONFIRM_MESSAGE_PREFIX


# Our new exception
class PatchException(BaseException):
    pass

class ApplyPatch():
    def __init__(self, settingsFile='settings.conf', log_dir=None):
        print("Forward Patch Apply system. V. {0}".format(VERSION))
        
        self.settings = readfile(settingsFile)
        self.encoding = self.settings['DEFAULT_ENCODING']
        self.system = None
        if 'apply.system' in self.settings:
            self.system = self.settings['apply.system']
        
        self.log_dir = log_dir
        
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        
        self.check_invalid = False
        
    def pre_std(self, file, dir=None):
        
        if self.log_dir is None:
            return False
        
        else:
            
            if dir is not None:
                real_log_dir = self.log_dir + '/' + dir
                if not os.path.exists(real_log_dir):
                    os.mkdir(real_log_dir)
            else:
                real_log_dir = self.log_dir
                
            sys.stdout = open(real_log_dir + "/" + file + ".log", mode='w', encoding='utf-8') 
            sys.stderr = open(real_log_dir + "/" + file + ".err", mode='w', encoding='utf-8')            
        
            self.real_log_dir = real_log_dir
            
            return True
        
    def post_std(self):
        if self.log_dir is not None:
            sys.stdout.flush()
            sys.stderr.flush()
            
            sys.stdout = self.stdout 
            sys.stderr = self.stderr 
        
    def get_connection(self):
        '''
        Returning connection
        '''
        auth = self.settings['apply.account']
        print ('Logging into', auth)
        return cx_Oracle.connect(auth)
    
    def check_invalids(self):
        if 'check.invalid' in self.settings and self.settings['check.invalid'] == 'True':
            self.check_invalid = True
        return self.check_invalid
        
    def get_current_db_version(self, project=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if project is None:
                cursor.execute(SELECT_SIMPLE_VER)
            else:
                cursor.execute(SELECT_PROJECT_VER, proj=project)
            for system, current_version, in cursor:                       
                print ('Current {0} database version = {1}'.format(system, current_version))

                return system, current_version
            
            return None, None
        finally:
            conn.close()


    def validate(self, patches):
        patchset = []
        for patch in patches:
            with open(patch, encoding=self.encoding) as file:
                message = ''
                for line in file:
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
            confirm = input('Confirm? (y/n):')
            if confirm.upper() != 'Y':
                print("\nDid not confirmed")
                return False

            
        return True

    def check(self, patches, project=None):
        '''
        Checking current current_version in database.
        
            return True if patches are correct and False is current_version does not same
        '''
        
        assert patches != None, 'Patches required'
        
        
        self.pre_std("prepare")
        
        versions = []
        
        # Pattern for searching current_version 
        if project is None:
            print ('using no project')
            version_pattern = re.compile(VER_SIMPLE_PATTERN, re.IGNORECASE)
        else:
            print ('using \'' + project)
            version_pattern = re.compile(VER_PROJECT_PATTERN + project + VER_PROJECT_PATTERN_END, re.IGNORECASE)
        for patch in patches:
            with open(patch, encoding=self.encoding) as file:
                for line in file:
                    found = version_pattern.search(line)
                    # Found!
                    if found:
                        current_version = int(found.group(1))
                        print ('Accepted applying patch', current_version)
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
        
        try:
            system, db_version = self.get_current_db_version(project)
            if project is None and self.system is not None and self.system != '' and system != self.system:
                print ('\n\n<<< Error when checking system {0}. Current is {1} >>>\n'.format(self.system, system))
                raise PatchException(('\n\nINVALID SYSTEM VERSION.\nDatabase system = {0}. ' + 
                                      'Your patch for system {1}. ' + 
                                      '\nMust be the same!').format(system, self.system))

                
            if first_applying_ver != db_version + 1:
                        print ('\n\n<<< Error when checking version {0}. Current is {1} >>>\n'.format(first_applying_ver, current_version))
                        raise PatchException(('\n\nINVALID PATCH.\nDatabase current_version = {0} ' + 
                                            'but you trying to apply version {1}. ' + 
                                            'Must be next version.').format(db_version, first_applying_ver))
            else:
                print ('Version is correct. Ready to proceed.')
        finally:
            self.post_std()  


        if not self.validate(patches):
            print ('Patch applying is canceled')
            return False
        
        return True
    
    def preprocess(self, fileFrom, fileTo):
        if 'apply.remap_tablespace' in self.settings:
            print ('Remapping {0} -> {1}'.format(fileFrom, fileTo))
            remapTS = self.settings['apply.remap_tablespace']
            lines = loadfile(fileFrom).split("\n")
            target = "\n".join(filter_ts(lines, remapTS))
            savefile(fileTo, target)
        else:
            print ('Copying {0} -> {1}'.format(fileFrom, fileTo))
            shutil.copy(fileFrom, fileTo)
            
    def get_invalids(self):
        if not self.check_invalids():
            return []
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("select object_name from user_objects where status = 'INVALID' order by object_name")
            names = []
            for object_name, in cursor:                       
                names.append(object_name)
            
            return names
        finally:
            conn.close()

    def apply(self, patches):
        '''
        Executing patch onto database.
            
            patches -- list of patches we run
        '''
        
        
        # Very easy running
        for patch in patches:
            
            redirect = ''
            patchPath = os.path.split(os.path.realpath(patch))
            if self.pre_std("execute", patchPath[1]):
                targetPatch = os.path.realpath(self.real_log_dir + '/' + patchPath[1])
                self.preprocess(patch, targetPatch)
                patch = targetPatch
                redirect = ' > ' + self.real_log_dir + '/sqlplus.log'

            watch = StopWatch()
            watch.start()                
            try:
                
                invalids_before = self.get_invalids()
                
                line = self.settings['apply.arg']
                if line == "sqlplus {0} {1}":
                    line = "sqlplus -L {0} {1}"

                line = line.format(self.settings['apply.account'], redirect)
                
                self.stdout.write(" + {0} ... ".format(patch))
                self.stdout.flush()
                print ('Executing: "{0}"'.format(line))
                
                proc = subprocess.Popen(line, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                
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
                WatchingThread(watcher(self.encoding, proc.communicate(sql.encode(self.encoding)))).start()
                
                
                ret = proc.wait()
                if ret != 0:
                    raise PatchException('Failed executing script {0}. Return error code: {1}'.format(patch, ret))
                
                time = watch.stop()
                self.stdout.write("OK in {0:.2f} sec\n".format(time))
                self.stdout.flush()
                
                
                invalids_after = self.get_invalids()
                if invalids_before != invalids_after:
                    diff = set(invalids_after) - set(invalids_before)
                    if len(diff) > 0:
                        print ('\n\n<<< Error when checking invalid objects. New invalid objects:\n')
                        for d in diff:
                            print(' <<< {0}\n'.format(d))
                        raise PatchException('New invalid objects after patch {0}'.format(patch))
                    
                
                print("Executed successfully in {0:.2f} sec\n".format(time))
            except:
                time = watch.stop()
                self.stdout.write("FAIL in {0:.2f} sec\n".format(time))
                self.stdout.flush()
                print ('\n\n<<< Error when applying patch {0} >>>\n'.format(patch))
                raise
            finally:
                self.post_std()
    
    def check_and_apply(self, patches, project=None):
        assert len(patches) > 0, 'Invalid arguments, expected at least one patch for apply'  
    
        patches.sort()
        
        print ('\nChecking patch list:')
        for patch in patches:
            print (" + {0}".format(patch))

        if not self.check(patches, project):
            print ('Did not checked')
            return
        
        if self.system is None:
            print("\n\nPatches will be APPLIED ON {0}".format(self.settings['apply.account']))
        else:
            print("\n\nPatches for {1} will be APPLIED ON {0}".format(self.settings['apply.account'], self.system))
        confirm = input('Execute them all? (y/n):')
        if confirm.upper() != 'Y':
            print('Did not confirm')
            return
        
        print ('\n\nApplying patches:')
        self.apply(patches)
