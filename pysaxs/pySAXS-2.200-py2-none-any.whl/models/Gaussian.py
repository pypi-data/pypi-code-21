from pySAXS.models.model import Model
import numpy

class Gaussian(Model):
    '''
    Gaussian model
    by OT : 09/06/2009
    '''
    
    def GaussianFunction(self,q,par):
        """
        Gaussian model to fit the peak to get exact zero position
        par[0] : height of gaussian
        par[1] : is related to the FWHM
        par[2] : center of gaussian
        par[3] : background
        """
        sigm=par[1]*((2*numpy.log(2))**0.5)/2
        return (par[0]-par[3])*numpy.exp(-((q-par[2])**2)/sigm**2)+par[3]
    
    def prefit(self,x,y):
        '''
        try to determine some parameters from the datas
        '''
        center=(x[0]+x[-1])/2
        FWMH=(x[-1]-x[0])/10
        slope=FWMH/2
        maxi=y.max()
        mini=y.min()
        if len(y)>10:
            m=y[:10].mean()
            HalfValue=(maxi-mini)/2
            if HalfValue<m:
                #decreasing front
                t=maxi
                maxi=mini
                mini=t
            #idx = numpy.argmin(numpy.abs(y - HalfValue))
        self.Arg=[maxi,FWMH,center,mini]
        return self.Arg
    
    '''
    parameters definition
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.GaussianFunction #function
        self.N=0
        self.q=numpy.arange(-10,10,0.2)      #q range(x scale)
        self.Arg=[100.,1.,0.5,0]            #list of parameters
        self.Format=["%f","%f","%f","%f"]      #list of c format
        self.istofit=[True,True,True,True]    #list of boolean for fitting
        self.name="Gaussian"          #name of the model
        self.Doc=["max (or min) of gaussian"\
                 ,"FWHM"\
                 ,"center of gaussian"\
                 ,"background"] #list of description for parameters
        self.Description="Gaussian model for x-ray beam"  # description of model
        self.Author="Olivier Tache'"       #name of Author
    
if __name__=="__main__":
    '''
    test code
    '''
    g=Gaussian()
    g.Arg=[100,10,50,0]
    import Gnuplot
    gp=Gnuplot.Gnuplot()
    c=Gnuplot.Data(g.q,g.getIntensity(),with_='points')
    gp.plot(c)
    
    yn=g.getNoisy()
    cn=Gnuplot.Data(g.q,yn,with_='points')
    gp.plot(c,cn)
    res=g.fit(yn) 
    
    cf=Gnuplot.Data(g.q,g.IntensityFunc(g.q,res),with_='lines')
    gp.plot(c,cn,cf)
    raw_input("enter")    
    
    bounds=[(0,200),(2,12),(30.0,55.0),(-1,2)]
    res2=g.fitBounds(yn,bounds)
    print res2
    raw_input("enter")  
    
