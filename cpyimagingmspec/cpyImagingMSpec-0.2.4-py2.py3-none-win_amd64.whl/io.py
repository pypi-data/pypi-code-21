# -*- encoding: utf-8 -*-
import numpy as np
import pandas as pd

import cpyImagingMSpec.utils as utils
_ffi = utils.init_ffi()
_ims = utils.load_shared_lib()

class ImzbReader(object):
    """
    Class for reading .imzb file format, which is optimized for very fast m/z-image queries.

    WARNING: the format is not going to be supported in the future!
    Most likely, it will be eventually superceded by Parquet format.

    ImzML files can be converted to it using 'ims convert' tool which
    can either be compiled from source (https://github.com/alexandrovteam/ims-cpp)
    or installed with conda ("conda install -c lomereiter ims-cpp").
    """
    def __init__(self, filename):
        """
        Open .imzb file for reading
        """
        self._filename = filename
        r = _ims.imzb_reader_new(filename.encode('utf-8'))
        utils.raise_ims_exception_if_null(r)
        self._reader = _ffi.gc(r, _ims.imzb_reader_free)

    @property
    def height(self):
        """
        Image height
        """
        return _ims.imzb_reader_height(self._reader)

    @property
    def width(self):
        """
        Image width
        """
        return _ims.imzb_reader_width(self._reader)

    @property
    def min_mz(self):
        """
        Minimal m/z value
        """
        return _ims.imzb_reader_min_mz(self._reader)

    @property
    def max_mz(self):
        """
        Maximal m/z value
        """
        return _ims.imzb_reader_max_mz(self._reader)

    def get_mz_image(self, mz, ppm):
        """
        Read m/z-image formed from peaks within mz × (1 ± 10 :sup:`-6` × ppm) window.

        Pixels that were not scanned have intensity set to -1.
        """
        data = utils.cffi_buffer(self.height * self.width, 'f')
        read_func = _ims.imzb_reader_image
        ret = read_func(self._reader, _ffi.cast("double", mz), _ffi.cast("double", ppm),
                        data.ptr)
        if ret < 0:
            utils.raise_ims_exception()
        return data.buf.reshape((self.height, self.width))

    def peaks(self, min_mz, max_mz):
        """
        Returns peaks between min_mz and min_mz formatted as a Pandas dataframe
        with columns mz, intensity, x, y, z.
        """
        peaks_ptr = _ffi.new("Peak**", _ffi.NULL)
        n = _ims.imzb_reader_slice(self._reader,
                                   _ffi.cast("double", min_mz), _ffi.cast("double", max_mz),
                                   peaks_ptr)
        alignment = _ffi.alignof('Peak')
        if alignment == 8:
            dtype = [('x', 'u4'), ('y', 'u4'), ('z', 'u4'), ('_', 'u4'),
                     ('mz', 'f8'), ('intensity', 'f4'), ('__', 'f4')]
        else:
            dtype = [('x', 'u4'), ('y', 'u4'), ('z', 'u4'),
                     ('mz', 'f8'), ('intensity', 'f4')]
        arr = np.frombuffer(_ffi.buffer(peaks_ptr[0], n * _ffi.sizeof('Peak')), dtype, n)
        df = pd.DataFrame(arr)
        if alignment == 8:
            del df['_'], df['__']
        _ims.free(peaks_ptr[0])
        return df

    def dbscan(self, minPts=None, eps=lambda mz: 1e-6 * mz, min_mz=None, max_mz=None):
        """
        Runs DBSCAN algorithm on the set of all m/z values encountered in the file.
        Meaningful only for centroided data.
        If minPts is not provided, it is set as 2% of the number of spectra.
        The range can be set through min_mz and max_mz parameters.

        Returns m/z bins formatted as a Pandas dataframe with the following columns:

        * left, right - bin boundaries;
        * count - number of peaks in the bin;
        * mean - average m/z;
        * sd - standard deviation of m/z;
        * intensity - total intensity.
        """
        bins_ptr = _ffi.new("MzBin**", _ffi.NULL)
        if minPts is None:
            minPts = int(self.width * self.height * 0.02)  # FIXME don't assume rectangular
        if (min_mz is None) and (max_mz is None):
            n = _ims.imzb_reader_dbscan3(self._reader,
                                         _ffi.cast("int", minPts),
                                         _ffi.callback("double(*)(double)", eps),
                                         bins_ptr)
        elif (min_mz is None) and (max_mz is not None):
            min_mz = self.min_mz
        elif (min_mz is not None) and (max_mz is None):
            max_mz = self.max_mz + 1

        if min_mz is not None:
            n = _ims.imzb_reader_dbscan4(self._reader,
                                         _ffi.cast("int", minPts),
                                         _ffi.callback("double(*)(double)", eps),
                                         _ffi.cast("double", min_mz), _ffi.cast("double", max_mz),
                                         bins_ptr)
        assert _ffi.sizeof('MzBin') == 8 * 8
        dtype = [('left', 'f8'), ('right', 'f8'), ('count', 'u8'), ('_', 'u8'),
                 ('intensity', 'f8'), ('median', 'f8'),
                 ('mean', 'f8'), ('sd', 'f8')]
        arr = np.frombuffer(_ffi.buffer(bins_ptr[0], n * _ffi.sizeof('MzBin')), dtype, n)
        df = pd.DataFrame(arr)
        del df['_']
        _ims.free(bins_ptr[0])
        return df
