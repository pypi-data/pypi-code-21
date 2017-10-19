from .timestamps import TIMESTAMP_FIELD, iso_from_timestamp
from procgraph.utils import system_cmd_result, CmdException
import os
import yaml
from . import logger


def get_ffmpeg_metadata_args(md, timestamp):
    args = []
    if timestamp is not None:
        iso = iso_from_timestamp(timestamp)
        # timestamp_ff = str(dt)
        # args += ['-timestamp', timestamp_ff] # deprecated
        md['creation_time'] = iso
        md[TIMESTAMP_FIELD] = iso
    for k, v in md.items():
        args += ['-metadata', '%s=%s' % (k, v)]
    return args

def get_metadata_file(filename):
    return filename + '.metadata.yaml'

def write_extra_metadata_for(filename, md):
    metadata_file = get_metadata_file(filename) 
    with open(metadata_file, 'w') as f:
        f.write(yaml.dump(md, default_flow_style=False))

def read_extra_metadata_for(filename):
    metadata_file = get_metadata_file(filename)
    if not os.path.exists(metadata_file):
        return dict(warning='Metadata file %s did not exist' % filename)  
    with open(metadata_file, 'r') as f:
        return yaml.load(f)


def ffmpeg_get_metadata(video):
    cmds = ['ffmpeg', '-i', video, '-f', 'ffmetadata', '-']
    try:
        res = system_cmd_result('.', cmds,
                  display_stdout=False,
                  display_stderr=False,
                  raise_on_error=True,
                  capture_keyboard_interrupt=False)
    except CmdException as e:
        # TODO: be more descriptive
        logger.debug(e)
        return {}
    
    lines = res.stdout.split('\n')
    assert lines[0] == ';FFMETADATA1'
    
    keys = {}
    for line in lines[1:]:
        line = line.strip()
        if not line: 
            continue
        k, v = line.split('=')
        if v[0] == "'":
            v = v[1:-1]
            
        k = k.lower()
        keys[k] = v
    
    return dict(keys)
