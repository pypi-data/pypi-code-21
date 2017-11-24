"""
project : pySAXS
description : class for radial average parameters
authors : Olivier Tache
Last changes :
2012 : replacing the old SAXSparameters

IMPORTANT HERE :
THE INITIALS PARAMETERS FOR ABSOLUTE SCALE
"""
xml_init='<parameters>\
    <comment datatype="string" description="comment" order="10">comment</comment>\
    <D datatype="float" description="Detector to sample distance (cm)" order="3">1.0</D>\
    <TransmittedFlux datatype="float" description="Transmitted Flux" order="12">-1.0</TransmittedFlux>\
    <transmission datatype="float" description="Transmission" order="13" formula="TransmittedFlux/IncidentFlux">-1.0</transmission>\
    <flux datatype="float" description="Total Flux = Incident Flux * K (ph/s)" order="17" formula="IncidentFlux*K">1.0</flux>\
    <K datatype="float" description="K constant" order="16">1.0</K>\
    <thickness datatype="float" description="Thickness (cm)" order="14">1.0</thickness>\
    <DeltaOmega datatype="float" description="Delta Omega" order="15" formula="(pixel_size/D)**2">1.0</DeltaOmega>\
    <filename datatype="file" description="Filename" order="1">param.par</filename>\
    <q_by_pixel datatype="float" description="q by pixel (-1 if not used)" order="5">-1.0</q_by_pixel>\
    <backgd_by_s datatype="float" description="Background by second" order="7">0.0</backgd_by_s>\
    <backgd_by_pix datatype="float" description="Background by pixel" order="8">0.0</backgd_by_pix>\
    <backgd datatype="float" description="Total background (B by pixel + B by s * time)" order="9" formula="backgd_by_pix+backgd_by_s*time">0.0</backgd>\
    <time datatype="float" description="Exposition time (s)" order="6">1.0</time>\
    <wavelength datatype="float" description="Wavelength (A)" order="2">1.542</wavelength>\
    <IncidentFlux datatype="float" description="Incident Flux" order="11">1.0</IncidentFlux>\
    <pixel_size datatype="float" description="Pixel size (cm)" order="4">1</pixel_size>\
</parameters>'
xml_short='<parameters>\
    <comment datatype="string" description="comment" order="10">comment</comment>\
    <TransmittedFlux datatype="float" description="Transmitted Flux" order="12"></TransmittedFlux>\
    <time datatype="float" description="Exposition time (s)" order="6">1.0</time>\
    <IncidentFlux datatype="float" description="Incident Flux" order="11">-1.0</IncidentFlux>\
    </parameters>'
    

rpt_xml_OLD={'filename':'filename',\
         'exposure':'time',\
         'transmission':'TransmittedFlux',\
         'user.DetectorDistance':'D',\
         'user.PixelSize':'pixel_size',\
         'user.wavelength':'wavelength' }
         
rpt_xml=[['filename','acquisition','filename'],\
         ['time','acquisition','exposure'],\
         ['TransmittedFlux','acquisition','transmitted flux'],\
         ['D','imagej','user.DetectorDistance'],\
         ['pixel_size','imagej','user.PixelSize'],\
         ['wavelength','imagej','user.wavelength'],\
         ['D','pyfai','imagej.DetectorDistance'],\
         ['pixel_size','pyfai','imagej.PixelSize'],\
         ['wavelength','pyfai','imagej.wavelength'],\
         ['D','pyfai','pyfai.detectordistance'],\
         ['pixel_size','pyfai','pyfai.PixelSize'],\
         ['wavelength','pyfai','pyfai.wavelength'],\
         ['time','Image Header','count_time'],\
         ['TransmittedFlux','Image Header','pilroi0'],\
         ['IncidentFlux','Image Header','pilai1'],\
         ['filename','Image Header','title'],\
         ['TransmittedFlux','absolute intensities','transmittedflux'],\
         ['comment','Image Header','comment']
         ]

