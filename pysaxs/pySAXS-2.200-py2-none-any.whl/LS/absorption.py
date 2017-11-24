from string import *
from math import *
from numpy import *
import os
#import re
import pySAXS
import pySAXS.tools.isNumeric


ATOMS=[	"H","He","Li","Be","B","C","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U"]

ATOMS_NAME=["Hydrogen","Helium","Lithium","Beryllium","Boron","Carbon, Graphite","Nitrogen","Oxygen","Fluorine","Neon","Sodium","Magnesium","Aluminum","Silicon","Phosphorus","Sulfur","Chlorine","Argon","Potassium","Calcium","Scandium","Titanium","Vanadium","Chromium","Manganese","Iron","Cobalt","Nickel","Copper","Zinc","Gallium","Germanium","Arsenic","Selenium","Bromine","Krypton","Rubidium","Strontium","Yttrium","Zirconium","Niobium","Molybdenum","Technetium","Ruthenium","Rhodium","Palladium","Silver","Cadmium","Indium","Tin","Antimony","Tellurium","Iodine","Xenon","Cesium","Barium","Lanthanum","Cerium","Praseodymium","Neodymium","Promethium","Samarium","Europium","Gadolinium","Terbium","Dysprosium","Holmium","Erbium","Thulium","Ytterbium","Lutetium","Hafnium","Tantalum","Tungsten","Rhenium","Osmium","Iridium","Platinum","Gold","Mercury","Thallium","Lead","Bismuth","Polonium","Astatine","Radon","Francium","Radium","Actinium","Thorium","Protactinium","Uranium"]

COMMON_XRAY_SOURCE_MATERIALS=['Cu','Cr','Mo']
COMMON_XRAY_SOURCE_ENERGY={'Cu':8.04105057076251,'Cr':5.41159550114,'Mo':17.4432170305}

ATOMS_MASSE=array([1.0079,4.0026,6.9410,9.0122,10.8110,12.0107,14.0067,15.9994,18.9984,20.1797,22.9897,24.3050,26.9815,28.0855,30.9738,32.0650,35.4530,39.9480,39.0983,40.0780,44.9559,47.8670,50.9415,51.9961,54.9380,55.8450,58.9332,58.6934,63.5460,65.3900,69.7230,72.6400,74.9216,78.9600,79.9040,83.8000,85.4678,87.6200,88.9059,91.2240,92.9064,95.9400,98.0000,101.0700,102.9055,106.4200,107.8682,112.4110,114.8180,118.7100,121.7600,127.6000,126.9045,131.2930,132.9055,137.3270,138.9055,140.1160,140.9077,144.2400,145.0000,150.3600,151.9640,157.2500,158.9253,162.5000,164.9303,167.2590,168.9342,173.0400,174.9670,178.4900,180.9479,183.8400,186.2070,190.2300,192.2170,195.0780,196.9665,200.5900,204.3833,207.2000,208.9804,209.0000,210.0000,222.0000,223.0000,226.0000,227.0000,232.0381,231.0359,238.0289,237.0000],float)

