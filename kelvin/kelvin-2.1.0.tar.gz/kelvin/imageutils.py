
from ctypes import *
from os.path import exists, basename, join, dirname, isabs
from distutils.errors import *

PSTR      = c_char_p
DWORD     = c_uint
ULONG_PTR = POINTER(c_ulong)

def find_dependencies(image, path):
    """
    Returns DLLs that `image` is dependent on as a mapping from lowercased DLL file name to its
    fully qualified path.  If a DLL is not found on the path, it maps to None.

    image
      Fully qualified path to an executable or DLL.

    path
      A Windows path string to search.
    """
    ih = windll.Imagehlp
    bi = ih.BindImageEx
    bi.argtypes = [ DWORD, PSTR, PSTR, PSTR, IMAGEHLP_STATUS_ROUTINE ]

    GetLastError = windll.kernel32.GetLastError

    BIND_NO_BOUND_IMPORTS = 0x00000001
    BIND_NO_UPDATE        = 0x00000002
    BIND_ALL_IMAGES       = 0x00000004

    assert exists(image), image

    # Strangely, Imagehlp only supports ASCII filenames.
    imageA = image.encode('UTF8')
    pathA  = path.encode('UTF8')

    global map_module_to_path
    map_module_to_path = {}

    callback = IMAGEHLP_STATUS_ROUTINE(StatusRoutine)
    b = bi(BIND_NO_BOUND_IMPORTS | BIND_ALL_IMAGES | BIND_NO_UPDATE, imageA, pathA, None, callback)
    if b == 0:
        raise DistutilsInternalError('BindImageEx({}) failed with error {}'.format(image, GetLastError()))

    return map_module_to_path


BindOutOfMemory           = 1
BindRvaToVaFailed         = 2
BindNoRoomInImage         = 3
BindImportModuleFailed    = 4
BindImportProcedureFailed = 5
BindImportModule          = 6
BindImportProcedure       = 7
BindForwarder             = 8
BindForwarderNOT          = 9
BindImageModified         = 10
BindExpandFileHeaders     = 11
BindImageComplete         = 12
BindMismatchedSymbols     = 13
BindSymbolsNotUpdated     = 14
BindImportProcedure32     = 15
BindImportProcedure64     = 16
BindForwarder32           = 17
BindForwarder64           = 18
BindForwarderNOT32        = 19
BindForwarderNOT64        = 20

seen_modules = set() # module names with no path
seen_fqn     = [] # fully qualified names
bad_modules = set() # Modules that could not be loaded

map_module_to_path = {}
# If a module is required but not found, the value will be None.

IMAGEHLP_STATUS_ROUTINE = WINFUNCTYPE(c_int, DWORD, PSTR, PSTR, ULONG_PTR, ULONG_PTR)

def StatusRoutine(reason, imageName, dllName, va, param):
    dllName = dllName.decode('ascii')

    if isabs(dllName):
        module = basename(dllName).lower()
        map_module_to_path[module] = dllName
        return 1

    else:
        # dllName is just a module name.  Since it might be passed in as a fully-qualified path
        # later, just store it for now and we'll resolve them to full paths elsewhere.
        module = dllName.lower()
        if module not in map_module_to_path:
            map_module_to_path[module] = None

    return 1


if __name__ == '__main__':
    imagename  = "C:\\bin\\python32\\python.exe"
    searchpath = "C:\\bin\\python32;c:\\bin\\java6\\bin;C:\\Windows\\system32;C:\\Windows;C:\\Windows\\System32\\Wbem;C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\;C:\\Program Files\\Intel\\WiFi\\bin\\;C:\\Program Files\\Common Files\\Intel\\WirelessCommon\\;C:\\Program Files (x86)\\Common Files\\Roxio Shared\\OEM\\DLLShared\\;C:\\Program Files (x86)\\Common Files\\Roxio Shared\\OEM\\DLLShared\\;C:\\Program Files (x86)\\Common Files\\Roxio Shared\\OEM\\12.0\\DLLShared\\;C:\\Program Files (x86)\\Roxio\\OEM\\AudioCore\\;C:\\Program Files (x86)\\Microsoft SQL Server\\100\\Tools\\Binn\\;C:\\Program Files\\Microsoft SQL Server\\100\\Tools\\Binn\\;C:\\Program Files\\Microsoft SQL Server\\100\\DTS\\Binn\\;C:\\Program Files (x86)\\Microsoft SQL Server\\100\\Tools\\Binn\\VSShell\\Common7\\IDE\\;C:\\Program Files (x86)\\Microsoft SQL Server\\100\\DTS\\Binn\\;C:\\bin\\mercurial\\;C:\\bin\\graphviz\\bin;C:\\PROGRA~2\\IBM\\GSK7_64\\bin;C:\\PROGRA~2\\IBM\\GSK7_64\\lib64;C:\\Program Files\\IBM\\GSK7_64\\bin;C:\\Program Files\\IBM\\GSK7_64\\lib64;C:\\PROGRA~2\\ibm\\gsk7\\bin;C:\\PROGRA~2\\ibm\\gsk7\\lib;C:\\Program Files (x86)\\ibm\\gsk7\\bin;C:\\Program Files (x86)\\ibm\\gsk7\\lib;c:\\bin\\git\\cmd;c:\\bin\\git\\bin;C:\\bin\\svn\\bin;C:\\Program Files (x86)\\QuickTime\\QTSystem\\;c:\\bin\\utils;c:\\bin\\git\\bin;c:\\bin\\python27;c:\\bin\\emacs\\bin;c:\\bin\\python27\\Scripts;C:\\dev\\kelvin\\kelvin;C:\\dev\\kelvin\\tmp;C:\\Windows\\system32\\python32.zip;C:\\bin\\python32\\DLLs;C:\\bin\\python32\\lib;C:\\bin\\python32;C:\\bin\\python32\\lib\\site-packages"
    found, missing = find_dependencies(imagename, searchpath)
    print('found:', found)
    print('missing:', missing)
