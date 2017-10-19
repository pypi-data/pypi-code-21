from .conversions import pg_video_info
from contracts.main import check
from procgraph import BadConfig, Block, Generator
from procgraph.block_utils import expand
from procgraph.utils import friendly_path
from procgraph_mplayer.programs_existence import check_programs_existence
import math
import numpy
import os
import subprocess
import tempfile


__all__ = ['MPlayer']

class MPlayer(Generator):
    ''' Decodes a video stream. '''

    Block.alias('mplayer')

    Block.config('file', 'Input video file. This can be in any format that '
                         '``mplayer`` understands.')
    Block.config('quiet', 'If true, suppress stderr messages from mplayer.',
                          default=True)
    Block.config('stats', 'If true, writes some statistics about the '
                          'remaining time.', default=True)

    Block.config('max_duration', 'Maximum length, in seconds, of the output.' 
                                 'Useful to get a maximum duration.', default=None)
    
    Block.output('video', 'RGB stream as numpy array.')

    TIMESTAMPS_SUFFIX = ".timestamps"


    def init(self):
        self.programs = check_programs_existence(programs=['mencoder'])

        for p in self.programs:
            self.info('Using %13s = %s' % (p, self.programs[p]))

        if not isinstance(self.config.file, str):
            raise BadConfig('This should be a string.', self, 'file')
        
        self.file = expand(self.config.file)

        if not os.path.exists(self.file):
            msg = 'File %r does not exist.' % self.file
            raise BadConfig(msg, self, 'file')

        timestamps_file = self.file + MPlayer.TIMESTAMPS_SUFFIX
        if os.path.exists(timestamps_file):
            self.info('Reading timestamps from %r.' % timestamps_file)
            self.timestamps = open(timestamps_file)
        else:
            self.timestamps = None
            #self.info('Will use fps for timestamps.')

        self.mencoder_started = False

        self.state.timestamp = None
        self.state.timestamp = self.get_next_timestamp()
        self.state.next_frame = None
        self.state.finished = False

        self.num_frames_read = 0

    def open_mencoder(self):
        self.mencoder_started = True

        info = pg_video_info(self.file, intolerant=True)

        self.width = info['width']
        self.height = info['height']
        
        self.fps = info['fps']
        self.length = info['length']
        
        
        check('float|int', self.length)
        check('float|int', self.fps)
        self.info('length: %r' % self.length)
        self.info('fps: %r' % self.fps)
        self.approx_frames = int(math.ceil(self.length * self.fps))

        # TODO: reading non-RGB streams not supported
        self.info('Reading %dx%d @ %.3f fps '
                  ' (length %ss, approx %d frames), from %s.' % 
                   (self.width, self.height, self.fps,
                    self.length, self.approx_frames,
                    friendly_path(self.config.file)))

        self.shape = (self.height, self.width, 3)
        self.dtype = 'uint8'

        pixel_format = "rgb24" 

        self.temp_dir = tempfile.mkdtemp(prefix='procgraph_fifo_dir')
        self.fifo_name = os.path.join(self.temp_dir, 'mencoder_fifo')
        os.mkfifo(self.fifo_name)
        args = [
            self.programs['mencoder'],
            self.file,
            '-ovc', 'raw',
            '-rawvideo', 'w=%d:h=%d:format=%s' %
                (self.width, self.height, pixel_format),
            '-of', 'rawvideo',
            '-vf', 'format=rgb24',
            '-nosound',
            '-o',
            self.fifo_name
        ]

        self.tmp_stdout = tempfile.TemporaryFile()
        self.tmp_stderr = tempfile.TemporaryFile()

        if self.config.quiet:
            self.process = subprocess.Popen(args,
                                    stdout=self.tmp_stdout.fileno(),
                                    stderr=self.tmp_stderr.fileno())
        else:
            self.process = subprocess.Popen(args)

        self.delta = 1.0 / self.fps
        
        if not self.timestamps:
            msg = ('No timestamps found; using delta = %.2f (%.2f fps).' 
                      % (self.delta, self.fps))
            self.info(msg)    

        self.stream = open(self.fifo_name, 'r')

        
    def get_next_timestamp(self):
        if self.timestamps:
            # If reading from files
            l = self.timestamps.readline()
            if not l:  
                # XXX warn if not even one
                self.error_once('Timestamps were too short; now using incremental.')
                if self.state.timestamp is not None:
                    return self.state.timestamp + self.delta
                else:
                    # empty file, not even one
                    self.error_once('Empty timestamp file? Starting at 0.')
                    return 0.0
            else:
                return float(l)
        else:
            if self.state.timestamp is None:
                return 0.0
            else:
                return self.state.timestamp + self.delta

    def update(self):
        if not self.mencoder_started:
            self.open_mencoder()
            self.read_next_frame()

        self.set_output(0,
                        value=self.state.next_frame,
                        timestamp=self.state.timestamp)
        self.state.timestamp = self.get_next_timestamp()

        self.state.next_frame = None
        self.read_next_frame()

        if self.config.stats:
            self.num_frames_read += 1
            if self.num_frames_read % 500 == 0:
                self.print_stats()

    def print_stats(self):
        if self.approx_frames != 0:
            percentage = 100.0 * self.num_frames_read / self.approx_frames
        else:
            percentage = 0
        # this assumes constant fps
        seconds = self.num_frames_read * self.delta
        seconds_total = self.approx_frames * self.delta
        self.info('%6d/%d frames, %.1f/%.1f sec (%4.1f%%) of %s' % 
                  (self.num_frames_read, self.approx_frames,
                   seconds, seconds_total,
                   percentage,
                   friendly_path(self.file)))

    def read_next_frame(self):
        if self.state.finished:
            return
        if self.state.next_frame is not None:
            return

        # TODO: add display of stderr after timeout

        dtype = numpy.dtype(('uint8', self.shape))
        rgbs = numpy.fromfile(self.stream, dtype=dtype, count=1)

        if len(rgbs) == 0:
            self.state.next_frame = None
            self.state.finished = True
        else:
            self.state.next_frame = rgbs[0, :].squeeze()

    def too_long_for_us(self):
        """ Returns true if max_duration is set and we passed it. """
        if self.config.max_duration is None:
            return False
        
        # We haven't started yet, so we don't have "delta"
        if not self.mencoder_started:
            return False
        
        passed = self.num_frames_read * self.delta
        
        if passed > self.config.max_duration:
            self.info_once('Finishing because passed %d frames = %f seconds > duration %f' % 
                           (self.num_frames_read, passed, self.config.max_duration))
            return True
        else:
            return False
        
    def next_data_status(self):
        # The stream has finished
        if self.state.finished:
            return (False, None)
        # We passed the limit
        elif self.too_long_for_us():
            return (False, None)
        else:
            return (True, self.state.timestamp)

    def finish(self):
        # TODO: make sure process is closed?
        if os.path.exists(self.fifo_name):
            os.unlink(self.fifo_name)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

#
# # backported from 2.7
# def check_output(*popenargs, **kwargs):
#     """
#     Run command with arguments and return its output as a byte string.
#
#     If the exit code was non-zero it raises a CalledProcessError.  The
#     CalledProcessError object will have the return code in the returncode
#     attribute and output in the output attribute.
#
#     The arguments are the same as for the Popen constructor.  Example:
#
#     >>> check_output(["ls", "-l", "/dev/null"])
#     'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'
#
#     The stdout argument is not allowed as it is used internally.
#     To capture standard error in the result, use stderr=STDOUT.
#
#     >>> check_output(["/bin/sh", "-c",
#     ...               "ls -l non_existent_file ; exit 0"],
#     ...              stderr=STDOUT)
#     'ls: non_existent_file: No such file or directory\n'
#     """
#     if 'stdout' in kwargs:
#         raise ValueError('stdout argument not allowed, it will be overridden.')
#     process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
#     output, unused_err = process.communicate()
#     retcode = process.poll()
#     if retcode:
#         cmd = kwargs.get("args")
#         if cmd is None:
#             cmd = popenargs[0]
#         raise subprocess.CalledProcessError(retcode, cmd, output=output)
#     return output
