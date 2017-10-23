from .log import log

def log_error(exc, msg=None):
    if msg is None:
        log.error("Operation failed: %s", exc)
    else:
        log.error("Operation failed: %s (%s)", msg, exc)



def handle_error(exc, msg, on_error=None):
    if on_error is not None:
        on_error(exc)
    log_error(exc)