'''
#filename :    OT-2015-01-20-01-1800s
#date :     2015-01-20 12h00min38s
#exposure time :    1800
#transmission:    0.845226466656
#passeurz :    15.0
#generator mA :    52
#generator kV :    48
#passeur :    32.0
#average :    -0.00400000018999
#exposure :    1800.0
#pilatusx :    0.0
#pilatusz :    0.0
#filename :    OT-2015-01-20-01-1800s
#user.centerx=11.0
#user.centery=41.0
#user.DetectorDistance=112.5
#user.alpha_deg=90.0
#user.PixelSize=0.0172000005841
#user.wavelength=1.542
#user.MaskImageName=Q:\SIS2M\LIONS\SAXS data\SAXS\Visiteurs\2014\PG\\mask.tif'
'''
#-------------------------------------------------

from numpy import *
from xml.etree import ElementTree
from pySAXS.tools import xmltools
import sys

from copy import deepcopy
from pySAXS.tools import isNumeric
from pySAXS.tools import filetools
#from PyQt4 import QtGui, QtCore

# ----------------------------------------------------------------------------------

class SAXSparameters:
    """
    Radial Average Parameters -
    """
    def __init__(self,printout=None,short=False):
        #print 'a new object SAXS parameters'
        self.parameters={} #dict of parameters
        self.printout=printout
        self.short=False
        #print printout
        if short:
            element=ElementTree.XML(xml_short)
            self.short=True
        else:
            element=ElementTree.XML(xml_init)
            
        self.getFromXML(element)
 
    def __repr__(self):
        chaine=""
        for var in self.parameters:
            chaine+=str(var)+" = "+str(self.parameters[var])+"\n"
        return chaine

    def printTXT(self,txt="",par=""):
        #print self.printout
        if self.printout==None:
            print(str(txt)+str(par))
        else:
            self.printout(txt,par)
    
    def copy(self):
        '''
        a copy of me
        '''
        newclass=SAXSparameters()
        xmlelement=self.xml()
        newclass.getFromXML(xmlelement)
        '''
        new={}
        for var in self.parameters:
            new[var]=self.parameters[var].copy()
        newclass.parameters=new
        '''
        return newclass
        
    
    def get(self,variable):
        '''
        return the value of the specified variable
        '''
        if self.parameters.has_key(variable):
            return self.parameters[variable].get()
        else:
            return None
        
    def set(self,variable,value):
        '''
        change the value of the specified variable
        '''
        if self.parameters.has_key(variable):
            self.parameters[variable].set(value)

    def order(self):
        '''
        return a list with dictionnary key ordered
        '''
        l={}
        for name in self.parameters:
            l[self.parameters[name].order]=name
        list_ordered=[]
        for ord in l:
            list_ordered.append(l[ord])
        return list_ordered


    def save_printable(self,file_name):
        '''
        save in a txt file
        '''
        f=open(file_name,mode='w')
        f.write(self.__repr__())
        f.close()
        print file_name," saved"

    def save(self,file_name):
        '''
        save in a pickle (binary) file
        '''
        import pickle
        f=open(file_name,mode='w')
        pickle.dump(self.parameters,f)
        f.close()
        

    def load(self,file_name):
        '''
        load from a pickle (binary) file
        '''
        import pickle
        f=open(file_name,mode='r')
        par=pickle.load(f)
        for name in par:
            if self.parameters.has_key(name):
                self.parameters[name]=datatype(self.parameters[name])(par[name])
            else:
                self.parameters[name]=par[name]
        f.close()

    def xml(self):
        '''
        return an xml object
        '''
        root_element = ElementTree.Element("parameters")
        for keys, param in self.parameters.items():
            root_element.append(param.xml())
        return root_element

    def xmlString(self):
        '''
        return a xml string
        '''
        x=self.xml()
        return ElementTree.tostring(x)
    
    def saveXML(self,filename):
        '''
        save in a xml file
        '''
        root_element=self.xml()
        el=ElementTree.ElementTree()
        el._setroot(root_element)
        el.write(filename)
            
    def getFromXML(self,xmlElement):
        """
        get parameters from xml element
        """
        for subelement in xmlElement:
            #get all element in root element
            tag=subelement.tag #get tag ie <time> or <flux>
            #print tag
            newpar=parameter(tag,parent=self)
            newpar.getfromXML(subelement)
            self.parameters[tag]=newpar
        #self.__repr__()
        if not(self.short):
            self.goodCalculation()
        
    def goodCalculation(self):
        '''
        modify some parameter for good calculation :
        - backg=dbackgd_by_pix+backgd_by_s*time
        - transmission=TransmittedFlux/IncidentFlux
        - DeltaOmega=(pixel_size/D)**2
        - flux=IncidentFlux*K
        '''
        
        self.parameters['backgd'].formula="backgd_by_pix+backgd_by_s*time"
        self.parameters['transmission'].formula="TransmittedFlux/IncidentFlux"
        self.parameters['DeltaOmega'].formula="(pixel_size/D)**2"
        self.parameters['flux'].formula="IncidentFlux*K"
       
    def openXML(self,filename):
        '''
        read from a xml file
        '''
        self.__init__(self.printout)
        element=ElementTree.parse(filename)
        root=element.getroot()
        if root.tag=='parameters':
            self.getFromXML(root)


    def calculate_All(self,verbose=True):
        '''
        calculate all the functions defined 
        '''
        self.printTXT("--- calculation for all parameters ---")
        for key,values in self.parameters.items():
            res=values.eval()
            if values.formula is not None and verbose:
                self.printTXT(str(key)+"="+values.formula+"="+str(res))
                
