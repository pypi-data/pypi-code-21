import struct

import win32api


def get_file_properties(fname):
    """
    Read all properties of the given file return them as a dictionary.
    props = {'FixedFileInfo': , 'StringFileInfo': , 'FileVersion': }
    """
    propNames = ('Comments', 'InternalName', 'ProductName',
                 'CompanyName', 'LegalCopyright', 'ProductVersion',
                 'FileDescription', 'LegalTrademarks', 'PrivateBuild',
                 'FileVersion', 'OriginalFilename', 'SpecialBuild')

    props = {}

    try:
        # backslash as parm returns dictionary of numeric info corresponding
        # to VS_FIXEDFILEINFO struc
        fI = win32api.GetFileVersionInfo(fname, '\\')
        props['FixedFileInfo'] = fI
        props['FileVersion'] = "%d.%d.%d.%d" % (fI['FileVersionMS'] / 65536,
                                                fI['FileVersionMS'] % 65536,
                                                fI['FileVersionLS'] / 65536,
                                                fI['FileVersionLS'] % 65536)

        # \VarFileInfo\Translation returns list of available
        # (language, codepage), pairs that can be used to
        # retreive string info. We are using only the first pair.
        varstr = '\\VarFileInfo\\Translation'
        lang, codepage = win32api.GetFileVersionInfo(fname, varstr)[0]

        # any other must be of the form \StringfileInfo\%04X%04X\parm_name,
        # middle, two are language/codepage pair returned from above
        strInfo = {}
        varstr = '\\StringFileInfo\\%04X%04X\\%s'
        for propName in propNames:
            strInfoPath = varstr % (lang, codepage, propName)
            # print str_info
            strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)

        props['StringFileInfo'] = strInfo
    except:
        pass

    return props


IMAGE_FILE_MACHINE_I386 = 332
IMAGE_FILE_MACHINE_IA64 = 512
IMAGE_FILE_MACHINE_AMD64 = 34404


def get_image_file_type(fname):
    with open(fname, "rb") as f:
        s = f.read(2)
        if s != b"MZ":
            return 0
        f.seek(60)
        s = f.read(4)
        header_offset = struct.unpack("<L", s)[0]
        f.seek(header_offset + 4)
        s = f.read(2)
        return struct.unpack("<H", s)[0]
