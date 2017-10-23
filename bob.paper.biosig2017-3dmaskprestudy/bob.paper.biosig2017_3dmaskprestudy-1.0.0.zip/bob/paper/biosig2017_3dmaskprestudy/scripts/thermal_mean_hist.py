#!/usr/bin/env python
# encoding: utf-8
# Sushil Bhattacharjee <sushil.bhattacharjee@idiap.ch>
# Tue 19 Sep 17:34:23 CEST 2015


import os, sys
import argparse
import numpy as np
import math

from PIL import Image
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as P
    
    
def load_data(image_file, face_loc_file):
    ''' returns image, and face-location parameters loaded from provided input files'''
    inpimage = np.array(Image.open(image_file))
    fileptr = open(face_loc_file, 'r')
    info = fileptr.readlines()

    values = read_framing_paramsfile(face_loc_file)
    return (inpimage, values)


def extract_face_region(inpimage, location_values):
    '''returns face-region, extracted from provided input-image, according to the input location-values'''
    outer_width, outer_height, offset_x, offset_y, inner_width, inner_height  = location_values
    center_x = offset_x + outer_width/2
    center_y = offset_y + outer_height/2
    inner_x = center_x - inner_width/2
    inner_y = center_y - inner_height/2
    
    return inpimage[inner_y:inner_y+inner_height, inner_x:inner_x+inner_width]
    


def plot_stats(stats, labels, plot_file=None):
    '''produces a plot of a histogram from the given parameters. Saves the plot in a file, if plot_file is specified.
    Inputs:
    stats: gray-level statistics, to be used to construct histograms
    labels: contains 1s and 0s. 0 identifies bona-fide (no mask) class (for green histogram), and 1 indicates attack (mask) class.
    plot_file: full-path for filename (including '.pdf') where the generated plot will be stored in pdf format. 
                If plot_file is specified as None, the plot is displayed on the screen.
    '''
    fig=P.figure(figsize=(5,4))

    pos = stats[np.where(labels==0)]
    neg = stats[np.where(labels==1)]
   
    mybins = 256
    scoresRange= (0,255)
    histoargs = {'bins': mybins, 'alpha': 0.5, 'histtype': 'step', 'range': scoresRange} 
    lineargs = {'alpha': 0.5}
    #axis_fontsize = 8

    # for the development set
    P.subplot(1,1,1)
    P.hist(pos, bins=mybins, histtype='stepfilled', range=scoresRange, label='Bona fide', color='g', stacked=False)
    P.hist(neg, bins=mybins, histtype='stepfilled', range=scoresRange, label='Attacks', color='r', stacked=False)

    _, _, ymax, ymin = P.axis()

    P.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0.)
    P.grid(True, alpha=0.5)
    P.ylabel('count')
    P.xlabel('gray levels')
    
    if plot_file:
        with PdfPages(plot_file) as pdf:
            pdf.savefig(fig)
    else:
        P.show()


def read_framing_paramsfile(full_faceloc_filename):
    ''' returns the face-location parameters from the input file'''
    fileptr = open(full_faceloc_filename, 'r')
    info = fileptr.readlines()
    values = []
    [values.append(int(l.strip().split( )[-1])) for l in info if l.strip() is not '']
    
    return values
    

def construct_argument_list():
    '''creates a parser for command-line arguments.'''
    
    argParser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    argParser.add_argument('-ip', '--input_path', dest='inPath', default = None,
       help='path for input face-image files.')
    
    argParser.add_argument('-op', '--output_path', dest='outPath', default = None,
       help='path for output file containing plot.')


    return argParser


def main(command_line_parameters=None):
    ''' program to plot the histogram of projection-profile statistics for thermal face-images with and without masks'''
     
    argParser = construct_argument_list()
    args = argParser.parse_args(command_line_parameters)
    
    if not args.inPath: argParser.error('Specify parameter --input_path')
    if not args.outPath: argParser.error('Specify parameter --output_path')
    
    data_root = args.inPath
    if data_root[-1] != '/':
        data_root = data_root + '/'

    face_loc_file = '/Framing_parameters.txt'
    
    plot_root = args.outPath
    if plot_root[-1] != '/':
        plot_root = plot_root + '/'
    
    user_list = ['subject1/', 'subject2/','subject3/','subject4/']
    mask_list = ['no_mask', 'rigid_1_0', 'rigid_1_1', 'rigid_1_2', 'rigid_0_0', 'rigid_0_1', 'rigid_0_2']
    
    labels = []
    stats = None
    for u, user in enumerate(user_list):
        for i, mask in enumerate(mask_list):
            if i==0:
                limit = 6   #take more frames (6) for 'no_mask' category than for the other categories, to have approx. same number of samples in the 2 categories
            else:
                limit= 2
            for fn in range(1,limit):
                mask_file = data_root+user+mask+'/png/frameIR'+str(fn)+'.png'
                mask_face_loc = data_root+user+mask+face_loc_file
            
                mask_image, values = load_data(mask_file, mask_face_loc)
                mask_face_region = extract_face_region(mask_image, values) 
                mask_stats = np.mean(mask_face_region)

                
                if stats is None:
                    stats = mask_stats
                else:
                    stats = np.vstack((stats, mask_stats))
                    
                if i == 0:
                    labels.append(0)
                else:
                    labels.append(1)
            
    labels=np.array(labels)

    plot_file = plot_root+'thermal_profile_hist.pdf'
    plot_stats(stats, labels, plot_file)



'''
main entry point.
'''
if __name__ == '__main__':
    main(sys.argv[1:])
    