# ----------------------------------------------------------------------------------

    def eval_function(self,formula):
        '''
        return the evaluated value
        '''
        #create the dict
        d={}
        for key, val in self.parameters.items():
            d[key]=val.value
        #print formula,"<--",d
        try:
            ret=eval(formula,d)
            return ret
        except NameError,e:
            self.printTXT("Formula error in xml expression ("+formula+') :' +str( e))
        

    def calculate_q_by_pix(self):
        """
        calculate q by pix in A-1 from parameters (RAP)
        """
        self.parameters['q_by_pixel']=self.calculate_q(1)


    def calculate_q(self,n):
        """
        calculate q in A-1 from parameters
        n : pixel number
        ----------------------------------
        q=(4*pi/lambda)*sin(theta/2)
        with tan(theta)=d/D
        D : sample detector distance
        d : pixel number (n) * pixel size
        """
        if self.parameters['q_by_pixel'].value<=0:
            self.printTXT('q=(4*pi/lambda)*sin(theta/2)   with tan(theta)=d/D    D : sample detector distance   d : pixel number (n) * pixel size')
            return ((4*pi)/float(self.parameters['wavelength'].value))*sin(arctan((float(self.parameters['pixel_size'].value)*n)/float(self.parameters['D'].value))/2)
        else:
            return n*float(self.parameters['q_by_pixel'].value)

    def calculTransm(self):
        '''
        calculate Transmission
        '''
        self.parameters['transmission'].value=self.parameters['Transmitted_Flux'].value/self.parameters['Incident_Flux'].value
        return self.parameters['transmission'].value

    def calculDeltaOmega(self):
        '''
        calculate DeltaOmega
        '''
        #--deltaomega
        #print "DeltaOmega=(pixel size / distance sample detector)^2"
        self.parameters['DeltaOmega'].value=(float(self.parameters['pixel_size'].value) / float(self.parameters['D'].value))**2
        return self.parameters['DeltaOmega'].value

    def calculTotalFlux(self):
        '''
        calculate Flux
        '''
        self.parameters['flux'].value = float(self.parameters['IncidentFlux'].value)*float(self.parameters['K'].value)
        return self.parameters['flux'].value

    def calculBack(self):
        '''
        calculate background
        '''
        self.parameters['backgd'].value=float(self.parameters['backgd_by_pix'].value)+float(self.parameters['backgd_by_s'].value)*float(self.parameters['time'].value)
        return self.parameters['backgd'].value

    def calculate_i(self,n,q=None,solvent=None,deviation=None,solventdeviation=None,\
                    background_q=None, background_i=None,background_error=None):
        '''
        Calculate i in cm-1 from parameters
        n : raw intensity
        solvent : empty cell to substract
        deviation : absolute deviation for i
        solventdeviation : absolute deviation for background
        #add by OT 2015 
        background_q: background data
        background_i: 
        background_error: background deviation 
        -----------------------------------
        DeltaOmega=(pixel size / distance sample detector)^2
        Flux = (monitor/transmission)*K
        Intensity=(n-background)/(time * DeltaOmega * Transmission * Thickness * Flux)
        if empty cell (solvent) then     Final Intensity=( Intensity(with Thickness=1) - empty cell)/thickness
        '''
        
        self.printTXT("---- setting absolute scale ----")
        #--deltaomega
        self.printTXT("DeltaOmega=(pixel size / distance sample detector)^2")
        self.printTXT('Delta Omega is : ',self.parameters['DeltaOmega'].value)
        #-- flux
        self.printTXT("Flux = (monitor/transmission)*K")
        self.printTXT( "Flux is : (cps/s) ", self.parameters['flux'].value)
        #-- background
        self.printTXT( "background is", self.parameters['backgd'].value)
        if background_i is not None :
            self.printTXT("trying to subtract background")
            
        if deviation is not None:
            newdeviation=deviation
        #-- I
        #if solvent is None:
        self.printTXT( "Intensity=(n-background)/(time * DeltaOmega * Transmission * Thickness * Flux)")
        i=(n-self.parameters['backgd'].value)/(float(self.parameters['time'].value)*self.parameters['DeltaOmega'].value*float(self.parameters['transmission'].value)*float(self.parameters['thickness'].value)*float(self.parameters['flux'].value))
        if deviation is not None:
            self.printTXT( "Calculating deviation")
            newdeviation=deviation/(float(self.parameters['time'].value)*self.parameters['DeltaOmega'].value*float(self.parameters['transmission'].value)*float(self.parameters['thickness'].value)*float(self.parameters['flux'].value))
        ''' Solvent subtraction is not manage here anymore
        else:
            self.printTXT( "Intensity=(n-background)/(time * DeltaOmega * Transmission * Flux)")
            i=(n-self.parameters['backgd'].value)/(float(self.parameters['time'].value)*self.parameters['DeltaOmega'].value*float(self.parameters['transmission'].value)*float(self.parameters['flux'].value))
            self.printTXT( "Final Intensity=( Intensity - empty cell)/thickness")
            i=(i-solvent)/float(self.parameters['thickness'].value)
            
            if (solventdeviation is not None) and (deviation is not None):
                newdeviation=deviation/(float(self.parameters['time'].value)*self.parameters['DeltaOmega'].value*float(self.parameters['transmission'].value)*float(self.parameters['thickness'].value)*float(self.parameters['flux'].value))
                newdeviation=(newdeviation-solventdeviation)/float(self.parameters['thickness'].value)
            else:
                self.printTXT( "solvent deviation is not specified, impossible to manage deviation ")
                deviation=None
         '''       
        self.printTXT( "---- intensity scaled for "+str(len(n))," datas ----")
        if deviation is not None:
            return i,newdeviation
        else:
            return i,None

    def generateQtGUI(self):
        """
        generate a GUI with guidata
        """
        import guidata.dataset.datatypes as dt
        from guidata.dataset.dataitems import (ChoiceItem, StringItem, TextItem,
                                       ColorItem, FloatItem,IntItem)
        items = { }
        #"a" : di.IntItem("a"),
        # "b" : di.FloatItem("b")
        #" }
        #-sorting parameters
        paramslist=self.order()
        #- controls
        for name in paramslist:
            active=True
            callback=self.guidataCallback
            par=self.parameters[name]
            #print par.datatype
            if par.formula is not None:
                active=False
                callback=None
            if par.datatype=="float":
                items[name]=FloatItem(par.description,par.value).set_prop("display", callback=callback,active=active)
            elif par.datatype=="int":
                items[name]=IntItem(par.description,par.value).set_prop("display", callback=callback,active=active)
            elif par.datatype=="string":
                items[name]=StringItem(par.description,par.value).set_prop("display", callback=callback,active=active)
            else:
                items[name]=StringItem(par.description,par.value).set_prop("display", callback=None,active=active)#no call back on string
        clz = type("Dialog", (dt.DataSet,), items)
        dlg = clz()
        return dlg
        
    def guidataCallback(self,obj,item, value):
        #print 'call back on ',item._name
        pass
        '''#change the 
        d={}
        
        for key,value in obj.__dict__:
            
            else:
                self.params.parameters[key].value=self.listTextCtrl[key].GetValue()
        #print self.parameters.items()
        for key,values in self.parameters.items():
            #print key
            res=values.eval()
            if values.formula<>None:
                self.printTXT(str(key)+"="+values.formula+"="+str(res))
        '''
            
    def importOLD(self,filename):
        '''
        let us to import a old parameter file
        '''
        from pySAXS.LS import SAXSparametersOLD
        p=SAXSparametersOLD.SAXSparametersOLD()
        p.load(filename)
        self.parameters['filename'].value=p.parameters['filename']
        self.parameters['wavelength'].value=p.parameters['wavelength']
        self.parameters['D'].value=p.parameters['D']
        self.parameters['pixel_size'].value=p.parameters['pixel size']
        self.parameters['q_by_pixel'].value=p.parameters['q by pixel']
        self.parameters['time'].value=p.parameters['time']
        self.parameters['backgd_by_s'].value=p.parameters['backgd by s']
        self.parameters['backgd_by_pix'].value=p.parameters['backgd by pix']
        self.parameters['backgd'].value=p.parameters['backgd']
        self.parameters['comment'].value=p.parameters['comment']
        self.parameters['IncidentFlux'].value=p.parameters['Incident Flux']
        self.parameters['TransmittedFlux'].value=p.parameters['Transmitted Flux']
        self.parameters['transmission'].value=p.parameters['transmission']
        self.parameters['thickness'].value=p.parameters['thickness']
        self.parameters['DeltaOmega'].value=p.parameters['DeltaOmega']
        self.parameters['K'].value=p.parameters['K']
        self.parameters['flux'].value=p.parameters['flux']
        
    '''def getfromRPTOLD(self,filename):
        
        r=rptOpen(filename)
        for k in r:
            if rpt_xml.has_key(k):
                #print "key ",k,' found with val :',r[k]
                val=r[k]
                self.printTXT(str(k)+"->"+str(val))
                k2=rpt_xml[k]
                self.set(k2,val)
            #else :
            #    print "key ",k,' not found '
    '''        
    def getfromRPT(self,filename):
        '''
        open a rpt file and distribute the values in xml
        '''
        r=rptOpen(filename)
        if r is None:
            self.printTXT("---- import FAILED rpt file :", filename)
            return
        self.printTXT("---- import from rpt file :", filename)
        for n in rpt_xml:
            key=n[0]
            session=n[1]
            option=n[2]
            #get value from rpt
            #print key,' - ',session,'-',option
            if r.has_option(session,option):
                v=r.get(session,option)
                if isNumeric.isNumeric(v):
                    v=float(v)
                self.set(key,v)
                self.printTXT(str(key)+"->"+str(v))
            
        
