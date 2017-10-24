
from __future__ import print_function, unicode_literals, absolute_import
from .headers import get_headers
import sys
import io
import gzip
import struct
from functools import wraps
from lbinstall.rpmfile.io_extra import _SubFile
try:
    from backports import lzma as lzma
    using_backport_lzma = True
except Exception as e:
    # print(e)
    using_backports_lzma = False
    import lzma


def pad(fileobj):
    return (4 - (fileobj.tell() % 4)) % 4


class RPMInfo(object):
    '''
    Informational class which holds the details about an
    archive member given by an RPM entry block.
    RPMInfo objects are returned by RPMFile.getmember() and
    RPMFile.getmembers() and are
    usually created internally.
    '''
    _new_coder = struct.Struct(b'8s8s8s8s8s8s8s8s8s8s8s8s8s')

    def __init__(self, name, file_start, file_size,
                 initial_offset, isdir, attrs):
        self.name = name.decode('utf-8')
        self.file_start = file_start
        self.size = file_size
        self.initial_offset = initial_offset
        self._isdir = isdir
        self._attrs = attrs

    @property
    def isdir(self):
        return self._isdir

    def __repr__(self):
        return '<RPMMember %r>' % self.name

    @classmethod
    def _read(cls, magic, fileobj):
        if magic == '070701':
            return cls._read_new(fileobj, magic=magic)
        else:
            raise Exception('bad magic number %r' % magic)

    @classmethod
    def _read_new(cls, fileobj, magic=None):
        coder = cls._new_coder

        initial_offset = fileobj.tell()
        d = coder.unpack_from(fileobj.read(coder.size))

        namesize = int(d[11], 16)
        name = fileobj.read(namesize)[:-1]
        fileobj.seek(pad(fileobj), 1)
        file_start = fileobj.tell()
        file_size = int(d[6], 16)
        fileobj.seek(file_size, 1)
        fileobj.seek(pad(fileobj), 1)

        # This only works for magic
        # 070701
        # Should fail with fracas with the others...
        # Remeber: magic already read...
        #       New ASCII Format
        # The "new" ASCII format uses 8-byte hexadecimal fields for all numbers
        # and separates device numbers into separate fields for major and minor
        # numbers.

        #       struct cpio_newc_header {
        #    	   char    c_magic[6];
        #    	   char    c_ino[8];
        #    	   char    c_mode[8];
        #    	   char    c_uid[8];
        #    	   char    c_gid[8];
        #    	   char    c_nlink[8];
        #    	   char    c_mtime[8];
        #    	   char    c_filesize[8];
        #    	   char    c_devmajor[8];
        #    	   char    c_devminor[8];
        #    	   char    c_rdevmajor[8];
        #    	   char    c_rdevminor[8];
        #    	   char    c_namesize[8];
        #    	   char    c_check[8];
        #       };
        mode = int(d[1], 16)
        ftype = mode & 0o170000
        masks = {"isLink": 0o120000,
                 "isFile":  0o100000,
                 "isDir": 0o040000}
        attrs = dict((key, (ftype == mask))
                     for (key, mask) in masks.items())
        attrs["ino"] = d[0]
        attrs["mode"] = mode & 0o000777
        nlink = int(d[4], 16)
        isdir = nlink >= 2 and file_size == 0
        # print("CHRIS name %s size %s nlink %s isdir %s"%(name, file_size,
        #                                                  nlink, isdir))
        # print(d)
        return cls(name, file_start, file_size, initial_offset, isdir, attrs)


class RPMFile(object):
    '''
    Open an RPM archive `name'. `mode' must be 'r' to
    read from an existing archive.

    If `fileobj' is given, it is used for reading or writing data. If it
    can be determined, `mode' is overridden by `fileobj's mode.
    `fileobj' is not closed, when TarFile is closed.

    '''
    def __init__(self, name=None, mode='rb', fileobj=None):

        if mode != 'rb':
            raise NotImplementedError("currently the only supported "
                                      "mode is 'rb'")
        self._fileobj = fileobj or io.open(name, mode)
        self._header_range, self._headers = get_headers(self._fileobj)
        # print("CHRIS header range %s"%(self._header_range,))
        self._ownes_fd = fileobj is not None

    @property
    def data_offset(self):
        return self._header_range[1]

    @property
    def header_range(self):
        return self._header_range

    @property
    def headers(self):
        'RPM headers'
        return self._headers

    def __enter__(self):
        return self

    def __exit__(self, *excinfo):
        if self._ownes_fd:
            self._fileobj.close()

    _members = None

    def getmembers(self):
        '''
        Return the members of the archive as a list of RPMInfo objects. The
        list has the same order as the members in the archive.
        '''
        if self._members is None:
            self._members = _members = []
            g = self.gzip_file
            tmp_magic = g.read(2)
            magic = tmp_magic.decode('utf-8')
            while magic:
                if magic == '07':
                    tmp_magic = g.read(4)
                    magic += tmp_magic.decode('utf-8')
                    member = RPMInfo._read(magic, g)
                    if member.name == 'TRAILER!!!':
                        break

                    # if not member.isdir:
                    # We need all members to match with the metadata info
                    _members.append(member)
                tmp_magic = g.read(2)
                magic = tmp_magic.decode('utf-8')
            return _members
        return self._members

    def getmember(self, name):
        '''
        Return an RPMInfo object for member `name'. If `name' can not be
        found in the archive, KeyError is raised. If a member occurs more
        than once in the archive, its last occurrence is assumed to be the
        most up-to-date version.
        '''
        members = self.getmembers()
        for m in members[::-1]:
            if m.name == name:
                return m

        raise KeyError("member %s could not be found" % name)

    def extractfile(self, member):
        '''
        Extract a member from the archive as a file object. `member' may be
        a filename or an RPMInfo object.
        The file-like object is read-only and provides the following
        methods: read(), readline(), readlines(), seek() and tell()
        '''
        if not isinstance(member, RPMInfo):
            member = self.getmember(member)
        return _SubFile(self.gzip_file, member.file_start, member.size)

    _gzip_file = None

    @property
    def gzip_file(self):
        'Return the uncompressed raw CPIO data of the RPM archive'
        if self._gzip_file is None:
            fileobj = _SubFile(self._fileobj, self.data_offset)
            if self.headers['archive_compression'] == 'xz':
                # print("CHRIS _fileobj %s data_offset %s"%(self._fileobj,
                #                                           self.data_offset))
                # self._gzip_file = gzip.GzipFile(fileobj=fileobj)
                # self._gzip_file = lzma.LZMAFile(filename =fileobj)
                self._gzip_file = lzma.LZMAFile(fileobj)
            elif self.headers['archive_compression'] == 'gzip':
                self._gzip_file = gzip.GzipFile(fileobj=fileobj)
            else:
                raise Exception('to be decided')
        return self._gzip_file


def open(name=None, mode='rb', fileobj=None):
    '''
    Open an RPM archive for reading. Return
    an appropriate RPMFile class.
    '''
    return RPMFile(name, mode, fileobj)


def main():
    print(sys.argv[1])
    with open(sys.argv[1]) as rpm:
        print(rpm.headers)
        for m in rpm.getmembers():
            print(m)
        print('done')


if __name__ == '__main__':
    main()
