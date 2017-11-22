import os
import time
from ctypes import *
from ctypes.wintypes import *
from contextlib import contextmanager

from enum import IntEnum


ENV_FOR_SERVICE_NAME = '8198CE51-0D47-4FF9-9CDE-C531D466A7F7'


class CtypesEnum(IntEnum):
    @classmethod
    def from_param(cls, obj):
        return int(obj)


advapi32 = WinDLL('advapi32')
kernel32 = WinDLL('kernel32')


SC_MANAGER_ALL_ACCESS = 0xF003F
SERVICE_ALL_ACCESS = 0xF01FF
SERVICE_WIN32_OWN_PROCESS = 0x00000010
SERVICE_DEMAND_START = 0x00000003
SERVICE_ERROR_NORMAL = 0x00000001
SERVICE_AUTO_START = 0x00000002
DELETE = 0x00010000
SC_STATUS_PROCESS_INFO = 0

STANDARD_RIGHTS_REQUIRED = 0x000F0000
SC_MANAGER_CONNECT = 0x0001
SC_MANAGER_CREATE_SERVICE = 0x0002
SC_MANAGER_ENUMERATE_SERVICE = 0x0004
SC_MANAGER_LOCK = 0x0008
SC_MANAGER_QUERY_LOCK_STATUS = 0x0010
SC_MANAGER_MODIFY_BOOT_CONFIG = 0x0020

SERVICE_STOPPED = 0x00000001
SERVICE_START_PENDING = 0x00000002
SERVICE_STOP_PENDING = 0x00000003
SERVICE_RUNNING = 0x00000004

SERVICE_STOP = 0x0020
SERVICE_QUERY_STATUS = 0x0004
SERVICE_ENUMERATE_DEPENDENTS = 0x0008
SERVICE_CONTROL_STOP = 0x00000001

SC_MANAGER_ALL_ACCESS = STANDARD_RIGHTS_REQUIRED\
                        | SC_MANAGER_CONNECT\
                        | SC_MANAGER_CREATE_SERVICE\
                        | SC_MANAGER_ENUMERATE_SERVICE\
                        | SC_MANAGER_LOCK\
                        | SC_MANAGER_QUERY_LOCK_STATUS\
                        | SC_MANAGER_MODIFY_BOOT_CONFIG

SYNCHRONIZE = 0x00100000
EVENT_ALL_ACCESS = STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0x3

INFINITE = 0xFFFFFFFF

SERVICE_CHANGE_CONFIG = 0x0002
SERVICE_NO_CHANGE = 0xffffffff


class SC_STATUS_TYPE(CtypesEnum):
    SC_STATUS_PROCESS_INFO = 0


class SERVICE_STATUS(Structure):
    _fields_ = [
        ('dwServiceType', DWORD),
        ('dwCurrentState', DWORD),
        ('dwControlsAccepted', DWORD),
        ('dwWin32ExitCode', DWORD),
        ('dwServiceSpecificExitCode', DWORD),
        ('dwCheckPoint', DWORD),
        ('dwWaitHint', DWORD)
    ]


class SERVICE_STATUS_PROCESS(Structure):
    _fields_ = [
        ('dwServiceType', DWORD),
        ('dwCurrentState', DWORD),
        ('dwControlsAccepted', DWORD),
        ('dwWin32ExitCode', DWORD),
        ('dwServiceSpecificExitCode', DWORD),
        ('dwCheckPoint', DWORD),
        ('dwWaitHint', DWORD),
        ('dwProcessId', DWORD),
        ('dwServiceFlags', DWORD)
    ]


OpenSCManager = WINFUNCTYPE(
    SC_HANDLE,
    LPCWSTR,  # lpMachineName
    LPCWSTR,  # lpDatabaseName
    DWORD  # dwDesiredAccess
)(('OpenSCManagerW', advapi32))


CloseServiceHandle = WINFUNCTYPE(
    BOOL,
    SC_HANDLE  # hSCObject
)(('CloseServiceHandle', advapi32))


