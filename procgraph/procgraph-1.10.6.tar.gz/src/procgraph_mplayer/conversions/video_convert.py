from .containers import (CONTAINERS, CONTAINER_MP4, do_quickstart, 
    guess_container, supports_full_metadata)
from .metadata import get_ffmpeg_metadata_args, write_extra_metadata_for
from .vcodecs import VCODECS, guess_vcodec
from .video_info import pg_video_info
from contracts import contract
from procgraph import logger
from procgraph.utils import CmdException, system_cmd_result
import os


__all__ = ['pg_video_convert']


@contract(timestamp='None|float|int', metadata='dict', vcodec_params='dict')
def pg_video_convert(filename,
                     out,
                     quiet=True,
                     container=None,
                     vcodec=None,
                     vcodec_params={},
                     timestamp=None,
                     metadata={}):
    """
        Converts a video file (e.g. an AVI) to another format.
        
        
        container: one of "mkv", "mp4", "mov"
        
        vcodec : vcodec params with defaults
        'prores': profile=3, qv=None
        'x264': crf=18, preset='medium'
        
        It makes sure to write information to preserve timestamp 
        and the given metadata.
        
        One can then be guaranteed to access this data using 
        the pg_info_video() function. 
    """
    logger.info('pg_video_convert:\n<- %s\n-> %s' % (filename, out))
    
    if container is None:
        container = guess_container(out)
        
    assert container in CONTAINERS 

    if vcodec is None:
        vcodec, vcodec_params = guess_vcodec(container)
    
    logger.info('container: %s' % container)
    logger.info('vcodec: %s' % vcodec)
    logger.info('vcodec_params: %s' % vcodec_params)

    no_audio = True

    cmds = ['ffmpeg']
    
    # For using aac out
    # cmds += ['-strict', '-2']
    
    cmds += ['-y']
    cmds += ['-i', filename]
    
    if no_audio:
        cmds += ['-an']
        
    cmds += VCODECS[vcodec](**vcodec_params)
    
    info = pg_video_info(filename, intolerant=False)
    info['metadata'].update(metadata) 
    
    if timestamp is None:
        timestamp = info['timestamp']
    else:
        timestamp = float(timestamp)
        
    cmds += get_ffmpeg_metadata_args(metadata, timestamp)
    # cmds += ['-f', container]
    
    if container == CONTAINER_MP4:
        out1 = out + '.firstpass.mp4'
        cmds += [out1]
    else:
        out1 = out
        cmds += [out1]
    
    
    try:
        system_cmd_result('.', cmds,
                  display_stdout=not quiet,
                  display_stderr=not quiet,
                  raise_on_error=True,
                  capture_keyboard_interrupt=False)
    except CmdException:
        if os.path.exists(out1):
            os.unlink(out1)
        raise
    
    assert os.path.exists(out1)
    
    if container == CONTAINER_MP4:
        do_quickstart(out1, out)
        os.remove(out1)
        # warnings.warn("Not sure why quickstart does not work.")
        # os.rename(out1, out)
    else:
        assert out1 == out 
        
    if not os.path.exists(out):
        logger.error('Something is wrong, path does not exist.\nPath: %s' % out)

    if not supports_full_metadata(container):
        write_extra_metadata_for(out, metadata)
        



    
