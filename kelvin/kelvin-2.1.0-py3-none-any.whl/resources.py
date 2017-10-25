# Python functions for dealing with Windows resources.

# The encodings should be UCS2 but Python 3.6 does not seem to have it.  I'm going to use
# UTF-16LE, so don't use anything that wouldn't be compatible.

# http://blogs.msdn.com/b/oldnewthing/archive/2006/12/20/1332035.aspx
# http://blogs.msdn.com/b/oldnewthing/archive/2006/12/21/1340571.aspx
#
# "Version resources can be viewed as a serialized tree structure. Each node of the tree has a
#  name and associated data (either binary or text), and each node can have zero or more child
#  nodes."

from ctypes import Structure, string_at, addressof, sizeof, windll, WinError
from ctypes import c_long, c_void_p, c_short, c_longlong
import struct, re
from os.path import exists

RT_VERSION  = 16
RT_MANIFEST = 24

LANG_NEUTRAL    = 0x00
SUBLANG_NEUTRAL = 0x00

VOS_NT_WINDOWS32   = 0x00040004
VS_FF_SPECIALBUILD = 0x00000020
VS_FF_PRERELEASE   = 0x00000002
VFT_APP            = 0x00000001

HANDLE = c_longlong
BOOL   = c_long
WORD   = c_short
DWORD  = c_long


def AddVersionResource(exe, version, version_strings):
    """
    Adds a version resource to the given executable, constructed from `version_strings`.

    version
      The executable version as a string.  It can only contain numbers and periods and can have
      up to 4 parts.

    version_strings
      Maps from language identifier (int) to a dictionary of key / value pairs that are the
      version strings for that language.  Use 0x0409 for English.
    """
    # Parse version numbers.  We'll take any integers in the order they were found.
    # We need 4 parts total, so fill with 0s and truncate.

    parts = [int(n) for n in re.findall('\d+', version)]
    parts = (parts + [0, 0, 0, 0])[:4]

    ffi = VS_FIXEDFILEINFO()
    ffi.dwSignature        = 0xFEEF04BD
    ffi.dwStrucVersion     = 0x00010000
    ffi.dwFileVersionMS    = (parts[0] << 16) | parts[1]
    ffi.dwFileVersionLS    = (parts[2] << 16) | parts[3]
    ffi.dwProductVersionMS = (parts[0] << 16) | parts[1]
    ffi.dwProductVersionLS = (parts[2] << 16) | parts[3]
    ffi.dwFileFlagsMask    = 0x3F
    ffi.dwFileFlags        = 0x00
    ffi.dwFileOS           = VOS_NT_WINDOWS32
    ffi.dwFileType         = VFT_APP

    if version_strings:
        for lang, strings in version_strings.items():
            if 'SpecialBuild' in strings:
                ffi.dwFileFlags |= VS_FF_SPECIALBUILD

    root = VersionNode('VS_VERSION_INFO', ffi)

    sfi = VersionNode('StringFileInfo', None)
    root.children.append(sfi)

    words = []
    if version_strings:
        for lang, strings in version_strings.items():
            lang = VersionNode('{:04X}{:04X}'.format(lang, 0x04B0), None)
            sfi.children.append(lang)

            for name, value in strings.items():
                lang.children.append(VersionNode(name, (value + '\0').encode('utf_16_le')))

        for lang in version_strings:
            words.append(lang)
            words.append(0x04B0)

    vfi = VersionNode('VarFileInfo', None)
    root.children.append(vfi)

    # The Translation block is a child of VarFileInfo.  Normally we copy the languages from
    # the version_strings, but if they are not found we'll put something in.
    if not words:
        words = [0x0409, 0x04B0]

    translation = struct.pack('H' * len(words), *words)
    vfi.children.append(VersionNode('Translation', translation))

    UpdateFileVersion(exe, root.tobytes())