#----------------------------------------------------------------------------------------------------
        
class parameter:
    '''
    class for parameters
    '''
    def __init__(self,name, value=None,description="",order=-1,formula=None,datatype=None,parent=None):
        self.name=name
        self.value=value
        self.description=description
        self.order=order
        self.formula=formula
        self.datatype=datatype
        self._parent=parent
        
    def __repr__(self):
        if self.formula<>"" and self.formula<>None:
            return "("+self.description+") : "+str(self.value)+ " CALCULATED from "+self.formula
        else :
            return "("+self.description+") : "+str(self.value)
    
    def get(self):
        '''
        return the value of the parameter
        '''
        return self.value
    
    def set(self,value):
        '''
        set the value of the parameter
        '''
        self.value=value
        
        
    def copy(self):
        new=parameter(self.name)
        new.name=deepcopy(self.name)
        new.value=deepcopy(self.value)
        new.description=deepcopy(self.description)
        new.order=deepcopy(self.order)
        new.formula=deepcopy(self.formula)
        new.datatype=deepcopy(self.datatype)
        new._parent=self._parent
        return new
    
    def eval(self):
        '''if self.evaluationFunction<>None:
            self.value=self.evaluationFunction()
            return self.value
        '''
        try:
            if self.formula<>"" and self.formula<>None and self._parent<>None:
                val=self._parent.eval_function(self.formula)
                self.value=val
        except:
            print "ERROR on ", self.formula
        return self.value
            
    def xml(self):
            '''
            return an element xml
            <time description='time(s)' order='2' formula='e=mc**2' datatype='float'>1.25</time>
            '''
            attrib={}
            
            if self.description<>None:
                attrib["description"]=self.description
            if self.order<>None:
                attrib["order"]=str(self.order)
            if self.formula<>None:
                attrib["formula"]=str(self.formula)
            if self.datatype<>None:
                attrib["datatype"]=xmltools.getDatatype(self.value)
                #attrib["datatype"]=str(self.datatype)
            #else:
               
            xml = ElementTree.Element(self.name,attrib)
            xml.text=str(self.value)
            # ie  : <time description='time in s' order=0 datatype=''>3600.0</time>
            return xml
             
    def getfromXML(self,xmlElement):
        '''
        initialization given by xml element
        '''
        self.name=xmlElement.tag
        attrib=xmlElement.attrib
        text=xmlElement.text
        
        self.description=None
        self.order=None
        self.formula=None
        self.datatype=None
        
        if (attrib.has_key('description')):
            self.description=attrib['description']
        if (attrib.has_key('order')):
            self.order=int(attrib['order'])
        if (attrib.has_key('formula')):
            self.formula=attrib['formula']
        if (attrib.has_key('datatype')):
            self.datatype=attrib['datatype']
            self.value=xmltools.convertText(xmlElement.text,self.datatype)
        else:
            self.value=text
        return self

    


