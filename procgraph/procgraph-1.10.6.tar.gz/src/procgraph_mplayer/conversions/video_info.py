from .metadata import ffmpeg_get_metadata, read_extra_metadata_for
from .timestamps import TIMESTAMP_FIELD, timestamp_from_iso
from contracts import contract, raise_wrapped
from procgraph.utils import CmdException, system_cmd_result
import math
import os


@contract(returns='dict(str:*)')
def pg_video_info(filename, intolerant=True):
    """
          Returns a dictionary, with fields:
        
            metadata
            
            width, height
            
            fps* (might fail)
            length* (might fail)
            
            timestamp # start timestamp
                        
            extra_mencoder_info
                
        Tries to read precise timestamp from metadata; otherwise 
        it tries from the .timestamps file; otherwise from the file's mtime.
        
        Mplayer might fail to identify FPS and length. If intolerant=True,
        an error is raised, otherwise they are set to None. 
    """
    if not os.path.exists(filename):
        msg = 'File %r does not exist.' % filename
        raise ValueError(msg)

    info = mplayer_identify(filename, intolerant=intolerant)
    
    info['metadata'] = ffmpeg_get_metadata(filename)
        
    extra_md = read_extra_metadata_for(filename)
    
    info['metadata'].update(extra_md)
    
    precise = info['metadata'].get(TIMESTAMP_FIELD, None)
    if precise is None:
        # logger.info('No precise timestamp in metadata found for %s' % filename)
        timestamp = os.path.getmtime(filename)
    else:
        # logger.info('Precise timestamp found for %s' % filename)
        timestamp = timestamp_from_iso(precise)
        
    timestamps = filename + '.timestamps'
    if os.path.exists(timestamps):
        # logger.info('Reading timestamps from %r.' % timestamps)
        f = open(timestamps)
        line = f.readline()
        # print('frist line: %s' % line)
        timestamp = float(line)
        # print('timestamp: %s' % timestamp)


    info['timestamp'] = timestamp
    
    return info



def mplayer_identify(filename, intolerant=True):
    """
        Returns a dictionary, with fields:
        
            width, height
            fps *
            length * 
            
            extra_mencoder_info
            
        Mplayer might fail to identify FPS and length. If intolerant=True,
        an error is raised, otherwise they are set to None.
    
    """
 
    # need at least 1 frame otherwise sometimes the video aspect is not known
    args = ('mplayer -identify -vo null -ao null -frames 1'.split()
            + [filename])
    
    try:
        
        try:
            res = system_cmd_result('.', args,
                      display_stdout=False,
                      display_stderr=False,
                      raise_on_error=True,
                      capture_keyboard_interrupt=False)
        except CmdException:
            raise 
        
    except Exception as e:
        raise_wrapped(Exception, e, "Could not identify movie", 
                      filename=filename)

    try:
        output = res.stdout
        return parse_mplayer_info_output(output,intolerant=intolerant)
    except Exception as e:
        raise_wrapped(Exception, e, "Could not identify movie",
                      cmd=" ".join(args), filename=filename,
                      output=output)
    

def parse_mplayer_info_output(output, intolerant=True):
    keys = ["ID_VIDEO_WIDTH", "ID_VIDEO_HEIGHT",
            "ID_VIDEO_FPS", "ID_LENGTH", "ID_VIDEO_ASPECT"]
    id_width, id_height, id_fps, id_length, id_video_aspect = keys

    info = {}
    for line in output.split('\n'):
        if line.startswith('ID_'):
            key, value = line.split('=', 1)
            try:  # interpret numbers if possible
                value = eval(value)
            except:
                pass
            if key in info:
                # print('overriding %r=%r from %r' % (key,value,info[key]))
                pass
            info[key] = value

    for k in keys:
        if not k in info:
            msg = ('Could not find key %r in properties %s.' % 
                  (k, sorted(info.keys())))
            raise Exception(msg)

    if id_length == 0:
        msg = 'I could not find find the length of this video.' 
        raise Exception(msg)
    
    res = {}
    res['width'] = info[id_width]
    res['height'] = info[id_height]
    if isinstance(info[id_fps], str):
        msg = 'Invalid fps %r:\n' % info[id_fps]
        if intolerant:
            raise ValueError(msg)
        else:
            print(msg) # XXX
        res['fps'] = None
    else:
        res['fps'] = float(info[id_fps])
    
    res['length'] = info[id_length]
    
    if not res['length'] > 0:
        if intolerant:
            msg = 'invalid length %r' % res['length']
            raise ValueError(msg)
        else:
            res['length'] = None
#     check('float,>0', res['length'])
    
    res['extra_mencoder_info'] = info
    
    w_over_h = res['width'] * 1.0 / res['height']
    
    dar = info[id_video_aspect] * 1.0
    if dar == 0:
        # dar = 1.0
        dar = w_over_h
        
    res['dar'] = dar
    #     print('dar', dar)
    
    # dar/sar = width/height
    
    #print('w_over_h', w_over_h)
    # sar = dar / w_over_h 
    sar = res['dar'] / w_over_h
    #     print('sar', sar) 
    if math.fabs(1.0-sar) < 0.01:
        sar = 1.0
    res['sar'] = sar 
    return res
    