class VersionNode:
    def __init__(self, name, value):
        """
        name
          The name of the node.

        value
          The node's data, not including children.  This can be:

          * None if there is no data
          * A ctypes.Structure instance (e.g. VS_FIXEDFILEINFO)
          * A bytes instance for binary data
          * A string for string data.
        """
        self.name = name

        # Set wType to string (1) if there is no data to match StringFileInfo.  I'm not sure if
        # it matters.
        self.wType = (value is None or isinstance(value, str)) and 1 or 0

        if isinstance(value, Structure):
            value = string_at(addressof(value), sizeof(value))
        elif isinstance(value, str):
            # We need to write the NULL terminator and it needs to be included in the length.
            value = (value + '\0').encode('utf_16_le')

        self.value = value
        self.children = []

    def tobytes(self):
        """
        Returns this node encoded as an unpadded VERSIONNODE.
        """
        if self.value is not None:
            valuelen = len(self.value)
        else:
            valuelen = 0

        parts = [
            b'--',  # placeholder for cbNode
            struct.pack('HH', valuelen, self.wType),
            (self.name + '\0').encode('utf_16_le')
        ]

        cbNode = sum(len(part) for part in parts)

        if self.value is not None:
            cbNode = self.add_aligned(parts, cbNode, self.value)

        for child in self.children:
            cbNode = self.add_aligned(parts, cbNode, child.tobytes())

        parts[0] = struct.pack('H', cbNode)

        return b''.join(parts)

    def add_aligned(self, parts, length, value):
        """
        Adds `value` to the parts list and returns the updated byte length of items in the
        list.

        If the current length of items in the list (`length`) is not aligned on a 32-bit
        boundary, padding will be inserted before the value.
        """
        if not value:
            return length

        r = length % 4
        if r:
            padding = (b'\0' * 3)[:(4 - r)]
            parts.append(padding)
            length += len(padding)

        parts.append(value)
        length += len(value)

        return length

    def dump(self, indent=0):
        print('{}{} = {}'.format(' ' * indent, self.name, self.value))
        indent += 4
        for child in self.children:
            child.dump(indent=indent)


class VS_FIXEDFILEINFO(Structure):
    _fields_ = [
        ("dwSignature", DWORD),
        ("dwStrucVersion", DWORD),
        ("dwFileVersionMS", DWORD),
        ("dwFileVersionLS", DWORD),
        ("dwProductVersionMS", DWORD),
        ("dwProductVersionLS", DWORD),
        ("dwFileFlagsMask", DWORD),
        ("dwFileFlags", DWORD),
        ("dwFileOS", DWORD),
        ("dwFileType", DWORD),
        ("dwFileSubtype", DWORD),
        ("dwFileDateMS", DWORD),
        ("dwFileDateLS", DWORD)
    ]


def dump(a):
    offset = 0
    while a:
        line, a = a[:16], a[16:]

        parts = ['%04x ' % offset]

        parts.append(' '.join('%02X' % ord(b) for b in line[:8]))
        parts.append('-')
        parts.append(' '.join('%02X' % ord(b) for b in line[8:]))
        parts.append(' ')
        parts.append(''.join((31 <= ord(b) < 128) and b or '.' for b in line))
        print(''.join(parts))

        offset += 16


def MAKELANGID(p, s):
    return int(((s & 0xFF) << 10) | (p & 0xFF))


def UpdateFileVersion(filename, version):
    # NB: Remember that Win64 uses 32-bit longs and 64-bit pointers.  A HANDLE in Windows is a
    # pointer, so we use c_longlong.  The type ane name parameters to UpdateResource are
    # character strings, but we're using the integer versions, so those need to be c_longlong
    # too.  (We might be able to use c_void_p.  I didn't want to deal with c_types conversions
    # when I know the bit sizes.)

    kernel32 = windll.kernel32
    BeginUpdateResource = kernel32.BeginUpdateResourceW
    UpdateResource      = kernel32.UpdateResourceW
    EndUpdateResource   = kernel32.EndUpdateResourceW

    # BOOL WINAPI UpdateResource(
    # _In_     HANDLE  hUpdate,
    # _In_     LPCTSTR lpType,
    # _In_     LPCTSTR lpName,
    # _In_     WORD    wLanguage,
    # _In_opt_ LPVOID  lpData,
    # _In_     DWORD   cbData
    # );

    BeginUpdateResource.restype = HANDLE
    UpdateResource.argtypes     = [HANDLE, c_longlong, c_longlong, c_short, c_void_p, c_long]
    EndUpdateResource.argtypes  = [HANDLE, BOOL]

    if not exists(filename):
        raise Exception('file does not exist: %s' % filename)

    h = BeginUpdateResource(filename, 0)
    if not h:
        raise WinError()

    if not UpdateResource(h, RT_VERSION, 1, MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL), version,
                          len(version)):
        raise WinError()

    if not EndUpdateResource(h, 0):
        raise WinError()
