# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 08:59:11 2017

@author: danaukes
using information from: http://lpsa.swarthmore.edu/NumInt/NumIntFourth.html
http://depa.fquim.unam.mx/amyd/archivero/DormandPrince_19856.pdf
"""
import numpy

class Integrator(object):

    def __init__(self,f,x0,t,tol = 1e-7,h_min = None):
        self.f = f
        self.t = t
        self.h = t[1]-t[0]
        self.tol = tol
        self.h_min = h_min or self.h*1e-3
        self.h_max = self.h
        self.x0 = x0
    
    def run(self,args = None):
        x = []
        x.append(self.x0)
        for time in self.t:
            x.append(self.step(time,x[-1],args = args))
        return numpy.array(x)[1:]
    
class RK4(Integrator):
    def step(self,t,x,args = None):
        h = self.h
        f = self.f
        
        args = args or []
        
        x = list(x)
        k1 = numpy.array(f(x,t,*args))
        k2 = numpy.array(f((x+k1*(h/2)),t+h/2,*args))
        k3 = numpy.array(f((x+k2*(h/2)),t+h/2,*args))
        k4 = numpy.array(f((x+k3*h),t+h,*args))        
        
        x1 = x+(k1+2*k2+2*k3+k4)/6*h
    
        return x1

class DoPri(Integrator):
    def step(self,t,x,args = None):
        raise(Exception('not working yet'))
        h = self.h
        f = self.f
        
        args = args or []
        
        x = numpy.array(x)
        
        a = 1/5
        b = 1/5
        c = 3/40
        d = 9/40
        e = 3/10
        ff = 44/45
        g = -56/15
        hh = 32/9
        i = 4/5
        j = 19372/6561
        k = -25360/2187
        l = 64448/6561
        m = -212/729
        n = 8/9
        o = 9017/3168
        p = -355/33
        q = -46732/5247
        r = 49/176
        s = -5103/18656
        tt = 1
        u = 35/384
        v = 0
        w = 500/1113
        xx = 125/192
        y = -2187/6784
        z = 11/84
        aa = 1
        
        k1 = h*numpy.array(f(x,t,*args))
        k2 = h*numpy.array(f((x+a*k1),t+b*h,*args))
        k3 = h*numpy.array(f((x+c*k1+d*k2),t+e*h,*args))
        k4 = h*numpy.array(f((x+ff*k1+g*k2+hh*k3),t+i*h,*args))
        k5 = h*numpy.array(f((x+j*k1+k*k2+l*k3+m*k4),t+n*h,*args))
        k6 = h*numpy.array(f((x+o*k1+p*k2+q*k3+r*k4+s*k5),t+tt*h,*args))
        
        jj = x+u*k1+v*k2+w*k3+xx*k4+y*k5+z*k6
        k7 = numpy.array(f(jj,t+aa*h,*args))
        

        x1 = x+(k1+2*k2+2*k3+k4)/6*h
        
        zk1 =   x + 5179/57600*k1 + 7571/16695*k3 + 393/640*k4 + -92097/339200*k5 + 187/2100*k6 + 1/40*k7
        error = numpy.abs(x1-zk1).max()

        s = (self.tol*h/(2*error))**(1/5)
        hopt = s*h
        if(hopt<self.h_min):
            self.h=self.h_min
        elif hopt> self.h_max:
            self.h = self.h_max
        else:
            self.h = hopt
    
        return x1