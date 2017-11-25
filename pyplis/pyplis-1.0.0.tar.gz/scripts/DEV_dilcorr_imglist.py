# -*- coding: utf-8 -*-
#
# Pyplis is a Python library for the analysis of UV SO2 camera data
# Copyright (C) 2017 Jonas Gliß (jonasgliss@gmail.com)
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License a
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
Pyplis example script no. 11 - Image based signal dilution correction

This script illustrates how extinction coefficients can be retrieved from 
image data using the DilutionCorr class and by specifying suitable terrain
features in the images. 

The extinction coefficients are retrieved from one on an from one off band 
image recorded ~15 mins before the dataset used in the other examples. The 
latter data is less suited for illustrating the feature since it contains 
less terrain (therfore more sky background). 

The two example images are then corrected for dilution and the results are 
plotted (as comparison of the retrieved emission rate along an exemplary 
plume cross section)
"""
from SETTINGS import check_version
# Raises Exception if conflict occurs
check_version()

import pyplis
from matplotlib.pyplot import close
from os.path import join, exists

### IMPORT GLOBAL SETTINGS
from SETTINGS import IMG_DIR, SAVEFIGS, SAVE_DIR, FORMAT, DPI, OPTPARSE
### IMPORTS FROM OTHER EXAMPLE SCRIPTS
from ex04_prep_aa_imglist import prepare_aa_image_list

### SCRIPT OPTONS  

### RELEVANT DIRECTORIES AND PATHS
CALIB_FILE = join(SAVE_DIR, "ex06_doascalib_aa.fts")
    
### SCRIPT MAIN FUNCTION       
if __name__ == "__main__":
    if not exists(CALIB_FILE):
        raise IOError("Calibration file could not be found at specified "
            "location:\n %s\nYou might need to run example 6 first")

    close("all")
    GO = False
    
    lst = prepare_aa_image_list()
    lst.ext_coeffs = 7.4e-5
    lst.get_off_list().ext_coeffs = 6.5e-5

    lst.aa_mode=False
    
    lst.vigncorr_mode = True
    lst.this.show(tit="vigncorr")
    
    lst.dilcorr_mode = True
    lst.this.show(tit="Dilcorr and vigncorr")
    
    lst.tau_mode = True
    lst.this.show(tit="tau (dilcorr)", vmin=-0.3, vmax=1.0)
    
    lst.dilcorr_mode = False
    lst.this.show(tit="tau (no dilcorr)", vmin=-0.3, vmax=1.0)
    
    lst.aa_mode = True 
    lst.this.show(tit="AA (no dilcorr)", vmin=-0.3, vmax=1.0)
    
    lst.dilcorr_mode = True
    lst.this.show(tit="AA (dilcorr)", vmin=-0.3, vmax=1.0)
    
    c = pyplis.DoasCalibData()
    c.load_from_fits(CALIB_FILE)
    
    lst.calib_data = c
    lst.dilcorr_mode=False
    lst.calib_mode = True
    lst.this.show(tit="Calib (no dilcorr)", vmin = -2e18, vmax=5e18)
    
    lst.dilcorr_mode = 1
    lst.this.show(tit="Calib (no dilcorr)", vmin = -2e18, vmax=5e18)
    if GO:
        from os import getcwd
        lst.correct_dilution_all(ext_on=7.4e-5, ext_off=6.5e-5,
                             save_dir=getcwd(),
                             save_masks=True, save_bg_imgs=True, 
                             save_tau_prev=True,
                             vmin_tau_prev=-0.3,
                             vmax_tau_prev=0.7)
        
