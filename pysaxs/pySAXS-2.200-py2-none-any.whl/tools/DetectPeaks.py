from numpy import *
from scipy import  interpolate
from pySAXS import models

def findPeaks(x,y,pp,percent,printout=None,method='gaussian'):
        '''
        find peaks on x,y datas
        return array aof founds peaks [center position, max,fwhm], x, and y of fitted datas
        pp : Window for scan
        percent  : Peaks height from the background (in percent)
        '''
        def printTXT(txt):
            if printout==None:
                print txt
            else:
                printout.printTXT(txt)
        founds=[]
        newx=None
        #derivate datas        
        tck = interpolate.splrep(x,y,s=0)
        yder = interpolate.splev(x,tck,der=1) #derivate
        printTXT( "---------      peak detection ---------")
        lastpeak=0
        n=0 #number of detected peaks
        imin=x.min()
        imax=x.max()
        window=int(pp/2)
        pp=int(pp)
        for ii in range(window,len(y)-pp):
                #calculate mean on the derivate for the two part of the window
                try:
                    mean1=yder[ii-window:ii].mean()
                    mean2=yder[ii:ii+window].mean()
                except:
                    printTXT("Error on input data, cannot calulate derivative")
                    return
                
                if mean1>0 and mean2<0:
                    #first part of the derivate >0 and the second one is <0 there is a peak.
                    mn=y[ii-window:ii+window].min()-imin
                    mx=y[ii-window:ii+window].max()-imin
                    h=mx-mn
                    if mx>mn*(1+percent):
                        #print "I have a peak between ",q[ii]," and ",q[ii+pp]
                        if ii<lastpeak+pp:
                            #print "same peak"
                            pass
                        else:
                            #print "new peak between ",q[ii]," and ",q[ii+pp]," last peak",lastpeak
                            lastpeak=ii
                            #self.printTXT( "mean : "+str(yder[ii-window:ii].mean())+" - "+str(yder[ii:ii+window].mean()))
                            if method!='gaussian':
                                #try to fit with trapez
                                res,result_x,result_y=fitPeakWithTrapez(x[ii-window:ii+window*2-1],y[ii-window:ii+window*2-1])
                            else :
                                #try to fit with gaussian
                                res,result_x,result_y=fitPeakWithGaussian(x[ii-window:ii+window*2-1],y[ii-window:ii+window*2-1])
                            #printTXT(  "found peak at x="+str(res[2])+"\t i="+str(res[0])+ "\t fwhm="+str(res[1]))
                            founds.append([res[0],res[1],res[2]])
                            n+=1
                            if newx is None:
                                newx=result_x
                                newy=result_y
                            else:
                                #print result_q
                                newx=concatenate((newx,array(result_x)))
                                newy=concatenate((newy,result_y))
                            
        #end of peak search
        #if n>0:
        #    self.data_dict[label+" peaks"]=dataset(label+" peaks",numpy.array(newq),numpy.array(newi),comment=label+" peaks",type='calculated')#[data[0], data[1], datafilename, True]
       # printTXT(str(n)+" peaks found ---------")    
        #self.redrawTheList()
        return founds,newx,newy
    
    
def fitPeakWithGaussian(x,y):
        '''
        fit peak with a gaussian
        x, and y are the datas,
        return result for fit as list [height,fwhm,center,zero],x, and fitted y
        '''
        gauss=models.Gaussian()
        istofit=[False,True,True,False]
        gauss.q=x
        #print q
        #print i
        maxy=y.max()#height 
        miny=y.min()
        maxx=x.max()
        minx=x.min()
        center=x[y.argmax()]
        fwhm=(maxx-minx)/4.0
        gauss.Arg=[maxy,fwhm,center,miny]
        #print "initial parameters : ",gauss.Arg
        bounds=[(maxy*0.9,maxy*1.1),(fwhm*0.2,fwhm*1.5),(minx,maxx),(miny*0.9,miny*1.1)]
        #print "bounds : ",bounds
        #print gauss.Arg
        #print bounds
        res=gauss.fitBounds(y,bounds)
        gauss.setArg(res)
        #print "res : ",res
        newy=gauss.getIntensity()
        return res,x,newy
    
def fitPeakWithTrapez(x,y):
    '''
    fit peaks with trapez
    x, and y are the datas,
    return result for fit as list [height,fwhm,center,zero],x, and fitted y
    '''
    x=array(x)
    y=array(y)
    modl=models.Trapez()
    #print "trapez"
    '''
    par[0] : center
    par[1] : FWHM
    par[2] : slope
    par[3] : height
    par[4] : zero
    '''
    istofit=[True,True,True,True,True]
    modl.q=x
    #estimate initial parameters
    maxy=y.max()#height 
    miny=y.min()
    maxx=x.max()
    minx=x.min()
    center=(minx+maxx)/2.0
    fwhm=(maxx-minx)/4.0
    modl.Arg=[center,fwhm,0.5,maxy,miny]
    #estimate bounds
    #bounds=[(minx,maxx),(fwhm*0.2,fwhm*1.5),(0.1,2),(maxy*0.9,maxy*1.1),(miny*0.9,miny*1.1)]
    #fit with bounds
    res=modl.fit(y)
    #get y with found parameters
    modl.setArg(res)
    newy=modl.getIntensity()
    #return
    res=[res[3],res[1],res[0],res[4]]
    return res,x,newy