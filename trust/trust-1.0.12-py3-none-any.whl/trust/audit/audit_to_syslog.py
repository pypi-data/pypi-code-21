from .audit_to_log import AuditToLog
import logging
import logging.handlers


class AuditToSyslog(AuditToLog):
    def __init__(self,
                 name,
                 address="/dev/log",
                 facility=logging.handlers.SysLogHandler.LOG_AUTH):
        logHandler = logging.handlers.SysLogHandler(
            address=address, facility=facility
        )

        formatter = logging.Formatter(name + ": [%(levelname)s] %(message)s")
        logHandler.setFormatter(formatter)

        logHandler.setLevel(logging.INFO)

        log = logging.getLogger(name)
        log.addHandler(logHandler)
        log.setLevel(logging.INFO)

        super(AuditToSyslog, self).__init__(log)
