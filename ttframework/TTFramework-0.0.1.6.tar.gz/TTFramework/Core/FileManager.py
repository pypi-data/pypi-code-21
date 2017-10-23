#encoding:utf-8


import zipfile
import os.path
import os


class ZFile(object):
    def __init__(self, filename, mode='r', basedir=''):
        self.filename = filename
        self.mode = mode
        if self.mode in ('w', 'a'):
            self.zfile = zipfile.ZipFile(filename, self.mode, compression=zipfile.ZIP_DEFLATED)
        else:
            self.zfile = zipfile.ZipFile(filename, self.mode)
        self.basedir = basedir
        if not self.basedir:
            self.basedir = os.path.dirname(filename)

    def addfile(self, path, arcname=None):
        path = path.replace('//', '/')
        if not arcname:
            if path.startswith(self.basedir):
                arcname = path[len(self.basedir):]
            else:
                arcname = ''
        self.zfile.write(path, arcname)

    def addfiles(self, paths):
        for path in paths:
            if isinstance(path, tuple):
                self.addfile(*path)
            else:
                self.addfile(path)

    def close(self):
        self.zfile.close()

    def extract_to(self, path):
        fileList = []
        for p in self.zfile.namelist():
            fileList.append(p)
            self.extract(p, path)
        return fileList

    def extract(self, filename, path):
        if not filename.endswith('/'):
            f = os.path.join(path, filename)
            dir = os.path.dirname(f)
            if not os.path.exists(dir):
                os.makedirs(dir)
            open(f, 'wb').write(self.zfile.read(filename))

class FileManager(object):
    def __init__(self):
        pass

    def directory_to_zip(self, zfile, files):
        result = zfile
        try:
            z = ZFile(zfile, 'w')
            z.addfiles(files)
            z.close()
        except:
            result = None
        return result

    def zip_to_directory(self, zfile, path=''):
        try:
            z = ZFile(zfile)
            result = z.extract_to(path)
            z.close()
            if path.endswith('/'):
                result = [path + f for f in result]
            else:
                result = [path + '/' + f for f in result]
        except:
            result = None
        return result

    def mkdirs(self,dirs):
        if not os.path.exists(dirs):
            os.makedirs(dirs)

    def division_file_name(self, fileAllPath=''):
        i = fileAllPath.rfind('/')
        return fileAllPath[i + 1:]


