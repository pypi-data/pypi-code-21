from __future__ import absolute_import, division, print_function
import autest.core.streamwriter as streamwriter
from autest.core import CopyLogic
import autest.common.process
import hosts.output as host
import autest.common.disk
import autest.testers as testers
from autest.exceptions.setuperror import SetupError

import subprocess
import string
import shutil
import os
if os.name != 'nt':
    import grp
    import pwd

# base class for any Setup task extension
# contains basic API that maybe useful in defining a given task.


class SetupItem(object):

    def __init__(self, itemname=None, taskname=None):
        if itemname:
            self.__itemname = itemname
        elif taskname:
            self.__itemname = taskname
        else:
            host.WriteError("itemname is not provided")
        self.__runable = None
        self.cnt = 0

        # description of what we are trying to do
        self.__description = "actions description not defined"

        # assume pass unless an error happens
        self._Result = testers.ResultType.Passed

        # did we run this item
        self.__ran = val = False

    # basic properties values we need

    @property
    def ItemName(self):
        # name of the task
        return self.__itemname

    @ItemName.setter
    def ItemName(self, val):
        # name of the task
        self.__itemname = val

    @property
    def Description(self):
        # name of the task
        return self.__description

    @Description.setter
    def Description(self, val):
        # name of the task
        self.__description = val

    @property
    def RanOnce(self):
        return self.__ran

    @RanOnce.setter
    def RanOnce(self, val):
        self.__ran = val

    @property
    def SandBoxDir(self):
        # directory we run the test in
        return self.__runable._RootRunable.RunDirectory

    @property
    def TestRootDir(self):
        # the directory location given to scan for files for all the tests
        return self.__runable._RootRunable.TestRoot

    @property
    def TestFileDir(self):
        # the directory the test file was defined in
        return self.__runable._RootRunable.TestDirectory

    # useful util functions
    def RunCommand(self, cmd):

        # create a StreamWriter which will write out the stream data of the run
        # to sorted files
        output = streamwriter.StreamWriter(
            os.path.join(
                self.__runable.RunDirectory,
                "_setup_tmp_{0}_{1}".format(
                    self.ItemName.replace(" ", "_"),
                    self.cnt)
            ),
            cmd,
            self.__runable.Env
        )
        self.cnt += 1
        # the command line we will run. We add the RunDirectory to the start of the command
        # to avoid having to deal with cwddir() issues
        command_line = "cd {0} && {1}".format(self.SandBoxDir, cmd)
        # subsitute the value of the string via the template engine
        # as this provide a safe cross platform $subst model.
        template = string.Template(command_line)
        command_line = template.substitute(self.__runable.Env)

        proc = autest.common.process.Popen(
            command_line,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.__runable.Env)

        # get the output stream from the process we created and redirect to
        # files
        stdout = streamwriter.PipeRedirector(proc.stdout, output.WriteStdOut)
        stderr = streamwriter.PipeRedirector(proc.stderr, output.WriteStdErr)

        proc.wait()

        output.Close()

        # clean up redirectory objects for this run
        stdout.close()
        stderr.close()

        return proc.returncode

    def Copy(self, source, target=None, copy_logic=CopyLogic.Default):
        copy_logic = CopyLogic.DefaultLogic(copy_logic)
        source, target = self._copy_setup(source, target)
        if copy_logic != CopyLogic.Copy:
            self._smartLink(source, target, copy_logic, self.Copy)
        else:
            # do the copy
            host.WriteVerbose("setup", "Copying {0} to {1}".format(source, target))
            try:
                # copy file
                if os.path.isfile(source):
                    if os.path.exists(target):
                        host.WriteVerbose("setup", "target already exists! Replacing...")
                    shutil.copy2(source, target)
                # else copy a directory
                else:
                    autest.common.disk.copy_tree(source, target)
            except Exception as e:
                raise SetupError(
                    "Cannot copy {0} because {1}".format(source, str(e))
                )

    def CopyAs(self, source, targetdir, targetname=None):
        '''
        For copying files as a different name in nonexisting directories
        This is better than Copy most of the time as it makes the target directory
        if it does not exist, and is a little more clear on if the output is renamed
        or not.
        '''
        source, targetdir = self._copy_setup(source, targetdir)
        self.MakeDir(targetdir)
        if targetname is None:
            target = targetdir
        else:
            target = os.path.join(targetdir, targetname)
        host.WriteVerbose("setup", "Copying {0} as {1}".format(source, target))
        try:
            shutil.copy2(source, target)
        except Exception as e:
            raise SetupError("Cannot copy {0} to {1} because {2}".format(
                source, targetdir, str(e)))

    def MakeDir(self, path, mode=None):
        # check if the path given is in the sandbox if abs
        self._in_sandbox(path)
        # if abs path isn't specified then put it in the sandbox
        path = os.path.join(self.SandBoxDir, path)
        if not os.path.isdir(path):
            if not os.path.isfile(path):
                if mode is None:
                    os.makedirs(path)
                else:
                    os.makedirs(path, mode)
                host.WriteVerbose("setup", "Making directory {0}".format(path))
            else:
                raise SetupError('Path already exists as a file.')

    def Chown(self, path, uid, gid):
        if os.name == 'nt':
            return
        if not os.path.isabs(path):
            # assume it's in our sandbox
            path = os.path.join(self.SandBoxDir, path)
        if not os.path.exists(path):
            raise OSError("File or Directory doesn't exist")
        uid = pwd.getpwnam(uid).pw_uid
        gid = grp.getgrnam(gid).gr_gid
        try:
            os.chown(path, uid, gid)
            host.WriteVerbose(
                "setup", "Changing ownership of {0} to uid {1} gid {2}".format(path, uid, gid))
        except OSError as e:
            # Operation not Permitted will just pass
            host.WriteVerbose("setup", "Chown-", e)
            if e.errno != 1:
                raise

    def _copy_setup(self, source, target=None):
        # check to see if this is absolute path or not
        if not os.path.isabs(source):
            # if not we assume that the directory is based on our
            # Sandbox directory
            source = os.path.join(self.TestFileDir, source)
        if target:
            # check if target is permissible
            self._in_sandbox(target)
            target = os.path.join(self.SandBoxDir, target)
        else:
            # given that target is None we assume that we want to copy it
            # the sandbox directory with the same name as the source
            target = os.path.join(self.SandBoxDir, os.path.basename(source))

        return (source, target)

    # check that the path give is within the sandbox
    def _in_sandbox(self, path):
        # the split should have the first index as empty if the prefix is the
        # same as the SandBoxDir
        split = path.split(self.SandBoxDir)
        if os.path.isabs(path) and split[0] != '':
            raise IOError(
                'Target path is not within sandbox:\n {0}'.format(path))

    def SymLink(self, source, target):
        os.symlink(source, target)

    def HardLink(self, source, target):
        os.link(source, target)

    def _smartLink(self, source, target, link_policy, copy_func):
        '''
        Tires to make a Hard link then a SymLink then do a copy
        ToDo: look at making this overidable in what logic is used
        such as hard_copy or soft_copy as some tests might want to
        control how this smart logic is handled
        '''

        if link_policy == CopyLogic.HardSoft or link_policy == CopyLogic.Hard:
            try:
                host.WriteVerbose("setup", "Hardlinking {0} to {1}".format(source, target))
                self.HardLink(source, target)
                return
            except:
                host.WriteVerbose("setup", "Hardlinking - Failed! Trying..")
                if link_policy == CopyLogic.HardSoft:
                    copy_func(source, target, CopyLogic.Soft)
                else:
                    copy_func(source, target, CopyLogic.Copy)
        elif link_policy == CopyLogic.Soft:
            try:
                host.WriteVerbose("setup", "Symlinking {0} to {1}".format(source, target))
                self.SymLink(source, target)
            except:
                host.WriteVerbose("setup", "Symlinking - Failed! Trying..")
                copy_func(source, target, CopyLogic.Copy)

        elif link_policy == CopyLogic.HardSoftFiles or link_policy == CopyLogic.HardFiles:
            # source is a directory
            if os.path.isdir(source):
                self.MakeDir(target)
                files = os.listdir(source)
                for x in files:
                    fullsrc = os.path.join(source, x)
                    fulldest = os.path.join(target, x)
                    copy_func(fullsrc, fulldest, link_policy)
            # else source is a file
            else:
                copy_func(fullsrc, fulldest, CopyLogic.HardSoft)
        elif link_policy == CopyLogic.SoftFiles:
            # source is a directory
            if os.path.isdir(source):
                self.MakeDir(target)
                files = os.listdir(source)
                for x in files:
                    fullsrc = os.path.join(source, x)
                    fulldest = os.path.join(target, x)
                    copy_func(fullsrc, fulldest, link_policy)
            # else source is file
            else:
                copy_func(source, target, CopyLogic.Soft)
        else:
            copy_func(fullsrc, fulldest, CopyLogic.Copy)

    def _bind(self, test):
        '''
        Allow us to bind the Test information with the setup item
        This is done before we try to execute the setup logic
        '''
        self.__runable = test
        self.onBind()  # in case the item need to do something once we bind to the setup object

    def onBind(self):
        pass

    def cleanup(self):
        pass

    def _AddMethod(self, func, name=None):
        m = func.__get__(self)
        name = name if name is not None else func.__name__
        setattr(self, name, m)

    def _AddObject(self, obj, name=None):
        name = name if name is not None else obj.__name__
        setattr(self, name, obj)
        obj.Bind(self)

    @property
    def Env(self):
        return self.__runable.Env

    @property
    def Variables(self):
        return self.__runable.Variables

    def ComposeEnv(self):
        return self.__runable.ComposeEnv()

    def ComposeVariables(self):
        return self.__runable.ComposeVariables()
