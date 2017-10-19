from procgraph import Generator, Block, BadConfig
from procgraph.block_utils import expand
import os
import re

__all__ = ['FilesFromDir']

class FilesFromDir(Generator):
    ''' 
        This block reads the filenames from a directory according
        to a given regexp. 
        
        For now the timestamp starts from 0 and it is fixed.
    '''
    Block.alias('files_from_dir')
    Block.config('dir', 'Directory containing the image files.')
    Block.config('regexp', 'Regular expression for images.',
#                  default='(\w+)(\d+)\.(\w+)')
                default='.+\.(png|jpg)')
    Block.config('fps', 'Fixed frame per second.', default=20.0)
    Block.output('filename', 'Image filename')

    def init(self):
        dirname = self.config.dir
        dirname = expand(dirname)

        if not os.path.exists(dirname):
            raise BadConfig('Not existent directory %r.' % dirname, self,
                            'dir')

        if not os.path.isdir(dirname):
            raise BadConfig('The file %r is not a directory.' % dirname, self,
                            'dir')

        regexp = self.config.regexp

        # TODO: use proper logging
        self.info("Reading %r from %r." % (regexp, dirname))
        all_files = os.listdir(dirname)

        selected = [os.path.join(dirname, f)
                    for f in all_files
                    if re.match(regexp, f)]

        def natural_key(string):
            """See http://www.codinghorror.com/blog/archives/001018.html"""
            return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string)]

        selected.sort(key=lambda x: natural_key(os.path.basename(x)))

        self.info("Selected %d/%d files." % (len(selected), len(all_files)))

        fps = float(self.config.fps)
        if fps <= 0:
            raise BadConfig(self, "Invalid fps value %s." % fps, 'fps')
        # tuples (timestamp, filename)
        frames = [(i / fps, f)
                    for i, f in enumerate(selected)]

        if not frames:
            raise Exception('No frames found in dir %r.' % dirname)

        self.state.frames = frames
        self.state.next_frame = 0

    def next_data_status(self):
        k = self.state.next_frame
        if k is None:
            return (False, None)
        else:
            frames = self.state.frames
            timestamp = frames[k][0]
            return (True, timestamp)

    def update(self):
        frames = self.state.frames
        k = self.state.next_frame

        assert k < len(frames)

        timestamp, filename = frames[k]

        self.set_output(0, value=filename, timestamp=timestamp)

        if k + 1 >= len(frames):
            self.state.next_frame = None
        else:
            self.state.next_frame = k + 1

