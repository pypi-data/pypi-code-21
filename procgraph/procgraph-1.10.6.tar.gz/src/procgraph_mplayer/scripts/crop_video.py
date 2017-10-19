#!/usr/bin/env python
from optparse import OptionParser
from procgraph import pg, register_model_spec
import numpy as np
import os

usage = """
    %cmd  [-o <output>] <filename>
"""


def main():
    parser = OptionParser(usage=usage)

    parser.add_option("-o", dest='output', type="string",
                      help='Output video.')

    (options, args) = parser.parse_args()

    if len(args) != 1:
        msg = 'Exactly one argument necessary.'
        raise Exception(msg)

    filename = args[0]

    return video_crop(filename, options.output)


def video_crop(filename, output=None):
    if output is None:
        base, ext = os.path.splitext(filename)
        output = '%s-crop%s' % (base, ext)

    mask = get_motion_mask(filename)
    #print mask
    H, W = mask.shape
    useless_line = [np.min(mask[i, :]) for i in range(H)]
    useless_col = [np.min(mask[:, i]) for i in range(W)]

    useful_line = np.logical_not(useless_line)
    useful_col = np.logical_not(useless_col)
    #print useful_line
    #print useful_col

    crop_top = np.min(np.nonzero(useful_line)[0])
    crop_bottom = H - np.max(np.nonzero(useful_line)[0])
    crop_left = np.min(np.nonzero(useful_col)[0])
    crop_right = W - np.max(np.nonzero(useful_col)[0])

    print('Cropping left %s  right %s  top %s  bottom %s' %
          (crop_left, crop_right, crop_top, crop_bottom))

    register_model_spec("""
--- model crop_movie
config video 'video'
config output
config top = 0
config left = 0
config right = 0
config bottom = 0

|mplayer file=$video stats=1| --> rgb

rgb --> |crop left=$left top=$top bottom=$bottom right=$right| --> rgb2

rgb2 --> |mencoder quiet=1 file=$output timestamps=0|
    
    """)

    pg('crop_movie', dict(top=crop_top, bottom=crop_bottom,
                          left=crop_left, right=crop_right,
                          video=filename, output=output))

register_model_spec("""
--- model movie_stats
config video 'video'
output rgb_min
output rgb_max

|mplayer file=$video stats=1| --> rgb

rgb --> |minimum_over_time| --> |output name=rgb_min|
rgb --> |maximum_over_time| --> |output name=rgb_max|
    
    """)
def get_motion_mask(filename):

    model = pg('movie_stats', dict(video=filename))
    rgb_min = model.get_output('rgb_min')
    rgb_max = model.get_output('rgb_max')

    no_motion = np.min(rgb_min == rgb_max, axis=2)

    def percentage(x):
        return (100.0 * np.sum(x.flat) / x.size)

    print('Immobile: %.1f%% of the image.' % percentage(no_motion))

    bgcolor = rgb_min[0, 0, :]

    print('bgcolor: %s' % bgcolor)

    whiter = rgb_min[:, :, 0] == bgcolor[0]
    whiteg = rgb_min[:, :, 1] == bgcolor[1]
    whiteb = rgb_min[:, :, 2] == bgcolor[2]

    white = np.logical_and(np.logical_and(whiter, whiteg), whiteb)

    print('White: %.1f%% of the image.' % percentage(white))

    mask = np.logical_and(white, no_motion)

    print('Both: %.1f%% of the image.' % percentage(mask))

    return mask

if __name__ == '__main__':
    main()
