#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Hannah Muckenhirn <hannah.muckenhirn@idiap.ch>
# Fri April  1 14:24:21 CEST 2016
#
# Copyright (C) 2012-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from setuptools import setup, dist

dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements, find_packages

install_requires = load_requirements()

setup(
    name='bob.paper.taslp_2017',
    version=open("version.txt").read().rstrip(),
    description='Presentation Attack Detection Using Long Term Spectral Statistics for Trustworthy Speaker Verification',
    url='https://gitlab.idiap.ch/bob/bob.paper.taslp_2017',
    license='GPLv3',
    keywords = "presentation attack detection, speaker verification, long term spectral statistics",
    author='Hannah Muckenhirn',
    author_email='hannah.muckenhirn@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
   
    install_requires=install_requires,
    
    entry_points={
      'console_scripts': [
        'evaluate_pad.py                    = bob.paper.taslp_2017.script.evaluate_pad:main',
        'compute_EER_perattack_eval.py      = bob.paper.taslp_2017.script.compute_EER_perattack_eval:main',
        'compute_HTER_perattack_eval.py      = bob.paper.taslp_2017.script.compute_HTER_perattack_eval:main',
        ], 
       'bob.pad.database': [
        'avspoof-physical            = bob.paper.taslp_2017.config.database.avspoof_physical:database',
	'avspoof                     = bob.paper.taslp_2017.config.database.avspoof:database',
        'avspoof-logical             = bob.paper.taslp_2017.config.database.avspoof_logical:database',
        'asvspoof-cm                        = bob.paper.taslp_2017.config.database.asvspoof_cm:database',
       ],
       'bob.pad.algorithm': [
         'lda                     = bob.paper.taslp_2017.algorithm.lda:algorithm',
      ],
       'bob.pad.extractor': [
        'mean-spectrum-32ms-shift-10ms     = bob.paper.taslp_2017.config.extractor.mean_spectrum_32ms_shift_10ms:extractor',
        'mean-spectrum-256ms-shift-10ms     = bob.paper.taslp_2017.config.extractor.mean_spectrum_256ms_shift_10ms:extractor',
        'std-spectrum-32ms-shift-10ms      = bob.paper.taslp_2017.config.extractor.std_spectrum_32ms_shift_10ms:extractor',
        'std-spectrum-256ms-shift-10ms      = bob.paper.taslp_2017.config.extractor.std_spectrum_256ms_shift_10ms:extractor',
        'mean-std-spectrum-16ms-shift-10ms  = bob.paper.taslp_2017.config.extractor.mean_std_spectrum_16ms_shift_10ms:extractor',
        'mean-std-spectrum-32ms-shift-10ms  = bob.paper.taslp_2017.config.extractor.mean_std_spectrum_32ms_shift_10ms:extractor',
        'mean-std-spectrum-64ms-shift-10ms  = bob.paper.taslp_2017.config.extractor.mean_std_spectrum_64ms_shift_10ms:extractor',
        'mean-std-spectrum-128ms-shift-10ms = bob.paper.taslp_2017.config.extractor.mean_std_spectrum_128ms_shift_10ms:extractor',
        'mean-std-spectrum-256ms-shift-10ms = bob.paper.taslp_2017.config.extractor.mean_std_spectrum_256ms_shift_10ms:extractor',
        'mean-std-spectrum-512ms-shift-10ms = bob.paper.taslp_2017.config.extractor.mean_std_spectrum_512ms_shift_10ms:extractor',
   ],
       'bob.pad.preprocessor': [
        'energy-2gauss-remove-head-tail     = bob.paper.taslp_2017.config.preprocessor.energy_2gauss_remove_head_tail:preprocessor',
        'none                               = bob.paper.taslp_2017.config.preprocessor.no_preprocessing:preprocessor',       
      ],
      'bob.pad.grid': [
        'normal                             = bob.paper.taslp_2017.config.grid.normal:grid',
      ],
      },


    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
)
