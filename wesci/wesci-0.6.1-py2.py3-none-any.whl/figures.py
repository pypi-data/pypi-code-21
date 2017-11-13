import os
from wesci.timer import Timer
from wesci.hash import Hash
import tempfile
from matplotlib.pyplot import gcf
from PIL import Image


class Figures(object):
    FIGURE_FORMAT = 'png'
    SIZE_PIXELS = 512, 512

    @staticmethod
    def add_output_figure(thumbnail_dir, fig):
        with Timer() as timer:
            fighash = Figures.__process_figure(thumbnail_dir, fig)
        return {'hash': fighash, 'timing': timer.duration_ms()}

    @staticmethod
    def __process_figure(thumbnail_dir, fig):
        if fig is None:
            fig = gcf()
        try:
            tmp, temp_filename = tempfile.mkstemp(suffix='.png')
            os.close(tmp)  # os may prohibit saving to an already open file
            fig.savefig(temp_filename)
            fighash = Figures.__figure_hash(temp_filename)
            Figures.__store_figure_thumbnail(temp_filename, thumbnail_dir,
                                             fighash)
        finally:
            os.remove(temp_filename)
        return fighash

    @staticmethod
    def __figure_hash(filename):
        with open(filename, 'rb') as f:
            file_data = f.read()
        return Hash.hash(file_data)

    @staticmethod
    def __save_figure_thumbnail(origin, thumbnail_dir, filename):
        fig = Image.open(origin)
        fig.thumbnail(Figures.SIZE_PIXELS)
        fig.save('%s/%s.%s' % (thumbnail_dir, filename, Figures.FIGURE_FORMAT))

    @staticmethod
    def __store_figure_thumbnail(origin, thumbnail_dir, filename):
        if not os.path.exists(thumbnail_dir):
            os.makedirs(thumbnail_dir)
        Figures.__save_figure_thumbnail(origin, thumbnail_dir, filename)
