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

from SETTINGS import check_version
# Raises Exception if conflict occurs
check_version()

from os.path import join, exists
from os import mkdir
from collections import OrderedDict as od
from matplotlib.pyplot import close, rc_context, subplots

rc_context({'font.size':'18'})

import pyplis
### IMPORT GLOBAL SETTINGS
from SETTINGS import SAVE_DIR, FORMAT, DPI, LINES

SAVE_DIR_NEW = join(SAVE_DIR, "performance_test")
if not exists(SAVE_DIR_NEW):
    mkdir(SAVE_DIR_NEW)
### IMPORTS FROM OTHER EXAMPLE SCRIPTS
from ex04_prep_aa_imglist import prepare_aa_image_list

PCS = LINES[0] 

### SCRIPT OPTONS  
PYRLEVELS = [1]
PLUME_VELO_GLOB = 4.29 #m/s
PLUME_VELO_GLOB_ERR = 1.5
# applies multi gauss fit to retrieve local predominant displacement 
# direction, if False, then the latter is calculated from 1. and 2. moment
# of histogram (Faster but more sensitive to additional peaks in histogram)
HISTO_ANALYSIS_MULTIGAUSS = [True, False]

VELO_MODES = od([
# =============================================================================
#                 (  "set1"      ,   {"glob":True,
#                                  "flow_hybrid":False}),
#                 ("set2"      ,   {"glob":False,
#                                  "flow_hybrid":True}),
# =============================================================================
                ("set3"      ,   {"glob":True,
                                 "flow_raw":True,
                                 "flow_histo":True,
                                 "flow_hybrid":True})])

#molar mass of SO2
MMOL = 64.0638 #g/mol
# minimum required SO2-CD for emission-rate retrieval
CD_MIN = 5e16

START_INDEX = 10
STOP_INDEX = 30
DO_EVAL = True

# DOAS calibration results from example script 6
CALIB_FILE = join(SAVE_DIR, "ex06_doascalib_aa.fts")

# AA sensitivity correction mask retrieved from cell calib in script 7
CORR_MASK_FILE = join(SAVE_DIR, "ex07_aa_corr_mask.fts")
    

def avg_computation_time_image_load(lst, start_idx=0, stop_idx=20):
    cidx = lst.cfn
    lst.goto_img(start_idx)
    counter = 0
    t0 = time()
    for idx in range(start_idx, stop_idx):
        lst.next_img()
        counter += 1
    delt = time() - t0
    print "Total time: %.2f s, per image: %.2f" %(delt, delt/counter)
    lst.goto_img(cidx)
    return (delt, counter)

def print_result_times(dic):
    for val, item in dic.iteritems():
        for plevel, velo_item in item.iteritems():
            for velo_id, res in velo_item.iteritems():
                print ("HISTO_FIT: %s, PYRLEVEL: %d, VELO_ID: %s\n"
                       "TIME: %.2f s (Mean: %.2f kg/s)"
                       %(val, plevel, velo_id, res[0], res[1]))
