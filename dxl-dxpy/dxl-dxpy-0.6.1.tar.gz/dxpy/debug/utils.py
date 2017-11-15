import sys


class ExceptionHook:
    instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            from IPython.core import ultratb
            self.instance = ultratb.FormattedTB(mode='Plain',
                                                color_scheme='Linux', call_pdb=1)
        return self.instance(*args, **kwargs)


def enter_debug():
    sys.excepthook = ExceptionHook()


_last_msg_file = None


def dbgmsg(*args, **kwargs):
    global _last_msg_file
    from .config import verbose
    if verbose <= 0:
        return
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe().f_back)
    fn = frameinfo.filename
    if _last_msg_file is None or not _last_msg_file == fn:
        _last_msg_file = fn
        print('[DEBUG] MESSAGE(S) FROM:', _last_msg_file)
    print('[DEBUG:{ln}]'.format(ln=frameinfo.lineno), *args, **kwargs)
