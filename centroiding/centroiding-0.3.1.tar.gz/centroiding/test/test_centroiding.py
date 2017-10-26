# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 13:54:17 2017

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
import sys, timeit




NGTSIO_PATH = '/Users/mx/Data/Studium_aktuelles/PhD/NGTS/NGTSIO/'
if not NGTSIO_PATH in sys.path:
    sys.path.insert(0,NGTSIO_PATH)
    
CENTROIDING_PATH = '/Users/mx/Data/Studium_aktuelles/PhD/NGTS/CENTROIDING/centroiding_pip/'
if not CENTROIDING_PATH in sys.path:
    sys.path.insert(0,CENTROIDING_PATH)

#import ngtsio   
#import centd

#::: load pip centroiding
from ngtsio import ngtsio
from centroiding import centd




############################################################################
##::: MAIN
############################################################################             
if __name__ == '__main__':    
    
#    dic = ngtsio.get('NG0304-1115', ['PERIOD','EPOCH','WIDTH'], obj_id='012118', ngts_version='TEST18')
#    print dic
    fname = '/Users/mx/Big_Data/BIG_DATA_NGTS/2016/TEST18/NG0304-1115_809_2016_TEST18.fits'
    centd.identify('NG0304-1115', '012118', 'TEST18',
                   source='pipeline', fname_BLSPipe_megafile=fname,
                   outfname_info='testpipe', outfname_plot='testpipe',
                   user_period=66797.748228236189, user_width=12598.531879587919,
                   user_epoch=58118238.0)  
                   
                   
                   
    
    
#    fname = '/Users/mx/Data/Studium_aktuelles/PhD/NGTS/CENTROIDING/centroiding_pip/centroiding/test/input/candidates_TEST18_20170707.txt'
#    centd.identify_list( fname )



############################################################################
##::: MAIN
############################################################################             
#if __name__ == '__main__':
#    
#    start = timeit.default_timer()
#    if len(sys.argv) == 1:
#        #::: TEST candidate
#        C = centroid('NG0304-1115', '019780', ngts_version='TEST18', user_period=69260.3241759, user_epoch=58102726.652, user_width=0.1*69260.3241759, dt=0.001)  
#        C.run()
#        
#    elif len(sys.argv) == 3:
#        print 'Input:', sys.argv[1], sys.argv[2]
#        C = centroid(str(sys.argv[1]), str(sys.argv[2]), show_plot=True)  
#        C.run()
#        
#    elif len(sys.argv) == 4:
#        print 'Input:', sys.argv[1], sys.argv[2], sys.argv[3]
#        C = centroid(str(sys.argv[1]), str(sys.argv[2]), ngts_version=str(sys.argv[3]) )  
#        C.run()
#    elif len(sys.argv) == 5:
#        print 'Input:', sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
#        C = centroid(str(sys.argv[1]), str(sys.argv[2]), ngts_version=str(sys.argv[3]), user_period=float(sys.argv[4]) )  
#        C.run()
#        
#    elif len(sys.argv) == 6:
#        print 'Input:', sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
#        C = centroid(str(sys.argv[1]), str(sys.argv[2]), ngts_version=str(sys.argv[3]), user_period=float(sys.argv[4]), user_epoch=float(sys.argv[5]) )
#        C.run()
#        
#    elif len(sys.argv) == 7:
#        print 'Input:', sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
#        C = centroid(str(sys.argv[1]), str(sys.argv[2]), ngts_version=str(sys.argv[3]), user_period=float(sys.argv[4]), user_epoch=float(sys.argv[5]), user_width=float(sys.argv[6]) )
#        C.run()        
#        
#    print 'execution time:', timeit.default_timer() - start