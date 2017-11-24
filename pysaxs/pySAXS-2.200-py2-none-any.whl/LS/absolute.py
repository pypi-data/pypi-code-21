"""
project : pySAXS
description : class for absolute intensities
authors : Olivier Tache
"""

from pySAXS.LS import SAXSparametersXML as SAXSparameters
from numpy import *
from xml.etree import ElementTree
from pySAXS.tools import xmltools
from pySAXS.LS import background
from pySAXS.tools import filetools
from scipy import interpolate

class absolute(SAXSparameters.SAXSparameters):
    '''
    redefine SAXSparameters for better understanding
    '''
    
    def __init__(self,filename=None,q=None,i=None,ierr=None,parameters=None,printout=None,short=False):
        #SAXSparameters.SAXSparameters.__init__(printout,short)
        #print 'a new object SAXS parameters'
        self.parameters=parameters #dict of parameters
        self.printout=printout
        self.short=False
        
        if self.parameters is None:
            #init parameters
            self.parameters={}
            if short:
                element=ElementTree.XML(SAXSparameters.xml_short)
                self.short=True
            else:
                element=ElementTree.XML(SAXSparameters.xml_init)
            self.getFromXML(element)
        
        self.filename=filename
        if self.filename is not None :
            #read the filename and import datas
            self.q,self.i,self.ierr=filetools.openFile(filename)
        
        if i is not None:
            self.i=i
        if q is not None:
            self.q=q
        if ierr is not None:
            self.ierr=ierr
        #1-background data
        self.backData=False
        self.iBack=None     #i background
        self.qBack=None     #q background
        self.ierrBack=None  #ierr background
        #gives iSub
        self.iSub=self.i         #i bg subtracted 
        self.ierrSub=self.ierr   #ierr bg subtracted 
        self.backFile=None
        
        #2-absolute intensities datas       
        self.iAbs=None
        self.qAbs=self.q
        self.ierrAbs=None
        
        #3-solvent data
        self.solventData=False
        self.qSolvent=None
        self.iSolvent=None
        self.ierrSolvent=None 
        self.solventFile=None
        #gives iFinal
        self.iFinal=None
        self.ierrFinal=None
        
    
    def subtractBackgroundFile(self,filename):
        '''
        subtract background data file
        '''
        qb,ib,ierrb=filetools.openFile(filename)
        self.subtractBackground(qb, ib, ierrb, filename)
        return self.iSub,self.ierrSub
        
    def subtractBackground(self,q,i,ierr=None,filename=None):
        '''
        subtract background data if defined
        '''
        self.iBack=i
        self.qBack=q
        self.ierrBack=ierr
        self.backData=True
        self.backFile=filename
        self.printTXT('--- subtract background from data ----')
        self.printTXT("for "+str(len(i))+ " datas")
        q,self.iSub,self.ierrSub=background.subtract2D(self.q,self.i,self.ierr,self.qBack,self.iBack,self.ierrBack)
        return self.iSub,self.ierrSub
                
    def subtractSolvent(self,q,i,ierr=None,filename=None,thickness=None):
        self.iSolvent=i
        self.qSolvent=q
        self.ierrSolvent=ierr
        self.solventData=True
        self.solventFile=filename
        self.printTXT( "--- solvent subtraction ---")
        
        if float(self.parameters['thickness'].value)!=1:
            self.printTXT("WARNING thickness for absolute intensities is different of 1 :",float(self.parameters['thickness'].value))
            '''oldval=float(self.parameters['thickness'].value)
            self.parameters['thickness'].value=1.0
            self.printTXT("trying to calculate for thickness =1.0")
            self.calculate()
            self.parameters['thickness'].value=oldval'''
            
        if thickness is not None :
            self.parameters['thickness'].value=float(thickness)
        
        self.printTXT( "Final Intensity=(Intensity - solvent)/thickness")
        if len(self.iAbs)!=len(self.iSolvent):
            #trying interpolation
            self.printTXT( "with interpolation")
            newSolvent=interpolate.interp1d(self.qSolvent,self.iSolvent,kind='linear',bounds_error=0) #interpolation for i
            self.iSolvent=newSolvent(self.q)
            
            if self.ierrSolvent is not None:
                newErr=interpolate.interp1d(self.qSolvent,self.ierrSolvent,kind='linear',bounds_error=0) #interpolation for i
                self.ierrSolvent=newErr(self.q)
            self.qSolvent=self.q
            
        self.iFinal=(self.iAbs-self.iSolvent)/float(self.parameters['thickness'].value)
        self.printTXT( "thickness=",self.parameters['thickness'].value)
        if (self.ierrSolvent is not None) and (self.ierr is not None):
            print "-------------------------------------            calculate uncertainties"
            self.ierrFinal=(self.ierrAbs+self.ierrSolvent)/float(self.parameters['thickness'].value)
        else:
            self.printTXT( "solvent deviation is not specified, impossible to manage deviation ")
            deviation=None
        return self.iFinal,self.ierrFinal
        
    def subtractSolventFile(self,filename,thickness=None):
        '''
        subtract solvent file
        '''
        self.solventFile=filename
        qso,iso,ierrso=filetools.openFile(filename)
        self.subtractSolvent(qso, iso, ierrso, filename,thickness)
        return self.iSub,self.ierrSub
    
    def calculate(self):
        '''
        calculate i abs
        '''
        self.calculate_All() #calculate parameters
        self.iAbs,self.ierrAbs=self.calculate_i(self.iSub,deviation=self.ierrSub)
        
        return  self.iAbs,self.ierrAbs
    
    def openRPT(self):
        '''
        import associated rpt
        '''
        filenamerpt=self.filename
        newfn=filetools.getFilenameOnly(filenamerpt) #filename without extension
        self.getfromRPT(newfn+'.rpt')
    
    def saveRPT(self,filename=None):
        import ConfigParser
        rpt=ConfigParser.ConfigParser()   
        #check if there is a associated rpt file
        if filename is None:
            filename=self.filename
        newfn=filetools.getFilenameOnly(filename) #filename without extension
        newfn+='.rpt'
        r=rpt.read(newfn) #if r=[] rpt doesn't exist
        self.printTXT("--- saving rpt file ---")
        if len(r)<=0:
            self.printTXT("file doesn't exist ")
        self.printTXT('saving in file : ',newfn)
        #background subtraction
        if self.backData:
            if not rpt.has_section('background subtraction'):
                rpt.add_section('background subtraction')
            rpt.set('background subtraction','file',str(self.backFile))
            
        #absolute intensities
        if not rpt.has_section('absolute intensities'):
            rpt.add_section('absolute intensities')
        for var in self.parameters:
            if self.parameters[var].formula<>None:
                rpt.set('absolute intensities',str("calc."+var),str(self.parameters[var]))
            else:
                rpt.set('absolute intensities',str(var),str(self.parameters[var].value))
        #solvent subtraction
        if self.solventData:
            if not rpt.has_section('solvent subtraction'):
                rpt.add_section('solvent subtraction')
            rpt.set('solvent subtraction','file',str(self.solventFile))
                
        f=open(newfn,'wb')
        rpt.write(f)
        f.close()
        
    def saveABS(self,filename=None):
        '''
        save the datas and treatment
        '''
        if filename is None:
            filename=filetools.getFilenameOnly(self.filename) #filename without extension
            filename+=".abs"
        #0
        self.printTXT('---- saving ABS file : '+filename+ '----')
        tabcomment="#q \ti"
        tab=[]
        tab.append(self.q)
        tab.append(self.i)
        
        if self.ierr is not None:
            tabcomment+='\t error'
            tab.append(self.ierr)
        #1-background data
        if self.backData:
            tabcomment+="\tq background \ti background"
            tab.append(self.qBack)
            tab.append(self.iBack)
            if self.ierrBack is not None:  #ierr background
                tabcomment+="\tbackground error"
                tab+=[self.ierrBack]
            #gives iSub
            tabcomment+="\tq subtracted \ti subtracted"
            tab+=[self.q,self.iSub]
            if self.ierrSub is not  None:  #ierr background
                tabcomment+="\tsubtraction error"
                tab+=[self.ierrSub] 
            
        #2-absolute intensities
        if self.iAbs is not None:
            tabcomment+="\tq abs \ti abs"
            tab+=[self.q,self.iAbs]
            if self.ierrAbs is not None:  #ierr background
                tabcomment+="\terror abs"
                tab+=[self.ierrAbs]
        
        #3-solvent data
        if self.solventData:
            tabcomment+="\tq solvent \ti solvent"
            tab+=[self.qSolvent,self.iSolvent]
            if self.ierrSolvent is not None:  #ierr background
                tabcomment+="\terror solvent"
                tab+=[self.ierrSolvent]
        
        if self.iFinal is not None:
            tabcomment+="\tq final \ti final"
            tab+=[self.q,self.iFinal]
            if self.ierrFinal is not None:  #ierr background
                tabcomment+="\terror final"
                tab+=[self.ierrFinal]
        
        f=open(filename,mode='w')
        #--- header
        f.write(tabcomment+'\n')
        print tabcomment
        nrows=0
        #print tab
        for a in tab:
            if a is not None:
                if len(a)>nrows:
                    nrows=len(a)
        self.printTXT(str( nrows)+" rows will be saved")
        #-- datas
        for n in range(nrows):
            dat=''
            for a in tab:
                if a is not None:
                    if n<len(a):
                        dat+=str(a[n])+'\t'
                    else:
                        dat+='\t'
                else:
                    dat+='Nan\t'
            dat+='\n'
            f.write(dat)
        self.printTXT("data are saved")
        self.printTXT("-------------------")
        f.close()
        
        