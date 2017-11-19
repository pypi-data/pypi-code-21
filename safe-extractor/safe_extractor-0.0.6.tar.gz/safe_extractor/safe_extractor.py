###############
# SafeExtractor.py
#
# Usage:
# SafeExtractor.untar_it("myfile.tar.gz", extract_path='.')
# SafeExtractor.unzip_it("myfile.zip", extract_path='.')
#
# For more information see:
# http://stackoverflow.com/a/10077309/555017
# http://stackoverflow.com/a/36583849
###############

import tarfile, zipfile, os
from os.path import abspath, realpath, dirname, join as joinpath
from sys import stderr

resolved = lambda x: realpath(abspath(x))

class SafeExtractor:
    def badpath(path, base):
        # joinpath will ignore base if path is absolute
        return not resolved(joinpath(base,path)).startswith(base)

    def badlink(info, base):
        # Links are interpreted relative to the directory containing the link
        tip = resolved(joinpath(base, dirname(info.name)))
        return SafeExtractor().badpath(info.linkname, base=tip)

    def safemembers(members):
        base = resolved(".")

        for finfo in members:
            if  SafeExtractor().badpath(finfo.name, base):
                print >>stderr, finfo.name, "is blocked (illegal path)"
            elif finfo.issym() and SafeExtractor().badlink(finfo,base):
                print >>stderr, finfo.name, "is blocked: Hard link to", finfo.linkname
            elif finfo.islnk() and SafeExtractor().badlink(finfo,base):
                print >>stderr, finfo.name, "is blocked: Symlink to", finfo.linkname
            else:
                yield finfo

    def untar_it(tar_file, extract_path='.'):
        ar = tarfile.open(tar_file)
        ar.extractall(path=extract_path, members=SafeExtractor().safemembers(ar))
        ar.close()

    def unzip_it(zip_file, extract_path='.'):
        with zipfile.ZipFile(zip_file, 'r') as zf:
            for member in zf.infolist():
                abspath = os.path.abspath(os.path.join(extract_path, member.filename))
                if abspath.startswith(os.path.abspath(extract_path)):
                    zf.extract(member, extract_path)