### SCRIPT MAIN FUNCTION    
if __name__ == "__main__":
    close("all")
    figs = []
    if not exists(CALIB_FILE):
        raise IOError("Calibration file could not be found at specified "
            "location:\n%s\nPlease run example 6 first")
    if not exists(CORR_MASK_FILE):
        raise IOError("Cannot find AA correction mask, please run example script"
            "7 first") 
    
    result_times = od()
    
    ### Load AA list
    aa_list = prepare_aa_image_list() #includes viewing direction corrected geometry
    
    
    ### Load DOAS calbration data and FOV information (see example 6)
    doascalib = pyplis.doascalib.DoasCalibData()
    doascalib.load_from_fits(file_path=CALIB_FILE)
    doascalib.fit_calib_polynomial()
    
    #Load AA corr mask and set in image list(is normalised to DOAS FOV see ex7)
    aa_corr_mask = pyplis.Img(CORR_MASK_FILE)
    aa_list.aa_corr_mask = aa_corr_mask
    
    #set DOAS calibration data in image list
    from time import time
    aa_list.calib_data = doascalib
    if DO_EVAL:
        for val in HISTO_ANALYSIS_MULTIGAUSS:
            result_times[val] = od()
            for pyrlevel in PYRLEVELS:
                result_times[val][pyrlevel] = od()
                # convert the retrieval line to the specified pyramid level (script option)
                pcs = PCS.convert(to_pyrlevel=pyrlevel)
                aa_list.pyrlevel = pyrlevel
                ana = pyplis.EmissionRateAnalysis(imglist=aa_list, 
                                                  pcs_lines=pcs,
                                                  velo_glob=PLUME_VELO_GLOB,
                                                  velo_glob_err=PLUME_VELO_GLOB_ERR)
                ana.settings.velo_dir_multigauss = val
                ana.settings.min_cd = CD_MIN
                fig, ax = subplots(1,1)
                ax = ana.plot_pcs_lines(ax=ax)
                ax.set_title("")
                fig.savefig(join(SAVE_DIR_NEW, "ex12_histo-%d_Pyr%d.%s" 
                                        %(int(val), pyrlevel, FORMAT)),
                                        format=FORMAT, dpi=DPI)
                try:
                    del fig
                except:
                    pass
                for velo_set_id, velo_setting in VELO_MODES.iteritems():
                    print "HISTO: %s, PYRLEVEL: %s, VELO_SET: %s" %(val, pyrlevel, 
                                                                    velo_set_id)
                    
                           
                    aa_list.goto_img(0)
                    for k, v in velo_setting.iteritems():
                        if not ana.settings.velo_modes.has_key(k):
                            raise KeyError(k)
                        ana.settings.velo_modes[k]=v
                    
                    t0=time()
                    
                    ana.run_retrieval(start_index=START_INDEX, 
                                          stop_index=STOP_INDEX)
                    
                    mean = od()
                    for vm in ana.settings.velo_modes:
                        if vm in velo_setting and velo_setting[vm]:
                            try:
                                res = ana.get_results(pcs.line_id,
                                                      velo_mode=vm)
                                mean = res.nanmean()
                            except:
                                mean = -999999.99
                    
                    result_times[val][pyrlevel][velo_set_id] = [time()-t0, mean]
    try:
        print_result_times(result_times)
    except Exception as e:
        print repr(e)
  
def time_next_image(aa_list):
    t0=time()
    aa_list.next_img()
    dt = time()-t0
    print "Elapsed time: %.3f s" %(dt)
    aa_list.prev_img()
    return dt

import numpy as np

def check_performance_optflow(aa_list):
    dt0 = time_next_image(aa_list)
    
    aa_list.optflow_mode = True
    
    tot = time_next_image(aa_list)
    diff = tot - dt0
    diff_percent = diff/tot*100
    print ("PYRLEVEL: %d\n"
           "BLUR: %d\n"
           "TOTAL TIME: %.3f s\n"
           "Percentage optflow = %.2f" 
           %(aa_list.pyrlevel, aa_list.gaussian_blurring, tot, 
             diff_percent))
    
    aa_list.optflow_mode = False
    return (dt0, diff, diff_percent, tot)

blur_facs = [0,10]
pyrlevels = [0,1,2]

res = np.ndarray(shape=(len(blur_facs)*len(pyrlevels), 6))

c = 0
for bl in blur_facs:
    aa_list.gaussian_blurring = bl
    for pl in pyrlevels:
        aa_list.pyrlevel = pl
        dt0, diff, diff_pc, tot = check_performance_optflow(aa_list)
        
        res[c] = [aa_list.gaussian_blurring, aa_list.pyrlevel, dt0, diff,
           diff_pc, tot]
        c+=1
        
go=0
if go:    
    print "PYRLEVEL 0"
    aa_list.pyrlevel=0   
    print "Calib mode"
    avg_computation_time_image_load(aa_list)
    
# =============================================================================
#     aa_list.aa_mode=True
#     print "AA mode"     
#     avg_computation_time_image_load(aa_list)
#     
#     print "RAW mode"
#     aa_list.aa_mode=False
#     avg_computation_time_image_load(aa_list)
#     
#     aa_list.calib_mode=True
#     print "PYRLEVEL 1"
#     aa_list.pyrlevel=1   
#     print "Calib mode"
#     avg_computation_time_image_load(aa_list)
#     
#     aa_list.aa_mode=True
#     print "AA mode"     
#     avg_computation_time_image_load(aa_list)
#     
#     print "RAW mode"
#     aa_list.aa_mode=False
#     avg_computation_time_image_load(aa_list)
# =============================================================================
