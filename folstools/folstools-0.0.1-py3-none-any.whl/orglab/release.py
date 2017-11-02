import os
import sys
import re
import shutil
import zipfile
from subprocess import check_call
from ftplib import FTP
from urllib.request import urlretrieve

import folstools.win32.utils as win32utils

EXCLAMINATION = '!!!!!!!!!!!'


class CopyBuild(object):
    def __init__(self, key1, key2, srcPath, desPath, desZipPath):
        self.key1 = key1
        self.key2 = key2
        self.srcPath = srcPath
        self.desPath = desPath
        self.desZipPath = desZipPath
        pass

    def do(self, build):
        file = os.path.join(self.srcPath, build)
        desfile = os.path.join(self.desPath, build)
        print("Copying {} to {} ...".format(build, self.desPath))
        try:
            shutil.copytree(file, desfile)
            print("Done{}\n".format(EXCLAMINATION))

            with zipfile.ZipFile(os.path.join(self.desZipPath, build) + '.zip',
                                 'w') as myzip:
                print("Zipping {} to {} ...".format(file, self.desZipPath))
                for ff in os.listdir(file):
                    myzip.write(os.path.join(file, ff), ff,
                                zipfile.ZIP_DEFLATED)
                print("Done{}\n".format(EXCLAMINATION))

            return True
        except FileNotFoundError:
            print("{} does not exist, fail to copy to {}"
                  .format(file, desfile))

        return False


class GetBuildFromFTP(object):
    def __init__(self, key1, key2, srcpath, despath, aria2c,
                 ftpsite='',
                 username='',
                 password=''):
        self.key1 = key1
        self.key2 = key2
        self.srcpath = srcpath
        self.despath = despath
        self.aria2c = aria2c
        self.ftpsite = ftpsite
        self.username = username
        self.password = password

    def do(self):
        f = self._fetch()
        if f:
            fdest = os.path.join(self.despath, f)
            if os.path.exists(fdest):
                print('{} already exists'.format(fdest))
                return
            return self._get_build(f)

    def _pattern(self):
        return r"IR%ssr\d[-_](\d+)([a-z]?)((?:\.\d+)?)(_H)?" % (self.key1)

    def _fetch(self):
        print("Connecting %s ..." % self.ftpsite)
        try:
            with FTP(self.ftpsite, self.username, self.password) as ftp:
                try:
                    ftp.set_pasv(False)
                    ftp.cwd(self.srcpath)
                except:
                    print("Build directory changed{}\n".format(EXCLAMINATION))
                    return None

                build = []

                def get(s):
                    match = re.search(self._pattern(), s, re.I)
                    if match:
                        build.append(match)

                def build_comp(build):
                    h_suffix = build.group(4)
                    return int(build.group(1)), build.group(2), build.group(3), h_suffix if h_suffix else ''

                ftp.dir(get)
                if build:
                    build.sort(reverse=True, key=build_comp)
                    return build[0].group(0)
        except Exception as e:
            print('Failed to connect {} : {}'.format(self.ftpsite, e))

    def _get_build(self, f):
        files = []
        try:
            with FTP(self.ftpsite, self.username, self.password) as ftp:
                ftp.set_pasv(False)
                ftp.cwd(os.path.join(self.srcpath, f))

                def get(s):
                    files.append(s.split()[-1])
                ftp.dir(get)
        except Exception as e:
            print('Failed to connect {} : {}'.format(self.ftpsite, e))

        print('Downloading {}'.format(f))
        try:
            os.mkdir(os.path.join(self.despath, f))
        except:
            pass

        get = self._get_by_aria2c if self.aria2c else _get_direct
        for f1 in files:
            get(f, f1)

        print('Downloaded{}\n'.format(EXCLAMINATION))
        return f

    def _get_by_aria2c(self, f, f1):
        check_call(self.aria2c + ['ftp://{}:{}@{}/{}{}/{}'
                                  .format(self.username,
                                          self.password,
                                          self.ftpsite,
                                          self.srcpath,
                                          f,
                                          f1),
                                  '-d',
                                  os.path.join(self.despath, f)])

    def _get_direct(self, f, f1):
        sys.stdout.write(f1 + ' ... ')
        sys.stdout.flush()

        self.lastpercent = ''
        urlretrieve('ftp://{}:{}@{}/{}{}/{}'.format(self.username,
                                                    self.password,
                                                    self.ftpsite,
                                                    self.srcpath,
                                                    f,
                                                    f1),
                    os.path.join(self.despath, f, f1),
                    reporthook=self._progress
                    )
        print()

    def _progress(self, count, blocksize, totalsize):
        sys.stdout.write('\b' * len(self.lastpercent))
        percent = count * blocksize * 100.0 / totalsize
        if percent > 100:
            percent = 100
        self.lastpercent = '{:.2f}%'.format(percent)
        sys.stdout.write(self.lastpercent)
        sys.stdout.flush()


def get_origin_binaries(folder, win32, version, sln=None):
    projects = []
    if sln:
        with open(sln, encoding='utf-8') as f:
            data = f.read()
        projects = re.findall(r'Project\("{[-\w]+}"\) = "(\w+)"', data)
    for root, dirs, files in os.walk(folder):
        for f in files:
            name, ext = [s.lower() for s in os.path.splitext(f)]
            if ext in ('.exe', '.dll', '.pyd'):
                ff = os.path.join(root, f)

                def bin_name():
                    return ff.replace(folder + '\\', '')
                itype = win32utils.get_image_file_type(ff)
                if (win32 and itype == win32utils.IMAGE_FILE_MACHINE_I386 or
                   not win32 and itype == win32utils.IMAGE_FILE_MACHINE_AMD64):
                    try:
                        for proj in projects:
                            if name.find(proj) == 0:
                                yield bin_name()
                                raise ValueError
                        props = win32utils.get_file_properties(ff)
                        try:
                            sI = props['StringFileInfo']
                            if sI['CompanyName'] == 'OriginLab Corporation':
                                v = sI['ProductVersion'].replace('.', '')
                                fileflags = props['FixedFileInfo']['FileFlags']
                                if v == version and (fileflags & 1) == 0:
                                    yield bin_name()
                        except:
                            pass
                    except ValueError:
                        pass
