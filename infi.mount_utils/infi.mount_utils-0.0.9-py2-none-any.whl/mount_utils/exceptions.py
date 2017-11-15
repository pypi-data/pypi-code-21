from infi.exceptools import InfiException

class MountException(InfiException):
    pass

class IncorrectInvocationOrPermissions(MountException):
    pass

class SystemErrorException(MountException):
    pass

class MountInternalBugException(MountException):
    pass

class UserInterruptException(MountException):
    pass

class ProblemWithWritingOrLockingException(MountException):
    pass

class MountFailureException(MountException):
    pass

class SomeMountSucceededException(MountException):
    pass


ERRORCODES_DICT = {1:IncorrectInvocationOrPermissions,
                   2:SystemErrorException,
                   4:MountInternalBugException,
                   8:UserInterruptException,
                   16:ProblemWithWritingOrLockingException,
                   32:MountFailureException,
                   64:SomeMountSucceededException}

def translate_mount_error(errorno):
    if ERRORCODES_DICT.has_key(errorno):
        return ERRORCODES_DICT.get(errorno)
    else:
        return MountException(errorno)
