from .conversions import pg_video_convert
from .scripts.crop_video import video_crop
from contextlib import contextmanager
from procgraph import Block
from procgraph.block_utils import (expand, make_sure_dir_exists,
    input_check_rgb_or_grayscale)
from procgraph.utils import friendly_path, indent
import numpy
import os
import signal
import subprocess
import tempfile


__all__ = ['MEncoder']


class MEncoder(Block):
    ''' 
        Encodes a video stream using ``mencoder``.
    
        Note that allowed codec and bitrate depend on 
        your version of mencoder.
        
        MP4 output: currently it works by creating a .AVI with mencoder
        and then converting to MP4 using ffmpeg.
        
        RGBA videos: not working fully. For now it outputs .AVI with 
        mencoder and encoded using png. 
        
        
    '''
    Block.alias('mencoder')

    Block.input('image', 'Either a HxWx3 uint8 numpy array representing '
                         'an RGB image, or a HxW representing grayscale. ')

    Block.config('file', 'Output file (AVI/MP4 format)')
    Block.config('fps', 'Framerate of resulting movie. If not specified, '
                        'it will be guessed from data.', default=None)
    Block.config('fps_safe', 'If the frame autodetect gives strange results, '
                             'we use this safe value instead.', default=10)

    Block.config('quiet', "If True, suppress mencoder's messages",
                 default=True)
    Block.config('timestamps', "If True, also writes <file>.timestamps that"
                               " includes a line with the timestamp for"
                               " each frame", default=True)

    Block.config('crop', "If true, the video will be "
                 "post-processed and cropped", default=False)
    
    Block.config('md', 'Metadata for the file.', default={})

    Block.config('container', 'Which container to use; '
                            'if None, it will be guessed.', default=None)
    Block.config('vcodec', 'Codec to use. If None, it will be guessed',
                 default=None)
    Block.config('vcodec_params', 'Codec-dependent params.', default={})

    Block.config('firstpass_bitrate', default=3 * 1000 * 1000)
    
    def init(self):
        self.process = None
        self.buffer = []
        self.image_shape = None  # Shape of image being encoded

        self.first_frame_timestamp = None
        
        from .programs_existence import check_programs_existence

        programs = ['mencoder', 'ffmpeg']
        self.programs = check_programs_existence(programs=programs)

        for p in self.programs:
            self.info('Using %13s = %s' % (p, self.programs[p]))

    def update(self):
        input_check_rgb_or_grayscale(self, 0)

        # Put image in a buffer -- we don't use it right away
        image = self.get_input(0)
        
        timestamp = self.get_input_timestamp(0)
        self.buffer.append((timestamp, image))

        if self.process is None:
            self.try_initialization()

        if self.process is not None:
            # initialization was succesful
            while self.buffer:
                timestamp, image = self.buffer.pop(0)
                
                if self.first_frame_timestamp is None:
                    self.first_frame_timestamp = timestamp
                    
                self.write_value(timestamp, image)

    def try_initialization(self):
        # If we don't have at least two frames, continue
        if len(self.buffer) < 2:
            return

        # Get height and width from first image
        first_image = self.buffer[0][1]

        self.shape = first_image.shape
        self.height = self.shape[0]
        self.width = self.shape[1]

        if self.height > 8192 or self.width > 8192:
            msg = 'Mencoder cannot support movies this big (%sx%s)'
            msg = msg % (self.height, self.width)
            raise Exception(msg)
        self.ndim = len(self.shape)

        # Format for mencoder's rawvideo "format" option
        if self.ndim == 2:
            format = 'y8'  # @ReservedAssignment
        else:
            if self.shape[2] == 3:
                format = 'rgb24'  # @ReservedAssignment
            elif self.shape[2] == 4:
                # Note: did not try this yet
                format = 'rgba'  # @ReservedAssignment
                msg = 'I detected that you are trying to write a transparent'
                msg += 'video. This does not work well yet (and besides,'
                msg += 'it is not supported in many applications, like '
                msg += 'Keynote). Anyway, the plan is to use mencoder '
                msg += 'to write a .AVI with codec "png". This will fail '
                msg += 'for now, but perhaps in the future it will be '
                msg += '.better'
                self.error(msg)

        # guess the fps if we are not given the config
        if self.config.fps is None:
            delta = self.buffer[-1][0] - self.buffer[0][0]

            if delta == 0:
                timestamps = [x[0] for x in self.buffer]
                self.debug('Got 0 delta: timestamps: %s' % timestamps)
                fps = 0
            else:
                fps = (len(self.buffer) - 1) / delta

            # Check for very wrong results
            if not (3 < fps < 60):
                self.error('Detected fps is %.2f; this seems strange to me,'
                           ' so I will use the safe choice fps = %.2f.' % 
                           (fps, self.config.fps_safe))
                fps = self.config.fps_safe
        else:
            fps = self.config.fps

        # adapt the bitrate to the size of the image
        vbitrate0 = self.config.firstpass_bitrate
        shape0 = (640, 480)

        n1 = self.width * self.height
        n0 = shape0[0] * shape0[1]
        vbitrate = vbitrate0 * n1 / n0
        self.info('Using bitrate %r' % vbitrate)

        self.filename = expand(self.config.file)
        if os.path.exists(self.filename):
            self.info('Removing previous version of %s.' % 
                      friendly_path(self.filename))
            os.unlink(self.filename)

        

        self.tmp_filename = '%s-active.avi' % self.filename
        
        make_sure_dir_exists(self.filename)

        self.info('Writing %dx%d %s video stream at %.3f fps to %r.' % 
                  (self.width, self.height, format, fps,
                   friendly_path(self.filename)))

        if format == 'rgba':
            ovc = ['-ovc', 'lavc', '-lavcopts', 'vcodec=png']
        else:
            ovc = ['-ovc', 'lavc', '-lavcopts',
                  'vcodec=%s:vbitrate=%d' % ('mpeg4', vbitrate)]

        out = ['-o', self.tmp_filename]
        args = [
                self.programs['mencoder'],
                '/dev/stdin',
                '-demuxer', 'rawvideo',
                '-rawvideo', 'w=%d:h=%d:fps=%f:format=%s' % 
                (self.width, self.height, fps, format)
        ] + ovc + out

                # '-v', "0", # verbosity level (1 prints stats \r)

        # self.debug('$ %s' % " ".join(args))
        # Note: mp4 encoding is currently broken in mencoder :-(
        #       so we have to use ffmpeg as a second step.
        # These would be the options to add:
        # '-of', 'lavf', '-lavfopts', 'format=mp4'

        self.tmp_stdout = tempfile.TemporaryFile()
        self.tmp_stderr = tempfile.TemporaryFile()

        quiet = self.config.quiet
        if quiet:
            # XXX /dev/null not portable
