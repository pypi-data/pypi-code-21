"""
pySAXS routines for ultra small angle xray scattering.
Lake deconvolution
background substraction,...

version LSusaxs replacing LSreg by OT 7-2012
version 0.1 22/03/2006
version OS 20/11/2009
"""
#import scipy.io  as SPio remplaced by Numpy.loadtxt()
from scipy.optimize import leastsq
from scipy import interpolate
import os
from string import rsplit
import numpy
import time as t
import pySAXS

file_resfunc=os.path.dirname(pySAXS.__file__) + os.sep +"saxsdata"+os.sep+"usaxs_res_func.dat"

CONSTANTBACKGROUND='Constant background'
POWERLAW='Power law'


'''def ReadUSAXSData(filename):
    return SPio.array_import.read_array(filename,columns=(0,-2),lines=(1,-1))

def WriteUSAXSdata(filename,data):
    return SPio.array_import.write_array(filename,data,separator=' ')
'''
def BackgroundCorrection(I,bkg):
    return I-bkg

def QtoTheta(q,wavelength=1.542):
    '''
    Converts q to theta
    '''
    return numpy.arcsin(q*wavelength)/(2.*numpy.pi)

def ThetatoQ(Theta,wavelength=1.542):
    '''
    Converts theta to q
    '''
    return 4.*(numpy.pi/wavelength)*numpy.sin(Theta/2.)

def ZeroCentre(q,I):
    '''
    Converts the q making the peak at zero
    '''
    return (q-q[numpy.argmax(I)])

def select(q,I,n):
    '''
    Selects the q,I for n points around the maximum
    '''
    x=ZeroCentre(q,I)
    sel= numpy.arange(numpy.argmax(I)-n,numpy.argmax(I)+n)
    y_sel=numpy.take(I, sel)
    x_sel=numpy.take(q, sel)
    return x_sel,y_sel

def somme(q,I):
    '''
    This gives the sum(I*delta q)
    '''
    #print  'Area in the central beam', numpy.trapz(y,x)
    return numpy.trapz(I,q)

def gaussian(par, x):
       f=par[0]*(numpy.exp(-par[1]*(x-par[2])*(x-par[2])))
       return f

def residuals(par, y, x):
        err = (y-gaussian(par,x))
        return err

def FitGauss(q,I,n,a0,a1,a2,tol=1e-15,it=2000):
        q1,I1=select(q,I,n)
        #I1=select(q,I,n)[1]
        plsq = leastsq(residuals, ([a0,a1,a2]), args=(I1, q1), ftol=tol, maxfev=it)
        #print plsq[0]
        return gaussian(plsq[0],q1),q1,I1,plsq[0]


def Qscalemod(dq,q,step):

       return q+dq+step

def InterpolateForCommonvalue(qexp,Iexp,qrock,Irock):
        '''
        interpolate datas for substraction
        return qnew, I sample, I rock
        '''
        sel_qmin=numpy.max(numpy.min(qrock),numpy.min(qexp))
        sel_qmax=numpy.min(numpy.max(qrock),numpy.max(qexp))
        qnew1=numpy.repeat(qexp,qexp>=sel_qmin)
        #qnew=numpy.repeat(qexp,(qexp>=min(qrock)))
        #qnew=numpy.repeat(qexp,(qexp<=max(qrock)))
        qnew=numpy.repeat(qnew1,qnew1<=sel_qmax)
        #spl_samp=interpolate.splrep(qexp,Iexp, k=3)
        #Ip_samp=interpolate.splev(qnew,spl_samp)


        Isamp=interpolate.interp1d(qexp,Iexp, kind='linear')
        Ip_samp=Isamp(qnew)
        #spl_rock=interpolate.splrep(qrock,Irock, k=3)
        #Ip_rock=interpolate.splev(qnew,spl_rock)
        Irocking=interpolate.interp1d(qrock,Irock, kind='linear')
        Ip_rock=Irocking(qnew)
        return qnew,Ip_samp,Ip_rock

def TransmissionValue(nsamp,nrock):
    '''
    calculate transmission : nsamp/nrock
    '''
    return nsamp/nrock

def TrCorrectedProf(qexp,Iexp,qrock,Irock,thickness,central_area,T):
    '''
    Transmission corrected profile
    qexp
    Iexp
    qrack
    Irock
    thickness : sample thickness
    central_area : Area in the central beam
    T : transmission
    '''
    qnew=InterpolateForCommonvalue(qexp,Iexp,qrock,Irock)[0]
    Ip_samp=InterpolateForCommonvalue(qexp,Iexp,qrock,Irock)[1]
    Ip_rock=InterpolateForCommonvalue(qexp,Iexp,qrock,Irock)[2]
    Ic1=(Ip_samp/T)-Ip_rock
    Ic=Ic1/(central_area*thickness)
    return qnew,Ic

