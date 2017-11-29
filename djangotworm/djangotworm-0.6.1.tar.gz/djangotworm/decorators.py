from twisted.internet import threads
from functools import wraps

# def error(failure):
#     print(str(failure.type).split("'")[1])
#     print(failure.getBriefTraceback().split()[-1])
#     print(failure.getErrorMessage())
    # logger.error('%(error_line)s - %(error_type)s: %(error_msg)s' % {
    #     'error_type': str(failure.type).split("'")[1],
    #     'error_line': failure.getBriefTraceback().split()[-1],
    #     'error_msg': failure.getErrorMessage(),
    # })


def make_asynclike(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if not getattr(self, 'defered', False):
            def task_done(result):
                self.defered = False
                return result
            self.defered = True
            result = threads.deferToThread(method, self, *args, **kwargs)
            # result.addErrback(error)
            result.addCallback(task_done)
        else:
            result = method(self, *args, **kwargs)
        return result
    return wrapped


def make_asynclike_instance(method):
    #use for instance method's of some class
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if not getattr(self, 'defered', False):
            def task_done(result):
                self.defered = False
                return result
            self.defered = True
            result = threads.deferToThread(method, *args, **kwargs)
            # result.addErrback(error)
            result.addCallback(task_done)
        else:
            result = method(*args, **kwargs)
        return result
    return wrapped
