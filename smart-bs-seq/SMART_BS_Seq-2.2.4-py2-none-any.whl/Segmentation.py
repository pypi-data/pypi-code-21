#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Time-stamp: <2017-07-09 16:39:00 Hongbo Liu>
'''
Modified on 2017.7.9

@author: Hongbo Liu

'''
import scipy.spatial.distance
import NewEntropy
import NewEntropyNormal
from scipy import stats
import numpy as np
import random
from multiprocessing import Pool
import time
import os
import sys
from collections import defaultdict
import statsmodels.api as sm
from statsmodels.formula.api import ols
import pandas as pd
from math import sqrt
import shutil

def multi_genome_segmentation(args):
        SmallSegmentNumChrome=Segmentation().GenomeSegmentMeanMethy_MultiProcess_Chrome(*args)
        return SmallSegmentNumChrome

def multi_final_results(args):
        Numdec=Segmentation().DeNovoFinalResult_MultiProgress_Chrome(*args)
        return Numdec       

class Segmentation():
    '''
    This module is only used for genome segmentation based on DNA methylation in multiple samples 
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
    def _chk_asarray(self, a, axis):
        if axis is None:
            a = np.ravel(a)
            outaxis = 0
        else:
            a = np.asarray(a)
            outaxis = axis
        return a, outaxis
    
    def MethySpecificity_Calculator_SMART2(self,PreviousMethydataSet,CurrentMethydataSet,Group_Key,AvailableGroup):
        Groups=Group_Key.keys()
        GroupNum=len(Groups)
        AvailableCommonGroupNum=0 #Number of groups in which at least one sample have methylation value
        PreviousMethydataSet_A=[]
        CurrentMethydataSet_A=[]
        MethySpecificity=-1
        SimilarityEntropyvalue=-1
        EucDistance=-1
        
        Methyentropy=NewEntropy.Entropy()
        
        for eachgroup in Groups:
            Samples_sameGroup=Group_Key[eachgroup]  #The samples in the same group
            for eachvalue_samegroup in Samples_sameGroup:
                if (PreviousMethydataSet[eachvalue_samegroup] != '-' and CurrentMethydataSet[eachvalue_samegroup] != '-'):
                    PreviousMethydataSet_A.append(float(PreviousMethydataSet[eachvalue_samegroup]))
                    CurrentMethydataSet_A.append(float(CurrentMethydataSet[eachvalue_samegroup]))
                    AvailableCommonGroupNum=AvailableCommonGroupNum+1
        if float(AvailableCommonGroupNum)/float(GroupNum) >=AvailableGroup: #Check whether there are enough values for entropy calculate
            EucDistance=scipy.spatial.distance.euclidean(PreviousMethydataSet_A, CurrentMethydataSet_A)/sqrt(AvailableCommonGroupNum)  #calculate the euclidean distance between the methylation leveles of current C and previous C
            EucDistance=("%.3f" % EucDistance)
            DifferMethydataSet=list(map(lambda x: abs(x[0]-x[1]), zip( PreviousMethydataSet_A, CurrentMethydataSet_A)))
            CurrentMethydataSet_A=tuple(CurrentMethydataSet_A)
            MethySpecificity=("%.3f" % (1.0-Methyentropy.EntropyCalculate(CurrentMethydataSet_A)))
            DifferMethydataSet=tuple(DifferMethydataSet)
            SimilarityEntropyvalue=("%.3f" % (1.0-Methyentropy.EntropyCalculate(DifferMethydataSet)))
            
        return MethySpecificity,SimilarityEntropyvalue,EucDistance
    
    def DataCheck_and_MissReplace(self,MethyData,MissReplace,AvailableGroup,MSthreshold,tmpDMCfolder,DMCmethyfile,p_DMR,statisticout):
        '''
        Split the BS-SEq data into chromes
        Select the CpG sites with methylation values in at least **% samples
        '''
        #RawMethyDataFolderName=MethyDataFolder+'*.wig'
        ChromeArray=[]
        SampleNames=[]
        TotalCpGNum=0
        AvailableCpGNum=0
        DMC_Num=0
        
        if tmpDMCfolder:
            # use a output directory to store Splited Methylation data 
            if not os.path.exists( tmpDMCfolder ):
                try:
                    os.makedirs( tmpDMCfolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % tmpDMCfolder )
   
        methyfile=open(MethyData,'rb') #open current methylation file
        filecontent=methyfile.readline()
        
        ###First line for sample information
        filecontent=filecontent.strip('\n')
        firstline=filecontent.split('\t')
        SampleNames=firstline[3:]
        SampleNum=len(SampleNames)
        Group_Key = defaultdict(list)
        Column_Key_Group = dict()
        sampleorder=0
        for sample in SampleNames:
            sample_info=sample.split('_')
            if len(sample_info)>=2 and sample_info[-1].isdigit():
                GroupName='_'.join(sample_info[0:-1])
                Group_Key[GroupName].append(sampleorder)
                Column_Key_Group[sampleorder] = GroupName
                sampleorder=sampleorder+1
            else:
                Group_Key[sample].append(sampleorder)
                Column_Key_Group[sampleorder] = sample
                sampleorder=sampleorder+1
        Group_Key_str = str(Group_Key)
        Column_Key_Group_str = str(Column_Key_Group)
        statisticout.write(Group_Key_str)
        statisticout.write(Column_Key_Group_str)
        Groups=Group_Key.keys()
        GroupNum=float(len(Groups))
        ChromeFirstlyOutline=filecontent+"\tMethySpecificity\tSimilarityEntropyvalue\tEucDistance\n"
        #DMCFirstlyOutline=filecontent+"\tMethySpecificity\tSimilarityEntropyvalue\tEucDistance\n"
        DMCmethyfile.write(ChromeFirstlyOutline)
        ###Process methylation data
        filecontent=methyfile.readline()
        CurrentStr='chr'
        ErrorRowNum=0
        FillMissNum=0
        while filecontent:
            TotalCpGNum=TotalCpGNum+1
            filecontent=filecontent.strip('\n')
            currentMeth=filecontent.split('\t')
            ###20170616: add function: Check whether the number of sample name equals the number of sample data
            if len(currentMeth) > len(firstline):
                print "[Warning] Row "+str(TotalCpGNum)+": Number of data columns is more than that of sample names!"
                ErrorRowNum=ErrorRowNum+1
                
            elif len(currentMeth) < len(firstline):
                print "[Warning] Row "+str(TotalCpGNum)+": Number of data columns is less than that of sample names!"
                ErrorRowNum=ErrorRowNum+1
            else:
                chrome=currentMeth[0]
                if chrome != CurrentStr:  #If search the new chrome,
                    ChromeArray.append(chrome)
                    CurrentStr=chrome
                    PreviousMethydataSet=[]
                    Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
                    print Starttime+" Start data check on: "+chrome
                    statisticout.write(Starttime+" Start data check on: "+chrome+"\n")
                    chromemethyfile=tmpDMCfolder+chrome+".txt"
                    #print chromemethyfile
                    chromemethyfile=open(chromemethyfile,'wb')
                    chromemethyfile.write(ChromeFirstlyOutline)
                # Data process
                CurrentMethydataSet=currentMeth[3:]
                ## Add missing value using the median value obtained the replicate samples 
                AvailableGroupNum=0 #Number of groups in which at least one sample have methylation value
                for eachgroup in Groups:
                    Samples_sameGroup=Group_Key[eachgroup]  #The samples in the same group
                    GroupSampleNum=float(len(Samples_sameGroup))
                    Valuelist=[]
                    MissValueNum=0
                    for eachvalue_samegroup in Samples_sameGroup:
                        if CurrentMethydataSet[eachvalue_samegroup] != '-':
                        ###20170616: add the data check for DNA methylation values
                            if(float(CurrentMethydataSet[eachvalue_samegroup]) >=0.0 and float(CurrentMethydataSet[eachvalue_samegroup]) <=1.0):
                                Valuelist.append(float(CurrentMethydataSet[eachvalue_samegroup]))
                            else:
                                print "[Warning] Row "+str(TotalCpGNum)+": Data filtering of methylation value that is out of range from 0.0 to 1.0!"
                        else:
                            MissValueNum=MissValueNum+1
                    NoneMissPercentage=float(len(Valuelist))/GroupSampleNum
                    if MissValueNum>0 and NoneMissPercentage >= MissReplace:  #There are enough available values in the samples of the same group
                        MedianValue=self.getMedian(Valuelist)  #Median value
                        MedianValue=("%.3f" % MedianValue)
                        for eachvalue_samegroup in Samples_sameGroup:
                            #print CurrentMethydataSet[eachvalue_samegroup]
                            if CurrentMethydataSet[eachvalue_samegroup] is '-':
                                #print MedianValue
                                CurrentMethydataSet[eachvalue_samegroup] = MedianValue
                                FillMissNum=FillMissNum+1
                    if len(Valuelist) > 0: # 
                        AvailableGroupNum=AvailableGroupNum+1
                        
                ##New methylation data after missing replacement
                MethylationNewList=CurrentMethydataSet
                Methydata=''
                for each in range(SampleNum):
                    MethylationNewList[each]=str(MethylationNewList[each])
                Methydata='\t'.join(MethylationNewList)
                filecontent=currentMeth[0]+"\t"+str(currentMeth[1])+"\t"+str(currentMeth[2])+"\t"+Methydata        
                    
                ## Calculate entropy value for the CpG sites with enough methylation values
                
                if float(AvailableGroupNum)/float(GroupNum) >= AvailableGroup: #Check whether there are enough values for entropy calculate
                    if len(PreviousMethydataSet)==0:
                        PreviousMethydataSet=CurrentMethydataSet
                    ### Entropy and similarity
                    MethySpecificity,SimilarityEntropyvalue,EucDistance = self.MethySpecificity_Calculator_SMART2(PreviousMethydataSet,CurrentMethydataSet,Group_Key,AvailableGroup)
                    
                    ### Determine DMC and output
                    if MethySpecificity >= 0:
                        AvailableCpGNum=AvailableCpGNum+1
                        Outline=filecontent+"\t"+str(MethySpecificity)+"\t"+str(SimilarityEntropyvalue)+"\t"+str(EucDistance)+"\n"
                        chromemethyfile.write(Outline)
                        DMCmethyfile.write(Outline)
                        
                PreviousMethydataSet=CurrentMethydataSet        
            filecontent=methyfile.readline()
            
        if (float(ErrorRowNum)/float(TotalCpGNum) > 0.1):
                    sys.exit("[Error:] Program termination due to more than 10% of data rows have errors!")

        return ChromeArray,SampleNames,Group_Key,Column_Key_Group,TotalCpGNum,AvailableCpGNum,DMC_Num,FillMissNum


#     def MissReplace_Primary_Segmentation(self,MethyData,MissReplace,AvailableGroup,MSthreshold,tmpDMCfolder,DMCmethyfile,p_DMR,statisticout):
#         '''
#         Split the BS-SEq data into chromes
#         Select the CpG sites with methylation values in at least **% samples
#         '''
#         #RawMethyDataFolderName=MethyDataFolder+'*.wig'
#         Methyentropy=NewEntropy.Entropy()
#         MissReplace=float(MissReplace)
#         ChromeArray=[]
#         SampleNames=[]
#         TotalCpGNum=0
#         AvailableCpGNum=0
#         DMC_Num=0
#         SmallSegNum=0
#         SmallDMRNum=0
#         GenomeSegmentOutFolder=tmpFolder+"GenomeSegment/"
#         GenomeSegmentMethyOutFolder=tmpFolder+"GenomeSegmentMethy/"
#         
#         
#         if tmpDMCfolder:
#             # use a output directory to store Splited Methylation data 
#             if not os.path.exists( tmpDMCfolder ):
#                 try:
#                     os.makedirs( tmpDMCfolder )
#                 except:
#                     sys.exit( "Output directory (%s) could not be created. Terminating program." % tmpDMCfolder )
#                     
#         if GenomeSegmentOutFolder:
#             # use a output directory to store merged Methylation data 
#             if not os.path.exists( GenomeSegmentOutFolder ):
#                 try:
#                     os.makedirs( GenomeSegmentOutFolder )
#                 except:
#                     sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentOutFolder )
#         if GenomeSegmentMethyOutFolder:
#             # use a output directory to store merged Methylation data 
#             if not os.path.exists( GenomeSegmentMethyOutFolder ):
#                 try:
#                     os.makedirs( GenomeSegmentMethyOutFolder )
#                 except:
#                     sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentMethyOutFolder )
#    
#         methyfile=open(MethyData,'rb') #open current methylation file
#         filecontent=methyfile.readline()
#         
#         ###First line for sample information
#         filecontent=filecontent.strip('\n')
#         firstline=filecontent.split('\t')
#         SampleNames=firstline[3:]
#         SampleNum=len(SampleNames)
#         Group_Key = defaultdict(list)
#         Column_Key_Group = dict()
#         sampleorder=0
#         for sample in SampleNames:
#             sample_info=sample.split('*')
#             if len(sample_info)>2:
#                 sys.exit( "Please make sure there is at most one underscore in the name of sample: (%s) " % sample )     
#             Group_Key[sample_info[0]].append(sampleorder)
#             Column_Key_Group[sampleorder] = sample_info[0]
#             sampleorder=sampleorder+1
#         Group_Key_str = str(Group_Key)
#         Column_Key_Group_str = str(Column_Key_Group)
#         statisticout.write(Group_Key_str)
#         statisticout.write(Column_Key_Group_str)
#         Groups=Group_Key.keys()
#         GroupNum=float(len(Groups))
#         ChromeFirstlyOutline=filecontent+"\tMethySpecificity\tSimilarityEntropyvalue\tEucDistance\n"
# #         DMCFirstlyOutline=filecontent+"\tDMCState\tNAOVA_pvalue\tMethySpecificity\tSimilarityEntropyvalue\tEucDistance\n"
# #         DMCmethyfile.write(DMCFirstlyOutline)
#         #AvailableCpGmethyfile.write(DMCFirstlyOutline)
#         ###Process methylation data
#         filecontent=methyfile.readline()
#         CurrentStr='chr'
#         ErrorRowNum=0
#         FillMissNum=0
#         while filecontent:
#             TotalCpGNum=TotalCpGNum+1
#             filecontent=filecontent.strip('\n')
#             currentMeth=filecontent.split('\t')
#             ###20170616: add function: Check whether the number of sample name equals the number of sample data
#             if len(currentMeth) > len(firstline):
#                 print "[Warning] Row "+str(TotalCpGNum)+": Number of data columns is more than that of sample names!"
#                 ErrorRowNum=ErrorRowNum+1
#                 
#             elif len(currentMeth) < len(firstline):
#                 print "[Warning] Row "+str(TotalCpGNum)+": Number of data columns is less than that of sample names!"
#                 ErrorRowNum=ErrorRowNum+1
#             else:
#                 chrome=currentMeth[0]
#                 if chrome != CurrentStr:  #If search the new chrome,
#                     ChromeArray.append(chrome)
#                     CurrentStr=chrome
#                     PreviousMethydataSet=[]
#                     PreviousLocation=0
#                     Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
#                     print Starttime+" Start identifying DMC for "+chrome
#                     #statisticout.write(Starttime+" Identifying DMC: "+chrome+"\n")
#                     chromemethyfile=tmpDMCfolder+chrome+".txt"
#                     #print chromemethyfile
#                     chromemethyfile=open(chromemethyfile,'wb')
#                     chromemethyfile.write(ChromeFirstlyOutline)
#                     
#                     SegmentMethyOUT=open(GenomeSegmentMethyOutFolder+CurrentStr+".txt", 'w')  #Open the file for segment and methylation
#                     #Parameter initialization
#                     SegmentCpGlist=[]
#                     SegmentMethyMatrix=[]
#                     
#                 # Data process
#                 CurrentLocation=int(currentMeth[1])
#                 CurrentMethydataSet=currentMeth[3:]
#                 ## Add missing value using the median value obtained the replicate samples 
#                 AvailableGroupNum=0 #Number of groups in which at least one sample have methylation value
#                 AvailableSampleNum=0 #Number of groups in which at least one sample have methylation value
#                 for eachgroup in Groups:
#                     Samples_sameGroup=Group_Key[eachgroup]  #The samples in the same group
#                     GroupSampleNum=float(len(Samples_sameGroup))
#                     Valuelist=[]
#                     MissValueNum=0
#                     for eachvalue_samegroup in Samples_sameGroup:
#                         if CurrentMethydataSet[eachvalue_samegroup] != '-':
#                         ###20170616: add the data check for DNA methylation values
#                             if(float(CurrentMethydataSet[eachvalue_samegroup]) >=0.0 and float(CurrentMethydataSet[eachvalue_samegroup]) <=1.0):
#                                 Valuelist.append(float(CurrentMethydataSet[eachvalue_samegroup]))
#                                 AvailableSampleNum=AvailableSampleNum+1
#                             else:
#                                 print "[Warning] Row "+str(TotalCpGNum)+": Methylation value that is out of range from 0.0 to 1.0 is treated as miss value! "
#                                 CurrentMethydataSet[eachvalue_samegroup] = '-'
#                                 MissValueNum=MissValueNum+1
#                         else:
#                             MissValueNum=MissValueNum+1
#                     NoneMissPercentage=float(len(Valuelist))/GroupSampleNum
#                     if MissValueNum>0 and NoneMissPercentage >= MissReplace:  #There are enough available values in the samples of the same group
#                         MedianValue=self.getMedian(Valuelist)  #Median value
#                         MedianValue=("%.3f" % MedianValue)                  
#                         #print MedianValue
#                         for eachvalue_samegroup in Samples_sameGroup:
#                             #print CurrentMethydataSet[eachvalue_samegroup]
#                             if CurrentMethydataSet[eachvalue_samegroup] is '-':
#                                 #print MedianValue
#                                 CurrentMethydataSet[eachvalue_samegroup] = MedianValue
#                                 FillMissNum=FillMissNum+1
#                                 AvailableSampleNum=AvailableSampleNum+1
#                     if len(Valuelist) > 0: # 
#                         AvailableGroupNum=AvailableGroupNum+1
#                         
#                 ##New methylation data after missing replacement
#                 MethylationNewList=CurrentMethydataSet
#                 Methydata=''
#                 for each in range(SampleNum):
#                     MethylationNewList[each]=str(MethylationNewList[each])
#                 Methydata='\t'.join(MethylationNewList)
#                 filecontent=currentMeth[0]+"\t"+str(currentMeth[1])+"\t"+str(currentMeth[2])+"\t"+Methydata
#                 
#                 ## Calculate entropy value for the CpG sites with enough methylation values
#                 if float(AvailableGroupNum)/float(GroupNum) >= AvailableGroup: #Check whether there are enough values for entropy calculate
#                     if len(PreviousMethydataSet)==0:
#                         PreviousMethydataSet=CurrentMethydataSet
#                         PreviousLocation=CurrentLocation
#                     ### Entropy and similarity
#                     MethySpecificity,SimilarityEntropyvalue,EucDistance = self.MethySpecificity_Calculator_SMART2(PreviousMethydataSet,CurrentMethydataSet,Group_Key,AvailableGroup)
#                     
#                     if (SimilarityEntropyvalue <= SMthreshold and EucDistance <= EDthreshold) and (CurrentLocation-PreviousLocation)<=CDthreshold:  #If the states are the same and the methylation are similar, merge them
#                         SegmentMethyMatrix.append(CurrentMethydataSet)
#                         #MethySumList=[x+y for x, y in zip(MethySumList, MethyList)]  #Sum the methylaion in each cell type
#                         SegmentCpGlist.append(CurrentLocation)  #Record current CpG and merge it
#                         #print SegmentCpGlist
#                     else:     #If the merger condition is not filled, output current segment, and initialize the new segment
#                         #output current segment
#                         SegmentCpGNum=len(SegmentCpGlist)
#                         #print SegmentCpGlist
#                         if len(SegmentCpGlist)>0:
#                             # Output a segment with its mean methylation in each group, methylation specificity and p value
#                             Group_Key_Methyl = defaultdict(list)  # Record the methylation values in each group
#                             ItemNum=0
#                             #Group_Key_Methyl_new = dict(list)  # Record the methylation values in each group
#                             for eachCpG in SegmentMethyMatrix:
#                                 for sampleorder in range(SampleNum):
#                                     if eachCpG[sampleorder] != '-':
#                                         Group_Key_Methyl[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups
#                                         ItemNum=ItemNum+1
#                                         #Group_Key_Methyl_new[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups  
#                             #Mean methylation
#                             Group_Methyl_mean=[]  # Order the same with Groups
#                             Group_Methyl_mean_out=[]  # Order the same with Groups
#                             for eachgroup in Groups:
#                                 if Group_Key_Methyl[eachgroup]:
#                                     Group_Methyl_mean.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for calculation of methylation specificity
#                                     Group_Methyl_mean_out.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for output of methylation specificity
#                                 else:
#                                     Group_Methyl_mean_out.append('-')
#                             #Methylation specificity                    
#                             MethySumListforEntropy=tuple(Group_Methyl_mean)
#                             #print MethySumListforEntropy
#                             MethySpecificity=round(1.0-Methyentropy.EntropyCalculate(MethySumListforEntropy),3)       #Calculate the new MethySpecificity for mean methylation     
#                                 
#                             #Output
#                             SegmentInfor=CurrentStr+":"+str(SegmentCpGlist[0])+"-"+str(int(SegmentCpGlist[-1])+2)+"\t"+str(MethySpecificity)+"\t"+str(SegmentCpGNum)
#                             SmallSegNum=SmallSegNum+1
#                             #print >> SegmentOUT, SegmentInfor
#                             print >> SegmentMethyOUT, SegmentInfor, Group_Methyl_mean_out
#     #                         print SegmentInfor
#     #                         print MethySpecificity 
#     #                         print NAOVA_pvalue
#                             
#                             Methydata=''
#                             for GroupOrder in range(len(Group_Methyl_mean_out)):
#                                 Group_Methyl_mean_out[GroupOrder]=str(Group_Methyl_mean_out[GroupOrder])
#                             Methydata=','.join(Group_Methyl_mean_out)
#                             
#                             #SegmentBedOutFile.write(CurrentStr+"\t"+SegmentCpGlist[0]+"\t"+str(int(SegmentCpGlist[-1])+2)+"\t"+str(SegmentCpGNum)+"\t"+MethySpecificity+"\t"+str(MethySpecificity)+"\t"+str(1.0)+"\t"+Methydata+"\n")
#                         #initialize the new segment
#                         SegmentCpGlist=[]
#                         SegmentMethyMatrix=[]
#                         SegmentMethyMatrix.append(CurrentMethydataSet)
#                         SegmentCpGlist.append(CurrentLocation)  #Record current CpG and merge it                                                                                                     
#                         
#                 PreviousMethydataSet=CurrentMethydataSet
#                 PreviousLocation=CurrentLocation      
#             filecontent=methyfile.readline()
#             
#         if (float(ErrorRowNum)/float(TotalCpGNum) > 0.1):
#                     sys.exit("[Error:] Program termination due to more than 10% of data rows have errors!")
# 
#         return ChromeArray,SampleNames,Group_Key,Column_Key_Group,TotalCpGNum,AvailableCpGNum,DMC_Num,FillMissNum,SmallSegNum
    

    def GenomeSegmentMeanMethy_MultiProcess_Chrome(self,RegionChrome,SampleNames,Group_Key,Column_Key_Group,tmpDMCfolder,tmpFolder,MSthreshold,EDthreshold,SMthreshold,CDthreshold,p_DMR):
        '''
        For each ChromeArrayome, segment it based the methylation entropy, differentroy and EuclideanDistance
        '''
        Extremep_DMR=p_DMR/0.00000000000000000001
        ExtrmeMSthreshold=MSthreshold/3
        SampleNum=len(SampleNames)
        Groups=Group_Key.keys()
        GroupNum=float(len(Groups))
        GenomeSegmentOutFolder=tmpFolder+"GenomeSegment/"
        GenomeSegmentMethyOutFolder=tmpFolder+"GenomeSegmentMethy/"
        Methyentropy=NewEntropy.Entropy()
        
        if GenomeSegmentOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( GenomeSegmentOutFolder ):
                try:
                    os.makedirs( GenomeSegmentOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentOutFolder )
        if GenomeSegmentMethyOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( GenomeSegmentMethyOutFolder ):
                try:
                    os.makedirs( GenomeSegmentMethyOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentMethyOutFolder )
        SmallSegNum=0
        SmallDMRNum=0

        EntropyDEEDFile =open(tmpDMCfolder+RegionChrome+".txt", 'r')  #Open the corresbondign methylation file
        #SegmentOUT=open(GenomeSegmentOutFolder+RegionChrome+".txt", 'w')  #Open the file for the segment
        SegmentMethyOUT=open(GenomeSegmentMethyOutFolder+RegionChrome+".txt", 'w')  #Open the file for segment and methylation
        #Parameter initialization
        SegmentCpGlist=[]
        SegmentMethyMatrix=[]
        
        #Perform segmentation
        CurrentCline=EntropyDEEDFile.readline()     #Read the first line (Colomn Name) of the methylation file
        PreviousState=''
        PreviousLocation=0
        CurrentCline=EntropyDEEDFile.readline()     #Read the first data line
        while CurrentCline:
            CurrentCline=CurrentCline.strip('\n')      #
            MethyEntropyInfor=CurrentCline.split()
            CurrentLocation=int(MethyEntropyInfor[1])              
            Entropy=float(MethyEntropyInfor[-3])
            SimilarityEntropy=float(MethyEntropyInfor[-2])
            EuclidDistance=float(MethyEntropyInfor[-1])
            if Entropy>=MSthreshold:
                CurrentState='DMC'
            else:
                CurrentState='NonDMC'
            