CreateService = WINFUNCTYPE(
    SC_HANDLE,
    SC_HANDLE,  # hSCManager
    LPCWSTR,  # lpServiceName
    LPCWSTR,  # lpDisplayName
    DWORD,  # dwDesiredAccess
    DWORD,  # dwServiceType
    DWORD,  # dwStartType
    DWORD,  # dwErrorControl
    LPCWSTR,  # lpBinaryPathName
    LPCWSTR,  # lpLoadOrderGroup
    LPDWORD,  # lpdwTagId
    LPCWSTR,  # lpDependencies
    LPCWSTR,  # lpServiceStartName
    LPCWSTR,  # lpPassword
)(('CreateServiceW', advapi32))


GetLastError = WINFUNCTYPE(
    DWORD
)(('GetLastError', kernel32))


CloseHandle = WINFUNCTYPE(
    BOOL,
    HANDLE  # hObject
)(('CloseHandle', kernel32))


OpenService = WINFUNCTYPE(
    SC_HANDLE,
    SC_HANDLE,  # sc_manager
    LPCWSTR,  # service_name
    DWORD  # dwDesiredAccess
)(('OpenServiceW', advapi32))


DeleteService = WINFUNCTYPE(
    BOOL,
    SC_HANDLE  # hService
)(('DeleteService', advapi32))


GetTickCount = WINFUNCTYPE(
    DWORD
)(('GetTickCount', kernel32))


StartService = WINFUNCTYPE(
    BOOL,
    SC_HANDLE,  # hService
    DWORD,  # dwNumServiceArgs
    LPWSTR  # lpServiceArgVectors
)(('StartServiceW', advapi32))


ControlService = WINFUNCTYPE(
    BOOL,
    SC_HANDLE,  # hService
    DWORD,  # dwControl
    POINTER(SERVICE_STATUS)  # lpServiceStatus
)(('ControlService', advapi32))


QueryServiceStatusEx = WINFUNCTYPE(
    BOOL,
    SC_HANDLE,  # hService
    SC_STATUS_TYPE,  # InfoLevel
    LPBYTE,  # lpBuffer
    DWORD,  # cbBufSize
    LPDWORD  # pcbBytesNeeded
)(('QueryServiceStatusEx', advapi32))


OpenEvent = WINFUNCTYPE(
    HANDLE,
    DWORD,  # dwDesiredAccess
    BOOL,  # bInheritHandle
    LPWSTR  # lpName
)(('OpenEventW', kernel32))


WaitForSingleObject = WINFUNCTYPE(
    DWORD,
    HANDLE,  # hHandle
    DWORD  # dwMilliseconds
)(('WaitForSingleObject', kernel32))


ChangeServiceConfig = WINFUNCTYPE(
    BOOL,
    SC_HANDLE,  # hService
    DWORD,  # dwServiceType
    DWORD,  # dwStartType
    DWORD,  # dwErrorControl
    LPWSTR,  # lpBinaryPathName
    LPWSTR,  # lpLoadOrderGroup
    LPDWORD,  # lpdwTagId
    LPWSTR,  # lpDependencies
    LPWSTR,  # lpServiceStartName
    LPWSTR,  # lpPassword
    LPWSTR,  # lpDisplayName
)(('ChangeServiceConfigW', advapi32))


def check_last_error():
    code = GetLastError()
    if code != 0:
        raise WinError(code)


def guard(close_handle=CloseHandle):
    def real_guard(f):
        @contextmanager
        def wrapper(*args, **kwargs):
            handle = f(*args, **kwargs)
            try:
                check_last_error()
                yield handle
            finally:
                close_handle(handle)
        return wrapper
    return real_guard


@guard(CloseServiceHandle)
def open_sc_manager():
    return OpenSCManager(None, None, SC_MANAGER_ALL_ACCESS)


@guard(CloseServiceHandle)
def create_service(service_name, cmd, service_start_name, password):
    with open_sc_manager() as sc_manager:
        return CreateService(
            sc_manager,
            service_name,
            service_name,
            SERVICE_ALL_ACCESS,
            SERVICE_WIN32_OWN_PROCESS,
            SERVICE_AUTO_START,
            SERVICE_ERROR_NORMAL,
            cmd,
            None, None, None,
            service_start_name, password
        )


