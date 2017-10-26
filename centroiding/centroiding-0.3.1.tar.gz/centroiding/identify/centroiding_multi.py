# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 23:26:13 2016

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
import sys, os, warnings
import numpy as np
from itertools import izip
from centroiding import centroid


###########################################################################
#::: import my custom packages
########################################################################### 
from ngtsio import ngtsio




###########################################################################
#::: canvas or bls run (for all individual canvas targets)
###########################################################################              
def evaluate_all_fields_canvas(key, ngts_version, dt, cut=False):
    """
    EVALUATE ALL FIELDS' CANVAS OBJECTS
    """
    
    #::: create outdir and flagfile
    outdir = os.path.join( 'output', key+'_'+ngts_version+'_dt='+str(dt)+'_cut='+str(cut), '' )
    if not os.path.exists(outdir): os.makedirs(outdir)
    flagfile = initialize_flagfile(outdir)       
            
    #::: read in fieldnames
    fieldnames = np.genfromtxt('input/FIELD_LIST.txt', dtype=None)
    if not isinstance(fieldnames, np.ndarray): fieldnames = [fieldnames]
        
    #::: proceed in loop for each field
    for fieldname in fieldnames:
        print '###########################################################################'
        print fieldname
        print '###########################################################################'
        canvasbls_run(key, fieldname, ngts_version, dt, cut, outdir, flagfile)
#        except:
#            warnings.warn('Skipped because of problems.')   
            
            
            
def canvasbls_run(key, fieldname, ngts_version, dt, cut, outdir, flagfile):
    '''
    key: 'canvas' or 'bls'
    '''
    #:::
    if key=='canvas':
        depth_key = 'CANVAS_DEPTH'
    else:
        depth_key = 'DEPTH'
    
    #::: load canvas obj_id list
    objdic = ngtsio.get( fieldname, ['OBJ_ID', depth_key, 'FLUX_MEAN', 'CCD_X', 'CCD_Y'], obj_id=key, ngts_version=ngts_version, silent=True)
    '''
    (note that 'CCD_X' denotes the mean location, while 'CCDX' is the location per exposure)
    '''
    
    if objdic is None:
        warnings.warn(fieldname+' not existant on this server.')
    else:
        
        #::: depth cut-off
        if cut:
            depth_cut = -0.01 #1%
            flux_cut = 500. #min 500 ADU/s
            ccd_cut = 50. #at least 50 pixels away from the edge
            obj_ids = objdic['OBJ_ID'][ (objdic[depth_key] < depth_cut) & \
                                        (objdic['FLUX_MEAN'] > flux_cut) & \
                                        (objdic['CCD_X'] > ccd_cut) & \
                                        (objdic['CCD_X'] < (2048.-ccd_cut)) & \
                                        (objdic['CCD_Y'] > ccd_cut) & \
                                        (objdic['CCD_Y'] < (2048.-ccd_cut)) ]
        else:
            obj_ids = objdic['OBJ_ID']
        
        #::: run for all individually
        for i, obj_id in enumerate( obj_ids ):
            print '\n'
            print '###########################################################################'
            print i, '/', len(obj_ids), ',', obj_id
            print '###########################################################################'
            
            try:
                C = centroid(fieldname, obj_id, ngts_version=ngts_version, dt=dt, outdir=outdir, flagfile=flagfile)
                C.run()
            except:
                with open( flagfile, 'a+') as f: 
                    f.write('# '+fieldname+'\t'+obj_id+'\t'+'(broke)\n') 
                warnings.warn('Skipped because of problems.')   



