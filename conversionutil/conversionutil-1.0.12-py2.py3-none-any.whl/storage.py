# encoding: utf-8

import logging_helper

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'

logging = logging_helper.setup_logging()

FORMAT = u"{neg}{size:.{decimals}f}{output_units}"
MULTIPLIER = u'multiplier'
EXPONENT = u'exp'
DECIMALS = u'decimals'

# KB - Kilobyte; KiB - KibiByte
# 1 KB = 1000 B; 1KiB = 1024 B
SI_MULTIPLIER = 1000  # The new system
IEC_MULTIPLIER = 1024  # The old system

BYTES = u'B'
KILOBYTES = u'KB'
KIBIBYTES = u'KiB'
MEGABYTES = u'MB'
MEBIBYTES = u'MiB'
GIGABYTES = u'GB'
GIBIBYTES = u'GiB'
TERABYTES = u'TB'
TEBIBYTES = u'TiB'
PETABYTES = u'PB'
PEBIBYTES = u'PiB'
EXABYTES = u'EB'
EXBIBYTES = u'EiB'
ZETTABYTES = u'ZB'
ZEBIBYTES = u'ZiB'
YOTTABYTES = u'YB'
YOBIBYTES = u'YiB'

SUPPORTED_UNITS = {BYTES:      {MULTIPLIER: SI_MULTIPLIER,  EXPONENT: 0},
                   KIBIBYTES:  {MULTIPLIER: IEC_MULTIPLIER, EXPONENT: 1},
                   KILOBYTES:  {MULTIPLIER: SI_MULTIPLIER,  EXPONENT: 1},
                   MEBIBYTES:  {MULTIPLIER: IEC_MULTIPLIER, EXPONENT: 2},
                   MEGABYTES:  {MULTIPLIER: SI_MULTIPLIER,  EXPONENT: 2},
                   GIBIBYTES:  {MULTIPLIER: IEC_MULTIPLIER, EXPONENT: 3},
                   GIGABYTES:  {MULTIPLIER: SI_MULTIPLIER,  EXPONENT: 3},
                   TEBIBYTES:  {MULTIPLIER: IEC_MULTIPLIER, EXPONENT: 4},
                   TERABYTES:  {MULTIPLIER: SI_MULTIPLIER,  EXPONENT: 4},
                   PEBIBYTES:  {MULTIPLIER: IEC_MULTIPLIER, EXPONENT: 5},
                   PETABYTES:  {MULTIPLIER: SI_MULTIPLIER,  EXPONENT: 5},
                   EXBIBYTES:  {MULTIPLIER: IEC_MULTIPLIER, EXPONENT: 6},
                   EXABYTES:   {MULTIPLIER: SI_MULTIPLIER,  EXPONENT: 6},
                   ZEBIBYTES:  {MULTIPLIER: IEC_MULTIPLIER, EXPONENT: 7},
                   ZETTABYTES: {MULTIPLIER: SI_MULTIPLIER,  EXPONENT: 7},
                   YOBIBYTES:  {MULTIPLIER: IEC_MULTIPLIER, EXPONENT: 8},
                   YOTTABYTES: {MULTIPLIER: SI_MULTIPLIER,  EXPONENT: 8}, }


def convert_storage_size(value,
                         input_units=BYTES,
                         output_units=None,
                         decimals=2):

    value = int(value)

    # Validate Units
    if input_units not in SUPPORTED_UNITS:
        raise ValueError(u'{units} is not a recognised unit'
                         .format(units=input_units))

    elif output_units is not None and output_units not in SUPPORTED_UNITS:
        raise ValueError(u'{units} is not a recognised unit'
                         .format(units=output_units))

    input_multiplier = SUPPORTED_UNITS[input_units][MULTIPLIER]
    if output_units is not None:
        output_multiplier = SUPPORTED_UNITS[output_units][MULTIPLIER]
    else:

        output_multiplier = input_multiplier

    # Check for and extract negative
    neg = u'-' if value < 0 else u''
    value = abs(value)

    # Convert input to bytes
    size = float(value * input_multiplier ** SUPPORTED_UNITS[input_units][EXPONENT])

    # Run the Conversion
    for output_type in (BYTES,
                        KIBIBYTES if output_multiplier is IEC_MULTIPLIER else KILOBYTES,
                        MEBIBYTES if output_multiplier is IEC_MULTIPLIER else MEGABYTES,
                        GIBIBYTES if output_multiplier is IEC_MULTIPLIER else GIGABYTES,
                        TEBIBYTES if output_multiplier is IEC_MULTIPLIER else TERABYTES,
                        PEBIBYTES if output_multiplier is IEC_MULTIPLIER else PETABYTES,
                        EXBIBYTES if output_multiplier is IEC_MULTIPLIER else EXABYTES,
                        ZEBIBYTES if output_multiplier is IEC_MULTIPLIER else ZETTABYTES,
                        YOBIBYTES if output_multiplier is IEC_MULTIPLIER else YOTTABYTES):

        if (size < output_multiplier and output_units is None) or output_units == output_type:
            decimals = 0 if SUPPORTED_UNITS[output_type][EXPONENT] is 0 else decimals

            return FORMAT.format(neg=neg,
                                 size=size,
                                 decimals=decimals,
                                 output_units=output_type)
        # Not matched, try the next size up
        size = size / output_multiplier