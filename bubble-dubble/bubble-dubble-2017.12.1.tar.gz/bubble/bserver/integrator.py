#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import traceback
import numpy as np
from scipy.misc import imresize
import cryio
import decor
from ..bcommon import compressor


class Integrator:
    MAX_ATTEMPTS = 10

    def __call__(self, filename, interface, catchException=True):
        image = self.open_image(filename, interface.is_monitor)
        if not image:
            return None
        if catchException:
            # noinspection PyBroadException
            try:
                result = self._integrate(filename, image, interface)
            except Exception:
                traceback.print_exc(file=sys.stdout)
                print(f'Frame: {filename}')
                return None
            else:
                return result
        else:
            return self._integrate(filename, image, interface)

    def _integrate(self, filename, frames, interface):
        retval = None
        ext = interface.ext
        if ext.startswith('.'):
            ext = ext[1:]
        if frames.header.get('Bubble_normalized', 0):
            return retval
        path, base = os.path.split(filename)
        newpath = os.path.join(path, interface.subdir)
        if frames.multiframe:
            newpath = os.path.join(newpath, '.'.join(base.split('.')[:-1]))
        try:  # it seems that here we can have race conditions
            os.makedirs(newpath)
        except OSError:
            pass
        for i, image in enumerate(frames):
            image = self.apply_corrections(interface, image)
            res, chi = self._do_integration(interface, image, base, newpath, ext, i)
            self.saveNormalizedFrame(interface, chi, image)
            img, data = self.pack_data(interface, image, res)
            interface.counter += 1
            retval = {
                'imageFile': filename,
                'chiFile': chi,
                'transmission': image.transmission_coefficient,
                'data1d': data,
                'image': img,
                'timestamp': time.time(),
                'sent': False,
            }
        return retval

    def open_image(self, filename, is_monitor):
        i = 0
        while True:
            i += 1
            # noinspection PyBroadException
            try:
                image = cryio.openImage(filename)
                if is_monitor and isinstance(image, cryio.cbfimage.CbfImage) and 'Flux' not in image.header:
                    raise ValueError(f'Cbf file {filename} does not contain the "Flux" key in the header.\n'
                                     f'Either switch off the normalization by monitor or wait until all the headers '
                                     f'are written')
            except Exception:
                if i < self.MAX_ATTEMPTS:
                    print(f'File {filename} could not be read {i:d} times, another attempt in 1 sec...')
                    time.sleep(1)
                else:
                    traceback.print_exc(file=sys.stdout)
                    print(f'Frame {filename} could not be read, see exception above :(')
                    return None
            else:
                return image

    def apply_corrections(self, i, image):
        image.float()
        image = i.darksample(image)
        image = i.flatfield(image)
        image = i.normalize(image)
        image = i.background(image, i.calcTransmission, i.thickness, i.concentration, i.halina)
        image.array *= i.calibration
        image = i.mask(image)
        image.array = i.distortion(image.array)
        return image

    def pack_data(self, i, image, res):
        img = None
        rs = None
        if not i.speed:
            img = decor.correctImage(i.beamline, i.type, image.array)
            img = imresize(img, 40)
            img = compressor.compressNumpyArray(img, not i.pickle)
        if not i.sspeed:
            rs = [compressor.compressNumpyArray(array, not i.pickle) for array in res]
        return img, rs

    def _do_integration(self, i, image, base, newpath, ext, num):
        res, chi = None, None
        ext = ext if ext else 'dat'
        mf = '_{:05d}'.format(num) if image.multiframe else ''
        if i.azimuthChecked and i.azimuthSlices:
            step = i.azimuth[1]
            for aslice in np.arange(0, 360, step):
                azmin, azmax = aslice, aslice + step
                res = i.i(image.array, azmin, azmax)
                chi = '{}{}_{:03.0f}_{:03.0f}.{}'.format('.'.join(base.split('.')[:-1]), mf, azmin, azmax, ext)
                self._save_results(i, newpath, chi, res, image.transmission_coefficient)
        else:
            i.i.azimuth = i.azimuth if i.azimuthChecked else None
            res = i.i(image.array)
            chi = '{}{}.{}'.format('.'.join(base.split('.')[:-1]), mf, ext)
            res = self._save_results(i, newpath, chi, res, image.transmission_coefficient)
        return res, chi

    def correctIncidence(self, i, res):
        if i.detector == 'Frelon' and i.incidence:
            return decor.correctFrelonIncidence(i.wavelength, res)
        return res

    def _save_results(self, i, newpath, chi, res, transCoef):
        res = np.array(res)
        res = self.correctIncidence(i, res)
        res = i.normalize.norm_after(res, i.calibration)
        chi = os.path.join(newpath, chi)
        np.savetxt(chi, res.T, '%.6e')
        if i.calcTransmission:
            with open(chi, 'r+') as fchi:
                old = fchi.read()
                fchi.seek(0)
                fchi.write('# Transmission coefficient {0:.7f}\n{1}'.format(transCoef, old))
        return res

    def saveNormalizedFrame(self, i, chifile, image):
        if i.save:
            image.array = image.array.astype(np.int32)
            name = '{}_norm.edf'.format(chifile[:-4])
            image.save_edf(name, Bubble_normalized=1)
