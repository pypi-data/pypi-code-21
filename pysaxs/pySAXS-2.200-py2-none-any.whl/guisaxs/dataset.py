from xml.etree import ElementTree
from pySAXS.tools import xmltools
import pySAXS.LS.SAXSparametersXML as SAXSparameters
from pySAXS.models import model
from numpy import *
from scipy import interpolate
'''
Dataset class for datas
'''

class dataset:
    def __init__(self,name=None,q=None,i=None,filename=None,\
                 checked=True,model=None,rawdata_ref=None,\
                 type=None,parameters=None,error=None,comment=None,\
                 parent=None,child=None,parentformula=None,variableDict=None,color=None,\
                 image=None,background_data=None,background_value=None,rpt=None,abs=None):
        self.name=name
        if filename is None:
            self.filename=name
        else:
            self.filename=filename
        
        self.checked=checked
        if checked<>None:
            #print checked
            self.checked=(str(checked).lower()=='true')
        
        self.q=q
        self.i=i
        self.error=error
        self.model=model
        self.rawdata_ref=rawdata_ref
        self.type=type
        self.parameters=parameters
        self.comment=comment
        self.parent=parent#[data1,data2,...]
        self.child=child 
        self.parentformula=parentformula #"i1+i2+i3"
        #self.parentvariables=parentvariablesdict #['i1','i2',...]
        self.variableDict=variableDict#{'i0':'data1','i1':'data2',...}
        self.color=color
        self.image=image
        self.background_data=background_data
        self.background_value=background_value
        self.rpt=rpt
        self.abs=abs

    def _check(self):
        if self.checked<>None:
            self.checked=(str(self.checked).lower()=='true')
        

    def _copy(self):
        """
        return a copy without model and parameters
        use in saveDataDictRaw
        """
        new=dataset(name=self.name,q=self.q,i=self.i,filename=self.filename,checked=self.checked,\
                    rawdata_ref=self.rawdata_ref,type=self.type,error=self.error,comment=self.comment,\
                    model=None, parameters=None)
        #new=copy(self)
        return new

    def _deepcopy(self):
        """
        return a deepcopy of the dataset object
        """
        from copy import  deepcopy
        return deepcopy(self)
    
    def _evaluateFromParent(self,data_dict,qref=None):
        '''
        evaluate i from parent
        datadict : a dictionnary of dataset 
        '''
        from numpy import *
        if qref==None:
            qref=self.q
        #print self.name
        if self.parentformula==None:
            return
        newdict={}
        newerror=zeros(shape(qref))
        #--convert variableDict
        for var in self.variableDict:
            name=self.variableDict[var]
            #print name
            if not(data_dict.has_key(name)):
                return "Data are missing for "+name+" with formula : "+self.parentformula+". Data will not be recalculated."
                #return data_dict[name].i
                
            #variableDict contain variable name and dataset name
            i=data_dict[name].i
            q=data_dict[name].q
            if str(q)<>str(qref):
                #self.printTXT("trying interpolation for ",name)
                newf=interpolate.interp1d(q,i,kind='linear',bounds_error=0)
                newi=newf(qref)
            else:
                newi=i
                #addition for errors
                error=data_dict[name].error
                if error!=None and newerror!=None:
                    newerror+=error
                else:
                    newerror=None
            newdict[var]=newi
        #--evaluate
        #self.printTXT("trying evaluation of ",formula)
        safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'degrees', \
                     'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log',\
                     'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh'] #use the list to filter the local namespace safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ])
        for k in safe_list:
            newdict[k]=locals().get(k,None)
        iout=array(eval(self.parentformula,newdict))
        self.q=qref
        self.i=iout
        self.error=newerror
        return ""
    
    def _xml(self):
        '''
        return a xml element
        '''
        #create the root </root><root>
        root_element = ElementTree.Element("data",name=self.name)
        for attributeName in dir(self):
            #print attributeName
            if attributeName[0]<>'_':
                #class attribute
                #child = ElementTree.SubElement(root_element, attributeName)
                val=getattr(self,attributeName)
                if val is not None:
                    if attributeName=="parameters":
                        child=val.xml()
                    elif attributeName=="model":
                        child=val.xml()
                    else:
                        child = ElementTree.Element(attributeName,datatype=xmltools.getDatatype(val))
                        if xmltools.getDatatype(val).find('array')>=0:#val.__class__==array(1).__class__:
                            #attribute is an array
                            child.text = xmltools.data2string(val)
                        else:
                            child.text=str(val)
                    #now append
                    root_element.append(child)
        return root_element

