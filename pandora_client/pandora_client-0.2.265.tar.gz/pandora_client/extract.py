#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# GPL 2017
from __future__ import division, print_function, absolute_import

from glob import glob
import os
import shutil
import subprocess
import sys

import ox

from .utils import AspectRatio, run_command, basedir

FFMPEG_SUPPORTS_VP9 = False

def command(program):
    local = os.path.join(basedir(), 'bin', program)
    if sys.platform.startswith('win'):
        local += '.exe'
    if os.path.exists(local):
        program = local
    return program

def frame(video, target, position):
    fdir = os.path.dirname(target)
    if fdir and not os.path.exists(fdir):
        os.makedirs(fdir)

    # ffmpeg
    pre = position - 2
    if pre < 0:
        pre = 0
    else:
        position = 2
    cmd = [command('ffmpeg'), '-y', '-ss', str(pre), '-i', video, '-ss', str(position),
           '-vf', 'scale=iw*sar:ih',
           '-an', '-vframes', '1', target]
    r = run_command(cmd)
    return r == 0

def supported_formats():
    ffmpeg = command('ffmpeg')
    if ffmpeg is None:
        return None
    p = subprocess.Popen([ffmpeg, '-codecs'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    stdout, stderr = p.communicate()
    stdout = stdout.decode('utf-8')
    return {
        'ogg': 'libtheora' in stdout and 'libvorbis' in stdout,
        'webm': 'libvpx' in stdout and 'libvorbis' in stdout,
        'vp8': 'libvpx' in stdout and 'libvorbis' in stdout,
        'vp9': 'libvpx-vp9' in stdout and 'libopus' in stdout,
        'mp4': 'libx264' in stdout and 'DEA.L. aac' in stdout,
        'h264': 'libx264' in stdout and 'DEA.L. aac' in stdout,
    }

def video_cmd(video, target, profile, info):

    if not os.path.exists(target):
        ox.makedirs(os.path.dirname(target))

    '''
        look into
            lag
            mb_static_threshold
            qmax/qmin
            rc_buf_aggressivity=0.95
            token_partitions=4
            level / speedlevel
            bt?
    '''
    support = supported_formats()

    profile, format = profile.split('.')
    bpp = 0.17
    video_codec = 'libvpx'
    audio_codec = 'libvorbis'

    if profile == '1080p':
        height = 1080

        audiorate = 48000
        audioquality = 6
        audiobitrate = None
        audiochannels = None
    elif profile == '720p':
        height = 720

        audiorate = 48000
        audioquality = 5
        audiobitrate = None
        audiochannels = None
    elif profile == '480p':
        height = 480

        audiorate = 44100
        audioquality = 3
        audiobitrate = None
        audiochannels = 2
    elif profile == '432p':
        height = 432
        audiorate = 44100
        audioquality = 2
        audiobitrate = None
        audiochannels = 2
    elif profile == '360p':
        height = 360

        audiorate = 44100
        audioquality = 1
        audiobitrate = None
        audiochannels = 1
    elif profile == '288p':
        height = 288

        audiorate = 44100
        audioquality = 0
        audiobitrate = None
        audiochannels = 1
    elif profile == '240p':
        height = 240

        audiorate = 44100
        audioquality = 0
        audiobitrate = None
        audiochannels = 1
    elif profile == '144p':
        height = 144

        audiorate = 22050
        audioquality = -1
        audiobitrate = '22k'
        audiochannels = 1
    else:
        height = 96

        #if support['vp9']:
        #    audio_codec = 'libopus'
        #    video_codec = 'libvpx-vp9'

        audiorate = 22050
        audioquality = -1
        audiobitrate = '22k'
        audiochannels = 1

    if format == 'webm' and audio_codec == 'libopus':
        audiorate = 48000
        if not audiobitrate:
            audiobitrate = '%sk' % {
                -1: 32,  0: 48,  1: 64,  2: 96,  3: 112,  4: 128,
                 5: 144, 6: 160, 7: 192, 8: 256, 9: 320, 10: 512,
            }[audioquality]
    if format == 'webm' and video_codec == 'libvpx-vp9':
        bpp = 0.15

    if info['video'] and 'display_aspect_ratio' in info['video'][0]:
        # dont make video bigger
        height = min(height, info['video'][0]['height'])

        dar = AspectRatio(info['video'][0]['display_aspect_ratio'])
        width = int(dar * height)
        width += width % 2

        aspect = dar.ratio
        # use 1:1 pixel aspect ratio if dar is close to that
        if abs(width/height - dar) < 0.02:
            aspect = '%s:%s' % (width, height)

        if info['video'][0]['framerate'] == '0:0':
            fps = 25
        else:
            fps = AspectRatio(info['video'][0]['framerate'])

        extra = []
        if fps == 50:
            fps = 25
            extra += ['-r', '25']
        if fps == 60:
            fps = 30
            extra += ['-r', '30']
        fps = min(float(fps), 30)

        bitrate = height*width*fps*bpp/1000

        video_settings = [
            '-vb', '%dk' % bitrate,
            '-aspect', aspect,
            '-g', '%d' % int(fps*5),
            '-vf', 'yadif,hqdn3d,scale=%s:%s' % (width, height),
        ] + extra
        if format == 'webm':
            video_settings += [
                '-vcodec', video_codec,
                '-quality', 'good',
                '-cpu-used', '1' if video_codec == 'libvpx-vp9' else '0',
                '-lag-in-frames', '16',
                '-auto-alt-ref', '1',
            ]
            if video_codec == 'libvpx-vp9':
                video_settings += [
                    '-tile-columns', '6',
                    '-frame-parallel', '1',
                ]
        if format == 'mp4':
            video_settings += [
                '-c:v', 'libx264',
                '-preset:v', 'medium',
                '-profile:v', 'high',
                '-level', '4.0',
            ]
        video_settings += ['-map', '0:%s,0:0' % info['video'][0]['id']]
        audio_only = False
    else:
        video_settings = ['-vn']
        audio_only = True

    # ignore some unsupported audio codecs
    if info['audio'] and info['audio'][0].get('codec') in ('qdmc', ):
        audio_settings = ['-an']
    elif info['audio']:
        if video_settings == ['-vn'] or not info['video']:
            n = 0
        else:
            n = 1
        audio_settings = []
        # mix 2 mono channels into stereo(common for fcp dv mov files)
        audio_track = 0
        if audio_track == 0 and len(info['audio']) == 2 \
                and len(list(filter(None, [a['channels'] == 1 or None for a in info['audio']]))) == 2:
            audio_settings += [
                '-filter_complex',
                '[0:%s][0:%s] amerge' % (info['audio'][0]['id'], info['audio'][1]['id'])
            ]
            mono_mix = True
        else:
            mono_mix = False
            audio_settings += ['-map', '0:%s,0:%s' % (info['audio'][audio_track]['id'], n)]
        audio_settings += ['-ar', str(audiorate)]
        if audio_codec != 'libopus':
            audio_settings += ['-aq', str(audioquality)]
        if mono_mix:
            ac = 2
        else:
            ac = info['audio'][0].get('channels')
            if not ac:
                ac = audiochannels
        if audiochannels:
            ac = min(ac, audiochannels)
            audio_settings += ['-ac', str(ac)]
        if audiobitrate:
            audio_settings += ['-ab', audiobitrate]
        if format == 'mp4':
            audio_settings += ['-c:a', 'aac', '-strict', '-2']
        elif audio_codec == 'libopus':
            audio_settings += ['-c:a', 'libopus', '-frame_duration', '60']
        else:
            audio_settings += ['-c:a', audio_codec]
    else:
        audio_settings = ['-an']

    base = [command('ffmpeg'),
            #'-nostats', '-loglevel', 'error',
            '-y', '-i', video, '-threads', '4', '-map_metadata', '-1', '-sn']

    if format == 'webm':
        post = ['-f', 'webm', target]
    elif format == 'mp4':
        post = ['-movflags', '+faststart', '-f', 'mp4', target]
    else:
        post = [target]

    cmds = []
    if video_settings != ['-vn']:
        pass1_post = post[:]
        pass1_post[-1] = '/dev/null'
        if format == 'webm':
            pass1_post = ['-speed', '4'] + pass1_post
            post = ['-speed', '1'] + post
        cmds.append(base + ['-an', '-pass', '1', '-passlogfile', '%s.log' % target]
                         + video_settings + pass1_post)
        cmds.append(base + ['-pass', '2', '-passlogfile', '%s.log' % target]
                         + audio_settings + video_settings + post)
    else:
        cmds.append(base + audio_settings + video_settings + post)

    if not support.get(format):
        if format == 'webm':
            print("ffmpeg is compiled without WebM support")
        elif format == 'mp4':
            print("ffmpeg is compiled without H.264 support")
        else:
            print('trying to encode in an unsupported format')
        sys.exit(1)
    return cmds

def video(video, target, profile, info):
    enc_target = target + 'tmp.mp4' if target.endswith('.mp4') else target + '.tmp.webm'
    cmds = video_cmd(video, enc_target, profile, info)
    profile, format = profile.split('.')
    for cmd in cmds:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             close_fds=True)
        try:
            p.wait()
            r = p.returncode
            print('Input:\t', video)
            print('Output:\t', target)
        except KeyboardInterrupt:
            p.kill()
            r = 1
            if os.path.exists(enc_target):
                print("\n\ncleanup unfinished encoding:\nremoving", enc_target)
                print("\n")
                os.unlink(enc_target)
            if os.path.exists(target):
                print("\n\ncleanup unfinished encoding:\nremoving", target)
                print("\n")
                os.unlink(target)
            if format == 'mp4' and os.path.exists("%s.mp4" % target):
                os.unlink("%s.mp4" % target)
            sys.exit(1)
        if p.returncode != 0:
            if os.path.exists(enc_target):
                os.unlink(enc_target)
            if os.path.exists(target):
                os.unlink(target)
            for f in glob('%s.log*' % enc_target):
                os.unlink(f)
            return False
        else:
            r = 0
    if r == 0 and enc_target != target:
        shutil.move(enc_target, target)
    for f in glob('%s.log*' % enc_target):
        os.unlink(f)
    return r == 0
