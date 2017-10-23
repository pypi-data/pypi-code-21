import numpy as np

def BinGrid(xdata,ydata,Xgrid,thres):
    """Bin the data with the binning grid Xgrid, the out put is a dictionanry with fields:\n
    xmean: Binned x values; ymean: Binned y values; ystd/xstd: std of x/y; xstdm/ystdm: std of mean; \n
    xlist/ylist: list of data points in each bin"""
    Xgrid = np.sort(Xgrid)

    N=len(Xgrid)
    xlist = (N-1)*[None]
    ylist=  (N-1)*[None]
    for i in range(1,N):
        mask=(xdata<Xgrid[i]) & (xdata>=Xgrid[i-1])
        xlist[i-1]=xdata[mask]
        ylist[i-1]=ydata[mask]

    xmean = np.zeros(N-1)
    xstdm = np.zeros(N-1)
    ymean = np.zeros(N-1)
    ystdm = np.zeros(N-1)
    xstd = np.zeros(N-1)
    ystd = np.zeros(N-1)

    for i in range(0,N-1):
        if len(xlist[i])>thres:
            xmean[i]=np.mean(xlist[i])
            ymean[i]=np.mean(ylist[i])
            xstd[i]=np.std(xlist[i])*np.sqrt(len(xlist[i]))/np.sqrt(len(xlist[i])-1)
            ystd[i]=np.std(ylist[i])*np.sqrt(len(xlist[i]))/np.sqrt(len(xlist[i])-1)
            xstdm[i]=np.std(xlist[i])/np.sqrt(len(xlist[i]))
            ystdm[i]=np.std(ylist[i])/np.sqrt(len(xlist[i]))
        else:
            xmean[i]=np.nan
            ymean[i]=np.nan
            xstd[i] = np.nan
            ystd[i] = np.nan
            xstdm[i] = np.nan
            ystdm[i] = np.nan
    return {'xmean':xmean,'ymean':ymean,'ystd':ystd,'xstd':xstd,'xstdm':xstdm,'ystdm':ystdm,'xlist':xlist,'ylist':ylist}

def FiniteD(xdata,ydata,SD,xerr=None,yerr=None):
    if (xerr is None) or (yerr is None):
        xerr=xdata*0
        yerr=ydata*0
    out=np.zeros(len(xdata))
    outerr=out*0
    for i in range(0,len(xdata)):
        k1 = np.max([0, i - SD])
        k2 = np.min([len(xdata)-1, i + SD])
        if (k2 - k1) == (SD * 2):
            k0 = np.int_(np.round((k1 + k2) / 2))
            X = [xdata[k1], xdata[k0], xdata[k2]]
            Y = [ydata[k1], ydata[k0], ydata[k2]]
            p = np.polyfit(X, Y, 2)
            dp = np.polyder(p)
            out[i] = np.polyval(dp, xdata[i])
        else:
            out[i] = (ydata[k2] - ydata[k1]) / (xdata[k2] - xdata[k1])
        deltay = np.sqrt(yerr[k2] ** 2 + yerr[k1] ** 2)
        deltax = np.sqrt(xerr[k2] ** 2 + xerr[k1] ** 2)
        outerr[i] = np.sqrt((deltay / (xdata[k2] - xdata[k1])) ** 2 + (deltax * (ydata[k2] - ydata[k1]) / (xdata[k2] - xdata[k1]) ** 2) ** 2)

    return [out,outerr]

def TailTailor(x,y,xmin,xmax):
    mask=(x<xmin) | (x>xmax)
    mask= mask & (~np.isnan(y))
    xfit=x[mask]
    yfit=y[mask]

    if len(xfit)==0:
        print('Warning: No tail data point included in background removal')
        yf=y.copy()
    else:
        P=np.polyfit(xfit,yfit,1)
        yfitted=np.polyval(P,x)
        yf=y-yfitted
    return yf

def clean_nan(inlist):

    outlist=[]
    mask = np.array(len(inlist[0]) * [True])
    for i in range(0,len(inlist)):
        mask = mask & (~np.isnan(inlist[i]))

    for i in range(0,len(inlist)):
        outlist.append(inlist[i][mask])

    return outlist