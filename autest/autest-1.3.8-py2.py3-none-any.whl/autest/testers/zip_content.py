from . import tester
import hosts.output as host
from autest.exceptions.killonfailure import KillOnFailureError

import os
import tarfile
import zipfile

# update this to allow for basic file wildcard patterns with * and ?


class ZipContent(tester.Tester):
    ZIP_MAGIC = '\x50\x4B\x05\x06'

    def __init__(self,
                 includes=None,
                 excludes=None,
                 kill_on_failure=False,
                 description_group=None):
        self.__include = includes or ()
        self.__exclude = excludes or ()
        super(ZipContent, self).__init__(
            value=None,  # this the _include,_exclude
            test_value=None,  # this is a file name, ie it set when it assigned to the File.content member
            kill_on_failure=kill_on_failure,
            description_group=description_group,
            description='')

    def test(self, eventinfo, **kw):
        self.__test()
        if self.Result == tester.ResultType.Failed and self.KillOnFailure:
            raise KillOnFailureError

    def __test(self):
        zfile = self.TestValue.AbsPath
        self.Description = "Checking that {0} contains {1} and does not contain {2}".format(
            zfile, self.__include, self.__exclude)

        # check that file exists
        if not os.path.exists(zfile):
            self.Result = tester.ResultType.Failed
            self.Reason = 'File {0} does not exist, cannot check contents'.format(
                zfile)
            host.WriteVerbose(
                ["testers.ZipContent", "testers"], "{0} - ".format(
                    tester.ResultType.to_color_string(self.Result)),
                self.Reason)
            return

        fileName = zfile.lower()
        if any(
                fileName.endswith(ext)
                for ext in ('.tar.gz', '.tgz', '.tar.bz2', '.tbz', '.tb2',
                            '.bz2')):
            archive = tarfile.open(zfile)
            names = archive.getnames()
        elif fileName.endswith('.zip'):
            # a check for Python 2.6 having issues with empty zip files
            fileSize = os.path.getsize(zfile)
            if fileSize == 0:
                # empty zip file, don't try to open
                names = ()
            elif fileSize <= 22:  # the size of empty zipfile with header
                with open(zfile, 'rb') as f:
                    content = f.read()
                if not content.startswith(self.ZIP_MAGIC):
                    raise zipfile.BadZipfile(
                        ('"%s" seems to be not a zip file: ' +
                         'it doesn\'t start with ZIP magic') % zfile)
                if content[len(self.ZIP_MAGIC):].replace('\x00', ''):
                    raise zipfile.BadZipfile(
                        ('"%s" seems to be not a zip file: ' +
                         'it\s too small but isn\'t empty inside') % zfile)
                names = ()
            else:
                # this seems to be normal zipfile, try python zipfile now
                archive = zipfile.ZipFile(zfile)
                names = archive.namelist()
        else:
            self.Result = tester.ResultType.Failed
            self.Reason = 'Unsupported archive type: {0}'.format(zfile)

        for contain in self.__include:
            if contain not in names:
                self.Result = tester.ResultType.Failed
                self.Reason = 'File "{0}" not found in archive "{1}"'.format(
                    contain, zfile)
                host.WriteVerbose(
                    ["testers.ZipContent", "testers"], "{0} - ".format(
                        tester.ResultType.to_color_string(self.Result)),
                    self.Reason)
                return

        for notContain in self.__exclude:
            if notContain in names:
                self.Result = tester.ResultType.Failed
                self.Reason = 'File "{0}" found in archive "{1}"'.format(
                    notContain, zfile)
                host.WriteVerbose(
                    ["testers.ZipContent", "testers"], "{0} - ".format(
                        tester.ResultType.to_color_string(self.Result)),
                    self.Reason)
                return

        self.Result = tester.ResultType.Passed
        self.Reason = "Archive file contents match requested filters"
        host.WriteVerbose(
            ["testers.ZipContent", "testers"],
            "{0} - ".format(tester.ResultType.to_color_string(self.Result)),
            self.Reason)