# ---------------------------------------------------------------------------------- 
    
def getDatasetFromXML(element):
    '''
    set the dataset with the parsed xml as Element
    
    <root>
        <name> mqlkqsmldk</name>
        <checked>true</checked>
        <q datatype='numpy.array'>0,0.1,0.2,0.3</q> if it is an array datatype must contain 'array'
        ...
    </root>
    '''
    dt=dataset()
    for subelement in element:
        #get all element in root element
        tag=subelement.tag #get tag ie <filename> or <q>
        #print tag
        if hasattr(dt,tag) and tag[0]<>"_":
            if tag=="parameters":
                #print "TAG parameters"
                val=SAXSparameters.SAXSparameters()
                val.getFromXML(subelement)
            elif tag=="model":
                #print "TAG Model"
                val=model.getModelFromXML(subelement)
                    
            else:
                #tag exist in dataset class -> get attrib and text
                attrib=subelement.attrib
                #print attrib
                text=subelement.text
                val=text
                # attrib has 'datatype' ?
                if attrib.has_key('datatype'):
                    datatype=attrib['datatype']
                    #check datatype 
                    val=xmltools.convertText(text,datatype)
                
                #IMPORTANT set value of attibute
            setattr(dt,tag,val)
    if len(dt.q)>len(dt.i):
        #print "lecture error"
        dt.q=dt.q[:len(dt.i)]
    if len(dt.q)<len(dt.i):
        #print "lecture error"
        dt.i=dt.i[:len(dt.q)]
            
            
    return dt

def getDatasetFromXMLFile(filename):
    element=ElementTree.parse(filename)
    root=element.getroot()
    return getDatasetFromXML(root)

def saveDatasetOnXMLFile(filename,dataset):
    xmltools.data2XMLfile(dataset,filename,name="data")
    

def saveDataDictOnXMLFile(filename, data_dict):
    root_element = ElementTree.Element("dataset",name=filename)
    for key,value in data_dict.items():
        print "---",key,value.checked
        #value=data_dict[key]
        el=value._xml()
        #print ElementTree.tostring(el)
        root_element.append(el)
    tree=ElementTree.ElementTree()
    tree._setroot(root_element)
    tree.write(filename)
        
def getDataDictFromXMLFile(filename):
    element=ElementTree.parse(filename)
    root=element.getroot()
    data_dict={}
    for subelement in list(root):
        #get all element in root element
        tag=subelement.tag #get tag ie <data> or <q>
        #print tag
        if tag=='data':
            dataset_name=subelement.attrib["name"]
            #new dataset
            data_dict[dataset_name]=getDatasetFromXML(subelement)
            #print list(subelement)
    return data_dict
                
def saveDataDictRaw(filename,data_dict):
    '''
    save dataset in old format
    '''
    import pickle
    f=open(filename,mode='w')
    newdict={}
    for key, datas in data_dict.items():
        newdict[key]=datas._copy()
    pickle.dump(newdict,f)
    f.close()
        
def getDataDictRaw(filename):
    '''
    get dataset from old format
    '''
    import pickle
    f=open(filename,mode='r')
    data_dict=pickle.load(f)
    f.close()
    return data_dict
# ----------------------------------------------------------------------------------
if __name__== '__main__':
    '''
    q=arange(0,10,0.1)
    i=q**2
    dt=dataset('test',q,i)
    x=dt._getxml()
    print ElementTree.tostring(x)
    print "save in file :", "test_xml_from_python.xml"
    dt._data2XMLfile("c:\\python26\\test_xml_from_python.xml")
    '''
    dt=getDataDictFromXMLFile("c:\\python26\\test1.xml")
