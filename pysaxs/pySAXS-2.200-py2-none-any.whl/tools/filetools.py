#__all__=['listFiles','getExtension']
"""
general tools for files manipulation
"""
import numpy
import os
import os.path
import time
import sys
import glob

def listFiles(paths,file):
    """
    Searches a path for a specified file.
    ListFile("c:\data",*.rgr") return a list with file *.rgr
    """
    list=[]
    if file=="" or paths=="":
        print """\
        where (Environment) Filespec
        Searches the paths specified in Environment for all files matching Filespec.
        If Environment is not specified, the system PATH is used.\
        """
    #print 'list file : ',paths, file
    for path in paths.split(";"):
        #print "path: ",path+os.sep+file
        #print "glob" ,glob.glob(path+os.sep+file)
        for match in glob.glob(os.path.join(path, file)):
            list.append(match)
    return list

def getExtension(filename):
    """
    return extension from filename
    """
    #on decoupe la chaine
    l=filename.split(".")
    #l'extension est en fin de liste
    return l[len(l)-1]

def getFilename(filename):
    """
    return name from filename without directory structure
    """
    #on decoupe la chaine
    #l=filename.split(os.sep)
    #l'extension est en fin de liste
    #return l[len(l)-1]
    return os.path.split(filename)[1]

def getDir(filename):
    '''
    return dir name
    '''
    return os.path.dirname(filename)
    

def getFilenameOnly(filename):
    '''
    return name from filename without extension
    '''
    #cut the string
    l=filename.split(".")
    #name is at the beginning
    return l[0]


def getModifiedDate(filename):
    '''
    return the modified date
    '''
    return time.ctime(os.path.getmtime(filename))

def fileExist(filename):
    """
    check if a file exist
    """
    return os.path.exists(filename)

def openFile(filename):
    '''
    open a txt file with q,i,ierr
    return q,i,ierr
    #best is to use filefilter library
    '''
    completeData=numpy.loadtxt(filename)
    data=completeData.transpose()
    q=data[0]
    i=data[1]
    if len(data)>2:
        error=data[2]
        return q,i,error
    else :
        return q,i,None

def importArray(filename,linestoskip=None,separator='\t',cols=None):
    """
    import a file into a
    numeric float array
    skipping lines beginning by #
    #best is to use filefilter library
    """
    f=open(filename,'r')
    lines=f.readlines()
    datas=[]
    for i in lines[linestoskip:]:
        if i[0]<>'#':
            i=i.replace(separator+'\n','')
            i=i.replace('\n','')
            l=i.split(separator)
            for j in range(len(l)):
                try:
                    l[j]=float(l[j])
                except:
                    l[j]=0.0
            datas.append(l)
    dat=numpy.transpose(numpy.array(datas))
    if cols<>None:
        return dat[:cols]
    else:
        return dat