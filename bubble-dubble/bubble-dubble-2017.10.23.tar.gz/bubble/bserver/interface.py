#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import threading
import decor
from integracio import igracio
from ..bcommon import compressor


class _Interface:
    type = 'None'
    calcTransmission = False

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.i = igracio.IGracio()
        self._precision = self.i.precision
        self._lock = threading.RLock()
        self._counter = 0
        self._maskFile = None
        self._pickle = False
        self._floodFile = None
        self._splineFile = None
        self._backgroundFiles = []
        self._darkSampleFiles = []
        self._darkBackgroundFiles = []
        self._beamline = 'Dubble'
        self._concentration = 0
        self._calibration = 1
        self._units = 'q'
        self._ext = ''
        self._thickness = 1
        self._subdir = ''
        self._detector = 'Pilatus'
        self._save = False
        self._azimuth = None
        self._radial = None
        self._bkgCoef = 0
        self._speed = True
        self._sspeed = False
        self._poni = ''
        self._azimuth_checked = False
        self._azimuth_slices = False
        self._incidence = False
        self._normalization = 'Monitor'
        self._normrange = 0, 0
        self._threads = 0
        self._polarization = -2
        self._halina = False
        self._solidangle = True
        self._bins = 0
        self.wavelength = 1
        self.normalize = decor.Normalization()
        self.mask = decor.Mask()
        self.background = decor.Background()
        self.darksample = decor.DarkCurrent()
        self.darkbackground = decor.DarkCurrent()
        self.flatfield = decor.FloodField()
        self.distortion = decor.Distortion()

    def init(self):
        self.i.poni = self.poni
        self.i.units = self.units
        self.i.radial = self.radial
        self.i.polarization = self.polarization
        self.i.sa = self.solidangle
        self.i.bins = self.bins
        self.normalize.beamline = self.beamline
        self.normalize.type = self.normalization
        self.normalize.range = self.normrange
        self.wavelength = self.i.poni.wavelength / 10  # nm
        if self.detector == 'Frelon':
            ds = self.darkSample
            db = self.darkBackground
            flood = self.flood
            spline = self.spline
        else:
            ds = db = flood = spline = None
        self.darksample.init(ds)
        self.darkbackground.init(db)
        self.flatfield.init(flood)
        self.distortion.init(spline)
        self.mask.init(self.maskFile, self.beamline, self.type)
        self.background.init(self.backgroundFiles, self.darkbackground, self.normalize, self.bkgCoef, self.flatfield)

    @property
    def backgroundFiles(self):
        return self._backgroundFiles

    @backgroundFiles.setter
    def backgroundFiles(self, bkg):
        self._backgroundFiles = []
        if bkg:
            self._backgroundFiles = [b for b in bkg if os.path.exists(b)]
            if not self._backgroundFiles:
                self.warnings.append('Not all the {} background files could be found'.format(self.type))

    @property
    def darkBackground(self):
        return self._darkBackgroundFiles

    @darkBackground.setter
    def darkBackground(self, dark):
        self._darkBackgroundFiles = []
        if dark:
            self._darkBackgroundFiles = [d for d in dark if os.path.exists(d)]
            if not self._darkBackgroundFiles:
                self.warnings.append('Not all the {} dark background files could be found'.format(self.type))

    @property
    def darkSample(self):
        return self._darkSampleFiles

    @darkSample.setter
    def darkSample(self, dark):
        self._darkSampleFiles = []
        if dark:
            self._darkSampleFiles = [d for d in dark if os.path.exists(d)]
            if not self._darkSampleFiles:
                self.warnings.append('Not all the {} dark sample files could be found'.format(self.type))

    @property
    def poni(self):
        return self._poni

    @poni.setter
    def poni(self, filename):
        if not filename:
            self.errors.append('The {} poni file must be specified'.format(self.type))
            return
        if os.path.exists(filename):
            self._poni = open(filename).read()
        else:
            try:
                self._poni = compressor.decompress(filename).decode()
            except compressor.CompressError:
                self.errors.append('The {} poni string seems to be corrupted'.format(self.type))

    @property
    def maskFile(self):
        return self._maskFile

    @maskFile.setter
    def maskFile(self, mask):
        if not mask:
            self._maskFile = None
        else:
            _mask = compressor.decompressNumpyArray(mask)
            if _mask is not None:
                self._maskFile = _mask
            else:
                if os.path.exists(mask):
                    self._maskFile = mask
                else:
                    self._maskFile = None
                    self.warnings.append('The {} mask file "{}" cannot be found. '
                                         'Run without mask'.format(self.type, mask))

    @property
    def spline(self):
        return self._splineFile

    @spline.setter
    def spline(self, spline):
        self._splineFile = None
        if spline:
            if os.path.exists(spline):
                self._splineFile = spline
            else:
                self.warnings.append('The {} spline file "{}" cannot be found'.format(self.type, spline))

    @property
    def flood(self):
        return self._floodFile

    @flood.setter
    def flood(self, flood):
        self._floodFile = None
        if flood:
            if os.path.exists(flood):
                self._floodFile = flood
            else:
                self.warnings.append('The {} flood file "{}" cannot be found'.format(self.type, flood))

    @property
    def bkgCoef(self):
        return self._bkgCoef

    @bkgCoef.setter
    def bkgCoef(self, coef):
        self._bkgCoef = coef

    @property
    def radial(self):
        return self._radial

    @radial.setter
    def radial(self, values):
        self._radial = values

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, values):
        self._azimuth = values

    @property
    def azimuthChecked(self):
        return self._azimuth_checked

    @azimuthChecked.setter
    def azimuthChecked(self, value):
        self._azimuth_checked = value

    @property
    def azimuthSlices(self):
        return self._azimuth_slices

    @azimuthSlices.setter
    def azimuthSlices(self, value):
        self._azimuth_slices = value

    @property
    def beamline(self):
        return self._beamline

    @beamline.setter
    def beamline(self, beamline):
        self._beamline = beamline

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, thickness):
        self._thickness = thickness

    @property
    def concentration(self):
        return self._concentration

    @concentration.setter
    def concentration(self, concentration):
        self._concentration = concentration

    @property
    def calibration(self):
        return self._calibration

    @calibration.setter
    def calibration(self, calibration):
        self._calibration = calibration

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, units):
        self._units = units

    @property
    def ext(self):
        return self._ext

    @ext.setter
    def ext(self, ext):
        self._ext = ext

    @property
    def subdir(self):
        return self._subdir

    @subdir.setter
    def subdir(self, subdir):
        self._subdir = subdir

    @property
    def detector(self):
        return self._detector

    @detector.setter
    def detector(self, detector):
        self._detector = detector

    @property
    def save(self):
        return self._save

    @save.setter
    def save(self, save):
        self._save = save

    @property
    def speed(self):
        with self._lock:
            return self._speed

    @speed.setter
    def speed(self, speed):
        with self._lock:
            self._speed = speed

    @property
    def sspeed(self):
        with self._lock:
            return self._sspeed

    @sspeed.setter
    def sspeed(self, sspeed):
        with self._lock:
            self._sspeed = sspeed

    def clearState(self):
        self.counter = 0

    @property
    def counter(self):
        with self._lock:
            return self._counter

    @counter.setter
    def counter(self, value):
        with self._lock:
            self._counter = value

    @property
    def pickle(self):
        return self._pickle

    @pickle.setter
    def pickle(self, v):
        self._pickle = v

    @property
    def incidence(self):
        return self._incidence

    @incidence.setter
    def incidence(self, v):
        self._incidence = v

    @property
    def normalization(self):
        return self._normalization

    @normalization.setter
    def normalization(self, v):
        self._normalization = v

    @property
    def normrange(self):
        return self._normrange

    @normrange.setter
    def normrange(self, v):
        if isinstance(v, (tuple, list)) and len(v) == 2:
            self._normrange = v
        else:
            self._normrange = 0, 0

    @property
    def is_monitor(self):
        return self._normalization == 'Monitor'

    @property
    def double(self):
        return self._precision == 'double'

    @double.setter
    def double(self, value: bool):
        self._precision = 'double' if value else 'float'
        self.i = igracio.IGracio(precision=self._precision)

    @property
    def polarization(self):
        return self._polarization

    @polarization.setter
    def polarization(self, value: float):
        self._polarization = value

    @property
    def halina(self):
        return self._halina

    @halina.setter
    def halina(self, value: bool):
        self._halina = value

    @property
    def solidangle(self):
        return self._solidangle

    @solidangle.setter
    def solidangle(self, value: bool):
        self._solidangle = value

    @property
    def bins(self):
        return self._bins

    @bins.setter
    def bins(self, value: bool):
        self._bins = value

    @property
    def threads(self):
        return self._threads

    @threads.setter
    def threads(self, value: int):
        self._threads = value


class Iwaxs(_Interface):
    def __init__(self):
        super().__init__()
        self.type = 'waxs'


class Isaxs(_Interface):
    def __init__(self):
        super().__init__()
        self.type = 'saxs'
        self.calcTransmission = True
