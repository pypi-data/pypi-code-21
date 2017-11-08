"""exceptions.py: custom exceptions and warnings for prosper.common libaries"""

class ProsperCommonException(Exception):
    """base class for prosper.common exceptions"""
    pass
class ProsperVersionException(ProsperCommonException):
    """base class for prosper.common.version exceptions"""
    pass

class ProsperCommonWarning(UserWarning):
    """base class for prosper.common warnings"""
    pass
class ProsperLoggerWarning(ProsperCommonWarning):
    """base class for prosper.common.prosper_logging warnings"""
    pass
class WebhookFailedEmitWarning(ProsperLoggerWarning):
    """Something went wrong in webhook handler.  Warn rather than raise"""
    pass
class WebhookCreateFailed(ProsperLoggerWarning):
    """unable to generate webhook requested"""
    pass

class ProsperVersionWarning(ProsperCommonWarning):
    """base class for prosper.common.prosper_version warnings"""
    pass
class ProsperVersionTestModeWarning(ProsperVersionWarning):
    """for overriding Travis modes for unit testing coverage"""
    pass
class ProsperDefaultVersionWarning(ProsperVersionWarning):
    """unable to set any version other than default.  New project or broken git?"""
    pass