###########################################################################
#::: candidate shortlist run
###########################################################################         
def evaluate_candidate_shortlist( fname, dt=0.005, outdir=None, mode='skipfiles' ):
    """
    EVALUATE ALL THE CANDIDATES E.G. FROM THE GOOGLE SPREADSHEET
    input must be an ascii (e.g. txt) file with four columns:
    fieldname obj_id ngts_version source
    source: BLS or CANVAS
    """
    
    #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    #::: load candidate list
    #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    data = np.genfromtxt(fname, names=['fieldnames', 'obj_ids', 'ngts_versions', 'source'], dtype=None) #dtype=['|S11','|S6',None])
    N_obj = len(data['obj_ids'])


    #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    #::: select output directory
    #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    if outdir is None:
        outdir = os.path.join( 'output', 'candidate_shortlists', os.path.basename(os.path.splitext(fname)[0]), 'dt='+str(dt) ) #no ending slash here (the ending slash will be added later)
    
    #if the dir already exists and mode==newdir, create it with suffix  
    if ( os.path.exists(outdir) & (mode=='newdir') ):
        
        i = 2
        outdir += '_' + str(i) #outdir_2
        while os.path.exists(outdir):
            i += 1
            outdir = outdir[0:-1] + str(i) #outdir_3, outdir_4, ...
  
        outdir = os.path.join( outdir, '' )
        os.makedirs(outdir)   
        
    #if the dir already exists and mode==skipfiles or replacefiles, do nothing 
    elif ( os.path.exists(outdir) & ( mode in ('skipfiles', 'replacefiles') ) ):
        pass
    
    #if the dir does not exists, create it
    elif ~os.path.exists(outdir):
        outdir = os.path.join( outdir, '' )
        os.makedirs(outdir)   
    

       
    #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    #::: if there's already a flagfile, rename it into flagfile_old
    #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    if (mode in ('skipfiles', 'replacefiles')) & (os.path.exists( os.path.join(outdir,'flagfile.txt') )):
        flagfile = os.path.join( outdir, 'flagfile.txt' )
        flagfile_old = os.path.join( outdir, 'flagfile_old.txt' )
        os.rename(flagfile, flagfile_old) #rename the original flagfile to flagfile_old
    else:
        pass
    
    
    #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    #::: create flagfile
    #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    flagfile = initialize_flagfile(outdir)
            
            
    #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    #::: loop over all candidates
    #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    i = 0
    for fieldname, obj_id, ngts_version, source in izip(data['fieldnames'], data['obj_ids'], data['ngts_versions'], data['source']):
        #::: load obj_id as string with leading zeros (for consistency in filenames)        
        obj_id = str(obj_id).zfill(6)
        i += 1
        print '###########################################################################'
        print str(i)+'/'+str(N_obj), fieldname, obj_id, ngts_version, source
        
        #check in flagfile_old if obj was already evaluated
        #if yes, copy it's results from flagfile_old
        #and write it into the new flagfile 
        oldline = None
        if (mode=='skipfiles') & (os.path.exists( os.path.join(outdir,'flagfile_old.txt') )):
            with open( flagfile_old, 'r' ) as of:
                for line in of:
                    if (fieldname in line) & (obj_id in line):
                        oldline = line
                        
        if oldline is not None:
            print "Skipped: object previously evaluated, flagfile entry already existant and mode=='skipfiles'."  
            with open( flagfile, 'a+') as f: 
                f.write( oldline ) 
        
        else:
            try:
                C = centroid(fieldname, obj_id, ngts_version=ngts_version, source=source, dt=dt, outdir=outdir, flagfile=flagfile, show_plot=False)
                C.run()
            except:
                with open( flagfile, 'a+') as f: 
                    f.write('#'+fieldname+'\t'+obj_id+'\t'+'(broke)\n') 
                print 'Skipped because of problems.'
        


###########################################################################
#::: initialize a flagfile
###########################################################################   
def initialize_flagfile(outdir):
    flagfile = os.path.join( outdir, 'flagfile.txt' )
    header = '#FIELDNAME' + '\t' +\
         'OBJ_ID' + '\t' +\
         'NGTS_VERSION' + '\t' +\
         'RA' + '\t' +\
         'DEC' + '\t' +\
         'CCDX_0' + '\t' +\
         'CCDY_0' + '\t' +\
         'FLUX_MEAN' + '\t' +\
         'CENTDX_fda_PHASE_RMSE' + '\t' +\
         'CENTDY_fda_PHASE_RMSE' + '\t' +\
         'CENTDX_fd_PHASE_RMSE' + '\t' +\
         'CENTDY_fd_PHASE_RMSE' + '\t' +\
         'CENTDX_f_PHASE_RMSE' + '\t' +\
         'CENTDY_f_PHASE_RMSE' + '\t' +\
         'CENTDX_PHASE_RMSE' + '\t' +\
         'CENTDY_PHASE_RMSE' + '\t' +\
         'RollCorrSNR_X' + '\t' +\
         'RollCorrSNR_Y' + '\t' +\
         'CrossCorrSNR_X' + '\t' +\
         'CrossCorrSNR_Y' + '\t' +\
         'Ttest_X' + '\t' +\
         'Ttest_Y' + '\t' +\
         'Binom_X' + '\t' +\
         'Binom_Y'
    with open( flagfile, 'w') as f:
        f.write(header+'\n')  
    return flagfile




###########################################################################
#::: MAIN
###########################################################################  
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Input file/command required.'
        
    if len(sys.argv) == 2:
        if sys.argv[1] in ['bls', 'canvas']:
            evaluate_all_fields_canvas(str(sys.argv[1]))
        else:
            evaluate_candidate_shortlist(str(sys.argv[1]), dt=0.005)
            evaluate_candidate_shortlist(str(sys.argv[1]), dt=0.0025)
            evaluate_candidate_shortlist(str(sys.argv[1]), dt=0.001)
            
    #sys.argv[2] is the mode 'newdir', skipfiles' or 'replacefiles'
    if len(sys.argv) == 3:
        if sys.argv[2] not in ('newdir', 'skipfiles', 'replacefiles'):
            warnings.warn("Aborted. Second argument has to be 'newdir', 'skipfiles', or 'replacefiles'.")
        else:
            if sys.argv[1] in ['bls', 'canvas']:
                evaluate_all_fields_canvas(str(sys.argv[1]))
            else:
                evaluate_candidate_shortlist(str(sys.argv[1]), dt=0.005, mode=sys.argv[2])
                evaluate_candidate_shortlist(str(sys.argv[1]), dt=0.0025, mode=sys.argv[2])
                evaluate_candidate_shortlist(str(sys.argv[1]), dt=0.001, mode=sys.argv[2])
            
    if len(sys.argv) == 5:
        'e.g. "bls TEST18 0.001 -0.01" means take BLS objects from TEST18, analyse for dt=0.001, and only select DEPTH<-0.01'
        if sys.argv[1] in ['bls', 'canvas']:
            evaluate_all_fields_canvas(str(sys.argv[1]), str(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
        else:
            raise ValueError('If passing three arguments, the first must be "bls" or "canvas", the second the desired dt value, and the third the desired depth cut-off.')
        
    
