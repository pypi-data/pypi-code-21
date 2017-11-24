"""
project : pySAXS
description : class for radial average parameters
authors : Olivier Tache
Last changes :
Replaced by SAXSparameterXML
08-03-2007 OT : port to pySAXS library

"""
from numpy import *

class SAXSparametersOLD:
    """
     - Radial Average Parameters -

    wave_length=1.542
    detector_to_sample=1
    pixel_size=1
    q_by_pixel=-1
    exposition_time=1
    backgd_by_s=0 #par seconde
    backgd_by_pix=0 #par pixel
    comment=""
    transmission=-1
    thickness=-1
    K=1
    monitor=1
    """
    def __init__(self,printout=None):
        self.paramDesc={}#list containing description, order for form, function if calculated by others values, type if special (files)
        self.parameters={}
        self.parameters['filename']="param.par"
        self.paramDesc['filename']=["Filename",1,None,'file']
        self.parameters['wavelength']=1.542
        self.paramDesc['wavelength']=["Wavelength (A)",2,None,None]
        self.parameters['D']=1.0
        self.paramDesc['D']=["Detector to sample distance (cm)",3,None,None]
        self.parameters['pixel size']=1.0
        self.paramDesc['pixel size']=["Pixel size (cm)",4,None,None]
        self.parameters['q by pixel']=-1.0
        self.paramDesc['q by pixel']=["q by pixel (-1 if not used)",5,None,None]
        self.parameters['time']=1.0
        self.paramDesc['time']=["Exposition time (s)",6,None,None]
        self.parameters['backgd by s']=0.0 #par seconde
        self.paramDesc['backgd by s']=["Background by second",7,None,None]
        self.parameters['backgd by pix']=0.0 #par pixel
        self.paramDesc['backgd by pix']=["Background by pixel",8,None,None]
        self.parameters['backgd']=0.0 #par pixel
        self.paramDesc['backgd']=["Total background (B by pixel + B by s * time)",9,self.calculBack,None]
        self.parameters['comment']="comment"
        self.paramDesc['comment']=["Comment",10,None,None]
        self.parameters['Incident Flux']=-1.0
        self.paramDesc['Incident Flux']=["Incident Flux",11,None,None]
        self.parameters['Transmitted Flux']=-1.0
        self.paramDesc['Transmitted Flux']=["Transmitted Flux",12,None,None]
        self.parameters['transmission']=-1.0
        self.paramDesc['transmission']=["Transmission",13,self.calculTransm,None]
        self.parameters['thickness']=-1.0
        self.paramDesc['thickness']=["Thickness",14,None,None]
        self.parameters['DeltaOmega']=1.0
        self.paramDesc['DeltaOmega']=["Delta Omega", 15,self.calculDeltaOmega,None]
        self.parameters['K']=1.0
        self.paramDesc['K']=["K constant",16,None,None]
        self.parameters['flux']=1.0
        self.paramDesc['flux']=["Total Flux = Incident Flux * K (ph/s)",17,self.calculTotalFlux,None]
        self.printout=printout
        
        
        #self.parameters['monitor']=1

    def __repr__(self):
        chaine=""
        for var in self.parameters:
            chaine+=str(var)+" = "+str(self.parameters[var])+"\n"
        return chaine

    def printTXT(self,txt="",par=""):
        if self.printout==None:
            print(str(txt)+str(par))
        else:
            self.printout(txt,par)
            

    def order(self):
        '''
        return a list with dictionnary key ordered
        '''
        l={}
        for name in self.parameters:
            l[self.paramDesc[name][1]]=name
        list_ordered=[]
        for ord in l:
            list_ordered.append(l[ord])
        return list_ordered

    def calculate_All(self):
        '''
        calculate all the function defined in paramsDesc
        '''
        for name in self.paramDesc:
            if self.paramDesc[name][2]<>None:
                val=self.paramDesc[name][2]()


    def save_printable(self,file_name):
        #enregistre dans un fichier
        f=open(file_name,mode='w')
        f.write(self.__repr__())
        f.close()
        print file_name," saved"

    def save(self,file_name):
        import pickle
        f=open(file_name,mode='w')
        pickle.dump(self.parameters,f)
        f.close()

    def load(self,file_name):
        import pickle
        f=open(file_name,mode='r')
        par=pickle.load(f)
        for name in par:
            if self.parameters.has_key(name):
                self.parameters[name]=type(self.parameters[name])(par[name])
            else:
                self.parameters[name]=par[name]
        f.close()

    def calculate_q_by_pix(self):
        """
        calculate q by pix in A-1 from parameters (RAP)
        """
        self.parameters['q by pixel']=calculate_q(1,self)


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
        if self.parameters['q by pixel']<=0:
            self.printTXT('q=(4*pi/lambda)*sin(theta/2)   with tan(theta)=d/D    D : sample detector distance   d : pixel number (n) * pixel size')
            return ((4*pi)/float(self.parameters['wavelength']))*sin(arctan((float(self.parameters['pixel size'])*n)/float(self.parameters['D']))/2)
        else:
            return n*float(self.parameters['q by pixel'])

    def calculTransm(self):
        '''
        calculate Transmission
        '''
        self.parameters['transmission']=self.parameters['Transmitted Flux']/self.parameters['Incident Flux']
        return self.parameters['transmission']

    def calculDeltaOmega(self):
        '''
        calculate DeltaOmega
        '''
        #--deltaomega
        #print "DeltaOmega=(pixel size / distance sample detector)^2"
        self.parameters['DeltaOmega']=(float(self.parameters['pixel size']) / float(self.parameters['D']))**2
        return self.parameters['DeltaOmega']

    def calculTotalFlux(self):
        '''
        calculate Flux
        '''
        self.parameters['flux'] = float(self.parameters['Incident Flux'])*float(self.parameters['K'])
        return self.parameters['flux']

    def calculBack(self):
        '''
        calculate background
        '''
        self.parameters['backgd']=float(self.parameters['backgd by pix'])+float(self.parameters['backgd by s'])*float(self.parameters['time'])
        return self.parameters['backgd']

    def calculate_i(self,n,b=None,deviation=None,bdeviation=None):
        """
        Calculate i in cm-1 from parameters
        n : raw intensity
        b : empty cell to substract
        deviation : absolute deviation for i
        bdeviation : absolute deviation for background
        -----------------------------------
        DeltaOmega=(pixel size / distance sample detector)^2
        Flux = (monitor/transmission)*K
        Intensity=(n-background)/(time * DeltaOmega * Transmission * Thickness * Flux)
        if empty cell (b) then     Final Intensity=( Intensity(with Thickness=1) - empty cell)/thickness
        """
        self.printTXT("---- setting absolute scale ----")
        #--deltaomega
        self.printTXT("DeltaOmega=(pixel size / distance sample detector)^2")
        self.printTXT('Delta Omega is : ',self.parameters['DeltaOmega'])
        #-- flux
        self.printTXT( "Flux is : (cps/s) ", self.parameters['flux'])
        #-- background
        self.printTXT( "background is", self.parameters['backgd'])
        if deviation!=None:
            newdeviation=deviation
        #-- I
        if b==None:
            self.printTXT( "Intensity=(n-background)/(time * DeltaOmega * Transmission * Thickness * Flux)")
            i=(n-self.parameters['backgd'])/(float(self.parameters['time'])*self.parameters['DeltaOmega']*float(self.parameters['transmission'])*float(self.parameters['thickness'])*float(self.parameters['flux']))
            if deviation!=None:
                self.printTXT( "Calculating deviation")
                newdeviation=deviation/(float(self.parameters['time'])*self.parameters['DeltaOmega']*float(self.parameters['transmission'])*float(self.parameters['thickness'])*float(self.parameters['flux']))
        else:
            self.printTXT( "Intensity=(n-background)/(time * DeltaOmega * Transmission * Flux)")
            i=(n-self.parameters['backgd'])/(float(self.parameters['time'])*self.parameters['DeltaOmega']*float(self.parameters['transmission'])*float(self.parameters['flux']))
            self.printTXT( "Final Intensity=( Intensity - empty cell)/thickness")
            i=(i-b)/float(self.parameters['thickness'])
            
            if (bdeviation!=None) and (deviation!=None):
                newdeviation=deviation/(float(self.parameters['time'])*self.parameters['DeltaOmega']*float(self.parameters['transmission'])*float(self.parameters['thickness'])*float(self.parameters['flux']))
                newdeviation=(newdeviation-bdeviation)/float(self.parameters['thickness'])
            else:
                self.printTXT( "background deviation is not specified, impossible to manage deviation ")
                deviation=None
                
        self.printTXT( "---- intensity scaled for "+str(len(n))," datas ----")
        if deviation!=None:
            return i,newdeviation
        else:
            return i