#            self.debug('stderr: %s' % self.tmp_stderr)
#            self.debug('stdout: %s' % self.tmp_stdout)
            # TODO: write error
            self.process = subprocess.Popen(args,
                                            preexec_fn=ignore_sigint,
                stdin=subprocess.PIPE, stdout=self.tmp_stdout.fileno(),
                                       stderr=self.tmp_stderr.fileno())
        else:
            self.process = subprocess.Popen(args=args,
                                            stdin=subprocess.PIPE)

        if self.config.timestamps:
            self.timestamps_filename = self.filename + '.timestamps'
            self.timestamps_file = open(self.timestamps_filename, 'w')

    def _get_metadata(self):
        """ Returns the user-given metadata as well as some extra created by us. """
        metadata = self.config.md
        # metadata['author'] = 'procgraph'
        # metadata['show'] = 'procgraph'
        # metadata['title'] = 'A video by me.'
        # metadata['comment'] = 'Another video by me.'
        return metadata

    def finish(self):
        if self.process is None:
            msg = 'Finish() before starting to encode.'
            self.error(msg)
            raise Exception(msg)
            return
        
        timestamp = self.first_frame_timestamp 
        metadata = self._get_metadata()
        container = self.config.container
        vcodec = self.config.vcodec
        vcodec_params = self.config.vcodec_params
        
        self.info('Transcoding %s' % friendly_path(self.filename))
        pg_video_convert(self.tmp_filename,
                         self.filename,
                         container=container,
                         vcodec=vcodec,
                         vcodec_params=vcodec_params,
                         timestamp=timestamp,
                         metadata=metadata)

