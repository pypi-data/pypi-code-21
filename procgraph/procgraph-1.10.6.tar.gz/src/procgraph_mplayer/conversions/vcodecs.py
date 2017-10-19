from .containers import CONTAINER_MOV, CONTAINER_MKV, CONTAINER_MP4
from contracts import contract
from procgraph.utils.calling_ext_program import system_cmd_result
from procgraph_mplayer.conversions.containers import CONTAINER_AVI

VCODEC_X264 = 'x264'
VCODEC_PRORES = 'prores'


@contract(profile='0|1|2|3')
def get_prores_encoder_params(profile=3, qv=None):
    assert profile in [0, 1, 2, 3]
    cmds = []
    cmds += ['-vcodec', 'prores_kostya']
    cmds += ['-profile:v', str(profile)]
    if qv is not None:
        cmds += ['-q:v', str(qv)]    
    return cmds


def get_x264_encoder_params(crf=18, preset='medium'):
    cmds = []
    cmds += ['-vcodec', 'libx264']
    # Let's detect ffmpeg version
    res = system_cmd_result('.', ['ffmpeg', '-version'])
    ffmpeg_version = res.stdout.split('\n')[0]
    
    # SVN-r0.5.9-4:0.5.9-0ubuntu0.10.04.3
    
    # if 'ubuntu0.10.04.3' in ffmpeg_version:
    if '0.5' in ffmpeg_version:  # or '0.8.6' in ffmpeg_version:
        cmds += ['-vpre', 'libx264-default']
    else:
        cmds += ['-preset', preset]

    cmds += ['-crf', '%d' % crf]
    return cmds

VCODECS = {
   VCODEC_PRORES: get_prores_encoder_params,
   VCODEC_X264: get_x264_encoder_params
}



@contract(returns='tuple(str, dict(str:*))')
def guess_vcodec(container):
    choices = {
        CONTAINER_MP4: (VCODEC_X264, dict()),
        CONTAINER_MKV: (VCODEC_X264, dict()),
        CONTAINER_MOV: (VCODEC_PRORES, dict()),
        CONTAINER_AVI: (VCODEC_X264, dict()),  # XXX: not sure
    }
    return choices[container]
    
    