#             if (CurrentState==PreviousState and SimilarityEntropy <= SMthreshold and EuclidDistance <= EDthreshold) and (CurrentLocation-PreviousLocation)<=CDthreshold:

            if (SimilarityEntropy <= SMthreshold and EuclidDistance <= EDthreshold) and (CurrentLocation-PreviousLocation)<=CDthreshold:  #If the states are the same and the methylation are similar, merge them
                SegmentMethyMatrix.append(MethyEntropyInfor[3:-3])
                #MethySumList=[x+y for x, y in zip(MethySumList, MethyList)]  #Sum the methylaion in each cell type
                SegmentCpGlist.append(MethyEntropyInfor[1])  #Record current CpG and merge it
                #print SegmentCpGlist
            else:     #If the merger condition is not filled, output current segment, and initialize the new segment
                #output current segment
                SegmentCpGNum=len(SegmentCpGlist)
                #print SegmentCpGlist
                if len(SegmentCpGlist)>0:
                    # Output a segment with its mean methylation in each group, methylation specificity and p value
                    Group_Key_Methyl = defaultdict(list)  # Record the methylation values in each group
                    ItemNum=0
                    #Group_Key_Methyl_new = dict(list)  # Record the methylation values in each group
                    for eachCpG in SegmentMethyMatrix:
                        for sampleorder in range(SampleNum):
                            if eachCpG[sampleorder] != '-':
                                Group_Key_Methyl[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups
                                ItemNum=ItemNum+1
                                 
                    #Mean methylation
                    Group_Methyl_mean=[]  # Order the same with Groups
                    Group_Methyl_mean_out=[]  # Order the same with Groups
                    for eachgroup in Groups:
                        if Group_Key_Methyl[eachgroup]:
                            Group_Methyl_mean.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for calculation of methylation specificity
                            Group_Methyl_mean_out.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for output of methylation specificity
                        else:
                            Group_Methyl_mean_out.append('-')
                    #Methylation specificity                    
                    MethySumListforEntropy=tuple(Group_Methyl_mean)
                    #print MethySumListforEntropy
                    MethySpecificity=round(1.0-Methyentropy.EntropyCalculate(MethySumListforEntropy),3)       #Calculate the new MethySpecificity for mean methylation     
                        
                    #Output
                    SegmentInfor=RegionChrome+":"+str(SegmentCpGlist[0])+"-"+str(int(SegmentCpGlist[-1])+2)+"\t"+str(MethySpecificity)+"\t"+str(SegmentCpGNum)
                    SmallSegNum=SmallSegNum+1
                    #print >> SegmentOUT, SegmentInfor
                    print >> SegmentMethyOUT, SegmentInfor, Group_Methyl_mean_out

                SegmentCpGlist=[]
                SegmentMethyMatrix=[]
                SegmentMethyMatrix.append(MethyEntropyInfor[3:-3])
                SegmentCpGlist.append(MethyEntropyInfor[1])  #Record current CpG and merge it                                                                                                     
            PreviousState=CurrentState
            PreviousLocation=CurrentLocation
            CurrentCline=EntropyDEEDFile.readline()
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Finish segmentation for "+RegionChrome  #Report the region are segmented
        #statisticout.write(Starttime+" Finish segmentation for "+RegionChrome+"\n")    
        return SmallSegNum
            
    
    def GenomeSegmentMeanMethy_MultiProcess(self,ChromeArray,SampleNames,Group_Key,Column_Key_Group,tmpDMCfolder,tmpFolder,MSthreshold,EDthreshold,SMthreshold,CDthreshold,p_DMR):
        '''
        For each ChromeArrayome, segment it based the methylation entropy, differentroy and EuclideanDistance
        '''
        GenomeSegmentOutFolder=tmpFolder+"GenomeSegment/"
        GenomeSegmentMethyOutFolder=tmpFolder+"GenomeSegmentMethy/"

        if GenomeSegmentOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( GenomeSegmentOutFolder ):
                try:
                    os.makedirs( GenomeSegmentOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentOutFolder )
        if GenomeSegmentMethyOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( GenomeSegmentMethyOutFolder ):
                try:
                    os.makedirs( GenomeSegmentMethyOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentMethyOutFolder )
                    
        pool = Pool(len(ChromeArray))
        tasks=[]
        for RegionChrome in ChromeArray:
            tasks.append((RegionChrome,SampleNames,Group_Key,Column_Key_Group,tmpDMCfolder,tmpFolder,MSthreshold,EDthreshold,SMthreshold,CDthreshold,p_DMR))

        SmallSegmentNumChrome=pool.map(multi_genome_segmentation,tasks)
        pool.close()
        SmallSegmentNum=0
        for each in SmallSegmentNumChrome:
            SmallSegmentNum=SmallSegmentNum+each
        return SmallSegmentNum
            
    
    def MethySpecificity_Calculator_Merge(self,PreviousMethydataSet,CurrentMethydataSet,Groups):
        '''
        Constructor
        Caculate the SimilarityEntropy and Euclidean Distance between neighbring CpG
        '''
        GroupNum=len(Groups)
        AvailableCommonGroupNum=0 #Number of groups in which at least one sample have methylation value
        PreviousMethydataSet_A=[]
        CurrentMethydataSet_A=[]
        SimilarityEntropyvalue=-1
        EucDistance=-1
        Methyentropy=NewEntropy.Entropy()

        for GroupOrder in range(GroupNum):
            if (PreviousMethydataSet[GroupOrder] != "'-'" and CurrentMethydataSet[GroupOrder] != "'-'"):
                PreviousMethydataSet_A.append(float(PreviousMethydataSet[GroupOrder]))
                CurrentMethydataSet_A.append(float(CurrentMethydataSet[GroupOrder]))
                AvailableCommonGroupNum=AvailableCommonGroupNum+1
        if AvailableCommonGroupNum>0: #Check whether there are enough values for entropy calculate
            EucDistance=scipy.spatial.distance.euclidean( PreviousMethydataSet_A, CurrentMethydataSet_A)/sqrt(AvailableCommonGroupNum)  #calculate the euclidean distance between the methylation leveles of current C and previous C
            DifferMethydataSet=list(map(lambda x: abs(x[0]-x[1]), zip( PreviousMethydataSet_A, CurrentMethydataSet_A)))
            DifferMethydataSet=tuple(DifferMethydataSet)
            SimilarityEntropyvalue=1.0-Methyentropy.EntropyCalculate(DifferMethydataSet)
            
#             CurrentMethydataSet_A=tuple(CurrentMethydataSet_A)
#             CurrentSpecificity=1.0-Methyentropy.EntropyCalculate(CurrentMethydataSet_A)
#             PreviousMethydataSet_A=tuple(PreviousMethydataSet_A)
#             PreviousSpecificity=1.0-Methyentropy.EntropyCalculate(PreviousMethydataSet_A)
                       
        return SimilarityEntropyvalue,round(EucDistance,3)

                
    def SegmentMerge(self,ChromeArray,SampleNames,Groups,tmpFolder,MSthreshold,EDthreshold,SMthreshold,CDthreshold,statisticout):
        '''
        For each ChromeArrayome, Merge the segments based on the methylation entropy, differentroy and EuclideanDistance
        '''
        MergedGenomeSegmentOutFolder=tmpFolder+"MergedGenomeSegment/"
        if MergedGenomeSegmentOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( MergedGenomeSegmentOutFolder ):
                try:
                    os.makedirs( MergedGenomeSegmentOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % MergedGenomeSegmentOutFolder )
        for RegionChrome in ChromeArray:
            
            #statisticout.write(Starttime+" Merging Segments for "+RegionChrome+"\n")
            file=open(tmpFolder+"GenomeSegmentMethy/"+RegionChrome+".txt", 'r')  #Open the file for segment and methylation
            MergedSegmentOUT =open(MergedGenomeSegmentOutFolder+RegionChrome+".txt", 'w')  #Open the file for the segment
            list0=[]
            length=len(list0)
            n=0
            while n<=(7-length):
                line=file.readline()
                if line:
                    line=line.strip('\n')
                    line0=line.split('\t')
                    a1=line0[0].split(':')
                    a2=a1[-1].split('-')
                    a1=a1+a2 
                    del a1[1]
                    line1=line0[-1].split(' [')
                    a=line1[-1].strip(']')
                    a=a.split(', ')
                    a1.append(line0[1])
                    a1.append(line1[0])
                    a1=a1+a
                    list0.append(a1)
                    n=n+1
                else:
                    break
            line=file.readline()
            j=1
            CpGNum=0
            #print list0
            while j<=(len(list0)-1):
                PreviousMethydataSet=list0[0][5:len(list0[0])]
                MethydataSet=list0[j][5:len(list0[0])]
                PreviousState=list0[0][3]
                CurrentState=list0[j][3]
#                 print "***************"
#                 print list0[0]
#                 print list0[j]
                ## Count the CpG Number between two segment
                IntraCpGNum=0
                for IntraSegNum in range(1,j):
                    IntraCpGNum=IntraCpGNum+int(list0[IntraSegNum][4])

                SimilarityEntropyvalue,EucDistance = self.MethySpecificity_Calculator_Merge(PreviousMethydataSet,MethydataSet,Groups)
                
#                 print PreviousMethydataSet
#                 print MethydataSet
#                 print str(math.fabs(PreviousSpecificity-CurrentSpecificity))+":"+CurrentState+PreviousState+":"+str(SimilarityEntropyvalue)+":"+str(EucDistance)+":"+str((int(list0[j][1])-int(list0[0][2])))+":"+str(IntraCpGNum)
                
#                 if CurrentState==PreviousState and SimilarityEntropyvalue<= SMthreshold and EucDistance<= EDthreshold and (int(list0[j][1])-int(list0[0][2]))<= CDthreshold and IntraCpGNum<=5:
                if SimilarityEntropyvalue<= SMthreshold and EucDistance<= EDthreshold and (int(list0[j][1])-int(list0[0][2]))<= CDthreshold and IntraCpGNum<=5:         
                    #avEntropyvalue=(float(list0[0][3])*float(list0[0][4])+float(list0[j][3])*float(list0[j][4]))/(float(list0[0][4])+float(list0[j][4]))
                    #avEntropyvalue=round(avEntropyvalue,3)
                    #avEntropyvalue=round(CurrentSpecificity,3)
                    count=int(list0[0][4])+int(list0[j][4])
                    a1=[list0[0][0],list0[0][1],list0[j][2],CurrentState,count]
                    b1=list0[0][5:len(list0[0])]
                    b2=list0[j][5:len(list0[0])]
                    for q in range(len(b1)):
                        if b1[q]!= "'-'" and b2[q]!= "'-'":
                            b1[q]=(float(b1[q])*float(list0[0][4])+float(b2[q])*float(list0[j][4]))/(float(list0[0][4])+float(list0[j][4]))
                            b1[q]=round(b1[q],3)
                        elif b1[q]!= "'-'":
                            b1[q]=round(float(b1[q]),3)
                        elif b2[q]!= "'-'":
                            b1[q]=round(float(b2[q]),3)
                        else:
                            b1[q]="'-'"
                    newlist=a1+b1
                    list0[j]=newlist
                    list0=list0[j:len(list0)]
                    length=len(list0)
                    n=0
                    while n<=(7-length) and line:
                        line=line.strip('\n')
                        line0=line.split('\t')
                        a1=line0[0].split(':')
                        a2=a1[-1].split('-')
                        a1=a1+a2 
                        del a1[1]
                        line1=line0[-1].split(' [')
                        a=line1[-1].strip(']')
                        a=a.split(', ')
                        a1.append(line0[1])
                        a1.append(line1[0])
                        a1=a1+a
                        list0.append(a1)
                        n=n+1
                        line=file.readline()
                    j=1
                elif j==(len(list0)-1):
                    MethyList=[str(x) for x in list0[0][5:len(list0[0])]]
                    Methydata='\t'.join(MethyList)
                    Segmentname=list0[0][0]+":"+list0[0][1]+"-"+list0[0][2]
                    MeanSpecificity=list0[0][3]
                    CpGNum=str(list0[0][4])
                    MergedSegmentOUT.write(Segmentname+"\t"+MeanSpecificity+"\t"+CpGNum+"\t"+Methydata+"\n")
                    list0=list0[1:len(list0)]
                    n=0
                    while n<=(7-len(list0))and line:
                        line=line.strip('\n')
                        line0=line.split('\t')
                        a1=line0[0].split(':')
                        a2=a1[-1].split('-')
                        a1=a1+a2 
                        del a1[1]
                        line1=line0[-1].split(' [')
                        a=line1[-1].strip(']')
                        a=a.split(', ')
                        a1.append(line0[1])
                        a1.append(line1[0])
                        a1=a1+a
                        list0.append(a1)
                        n=n+1
                        line=file.readline()
                    j=1
                else:
                    j=j+1
            if len(list0)==1:
                MethyList=[str(x) for x in list0[0][5:len(list0[0])]]
                Methydata='\t'.join(MethyList)
                Segmentname=list0[0][0]+":"+list0[0][1]+"-"+list0[0][2]
                MeanSpecificity=list0[0][3]
                CpGNum=str(list0[0][4])
                MergedSegmentOUT.write(Segmentname+"\t"+MeanSpecificity+"\t"+CpGNum+"\t"+Methydata+"\n")
            Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
            print Starttime+" Finish merging segments for "+RegionChrome  #Report the region are segmented

   

    def DeNovoFinalResult_MultiProgress_Chrome(self,chrome,tmpFolder,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark):
        '''
        '''
        Methyentropy=NewEntropy.Entropy()
        Numdec={'MergedSegment':0}
        SampleNum=len(SampleNames)
        CellTypeHypoNum={}
        CellTypeHyperNum={}
        for CellTypeName in Groups:
            CellTypeHypoNum[CellTypeName]=0
            CellTypeHyperNum[CellTypeName]=0

        tmpDMCfolder=tmpFolder+'DifferMethlCpG/'
        InputFolder=tmpFolder+"MergedGenomeSegment/"
        tmpFinalResultsFolder=tmpFolder+"TmpFinalResults/"
        BedOutFile=open(tmpFinalResultsFolder+"2_MergedSegment_"+chrome+".bed",'wb') #Build  a bed file
        MergedSegmentOutFile=open(tmpFinalResultsFolder+"3_MergedSegment_Methylation_"+chrome+".txt",'wb') #Build a bed file    
        
        EntropyDEEDFile =open(tmpDMCfolder+chrome+".txt", 'r')  #Open the corresbondign methylation file
        CurrentCline=EntropyDEEDFile.readline()     #Read the first line (Colomn Name) of the methylation file
        CurrentCline=EntropyDEEDFile.readline()     # First data line
        
        InputFilename=InputFolder+chrome+".txt"
        InputFile=open(InputFilename,'r')
        RegionFileLine=InputFile.readline()
        while RegionFileLine:
        #chrM:33-14946 0.0 684 [0.009, 0.006, 0.009, 0.011,
            
            RegionFileLine=RegionFileLine.strip('\n')
            RegionFileLine=RegionFileLine.replace(":",'\t')
            RegionFileLine=RegionFileLine.replace('-','\t')
            RegionFileLine=RegionFileLine.replace(']','')
            RegionFileLine=RegionFileLine.replace("\'",'')
            RegionFileLine=RegionFileLine.replace('[','')
            RegionFileLine=RegionFileLine.replace(', ','\t')
            #print RegionFileLine
            CurrentRegionrawinfor=RegionFileLine.split('\t')
            RegionChrome=CurrentRegionrawinfor[0]
            RegionStart=int(CurrentRegionrawinfor[1])
            RegionEnd=int(CurrentRegionrawinfor[2])
            SegmentLength=int(RegionEnd)-int(RegionStart)
            # Obtain the methylation level in a merged region in each group
            SegmentMethyMatrix=[]
            RegionCNum=0
            while CurrentCline:
                #CurrentCline=CurrentCline.strip('\n')      #
                MethyEntropyInfor=CurrentCline.split()
                CurrentLocation=int(MethyEntropyInfor[1])+1
                if (CurrentLocation >= RegionStart) and (CurrentLocation <= RegionEnd):  # Obtain the methylation level in a merged region in each group
                    SegmentMethyMatrix.append(MethyEntropyInfor[3:-3])
                    RegionCNum=RegionCNum+1
                    CurrentCline=EntropyDEEDFile.readline()
                elif CurrentLocation < RegionStart:
                    CurrentCline=EntropyDEEDFile.readline()
                else:
                    break
            
            # Output a segment with its mean methylation in each group, methylation specificity and p value
            Group_Key_Methyl = defaultdict(list)  # Record the methylation values in each group
            Sample_Key_Methyl = defaultdict(list)  # Record the methylation values in each sample
#             Group_Key_Methyl_forNAOVA = []
            Sample_MethylationList=[] # Order the same with Samples
            #Group_Key_Methyl_new = dict(list)  # Record the methylation values in each group
            for eachCpG in SegmentMethyMatrix:
                for sampleorder in range(SampleNum):
                    if eachCpG[sampleorder] != '-':
                        Sample_Key_Methyl[sampleorder].append(float(eachCpG[sampleorder])) 
                        Group_Key_Methyl[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups
#                         Group_Key_Methyl_forNAOVA.append([Column_Key_Group[sampleorder],float(eachCpG[sampleorder])])
                        #Group_Key_Methyl_new[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups  
            #Sample mean methylation
            for sampleorder in range(SampleNum):
                if Sample_Key_Methyl[sampleorder]: ## If there are methylation values, calculate the mean methyaltion level for the segment in the sample
                    Sample_MethylationList.append(str(round(np.mean(Sample_Key_Methyl[sampleorder]),3)))  # mean methylation value
                else:
                    Sample_MethylationList.append('-')  # No value, use '-'
            Sample_Mean_Methydata=','.join(Sample_MethylationList)
                
            #Mean methylation
            MethylationRawList=[]  # Order the same with Groups
            Group_Methyl_mean_out=[]  # Order the same with Groups
            for eachgroup in Groups:
                if Group_Key_Methyl[eachgroup]:
                    MethylationRawList.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for calculation of methylation specificity
                    Group_Methyl_mean_out.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for output of methylation specificity
                else:
                    Group_Methyl_mean_out.append('-')
            #Methylation specificity
            
            if len(MethylationRawList) > 0 and int(RegionCNum)>=SCthreshold and int(SegmentLength)>=SLthreshold: # Avoid the errors induced by the short segment and only output the segment with more than 5 CpGs and 20bp
                Numdec['MergedSegment']=Numdec['MergedSegment']+1
                MethySumListforEntropy=tuple(MethylationRawList)
                MethySpecificity=round(1.0-Methyentropy.EntropyCalculate(MethySumListforEntropy),3)       #Calculate the new MethySpecificity for mean methylation     

                ##############OUTPUT
                Methydata=''
                for GroupOrder in range(len(MethylationRawList)):
                    MethylationRawList[GroupOrder]=str(MethylationRawList[GroupOrder])
                Methydata=','.join(MethylationRawList)
                
                RegionName='MergedSegment_'+str(Numdec['MergedSegment'])+',S='+str(round(MethySpecificity,1))+',L='+str(SegmentLength)
                ##########Output the segments with core infor
                BedOutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+RegionName+"\t"+str(int(MethySpecificity*1000))+"\t"+"+"+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+"255,0,0"+"\n")
                ##########Output the segments with core infor and methylation data
                MergedSegmentOutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+str(MethySpecificity)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+Methydata+"\t"+Sample_Mean_Methydata+"\n")

            RegionFileLine=InputFile.readline()
        
        #print Numdec
        return Numdec

    def DeNovoFinalResult_MultiProgress(self,tmpFolder,BedOutFile,MergedSegmentOutFile,ChromeArray,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,statisticout):
        '''
        
        '''

        Total_Numdec={'MergedSegment':0}
        Numdec_Keys=Total_Numdec.keys()

        tmpFinalResultsFolder=tmpFolder+"TmpFinalResults/"
        CellTypeHypoNum={}
        CellTypeHyperNum={}
        for CellTypeName in Groups:
            CellTypeHypoNum[CellTypeName]=0
            CellTypeHyperNum[CellTypeName]=0
        
        pool = Pool(len(ChromeArray))
        tasks=[]
        for chrome in ChromeArray:
            tasks.append((chrome,tmpFolder,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark))
            
        Chrome_Numdec=pool.map(multi_final_results,tasks)
        pool.close()
        
        #Combine all chrome results
        for chrome in ChromeArray:
            BedOutFile_chrome=open(tmpFinalResultsFolder+"2_MergedSegment_"+chrome+".bed",'r') #Build  a bed file
            MergedSegmentOutFile_chrome=open(tmpFinalResultsFolder+"3_MergedSegment_Methylation_"+chrome+".txt",'r') #Build a bed file     
            
            CurrentCline=BedOutFile_chrome.readline()
            while CurrentCline:
                BedOutFile.write(CurrentCline)
                CurrentCline=BedOutFile_chrome.readline()
            
            CurrentCline=MergedSegmentOutFile_chrome.readline()
            while CurrentCline:
                MergedSegmentOutFile.write(CurrentCline)
                CurrentCline=MergedSegmentOutFile_chrome.readline()
        
        for eachChrome in Chrome_Numdec:
            for eachKey in Numdec_Keys:
                Total_Numdec[eachKey]=Total_Numdec[eachKey]+eachChrome[eachKey]
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Final result has been generated for all chromosomes."
        return Total_Numdec



           

    def median(self,sequence):
            if len(sequence) < 1:
                return None
            else:
                sequence.sort()
                return sequence[len(sequence) // 2]
        
    def getMedian(self,dataSet):
        newData=[];
        for i in range(len(dataSet)):    
            newData.append(dataSet[i]);
        newData.sort()  #Sort
        if(len(dataSet)%2!=0):
            return newData[len(dataSet)/2];    #for odd number of samples 
        else:
            return (newData[len(dataSet)/2]+newData[len(dataSet)/2-1])/2.0;  #for even number of samples
    
    
    def runSegment(self,UserArgslist,MethyData,ProjectName,MissReplace,AvailableGroup,MSthreshold,EDthreshold,SMthreshold,CDthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,OutFolder):

        MissReplace = float(MissReplace)
        AvailableGroup = float(AvailableGroup)
        MSthreshold = float(MSthreshold)
        EDthreshold = float(EDthreshold)
        SMthreshold = float(SMthreshold)
        CDthreshold = int(CDthreshold)
        SCthreshold = int(SCthreshold)
        SLthreshold = int(SLthreshold)
        p_DMR = float(p_DMR)
        p_MethylMark = float(p_MethylMark)

        MethyDataFolderName=MethyData
        
        #Searchregion=Segmentation()
        
        FinalResultFolder=OutFolder+'Segment/'
        tmpDMCfolder=FinalResultFolder+'tmp/DifferMethlCpG/'
        tmpFolder=FinalResultFolder+'tmp/'
        tmpFinalResultsFolder=tmpFolder+"TmpFinalResults/"
        RecordFile=FinalResultFolder+"Summary.txt"
    
        Searchregion=Segmentation()
        
        if FinalResultFolder:
            # use a output directory to store merged Methylation data 
            if os.path.exists( FinalResultFolder ):
                shutil.rmtree(FinalResultFolder)
            try:
                os.makedirs( FinalResultFolder )
            except:
                sys.exit( "Output directory (%s) could not be created. Terminating program." % FinalResultFolder )
            try:
                os.makedirs( tmpFolder )
            except:
                sys.exit( "Output directory (%s) could not be created. Terminating program." % tmpFolder )
            try:
                os.makedirs( tmpFinalResultsFolder )
            except:
                sys.exit( "Output directory (%s) could not be created. Terminating program." % tmpFinalResultsFolder )
        
        statisticout=open(RecordFile,'w')
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Starttime+" ***************Project "+ProjectName+" parameters**************"
        print UserArgslist        
        statisticout.write(Starttime+" ***************Project "+ProjectName+" parameters**************\n"+UserArgslist+"\n\n")
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Starttime+" *****************Project "+ProjectName+" Start*****************"
        statisticout.write(Starttime+" *****************Project "+ProjectName+" Start*****************\n")
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to check methylation data and fill missing value..."
        statisticout.write(Starttime+" Start to check data and fill missing value...\n")
        
        DMCmethyfile=open(FinalResultFolder+"1_AvailableCpGs.txt",'wb') #Built a txt file 
        ChromeArray,SampleNames,Group_Key,Column_Key_Group,TotalCpGNum,AvailableCpGNum,DMC_Num,FillMissNum = Searchregion.DataCheck_and_MissReplace(MethyDataFolderName,MissReplace,AvailableGroup,MSthreshold,tmpDMCfolder,DMCmethyfile,p_DMR,statisticout)
        Groups=Group_Key.keys()
        #Genome segmentation based on methylation similarity between neighboring C...
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start genome segmentation ..."
        statisticout.write(Starttime+" Start genome segmentation ...\n")
        #SegmentBedOutFile=open(FinalResultFolder+"2_SmallSegment.bed",'wb') #Built a bed file  
        #SmallSegNum,Groups=Searchregion.GenomeSegmentMeanMethy(ChromeArray,SampleNames,Group_Key,Column_Key_Group,tmpDMCfolder,tmpFolder,SegmentBedOutFile,MSthreshold,EDthreshold,SMthreshold,CDthreshold,p_DMR,statisticout)
        SmallSegNum=Searchregion.GenomeSegmentMeanMethy_MultiProcess(ChromeArray,SampleNames,Group_Key,Column_Key_Group,tmpDMCfolder,tmpFolder,MSthreshold,EDthreshold,SMthreshold,CDthreshold,p_DMR)
     
        #SegmentBedOutFile.close()
        
        #Merging Segmentation
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to merge small segments..."
        statisticout.write(Starttime+" Start to merge small segments...\n")
        Searchregion.SegmentMerge(ChromeArray,SampleNames,Groups,tmpFolder,MSthreshold,EDthreshold,SMthreshold,CDthreshold,statisticout)
        
        #Generate the final result
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to generate the final result..."
        statisticout.write(Starttime+" Start to generate the final result...\n")
        InputFolder=tmpFolder+"MergedGenomeSegment/"
        
        BedOutFile=open(FinalResultFolder+"2_MergedSegment.bed",'wb') #Build  a bed file
        BedOutFile.write("#Merged segments information for visualization in Genome browser.\ntrack name=\"MergedMethySegment\" description=\"Merged Methylation Segment by SMART2\" visibility=2 itemRgb=\"On\"\n")
        #BedOutFile.write("track name=\"MergedMethySegment\" description=\"Merged Methylation Segment of Human Cells/Tissues (0.4&0.2&500)\" visibility=2 itemRgb=\"On\"\n")
        ######Bed9 for Visualization in Hub of UCSC genome browser
        MergedSegmentOutFile=open(FinalResultFolder+"3_MergedSegment_Methylation.txt",'wb') #Build a bed file    
        MergedSegmentOutFile.write("#Merged segments and its methylation in each sample or group. \nChrome\tStart\tEnd\tCpG_Num\tLength\tGroup_Methyl:"+','.join(Groups)+"\tSample_Methyl:"+','.join(SampleNames)+"\n")

        Numdec=Searchregion.DeNovoFinalResult_MultiProgress(tmpFolder,BedOutFile,MergedSegmentOutFile,ChromeArray,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,statisticout)
 
        #print Numdec
        shutil.rmtree(tmpFolder) #Delete tmp files
        
        BedOutFile.close()
        MergedSegmentOutFile.close()

        
        Endtime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Endtime+" ********************Project Summary******************"
        print Endtime+" Chromesomes   : "+','.join(ChromeArray)
        print Endtime+" Sample Number : "+str(len(SampleNames))
        print Endtime+" Sample Names  : "+','.join(SampleNames)
        print Endtime+" Group Number : "+str(len(Groups)) 
        print Endtime+" Group Names  : "+','.join(Groups)
        print Endtime+" Number of total CpG sites in all chromesomes       :"+str(TotalCpGNum)
        print Endtime+" Number of CpG sites with available methylation     :"+str(AvailableCpGNum)
        print Endtime+" Number of missing values that have been filled     :"+str(FillMissNum)
        print Endtime+" Small  Segment Number                              :"+str(SmallSegNum)
        print Endtime+" Merged Segment Number                              :"+str(Numdec['MergedSegment'])
        
        statisticout.write("\n")
        statisticout.write(Endtime+" ********************Project Summary******************\n")
        statisticout.write(Endtime+" Chromesomes:  "+','.join(ChromeArray)+"\n")
        statisticout.write(Endtime+" SampleNumber: "+str(len(SampleNames))+"\n")
        statisticout.write(Endtime+" SampleNames:  "+','.join(SampleNames)+"\n")
        statisticout.write(Endtime+" Group Number : "+str(len(Groups)) +"\n")
        statisticout.write(Endtime+" Group Names  : "+','.join(Groups)+"\n")
        statisticout.write(Endtime+" Number of total CpG sites in all chromesomes      :"+str(TotalCpGNum)+"\n")
        statisticout.write(Endtime+" Number of CpG sites with available methylation    :"+str(AvailableCpGNum)+"\n")
        statisticout.write(Endtime+" Number of missing values that have been filled    :"+str(FillMissNum)+"\n")
        statisticout.write(Endtime+" Small Segment Number                              :"+str(SmallSegNum)+"\n")
        statisticout.write(Endtime+" Merged Segment Number                             :"+str(Numdec['MergedSegment'])+"\n")
        
        Endtime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Endtime+" *********************Summary End*********************"
        statisticout.write(Endtime+" *********************Summary End*********************\n")
        print "\n"
        print Endtime+" Detailed results in "+OutFolder
        print Endtime+" For any questions, visit http://fame.edbc.org/smart/ or contact Hongbo Liu (hongbo919@gmail.com)"
        print "\n"
        print Endtime+" ***************Project "+ProjectName+" Finished!***************"
        statisticout.write("\n")
        statisticout.write(Endtime+" The final Results can be found in "+OutFolder+"\n")
        statisticout.write(Endtime+" For any questions, visit http://fame.edbc.org/smart/ or contact Hongbo Liu (hongbo919@gmail.com)\n")
        statisticout.write("\n")
        statisticout.write(Endtime+" ***************Project "+ProjectName+" Finished!***************\n")
        statisticout.close()





if __name__ == '__main__':
    MissReplace = 0.5
    AvailableGroup = 0.5
    MSthreshold = 0.5
    EDthreshold = 0.2
    SMthreshold = 1.0
    CDthreshold = 500
    SCthreshold = 1
    SLthreshold = 1
    p_DMR = 0.05
    p_MethylMark = 0.05
    GenomeRegions=''
    ProjectName='SMART'
    UserArgslist=""
    
    #MethyDataFolderName='/Users/hongbo.liu/Desktop/MethylMatrix_Combined_2nd_CpG_Unique_Sorted_50p_SMART.bed'
    #MethyDataFolderName='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/TurSeqEPIC_CpGMethyl_Matrix_Test_chr2.bed'
    #MethyDataFolderName='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/TurSeqEPIC_CpGMethyl_Matrix_Test.bed'
    #MethyDataFolderName='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/TurSeqEPIC_CpGMethyl_Matrix.bed'
    MethyDataFolderName='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/Chr1_45735342_45857045_Test_segment.bed'
    OutFolder="/Users/hongbo.liu/Desktop/Results/"
    
    Searchregion=Segmentation()
    MethyData=MethyDataFolderName
    Searchregion.runSegment(UserArgslist,MethyData,ProjectName,MissReplace,AvailableGroup,MSthreshold,EDthreshold,SMthreshold,CDthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,OutFolder)
    