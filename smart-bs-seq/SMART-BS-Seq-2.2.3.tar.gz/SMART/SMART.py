#!/usr/bin/env python
# Time-stamp: <2017-07-09 16:39:00 Hongbo Liu>

"""Description: SMART main executable

Copyright (c) 2017 Hongbo Liu <hongbo919@gmail.com>

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD License (see the file COPYING included
with the distribution).

@status: release candidate
@version: 2.2.3
@author:  Hongbo Liu
@contact: hongbo919@gmail.com
"""
# ------------------------------------
# python modules
# Add "SMART." before "DeNovoDMR_Calling import DeNovoDMR_Calling"
# Add "SMART." before "Segmentation import Segmentation"
# cd bin
# dos2unix SMART
# ------------------------------------
import time
import os
import sys
import argparse
from SMART.DeNovoDMR_Calling import DeNovoDMR_Calling
from SMART.Segmentation import Segmentation

def restricted_float_M(x):
    x = float(x)
    if x < 0.01 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.01, 1.0]"%(x,))
    return x

def restricted_float_G(x):
    x = float(x)
    if x < 0.5 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.5, 1.0]"%(x,))
    return x

def restricted_float_Methylation_Specificity(x):
    x = float(x)
    if x < 0.2 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.2, 1.0]"%(x,))
    return x

def restricted_float_Euclidean_Distance(x):
    x = float(x)
    if x < 0.2 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.01, 0.5]"%(x,))
    return x

def restricted_float_Similarity_Entropy(x):
    x = float(x)
    if x < 0.2 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.01, 1.0]"%(x,))
    return x

def restricted_int_CpG_Distance(x):
    x = int(x)
    if x < 1 or x > 2000:
        raise argparse.ArgumentTypeError("%r not in range [1, 2000]"%(x,))
    return x

def restricted_int_DLThreshold(x):
    x = int(x)
    if x < 1:
        raise argparse.ArgumentTypeError("%r should be larger than 1 bp"%(x,))
    return x

def restricted_int_pThreshold(x):
    x = float(x)
    if x < 0 or x > 1:
        raise argparse.ArgumentTypeError("%r should be between 0 and 1"%(x,))
    return x

