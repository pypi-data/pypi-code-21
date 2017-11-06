#!/usr/bin/env python
'''
Updataed on 2017.04.11

@author: liuhongbo
'''
import gzip
import os
import sys
import NewEntropy
import scipy.spatial
from math import sqrt
import time
from collections import defaultdict

class DMC_Calling():
    '''
        Constructor
        Split the methylation files into different folders named as chrome id
        '''
    def __init__(self):
        '''
        Constructor
        Split the methylation files into different folders named as chrome id
        '''
    def Splitchrome(self,chromes,filenames,OutFolderName):
        '''
        Split the RRBS data
        '''
        #build the dirs with different chrome names
        for i in range(0,len(chromes)):
            dirpath=OutFolderName+chromes[i]
            isExists=os.path.exists(dirpath)
            if not isExists:
                os.mkdir(dirpath)
        
        for filename in filenames:
            print filename
            #build and open the out files
            filedict = {}
            namestart=filename.find('wgEncode')
            for i in range(0,len(chromes)):
                chromemethyfile=OutFolderName+chromes[i]+'/'+chromes[i]+'_'+filename[namestart:]
                chromemethyfile=gzip.open(chromemethyfile,'wb')
                filedict[chromes[i]]=chromemethyfile  #build a dictionary of chrome files: key is chrome, value is the file Handle
            methyfile=gzip.open(filename,'rb') #open current methylation file
            methyfile.readline()
            filecontent=methyfile.readline()
            while filecontent:
                methyinfor=filecontent.split('\t')
                if filedict.has_key(methyinfor[0]) and methyinfor[4]>=10:  #
                    filedict.get(methyinfor[0]).write(methyinfor[1]+"\t"+methyinfor[10])
                filecontent=methyfile.readline()
            for i in range(0,len(chromes)):
                filedict.get(chromes[i]).close
    
       
    def MethySpecificity_Calculator_SMART2(self,PreviousMethydataSet,CurrentMethydataSet,Group_Key,AvailableGroup):
        '''
        Constructor
        Caculate the SimilarityEntropy and Euclidean Distance between neighbring CpG
        '''
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
        if AvailableCommonGroupNum/GroupNum >=AvailableGroup: #Check whether there are enough values for entropy calculate
            EucDistance=scipy.spatial.distance.euclidean(PreviousMethydataSet_A, CurrentMethydataSet_A)/sqrt(AvailableCommonGroupNum)  #calculate the euclidean distance between the methylation leveles of current C and previous C
            DifferMethydataSet=list(map(lambda x: abs(x[0]-x[1]), zip( PreviousMethydataSet_A, CurrentMethydataSet_A)))
            CurrentMethydataSet_A=tuple(CurrentMethydataSet_A)
            MethySpecificity=1.0-Methyentropy.EntropyCalculate(CurrentMethydataSet_A)
            DifferMethydataSet=tuple(DifferMethydataSet)
            SimilarityEntropyvalue=1.0-Methyentropy.EntropyCalculate(DifferMethydataSet) 
                      
        return MethySpecificity,SimilarityEntropyvalue,round(EucDistance,3)
    
    
       
    def MissReplace_DMC_callling(self,MethyData,MissReplace,AvailableGroup,DMRthreshold,OutFolder,statisticout):
        '''
        Split the BS-SEq data into chromes
        Select the CpG sites with methylation values in at least **% samples
        '''
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to Identify Differentially methylated CpG sites (DMC)..."
        statisticout.write(Starttime+" Start to Identify Differentially methylated CpG sites (DMC)...\n")
        #RawMethyDataFolderName=MethyDataFolder+'*.wig.gz'
        OutFolderName=OutFolder+'DifferMethlCpG/'
        ChromeArray=[]
        SampleNames=[]
        TotalCpGNum=0
        AvailableCpGNum=0
        DMC_Num=0
        
        if OutFolderName:
            # use a output directory to store Splited Methylation data 
            if not os.path.exists( OutFolderName ):
                try:
                    os.makedirs( OutFolderName )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % OutFolderName )
   
        methyfile=open(MethyData,'rb') #open current methylation file
        DMCmethyfileLoc=OutFolderName+"DifferMethlCpGs.txt.gz"
        #print chromemethyfile
        DMCmethyfile=gzip.open(DMCmethyfileLoc,'wb')
        filecontent=methyfile.readline()
        
        ###First line for sample information
        filecontent=filecontent.strip('\n')
        firstline=filecontent.split('\t')
        SampleNames=firstline[3:]
        Group_Key = defaultdict(list)
        Column_Key_Group = dict()
        sampleorder=0
        SampleNum=len(SampleNames)
        for sample in SampleNames:
            sample_info=sample.split('_')
            Group_Key[sample_info[0]].append(sampleorder)
            Column_Key_Group[sampleorder] = sample_info[0]
            sampleorder=sampleorder+1
        Group_Key_str = str(Group_Key)
        Column_Key_Group_str = str(Column_Key_Group)
        statisticout.write(Group_Key_str)
        statisticout.write(Column_Key_Group_str)
        Groups=Group_Key.keys()
        GroupNum=float(len(Groups))
        ChromeFirstlyOutline=filecontent+"\tMethySpecificity\tSimilarityEntropyvalue\tEucDistance\n"
        DMCFirstlyOutline=filecontent+"\tDMCState\tMethySpecificity\tSimilarityEntropyvalue\tEucDistance\n"
        DMCmethyfile.write(DMCFirstlyOutline)
        ###Process methylation data
        filecontent=methyfile.readline()
        CurrentStr='chr'
               
        while filecontent:
            TotalCpGNum=TotalCpGNum+1
            filecontent=filecontent.strip('\n')
            currentMeth=filecontent.split('\t')
            chrome=currentMeth[0]
            if chrome != CurrentStr:  #If search the new chrome,
                ChromeArray.append(chrome)
                CurrentStr=chrome
                PreviousMethydataSet=[]
                Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
                print Starttime+" Identify DMC: "+chrome
                statisticout.write(Starttime+" Identify DMC: "+chrome+"\n")
                chromemethyfile=OutFolderName+chrome+".txt.gz"
                #print chromemethyfile
                chromemethyfile=gzip.open(chromemethyfile,'wb')
                chromemethyfile.write(ChromeFirstlyOutline)
            # Data process
            CurrentMethydataSet=currentMeth[3:]
            #print CurrentMethydataSet
            ## Add missing value using the random value obtained the replicate samples 
            AvailableGroupNum=0 #Number of groups in which at least one sample have methylation value 
            for eachgroup in Groups:
                Samples_sameGroup=Group_Key[eachgroup]  #The samples in the same group
                GroupSampleNum=len(Samples_sameGroup)
                Valuelist=[]
                for eachvalue_samegroup in Samples_sameGroup:
                    if CurrentMethydataSet[eachvalue_samegroup] != '-':
                        Valuelist.append(float(CurrentMethydataSet[eachvalue_samegroup]))
                NoneMissPercentage=len(Valuelist)/GroupSampleNum
                if NoneMissPercentage >= MissReplace:  #There are enough available values in the samples of the same group
                    MedianValue=self.getMedian(Valuelist)  #Median value
                    #print MedianValue
                    for eachvalue_samegroup in Samples_sameGroup:
                        if CurrentMethydataSet[eachvalue_samegroup] == '-':
                            CurrentMethydataSet[eachvalue_samegroup] = MedianValue
                if len(Valuelist) > 0: # 
                    AvailableGroupNum=AvailableGroupNum+1         
                
            ## Calculate entropy value for the CpG sites with enough methylation values
            
            if AvailableGroupNum/GroupNum >= AvailableGroup: #Check whether there are enough values for entropy calculate
                AvailableCpGNum=AvailableCpGNum+1
                if len(PreviousMethydataSet)==0:
                    PreviousMethydataSet=CurrentMethydataSet
                MethySpecificity,SimilarityEntropyvalue,EucDistance = self.MethySpecificity_Calculator_SMART2(PreviousMethydataSet,CurrentMethydataSet,Group_Key,AvailableGroup)
                if MethySpecificity >= 0:
                    if MethySpecificity >= DMRthreshold:
                        DMCState='DMC'
                        DMC_Num=DMC_Num+1
                    else:
                        DMCState='NonDMC'    
                    Outline=filecontent+"\t"+str(MethySpecificity)+"\t"+str(SimilarityEntropyvalue)+"\t"+str(EucDistance)+"\n"
                    chromemethyfile.write(Outline)
                    DMCOutline=filecontent+"\t"+DMCState+"\t"+str(MethySpecificity)+"\t"+str(SimilarityEntropyvalue)+"\t"+str(EucDistance)+"\n"
                    DMCmethyfile.write(DMCOutline)
                    
            PreviousMethydataSet=CurrentMethydataSet        
            filecontent=methyfile.readline()

        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Summary of DMC identification: "
        print "\t\t    Number of total CpG sites: "+str(TotalCpGNum)
        print "\t\t    Number of CpG sites with methylation in at least "+str(AvailableGroup*100)+"% of groups : "+str(AvailableCpGNum)
        print "\t\t    Number of identified DMC based threshold "+str(DMRthreshold)+": "+str(DMC_Num)
        statisticout.write(Starttime+" Summary of DMC identification: "+"\n")
        statisticout.write("\t\t    Number of total CpG sites: "+str(TotalCpGNum)+"\n")
        statisticout.write("\t\t    Number of CpG sites with methylation in at least "+str(AvailableGroup*100)+"% of groups : "+str(AvailableCpGNum)+"\n")
        statisticout.write("\t\t    Number of identified DMC based threshold "+str(DMRthreshold)+": "+str(DMC_Num)+"\n")
        return ChromeArray,SampleNames,Group_Key,Column_Key_Group
    
    def getMedian(self,dataSet):
        newData=[];
        for i in range(len(dataSet)):    
            newData.append(dataSet[i]);
        newData.sort()  #Sort
        if(len(dataSet)%2!=0):
            return newData[len(dataSet)/2];    #for odd number of samples 
        else:
            return (newData[len(dataSet)/2]+newData[len(dataSet)/2-1])/2.0;  #for even number of samples 

    def run(self,MethyDataFolderName,MissReplace,AvailableGroup,DMRthreshold,OutFolderName,statisticout):
        DMC_Calling=DMC_Calling()
        ChromeArray,SampleNames=DMC_Calling.MissReplace_DMC_callling(MethyDataFolderName,MissReplace,AvailableGroup,DMRthreshold,OutFolderName,statisticout)
        return ChromeArray,SampleNames

