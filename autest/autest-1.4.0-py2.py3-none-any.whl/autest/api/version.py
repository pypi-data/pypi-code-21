import autest
import autest.common.version as version

def AuTestVersion():
    return version.Version(autest.__version__)
