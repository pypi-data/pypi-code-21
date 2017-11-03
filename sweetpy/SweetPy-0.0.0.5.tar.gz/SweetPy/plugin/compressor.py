import os
from ..common.compressor import ZFile

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