if __name__ == '__main__':
    #chromes=['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chrX','chrY']
    #chromes=['chrY']
    MissReplace = 0.5
    AvailableGroup = 0.8
    DMRthreshold = 0.5
    Starttime=time.strftime('%Y-%m-%d %A %X',time.localtime(time.time()))
    print Starttime
    MethyDataFolderName='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/TurSeqEPIC_CpGMethyl_Matrix_Test.bed'
    OutFolderName='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/Results/'
#     MethyFolder=Folderprocess.Folderprocess()
#     filenames=MethyFolder.readFolderfile(MethyDataFolderName)
#     print "File Num is: "+str(len(filenames))
    #print filenames
    #Splitmethychrome=Splitchrome()
    #Splitmethychrome.Splitchrome(chromes,filenames,OutFolderName)
    statisticout=open(OutFolderName+"statistic.txt",'w')
    a=time.strftime('%Y-%m-%d %A %X',time.localtime(time.time()))
    statisticout.write(a)
    #statisticout.write(str(len(filenames))+"\n")
    statisticout.write(Starttime+"\n")
    #statisticout.write(filenames+"\n")
    DMC_Calling=DMC_Calling()
    DMC_Calling.MissReplace_DMC_callling(MethyDataFolderName,MissReplace,AvailableGroup,DMRthreshold,OutFolderName,statisticout)
    Endtime=time.strftime('%Y-%m-%d %A %X',time.localtime(time.time()))
    #print "File Num is: "+str(len(filenames))
    print "Start Time is: "+Starttime
    print "End Time is: "+Endtime
    statisticout=open(OutFolderName+"statistic.txt",'a') 
    #statisticout.write(str(len(filenames))+"\n")
    statisticout.write(Starttime+"\n")
    statisticout.write(Endtime+"\n")
    statisticout.close()