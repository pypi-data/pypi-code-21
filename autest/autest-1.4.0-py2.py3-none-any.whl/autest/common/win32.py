# ctypes wrapper to a number of win32 API's
# this is used to avoid use of win32api which
# is not always there.
# This allows me to avoid
# copy and paste of code in different files.
# this is a continous growing file...
# Will probally break up into a module
from __future__ import absolute_import, division, print_function
import os

if os.name == 'nt':

    import ctypes
    import collections
    from ctypes.wintypes import *

    # utils functions
    # this stub function allows try to get the function without breaking
    def _stubFunction(*_):
        ctypes.set_last_error(ERROR_INVALID_FUNCTION)
        return 0

    def tryKernel32(name, restype, argtypes):
        ''' Util function that allows us to test to see if we can import a function
            or not. This allows us to get at "new" win32 function on newer setups
            while not breaking older setups
        '''

        try:
            func = getattr(ctypes.windll.kernel32, name)
        except AttributeError:
            return _stubFunction

        func.argtypes = argtypes
        func.restype = restype

        return func

    def tryAdvapi32(name, restype, argtypes):
        ''' Util function that allows us to test to see if we can import a function
            or not. This allows us to get at "new" advapi32 function on newer setups
            while not breaking older setups
        '''

        try:
            func = getattr(ctypes.windll.advapi32, name)
        except AttributeError:
            return _stubFunction

        func.argtypes = argtypes
        func.restype = restype

        return func

    LPFILETIME = ctypes.POINTER(FILETIME)
    LPLARGE_INTEGER = ctypes.POINTER(LARGE_INTEGER)

    # constants taken from MSDN

    # thread flags .. clean up threads
    TH32CS_SNAPPROCESS = 0x2    # snapshot all the processes on the system
    TH32CS_SNAPTHREAD = 0x4     # snapshot all the threads on the system
    THREAD_SUSPEND_RESUME = 0x2  # suspend or resume a thread

    # process rights

    PROCESS_TERMINATE = 0x0001
    PROCESS_CREATE_THREAD = 0x0002
    PROCESS_SET_SESSIONID = 0x0004
    PROCESS_VM_OPERATION = 0x0008
    PROCESS_VM_READ = 0x0010
    PROCESS_VM_WRITE = 0x0020
    PROCESS_DUP_HANDLE = 0x0040
    PROCESS_CREATE_PROCESS = 0x0080
    PROCESS_SET_QUOTA = 0x0100
    PROCESS_SET_INFORMATION = 0x0200
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SUSPEND_RESUME = 0x0800
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    PROCESS_SET_LIMITED_INFORMATION = 0x2000

    FILE_SHARE_READ = 1
    FILE_SHARE_WRITE = 2
    FILE_SHARE_DELETE = 4

    GENERIC_READ = 0x80000000
    GENERIC_WRITE = 0x40000000

    CREATE_NEW = 1
    CREATE_ALWAYS = 2
    OPEN_EXISTING = 3
    OPEN_ALWAYS = 4
    TRUNCATE_EXISTING = 5

    MAX_PATH = 260

    SmallProcessInfo = collections.namedtuple(
        'SmallProcessInfo', 'name pid ppid')
    SmallThreadInfo = collections.namedtuple('SmallThreadInfo', 'tid pid')

    class ProcessEntry32(ctypes.Structure):
        _fields_ = [('dwSize',              DWORD),
                    ('cntUsage',            DWORD),
                    ('th32ProcessID',       DWORD),
                    ('th32DefaultHeapID',   ctypes.POINTER(ctypes.c_ulong)),
                    ('th32ModuleID',        DWORD),
                    ('cntThreads',          DWORD),
                    ('th32ParentProcessID', DWORD),
                    ('pcPriClassBase',      ctypes.c_long),
                    ('dwFlags',             DWORD),
                    ('szExeFile',           ctypes.c_char * MAX_PATH)]

        def __init__(self):
            ctypes.Structure.__init__(self)
            self.dwSize = ctypes.sizeof(self)

        def getInfo(self):
            return SmallProcessInfo(self.szExeFile, self.th32ProcessID, self.th32ParentProcessID)

    class ThreadEntry32(ctypes.Structure):
        _fields_ = [('dwSize',             DWORD),
                    ('cntUsage',           DWORD),
                    ('th32ThreadID',       DWORD),
                    ('th32OwnerProcessID', DWORD),
                    ('tpBasePri',          ctypes.c_long),
                    ('tpDeltaPri',         ctypes.c_long),
                    ('dwFlags',            DWORD)]

        def __init__(self):
            ctypes.Structure.__init__(self)
            self.dwSize = ctypes.sizeof(self)

        def getInfo(self):
            return SmallThreadInfo(self.th32ThreadID, self.th32OwnerProcessID)

    class ByHandleFileInformation(ctypes.Structure):
        _fields_ = [('dwFileAttributes', DWORD),
                    ('ftCreationTime', FILETIME),
                    ('ftLastAccessTime', FILETIME),
                    ('ftLastWriteTime', FILETIME),
                    ('dwVolumeSerialNumber', DWORD),
                    ('nFileSizeHigh', DWORD),
                    ('nFileSizeLow', DWORD),
                    ('nNumberOfLinks', DWORD),
                    ('nFileIndexHigh', DWORD),
                    ('nFileIndexLow', DWORD)]

    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_ = [('nLength', DWORD),
                    ('lpSecurityDescriptor', ctypes.POINTER(ctypes.c_void_p)),
                    ('bInheritHandle', BOOL)]

    # Job Objects and enums
    # I am probally missing something...

    JOB_OBJECT_MSG_END_OF_JOB_TIME = 1
    JOB_OBJECT_MSG_END_OF_PROCESS_TIME = 2
    JOB_OBJECT_MSG_ACTIVE_PROCESS_LIMIT = 3
    JOB_OBJECT_MSG_ACTIVE_PROCESS_ZERO = 4
    JOB_OBJECT_MSG_NEW_PROCESS = 6
    JOB_OBJECT_MSG_EXIT_PROCESS = 7
    JOB_OBJECT_MSG_ABNORMAL_EXIT_PROCESS = 8
    JOB_OBJECT_MSG_PROCESS_MEMORY_LIMIT = 9
    JOB_OBJECT_MSG_JOB_MEMORY_LIMIT = 10
    JOB_OBJECT_MSG_NOTIFICATION_LIMIT = 11
    JOB_OBJECT_MSG_JOB_CYCLE_TIME_LIMIT = 12

    # Define the valid notification filter values.

    JOB_OBJECT_MSG_MINIMUM = 1
    JOB_OBJECT_MSG_MAXIMUM = 12

    # Basic Limits
    JOB_OBJECT_LIMIT_WORKINGSET = 0x00000001
    JOB_OBJECT_LIMIT_PROCESS_TIME = 0x00000002
    JOB_OBJECT_LIMIT_JOB_TIME = 0x00000004
    JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
    JOB_OBJECT_LIMIT_AFFINITY = 0x00000010
    JOB_OBJECT_LIMIT_PRIORITY_CLASS = 0x00000020
    JOB_OBJECT_LIMIT_PRESERVE_JOB_TIME = 0x00000040
    JOB_OBJECT_LIMIT_SCHEDULING_CLASS = 0x00000080

    # Extended Limits

    JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
    JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
    JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION = 0x00000400
    JOB_OBJECT_LIMIT_BREAKAWAY_OK = 0x00000800
    JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK = 0x00001000
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    JOB_OBJECT_LIMIT_SUBSET_AFFINITY = 0x00004000

    JOB_OBJECT_LIMIT_JOB_READ_BYTES = 0x00010000
    JOB_OBJECT_LIMIT_JOB_WRITE_BYTES = 0x00020000
    JOB_OBJECT_LIMIT_RATE_CONTROL = 0x00040000

    # Valid Job Object Limits

    JOB_OBJECT_LIMIT_VALID_FLAGS = 0x0007ffff
    JOB_OBJECT_BASIC_LIMIT_VALID_FLAGS = 0x000000ff
    JOB_OBJECT_EXTENDED_LIMIT_VALID_FLAGS = 0x00007fff
    JOB_OBJECT_NOTIFICATION_LIMIT_VALID_FLAGS = 0x00070204
    JOB_OBJECT_RESERVED_LIMIT_VALID_FLAGS = 0x0007ffff

    # UI restrictions for jobs

    JOB_OBJECT_UILIMIT_NONE = 0x00000000

    JOB_OBJECT_UILIMIT_HANDLES = 0x00000001
    JOB_OBJECT_UILIMIT_READCLIPBOARD = 0x00000002
    JOB_OBJECT_UILIMIT_WRITECLIPBOARD = 0x00000004
    JOB_OBJECT_UILIMIT_SYSTEMPARAMETERS = 0x00000008
    JOB_OBJECT_UILIMIT_DISPLAYSETTINGS = 0x00000010
    JOB_OBJECT_UILIMIT_GLOBALATOMS = 0x00000020
    JOB_OBJECT_UILIMIT_DESKTOP = 0x00000040
    JOB_OBJECT_UILIMIT_EXITWINDOWS = 0x00000080

    JOB_OBJECT_UILIMIT_ALL = 0x000000FF

    JOB_OBJECT_UI_VALID_FLAGS = 0x000000FF

    JOB_OBJECT_SECURITY_NO_ADMIN = 0x00000001
    JOB_OBJECT_SECURITY_RESTRICTED_TOKEN = 0x00000002
    JOB_OBJECT_SECURITY_ONLY_TOKEN = 0x00000004
    JOB_OBJECT_SECURITY_FILTER_TOKENS = 0x00000008

    JOB_OBJECT_SECURITY_VALID_FLAGS = 0x0000000f

    # Control flags for CPU rate control.

    JOB_OBJECT_CPU_RATE_CONTROL_ENABLE = 0x1
    JOB_OBJECT_CPU_RATE_CONTROL_WEIGHT_BASED = 0x2
    JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP = 0x4
    JOB_OBJECT_CPU_RATE_CONTROL_NOTIFY = 0x8
    JOB_OBJECT_CPU_RATE_CONTROL_VALID_FLAGS = 0xf

    # Documented JOBOBJECTINFOCLASS enums values
    JobObjectBasicAccountingInformation = 1
    JobObjectBasicLimitInformation = 2
    JobObjectBasicProcessIdList = 3
    JobObjectBasicUIRestrictions = 4
    JobObjectEndOfJobTimeInformation = 6
    JobObjectAssociateCompletionPortInformation = 7
    JobObjectBasicAndIoAccountingInformation = 8
    JobObjectExtendedLimitInformation = 9
    JobObjectJobSetInformation = 10
    JobObjectGroupInformation = 11
    JobObjectNotificationLimitInformation = 12
    JobObjectLimitViolationInformation = 13
    JobObjectGroupInformationEx = 14
    JobObjectCpuRateControlInformation = 15
    JobObjectCompletionFilter = 16
    JobObjectCompletionCounter = 17

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [("ReadOperationCount", ctypes.c_ulonglong),
                    ("WriteOperationCount", ctypes.c_ulonglong),
                    ("OtherOperationCount", ctypes.c_ulonglong),
                    ("ReadTransferCount", ctypes.c_ulonglong),
                    ("WriteTransferCount", ctypes.c_ulonglong),
                    ("OtherTransferCount", ctypes.c_ulonglong), ]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [('PerProcessUserTimeLimit', LARGE_INTEGER),
                    ('PerJobUserTimeLimit', LARGE_INTEGER),
                    ('LimitFlags', DWORD),
                    ('MinimumWorkingSetSize', ctypes.c_ssize_t),
                    ('MaximumWorkingSetSize', ctypes.c_ssize_t),
                    ('ActiveProcessLimit', DWORD),
                    ('Affinity', LPVOID),
                    ('PriorityClass', DWORD),
                    ('SchedulingClass', DWORD), ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [('BasicLimitInformation', JOBOBJECT_BASIC_LIMIT_INFORMATION),
                    ('IoInfo', IO_COUNTERS),
                    ('ProcessMemoryLimit', ctypes.c_ssize_t),
                    ('JobMemoryLimit', ctypes.c_ssize_t),
                    ('PeakProcessMemoryUsed', ctypes.c_ssize_t),
                    ('PeakJobMemoryUsed', ctypes.c_ssize_t), ]

    class _min_max_rate(ctypes.Structure):
        _fields_ = [('MinRate', WORD),
                    ('MaxRate', WORD)]

    class _JOBOBJECT_CPU_RATE_CONTROL_INFORMATION(ctypes.Union):
        _anonymous_ = ('_MM',)
        _fields_ = [('CpuRate', DWORD),
                    ('Weight', DWORD),
                    ('_MM', _min_max_rate)]

    class JOBOBJECT_CPU_RATE_CONTROL_INFORMATION(ctypes.Structure):
        _anonymous_ = ('_JOBOBJECT_CPU_RATE_CONTROL_INFORMATION',)
        _fields_ = [('ControlFlags', DWORD),
                    ('_JOBOBJECT_CPU_RATE_CONTROL_INFORMATION', _JOBOBJECT_CPU_RATE_CONTROL_INFORMATION)]

    # structs and constants used to check for admin prilvileges
    class SID_IDENTIFIER_AUTHORITY(ctypes.Structure):
        _fields_ = [('byte0', ctypes.c_byte),
                    ('byte1', ctypes.c_byte),
                    ('byte2', ctypes.c_byte),
                    ('byte3', ctypes.c_byte),
                    ('byte4', ctypes.c_byte),
                    ('byte5', ctypes.c_byte)]

    SECURITY_BUILTIN_DOMAIN_RID = 0x20
    DOMAIN_ALIAS_RID_ADMINS = 0x220

##############################################################
    # function not currently in any good order
##############################################################

    # basic handle handling
    CloseHandle = tryKernel32("CloseHandle", BOOL, (HANDLE,))

    CreateToolhelp32Snapshot = tryKernel32(
        "CreateToolhelp32Snapshot", HANDLE, (DWORD, DWORD))

    # Debugging API
    DebugActiveProcess = tryKernel32("DebugActiveProcess", BOOL, (DWORD,))
    DebugActiveProcessStop = tryKernel32(
        "DebugActiveProcessStop", BOOL, (DWORD,))

    # Process/thread handling
    Process32First = tryKernel32(
        "Process32First", BOOL, (HANDLE, ctypes.POINTER(ProcessEntry32)))
    Process32Next = tryKernel32(
        "Process32Next", BOOL, (HANDLE, ctypes.POINTER(ProcessEntry32)))

    Thread32First = tryKernel32(
        "Thread32First", BOOL, (HANDLE, ctypes.POINTER(ThreadEntry32)))
    Thread32Next = tryKernel32(
        "Thread32Next", BOOL, (HANDLE, ctypes.POINTER(ThreadEntry32)))

    OpenThread = tryKernel32("OpenThread", HANDLE, (DWORD, BOOL, DWORD))
    SuspendThread = tryKernel32("SuspendThread", DWORD, (HANDLE,))

    OpenProcess = tryKernel32("OpenProcess", HANDLE, (DWORD, BOOL, DWORD))
    TerminateProcess = tryKernel32(
        "TerminateProcess", BOOL, (HANDLE, ctypes.c_uint))
    GetProcessTimes = tryKernel32(
        "GetProcessTimes", BOOL, (HANDLE, LPFILETIME, LPFILETIME, LPFILETIME, LPFILETIME))

    # the wait function
    WaitForSingleObject = tryKernel32(
        "WaitForSingleObject", DWORD, (HANDLE, DWORD))

    # Job object
    CreateJobObject = tryKernel32(
        "CreateJobObjectW", HANDLE, (ctypes.POINTER(SECURITY_ATTRIBUTES), LPWSTR))
    AssignProcessToJobObject = tryKernel32(
        "AssignProcessToJobObject", BOOL, (HANDLE, HANDLE))
    TerminateJobObject = tryKernel32(
        "TerminateJobObject", BOOL, (HANDLE, UINT))
    SetInformationJobObject = tryKernel32(
        "SetInformationJobObject", BOOL, (HANDLE, ctypes.c_uint32, LPVOID, DWORD))
    QueryInformationJobObject = tryKernel32(
        "QueryInformationJobObject", BOOL, (HANDLE, ctypes.c_uint32, LPVOID, DWORD, LPVOID))

    # file APIs
    CreateSymbolicLink = tryKernel32(
        'CreateSymbolicLinkW', BOOLEAN, (LPWSTR, LPWSTR, DWORD))
    CreateHardLink = tryKernel32(
        'CreateHardLinkW', BOOLEAN, (LPWSTR, LPWSTR, DWORD))
    CopyFile = tryKernel32('CopyFileW', BOOLEAN, (LPWSTR, LPWSTR, BOOL))
    DeleteFile = tryKernel32('DeleteFileW', BOOLEAN, (LPWSTR,))

    # advapi functions used for privilege checking
    _AllocateAndInitializeSid = tryAdvapi32("AllocateAndInitializeSid", BOOL,
                                            (ctypes.POINTER(SID_IDENTIFIER_AUTHORITY), BYTE, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, ctypes.c_void_p()))

    _CheckTokenMembership = tryAdvapi32("CheckTokenMembership", BOOL,
                                        (HANDLE, ctypes.c_void_p(), ctypes.POINTER(BOOL)))

    FreeSid = tryAdvapi32("FreeSid", LPVOID, (LPVOID,))

    def AllocateAndInitializeSid(pIdentifierAuthority, nSubAuthorityCount,
                                 dwSubAuthority0, dwSubAuthority1, dwSubAuthority2, dwSubAuthority3, dwSubAuthority4, dwSubAuthority5, dwSubAuthority6, dwSubAuthority7):

        admin_group = ctypes.c_void_p()

        if not _AllocateAndInitializeSid(pIdentifierAuthority, nSubAuthorityCount, dwSubAuthority0, dwSubAuthority1, dwSubAuthority2, dwSubAuthority3,
                                         dwSubAuthority4, dwSubAuthority5, dwSubAuthority6, dwSubAuthority7, ctypes.byref(admin_group)):
            raise WindowsError(ctypes.GetLastError(), ctypes.FormatError(ctypes.GetLastError()))

        return admin_group

    def CheckTokenMembership(TokenHandle, SidToCheck):
        is_admin = BOOL()

        if not _CheckTokenMembership(TokenHandle, SidToCheck, ctypes.byref(is_admin)):
            raise WindowsError(ctypes.GetLastError(), ctypes.FormatError(ctypes.GetLastError()))

        return is_admin

    def _long_path(path):
        if len(path) >= 200 and not path.startswith("\\\\?\\"):
            path = "\\\\?\\" + os.path.abspath(path)
        return path

    # some overides.. might want to do this differently later
    def win32_rm(path):
        path = _long_path(path)
        if not DeleteFile(path):
            raise WindowsError(ctypes.GetLastError(),
                               ctypes.FormatError(ctypes.GetLastError()), path)

    os.remove = win32_rm
    os.unlink = win32_rm

    def win32_link(source, link_name):
        source = _long_path(source)
        link_name = _long_path(link_name)
        if not CreateHardLink(link_name, source, 0):
            raise WindowsError(ctypes.GetLastError(), ctypes.FormatError(
                ctypes.GetLastError()), link_name)

    os.link = win32_link

    def win32_symlink(source, link_name):
        source = _long_path(source)
        link_name = _long_path(link_name)
        if not CreateSymbolicLink(link_name, source, 0):
            raise WindowsError(ctypes.GetLastError(), ctypes.FormatError(
                ctypes.GetLastError()), link_name)

    os.symlink = win32_symlink

    def user_is_admin():
        nt_authority = SID_IDENTIFIER_AUTHORITY()
        nt_authority.byte5 = 5

        administrator_group = AllocateAndInitializeSid(
            nt_authority, 2, SECURITY_BUILTIN_DOMAIN_RID, DOMAIN_ALIAS_RID_ADMINS, 0, 0, 0, 0, 0, 0)

        try:
            # invert C boolean, in Condition.IsElevated, we are using 0 as pass value since 0 is uid for root in *nixes
            return not CheckTokenMembership(0, administrator_group)
        finally:
            FreeSid(administrator_group)