#----------------------------------------------------------------------------------------------------
#RPT management
def rptOpenOLD(filename):
    f=open(filename)
    l=f.readlines()
    rpt={}
    for i in l:
        #cut 
        if i.find(":")>=0:
            tb=i.split(':')
        else:
            tb=i.split('=')
        key=tb[0]
        key=key.replace('#','')
        key=key.strip()
        #key=key.replace(' ','')
        #print len(tb),tb
        if len(tb)>1:
            val=tb[1]
            if isNumeric.isNumeric(val):
                val=float(val)
            else:
                val=val.strip()
            rpt[key]=val
        #print key,' - ',val
    return rpt
def rptOpen(filename):
    '''
    the new management of rpt
    '''
    import ConfigParser
    rpt = ConfigParser.ConfigParser()
    r=rpt.read(filename)
    if len(r)==0:
        return None
    return rpt

def saveImageHeader(header,filename):
    import ConfigParser
    rpt=ConfigParser.ConfigParser()   
    #check if there is a associated rpt file
    newfn=filetools.getFilenameOnly(filename)
    newfn+='.rpt'
    r=rpt.read(newfn) #if r=[] rpt doesn't exist
     
        
    if not rpt.has_section('Image Header'):
            rpt.add_section('Image Header')
    for key in header:    
        rpt.set('Image Header',str(key),str(header[key]))
    
            
    f=open(newfn,'wb')
    rpt.write(f)
    f.close()
    print "write EDF Header to RPT",newfn

if __name__ == "__main__":
      app = QtGui.QApplication(sys.argv)
      param=SAXSparameters(short=True)
      print param
      #test guidata
      #app = guidata.qapplication()
      dlg = param.generateQtGUI()
      dlg.edit() 
      