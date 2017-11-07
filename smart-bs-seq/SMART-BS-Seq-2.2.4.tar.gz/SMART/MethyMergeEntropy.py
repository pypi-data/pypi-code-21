#!/usr/bin/env python
'''
Created on 2013.11.11

@author: liuhongbo
'''
import gzip
import Folderprocess
import NewEntropy
import time
import scipy.stats
import scipy.spatial
import os
import sys
from math import sqrt

class MethyMergeEntropy():
    '''
    This module is used merge multiple profiles of the methylation in a chrome into an combined file
    100003153    100
    1000170    26
    1000190    65
    1000191    67
    1000198    74
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
    def Mergehashnull(self,chrome,Chromedirpath,OutFolderName):
        '''
        Constructor
        Read the methylation data in bed.gz, and combind all values into a file, Null is -1
        '''
        Chromemethyfile=gzip.open(OutFolderName+chrome+".txt.gz",'wb')
        Firstline=chrome
        #Build a hash        
        Methyhash={}
        MethyFolder=Folderprocess.Folderprocess()
        filenames=MethyFolder.readFolderfile(Chromedirpath)
        #print filenames
        column=0 
        for filename in filenames:
            Firstline=Firstline+"\t"+filename
            column=column+1
            methyfile=gzip.open(filename,'rb')
            methyfile.readline()
            filecontent=methyfile.readline()
            while filecontent:
                filecontent=filecontent.strip('\n')
                methyinfor=filecontent.split('\t')
                Methyhash[(methyinfor[0],column)]=methyinfor[1]   #key is the location of C and the column, value is the methylation level
                filecontent=methyfile.readline()
        Chromemethyfile.write(Firstline)
        #Obtain the keys
        MethyLocation=[]
        MethyKeys=Methyhash.keys()
        for i in range(0,len(MethyKeys)):
            MethyLocation.append(MethyKeys[i][0])
        MethyKeys=[]    #
        #Remove the repeat and Sort the location of C
        MethyLocation=list(set(MethyLocation))
        MethyLocation.sort(key=int)
        #Visit the hash and Output methy values
        for methyrow in range(0,len(MethyLocation)):
            methyline=MethyLocation[methyrow]
            for methycolumn in range(1,column+1):
                methyvalue=Methyhash.get((MethyLocation[methyrow],methycolumn),-1)
                methyline=methyline+"\t"+str(methyvalue)
            Chromemethyfile.write(methyline+"\n")
        #MethyLocation=[]
        #Methyhash={}

    def Mergehash(self,chrome,Chromedirpath,OutFolderName):
        '''
        Constructor
        Read the methylation data in bed.gz, and combind all values into a file without null -1
        '''
        Chromemethyfile=gzip.open(OutFolderName+chrome+".txt.gz",'wb')
        Firstline=chrome
        #Build a hash        
        Methyhash={}
        MethyFolder=Folderprocess.Folderprocess()
        filenames=MethyFolder.readFolderfile(Chromedirpath)
        #print filenames
        column=0 
        for filename in filenames:
            Firstline=Firstline+"\t"+filename
            column=column+1
            methyfile=gzip.open(filename,'rb')
            methyfile.readline()
            filecontent=methyfile.readline()
            while filecontent:
                filecontent=filecontent.strip('\n')
                methyinfor=filecontent.split('\t')
                Methyhash[(methyinfor[0],column)]=methyinfor[1]   #key is the location of C and the column, value is the methylation level
                filecontent=methyfile.readline()
        Chromemethyfile.write(Firstline)
        #Obtain the keys
        MethyLocation=[]
        MethyKeys=Methyhash.keys()
        for i in range(0,len(MethyKeys)):
            MethyLocation.append(MethyKeys[i][0])
        MethyKeys=[]    #
        #Remove the repeat and Sort the location of C
        MethyLocation=list(set(MethyLocation))
        MethyLocation.sort(key=int)
        #Visit the hash and Output methy values
        for methyrow in range(0,len(MethyLocation)):
            methyline=MethyLocation[methyrow]
            for methycolumn in range(1,column+1):
                methyvalue=Methyhash.get((MethyLocation[methyrow],methycolumn),-1)
                methyline=methyline+"\t"+str(methyvalue)
            if methyline.find("-1")<0:
                Chromemethyfile.write(methyline+"\n")
        #MethyLocation=[]
        #Methyhash={}
        
        
    def Mergehashmean(self,chrome,Chromedirpath,OutFolderName):
        '''
        Constructor
        Read the methylation data in bed.gz, and compute the mean of repeat samples, then calculate the entropy, at last combind all values into a file without null -1
        '''
        Chromemethyfile=gzip.open(OutFolderName+chrome+".txt.gz",'wb')
        Firstline=chrome          
        MethyFolder=Folderprocess.Folderprocess()
        filenames=MethyFolder.readFolderfile(Chromedirpath)
        #Obtain the repeat samples and store them into a dictionary
        filehash={}
        Samplelist=[]
        for filename in filenames:
            fileinfor=filename.split('Rep')
            Sample=fileinfor[0].split('MethylRrbs')[1]
            value=filehash.get(Sample,'')
            if value=='':
                filehash[Sample]=[filename]
                Samplelist.append(Sample)
                Firstline=Firstline+"\t"+Sample
            else:
                filehash[Sample].append(filename)
        Chromemethyfile.write(Firstline+"\n")
        
        #Build a hash        
        Methyhash={}
        for filename in filenames:
            methyfile=gzip.open(filename,'rb')
            methyfile.readline()
            filecontent=methyfile.readline()
            while filecontent:
                filecontent=filecontent.strip('\n')
                methyinfor=filecontent.split('\t')
                Methyhash[(methyinfor[0],filename)]=methyinfor[1]   #key is the location of C and the column, value is the methylation level
                filecontent=methyfile.readline()
        
        #Obtain the keys
        MethyLocation=[]
        MethyKeys=Methyhash.keys()
        for i in range(0,len(MethyKeys)):
            MethyLocation.append(MethyKeys[i][0])
        MethyKeys=[]    #
        #Remove the repeat and Sort the location of C
        MethyLocation=list(set(MethyLocation))
        MethyLocation.sort(key=int)
        
        #Visit the hash and Output methy values
        for methyrow in range(0,len(MethyLocation)):
            methyline=MethyLocation[methyrow]
            for Sample in Samplelist:
                SampleRepFiles=filehash.get(Sample,-1)
                MethySum=0
                Count=0
                for SampleRepFile in SampleRepFiles:
                    methyvalue=int(Methyhash.get((MethyLocation[methyrow],SampleRepFile),-1))
                    if methyvalue>=0:
                        MethySum=MethySum+methyvalue
                        Count=Count+1
                        #print Count
                if Count>0: #If at least one of the repeat sample has methylation value, compute the mean methylation level and record it
                    methyline=methyline+"\t"+str(MethySum/Count)
                    #print methyline
                else:  #If there are no methylation values in all repeat samples, exit current loop and set the methyline is null
                    methyline=''
                    break
            if methyline!='':  #IF methyline is not null, out put it into file
                Chromemethyfile.write(methyline+"\n")
        MethyLocation=[]
        Methyhash={}
        
        
    def MergehashmeanEntropy(self,chrome,Chromedirpath,OutFolderName,MaxMethyValue):
        '''
        Constructor
        Read the methylation data in bed.gz, and combind all values into a file without null -1
        '''
        Chromemethyfile=gzip.open(OutFolderName+chrome+".txt.gz",'wb')
        Firstline=chrome          
        MethyFolder=Folderprocess.Folderprocess()
        filenames=MethyFolder.readFolderfile(Chromedirpath)
        Methyentropy=NewEntropy.Entropy()
        Methyentropy.MaxMethylationLevel=MaxMethyValue
        #Obtain the repeat samples and store them into a dictionary
        filehash={}
        Samplelist=[]
        for filename in filenames:
            fileinfor=filename.split('Rep')
            Sample=fileinfor[0].split('MethylRrbs')[1]
            value=filehash.get(Sample,'')
            if value=='':
                filehash[Sample]=[filename]
                Samplelist.append(Sample)
                Firstline=Firstline+"\t"+Sample
            else:
                filehash[Sample].append(filename)
        Chromemethyfile.write(Firstline+"\tEntropy\n")
        
        #Build a hash        
        Methyhash={}
        for filename in filenames:
            methyfile=gzip.open(filename,'rb')
            methyfile.readline()
            filecontent=methyfile.readline()
            while filecontent:
                filecontent=filecontent.strip('\n')
                methyinfor=filecontent.split('\t')
                Methyhash[(methyinfor[0],filename)]=methyinfor[1]   #key is the location of C and the column, value is the methylation level
                filecontent=methyfile.readline()
        
        #Obtain the keys
        MethyLocation=[]
        MethyKeys=Methyhash.keys()
        for i in range(0,len(MethyKeys)):
            MethyLocation.append(MethyKeys[i][0])
        MethyKeys=[]    #
        #Remove the repeat and Sort the location of C
        MethyLocation=list(set(MethyLocation))
        MethyLocation.sort(key=int)
        
        #Visit the hash and Output methy values
        for methyrow in range(0,len(MethyLocation)):
            methyline=MethyLocation[methyrow]
            MethydataSet=[]
            for Sample in Samplelist:
                SampleRepFiles=filehash.get(Sample,-1)
                MethySum=0
                Count=0
                for SampleRepFile in SampleRepFiles:
                    methyvalue=int(Methyhash.get((MethyLocation[methyrow],SampleRepFile),-1))
                    if methyvalue>=0:
                        MethySum=MethySum+methyvalue
                        Count=Count+1
                        #print Count
                if Count>0: #If at least one of the repeat sample has methylation value, compute the mean methylation level and record it
                    Methymeanvalue=MethySum/Count
                    MethydataSet.append(Methymeanvalue)
                    methyline=methyline+"\t"+str(Methymeanvalue)
                    #print methyline
                else:  #If there are no methylation values in all repeat samples, exit current loop and set the methyline is null
                    methyline=''
                    break
            if methyline!='':  #IF methyline is not null, out put it into file
                MethydataSet=tuple(MethydataSet)
                Entropyvalue=round(Methyentropy.EntropyCalculate(MethydataSet),3)
                methyline=methyline+"\t"+str(Entropyvalue)+"\n"
                Chromemethyfile.write(methyline)
                #print MethyLocation[methyrow]+MethydataSet+str(Methyentropy.EntropyCalculate(MethydataSet[1:]))
        MethyLocation=[]
        Methyhash={}
        
    def MergehashBSSeqWigGzEntropy(self,chrome,Chromedirpath,OutFolderName,MaxMethyValue):
        '''
        Constructor
        Based on hash, need more Memory
        Read the methylation data in wig.gz, and combind all values into a file without null -1
        '''
        Chromemethyfile=gzip.open(OutFolderName+chrome+".txt.gz",'wb')
        Firstline=chrome          
        MethyFolder=Folderprocess.Folderprocess()
        filenames=MethyFolder.readFolderfile(Chromedirpath)
        Methyentropy=NewEntropy.Entropy()
        Methyentropy.MaxMethylationLevel=MaxMethyValue
        #Obtain the repeat samples and store them into a dictionary
        filehash={}
        Samplelist=[]
        for filename in filenames:
            fileinfor=filename.split('.Bisulfite-Seq.')
            Sample=fileinfor[0].split('UCSD.')[1]
            value=filehash.get(Sample,'')
            if value=='':
                filehash[Sample]=[filename]
                Samplelist.append(Sample)
                Firstline=Firstline+"\t"+Sample
            else:
                filehash[Sample].append(filename)
        Chromemethyfile.write(Firstline+"\tEntropy\n")
        
        #Build a hash        
        Methyhash={}
        for filename in filenames:
            methyfile=gzip.open(filename,'rb')
            methyfile.readline()
            filecontent=methyfile.readline()
            while filecontent:
                filecontent=filecontent.strip('\n')
                methyinfor=filecontent.split('\t')
                Methyhash[(methyinfor[0],filename)]=methyinfor[1]   #key is the location of C and the column, value is the methylation level
                filecontent=methyfile.readline()
        
        #Obtain the keys
        MethyLocation=[]
        MethyKeys=Methyhash.keys()
        for i in range(0,len(MethyKeys)):
            MethyLocation.append(MethyKeys[i][0])
        MethyKeys=[]    #
        #Remove the repeat and Sort the location of C
        MethyLocation=list(set(MethyLocation))
        MethyLocation.sort(key=int)
        
        #Visit the hash and Output methy values
        for methyrow in range(0,len(MethyLocation)):
            methyline=MethyLocation[methyrow]
            MethydataSet=[]
            for Sample in Samplelist:
                SampleRepFiles=filehash.get(Sample,-1)
                MethySum=0
                Count=0
                for SampleRepFile in SampleRepFiles:
                    methyvalue=int(Methyhash.get((MethyLocation[methyrow],SampleRepFile),-1))
                    if methyvalue>=0:
                        MethySum=MethySum+methyvalue
                        Count=Count+1
                        #print Count
                if Count>0: #If at least one of the repeat sample has methylation value, compute the mean methylation level and record it
                    Methymeanvalue=MethySum/Count
                    MethydataSet.append(Methymeanvalue)
                    methyline=methyline+"\t"+str(Methymeanvalue)
                    #print methyline
                else:  #If there are no methylation values in all repeat samples, exit current loop and set the methyline is null
                    methyline=''
                    break
            if methyline!='':  #IF methyline is not null, out put it into file
                MethydataSet=tuple(MethydataSet)
                Entropyvalue=round(Methyentropy.EntropyCalculate(MethydataSet),3)
                methyline=methyline+"\t"+str(Entropyvalue)+"\n"
                Chromemethyfile.write(methyline)
                #print MethyLocation[methyrow]+MethydataSet+str(Methyentropy.EntropyCalculate(MethydataSet[1:]))
        MethyLocation=[]
        Methyhash={}
        
    def MergefileBSSeqWigGznoRepEntropybase0(self,chrome,ChromeCfileName,Chromedirpath,OutFolderName,MaxMethyValue):
        '''
        Constructor
        Based on files, only need file input and output
        C file is 0 based
        Methylation data is 0 based
        Read the methylation data in wig.gz, and combind all values into a file without null -1
        '''
        ChromeCfile=gzip.open(ChromeCfileName,'rb')   #open the C file of the chrome
        MergedChromemethyfile=gzip.open(OutFolderName+chrome+".txt.gz",'wb') #open the output file
        Firstline=ChromeCfile.readline().strip('\n')          
        MethyFolder=Folderprocess.Folderprocess()
        filenames=MethyFolder.readFolderfile(Chromedirpath)
        Methyentropy=NewEntropy.Entropy()
        Methyentropy.MaxMethylationLevel=MaxMethyValue
        #Open the methy flies and store file handles into a dictionary; Obtain the sample names and store them into a list
        methyfilehandles={}
        CurrentSampleline={}
        Samplelist=[]
        CNum=0
        for filename in filenames:
            #Obtain the sample names and store them into a list
            fileinfor=filename.split('.Bisulfite-Seq.')
            Sample=fileinfor[0].split('UCSD.')[1]
            value=methyfilehandles.get(Sample,'')
            if value=='':
                chromemethyfile=gzip.open(filename,'rb')
                methyfilehandles[Sample]=chromemethyfile  #build a dictionary of methy files: key is sample, value is the file Handle
                CurrentSampleline[Sample]=chromemethyfile.readline()  #build a dictionary of methy files: key is sample, value is the file Handle
                Samplelist.append(Sample)
                Firstline=Firstline+"\t"+Sample
        MergedChromemethyfile.write(Firstline+"\tEntropy\n")
        
        #Merge the methy files
        CurrentCline=ChromeCfile.readline()
        PreviousC=0
        while CurrentCline:
            methyline=CurrentCline.strip('\n')
            print methyline
            CurrentCinfor=methyline.split('\t')
            CurrentC=int(CurrentCinfor[0])
            if (CurrentC-PreviousC)>10000000:
                print CurrentC
                PreviousC=CurrentC
            MethydataSet=[]
            SampleNum=0
            while SampleNum<len(Samplelist) and methyline!='':
                Sample=Samplelist[SampleNum]
                chromemethyfile=methyfilehandles.get(Sample,-1) #Obtain the sample file and compare their location
                filecontent=CurrentSampleline.get(Sample,'over')
                if filecontent=='':   #If filecontent=='', at least one methyfile has been over.
                    CurrentCline=False
                    break
                methyinfor=filecontent.strip('\n').split('\t')
                if int(methyinfor[0])==CurrentC:  #If current C is equal, give it to output line and MethydataSet[]
                    methyvalue=round(float(methyinfor[1]),3)
                    methyline=methyline+"\t"+str(methyvalue)
                    MethydataSet.append(methyvalue)
                    CurrentSampleline[Sample]=chromemethyfile.readline()
                elif int(methyinfor[0])<CurrentC:  #If current C is larger, go on in the methy file
                    Currentfileline=chromemethyfile.readline()
                    while Currentfileline:
                        methyinfor=Currentfileline.strip('\n').split('\t')
                        if int(methyinfor[0])<CurrentC:
                            Currentfileline=chromemethyfile.readline()
                            CurrentSampleline[Sample]=Currentfileline
                        elif int(methyinfor[0])==CurrentC:
                            methyvalue=round(float(methyinfor[1]),3)
                            methyline=methyline+"\t"+str(methyvalue)
                            MethydataSet.append(methyvalue)
                            CurrentSampleline[Sample]=chromemethyfile.readline()
                            Currentfileline=False
                        else:
                            CurrentSampleline[Sample]=Currentfileline
                            Currentfileline=False
                elif int(methyinfor[0])>CurrentC:  #If current C is smaller, go on in the C file
                    CurrentCline=ChromeCfile.readline()
                    while CurrentCline:
                        CurrentCinfor=CurrentCline.split('\t')
                        if int(methyinfor[0])<=int(CurrentCinfor[0]):
                            methyline=''
                            break
                        else:
                            CurrentCline=ChromeCfile.readline()                
                SampleNum+=1
            if len(MethydataSet)==len(Samplelist):  #IF methyline is not null, out put it into file
                MethydataSet=tuple(MethydataSet)
                Entropyvalue=round(Methyentropy.EntropyCalculate(MethydataSet),3)
                methyline=methyline+"\t"+str(Entropyvalue)+"\n"
                MergedChromemethyfile.write(methyline)
                CNum+=1
        ChromeCfile.close()
        MergedChromemethyfile.close()
        for Sample in Samplelist: methyfilehandles.get(Sample,-1).close()
        print chrome+"\tC Num is\t"+str(CNum)
        
        
    def MergefileBSSeqWigGznoRepEntropyCbase0Methybase1(self,chrome,ChromeCfileName,Chromedirpath,OutFolderName,MaxMethyValue):
        '''
        Constructor
        Based on files, only need file input and output
        C file is 0 based
        Methylation data is 1 based
        output is 1 based
        Read the methylation data in wig.gz, and combind all values into a file without null -1
        '''
        ChromeCfile=gzip.open(ChromeCfileName,'rb')   #open the C file of the chrome
        MergedChromemethyfile=gzip.open(OutFolderName+chrome+".txt.gz",'wb') #open the output file
        Firstline=ChromeCfile.readline().strip('\n')          
        MethyFolder=Folderprocess.Folderprocess()
        filenames=MethyFolder.readFolderfile(Chromedirpath)
        Methyentropy=NewEntropy.Entropy()
        Methyentropy.MaxMethylationLevel=MaxMethyValue
        #Open the methy flies and store file handles into a dictionary; Obtain the sample names and store them into a list
        methyfilehandles={}
        CurrentSampleline={}
        Samplelist=[]
        CNum=0
        for filename in filenames:
            #Obtain the sample names and store them into a list
            fileinfor=filename.split('.Bisulfite-Seq.')
            Sample=fileinfor[0].split('UCSD.')[1]
            value=methyfilehandles.get(Sample,'')
            if value=='':
                chromemethyfile=gzip.open(filename,'rb')
                methyfilehandles[Sample]=chromemethyfile  #build a dictionary of methy files: key is sample, value is the file Handle
                CurrentSampleline[Sample]=chromemethyfile.readline()  #build a dictionary of methy files: key is sample, value is the file Handle
                Samplelist.append(Sample)
                Firstline=Firstline+"\t"+Sample
        MergedChromemethyfile.write(Firstline+"\tEntropy\n")
        
        #Merge the methy files
        CurrentCline=ChromeCfile.readline()
        PreviousC=0
        while CurrentCline:
            CurrentCline=CurrentCline.strip('\n')
            CurrentCinfor=CurrentCline.split('\t')
            CurrentC=int(CurrentCinfor[0])+1
            if (CurrentC-PreviousC)>10000000:
                print CurrentC
                PreviousC=CurrentC
            methyline=CurrentCline.replace(CurrentCinfor[0],str(CurrentC))
            #print methyline
            MethydataSet=[]
            SampleNum=0
            while SampleNum<len(Samplelist) and methyline!='':
                Sample=Samplelist[SampleNum]
                SampleNum+=1
                chromemethyfile=methyfilehandles.get(Sample,-1) #Obtain the sample file and compare their location
                filecontent=CurrentSampleline.get(Sample,'over')
                if filecontent=='' or filecontent=="over" or len(filecontent)<=3: #a methyfile is over
                    CurrentCline=False
                    break
                methyinfor=filecontent.strip('\n').split('\t')
                if int(methyinfor[0])==CurrentC:  #If current C is equal, give it to output line and MethydataSet[]
                    methyvalue=round(float(methyinfor[1]),3)
                    methyline=methyline+"\t"+str(methyvalue)
                    MethydataSet.append(methyvalue)
                    Currentfileline=chromemethyfile.readline()
                    CurrentSampleline[Sample]=Currentfileline
                elif int(methyinfor[0])<CurrentC:  #If current C is larger, go on in the methy file
                    Currentfileline=chromemethyfile.readline()
                    while Currentfileline:
                        methyinfor=Currentfileline.strip('\n').split('\t')
                        if int(methyinfor[0])<CurrentC:
                            Currentfileline=chromemethyfile.readline()
                            CurrentSampleline[Sample]=Currentfileline
                        elif int(methyinfor[0])==CurrentC:
                            methyvalue=round(float(methyinfor[1]),3)
                            methyline=methyline+"\t"+str(methyvalue)
                            MethydataSet.append(methyvalue)
                            Currentfileline=chromemethyfile.readline()
                            CurrentSampleline[Sample]=Currentfileline
                            Currentfileline=False
                            break
                        elif len(Currentfileline)>3:
                            CurrentSampleline[Sample]=Currentfileline
                            Currentfileline=False
                            break
                elif int(methyinfor[0])>CurrentC:  #If current C is smaller, go on in the C file
                    CurrentCline=ChromeCfile.readline()
                    while CurrentCline:
                        CurrentCinfor=CurrentCline.split('\t')
                        CurrentC=int(CurrentCinfor[0])+1
                        if int(methyinfor[0])<=CurrentC:
                            methyline=''
                            break
                        else:
                            CurrentCline=ChromeCfile.readline()                
            if len(MethydataSet)==len(Samplelist):  #IF methyline is not null, out put it into file
                MethydataSet=tuple(MethydataSet)
                Entropyvalue=round(Methyentropy.EntropyCalculate(MethydataSet),3)
                methyline=methyline+"\t"+str(Entropyvalue)+"\n"
                MergedChromemethyfile.write(methyline)
                CNum+=1
        ChromeCfile.close()
        MergedChromemethyfile.close()
        for Sample in Samplelist: methyfilehandles.get(Sample,-1).close()
        print chrome+"\tC Num is\t"+str(CNum)
        
    def MergefileBSSeqWigGznoRepEntropyCbase1Methybase1(self,chrome,ChromeCfileName,Chromedirpath,OutFolderName,MaxMethyValue):
        '''
        Constructor
        Based on files, only need file input and output
        C file is 1 based
        Methylation data is 1 based
        output is 1 based
        Read the methylation data in wig.gz, and combind all values into a file without null -1
        '''
        ChromeCfile=gzip.open(ChromeCfileName,'rb')   #open the C file of the chrome
        MergedChromemethyfile=gzip.open(OutFolderName+chrome+".txt.gz",'wb') #open the output file
        EntropyWig=gzip.open(MergedmethyFolderName+"EntropyNWIE.wig.gz",'a') #Open a wig file 
        EntropyWig.write("variableStep chrom="+chrome+"\n")
        Firstline=ChromeCfile.readline().strip('\n')          
        MethyFolder=Folderprocess.Folderprocess()
        filenames=MethyFolder.readFolderfile(Chromedirpath)
        Methyentropy=NewEntropy.Entropy()
        #Open the methy flies and store file handles into a dictionary; Obtain the sample names and store them into a list
        methyfilehandles={}
        CurrentSampleline={}
        Samplelist=[]
        CNum=0
        for filename in filenames:
            #Obtain the sample names and store them into a list
            fileinfor=filename.split('.Bisulfite-Seq.')
            Sample=fileinfor[0].split('GSM')[1]
            value=methyfilehandles.get(Sample,'')
            if value=='':
                chromemethyfile=gzip.open(filename,'rb')
                methyfilehandles[Sample]=chromemethyfile  #build a dictionary of methy files: key is sample, value is the file Handle
                CurrentSampleline[Sample]=chromemethyfile.readline()  #build a dictionary of methy files: key is sample, value is the file Handle
                Samplelist.append(Sample)
                Firstline=Firstline+"\t"+Sample
        MergedChromemethyfile.write(Firstline+"\tEntropy\n")
        
        #Merge the methy files
        CurrentCline=ChromeCfile.readline()
        PreviousC=0
        while CurrentCline:
            CurrentCline=CurrentCline.strip('\n')
            CurrentCinfor=CurrentCline.split('\t')
            CurrentC=int(CurrentCinfor[0])
            if (CurrentC-PreviousC)>10000000:
                print CurrentC
                PreviousC=CurrentC
            methyline=CurrentCline.replace(CurrentCinfor[0],str(CurrentC))
            #print methyline
            MethydataSet=[]
            SampleNum=0
            while SampleNum<len(Samplelist) and methyline!='':
                Sample=Samplelist[SampleNum]
                SampleNum+=1
                chromemethyfile=methyfilehandles.get(Sample,-1) #Obtain the sample file and compare their location
                filecontent=CurrentSampleline.get(Sample,'over')
                if filecontent=='' or filecontent=="over" or len(filecontent)<=3: #a methyfile is over
                    CurrentCline=False
                    break
                methyinfor=filecontent.strip('\n').split('\t')
                if int(methyinfor[0])==CurrentC:  #If current C is equal, give it to output line and MethydataSet[]
                    methyvalue=round(float(methyinfor[1]),3)
                    methyline=methyline+"\t"+str(methyvalue)
                    MethydataSet.append(methyvalue)
                    Currentfileline=chromemethyfile.readline()
                    CurrentSampleline[Sample]=Currentfileline
                elif int(methyinfor[0])<CurrentC:  #If current C is larger, go on in the methy file
                    Currentfileline=chromemethyfile.readline()
                    while Currentfileline:
                        methyinfor=Currentfileline.strip('\n').split('\t')
                        if int(methyinfor[0])<CurrentC:
                            Currentfileline=chromemethyfile.readline()
                            CurrentSampleline[Sample]=Currentfileline
                        elif int(methyinfor[0])==CurrentC:
                            methyvalue=round(float(methyinfor[1]),3)
                            methyline=methyline+"\t"+str(methyvalue)
                            MethydataSet.append(methyvalue)
                            Currentfileline=chromemethyfile.readline()
                            CurrentSampleline[Sample]=Currentfileline
                            Currentfileline=False
                            break
                        elif len(Currentfileline)>3:
                            CurrentSampleline[Sample]=Currentfileline
                            Currentfileline=False
                            break
                elif int(methyinfor[0])>CurrentC:  #If current C is smaller, go on in the C file
                    CurrentCline=ChromeCfile.readline()
                    while CurrentCline:
                        CurrentCinfor=CurrentCline.split('\t')
                        CurrentC=int(CurrentCinfor[0])
                        if int(methyinfor[0])<=CurrentC:
                            methyline=''
                            break
                        else:
                            CurrentCline=ChromeCfile.readline()                
            if len(MethydataSet)==len(Samplelist):  #IF methyline is not null, out put it into file
                for i in range(len(MethydataSet)):
                    MethydataSet[i]=MethydataSet[i]*100.0/MaxMethyValue
                MethydataSet=tuple(MethydataSet)
                Entropyvalue=Methyentropy.EntropyCalculate(MethydataSet)
                methyline=methyline+"\t"+str(Entropyvalue)+"\n"
                MergedChromemethyfile.write(methyline)
                EntropyWig.write(str(CurrentC)+"\t"+str(Entropyvalue)+"\n")
                CNum+=1
        ChromeCfile.close()
        MergedChromemethyfile.close()
        for Sample in Samplelist: methyfilehandles.get(Sample,-1).close()
        statisticout=open(MergedmethyFolderName+"statistic.txt",'a')
        print chrome+"\tC Num is\t"+str(CNum)
        statisticout.write(chrome+"\tC Num is\t"+str(CNum)+"\n")
        statisticout.close()
        EntropyWig.close()
   
    def MergefileBSSeqWigGznoRepEntropyCbase1Methybase1PCC(self,chrome,ChromeCfileName,Chromedirpath,OutFolderName,MaxMethyValue):
        '''
        Constructor
        Based on files, only need file input and output
        C file is 1 based
        Methylation data is 1 based
        output is 1 based
        Read the methylation data in wig.gz, and combind all values into a file without null -1
        Caculate the pcc between neighbring CpG
        '''
        ChromeCfile=gzip.open(ChromeCfileName,'rb')   #open the C file of the chrome
        MergedChromemethyfile=gzip.open(OutFolderName+chrome+".txt.gz",'wb') #open the output file
        EntropyWig=gzip.open(MergedmethyFolderName+"EntropyNWIE.wig.gz",'a') #Open a wig file 
        EntropyWig.write("variableStep chrom="+chrome+"\n")
        Firstline=ChromeCfile.readline().strip('\n')          
        MethyFolder=Folderprocess.Folderprocess()
        filenames=MethyFolder.readFolderfile(Chromedirpath)
        Methyentropy=NewEntropy.Entropy()
        #Open the methy flies and store file handles into a dictionary; Obtain the sample names and store them into a list
        methyfilehandles={}
        CurrentSampleline={}
        Samplelist=[]
        CNum=0
        for filename in filenames:
            #Obtain the sample names and store them into a list
            fileinfor=filename.split('.Bisulfite-Seq.')
            Sample=fileinfor[0].split('GSM')[1]
            value=methyfilehandles.get(Sample,'')
            if value=='':
                chromemethyfile=gzip.open(filename,'rb')
                methyfilehandles[Sample]=chromemethyfile  #build a dictionary of methy files: key is sample, value is the file Handle
                CurrentSampleline[Sample]=chromemethyfile.readline()  #build a dictionary of methy files: key is sample, value is the file Handle
                Samplelist.append(Sample)
                Firstline=Firstline+"\t"+Sample
        MergedChromemethyfile.write(Firstline+"\tEntropy\tPCC\tpvalue\n")
        
        #Merge the methy files #calculate the entropy and pcc
        CurrentCline=ChromeCfile.readline()
        PreviousC=0
        while CurrentCline:
            CurrentCline=CurrentCline.strip('\n')
            CurrentCinfor=CurrentCline.split('\t')
            CurrentC=int(CurrentCinfor[0])
            if (CurrentC-PreviousC)>10000000:
                print CurrentC
                PreviousC=CurrentC
            methyline=CurrentCline.replace(CurrentCinfor[0],str(CurrentC))
            #print methyline
            MethydataSet=[]
            SampleNum=0
            while SampleNum<len(Samplelist) and methyline!='':
                Sample=Samplelist[SampleNum]
                SampleNum+=1
                chromemethyfile=methyfilehandles.get(Sample,-1) #Obtain the sample file and compare their location
                filecontent=CurrentSampleline.get(Sample,'over')
                if filecontent=='' or filecontent=="over" or len(filecontent)<=3: #a methyfile is over
                    CurrentCline=False
                    break
                methyinfor=filecontent.strip('\n').split('\t')
                if int(methyinfor[0])==CurrentC:  #If current C is equal, give it to output line and MethydataSet[]
                    methyvalue=round(float(methyinfor[1]),3)
                    methyline=methyline+"\t"+str(methyvalue)
                    MethydataSet.append(methyvalue)
                    Currentfileline=chromemethyfile.readline()
                    CurrentSampleline[Sample]=Currentfileline
                elif int(methyinfor[0])<CurrentC:  #If current C is larger, go on in the methy file
                    Currentfileline=chromemethyfile.readline()
                    while Currentfileline:
                        methyinfor=Currentfileline.strip('\n').split('\t')
                        if int(methyinfor[0])<CurrentC:
                            Currentfileline=chromemethyfile.readline()
                            CurrentSampleline[Sample]=Currentfileline
                        elif int(methyinfor[0])==CurrentC:
                            methyvalue=round(float(methyinfor[1]),3)
                            methyline=methyline+"\t"+str(methyvalue)
                            MethydataSet.append(methyvalue)
                            Currentfileline=chromemethyfile.readline()
                            CurrentSampleline[Sample]=Currentfileline
                            Currentfileline=False
                            break
                        elif len(Currentfileline)>3:
                            CurrentSampleline[Sample]=Currentfileline
                            Currentfileline=False
                            break
                elif int(methyinfor[0])>CurrentC:  #If current C is smaller, go on in the C file
                    CurrentCline=ChromeCfile.readline()
                    while CurrentCline:
                        CurrentCinfor=CurrentCline.split('\t')
                        CurrentC=int(CurrentCinfor[0])
                        if int(methyinfor[0])<=CurrentC:
                            methyline=''
                            break
                        else:
                            CurrentCline=ChromeCfile.readline()                
            if len(MethydataSet)==len(Samplelist):  #IF methyline is not null, calculate the entropy and pcc, out put them into file
                for i in range(len(MethydataSet)):
                    MethydataSet[i]=MethydataSet[i]*100.0/MaxMethyValue
                if CNum==0:
                    PreviousMethydataSet=MethydataSet
                PCC=scipy.stats.pearsonr(PreviousMethydataSet, MethydataSet)   #calculate the PCC between the methylation leveles of current C and previous C
                PreviousMethydataSet=MethydataSet
                MethydataSet=tuple(MethydataSet)
                Entropyvalue=Methyentropy.EntropyCalculate(MethydataSet)
                methyline=methyline+"\t"+str(Entropyvalue)+"\t"+str(round(PCC[0],3))+"\t"+str('%.2e'%PCC[1])+"\n"
                MergedChromemethyfile.write(methyline)
                EntropyWig.write(str(CurrentC)+"\t"+str(Entropyvalue)+"\n")
                CNum+=1
        ChromeCfile.close()
        MergedChromemethyfile.close()
        for Sample in Samplelist: methyfilehandles.get(Sample,-1).close()
        statisticout=open(MergedmethyFolderName+"statistic.txt",'a')
        print chrome+"\tC Num is\t"+str(CNum)
        statisticout.write(chrome+"\tC Num is\t"+str(CNum)+"\n")
        statisticout.close()
        EntropyWig.close()

    def MergefileBSSeqWigGznoRepEntropyCbase1Methybase1DiffEntropyED(self,chrome,ChromeCfileName,Chromedirpath,MergedmethyFolderName,MaxMethyValue,statisticout):
        '''
        Constructor
        Based on files, only need file input and output
        C file is 1 based
        Methylation data is 1 based
        output is 1 based
        Read the methylation data in wig.gz, and combind all values into a file without null -1
        Caculate the DifferEntropy and Euclidean Distance between neighbring CpG
        '''
        ChromeCfile=gzip.open(ChromeCfileName,'rb')   #open the C file of the chrome
        MergedChromemethyfile=gzip.open(MergedmethyFolderName+chrome+".txt.gz",'wb') #open the output file
        EntropyWig=gzip.open(MergedmethyFolderName+"MethylationSpecificity.wig.gz",'a') #Open a wig file 
        EntropyWig.write("variableStep chrom="+chrome+"\n")
        Firstline=ChromeCfile.readline().strip('\n')          
        MethyFolder=Folderprocess.Folderprocess()
        filenames=MethyFolder.readFolderfile(Chromedirpath)
        Methyentropy=NewEntropy.Entropy()
        #Open the methy flies and store file handles into a dictionary; Obtain the sample names and store them into a list
        methyfilehandles={}
        CurrentSampleline={}
        Samplelist=[]
        CNum=0
        TCNum=0
        CommonCNum=0
        for filename in filenames:
            #Obtain the sample names and store them into a list
            fileinfor=filename.split(chrome+'_')
            Sample=fileinfor[1].split('.wig')[0]
            value=methyfilehandles.get(Sample,'')
            if value=='':
                chromemethyfile=gzip.open(filename,'rb')
                methyfilehandles[Sample]=chromemethyfile  #build a dictionary of methy files: key is sample, value is the file Handle
                CurrentSampleline[Sample]=chromemethyfile.readline()  #build a dictionary of methy files: key is sample, value is the file Handle
                Samplelist.append(Sample)
                Firstline=Firstline+"\t"+Sample
        MergedChromemethyfile.write(Firstline+"\tEntropy\tDifferEntropy\tEuclideanDistance\n")
        SampleTotalNum=len(Samplelist)
        SqrtSampleTotalNum=sqrt(SampleTotalNum)
        #Merge the methy files #calculate the entropy and pcc
        CurrentCline=ChromeCfile.readline()
        TCNum=TCNum+1
        PreviousC=0
        while CurrentCline:
            CurrentCline=CurrentCline.strip('\n')
            CurrentCinfor=CurrentCline.split('\t')
            CurrentC=int(CurrentCinfor[0])
            if (CurrentC-PreviousC)>10000000:
                Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
                print Starttime+" Have finished "+str(CurrentC)+" C..."
                PreviousC=CurrentC
            methyline=CurrentCline.replace(CurrentCinfor[0],str(CurrentC))
            #print methyline
            MethydataSet=[]
            SampleNum=0
            while SampleNum<SampleTotalNum and methyline!='':
                Sample=Samplelist[SampleNum]
                SampleNum+=1
                chromemethyfile=methyfilehandles.get(Sample,-1) #Obtain the sample file and compare their location
                filecontent=CurrentSampleline.get(Sample,'over')
                if filecontent=='' or filecontent=="over" or len(filecontent)<=3: #a methyfile is over
                    CurrentCline=False
                    break
                methyinfor=filecontent.strip('\n').split('\t')
                if int(methyinfor[0])==CurrentC:  #If current C is equal, give it to output line and MethydataSet[]
                    methyvalue=round(float(methyinfor[1]),3)
                    methyline=methyline+"\t"+str(methyvalue)
                    MethydataSet.append(methyvalue)
                    Currentfileline=chromemethyfile.readline()
                    CurrentSampleline[Sample]=Currentfileline
                elif int(methyinfor[0])<CurrentC:  #If current C is larger, go on in the methy file
                    Currentfileline=chromemethyfile.readline()
                    while Currentfileline:
                        methyinfor=Currentfileline.strip('\n').split('\t')
                        if int(methyinfor[0])<CurrentC:
                            Currentfileline=chromemethyfile.readline()
                            CurrentSampleline[Sample]=Currentfileline
                        elif int(methyinfor[0])==CurrentC:
                            methyvalue=round(float(methyinfor[1]),3)
                            methyline=methyline+"\t"+str(methyvalue)
                            MethydataSet.append(methyvalue)
                            Currentfileline=chromemethyfile.readline()
                            CurrentSampleline[Sample]=Currentfileline
                            Currentfileline=False
                            break
                        elif len(Currentfileline)>3:
                            CurrentSampleline[Sample]=Currentfileline
                            Currentfileline=False
                            break
                elif int(methyinfor[0])>CurrentC:  #If current C is smaller, go on in the C file
                    CurrentCline=ChromeCfile.readline()
                    TCNum=TCNum+1
                    while CurrentCline:
                        CurrentCinfor=CurrentCline.split('\t')
                        CurrentC=int(CurrentCinfor[0])
                        if int(methyinfor[0])<=CurrentC:
                            methyline=''
                            break
                        else:
                            CurrentCline=ChromeCfile.readline()
                            TCNum=TCNum+1            
            if len(MethydataSet)==SampleTotalNum:  #IF methyline is not null, calculate the entropy and pcc, out put them into file
                CommonCNum=CommonCNum+1
                for i in range(len(MethydataSet)):
                    MethydataSet[i]=MethydataSet[i]*100.0/MaxMethyValue
                if CNum==0:
                    PreviousMethydataSet=MethydataSet
                EucDistance=scipy.spatial.distance.euclidean(PreviousMethydataSet, MethydataSet)/100/SqrtSampleTotalNum  #calculate the euclidean distance between the methylation leveles of current C and previous C
                #PCC=scipy.stats.pearsonr(PreviousMethydataSet, MethydataSet)   #calculate the PCC between the methylation leveles of current C and previous C
                #DifferMethydataSet=(PreviousMethydataSet-MethydataSet+1)/2
                DifferMethydataSet=list(map(lambda x: abs(x[0]-x[1]), zip(PreviousMethydataSet, MethydataSet)))
                #print PreviousMethydataSet
                #print MethydataSet
                #print DifferMethydataSet
                PreviousMethydataSet=MethydataSet
                MethydataSet=tuple(MethydataSet)
                MethySpecificity=1.0-Methyentropy.EntropyCalculate(MethydataSet)
                DifferMethydataSet=tuple(DifferMethydataSet)
                DifferEntropyvalue=Methyentropy.EntropyCalculate(DifferMethydataSet)
                methyline=methyline+"\t"+str(MethySpecificity)+"\t"+str(DifferEntropyvalue)+"\t"+str(round(EucDistance,3))+"\n"
                MergedChromemethyfile.write(methyline)
                EntropyWig.write(str(CurrentC)+"\t"+str(MethySpecificity)+"\n")
                CNum+=1
        ChromeCfile.close()
        MergedChromemethyfile.close()
        for Sample in Samplelist: methyfilehandles.get(Sample,-1).close()
        EntropyWig.close()
        return TCNum,CommonCNum     

    def run(self,chromes,CFolderName,OutFolder,statisticout):
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to calculate methylation specificiy ..."
        statisticout.write(Starttime+" Start to calculate methylation specificiy ...\n")
        MaxMethyValue=1    #The max methylation level,default is 1
        
        MethyDataFolderName=OutFolder+'SplitedMethy/'
        MergedmethyFolderName=OutFolder+'MethylationSpecificity/'
        if MergedmethyFolderName:
                # use a output directory to store merged Methylation data 
                if not os.path.exists( MergedmethyFolderName ):
                    try:
                        os.makedirs( MergedmethyFolderName )
                    except:
                        sys.exit( "Output directory (%s) could not be created. Terminating program." % MergedmethyFolderName )
        EntropyWig=gzip.open(MergedmethyFolderName+"MethylationSpecificity.wig.gz",'wb') #Biult a wig file 
        EntropyWig.write("track type=wiggle_0 name=\"Methylation Specificity of across Samples\" visibility=full color=20,150,20 altColor=150,20,20 windowingFunction=mean\n")
        EntropyWig.close()
        MethyMerge=MethyMergeEntropy()
        TotalCNum=0
        TotalCommonCNum=0
        for i in range(0,len(chromes)):
                ChromeCfileName=CFolderName+chromes[i]+".txt.gz"
                Chromedirpath=MethyDataFolderName+chromes[i]+"/*.wig.gz"
                Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
                print Starttime+" Calculating Methylation Specificity for "+chromes[i]
                statisticout.write(Starttime+" Calculating Methylation Specificity for "+chromes[i]+"\n")
                TCNum,CommonCNum=MethyMerge.MergefileBSSeqWigGznoRepEntropyCbase1Methybase1DiffEntropyED(chromes[i],ChromeCfileName,Chromedirpath,MergedmethyFolderName,MaxMethyValue,statisticout)
                TotalCNum=TotalCNum+TCNum
                TotalCommonCNum=TotalCommonCNum+CommonCNum
        return TotalCNum,TotalCommonCNum



if __name__ == '__main__':
    Starttime=time.strftime('%Y-%m-%d %A %X',time.localtime(time.time()))
    MaxMethyValue=1
    #RRBS
    chromes=['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chrX','chrY','chrM']
    #chromes=['chr1','chr2']
    #MethyDataFolderName='J:/DNAMethylationData/ENCODE_RRBS/MergedRRBS/'
    #MergedmethyFolderName='J:/DNAMethylationData/ENCODE_RRBS/MergedRRBS/Mergedmethy/'
    #WaveletEntropyFolderName='J:/DNAMethylationData/ENCODE_RRBS/MergedRRBS/WaveletEntropy/'
    #BS-seq
    #chromes=['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chrX','chrY']
    #chromes=['chrM','chrY']
    CFolderName='J:/HumanHg19Seq/ScanCresult/'
    MethyDataFolderName='J:/DNAMethylation/Human/BSSeq/RoadmapBSSeq/20140530_usedMerged_90percent/'
    MergedmethyFolderName=MethyDataFolderName+'MethylationSpecificity20140531/'
    statisticout=open(MergedmethyFolderName+"statistic.txt",'w')
    statisticout.write(Starttime+"\n")
    EntropyWig=gzip.open(MergedmethyFolderName+"MethylationSpecificity.wig.gz",'wb') #Biult a wig file 
    EntropyWig.write("track type=wiggle_0 name=\"Methylation Specificity of Human Tissues\" visibility=full color=20,150,20 altColor=150,20,20 windowingFunction=mean\n")
    EntropyWig.close()
    statisticout.close()
    #WaveletEntropyFolderName=MethyDataFolderName+'WaveletEntropy/'
    MethyMerge=MethyMergeEntropy()
    for i in range(0,len(chromes)):
            ChromeCfileName=CFolderName+chromes[i]+".txt.gz"
            Chromedirpath=MethyDataFolderName+chromes[i]+"/*.wig.gz"
            print chromes[i]
            MethyMerge.MergefileBSSeqWigGznoRepEntropyCbase1Methybase1DiffEntropyED(chromes[i],ChromeCfileName,Chromedirpath,MergedmethyFolderName,MaxMethyValue)
            #MethyMerge.Wavelet(chromes[i],MergedmethyFolderName,WaveletEntropyFolderName)
    Endtime=time.strftime('%Y-%m-%d %A %X',time.localtime(time.time()))
    statisticout=open(MergedmethyFolderName+"statistic.txt",'a')
    statisticout.write(Endtime+"\n")
    statisticout.close()
