#!/usr/bin/env python
from optparse import OptionParser
from procgraph import pg, register_model_spec
import os

usage = """
    %cmd  -o <output> -p <pattern> -d <dirname>
"""


def main():
    parser = OptionParser(usage=usage)

    parser.add_option("-o", dest='output', type="string",
                      help='Output video.')

    parser.add_option("-d", dest='dirname', type="string", default='.',
                      help='Directory.')

    parser.add_option("--fps", type="float", default=10.0,
                      help='Frames per second')

    parser.add_option("-p", dest='pattern', type="string",
                      default='([\w-]+)(\d+)\.(\w+)',
                      help='Pattern')

    (options, args) = parser.parse_args()
    if args:
        raise Exception("Spurious arg: %s" % args)
    
    if options.output is None:
        options.output = os.path.join(options.dirname, 'output.mp4')
    
    return join_video(options.output, options.dirname, options.pattern, options.fps)


def join_video(output, dirname, pattern, fps):
    """ 
        Note that the pattern is a Python regex:
        
        pg-video-join -d anim-simple/ -p '*.png' -o anim-simple-collate.mp4 --fps 1 
        
    """
    register_model_spec("""
--- model join_video_helper
config output
config dirname
config pattern
config fps

|files_from_dir dir=$dirname regexp=$pattern| -->file
#file --> |print|
file --> |imread_rgb| --> rgb
#file --> |imread| --> |torgb| --> rgb


rgb --> |mencoder quiet=1 file=$output timestamps=0 fps=$fps|
    
    """)

    pg('join_video_helper', dict(dirname=dirname, pattern=pattern, output=output,
                                 fps=fps))


def join_video_29(output, dirname, pattern, fps):
    """ 
        Note that the pattern is a Python regex:
        
        pg-video-join -d anim-simple/ -p '*.png' -o anim-simple-collate.mp4 --fps 1 
        
    """
    register_model_spec("""
--- model join_video_helper_29
config output
config dirname
config pattern
config factor

|files_from_dir dir=$dirname regexp=$pattern| -->file
file --> |imread_rgb| --> rgb
rgb --> |rewrite_timestamps interval=$factor| -> retimed
retimed --> |info|
# XXX this doesn't work
#retimed -> |fix_frame_rate fps=29.97| -->  fill
#fill --> |info|
retimed -> |mencoder quiet=1 file=$output timestamps=0|
    
    """)
    factor = 1.0 / fps
    pg('join_video_helper_29', dict(dirname=dirname, pattern=pattern, output=output,
                                 factor=factor))



if __name__ == '__main__':
    main()
