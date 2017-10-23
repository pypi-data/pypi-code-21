#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This lib produces the correct crysalis run files and other needed stuff.
Structure of the crysalis run file. Checked with dc editruns.
|*******************************************************************************|
|offset          size        type        description                            |
|*******************************************************************************|
|0x0-0x199       0x200       string      name of run                            | 1
|*******************************************************************************|
|0x200-0x201     0x2         ushort      number of scans to read (starts from 1)| 2
|0x204-0x20f     0xe                     unknown                                |
|*******************************************************************************|
|0x210-0x211     0x2         ushort      scan number (starts from 0)            | 3
|0x212-0x213     0x2         ushort      scanned axis (0x0 - omega, 0x4 - phi)  |
|0x214-0x217     0x4                     unknown                                |
|0x218-0x21f     0x8         double      unknown                                |
|0x220-0x227     0x8         double      detector-2theta                        |
|0x228-0x22f     0x8         double      kappa                                  |
|0x218-0x21f     0x8         double      phi or omega                           |
|0x238-0x23f     0x8         double      start                                  |
|0x240-0x247     0x8         double      end                                    |
|0x248-0x24f     0x8         double      width                                  |
|0x250-0x257     0x8                     unknown                                |
|0x258-0x25c     0x4         uint        #to do                                 |
|0x25d-0x25f     0x4         uint        #done                                  |
|0x260-0x267     0x8         double      exposure                               |
|*******************************************************************************|
|... block 3 again or EOF ...                                                   |
|*******************************************************************************|
"""

import os
import ctypes
from .templates import get_template


# noinspection PyTypeChecker
class RunHeader(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char * 256),
        ('folder', ctypes.c_char * 256),  # optional
        ('nscans', ctypes.c_ushort),
        ('unknown1', ctypes.c_int64),
    ]


class RunDscr(ctypes.Structure):
    _fields_ = [
        ('nscan', ctypes.c_ushort),
        ('axis', ctypes.c_ushort),
        ('unknown1', ctypes.c_int32),
        ('unknown2', ctypes.c_double),
        ('detector', ctypes.c_double),
        ('kappa', ctypes.c_double),
        ('omegaphi', ctypes.c_double),
        ('start', ctypes.c_double),
        ('end', ctypes.c_double),
        ('width', ctypes.c_double),
        ('unknown3', ctypes.c_double),
        ('todo', ctypes.c_uint32),
        ('done', ctypes.c_uint32),
        ('exposure', ctypes.c_double),
    ]


SCAN_AXIS = {
    'OMEGA': 0x0,
    'PHI': 0x4,
    'Omega': 0x0,
    'Phi': 0x4,
    'omega': 0x0,
    'phi': 0x4,
}


def saveSel(name, fmt=''):
    if fmt.lower() == 'esperanto':
        sel = get_template('sel_odEsp')
        num = 6
    else:
        sel = get_template('sel_od')
        num = 4
    with open(f'{name}_selexpinfo_1_{num}.sel_od', 'wb') as f:
        f.write(sel)


def saveCcd(name, fmt=''):
    try:
        ccd = get_template(f'ccd{fmt.lower()}')
    except KeyError:
        ccd = get_template(f'ccd2m')
    with open(f'{name}.ccd', 'wb') as f:
        f.write(ccd)


def saveSet(name, det='Frelon'):
    with open(f'{name}.set', 'wb') as f:
        f.write(get_template(f'set{det}').render().encode())


def saveRun(name, header, descr):
    structs = [header] + descr if isinstance(descr, (list, tuple)) else [header, descr]
    content = b''.join(bytes(memoryview(s)) for s in structs)
    with open(f'{name}.run', 'wb') as f:
        f.write(content)


def savePar(name, dct):
    with open(f'{name}.par', 'wb') as fPar:
        fPar.write(get_template('parfile').render(dct).encode().replace(b'#$$#', b'\xa7'))


def saveAliases(folder, params):
    with open(os.path.join(folder, 'dectrisaliases.ini'), 'wb') as f:
        f.write(get_template('aliases').render(params).encode())


def saveCrysalisExpSettings(folder):
    with open(os.path.join(folder, 'CrysalisExpSettings.ini'), 'wb') as f:
        f.write(get_template('CrysalisExpSettings.ini').render().encode())