def read_res_function():
    '''
    read the resolution function from the specified filename
    '''
    res=Numpy.loadtxt(file_resfunc)
    #res=SPio.array_import.read_array(file_resfunc,columns=(0,-1),lines=(0,-1))
    return res

def interpolate_res_func(x,resx=None,resy=None):
    '''
    Interpolated resolution function obtained from res_func.dat file
    if resx and resy are not None, use this datas
    '''
    if resx!=None:
        beta=resx#res[:,0]
        v=resy#res[:,1]
    else:
        read_res_function()
        beta=res[:,0]
        v=res[:,1]
    vf=interpolate.interp1d(beta,v, kind='linear')
    vf_intp=vf(x)
    return vf_intp

def porod(par, q):#Gives power law like Porod law
    f=par[0]*(q**(- par[1]) )
    return f

def smooth(y,ns):#Average point smoothing
    for i in range(len(y)-2*ns):
        y[i+ns]=sum(numpy.take(y,[i+ns-1,i+ns,i+ns+1]))/(2.*ns+1.)
    return   y

#******************************************************************************
#-----Start of Deconvolution program------------------------------------------
def lake(qexp,Iexp,it,type,ns,plotexp=None,resx=None,resy=None):
    '''
    Deconvolution subroutine based on Lake method
    qexp : q
    Iexp : I
    it    : ?
    type : CONSTANTBACKGROUND or POWERLAW
    ns    : ?
    plotexp    : plotexp (not used ?)
    resx : x resolution function
    resy : y resolution function
    '''
    #res=read_res_function(file_resfunc)
    Iexp0=Iexp
    qexp0=qexp
    for ii in range(0,it):
        last=Iexp.shape[0]-1
        sel=numpy.arange(last-9,last)
        I_sel=numpy.take(Iexp, sel)
        q_sel=numpy.take(qexp, sel)

        def residual(par, y, q):
            err = (y-porod(par,q))
            return err

        a0=Iexp0[0]
        a1=4.
        plsq = leastsq(residual, numpy.array([a0,a1]), args=(I_sel, q_sel), ftol=1e-15, maxfev=2000)
        def I(q):
            In=numpy.zeros(len(qexp))
            q1=numpy.repeat(q,q<=qexp[last])
            q2=numpy.repeat(q,q>qexp[last])
            In1=interpolate.interp1d(qexp,Iexp, kind='linear')
            In_a=In1(q1)
            if type==CONSTANTBACKGROUND:
               In_b=numpy.ones(len(q2))*Iexp[last]

            else:
                #type==POWERLAW:
                In_b=porod(plsq[0],q2)

            q1_list=q1.tolist()
            q2_list=q2.tolist()
            q1_list.extend(q2_list)
            In_a_list=In_a.tolist()
            In_b_list=In_b.tolist()
            In_a_list.extend(In_b_list)
            return numpy.array(In_a_list)

        def inte(x):
            int1=interpolate_res_func(x,resx,resy)*I((qexp*qexp+x*x)**0.5)
            return int1

        def sm1():
            l_limit=0.
            n = 100
            u_limit = 2.*qexp[last]
            h=( u_limit - l_limit)/float(n)
            sum=(inte(l_limit) + inte(u_limit))*0.5
            for i in range(1,n):
                x=l_limit+float(i*h)
                sum = sum + inte(x)
            return sum*h
        sm=2.*sm1()
        Icor=numpy.zeros(len(qexp))
        Icor=(Iexp/sm)*Iexp0
        Icor=smooth(Icor,ns)
        Iexp=Icor
        if (ii==it-1):
           break
    return Icor
#************************************************************************
#----End of deconvolution program----------------------------------------

#************************************************************************


#--------Please donot modify------------------------------------------------

