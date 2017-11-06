#!/usr/bin/env python
'''
Created on 2013.11.10

@author: liuhongbo
'''
import glob

class Folderprocess():
    def __init__(self):
        '''
        Constructor
        '''
    def readFolderfile(self,InFolderName):
        '''
        Read the file name in a folder
        '''
        #print "FileIn folder:"+InFolderName
        filenames = glob.glob(InFolderName)
        return filenames



if __name__ == '__main__':
    FolderName='J:/RoadmapBSSeq/20131216_used/*'
    FILENAMEOUT=open("J:/RoadmapBSSeq/UsedFileName.txt",'w')
    VisitFolder=Folderprocess()
    filenames=VisitFolder.readFolderfile(FolderName)
    print filenames
    for filename in filenames:
        FILENAMEOUT.write(filename+"\n")