@guard(CloseServiceHandle)
def open_service(service_name, access):
    with open_sc_manager() as sc_manager:
        return OpenService(sc_manager, service_name, access)


@guard(CloseHandle)
def open_event(access, service_name):
    return OpenEvent(access, False, service_name)


def query_service_status_ex(sch_service, ss_status, dw_bytes_needed):
    QueryServiceStatusEx(
        sch_service,
        SC_STATUS_TYPE.SC_STATUS_PROCESS_INFO,
        LPBYTE(ss_status),
        sizeof(SERVICE_STATUS_PROCESS),
        PDWORD(dw_bytes_needed)
    )
    check_last_error()


def set_user(username, password, service_name=None):
    service_name = service_name or os.environ[ENV_FOR_SERVICE_NAME]
    with open_service(service_name, SERVICE_CHANGE_CONFIG) as sch_service:
        if not ChangeServiceConfig(
            sch_service,
            SERVICE_NO_CHANGE, SERVICE_NO_CHANGE, SERVICE_NO_CHANGE,
            None, None, None, None,
            username, password,
            None
        ):
            check_last_error()


def status_wait(sch_service, state, equal):
    ss_status = SERVICE_STATUS_PROCESS()
    dw_bytes_needed = DWORD()

    query_service_status_ex(sch_service, ss_status, dw_bytes_needed)

    dw_start_tick_count = GetTickCount()
    dw_old_check_point = ss_status.dwCheckPoint

    while (ss_status.dwCurrentState == state) != equal:
        dw_wait_time = ss_status.dwWaitHint / 10
        if dw_wait_time < 1000:
            dw_wait_time = 1000;
        elif dw_wait_time > 10000:
            dw_wait_time = 10000

        time.sleep(dw_wait_time / 1000);

        query_service_status_ex(sch_service, ss_status, dw_bytes_needed)

        if ss_status.dwCheckPoint > dw_old_check_point:
            dw_start_tick_count = GetTickCount()
            dw_old_check_point = ss_status.dwCheckPoint
        else:
            if (GetTickCount() - dw_start_tick_count) > ss_status.dwWaitHint:
                check_last_error()


def start(service_name):
    ss_status = SERVICE_STATUS_PROCESS()
    dw_bytes_needed = DWORD()

    with open_service(service_name, SC_MANAGER_ALL_ACCESS) as sch_service:
        query_service_status_ex(sch_service, ss_status, dw_bytes_needed)
        if ss_status.dwCurrentState != SERVICE_STOPPED and \
                ss_status.dwCurrentState != SERVICE_STOP_PENDING:
            check_last_error()

        status_wait(sch_service, SERVICE_STOP_PENDING, False)

        if not StartService(sch_service, 0, None):
            check_last_error()

        status_wait(sch_service, SERVICE_START_PENDING, False)

        query_service_status_ex(sch_service, ss_status, dw_bytes_needed)
        if ss_status.dwCurrentState != SERVICE_RUNNING:
            WinError(ss_status.dwWin32ExitCode)


def stop(service_name):
    ss_status = SERVICE_STATUS_PROCESS()
    dw_bytes_needed = DWORD()

    with open_service(
        service_name,
        SERVICE_STOP | SERVICE_QUERY_STATUS | SERVICE_ENUMERATE_DEPENDENTS
    ) as sch_service:
        query_service_status_ex(sch_service, ss_status, dw_bytes_needed)

        if ss_status.dwCurrentState == SERVICE_STOPPED:
            check_last_error()

        status_wait(sch_service, SERVICE_STOP_PENDING, False)

        if not ControlService(
            sch_service,
            SERVICE_CONTROL_STOP,
            POINTER(SERVICE_STATUS)(ss_status)
        ):
            check_last_error()

        status_wait(sch_service, SERVICE_STOPPED, True)

        query_service_status_ex(sch_service, ss_status, dw_bytes_needed)

        if ss_status.dwCurrentState != SERVICE_STOPPED:
            raise WinError(ss_status.dwWin32ExitCode)


def wait(f):
    service_name = os.environ[ENV_FOR_SERVICE_NAME]

    with open_event(EVENT_ALL_ACCESS, service_name) as event:
        WaitForSingleObject(event, INFINITE)
    f()