# ------------------------------------
# Main function
# ------------------------------------
def main(argv):
    """The Main function/pipeline for SMART.
    """
    # Parse options...
    description = "%(prog)s 2.2 -- Specific Methylation Analysis and Report Tool for BS-Sequencing Data"
    epilog = "For any help, type: %(prog)s -h, or write to Hongbo Liu (hongbo919@gmail.com)"
    parser = argparse.ArgumentParser(description = description, epilog = epilog)
    parser.add_argument("MethylMatrix", type = str, default = '',
                        help = "The input methylation file (such as /WGBS/MethylMatrix.txt) including methylation values in all samples to compare (REQUIRED). The methylation data should be arranged as a matrix in which each row represents a CpG site. The columns are tab-separated. The column names should be included in the first line, with the first three columns representing the location of CpG sites: chrom, start, end. The methylation values starts from the fourth column. And the methylation value should be between 0 (unmethylated) to 1 (fully methylated). The missing values should be shown as -. The names of samples should be given as G1_1,G1_2,G2_1,G2_2,G3_1,G3_2,G3_3, in which Gi represents group i. \nThe Methylation matrix can be build based on bed files (chrom start end betavalue) by bedtools as: bedtools unionbedg -i G1_1.bed G1_2.bed G2_1.bed  G2_2.bed  G3_1.bed   G3_2.bed   G3_3.bed -header -names G1_1 G1_2 G2_1 G2_2 G3_1 G3_2 G3_3 -filler - > MethylMatrix.txt. The example data is also available at http://fame.edbc.org/smart/Example_Data_for_SMART2.zip. [Type: file]")
    parser.add_argument("-t", dest='Project_Type',type = str, choices=['DeNovoDMR','DMROI','DMC','Segment'], default = 'DeNovoDMR',
                        help = "Type of project including 'DeNovoDMR','DMROI','DMC' and 'Segment'. DeNovoDMR means de novo identification of differentially methylated regions (DMRs) based on genome segmentation. DMROI means the comparison of the methylation difference in regions of interest (ROIs) across multiple groups. DMC means identification of differentially methylated CpG sites (DMCs). It should be noted DMC is time-consuming for whole-genome methylation data. Segment means de novo segmentation of genome based on DNA methylation in all samples. DEFAULT: \'DeNovoDMR\' [Type: string]")
    parser.add_argument("-r", dest='Region_of_interest',type = str, default = '',
                        help = "Genome regions of interest in bed format without column names (such as /WGBS/Regions_of_interest.bed) for project type DMROI (REQUIRED only for DMROI). The regions in the file should be sorted by chromosome and then by start position (e.g., sort -k1,1 -k2,2n in.bed > in.sorted.bed). If this file is provided, SMART treat each region as a unit and compare its mean methylation across groups by methylation specificity and ANOVA analysis. This parameter is only for project type DMROI. DEFAULT: \'\' [Type: string]")
    parser.add_argument("-n", dest='Project_Name',type = str, default = "SMART",
                        help = "Project name, which will be used to generate output file names. This parameter is for all project types. DEFAULT: \"SMART\" [Type: string]")
    parser.add_argument("-o", dest='Output_Folder',type = str, default = '',
                        help = "The folder in which the result will be output. If specified all output files will be written to that directory. This parameter is for all project types. [Type: folder] [DEFAULT: the directory named using project name and current time (such as SMART20140801132559) in the current working directory]")
    parser.add_argument("-MR", dest='Miss_Value_Replace',type = restricted_float_M, default = 0.5,
                        help = "Replace the missing value with the mediate methylation value of available samples in the corresponding group. The user can control whether to replace missing value by setting this parameter from 0.01 (meaning methylation values are available in at least 1%% of samples in a group) to 1.0 (meaning methylation values are available in 100%% of samples in a group, i.e there is no missing values). This parameter is for all project types. [Type: float] [Range: 0.01 ~ 1.0] [DEFAULT: 0.5]")
    parser.add_argument("-AG", dest='Percentage_of_Available_Groups',type = restricted_float_M, default = 1.0,
                        help = "Percentage of available groups after missing value replacement. The user can use this parameter to filter CpG sites those have not enough available methylation levels by setting this parameter from 0.01 (meaning methylation values are available in at least 1%% of groups) to 1.0 (meaning methylation values are available in 100%% of groups, i.e there is no missing values). This parameter is for all project types. [Type: float] [Range: 0.01 ~ 1.0] [DEFAULT: 1.0]")
    parser.add_argument("-MS", dest='Methylation_Specificity',type = restricted_float_Methylation_Specificity, default = 0.5,
                        help = "Methylation Specificity Threshold for DMC or DMR calling. This parameter can be used to identify DMC or DMR as the the CpG site or region with methylation specificity which is greater than the threshold. This parameter is for all project types. [Type: float] [Range: 0.2 ~ 1.0] [DEFAULT: 0.5]")
    parser.add_argument("-ED", dest='Euclidean_Distance',type = restricted_float_Euclidean_Distance, default = 0.2,
                        help = "Euclidean Distance Threshold for methylation similarity between neighboring CpGs which is used in genome segmentation and de novo identification of DMR. The methylation similarity between neighboring CpGs is high if the Euclidean distance is less than the threshold. This parameter is only for project types DeNovoDMR and Segment. [Type: float] [Range: 0.01 ~ 0.5] [DEFAULT: 0.2]")
    parser.add_argument("-SM", dest='Similarity_Entropy',type = restricted_float_Similarity_Entropy, default = 0.6,
                        help = "Similarity Entropy Threshold for methylation similarity between neighboring CpGs which is used in genome segmentation and de novo identification of DMR. The methylation similarity between neighboring CpGs is high if similarity entropy is less than the threshold. This parameter is only for project types DeNovoDMR and Segment. [Type: float] [Range: 0.01 ~ 1.0] [DEFAULT: 0.6]")
    parser.add_argument("-CD", dest='CpG_Distance',type = restricted_int_CpG_Distance, default = 500,
                        help = "CpG Distance Threshold for the maximal distance between neighboring CpGs which is used in genome segmentation and de novo identification of DMR. The neighboring CpGs will be merged if the distance less than this threshold. This parameter is only for project types DeNovoDMR and Segment. [Type: int] [Range: 1 ~ 2000] [DEFAULT: 500]")
    parser.add_argument("-CN", dest='CpG_Number',type = restricted_int_DLThreshold, default = 5,
                        help = "Segment CpG Number Threshold for the minimal number of CpGs of merged segment and de novo identified DMR. The segments/DMRs with CpG number larger than this threshold will be output for further analysis. This parameter is only for project types DeNovoDMR and Segment. [Type: int] [Range: > 1] [DEFAULT: 5]")
    parser.add_argument("-SL", dest='Segment_Length',type = restricted_int_DLThreshold, default = 20,
                        help = "Segment Length Threshold for the minimal length of merged segment and de novo identified DMR. The segments/DMRs with a length larger than this threshold will be output for further analysis. This parameter is only for project types DeNovoDMR and Segment. [Type: int] [Range: > 1] [DEFAULT: 20]")
    parser.add_argument("-PD", dest='p_DMR',type = restricted_int_pThreshold, default = 0.05,
                        help = "p value of one-way analysis of variance (ANOVA) which is carried out for identification of DMCs or DMRs across multiple groups. The segments with p value less than this threshold are identified as DMC or DMR. This parameter is for all project types. [Type: float] [Range: 0 ~ 1] [DEFAULT: 0.05]")
    parser.add_argument("-PM", dest='p_MethylMark',type = restricted_int_pThreshold, default = 0.05,
                        help = "p value of one sample t-test which is carried out for identification of Methylation mark in a specific group based on the identified DMRs. The DMRs with p value less than this threshold is identified as group- specific methylation mark (Hyper methylation mark or Hypo methylation mark). This parameter is only for project types DeNovoDMR and DMROI [Type: float] [Range: 0 ~ 1] [DEFAULT: 0.05]")
    parser.add_argument("-v", "--version",dest='version',action='version', version='SMART 2.2.3')
        
    UserArgs = parser.parse_args()
    MethyData=UserArgs.MethylMatrix
    Project_Type=UserArgs.Project_Type
    Region_of_interest=UserArgs.Region_of_interest
    Project_Name=UserArgs.Project_Name
    OutFolder=UserArgs.Output_Folder
    Miss_Value_Replace=UserArgs.Miss_Value_Replace
    Percentage_of_Available_Groups=UserArgs.Percentage_of_Available_Groups
    Methylation_Specificity=UserArgs.Methylation_Specificity
    Euclidean_Distance=UserArgs.Euclidean_Distance
    Similarity_Entropy=UserArgs.Similarity_Entropy
    CpG_Distance=UserArgs.CpG_Distance
    CpG_Number=UserArgs.CpG_Number
    Segment_Length=UserArgs.Segment_Length
    p_DMR=UserArgs.p_DMR
    p_MethylMark=UserArgs.p_MethylMark
    UserArgslist = str(vars(UserArgs))
    
    if (MethyData==''):
        sys.exit( "[Error:] Methylation data is needed. Please re-run it giving the location of the methylation data.")
    if (MethyData):
        if not os.path.exists( MethyData ):
                sys.exit( "[Error:] Methylation data directory (%s) could not be found. Please re-run it giving the correct location of the methylation data." % MethyData )
                
        if (OutFolder==''):
            homedir = os.getcwd()
            Starttime=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
            OutFolder=homedir+"/"+Project_Name+Starttime+"/"
            #print OutFolder
        if OutFolder:
            # use a output directory to store SMART output
            if OutFolder[-1]!='/':
                OutFolder=OutFolder+'/'
            
            if not os.path.exists( OutFolder ):
                try:
                    os.makedirs( OutFolder )
                except:
                    sys.exit( "[Error:] Output directory (%s) could not be created. Terminating program." % OutFolder )            
        
                
        if Project_Type == 'DeNovoDMR':
            DeNovoDMR_Callingrun=DeNovoDMR_Calling()
            DeNovoDMR_Callingrun.runDeNovo(UserArgslist,MethyData,Project_Name,Miss_Value_Replace,Percentage_of_Available_Groups,Methylation_Specificity,Euclidean_Distance,Similarity_Entropy,CpG_Distance,CpG_Number,Segment_Length,p_DMR,p_MethylMark,OutFolder)
        elif Project_Type == 'DMROI':
            if (Region_of_interest==''):
                sys.exit( "[Error:] Genome Regions is needed. Please re-run it giving the location of the bed file for Genome Regions.")
            if (Region_of_interest):
                if not os.path.exists( Region_of_interest ):
                        sys.exit( "[Error:] Genome Regions file (%s) could not be found. Please re-run it giving the correct location of the bed file for Genome Regions." % Region_of_interest )
            DeNovoDMR_Callingrun=DeNovoDMR_Calling()
            DeNovoDMR_Callingrun.runDMROI(UserArgslist,MethyData,Project_Name,Miss_Value_Replace,Percentage_of_Available_Groups,Region_of_interest,Methylation_Specificity,Euclidean_Distance,Similarity_Entropy,CpG_Distance,CpG_Number,Segment_Length,p_DMR,p_MethylMark,OutFolder)        
        elif Project_Type == 'DMC':
            DeNovoDMR_Callingrun=DeNovoDMR_Calling()
            DeNovoDMR_Callingrun.runDMC(UserArgslist,MethyData,Project_Name,Miss_Value_Replace,Percentage_of_Available_Groups,Methylation_Specificity,Euclidean_Distance,Similarity_Entropy,CpG_Distance,CpG_Number,Segment_Length,p_DMR,p_MethylMark,OutFolder)
        elif Project_Type == 'Segment':
            Segmentationrun=Segmentation()
            Segmentationrun.runSegment(UserArgslist,MethyData,Project_Name,Miss_Value_Replace,Percentage_of_Available_Groups,Methylation_Specificity,Euclidean_Distance,Similarity_Entropy,CpG_Distance,CpG_Number,Segment_Length,p_DMR,p_MethylMark,OutFolder)
        else:
            sys.exit( "[Error:] Project Type (%s) is not supported. Please re-run it giving the correct project type 'DeNovoDMR','DMROI','DMC' or 'Segment'. " % Project_Type )
        


if __name__ == '__main__':
    main(sys.argv)