MENDELEIEV_TABLE =[['H', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 'He'],\
            ['Li', 'Be', None, None, None, None, None, None, None, None, None, None, 'B', 'C', 'N', 'O', 'F', 'Ne'],\
             ['Na', 'Mg', None, None, None, None, None, None, None, None, None, None, 'Al', 'Si', 'P', 'S', 'Cl', 'Ar'],\
              ['K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr'],\
               ['Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe'],\
               ['Cs','Ba','La','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn'],\
               ['Fr','Ra','Ac',None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],\
               [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],\
               ['Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu',None, None, None, None],\
               ['Th', 'Pa', 'U', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]

KEV2ANGST = 12.39841875

def SymbolToAtomicNumber(symbol):
    '''
    get the atomic number of a symbol
    copy of xraylib.SymbolToAtomicNumber(symbol)
    >>> SymbolToAtomicNumber('Cu')
    29
    '''
    return ATOMS.index(symbol)+1

def AtomicNumberToSymbol(Z):
    '''
    get the symbol from an atomic number
    copy of xraylib.AtomicNumberToSymbol(Z)
    >>> AtomicNumberToSymbol(29)
    'Cu'
    '''
    return ATOMS[Z-1]

def getNameZ(Z):
    '''
    return the name from a Z
    >>> getNameZ(29)
    'Copper'
    '''
    return ATOMS_NAME[Z-1]


def getEnergyFromSource(source='Cu'):
    '''
    return the KA LINE (most used) energy from the x-ray source
    >>> getEnergyFromSource('Cu')
    8.04105057076251
    >>> getEnergyFromSource('Mo')
    17.443217030477935
    '''
    if COMMON_XRAY_SOURCE_ENERGY.has_key(source):
        return COMMON_XRAY_SOURCE_ENERGY[source]
    else:
        return 0

def getAtomsSymbole(S):
    """
    Transform a string containing a chimical formula ('C 1 O 2') in two array
    - list of atoms
    - numeric array of atoms number
    7-13-2012 by OT
    """
    S=S.strip()
    L=S.split(' ') #cut at all spaces
    rS=L[::2] #Symbols to be return
    rN=array(L[1::2],dtype='float') #Numbers to be return
    return rS,rN
    
def getAtomsSymboleOLD(S):
    """
    Ceci est une fonction qui transforme une chaine de caracteres de formule
    chimique en deux tableaux l'un de chaine de caractere avec les symboles
    chimiques l'autre avec le nombre d'atome en question.
    version lourdo bugger pour le moment
    """

    r=re.compile('\W')
    return r.split(S.strip())[::2],  asarray(r.split(S.strip())[1::2]).astype(float)

def setAtomsSymbole(atomS,atomN):
    """
    Ceci est une fonction qui transforme une liste de symbole chimique 
    et de nombre en une chaine de caractere.
    """
    S=''
    if len(atomS)==len(atomN):
        for i in range(len(atomS)):
            S=S+' '+str(atomS[i])+' '+str(atomN[i])
    return S.strip()


def getAllMu():
    """
    This function returns a big table with all NIST xray absorption data.
    For practical script it is not useful!
    """
    MUDATA=array([0,0,0,0],float)
    MUDATA=reshape(MUDATA,(1,4))
    ndata=0
    for i in arange(92):
        file=os.path.dirname(pySAXS.__file__)+os.sep+"saxsdata"+os.sep+str(i+1)+".dat"
        f=open(file,'r')
        nbl=int(f.readline())
        for j in arange(nbl):
            if ndata<>0:
                MUDATA=resize(MUDATA,(ndata+1,4))
            S=f.readline().strip()
            S=S.split('  ' )
            MUDATA[ndata,0]=i+1
            MUDATA[ndata,1]=float(S[0])
            MUDATA[ndata,2]=float(S[1])
            MUDATA[ndata,3]=float(S[2])
            ndata=ndata+1
        f.close
    return MUDATA


def getMasseZ(Z):
    """
    This function returns the molar mass of the atom with atomic number Z
    """
    return ATOMS_MASSE[Z-1]

def getMasseSymbole(S):
    """
    This function returns the molar mass of the atom with symble S
    (ie 'C' fo carbon, 'Au' for gold)
    """
    Z=ATOMS.index(S)+1
    return getMasseZ(Z)

def getMasseName(S):
    """
    This function returns the molar mass of the atom with name S
    (ie 'Carbon' , 'Gold')
    """
    Z=ATOMS_NAME.index(S)+1
    return getMasseZ(Z)

def getMuFormula(S,NRJ=8.028,ISEN=1):
    """
    This function returns the mass attenuation coefficient for a chemical
    formula in the form 'C 6 H 6 O 2 N 1' 
    7-13-2012 by OT improved for formula with fraction 'Si 1.2 Al 0.8'
    """
    if len(S)!=0:
        S,N=getAtomsSymbole(S)
        Mu=zeros(len(S),float)
        Ma=zeros(len(S),float)
        CMa=0.0
        CMu=0.0
        for i in arange(len(S)):
            Mu[i]=getMuSymbole(S[i],NRJ,ISEN)
            Ma[i]=getMasseSymbole(S[i])
            CMa=CMa+Ma[i]*N[i]
            CMu=CMu+Mu[i]*Ma[i]*N[i]
        return CMu/CMa
    else:
        return 0.0


def getMasseFormula(S,NRJ=8.028,ISEN=1):
    """
    This function returns the molar mass a chemical formula
    in the form  'C 6 H 6 O 2 N 1'
    TODO improve getAtomsSymbole 
    """
    if len(S)!=0:
        S,N=getAtomsSymbole(S)
        Ma=zeros(len(S),float)
        CMa=0.0
        for i in arange(len(S)):
            Ma[i]=getMasseSymbole(S[i])
            CMa=CMa+Ma[i]*N[i]
        return CMa
    else:
        return 0.0

def getElectronNumber(S):
    S,N=getAtomsSymbole(S)
    Z=0
    for i in arange(len(S)):
        Z=Z+(1+ATOMS.index(S[i]))*N[i]
    return Z

def getElectronDensity(S,rho):
    """
    return the electron density and the scattering length density
    """
    if len(S)!=0:
        #Thomson scattering length
        Belec=0.282e-12
        Navo=6.0221415e23
        M=getMasseFormula(S)
        Z=getElectronNumber(S)
        ED=(rho*Z*Navo)/M
        #print "rho=",rho,"\tZ=",Z,"\tNavo=",Navo,"\tM=",M,"\tED=",ED
        return ED,ED*Belec
    else:
        return 0.0,0.0
    

def getMuSymbole(S,NRJ=8.028,ISEN=1):
    """
    This function returns the xray absorption coefficient of the atom with
    symbole S (ie 'C' fo carbon, 'Au' for gold) by default NRJ is 8.03 keV
    and mass-energy absorption coefficient are return. To get the mass
    absorption coefficient ISEN has to be 0
    """
    if len(S)!=0:
        Z=ATOMS.index(S)+1
        return getMuZ(Z ,NRJ,ISEN)
    else:
        return 0.0

def getMuName(S,NRJ=8.028,ISEN=1):
    """
    This function returns the xray absorption coefficient of the atom with
    name S (ie 'Carbon' , 'Gold') by default NRJ is 8.028 keV and mass-energy
    absorption coefficient are return. To get the mass absorption coefficient
    ISEN has to be 0
    """
    if len(S)!=0:
        Z=ATOMS_NAME.index(S)+1
        return getMuZ(Z ,NRJ,ISEN)
    else:
        return 0.0

def getMuZ(Z,NRJ=8.028,ISEN=1):
    """
    This function returns the xray absorption coefficient of the atom with
    name S (ie 'Carbon' , 'Gold') by default NRJ is 8.028 keV and mass-energy
    absorption coefficient is returned. To get the mass absorption coefficient
    ISEN has to be 0
    """
    if Z>=0 and Z<=91: 
        MUDATA=array([0,0,0,0],float)
        MUDATA=reshape(MUDATA,(1,4))
        ndata=0
        #file=os.path.split(__file__)[0] + os.sep +"saxsdata"+os.sep+str(Z)+".dat"
        file=os.path.dirname(pySAXS.__file__) + os.sep +"saxsdata"+os.sep+str(Z)+".dat"
        f=open(file,'r')
        nbl=int(f.readline())
        for j in arange(nbl):
            if ndata<>0:
                MUDATA=resize(MUDATA,(ndata+1,4))
            S=f.readline().strip()
            S=S.split('  ')
            MUDATA[ndata,0]=Z
            MUDATA[ndata,1]=float(S[0])
            MUDATA[ndata,2]=float(S[1])
            MUDATA[ndata,3]=float(S[2])
            ndata=ndata+1
        f.close
        E=compress(where(MUDATA[:,0]==Z,MUDATA[:,1],0),MUDATA[:,1])
        if(ISEN==1):
            mu=compress(where(MUDATA[:,0]==Z,MUDATA[:,3],0),MUDATA[:,3])
        else:
            mu=compress(where(MUDATA[:,0]==Z,MUDATA[:,2],0),MUDATA[:,2])
        EMeV=NRJ*1e-3
        indice=arange(len(mu))
        z=zeros(len(mu))

        #on cherche la valeure inferieure a EMeV
        if EMeV >= E[0] :
            Elow=repeat(E,E <= EMeV)
            Elo=Elow[len(Elow)-1]
        else:
            # en dehors des indices on prend le premier coeff
            return E[0]
        #on cherche la valeure superieure a EMeV
        if EMeV <= E[len(E)-1]:
            Ehigh=repeat(E,E > EMeV)
            Ehi=Ehigh[0]
        else:
            #en dehors des indices on prend la derniere valeur
            return E[len(E)-1]
        alo=int(sum(where(E==Elo,indice,z)))
        ylo=mu[int(alo)]
        ahi=int(sum(where(E==Ehi,indice,z)))
        yhi=mu[int(ahi)]

        slp=(yhi-ylo)/(log10(Ehi)-log10(Elo))
        #interpolation lineaire entre les deux points...
        MU=ylo+slp*(log10(EMeV)-log10(Elo))
        return MU
    else:
        return 0.0

def getTransmission(formula,thickness=1.0,density=1.0,energy=8.03):
    '''
    return the transmission of a compound
    thickness in cm
    >>> getTransmission('H 2 O 1',0.1,density=1.0,energy=8.03)
    0.376802369048
    '''
    #calculate mu for compound
    mu=getMuFormula(formula,energy)
    #calculate Transmission
    return exp(-density*mu*thickness)

