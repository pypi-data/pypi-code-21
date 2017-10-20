# -*- coding: utf-8 -*-
"""
On the long term this will implement several methods to make videos
out of VideoClips
"""

import subprocess as sp
import os
import numpy as np
import platform

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

FFMPEG_BINARY = None
if platform.system() == 'Windows':
    FFMPEG_BINARY = "ffmpeg.exe"
elif platform.system() == 'Linux':
    FFMPEG_BINARY = "ffmpeg"
else:
    raise OSError

class FFMPEG_VideoWriter:
    """ A class for FFMPEG-based video writing.
    A class to write videos using ffmpeg. ffmpeg will write in a large
    choice of formats.
    Parameters
    -----------
    filename
      Any filename like 'video.mp4' etc. but if you want to avoid
      complications it is recommended to use the generic extension
      '.avi' for all your videos.
    size
      Size (width,height) of the output video in pixels.
    fps
      Frames per second in the output video file.
    codec
      FFMPEG codec. It seems that in terms of quality the hierarchy is
      'rawvideo' = 'png' > 'mpeg4' > 'libx264'
      'png' manages the same lossless quality as 'rawvideo' but yields
      smaller files. Type ``ffmpeg -codecs`` in a terminal to get a list
      of accepted codecs.
      Note for default 'libx264': by default the pixel format yuv420p
      is used. If the video dimensions are not both even (e.g. 720x405)
      another pixel format is used, and this can cause problem in some
      video readers.
    audiofile
      Optional: The name of an audio file that will be incorporated
      to the video.
    preset
      Sets the time that FFMPEG will take to compress the video. The slower,
      the better the compression rate. Possibilities are: ultrafast,superfast,
      veryfast, faster, fast, medium (default), slow, slower, veryslow,
      placebo.
    bitrate
      Only relevant for codecs which accept a bitrate. "5000k" offers
      nice results in general.
    withmask
      Boolean. Set to ``True`` if there is a mask in the video to be
      encoded.
    """

    def __init__(self, filename, size, fps, codec="mpeg4", audiofile=None,
                 preset="placebo", bitrate="5000k", withmask=False,
                 logfile=None, threads=None, ffmpeg_params=None):

        if logfile is None:
            logfile = sp.PIPE

        self.filename = filename
        self.codec = codec
        self.ext = self.filename.split(".")[-1]

        # order is important
        cmd = [
            FFMPEG_BINARY,
            '-y',
            '-loglevel', 'error' if logfile == sp.PIPE else 'info',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', '%dx%d' % (size[0], size[1]),
            '-pix_fmt', 'rgba' if withmask else 'rgb24',
            '-r', '%.02f' % fps,
            '-i', '-', '-an',
        ]
        if audiofile is not None:
            cmd.extend([
                '-i', audiofile,
                '-acodec', 'copy'
            ])
        cmd.extend([
            '-vcodec', codec,
            '-preset', preset,
        ])
        if ffmpeg_params is not None:
            cmd.extend(ffmpeg_params)
        if bitrate is not None:
            cmd.extend([
                '-b', bitrate
            ])

        if threads is not None:
            cmd.extend(["-threads", str(threads)])

        if ((codec == 'libx264') and
                (size[0] % 2 == 0) and
                (size[1] % 2 == 0)):
            cmd.extend([
                '-pix_fmt', 'yuv420p'
            ])
        cmd.extend([
            filename
        ])

        popen_params = {"stdout": DEVNULL,
                        "stderr": logfile,
                        "stdin": sp.PIPE}

        # This was added so that no extra unwanted window opens on windows
        # when the child process is created
        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000

        self.proc = sp.Popen(cmd, **popen_params)


    def write_frame(self, img_array):
        """ Writes one frame in the file."""
        try:
            self.proc.stdin.write(img_array.tostring())
        except IOError as err:
            ffmpeg_error = self.proc.stderr.read()
            error = (str(err) + ("\n\nMoviePy error: FFMPEG encountered "
                                 "the following error while writing file %s:"
                                 "\n\n %s" % (self.filename, ffmpeg_error)))

            if "Unknown encoder" in ffmpeg_error:

                error = error+("\n\nThe video export "
                  "failed because FFMPEG didn't find the specified "
                  "codec for video encoding (%s). Please install "
                  "this codec or change the codec when calling "
                  "write_videofile. For instance:\n"
                  "  >>> clip.write_videofile('myvid.webm', codec='libvpx')")%(self.codec)

            elif "incorrect codec parameters ?" in ffmpeg_error:

                 error = error+("\n\nThe video export "
                  "failed, possibly because the codec specified for "
                  "the video (%s) is not compatible with the given "
                  "extension (%s). Please specify a valid 'codec' "
                  "argument in write_videofile. This would be 'libx264' "
                  "or 'mpeg4' for mp4, 'libtheora' for ogv, 'libvpx for webm. "
                  "Another possible reason is that the audio codec was not "
                  "compatible with the video codec. For instance the video "
                  "extensions 'ogv' and 'webm' only allow 'libvorbis' (default) as a"
                  "video codec."
                  )%(self.codec, self.ext)

            elif  "encoder setup failed" in ffmpeg_error:

                error = error+("\n\nThe video export "
                  "failed, possibly because the bitrate you specified "
                  "was too high or too low for the video codec.")

            elif "Invalid encoder type" in ffmpeg_error:

                error = error + ("\n\nThe video export failed because the codec "
                  "or file extension you provided is not a video")


            raise IOError(error)

    def close(self):
        self.proc.stdin.close()
        if self.proc.stderr is not None:
            self.proc.stderr.close()
        self.proc.wait()

        del self.proc

