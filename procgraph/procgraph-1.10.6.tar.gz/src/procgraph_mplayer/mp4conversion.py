from .conversions.containers import do_quickstart
from .conversions.metadata import get_ffmpeg_metadata_args
from .conversions.vcodecs import (get_x264_encoder_params,
    get_prores_encoder_params)
from system_cmd import system_cmd_result, CmdException
import os

def validate_args(filename, out, my_ext):
    """ Returns out """ 
    
    basename, _ = os.path.splitext(filename)

    if out is None:
        out = basename + my_ext
        
    if os.path.splitext(out)[1] != my_ext:
        msg = 'I expect a %r as out (%r)' % (my_ext, out)
        raise ValueError(msg)

    if os.path.splitext(filename)[1] == my_ext:
        msg = 'Need a file that does not end in %r (%r)' % (my_ext, filename)
        raise ValueError(msg)
    
    if not os.path.exists(filename):
        msg = 'Input filename does not exist (%r)' % filename
        raise ValueError(msg)

    if os.path.exists(out):
        os.unlink(out)
        
    return out



def convert_to_mov_prores(filename, out=None, quiet=True, profile=3, qv=None, timestamp=None, metadata={}):
    my_ext = '.mov'    
    out = validate_args(filename, out, my_ext)

    cmds = ['ffmpeg']
    cmds += ['-y']
    cmds += ['-i', filename]
    cmds += ['-f', 'mov']
    cmds += ['-an']  # no audio
    cmds += get_prores_encoder_params(profile, qv)
    cmds += get_ffmpeg_metadata_args(metadata, timestamp)
    cmds += [out]
    
    try:
        system_cmd_result('.', cmds,
                  display_stdout=not quiet,
                  display_stderr=not quiet,
                  raise_on_error=True,
                  capture_keyboard_interrupt=False)
    except CmdException:
        if os.path.exists(out):
            os.unlink(out)
        raise
    
    assert os.path.exists(out)


def convert_to_mkv_mp4(filename, out=None, quiet=True, crf=18, preset='medium', timestamp=None, metadata={}):
    """
        Converts to a matrioska file with all metadata.
        
    """
    my_ext = '.mkv'
    out = validate_args(filename, out, my_ext)
    

    cmds = ['ffmpeg']
    cmds += ['-y']
    cmds += ['-i', filename]
    cmds += get_x264_encoder_params(crf, preset)
    cmds += get_ffmpeg_metadata_args(metadata, timestamp)
    cmds += [out]
    
    try:
        system_cmd_result('.', cmds,
                  display_stdout=not quiet,
                  display_stderr=not quiet,
                  raise_on_error=True,
                  capture_keyboard_interrupt=False)
    except CmdException:
        if os.path.exists(out):
            os.unlink(out)
        raise
    
    assert os.path.exists(out)

    
def convert_to_mp4(filename, mp4=None, quiet=True, crf=18, preset='medium', timestamp=None, metadata={}):
    """ 
        Creates a web-ready mp4 using ffmpeg.
    
        Needs either qtquickstart (from the python package) or qt-quickstart from ffmpeg.
        
        On ubuntu 12.04: need 'sudo apt-get install x264 libavcodec-extra-53'
        to install necessary codecs.
        You can see a list of supported presets by using: 'x264 --help'.
    
        
        (other packages that might be helpful: # libavdevice-extra-52  libavfilter-extra-0 
         libavformat-extra-52 libavutil-extra-49 libpostproc-extra-51 libswscale-extra-0)
       
    """
    my_ext = '.mp4'
    
    if os.path.splitext(mp4)[1] != my_ext:
        msg = 'I expect a %r as out (%r)' % (my_ext, mp4)
        raise ValueError(msg)

    if os.path.splitext(filename)[1] == my_ext:
        msg = 'Need a file that does not end in %r (%r)' % (my_ext, filename)
        raise ValueError(msg)
    
    basename, _ = os.path.splitext(filename)

    if mp4 is None:
        mp4 = basename + my_ext

    # need .mp4 at the end otherwise ffmpeg gets confused
    tmp = basename + '.mp4.firstpass.mp4'

    if not os.path.exists(filename):
        raise ValueError("File does not exist: %s" % filename)

#    if (os.path.exists(mp4) and
#        (os.path.getmtime(mp4) > os.path.getmtime(filename))):
#        return

    if os.path.exists(tmp):
        os.unlink(tmp)
    if os.path.exists(mp4):
        os.unlink(mp4)

    cmds = ['ffmpeg']
    cmds += ['-y']
    cmds += ['-i', filename]
    cmds += get_x264_encoder_params(crf, preset)
    cmds += get_ffmpeg_metadata_args(metadata, timestamp)
    cmds += [tmp]
    
    print cmds
    
    try:
        system_cmd_result('.', cmds,
                  display_stdout=not quiet,
                  display_stderr=not quiet,
                  raise_on_error=True,
                  capture_keyboard_interrupt=False)
    except CmdException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise

    do_quickstart(source=tmp, target=mp4)
    
    if os.path.exists(tmp):
        os.unlink(tmp)
