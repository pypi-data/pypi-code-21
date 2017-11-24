from xml.etree import ElementTree
from numpy import *
import ast


       
        
def data2XMLfile(object,filename,name=""):
        ''' save data into XML file
        '''
        root_element=getxml(object,name)
        if filename==None:
           return
        else:
            el=ElementTree.ElementTree()
            el._setroot(root_element)
            el.write(filename)

def convertText(text,datatype=None):
    '''
    convert text with datatype
    '''
    if datatype==None:
        return str(text)
    val=str(text)
    try:
        if datatype.find('array')>=0:
            val=string2data(text)
        elif datatype.find('bool')>=0:
            #print "boolean trouve ", tag," ",datatype
            val= (text.lower() in ['1','true','y'])
        elif datatype.find('float')>=0:
            val=float(text)
        elif datatype.find('int')>=0:
            val=int(text)
        elif datatype.find('list')>=0:
            val=ast.literal_eval(text)
        elif datatype.find('dict')>=0:
            val=ast.literal_eval(text)
    except:
        #print "error when trying to convert : ",text,' as ',datatype
        return None
    return val
# ----------------------------------------------------------------------------------

def string2data(st):
        '''return a array containing datas from string
        '''
        #arr=array()
        arr=fromstring(st, dtype=float, sep=',')
        return arr
    
def getDatatype(obj):
        '''
        return type of object in string without < > 
        '''
        typ=str(obj.__class__)
        typ=typ.replace('<type ', '')
        typ=typ.replace('>', '')
        typ=typ.replace("'", '')
        return typ
    
def data2string(arr):
        ''' 
        return a string from an array separated with comma
        
        [1.2 2.3 ...] -> "1.2 2.3 "
        '''
        l=list(arr) #transform array in list
        s=str(l)    #transform list in string
        s=s.replace('[','')
        s=s.replace(']','') #remove [ and ]
        return s