# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 10:52:27 2017

@author:
Maximilian N. Guenther
Battcock Centre for Experimental Astrophysics,
Cavendish Laboratory,
JJ Thomson Avenue
Cambridge CB3 0HE
Email: mg719@cam.ac.uk
"""


###########################################################################
#::: import standard/community packages
########################################################################### 
import os
import numpy as np
import matplotlib.pyplot as plt


###########################################################################
#::: import my custom packages
########################################################################### 
from mytools import lightcurve_tools


###########################################################################
#::: import sub-packages
########################################################################### 
#import stacked_images
import plotting



#def load_stacked_image(C):
#    '''
#    C              centroid class, passed over as 'self' from centroiding.py
#    '''
#    
#    refcatdir = 'RefCatPipe*' + C.fieldname + 
#    filename = glob.glob( os.path.join( C.root, 'DITHERED_STACK_'+fieldname+'*.fits' ) )[-1]
#    RefCatPipe_P.5046627_F.NG1318-4500_C.811_A.118433_T.REFCAT1706A
#    data = fitsio.read( C.stacked_image_filename )
    
    

###########################################################################
#::: plot
########################################################################### 
def plot(C):
    '''
    C      centroid class, passed over as 'self' from centroiding.py
    '''
    if C.dic_blends is not None:
        N = len(C.dic_blends['OBJ_ID']) + 1
        
        fig, axes = plt.subplots( N, 3, figsize=(15,N*4), sharey='col' )
        
        for i in range(N):
            j = i-1
            
            #::: plot CCD locations of target and all neighbours
            axes[i,0].plot( C.dic['CCDX_0'], C.dic['CCDY_0'], 'bo', ms=12 )
            axes[i,0].plot( C.dic_blends['CCDX_0'], C.dic_blends['CCDY_0'], 'k.' )
            if i==0:
                axes[i,0].plot( C.dic['CCDX_0'], C.dic['CCDY_0'], 'ro', ms=12 )            
            else:
                axes[i,0].plot( C.dic_blends['CCDX_0'][j], C.dic_blends['CCDY_0'][j], 'ro', ms=12 )
            axes[i,0].set( xlim=[ C.dic['CCDX'][0]-9, C.dic['CCDX'][0]+9 ], ylim=[ C.dic['CCDY'][0]-9, C.dic['CCDY'][0]+9 ],
                           xlabel='CCD x', ylabel='CCD y' )        
            circle1 = plt.Circle((C.dic['CCDX_0'], C.dic['CCDY_0'],), 3, color='r', fill=False, linewidth=3)
            axes[i,0].add_artist(circle1)
            axes[i,0].set_aspect('equal')
            
            #::: plot phase folded lightcurve of selected neighbour
            if i==0:
                hjd_phase, flux_phase = C.dic['HJD_PHASE'], C.dic['SYSREM_FLUX3_PHASE']
            else:
                hjd_phase, flux_phase, _, _, _ = lightcurve_tools.phase_fold(C.dic_blends['HJD'][j,:], C.dic_blends['SYSREM_FLUX3'][j,:], C.dic['PERIOD'], C.dic['EPOCH'], dt = C.dt, ferr_type='meansig', ferr_style='sem', sigmaclip=True)
                flux_phase /= np.nanmedian(flux_phase[ (hjd_phase<0.15) | ( (hjd_phase>0.35) & (hjd_phase<0.65) ) | (hjd_phase>0.85) ])
            #::: mask upwards outliers
            flux_phase[ flux_phase>1.1 ] = np.nan
            axes[i,1].plot( hjd_phase, flux_phase, 'bo', rasterized=True )
            axes[i,1].set( xlim=[-0.25,0.75], xlabel='Phase', ylabel='Flux' )
           
            #::: plot info page
            if i==0:
                plotting.plot_target_info_text(axes[i,2], C)
            else:
                plotting.plot_neighbour_info_text(axes[i,2], C, j)
            
        plt.tight_layout()
        
        
        
    else:
        fig, ax = plt.subplots( 1, 1, figsize=(15,4) )
        ax.set_xlim([0,1])
        ax.set_ylim([0,1])
        ax.axis('off')
        ax.text(0.5,0.5,'No blending objects resolved in NGTS',ha='center',va='center')
        
        
        
    outfilename = os.path.join( C.outdir, C.fieldname + '_' + C.obj_id + '_' + C.ngts_version + '_blends.pdf' )   
    plt.savefig( outfilename )
    
        
        
        

    