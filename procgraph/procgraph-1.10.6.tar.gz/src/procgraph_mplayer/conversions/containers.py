import os

from procgraph.utils import system_cmd_result, CmdException

from . import logger


CONTAINER_MP4 = 'mp4'
CONTAINER_MOV = 'mov'
CONTAINER_MKV = 'mkv'
CONTAINER_AVI = 'avi'
CONTAINERS = [CONTAINER_MOV, CONTAINER_MP4, CONTAINER_MKV, CONTAINER_AVI]

def supports_full_metadata(container):
    return container in [CONTAINER_MKV] 


def guess_container(filename):    
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    choices = {
       '.mp4': CONTAINER_MP4,
       '.mkv': CONTAINER_MKV,
       '.mov': CONTAINER_MOV,
       '.avi': CONTAINER_AVI,
   }
    if not ext in choices:
        raise ValueError(ext)
    return choices[ext]


def do_quickstart(source, target):
    # TODO: check file exists
    names = ['qtfaststart', 'qt-faststart']
    errors = []
    for name in names:
        cmd = [name, source, target]
        try:

            system_cmd_result('.', cmd,
                      display_stdout=True,
                      display_stderr=True,
                      raise_on_error=True,
                      capture_keyboard_interrupt=False)
            break
        except CmdException as e:
            errors.append(e)

    else:
        msg = ('Could not call either of %s. '
               'The file will not be ready for streaming.\n%s' % 
               (names, errors))
        logger.error(msg)
        os.rename(source, target)    
