import inspect
from ..frame.frame import BaseFrame
from ..frame.label import BaseLabelFrame


def locate_calling_base_frame(frame=None):
    u"""
    Locate the calling BaseFrame or BaseLabelFrame
    :param frame: a frame reference or none
    :return: BaseFrame or BaseLabelFrame instance.
             This can be: the provided frame
                      or: the first BaseFrame or BaseLabelFrame
                          found when scanning back through the
                          stack.
    """
    if frame is None:
        stack = inspect.stack()
        for stack_frame in stack:
            try:
                obj = stack_frame[0].f_locals[u'self']
                if isinstance(obj, (BaseFrame, BaseLabelFrame)):
                    frame = obj
                    break
            except KeyError:
                pass  # Not called from an object
    if not frame:
        raise RuntimeError(u"Introspection failure. 'frame' parameter was not provided "
                           u"and could not find BaseFrame or BaseLabelFrame in stack.")

    return frame
