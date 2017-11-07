#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
:mod:`emsa` -- Reader/writer of EMSA/MAS file format
================================================================================

.. module:: emsa
   :synopsis: Reader/writer of EMSA/MAS file format.

.. moduleauthor:: Philippe T. Pinard <philippe.pinard@gmail.com>

.. inheritance-diagram:: pySpectrumFileFormat.emmff.emsa

"""

###############################################################################
# Copyright 2011 Philippe T. Pinard
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

# Standard library modules.
import os
import copy
from collections import MutableMapping

# Third party modules.

# Local modules.

# Project modules.
from pySpectrumFileFormat.emmff.formatter import formatter

# Globals and constants variables.

# Required
FORMAT = "FORMAT"
VERSION = "VERSION"
TITLE = "TITLE"
DATE = "DATE"
TIME = "TIME"
OWNER = "OWNER"
NPOINTS = "NPOINTS"
NCOLUMNS = "NCOLUMNS"
XUNITS = "XUNITS"
YUNITS = "YUNITS"
DATATYPE = "DATATYPE"
XPERCHAN = "XPERCHAN"
OFFSET = "OFFSET"

# Spectrum data
SPECTRUM = "SPECTRUM"
ENDOFDATA = "ENDOFDATA"

# Optional keywords relating mainly to spectrum characteristics.
SIGNALTYPE = "SIGNALTYPE"
XLABEL = "XLABEL"
YLABEL = "YLABEL"
CHOFFSET = "CHOFFSET"
COMMENT = "COMMENT"

# Optional keywords relating mainly to microscope/instrument.
BEAM_ENERGY = "BEAMKV"
EMISSION_CURRENT = "EMISSION"
PROBE_CURRENT = "PROBECUR"
BEAM_DIAMETER = "BEAMDIA"
MAGNIFICATION = "MAGCAM"
CONVERGENCE_ANGLE = "CONVANGLE"
OPERATING_MODE = "OPERMODE"

# Optional keywords relating mainly to specimen.
THICKNESS = "THICKNESS"
XSTAGE_TILT = "XTILTSTGE"
YSTAGE_TILT = "YTILTSTGE"
XPOSITION = "XPOSITION"
YPOSITION = "YPOSITION"
ZPOSITION = "ZPOSITION"

# Keywords relating mainly to ELS.
DWELL_TIME = "DWELLTIME"
INTEGRATION_TIME = "INTEGTIME"
COLLECTION_ANGLE = "COLLANGLE"
ELS_DETECTOR_TYPE = "ELSDET"

# Optional keywords relating mainly to EDS.
ELEVATION_ANGLE = "ELEVANGLE"
AZIMUTHAL_ANGLE = "AZIMANGLE"
SOLID_ANGLE = "SOLIDANGLE"
LIVE_TIME = "LIVETIME"
REAL_TIME = "REALTIME"
BE_WINDOW_THICKNESS = "TBEWIND"
AU_WINDOW_THICKNESS = "TAUWIND"
DEAD_LAYER_THICKNESS = "TDEADLYR"
ACTIVE_LAYER_THICKNESS = "TACTLYR"
AL_WINDOW_THICKNESS = "TALWIND"
PYROLENE_WINDOW_THICKNESS = "TPYWIND"
BORON_NITRIDE_WINDOW_THICKNESS = "TBNWIND"
DIAMOND_WINDOW_THICKNESS = "TDIWIND"
HYDRO_CARBON_WINDOW_THICKNESS = "THCWIND"
EDS_DETECTOR_TYPE = "EDSDET"
CHECKSUM = "CHECKSUM"

# Oxford instruments
OXINSTELEMS = "OXINSTELEMS"
OXINSTLABEL = "OXINSTLABEL"

# Default values
DATA_TYPE_Y = "Y"
DATA_TYPE_XY = "XY"

SIGNAL_TYPE_EDS = 'EDS' # Energy Dispersive Spectroscopy
SIGNAL_TYPE_WDS = 'WDS'  # Wavelength Dispersive Spectroscopy
SIGNAL_TYPE_ELS = 'ELS' # Energy Loss Spectroscopy
SIGNAL_TYPE_AES = 'AES' # Auger Electron Spectroscopy
SIGNAL_TYPE_PES = 'PES' # Photo Electron Spectroscopy
SIGNAL_TYPE_XRF = 'XRF' # X-ray Fluorescence Spectroscopy
SIGNAL_TYPE_CLS = 'CLS' # Cathodoluminescence Spectroscopy
SIGNAL_TYPE_GAM = 'GAM' # Gamma Ray Spectroscopy

OPERATING_MODE_IMAGE = "IMAGE" # Imaging Mode
OPERATING_MODE_DIFFR = "DIFFR" # Diffraction Mode
OPERATING_MODE_SCIMG = "SCIMG" # Scanning Imaging Mode
OPERATING_MODE_SCDIF = "SCDIF" # Scanning Diffraction Mode

ELS_DETECTOR_SERIAL = "SERIAL" # Serial ELS Detector
ELS_DETECTOR_PARALL = "PARALL" # Parallel ELS Detector

EDS_DETECTOR_SIBEW = 'SIBEW' # Si(Li) with Be Window
EDS_DETECTOR_SIUTW = 'SIUTW' # Si(Li) with Ultra Thin Window
EDS_DETECTOR_SIWLS = 'SIWLS' # Si(Li) Windowless
EDS_DETECTOR_GEBEW = 'GEBEW' # Ge with Be Window
EDS_DETECTOR_GEUTW = 'GEUTW' # Ge with Ultra Thin Window
EDS_DETECTOR_GEWLS = 'GEWLS' # Ge Windowless

_REQUIRED_KEYWORDS = [FORMAT, VERSION, TITLE, DATE, TIME, OWNER, NPOINTS,
                      NCOLUMNS, XUNITS, YUNITS, DATATYPE, XPERCHAN, OFFSET]

_DOC = {
    FORMAT: 'Character string identifies this format',
    VERSION: 'File format version number',
    TITLE: 'Short description of the spectra',
    DATE: 'The calendar day-month-year in which the spectra was recorded, DD-MMM-YYYY',
    TIME: 'The time of day at which the spectrum was recorded, in 24-hour format, HH:MM',
    OWNER: 'The name of the persion that recorded the spectrum',
    NPOINTS: 'total number of data points in X&Y data arrays',
    NCOLUMNS: 'Number of columns of data',
    XUNITS: 'Units for x-axis data, for example: eV.',
    YUNITS: 'Units for y-axis data, for example: counts.',
    DATATYPE: 'Method in which the data values are stored as Y Axis only values or X,Y data pairs.',
    XPERCHAN: 'The number of x-axis units  per channel.',
    OFFSET: 'A real (but possibly negative) number representing  value of channel one in xunits.',

    # Optional keywords relating mainly to spectrum characteristics.
    SIGNALTYPE: 'Type of Spectroscopy',
    XLABEL: 'X-Axis Data label',
    YLABEL: 'Y-Axis Data label',
    CHOFFSET: 'A real (but possibly negative) number  representing the channel number whose value corresponds to zero units on the x-axis scale.',
    COMMENT: 'Comment line',

    # Optional keywords relating mainly to microscope/instrument.
    BEAM_ENERGY: 'Accelerating Voltage of Instrument in kilovolts',
    EMISSION_CURRENT: 'Gun Emission current in microAmps',
    PROBE_CURRENT: 'Probe current in nanoAmps',
    BEAM_DIAMETER: 'Diameter of incident probe in nanometers',
    MAGNIFICATION: 'Magnification or Camera Length, Mag in x or times, Cl in mm',
    CONVERGENCE_ANGLE: 'Convergence semi-angle of incident beam in milliRadians',
    OPERATING_MODE: 'Operating Mode',

    # Optional keywords relating mainly to specimen.
    THICKNESS: 'Specimen thickness in nanometers',
    XSTAGE_TILT: 'Specimen stage tilt X-axis in degrees',
    YSTAGE_TILT: 'Specimen stage tilt Y-axis in degrees',
    XPOSITION: 'Specimen/Beam position along the X axis',
    YPOSITION: 'Specimen/Beam position along the Y axis',
    ZPOSITION: 'Specimen/Beam position along the Z axis',

    # Keywords relating mainly to ELS.
    DWELL_TIME: 'Dwell time/channel for serial data collection in msec',
    INTEGRATION_TIME: 'Integration time per spectrum for parallel data collection in milliseconds',
    COLLECTION_ANGLE: 'Collection semi-angle of scattered beam in mR',
    ELS_DETECTOR_TYPE: 'Type of ELS Detector',

    # Optional keywords relating mainly to EDS.
    ELEVATION_ANGLE: 'Elevation angle of EDS,WDS detector in degrees',
    AZIMUTHAL_ANGLE: 'Azimuthal angle of EDS,WDS detector in degrees',
    SOLID_ANGLE: 'Collection solid angle of detector in sR',
    LIVE_TIME: 'Signal Processor Active (Live) time in seconds',
    REAL_TIME: 'Total clock time used to record the spectrum in seconds',
    BE_WINDOW_THICKNESS: 'Thickness of Be Window on detector in cm',
    AU_WINDOW_THICKNESS: 'Thickness of Au Window/Electrical Contact in cm',
    DEAD_LAYER_THICKNESS: 'Thickness of Dead Layer in cm',
    ACTIVE_LAYER_THICKNESS: 'Thickness of Active Layer in cm',
    AL_WINDOW_THICKNESS: 'Thickness of Aluminium Window in cm',
    PYROLENE_WINDOW_THICKNESS: 'Thickness of Pyrolene Window in cm',
    BORON_NITRIDE_WINDOW_THICKNESS: 'Thickness of Boron-Nitride Window in cm',
    DIAMOND_WINDOW_THICKNESS: 'Thickness of Diamond Window in cm',
    HYDRO_CARBON_WINDOW_THICKNESS: 'Thickness of HydroCarbon Window in cm',
    EDS_DETECTOR_TYPE: 'Type of X-ray Detector'
    }

class EmsaHeader(MutableMapping):
    def __init__(self):
        self._data = {}

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __delitem__(self, key):
        del self._data[key]

    def __setitem__(self, key, value):
        self._data[key.upper()] = value

    def __getitem__(self, key):
        return self._data[key.upper()]

    def __getattr__(self, name):
        if not name.startswith('_'):
            return self[name]
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            self[name] = value
        else:
            object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if not name.startswith('_'):
            del self[name]

    def help(self, key):
        """
        Returns the definition/documentation of a keyword.
        Return an empty string if the keyword is unknown.
        """
        return _DOC.get(key, '')

class Emsa(object):
    def __init__(self):
        """
        An EMSA spectrum file.
        Use :func:`.read` or :func:`.write` to read and write EMSA spectrum
        file.

        The data of the spectrum can be accessed from the attributes:

          * :attr:`xdata`: x values (typically energy)
          * :attr:`ydata`: y values (typically counts)
          * :meth:`get_data <.Emsa.get_data>`: list of tuples

        The header's keywords can be accessed from the attribute :attr:`header`
        as follows::

          >>> spectrum1 = emsa.Emsa()
          >>> spectrum1.header.beamkv = 15.0
          >>> print(spectrum.header.beamkv)
          >>> 15.0

          >>> spectrum1.header[BEAM_ENERGY] = 15.0
          >>> print(spectrum.header[BEAM_ENERGY])
          >>> 15.0
        """
        self._header = EmsaHeader()
        self._header.format = "EMSA/MAS Spectral Data File"
        self._header.version = 1.0

        self.xdata = []
        self.ydata = []

    @property
    def header(self):
        """
        Header of the EMSA spectrum.
        The keyword of the header can be retrieved, set and deleted from the
        header.

        Example::

          >>> spectrum1 = emsa.Emsa()
          >>> spectrum1.header.title = "Spectrum 1"
          >>> print(spectrum.header.title)
          >>> Spectrum 1

          >>> spectrum1.header[TITLE] = "Spectrum 1"
          >>> print(spectrum.header[TITLE])
          >>> Spectrum 1
        """
        return self._header

    def validate(self):
        """
        Validates that the required keywords are defined and that the data
        is self-consistent.
        Raises :exc:`ValueError`.
        """
        for keyword in _REQUIRED_KEYWORDS:
            if keyword not in self.header:
                raise ValueError("Missing required keyword: %s" % keyword)

        if len(self.xdata) != len(self.ydata):
            raise ValueError("Number of x points (%i) != number of y points (%i)" % \
                (len(self.xdata), len(self.ydata)))

        if self.header.npoints != len(self.ydata):
            raise ValueError("Keyword NPOINTS (%i) != number of points in the data (%i)" % \
                (self.header.npoints, len(self.ydata)))

    def get_data(self):
        """
        Returns the data as a list of tuples: ``[(x0,y0), (x1,y1), ...]``.
        """
        assert(len(self.xdata) == len(self.ydata))
        return zip(self.xdata, self.ydata)

def _calculate_checksum(lines):
    checksum = 0

    for line in lines:
        if line.startswith('#CHECKSUM'):
            continue
        for character in line:
            checksum += ord(character.encode('utf-8'))

    return checksum

class EmsaReader(object):
    """
    Class to read EMSA spectrum.
    The wrapper function :func:`.read` should be used instead of this class.
    """

    def read(self, fileobj):
        """
        Reads an EMSA spectrum from the specified file-object and returns
        a :class:`.Emsa`

        :return: :class:`.Emsa`
        """
        return self._read_lines(fileobj.readlines())

    def _read_lines(self, lines):
        emsa = Emsa()
        self._checksum = -1

        # Parse lines
        for line in lines:
            self._parse_line(emsa, line)

        # Validate
        if self._checksum > 0: # only check if a checksum is in the input file
            checksum = _calculate_checksum(lines)
            if checksum != self._checksum:
                raise IOError("The checksums don't match: %i != %i " % \
                    (checksum, self._checksum))

        # Create xdata for DATA_TYPE == Y
        emsa.header.npoints = len(emsa.ydata)
        if not emsa.xdata:
            npoints = len(emsa.ydata)
            offset = emsa.header.offset
            xperchan = emsa.header.xperchan
            emsa.xdata = self._create_xdata(npoints, offset, xperchan)

        emsa.validate()

        return emsa

    def _parse_line(self, emsa, line):
        if self._is_line_keyword(line):
            keyword, comment, value = self._parse_keyword_line(line)

            if keyword in [SPECTRUM, ENDOFDATA]:
                return
            elif keyword == CHECKSUM:
                self._checksum = int(value)

            value = formatter.from_string(value)
            if comment:
                emsa.header[keyword] = (value, comment)
            else:
                emsa.header[keyword] = value
        else: # data line
            row = self._parse_data_line(line)

            if DATATYPE in emsa.header and NCOLUMNS in emsa.header:
                if emsa.header[DATATYPE] == DATA_TYPE_XY:
                    emsa.xdata.append(row[0])
                    emsa.ydata.append(row[1])
                elif emsa.header[DATATYPE] == DATA_TYPE_Y:
                    emsa.ydata.extend(row)

    def _is_line_keyword(self, line):
        try:
            if line.strip()[0] == '#':
                return True
        except:
            pass

        return False

    def _parse_keyword_line(self, line):
        line = line.strip("#") # Strip keyword character

        keyword, value = line.split(":", 1)

        keyword = keyword.strip()
        value = value.strip()

        try:
            keyword, comment = keyword.split()
        except:
            comment = ""

        keyword = keyword.upper()
        comment = comment.strip("-")

        return (keyword, comment, value)

    def _parse_data_line(self, line):
        # Split values separated by a comma
        tmprow = [value.strip() for value in line.split(',')]

        # Split values separated by a space
        row = []
        for value in tmprow:
            row.extend(value.split())

        # Convert to float
        row = [float(value) for value in row]

        return row

    def _create_xdata(self, npoints, offset, xperchan):
        return [offset + xperchan * i for i in range(npoints)]

def read(fileobj):
    """
    Reads a file-object containing a EMSA spectrum.

    The function will raise :exc:`ValueError` if the read :class:`.Emsa` is not
    valid or :exc:`IOError` if the checksums don't match.

    Example::

      with open('spectrum1.emsa', 'r') as f:
          spectrum1 = emsa.read(f)

    :return: :class:`.Emsa`
    """
    return EmsaReader().read(fileobj)

class EmsaWriter(object):
    """
    Class to write EMSA spectrum.
    The wrapper function :func:`.write` should be used instead of this class.
    """

    def write(self, emsa, fileobj):
        """
        Writes the specified :class:`.Emsa` spectrum in the file-object.
        The method will raise :exc:`ValueError` if the :class:`.Emsa` is not
        valid.
        """
        emsa.validate()

        lines = self._create_lines(emsa)

        for line in lines:
            fileobj.write(line + os.linesep)

    def _create_lines(self, emsa):
        lines = []

        ## Keywords
        header = copy.deepcopy(emsa.header) # copy of header

        # Required keywords
        for keyword in _REQUIRED_KEYWORDS:
            lines.append(self._create_keyword_line(keyword, header[keyword]))
            header.pop(keyword)

        # Other keywords
        for keyword, value in header.items():
            lines.append(self._create_keyword_line(keyword, value))

        # Data lines
        lines.append(self._create_keyword_line(SPECTRUM,
                                               'Spectral Data Starts Here'))
        lines.extend(self._create_data_lines(emsa))
        lines.append(self._create_keyword_line(ENDOFDATA, ''))

        # Checksum
        checksum = _calculate_checksum(lines)
        lines.append(self._create_keyword_line(CHECKSUM, checksum))

        return lines

    def _create_keyword_line(self, keyword, value):
        if isinstance(value, (tuple, list)):
            assert len(value) == 2
            value, comment = value

            tag = keyword.ljust(12 - len(comment)) + comment
        else:
            tag = keyword.ljust(12)

        assert len(tag) == 12

        return "#%s: %s" % (tag, formatter.to_string(value))

    def _create_data_lines(self, emsa):
        lines = []

        if emsa.header.datatype == DATA_TYPE_XY:
            for datum in emsa.get_data():
                lines.append("%s, %s" % datum)
        elif emsa.header.datatype == DATA_TYPE_Y:
            ncolumns = emsa.header.ncolumns
            for i in range(0, len(emsa.ydata), ncolumns):
                values = ['%s' % datum for datum in emsa.ydata[i:i + ncolumns]]
                lines.append(', '.join(values))

        return lines

def write(emsa, fileobj):
    """
    Writes an :class:`.Emsa` object into a file-object.

    The function will raise :exc:`ValueError` if the :class:`.Emsa` is not
    valid.

    Example::

      spectrum1 = emsa.Emsa()
      ...
      with open('spectrum1.emsa', 'w') as f:
          emsa.write(spectrum1, f)
    """
    EmsaWriter().write(emsa, fileobj)
