''' 
    Blocks for encoding/decoding video based on MPlayer. 

    Needs ffmepg > 0.8.6 that is present in Ubuntu 12.04. No PPA available. 
    Download static version from http://ffmpeg.gusari.org/
    (http://ffmpeg.gusari.org/static/64bit/ffmpeg.static.64bit.latest.tar.gz)
    and place in path.
'''


from .depth_buffer import *
from .fix_frame_rate import *
from .mencoder import *
from .mp4conversion import convert_to_mp4
from .mplayer import *
from .quick_animation import *


procgraph_info = {
    # List of python packages 
    'requires': ['qtfaststart']
}


from procgraph import pg_add_this_package_models
pg_add_this_package_models(__file__, __package__)

