import numpy
import os
import ConfigParser
import pySAXS
CFGFILE=pySAXS.__path__[0]+os.sep+"filefilters"+os.sep+"file_type.ini"

class fileImport():
        
    def __init__(self,filtername=None,extension='txt',description='data',\
                 icon='',comments='#',qcol=0,icol=1,errcol=2,skiprows=0,sep=None,xfactor=1.0):
        #------------- values which can be modified in ini file
        self.extension=extension#'txt'
        self.description=description#'datas in 2 columns (or 3 with error)'
        self.icon=icon#''
        self.comments=comments#'#'
        self.qcol=qcol#0
        self.icol=icol#1
        self.errcol=errcol#-1 #if is -1, is not read
        self.skiprows=skiprows#0 
        self.sep=sep#None
        self.xfactor=xfactor
        #-------------- No dynamic values here
        self.q=None
        self.i=None
        self.err=None
        self.data=None
        #
        if filtername is not None:
            self._import_fileformat_(filtername)
        
    def read(self,filename):
        '''
        read a file
        '''
        #read
        useCols=[self.qcol,self.icol]
        if self.errcol >=0 :
            useCols.append(self.errcol)
        #print filename,useCols
        #print self.skiprows
        try:
            self.data=numpy.loadtxt(filename, comments=self.comments, skiprows=self.skiprows, \
                                    usecols=useCols,delimiter=self.sep)# Load data from a text file.
        except IndexError:
            #there is an error of columns (no error columns)
            print useCols
            useCols=useCols[:-1]
            self.errcol=-1
            self.data=numpy.loadtxt(filename, comments=self.comments, skiprows=self.skiprows,\
                                     usecols=useCols,delimiter=self.sep)# Load data from a text file.
        
        self.data=numpy.transpose(numpy.array(self.data))
        self.q=self.data[0]*self.xfactor
        self.i=self.data[1]
        #nan values management
        isnotNan=numpy.where(~numpy.isnan(self.i))
        self.q=self.q[isnotNan]
        self.i=self.i[isnotNan]
        if self.errcol >=0 :
            self.err=self.data[2]
            self.err=self.err[isnotNan]
            isnotNan=numpy.where(~numpy.isnan(self.err))
            self.err=self.err[isnotNan]
            self.q=self.q[isnotNan]
            self.i=self.i[isnotNan]
        #print self.q,self.i,self.err    
        return self.q,self.i,self.err
    
    def _import_fileformat_(self,filtername):
        '''
        import the file format from the config file
        '''
        rpt = ConfigParser.ConfigParser()
        rpt.read(CFGFILE)
        if rpt.has_section(filtername):
            list_of_options=rpt.options(filtername)
            for option in list_of_options:
                option=option.lower()
                value=rpt.get(filtername,option)
                #print option,value
                #print type(getattr(self, option))
                if option == 'sep':
                    #print "sep="+str(value)+"-"
                    self.sep=value
                else:
                    setattr(self, option,type(getattr(self, option))(value))
        else :
            print "filter not found"

def import_list():
    '''
    List all data file format
    '''
    rpt = ConfigParser.ConfigParser()
    rpt.read(CFGFILE)
    return rpt.sections()

def import_dict():
    '''
    List all data file format
    and return a dictionary
    '''
    rpt = ConfigParser.ConfigParser()
    rpt.read(CFGFILE)
    d={}
    for section in rpt.sections():
       d[section]=[rpt.get(section,'description'),rpt.get(section,'extension')]
    return d 
    
    
        