#         if False:  # XXX
        if os.path.exists(self.tmp_filename):
            os.unlink(self.tmp_filename)

        if True:
            T = self.first_frame_timestamp
            os.utime(self.filename, (T, T))

        self.info('Finished %s' % friendly_path(self.filename))

        # TODO: skip mp4
        if self.config.crop:
            base, ext = os.path.splitext(self.filename)
            cropped = '%s-crop%s' % (base, ext)
            video_crop(self.filename, cropped)
            os.rename(cropped, self.filename)

    def cleanup(self):
        # TODO: remove timestamps
#         if 'timestamps_filename' in self.__dict__:
#             if os.path.exists(self.timestamps_filename):
#                 os.unlink(self.timestamps_filename)

        if 'tmp_filename' in self.__dict__:
#             if False:  # XXX
            if os.path.exists(self.tmp_filename):
                os.unlink(self.tmp_filename)


        self.cleanup_mencoder()

    def cleanup_mencoder(self):
        # Try to cleanup as well as possible
        if (not 'process' in self.__dict__) or self.process is None:
            return

        self.process.stdin.close()

        try:
            if False:
                with timeout(5):
                    self.process.terminate()
                    self.process.wait()
            else:
                self.process.terminate()
                self.process.wait()
        except Timeout as e:
            self.error(e)
        except (OSError, AttributeError):
            # Exception AttributeError: AttributeError("'NoneType' object 
            # has no attribute 'SIGTERM'",) 
            # in <bound method RangefinderUniform.__del__ 
            # of RangefinderUniform> ignored
            # http://stackoverflow.com/questions/2572172/
            pass
#            self.error('Error while cleanup: %s' % e)

    def write_value(self, timestamp, image):
        if self.image_shape is None:
            self.image_shape = image.shape

        if self.image_shape != image.shape:
            msg = ('The image has changed shape, from %s to %s.' % 
                   (self.image_shape, image.shape))
            raise Exception(msg)  # TODO: badinput

        # very important! make sure we are using a reasonable array
        if not image.flags['C_CONTIGUOUS']:
            image = numpy.ascontiguousarray(image)  # @UndefinedVariable

        try:
            if False:
                with timeout(5):
                    self.process.stdin.write(image.data)
                    self.process.stdin.flush()
            else:
                self.process.stdin.write(image.data)
                self.process.stdin.flush()
        except (Exception, KeyboardInterrupt) as e:
        # IOError = broken pipe
            msg = 'Could not write data to mencoder: %s.' % e
#            self.error(msg)
#            msg += '\n' + indent(self.process.stdout.read(), 'stdout> ')
#            msg += '\n' + indent(self.process.stderr.read(), 'stderr> ')

            def read_all(f):
                os.lseek(f.fileno(), 0, 0)
                return f.read()

            stderr = read_all(self.tmp_stderr)
            stdout = read_all(self.tmp_stdout)

            msg += indent('stdout>', stderr)
            msg += indent('stderr>', stdout)

            raise Exception(msg)

        if self.config.timestamps:
            self.timestamps_file.write('%.4f\n' % timestamp)
            self.timestamps_file.flush()


class Timeout(Exception):
    pass


@contextmanager
def timeout(delta=5):

    def handler(signum, frame):
        raise Timeout("operation took more than %s seconds" % delta)

    # Set the signal handler and a 5-second alarm
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(delta)
    try:
        yield
    finally:
        signal.alarm(0)


def ignore_sigint():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
