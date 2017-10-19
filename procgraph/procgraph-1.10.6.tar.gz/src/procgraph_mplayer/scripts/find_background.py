#!/usr/bin/env python
from contracts import contract
from itertools import product
from optparse import OptionParser
from procgraph_images import TransparentImageAverage
from procgraph_pil import imread, imwrite
from reprep import scale
import numpy as np
import os
from procgraph.utils.calling_ext_program import system_cmd_result
from procgraph.utils.friendly_paths import friendly_path



usage = """
    %cmd  [-o <output>] <filename>
"""

def main():
    parser = OptionParser(usage=usage)

    parser.add_option("-i", "--input", dest='video', type="string", help='Input video.')
    parser.add_option("-o", "--output", dest='background', type="string", help='Output png.')
    parser.add_option("-f", "--frames", dest='frames', type="string", default='1.0,2,3.4',
                      help='Frames to use; floats separated by comma.')

    (options, args) = parser.parse_args()

    if args:
        msg = 'No argument necessary.'
        raise Exception(msg)

    video = options.video
    background = options.background
    frames = map(float, options.frames.split(','))

    result = find_background(video, frames, debug=True)
    imwrite(result['background'], background)
    return 0


def get_frame(video, when):
    # out = join(tmp_path, 'frame%s.png' % when)
    out = os.path.basename(video) + '.tmp_frame%f.png' % when
    cmd = ("ffmpeg -ss %s -i %s -y -f image2 -vframes 1 %s" % (when, video, out))    
    system_cmd_result(cwd='.', cmd=cmd,
                      display_stdout=False,
                      display_stderr=False,
                      raise_on_error=True,
                      capture_keyboard_interrupt=False)  # @UnusedVariable
    
    frame = imread(out)
    os.unlink(out)
    return frame
        
from os.path import dirname, exists, basename, splitext, join

@contract(whens='list[>=3](float)')
def find_background(video, whens, debug=False, tmp_path=None):
    if not os.path.exists(video):
        msg = 'Filename does not exist: %s' % friendly_path(video) 
        raise ValueError(msg)
    id_video = splitext(basename(video))[0]
    
    if tmp_path is None:
        tmp_path = join(dirname(video), 'find_background-%s' % id_video)
    if not exists(tmp_path):
        os.makedirs(tmp_path)
    
    @contract(rgb='array[HxWx3](uint8)')
    def write_debug(rgb, id_image):
        if debug:
            f = join(tmp_path, '%s.png' % id_image)
            # print('Writing %s' % f)
            imwrite(rgb, f)
    
    frames = []
    for i, when in enumerate(whens):
        frame = get_frame(video, when)
        write_debug(frame, 'frame-%s-t%4.2f' % (i, when))
        frames.append(frame.astype('float32'))

    n = len(frames)

    errs = {}
    for i, j in product(range(n), range(n)):
        if i == j: 
            continue

        diff = np.abs(frames[i] - frames[j])
        errs[(i, j)] = np.mean(diff, axis=2)

        write_debug(scale(errs[(i, j)]), 'errs-%s-%s' % (i, j))

    
    mm = np.dstack(tuple(errs.values()))
    s = np.mean(mm, axis=2)
    write_debug(scale(s), 's')

    # print('computing moving stuff')
    moving = []
    bgshade = []
    for i in range(n):
        its = np.dstack([errs[(i, j)] for j in range(n) if i != j])
        moving_i = np.min(its, axis=2)
        moving.append(moving_i)

        bgshade_i = assemble_transp(frames[i], 1.0 / (moving_i + 10))
        bgshade.append(bgshade_i)

        write_debug(scale(moving_i), 'moving-%d' % i)
        write_debug(bgshade_i, 'bgshade-%d' % i)
        


    avg = TransparentImageAverage()
    for i in range(n):
        avg.update(bgshade[i])
    bg_rgb = avg.get_rgb()

    write_debug(bg_rgb, 'background')
    
    return {'background': bg_rgb}

@contract(rgb='array[HxWx3]', alpha='array[HxW]', returns='array[HxWx4](uint8)')
def assemble_transp(rgb, alpha):
    H, W = rgb.shape[0], rgb.shape[1]
    rgba = np.zeros((H, W, 4), dtype='uint8')
    rgba[:, :, 0:3] = rgb[:, :, 0:3]
    # print('alpha range %f - %f' % (np.min(alpha), np.max(alpha)))
    alpha = alpha - np.min(alpha)
    alpha = alpha / np.max(alpha)
    alpha = alpha * 255
    rgba[:, :, 3] = alpha[:, :]
    return rgba


if __name__ == '__main__':
    main()