def USAXS_count_convolute(q,Iabs,N0dX,thick,wavelength):
    '''
    This subroutine calculates the counts that will be observed on USAXS for a particular model with q,I in cm-1
    '''
    qexp=q
    Iexp=Iabs
    last=Iexp.shape[0]-1
    def I(q):#Interpolated
        In=numpy.zeros(len(qexp))
        q1=numpy.repeat(q,q<=qexp[last])
        q2=numpy.repeat(q,q>qexp[last])
        In1=interpolate.interp1d(qexp,Iexp, kind='linear')
        In_a=In1(q1)
        In_b=numpy.ones(len(q2))*Iexp[last]
        q1_list=q1.tolist()
        q2_list=q2.tolist()
        q1_list.extend(q2_list)
        In_a_list=In_a.tolist()
        In_b_list=In_b.tolist()
        In_a_list.extend(In_b_list)
        return numpy.array(In_a_list)

    def inte(x):#Integrand for sm1()
        int1=interpolate_res_func(x)*I((qexp*qexp+x*x)**0.5)
        return int1

    def sm1():
        l_limit=0.
        n = 100
        u_limit = 2.*qexp[last]
        h=( u_limit - l_limit)/float(n)
        sum=(inte(l_limit) + inte(u_limit))*0.5
        for i in range(1,n):
            x=l_limit+float(i*h)
            sum = sum + inte(x)
        return sum*h
    sm=sm1()

    return 2.*sm*N0dX*thick
#----------------End of USAXS convolute---------------------



def CalTransmission(mu_p,rho_p,mu_S,rho_S,phim_p,rho_soln,t):
    '''
    Calculates the transmission value for given sample parameters---
    '''
    mubyrho=(mu_p/rho_p)*phim_p+(mu_S/rho_S)*(1.-phim_p)
    T=numpy.exp(-mubyrho*rho_soln*t)
    return T
#print CalTransmission(193.305,8.9,6.06,1.188,0.435,1.9,0.0065)
#-----
def GoodnessOfFit(xexp,yexp,fmodel,par):
    '''
    This calculates the goodness of a fit
    '''
    ymodel=fmodel(xexp,*par)
    SStot=sum((yexp-mean(yexp))**2.)
    SSreg=sum((ymodel-yexp)**2.)
    return 1.-(SSreg/SStot)
#---------END----------------------


def calculate_res_func_USAXS(filename,c,step,boun):
    '''
    This routine calculates the resolution function for the USAXS
    c is the slit length
    step is the step size for the V(beta) profile
    boun is the extreme left/right beta value for the V(beta) for which it shoule calculate the V(beta)
    '''

    gplt = Gnuplot.Gnuplot()
    gplt.reset()
    beam=SPio.array_import.read_array(filename,columns=(0,-1),lines=(1,-1))
    w=beam[:,0]
    z=beam[:,1]
    r=numpy.arange(-2*c,2*c,c*step)
    last=len(z)-1
    def I(x):
        x0=numpy.repeat(x,x<w[0])
        x1a=numpy.repeat(x,x<=w[last])
        x1=numpy.repeat(x1a,x1a>w[0])
        x2=numpy.repeat(x,x>w[last])
        In1=interpolate.interp1d(w,z, kind='linear')
        In_a=In1(x1)
        In_b=numpy.zeros(len(x2))
        In_c=numpy.zeros(len(x0))
        x0_list=x0.tolist()
        x1_list=x1.tolist()
        x2_list=x2.tolist()
        x0_list.extend(x1_list)
        x0_list.extend(x2_list)
        In_0_list=In_c.tolist()
        In_1_list=In_a.tolist()
        In_2_list=In_b.tolist()
        In_0_list.extend(In_1_list)
        In_0_list.extend(In_2_list)
        return numpy.array(In_0_list)

    def inte(x):
        int1=I(x)
        return int1

    def v1(u):
        l_limit=u-c
        n = 100
        u_limit = u+c
        h=( u_limit - l_limit)/float(n)
        sum=(inte(l_limit) + inte(u_limit))*0.5
        for i in range(1,n):
            x=l_limit+float(i*h)
            sum = sum + inte(x)
        return sum*h

    v=[]
    for i in range(len(r)):
        v.append(v1(r[i])[0])
    v=v/max(v)
    r_low=numpy.arange(-boun,-2*c,(boun-2.*c)/len(r))
    r_high=numpy.arange(2*c,boun,(-2.*c+boun)/len(r))
    v_low=numpy.zeros(len(r_low))
    v_high=numpy.zeros(len(r_high))
    vf1=numpy.concatenate((v_low,v))
    vfinal=numpy.concatenate((vf1,v_high))
    rf1=numpy.concatenate((r_low,r))
    rfinal=numpy.concatenate((rf1,r_high))
    data=numpy.zeros((len(rfinal),2))
    data[:,0]=rfinal
    data[:,1]=vfinal
    WriteUSAXSdata(file_resfunc,data)
    #GD3=Gnuplot.Data(rfinal,vfinal,with_='linespoints')
    #gplt.plot(GD3)
    return rfinal,vfinal
#------------------------------------END------------------------------

