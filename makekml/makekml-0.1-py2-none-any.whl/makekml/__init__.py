import zipfile
import os
import math
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import mplot
import mplot.plot
import copy
import datetime
from mplot.color import *
import numpy
from mpmath import *
mp.dps = 100
CONDENSEREDUCTION = 0.2
RADIUSOFEARTH = 6371
PI = pi
DEG = 360.0
SQRTOFTWO = float(math.sqrt(2.0))
TICKS = 5
OFFSET_HEIGHT = 10
OFFSET_WIDTH = 10
BUFFER = 80
FONTSIZE = 30
LEGENDFONTSIZE = 150
FONT = 'arial'
LWIDTH = 2500 # 2500
LHEIGHT = 2900 # 3500
LWIDTH_SUB = 2
LHEIGHT_SUB = 6
COLORMAPSCALE = 3
LEGN = 300
LEGWIDTH = 0.1

ONETHIRD = 1.0/3.0
TWOTHIRD = 2.0/3.0
HALF = 1/2.0
TOLERANCE = 0.001
STRINGTYPE = type('string')
DATETIMETYPE = type(datetime.datetime(2000,1,1))
DATETYPE = type(datetime.date(2000,1,1))
DATETYPES = [DATETYPE,DATETIMETYPE]
NOINTERSECT = 'polygons do not overlap'
NOUNION = 'polygons are neither adjacent nor overlapping' ## note difference, two polys adjacent have no intersection, but do have a union!
UNION = 'union'
INTERSECT = 'intersect'


BADDIES = {'&':'&amp;'}

def createfolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def degtorad(degrees):
    return degrees*2*PI/DEG

def radtodeg(rad):
    return rad*DEG/(2*PI)

def distance(point1,point2,latlong = True):
    '''
    point 1 = (lat,long)
    point 2 = (lat,long)
    '''
    lati,longi = getlatlong(latlong)
    lat1 = degtorad(point1[lati])
    lat2 = degtorad(point2[lati])
    lon1 = degtorad(point1[longi])
    lon2 = degtorad(point2[longi])
    a = pow(math.sin((lat2-lat1)/2.0),2)
    b = math.cos(lat1)*math.cos(lat2)*pow(math.sin((lon2-lon1)/2.0),2)
    ang = math.sqrt(a+b)
    dist = 2*RADIUSOFEARTH*math.asin(ang)
    return dist


def offsetcord(origin,heading,latlong = True):
    '''
    origin = (lat,long)
    heading = (x,y)
    '''
    lati,longi = getlatlong(latlong)
    olat = degtorad(origin[lati])
    olng = degtorad(origin[longi])
    x = math.fabs(heading[0])
    y = math.fabs(heading[1])
    if heading[0] < 0:
        ang = PI
    else:
        ang = 0
    hwlat = math.asin(math.sin(olat)*math.cos(x/float(RADIUSOFEARTH))+math.cos(olat)*math.sin(x/float(RADIUSOFEARTH))*math.cos(ang))
    dhwlng = math.atan2(math.sin(ang)*math.sin(x/float(RADIUSOFEARTH))*math.cos(olat),math.cos(x/float(RADIUSOFEARTH))-math.sin(olat)*math.sin(hwlat))
    hwlng = ((olng-dhwlng + PI)%(2*PI))-PI
    hw = (radtodeg(hwlat),radtodeg(hwlng))
    if heading[1] <0:
        ang = PI/2.0
    else:
        ang = -PI/2.0
    lat = math.asin(math.sin(hwlat)*math.cos(y/float(RADIUSOFEARTH))+math.cos(hwlat)*math.sin(y/float(RADIUSOFEARTH))*math.cos(ang))
    dlng = math.atan2(math.sin(ang)*math.sin(y/float(RADIUSOFEARTH))*math.cos(hwlat),math.cos(y/float(RADIUSOFEARTH))-math.sin(hwlat)*math.sin(lat))
    lng = ((hwlng-dlng+PI)%(2*PI))-PI
    endpoint = (radtodeg(lat),radtodeg(lng))
    return endpoint
    



def planaroffsetcord(origin,heading,latlong = True):
    '''
    origin = (lat,long)
    heading = (x,y)
    '''
    lati,longi = getlatlong(latlong)
    dlat = heading[0]/float(RADIUSOFEARTH)
    dlong = heading[1]/float(RADIUSOFEARTH*math.cos(degtorad(origin[lati])))
    cords = (origin[lati]+radtodeg(dlat),origin[longi]+radtodeg(dlong))
    return cords
    








def breaklines(string):
    terms = []
    newstring = ''
    for char in string:
        if char == '\n':
            terms.append(newstring)
            newstring = ''
        else:
            newstring += char
    terms.append(newstring)
    return terms

def gethsws(terms,offset_height,draw,font):
    hs = []
    ws = []
    for term in terms:
        wtemp,htemp = draw.textsize(term,font)
        hs.append(htemp)
        ws.append(wtemp)
    w = max(ws)
    h = sum(hs)+offset_height*len(terms)
    return hs,ws,h,w

def adjustheightwidth(image,loc,height,width,offset_height,offset_width):
    im = Image.open(image,'r')
    im_w,im_h = im.size
    if loc in ['bottom','top']:
        newheight = height + im_h+offset_height
        newwidth = width
        if im_w + offset_width > width:
            newwidth = im_w + offset_width
    else:
        raise Exception()
    return newheight,newwidth,im_h,im_w,im

def makelegend(fname,heatmap,title,miner,maxer,pre = '',post = '',tickmarks = None,font = FONT,legendfontsize = LEGENDFONTSIZE,offset_height = OFFSET_HEIGHT,offset_width = OFFSET_WIDTH,addimage = None,addloc = 'bottom',reverse = False,roundto = None):
    '''
    Ok this creates a basic legend of the formate:
    Title
    heatmap image
    additional image (e.g. logo)
    '''
    colormap(fname+'_map',heatmap,miner,maxer,pre,post,reverse = reverse,roundto = roundto,tickmarks = tickmarks)
    lmap = Image.open(fname+'_map.png','r')
    lmap_w,lmap_h = lmap.size    
    font = ImageFont.truetype(font+"bd.ttf",legendfontsize)
    temp = Image.new('RGBA',(100,100),(255,255,255,255))
    draw = ImageDraw.Draw(temp)
    terms = breaklines(title)
    tit_hs,tit_ws,tit_h,tit_w = gethsws(terms,offset_height,draw,font)
    height = tit_h + lmap_h 
    width = max(tit_w,lmap_w) + offset_width
    if addimage != None:
        height,width,im_h,im_w,im = adjustheightwidth(addimage,addloc,height,width,offset_height,offset_width)
    legend = Image.new('RGBA',(width,height),(255,255,255,255))
    woff = (width - lmap_w)/2
    hoff = tit_h 
    legend.paste(lmap,(woff,hoff,woff+lmap_w,hoff + lmap_h))
    draw = ImageDraw.Draw(legend)
    color = (0,0,0,255)
    cur_h = offset_height/2
    for i in range(0,len(terms)):
        draw.text(((width-tit_ws[i])/2,cur_h),terms[i],fill = color,font = font)
        cur_h += tit_hs[i]+offset_height
    if addimage!=None:
        ## todo - add more locs in..
        if addloc == 'bottom':
            hoff = tit_h+lmap_h+offset_height
            woff = (width - im_w)/2
            legend.paste(im,(woff,hoff,woff+im_w,hoff+im_h))
        else:
            raise Exception()
        
    legend.save(fname+'.png')


def makecategorylegend(legname,title,cats,pre = '',post ='',offset_height = OFFSET_HEIGHT):
    xsize = 1000
    ysize = 2000
    xgap = 10
    ygap = 10
    ytitlegap = 30
    boxsize = (130,100)
    titlefont = ImageFont.truetype("arialbd.ttf",100)
    font = ImageFont.truetype("arialbd.ttf",70)
    temp = Image.new('RGBA',(xsize,ysize),(255,255,255,255))
    draw = ImageDraw.Draw(temp)
    terms = breaklines(title)
    tit_hs,tit_ws,tit_h,tit_w = gethsws(terms,offset_height,draw,font)
    #xlegsize,ylegsize = draw.textsize(title,titlefont)
    xlegsize = tit_w
    ylegsize = tit_h
    color = (0,0,0,255)
    xs = [xlegsize+xgap*2]
    ys = ygap+ylegsize+ytitlegap
    trippy = []
    for cat in cats:
        x,y = draw.textsize(pre+cat[3]+post,font)
        xs.append(x+xgap*3+boxsize[0])
        ys+=boxsize[1]+ygap
        trippy.append(y)
    xsize = max(xs)
    ysize = ys
    legend = Image.new('RGBA',(xsize,ysize),(255,255,255,255))
    draw = ImageDraw.Draw(legend)
    cur_h = offset_height/2
    for i in range(0,len(terms)):
        draw.text(((xsize-tit_ws[i])/2,cur_h),terms[i],fill = color,font = font)
        cur_h += tit_hs[i]+offset_height
    
    #draw.text(((xsize-xlegsize)/2,ygap/2),title,font=titlefont,fill = color)
    #ysofar = ygap+ylegsize+ytitlegap
    
    for i in range(0,len(cats)):
        term = cats[i]
        fill = (term[2][0],term[2][1],term[2][2],255)
        draw.rectangle([(xgap,cur_h+boxsize[1]),(xgap+boxsize[0],cur_h)],fill = fill,outline = (0,0,0,255))
        draw.text((xgap*2+boxsize[0],cur_h+trippy[i]/2),pre+term[3]+post,font=font,fill=color)
        cur_h += boxsize[1]+ygap
    legend.save(legname+'.png')


def colormap(fname,heatmap,miner,maxer,pre,post,reverse = False,roundto= None,fontsize = FONTSIZE,tickmarks = None):
    ps = []
    for i in range(0,LEGN):
        x,y,c,l = colormapsub(i,heatmap,reverse = reverse)
        ps.append(mplot.plot.area(x,y,legend = l,alpha = 1,color = c,stacked = False,byxaxis = False))
    if tickmarks == None:
        yvals = []
        ylocs = []
        for i in range(0,TICKS):
            val = i/float(TICKS-1)
            yval = miner + val*(maxer-miner)
            strval = prettystr(yval,roundto=roundto)
            yvals.append(pre+strval+post)
            ylocs.append(val)
        ticks = (ylocs,yvals)
        if reverse:
            yvals.reverse()
    else:
        ticks = tickmarks
    mplot.plot.display(ps,fname,xticks=[[0,LEGWIDTH],['','']],yticks=[[0,1],['','']],figsize = [LWIDTH_SUB,LHEIGHT_SUB],second_yticks=ticks,fontsize = fontsize,areastacked = False)
    
    
def colormapsub(i,heatmap,reverse = False):
    slope = 1.0/float(LEGN)
    x = [0,LEGWIDTH,LEGWIDTH,0,0]
    y = [slope*i,slope*i,slope*(i+1),slope*(i+1),slope*i]
    val = (i+0.5)/float(LEGN)
    if reverse:
        val = 1- val
    r,g,b = heatmap((i+0.5)/float(LEGN),rgbonly = True)
    c = converttohex(r,g,b)
    l = None
    return x,y,c,l

def prettystr(val,roundto = None):
    string = ''
    if roundto != None:
        if roundto == 0:
            string += str(int(round(val,roundto)))
        else:
            string+= str(round(val,roundto))
    elif val <1:
        string+= str(round(val,2))
    elif val < 100:
        string+= str(round(val,1))
    else:
        string+= str(int(round(val,0)))
    return string

##def determinecolor(val,heatmap,splitpoint = ONETHIRD,reverse = False):
##    if heatmap == 'redgreen':
##        return redgreenheatmap(val,rgbonly = True)
##    if heatmap == 'bluered':
##        return blueredheatmap(val,rgbonly = True)
##    if heatmap == 'grayscale':
##        return grayscaleheatmap(val,rgbonly = True)
##    if heatmap == 'brown':
##        return brownheatmap(val,rgbonly = True)
##    if heatmap == 'purple':
##        return purpleheatmap(val,rgbonly = True)
##    if heatmap == 'lightgrey':
##        return lightgrayscaleheatmap(val,rgbonly = True)
##    if heatmap == 'darkredgreen':
##        return darkredgreenheatmap(val,splitpoint = splitpoint,rgbonly = True)
##    if heatmap == 'green':
##        return greenheatmap(val,rgbonly = True)
##    if heatmap == 'red':
##        return redheatmap(val,rgbonly = True)
##    raise Exception()


def triangle(cords,width,height = None,orientation = 'up',latlong = True,bearing = 0.0,bearrad = True):
    '''
    cords = (lat,long)
    orientation is one of: up,down,right,left
    '''
    if not bearrad:
        bear = degtorad(bearing)
    else:
        bear = bearing
    lati,longi = getlatlong(latlong)
    if height == None:
        height = width*math.sqrt(3.0)/2.0
    laty = cords[lati]
    longy = cords[longi]
    latang = height/float(2.0*RADIUSOFEARTH)
    if orientation in ['up','down']:
        latang = latang*2
    latlow = laty - radtodeg(latang)
    lathigh = laty + radtodeg(latang)
    longang_unjust = width/float(2.0*RADIUSOFEARTH)
    if orientation in ['right','left']:
        longang_unjust = longang_unjust*2
    longang = math.asin(math.sin(longang_unjust)/math.cos(degtorad(laty)))
    longlow = longy - radtodeg(longang)
    longhigh = longy + radtodeg(longang)
    if orientation in ['up','down']:
        latoff = radtodeg(latang)/3.0
    elif orientation in ['right','left']:
        longoff = radtodeg(longang)/3.0
    else:
        raise Exception()
    if orientation == 'up':
        A = (lathigh-latoff,longy)
        B = (laty-latoff,longhigh)
        C = (laty-latoff,longlow)
    if orientation == 'down':
        A = (latlow+latoff,longy)
        B = (laty+latoff,longhigh)
        C = (laty+latoff,longlow)
    if orientation == 'right':
        A = (laty,longhigh-longoff)
        B = (latlow,longy-longoff)
        C = (lathigh,longy-longoff)
    if orientation == 'left':
        A = (laty,longlow+longoff)
        B = (latlow,longy+longoff)
        C = (lathigh,longy+longoff)
    poly = []
    Adist = distance((laty,longy),A)
    Bdist = distance((laty,longy),B)
    Cdist = distance((laty,longy),C)
    Abear = initbearing((laty,longy),A) 
    Bbear = initbearing((laty,longy),B)
    Cbear = initbearing((laty,longy),C)
    newA = rotate((laty,longy),Adist,Abear+bear,latlong = True,bearrad = True)
    newB = rotate((laty,longy),Bdist,Bbear+bear,latlong = True,bearrad = True)
    newC = rotate((laty,longy),Cdist,Cbear+bear,latlong = True,bearrad = True)
    poly.append(newA)
    poly.append(newB)
    poly.append(newC)
    poly.append(newA)
    return poly


def initbearing(fromloc,toloc,latlong=True):
    '''
    in radians. 
    '''
    lati,longi = getlatlong(latlong)
    fromlat = fromloc[lati]
    fromlong = fromloc[longi]
    tolat = toloc[lati]
    tolong = toloc[longi]
    tempone = sin(degtorad(tolong - fromlong))*cos(degtorad(tolat))
    temptwo = cos(degtorad(fromlat))*sin(degtorad(tolat))
    tempthree = sin(degtorad(fromlat))*cos(degtorad(tolat))*cos(degtorad(tolong - fromlong))
    return (atan2(tempone,temptwo - tempthree))%(2*PI)

def diamond(cords,width,latlong = True):
    '''
    cords = (lat,long)
    '''
    lati,longi = getlatlong(latlong)
    laty = cords[lati]
    longy = cords[longi]
    latang = width/float(2.0*RADIUSOFEARTH)
    latlow = laty - radtodeg(latang)
    lathigh = laty + radtodeg(latang)
    longang = math.asin(math.sin(latang)/math.cos(degtorad(laty)))
    longlow = longy - radtodeg(longang)
    longhigh = longy + radtodeg(longang)
    poly = []
    poly.append((lathigh,longy))
    poly.append((laty,longhigh))
    poly.append((latlow,longy))
    poly.append((laty,longlow))
    poly.append((lathigh,longy))
    return poly



def square(cords,width,latlong = True,bearing = 0.0,bearrad = True):
    return rectangle(cords,width,width,latlong,bearing,bearrad)

def rectangle(cords,width,height,latlong = True,bearing = 0.0,bearrad = True):
    '''
    cords = (lat,long)
    '''
    if not bearrad:
        bear = degtorad(bearing)
    else:
        bear = bearing
    lati,longi = getlatlong(latlong)
    laty = cords[lati]
    longy = cords[longi]
    latang = height/float(2*RADIUSOFEARTH)
    latlow = laty - radtodeg(latang)
    lathigh = laty + radtodeg(latang)
    longang_unjust = width/float(2*RADIUSOFEARTH)
    longang = math.asin(math.sin(longang_unjust)/math.cos(degtorad(laty)))
    longlow = longy - radtodeg(longang)
    longhigh = longy + radtodeg(longang)
    poly = []
    A = (lathigh,longhigh)
    B = (latlow,longhigh)
    C = (latlow,longlow)
    D = (lathigh,longlow)
    Adist = distance((laty,longy),A)
    Bdist = distance((laty,longy),B)
    Cdist = distance((laty,longy),C)
    Ddist = distance((laty,longy),D)
    Abear = initbearing((laty,longy),A) 
    Bbear = initbearing((laty,longy),B)
    Cbear = initbearing((laty,longy),C)
    Dbear = initbearing((laty,longy),D)
    newA = rotate((laty,longy),Adist,Abear+bear,latlong = True,bearrad = True)
    newB = rotate((laty,longy),Bdist,Bbear+bear,latlong = True,bearrad = True)
    newC = rotate((laty,longy),Cdist,Cbear+bear,latlong = True,bearrad = True)
    newD = rotate((laty,longy),Ddist,Dbear+bear,latlong = True,bearrad = True)
    poly = []
    poly.append(newA)
    poly.append(newB)
    poly.append(newC)
    poly.append(newD)
    poly.append(newA)
    return poly

def circle(cords,radius, n = 50,latlong = True):
    poly = []
    for i in range(0,n):
        bear = 2*PI*i/float(n)
        poly.append(rotate(cords,radius,bear,latlong))
    poly.append(poly[0])
    return poly

def rotate(cords,radius,bearing,latlong = True,bearrad = True):
    if not bearrad:
        bear = degtorad(bearing)
    else:
        bear = bearing
    lati,longi = getlatlong(latlong)
    laty = cords[lati]
    longy = cords[longi]
    lattempone = math.sin(degtorad(laty))*math.cos(radius/float(RADIUSOFEARTH))
    lattemptwo = math.cos(degtorad(laty))*math.sin(radius/float(RADIUSOFEARTH))*math.cos(bear)
    newlat = radtodeg(math.asin(lattempone+lattemptwo))
    longtempone = math.sin(bear)*math.sin(radius/float(RADIUSOFEARTH))*math.cos(degtorad(laty))
    longtemptwo = math.cos(radius/float(RADIUSOFEARTH))-math.sin(degtorad(laty))*math.sin(degtorad(newlat))        
    newlong = longy+radtodeg(math.atan2(longtempone,longtemptwo))
    return (newlat,newlong)
    



def kmlname(kml,name):
    kml.write('<name>')
    kml.write(kmlclean(name))
    kml.write('</name>\n')

def kmlopen(kml,op):
    kml.write('<open>')
    if op in [1,'1',True,'true','TRUE','True']:
        kml.write('1')
    else:
        kml.write('0')
    kml.write('</open>\n')

def kmlcolor(kml,color,alpha):
    kml.write('<color>')
    kml.write(hextocolor(color,alpha))
    kml.write('</color>\n')                

def kmlwidth(kml,width):
    kml.write('<width>')
    kml.write(makestr(width))
    kml.write('</width>')
    


def recursive_zip(zipf, directory, folder = ""):
   for item in os.listdir(directory):
      if os.path.isfile(directory + os.sep + item):
         zipf.write(directory + os.sep + item, folder + os.sep + item)
      elif os.path.isdir(directory + os.sep + item):
         recursive_zip(zipf, directory + os.sep + item, folder + os.sep + item)
         
def createkmz(fname):
    zipf = zipfile.ZipFile(fname+'.kmz','w',compression = zipfile.ZIP_DEFLATED)
    recursive_zip(zipf,fname)
    zipf.close()

def kmlvisibility(kml,visi):
    kml.write('<visibility>')
    if visi in [1,'1',True,'true','TRUE','True']:
        kml.write('1')
    else:
        kml.write('0')
    kml.write('</visibility>\n')



def placemark(kml,cords,name,descr = None,color = WHITE,scale = 1,ficon = None,style = None,latlong = True):
    lati,longi = getlatlong(latlong)
    laty = cords[lati]
    longy = cords[longi]
    kml.write('<Placemark>\n')
    kmlname(kml,name)
    if descr != None:
        kml.write('<description>\n')
        kml.write(kmlclean(descr))
        kml.write('</description>\n')

    kml.write('<Style>\n')
    if ficon != None:
        kml.write('<IconStyle><Icon>\n')
        kml.write(ficon)
        kml.write('</Icon></IconStyle>\n')
    changecolorsize(kml,color,scale)
    kml.write('</Style>\n')
    if style != None:
        kml.write('<styleUrl>#'+style+'</styleUrl>\n')
    kml.write('<Point>\n')
    kml.write('<coordinates>')
    kml.write(' '+str(longy)+','+str(laty))
    kml.write('</coordinates>')
    kml.write('</Point>\n')
    kml.write('</Placemark>\n')




def beginfolder(kml,name,op = 0,visi=1):
    kml.write('<Folder>\n')
    kmlname(kml,name)
    kmlvisibility(kml,visi)
    kmlopen(kml,op)



def endfolder(kml):
    kml.write('</Folder>\n')

def writefunc(name):
    f = open(name,'w')
    return f.write,f.close

class kmlobj():
    def __init__(self,fname,zippy,name):
        self.zip = zippy
        self.name = name
        w,c = writefunc(fname)
        self.write = w
        self.close = c



def initialise(rawfname,op = 0):
    zippy = False
    name = ''
    if rawfname.endswith('.kmz'):
        name = rawfname.replace('.kmz','')
        createfolder(name)
        fname = name + '/doc.kml'
        zippy = True
    elif rawfname.endswith('.kml'):
        fname = rawfname
    else:
        fname = rawfname + '.kml'
    kml = kmlobj(fname,zippy,name)
    kml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml.write('<kml xmlns="http://www.opengis.net/kml/2.2" \nxmlns:gx="http://www.google.com/kml/ext/2.2">\n')
    kml.write('<Document>\n')
    kmlopen(kml,op)
    return kml

def end(kml):
    kml.write('</Document>\n')
    kml.write('</kml>')
    kml.close()
    if not kml.zip:
        return
    createkmz(kml.name)

def screenoverlay(kml,fname,x,y,color = WHITE,alpha = 0.75,xs = None,ys = None,name='',visi = 1):
    kml.write('<ScreenOverlay>\n')
    kmlname(kml,name)
    kmlvisibility(kml,visi)
    kmlcolor(kml,color,alpha)
    kml.write('<Icon>\n')
    kml.write(fname)
    kml.write('</Icon>\n')
    kml.write('<overlayXY x="')
    kml.write(str(x))
    kml.write('" y="')
    kml.write(str(y))
    kml.write('" xunits="fraction" yunits="fraction"/>\n')
    kml.write('<screenXY x="')
    kml.write(str(x))
    kml.write('" y="')
    kml.write(str(y))
    kml.write('" xunits="fraction" yunits="fraction"/>\n')
    if xs!=None and ys!=None:
        kml.write('<size x="')
        kml.write(str(xs))
        kml.write('" y="')
        kml.write(str(ys))
        kml.write('" xunits="fraction" yunits="fraction"/>\n')
            
    kml.write('</ScreenOverlay>\n')
    

    
def getlatlong(latlong):
    longi = 0
    lati = 1
    if latlong:
        longi = 1
        lati = 0
    return lati,longi



def writepoly(kml,poly,outerorinner,relative,elevation,latlong):
    if elevation!=None:
        kml.write('<extrude>1</extrude>')
        kml.write('<altitudeMode>'+relative+'</altitudeMode>')
        heightstr = ','+str(elevation)
    else:
        heightstr = ''
    lati,longi = getlatlong(latlong)
    kml.write('<'+outerorinner+'BoundaryIs>\n')
    kml.write('<LinearRing>\n')
    kml.write('<coordinates>\n')   
    kml.write(str(poly[0][longi])+','+str(poly[0][lati])+heightstr)
    for i in range(1,len(poly)):
        kml.write('\n')
        kml.write(str(poly[i][longi])+','+str(poly[i][lati])+heightstr)
    kml.write('\n</coordinates>\n')
    kml.write('</LinearRing>\n')
    kml.write('</'+outerorinner+'BoundaryIs>\n')


def gettime(time):
    if type(time) == STRINGTYPE:
        return time
    if type(time) in DATETYPES:
        return str(time.year)+'-'+fixstr(time.month)+'-'+fixstr(time.day)
    raise Exception()

def fixstr(integer):
    if integer < 10:
        return '0'+str(integer)
    return str(integer)

    
def writetimespan(kml,timespan):
    kml.write('<TimeSpan>\n')
    kml.write('<begin>')
    kml.write(gettime(timespan[0]))
    kml.write('</begin>\n')
    kml.write('<end>')
    kml.write(gettime(timespan[1]))
    kml.write('</end>\n')
    kml.write('</TimeSpan>\n')
    
def changecolorsize(kml,namecolor,namescale,alpha=1):
    kml.write('<LabelStyle>\n')
    kml.write('<scale>'+str(namescale)+'</scale>\n')
    if namecolor!=None:
        kmlcolor(kml,namecolor,alpha)
    kml.write('</LabelStyle>\n')


    


def createpoly(kml,poly,inners = [],descr = None,namecolor = None,namescale = 1,color = WHITE,alpha = 1, edgecolor = BLACK,edgealpha = 1,width=1,pointcords = None,pointficon = None,pointstyle = None, name = '',elevation = None, latlong = True,visi = 1,relative = 'relativeToGround',timespan = None):
    if len(poly) == 0:
        raise Exception('impossible')
    lati,longi = getlatlong(latlong)
    kml.write('<Placemark>\n')
    kmlname(kml,name)
    kmlvisibility(kml,visi)
    if descr != None:
        kml.write('<description>\n')
        kml.write(kmlclean(descr))
        kml.write('</description>\n')
    if timespan != None:
        writetimespan(kml,timespan)
    kml.write('<Style>\n')
    kml.write('<PolyStyle>\n')
    kmlcolor(kml,color,alpha)
    kml.write('</PolyStyle>\n')
    kml.write('<LineStyle>\n')
    kmlcolor(kml,edgecolor,edgealpha)
    kmlwidth(kml,width)
    kml.write('</LineStyle>\n')
    if pointficon != None:
        kml.write('<IconStyle><Icon>\n')
        kml.write(pointficon)
        kml.write('</Icon></IconStyle>\n')
    changecolorsize(kml,namecolor,namescale)
    kml.write('</Style>\n')
    if pointstyle != None:
        kml.write('<styleUrl>#'+pointstyle+'</styleUrl>\n')
    if pointcords != None:
        kml.write('<MultiGeometry>\n')
        kml.write('<Point>\n')
        kml.write('<coordinates>')
        laty = pointcords[lati]
        longy = pointcords[longi]
        kml.write(' '+str(longy)+','+str(laty))
        kml.write('</coordinates>')
        kml.write('</Point>\n')
    kml.write('<Polygon>\n')
    writepoly(kml,poly,'outer',relative,elevation,latlong)
    for ip in inners:
        writepoly(kml,ip,'inner',relative,elevation,latlong)
    kml.write('</Polygon>\n')
    if pointcords != None:
        kml.write('</MultiGeometry>\n')
    kml.write('</Placemark>\n')


def createpath(kml,path,descr = None,width=2,color = BLACK,alpha = 1,name='',latlong=True,visi = 1):
    if len(path) == 0:
        raise Exception('impossible')
    kml.write('<Placemark>\n')
    kmlname(kml,name)
    kmlvisibility(kml,visi)
    if descr != None:
        kml.write('<description>\n')
        kml.write(kmlclean(descr))
        kml.write('</description>\n')
    kml.write('<Style>\n')
    kml.write('<LineStyle>\n')
    kmlcolor(kml,color,alpha)
    kmlwidth(kml,width)
    kml.write('</LineStyle>\n')
    changecolorsize(kml,namecolor,namescale)
    kml.write('</Style>\n')
    kml.write('<LineString>\n')
    kml.write('<coordinates>\n')
    lati,longi = getlatlong(latlong)
    for i in range(0,len(path)):
        kml.write(' ')
        kml.write(str(path[i][longi])+','+str(path[i][lati]))
    kml.write('</coordinates>\n')
    kml.write('</LineString>\n')
    kml.write('</Placemark>\n')






def makestr(string):
    if string == None:
        return ''
    return str(string)

def stylise(element,style):
    if type(style) != type('string'):
        raise Exception()
    string = makestr(element)
    if 'b' in style:
        string = '<b>'+string+'</b>'
    if 'i' in style:
        string = '<I>'+string+'</I>'
    tag = ''
    if 'r' in style:
        tag= ' align="right"'
    elif 'l' in style:
        tag= ' align="left"'
    elif 'c' in style:
        tag = ' align="center"'
    if 'h' in style:
        string = '<th'+tag+'>'+string+'</th>'
    else:
        string = '<td'+tag+'>'+string+'</td>'
    return string
        

def tablesub(element):
    if type(element) in [type((0,0)),type([0,0])]:
        if len(element) == 0:
            return '<td></td>'
        elif len(element) == 1:
            return '<td>'+makestr(element[0])+'</td>'
        else:
            return stylise(element[0],element[1])
    return '<td>'+makestr(element)+'</td>'


def table(tableinfo,align = None,width = None):
    tag = ''
    if width != None:
        tag+= ' width="'+str(width)+'"'
    if align != None:
        tag+= ' align="'+str(align)+'"'
    string = '<table'+tag+'>\n'
    for row in tableinfo:
        string += '<tr>'
        for element in row:
            string += tablesub(element)
        string+='</tr>\n'
    string+='</table>\n'
    return string

def latlongtoxyz(cord,latlong = True):
    lati,longi = getlatlong(latlong)
    lat = cord[lati]*PI/180.0
    lon = cord[longi]*PI/180.0
    x = RADIUSOFEARTH*math.cos(lat)*math.cos(lon)
    y = RADIUSOFEARTH*math.cos(lat)*math.sin(lon)
    z = RADIUSOFEARTH*math.sin(lat)
    return x,y,z


def xyztolatlong(x,y,z,latlong = True):
    lati,longi = getlatlong(latlong)
    r = float(math.sqrt(x*x+y*y+z*z))
    lat = PI/2.0 - math.acos(z/r)
    lon = math.atan2(y,x)
    cord = [None,None]
    cord[lati] = radtodeg(lat)
    cord[longi] = radtodeg(lon)
    return cord
    
    
def gallpetersplane_sub(lat,lng):
    x = RADIUSOFEARTH*degtorad(lng)/SQRTOFTWO
    y = RADIUSOFEARTH*SQRTOFTWO*math.sin(degtorad(lat))
    return x,y


def gallpetersplane(cords,latlong = True):
    lati,longi = getlatlong(latlong)
    points = []
    for cord in cords:
        x,y = gallpetersplane_sub(cord[lati],cord[longi])
        points.append((x,y))
    return points


def pointinpolygon_gp(cords,point,latlong = True):
    '''
    returns a float:
    0 = outside
    1 = inside
    0.5 = edge
    '''
    if point in cords:
        return 0.5
    poly = gallpetersplane(cords,latlong)
    pointtemp = gallpetersplane([point],latlong)
    return pointinpolygon_gallpeters(poly,pointtemp[0])


def pointinpolygon(cords,point,latlong = True,tolerance = TOLERANCE):
    old = cords[-1]
    if distance(point,old,latlong) <= tolerance:
        return 0.5
    count = 0
    for new in cords:
        if distance(point,new,latlong) <= tolerance:
            return 0.5
        val = rayintersect(point,new,old,latlong,tolerance)
        if val == 0.5:
            return 0.5
        count += val
        old = new
    return count %2


def rayintersect(point,new,old,latlong,tolerance):
    lati,longi = getlatlong(latlong)
    px = point[longi]
    py = point[lati]
    ax = new[longi]
    ay = new[lati]
    bx = old[longi]
    by = old[lati]
    if ay > by: 
        bx = new[longi]
        by = new[lati]
        ax = old[longi]
        ay = old[lati]
    if py == ay:
        py += tolerance*0.01
    if py == by:
        py += tolerance*0.01
    if py < ay or py > by:
        return 0
    if px > ax and px > bx:
        return 0
    if px < ax and px < bx:
        return 1
    if ax==bx:
        ## verticle line, and px is on it!! (and between a and b)
        return 0.5
    mred = (by-ay)/float(bx-ax)
    if px == ax:
        return 0.5
    mblue = (py-ay)/float(px-ax)
    diff = mblue - mred
    dist = distance((py,px),(ay,ax))
    if math.fabs(diff) <= float(tolerance)/math.sqrt((dist-tolerance)*(dist+tolerance)):
        return 0.5
    if mblue > mred:
        return 1
    return 0




def pointinpolygon_gallpeters(poly,point):
    xold = poly[-1][0]
    yold = poly[-1][1]
    count = 0
    w = point[0]
    z = point[-1]
    for p in poly:
        x = p[0]
        y = p[1]
        if x == w and y == z:
            return 0.5
        count += pointinpolygon_gallpeters_sub(x,y,xold,yold,w,z)
        xold = x
        yold = y
    return count%2

def pointinpolygon_gallpeters_sub(x,y,xold,yold,w,z):
    if yold == y:
        if z == y and min(x,xold) <= w and w <= max(x,xold):
            return 0.5
        return 0
    t = float(z-yold)/float(y-yold)
    if t < 0 or t>1:
        return 0
    n = (xold-w) + t*(x-xold)
    if n>=0:
        if t not in [0,1]:
            return 1
        else:
            return 0.5
    return 0
    

def basicpolygonarea(cords,latlong = True):
    '''
    calculates area of a polygon by converting it to a plane using the gall - peters method
    I tend to trust this function more, but in theory polygonarea is correct
    Basically this function will have mapping issues, in that if two cordinates are
    far appart then the line between those cordinates looks different in the plane projection,
    so a bias is introduced.
    polygonarea should remove this bug by doing the calculation on a sphere directly...
    however this approach requires the notion of clockwise into the mix... and I'm not convinced
    that that function works correct (particularly for very small areas)
    '''
    points = gallpetersplane(cords,latlong)
    area = 0
    xold = points[-1][0]
    yold = points[-1][1]
    for point in points:
        x = point[0]
        y = point[1]
        area += (x-xold)*(y+yold)/2.0
        yold = y
        xold = x
    return math.fabs(area)


def boundingcircle(cords,latlong = True,scalefactor = 1.01,n=50):
    pt,rad = boundingcircle_info(cords,latlong=latlong,scalefactor=scalefactor)
    return circle(pt,rad,n=n,latlong=latlong)

def getmaxdist(cords,latlong,point):
    maxdist = 0
    for cord in cords:
        dist = distance(point,cord)
        if dist > maxdist:
            maxdist = dist
    return maxdist
    


def boundingcircle_info(cords,latlong = True,scalefactor = 1.01):
    centroid = basiccentroid(cords,latlong)
    maxdist = getmaxdist(cords,latlong,centroid)
    return centroid,maxdist*scalefactor



def basiccentroid(cords,latlong = True):
    xave = 0
    yave = 0
    zave = 0
    lenny = float(len(cords))    
    for cord in cords:
        x,y,z = latlongtoxyz(cord,latlong)
        xave += x/lenny
        yave += y/lenny
        zave += z/lenny
    centroid = xyztolatlong(xave,yave,zave)
    return centroid



def polygonarea(cords,latlong = True):
    centroid,detailed = centroidandarea(cords,latlong)
    basic = basicpolygonarea(cords,latlong) 
    area = (detailed+basic)/2.0
    if (detailed - basic) > 0.02*area:
        print('Warning area mismatch: ',basic,detailed)
        return detailed
    return area

def centroid(cords,latlong = True):
    centroid,area = centroidandarea(cords,latlong)
    return centroid

def centroidandarea(cords,latlong = True):
    '''
    Calculates the centroid and area, by partitioning the N polygon into
    N-2 triangles, calculates the area of these individual triangles, and
    then averages the triangle centroids
    Note this function should be more accurate (less rounding errors than
    basicpolygonarea, and the centroid should remove vertice bias that is
    associated with basiccentroid, but wise to always double check, as this
    function is not exactly completely fool proof (I may have missed an edge
    case or two). 
    '''
    base = cords[0]
    weightedx = 0
    weightedy = 0
    weightedz = 0
    areas = 0
    tempcentroid = basiccentroid(cords,latlong)
    oldcord = cords[-1]
    arealist = []
    for cord in cords:
        triangle = (tempcentroid,oldcord,cord)
        centroid = basiccentroid(triangle)
        cx,cy,cz = latlongtoxyz(centroid,latlong)
        area = trianglearea(triangle,latlong,absolute = False)
        areas += area
        cw = clockwise(triangle)
        if cw == False:
            print(area)
        arealist.append((area,cw))
        weightedx += cx*area
        weightedy += cy*area
        weightedz += cz*area
        oldcord = cord
    areas = float(areas)
    arealist = sorted(arealist,key = lambda a:a[0])
    
    #print(arealist[0],arealist[-1])
    if areas == 0:
        return basiccentroid(cords,latlong),areas
    x = weightedx/areas
    y = weightedy/areas
    z = weightedz/areas
    centroid = xyztolatlong(x,y,z,latlong)
    areas = math.fabs(areas)
    #print(centroid)
    return centroid,areas
        


def clockwise(cords,latlong = True):
    points = gallpetersplane(cords,latlong)
    # note gallpeters preserves clockwise-ness
    summer = 0
    for i in range(1,len(cords)):
        x2 = points[i][0]
        x1 = points[i-1][0]
        y2 = points[i][1]
        y1 = points[i-1][1]
        summer += (x2-x1)*(y2+y1)/2.0
    x2 = points[0][0]
    x1 = points[-1][0]
    y2 = points[0][1]
    y1 = points[-1][1]
    summer += (x2-x1)*(y2+y1)/2.0
    if summer>0:
        return True
    return False

def trianglearea(triangle,latlong = True,absolute = True):
    A = triangle[0]
    B = triangle[1]
    C = triangle[2]
    if A == B or B == C or C == A:
        return 0.0
    Aangle = getinternalangle(B,A,C,latlong)
    Bangle = getinternalangle(A,B,C,latlong)
    Cangle = getinternalangle(A,C,B,latlong)
    internalangles = Aangle+Bangle+Cangle
    Area = RADIUSOFEARTH*RADIUSOFEARTH*(internalangles - PI)
    if not absolute:
        direction = clockwise(triangle,latlong)
        if not direction:
            Area = -Area
    return Area
    

def getinternalangle(frm,at,to,latlong = True):
    '''
    Returns the lesser internal angle
    if absolute = False, it return + if angle made is clockwise, and negative if anticlockwise
    '''
    endangle = initbearing(at,to,latlong)
    initangle = initbearing(at,frm,latlong)
    internalangle = (endangle - initangle)
    if internalangle > PI:
        internalangle = 2*PI - internalangle
    if internalangle < - PI:
        internalangle = 2*PI + internalangle
    internalangle = math.fabs(internalangle)
    return internalangle   


def getintersect(cords1,cords2,latlong = True,tolerance= TOLERANCE,fast = True):
    intersect,info = intersectpoly(cords1,cords2,latlong=latlong,tolerance= tolerance,fast = fast)
    if NOINTERSECT in info:
        return NOINTERSECT
    return intersect
    
def getunion(cords1,cords2,latlong = True,tolerance= TOLERANCE,fast = True):
    union,info = unionpoly(cords1,cords2,latlong=latlong,tolerance= tolerance,fast = fast)
    if NOUNION in info:
        return NOUNION
    return union


def midpoint(point1,point2,latlong = True):
    x1,y1,z1 = latlongtoxyz(point1,latlong)
    x2,y2,z2 = latlongtoxyz(point2,latlong)
    xa = (x1+x2)/2.0
    ya = (y1+y2)/2.0
    za = (z1+z2)/2.0
    return xyztolatlong(xa,ya,za,latlong)


















def adjustfortolerance(raw1,raw2,tolerance,latlong):
    p1 = []
    p2 = []
    gp1 = gallpetersplane(raw1,latlong)
    gp2 = gallpetersplane(raw2,latlong)
    p1len = len(raw1)
    p2len = len(raw2)
    lookup = {1: 'inside',
              0: 'outside',
              0.5 : 'boundary'}
    for elem in raw2:
        p2.append(elem)
    for p in raw1:
        new = p
        b = False
        for q in p2:
            d = distance(p,q,latlong)
            if d < tolerance:
                new = q
                b = True
        p1.append(new)
        if b:
            i1.append('boundary')
        else:
            val = pointinpolygon_gallpeters(gp2,cord)    
    return p1,p2


def getrawinfos(polys,latlong = True):
    poly1 = gallpetersplane(polys[0],latlong)
    poly2 = gallpetersplane(polys[1],latlong)
    lookup = {1: 'inside',
              0: 'outside',
              0.5 : 'boundary'}
    info1 = []
    info2 = []
    for cord in poly1:
        val = pointinpolygon_gallpeters(poly2,cord)
        info1.append(lookup[val])
    for cord in poly2:
        val = pointinpolygon_gallpeters(poly1,cord)
        info2.append(lookup[val])    
    return info1,info2



                

    





    
def getnearbytopoly(point,cords,latlong,tolerance):
    nearby = []
    locs = []
    i = 0
    for opt in cords:
        d = distance(point,opt,latlong)
        if d < tolerance:
            nearby.append(opt)
            locs.append(i)
        i+=1
    return nearby,locs

class statusclass():
    def __init__(self,cord,state):
        self.cord = cord
        self.state = state
        self.visited = False





def getstatusofpolys(cords1,cords2,latlong,tolerance):
    poly1 = gallpetersplane(cords1,latlong)
    poly2 = gallpetersplane(cords2,latlong)
    i = 0
    status1 = []
    adjust = {}
    for point in cords1:
        nearby,locs = getnearbytopoly(point,cords2,latlong,tolerance)    
        if nearby == []:
            val = pointinpolygon_gallpeters(poly2,poly1[i])
            pt = tuple(point)
            if val == 0.5:
                pt = (point[0]+0.000001,point[1]+0.000001)
                gp_pt = gallpetersplane([pt],latlong)
                val = pointinpolygon_gallpeters(poly2,gp_pt[0])
            status1.append(statusclass(pt,val))
        else:
            newpoint = tuple(basiccentroid(nearby))
            status1.append(statusclass(newpoint,0.5))
            for j in locs:
                adjust[j] = newpoint
        i+=1
    i = 0
    c = datetime.datetime.now()
    status2 = []
    oldpoint = cords2[-1]
    for point in cords2:
        if adjust.has_key(i):
            status2.append(statusclass(adjust[i],0.5))
            i+=1
            continue
        val = pointinpolygon_gallpeters(poly1,poly2[i])
        status2.append(statusclass(tuple(point),val))
        i+=1
    status1 = removeduplicates(status1)
    status2 = removeduplicates(status2)
    return status1,status2









def removeduplicates(status):
    corddict = getcorddict(status)
    newstatus = []
    for stat in status:
        if corddict[stat.cord] == 1:
            newstatus.append(stat)
        else:
            corddict[stat.cord] = corddict[stat.cord] -1
    return newstatus


def getcorddict(status):
    cords = {}
    for stat in status:
        if not cords.has_key(stat.cord):
            cords[stat.cord] = 0
        cords[stat.cord] += 1
    return cords


def needtoaddboundarypoint(old,new):
    if old == new:
        return False
    if 0.5 in [old,new]:
        return False    
    return True


##### AMEND THIS FUNCTION SO THAT NEW BOUNDARY POINTS ARE NOT NEARBY OTHER POINTS.


def addintersections(data1,data2,latlong,tolerance,fast):
    newdata1 = []
    newdata2 = []
    for pt in data2:
        newdata2.append(pt)
    old1 = data1[-1]
    i = -1 
    for new1 in data1:
        i+=1
        if fast:
            if not needtoaddboundarypoint(old1.state,new1.state):  ### REMOVE THIS IF TO SLOW SCRIPT DOWN BUT TAKE CARE OF EDGE CASES.
                newdata1.append(new1)
                old1 = new1
                continue
        old2 = newdata2[-1]
        newpoly = []
        boundaries = []
        for new2 in newdata2:
            intersect = findintersect((old1.cord,new1.cord),(old2.cord,new2.cord),latlong = latlong)    
            if not checkvalid(intersect,(old1.cord,new1.cord),(old2.cord,new2.cord),latlong,tolerance = tolerance/3.0):
                newpoly.append(new2)
                old2 = new2
                continue
            boundaries.append(intersect)
            newpoly.append(statusclass(intersect,0.5))
            newpoly.append(new2)
            old2 = new2
        boundaries = sortbydistance(boundaries,old1.cord)
        for bound in boundaries:
            newdata1.append(statusclass(bound,0.5))  
        newdata1.append(new1)
        newdata2 = newpoly
        old1 = new1
    return newdata1,newdata2


##
##def addintersections(data1,data2,latlong,tolerance,fast):
##    newdata1 = []
##    newdata2 = []
##    for pt in data2:
##        newdata2.append(pt)
##    old1 = data1[-1]
##    for new1 in data1:
##        if fast:
##            if not needtoaddboundarypoint(old1.state,new1.state):  ### REMOVE THIS IF TO SLOW SCRIPT DOWN BUT TAKE CARE OF EDGE CASES.
##                newdata1.append(new1)
##                old1 = new1
##                continue
##        newdata1,newdata2 = updatenewdatas(data1,newdata1,data2,newdata2,old1,new1,latlong,tolerance)
##        old1 = new1
##    return newdata1,newdata2
##
##
##def updatenewdatas(data1,newdata1,data2,newdata2,old1,new1,latlong,tolerance):
##    old2 = newdata2[-1]
##    newpoly = []
##    boundaries = []
##    for new2 in newdata2:
##        intersect = findintersect((old1.cord,new1.cord),(old2.cord,new2.cord),latlong = latlong)    
##        if not checkvalid(intersect,(old1.cord,new1.cord),(old2.cord,new2.cord),latlong,tolerance/3.0):
##            newpoly.append(new2)
##            old2 = new2
##            continue        
##        boundaries.append(intersect)
##        newpoly.append(statusclass(intersect,0.5))
##        newpoly.append(new2)
##        old2 = new2
##    boundaries = sortbydistance(boundaries,old1.cord)
##    for bound in boundaries:
##        newdata1.append(statusclass(bound,0.5))  
##    newdata1.append(new1)
##    newdata2 = newpoly
##    return newdata1,newdata2 

    

def findintersect(lineone,linetwo,latlong = True):
    '''
    lineone,linetwo are of the form:
    (point1,point2)
    finds the intersection point.
    '''
    x11,y11,z11 = latlongtoxyz(lineone[0],latlong)
    x12,y12,z12 = latlongtoxyz(lineone[1],latlong)
    x21,y21,z21 = latlongtoxyz(linetwo[0],latlong)
    x22,y22,z22 = latlongtoxyz(linetwo[1],latlong)
    #convert the lines to a plane
    a1 = (y11*z12-y12*z11)
    b1 = -(x11*z12-x12*z11)
    c1 = (x11*y12-x12*y11)
    a2 = (y21*z22-y22*z21)
    b2 = -(x21*z22-x22*z21)
    c2 = (x21*y22-x22*y21)
    # need some temps
    divisor  = float(b2*a1-a2*b1)
    if a1 == 0 or  divisor == 0:
        return None
    temp1 = (a2*c1-c2*a1)/divisor
    temp2 = -(b1*temp1+c1)/float(a1)
    temp3 = RADIUSOFEARTH/math.sqrt(float(temp1*temp1+temp2*temp2+1))
    xx1 = temp2*temp3
    yy1 = temp1*temp3
    zz1 = temp3
    xx2 = -temp2*temp3
    yy2 = -temp1*temp3
    zz2 = -temp3
    option1 = xyztolatlong(xx1,yy1,zz1)
    option2 = xyztolatlong(xx2,yy2,zz2)
    d1 = distance(lineone[0],option1)+distance(lineone[1],option1)
    d2 = distance(lineone[0],option2)+distance(lineone[1],option2)
    if d1 < d2:
        return option1
    return option2

def sortbydistance(cords,point):
    pairs = []
    for cord in cords:
        d = distance(cord,point)
        pairs.append((cord,d))
    pairs = sorted(pairs,key = lambda a:a[1])
    scords = []
    for pair in pairs:
        scords.append(pair[0])
    return scords
    

def checkvalid(intersect,lineone,linetwo,latlong = True,tolerance = TOLERANCE):
    if intersect == None:
        print('doh and sigh')
        return False
    for line in [lineone,linetwo]:
        length = distance(line[0],line[1],latlong)
        part1 = distance(line[0],intersect,latlong)
        part2 = distance(line[1],intersect,latlong)
        if part1 + part2 > length + tolerance:
            return False
    return True



def checkstatus(data):
    old = data[-1].state
    status = {}
    for triple in data:
        new = triple.state
        status[new] = True
        if needtoaddboundarypoint(old,new):
            print(old,new)
            raise Exception()
        old = new
    return sorted(status.keys())




def istrivial(cords1,cords2,sol1,sol2):
    both = sorted(list(set(sol1+sol2)))
    if both == []:
        # no data provided
        return None,None,True,[NOINTERSECT,NOUNION]
    if both == [0]:
        # don't intersect
        return None,None,True,[NOINTERSECT,NOUNION]
    if both == [0.5]:
        # same polygon
        return cords1,cords2,True,[]
    #intersect,union
    if sol1 == [1] or sol1 == [0.5,1]:
        # cords1 is entirely in cords2:
        return cords1,cords2,True,[]
    if sol2 == [1] or sol2 == [0.5,1]:
        # cords2 is entirely in cords1:
        return cords2,cords1,True,[]
    if both == [0.5,0]:
        # polys don't intersect, but have a union.
        return None,None,True,[NOINTERSECT]
    return None,None,False,[]



def getgoodies(version):
    if version == UNION:
        return [0],[0]
    if version == INTERSECT:
        return [1],[1]

def getbaddies(version):
    if version == UNION:
        return [1],[1]
    if version == INTERSECT:
        return [0],[0]
    
def getdirection(data,i,good,bad = [0,0.5,1],printout = False):
    lenny = len(data)
    backward = data[addone(i,lenny,'backward')]
    forward = data[addone(i,lenny,'forward')]
    if backward.state in good and backward.visited == False:
        return 'backward'
    if forward.state in good and forward.visited == False:
        return 'forward'
    if backward.state not in bad and backward.visited == False:
        return 'backward'
    if forward.state not in bad and forward.visited == False:
        return 'forward'
    if printout:
        print('here',forward.state,forward.visited,backward.state,backward.visited)
    return None

def reversedirection(direction):
    if direction == None:
        return None
    if direction == 'backward':
        return 'forward'
    if direction == 'forward':
        return 'backward'
    raise Exception()

### FIX THIS SO THAT THE SECOND ONE CANNOT BE: None.


def getstarts(data1,data2,goodies,badies):
    i = 0
    start1 = None
    for pt in data1:
        status = pt.state
        if status == 0.5:
            dirs = getdirection(data1,i,goodies[0])
            if dirs != None:
                dir1 = dirs
                start1 = i
                break
        i+=1
    if start1 == None:
        return None,None,None,None,True
    j = 0
    cord1 = data1[start1].cord
    for triple in data2:
        cords = triple.cord
        if cords == cord1:
            dir2 = reversedirection(getdirection(data2,j,goodies[1],badies[1],True))
            return start1,j,dir1,dir2,False
        j+=1
    raise Exception()



def addone(i,lenny,direction):
    if direction == 'forward':
        return (i+1)%lenny
    if direction == 'backward':
        return (i-1)%lenny
    raise Exception()


def lookahead(data,curi,dirs,good,bad,lenny,stopcord):
    i = addone(curi,lenny,dirs)
    c = 0
    while True:
        cur = data[i]
        c+=1
        if cur.cord == stopcord:
            return True,c
        if cur.state in bad:
            return False,c
        if cur.state in good and cur.visited == False:
            return True,c
        i = addone(i,lenny,dirs)
        if i == curi:
            raise exception()
    



def pickbestoption(datas,curi,curp,dirs,goodies,badies,lennys,stopcord,latlong):
    simple,p,i = simplebestoption(datas,curi,curp,dirs,goodies,badies,lennys,stopcord,latlong)
    if simple:
        return p,i
    tricky,p,i = trickybestoption(datas,curi,curp,dirs,goodies,badies,lennys,stopcord,latlong)
    if tricky:
        return p,i
    raise Exception()


def simplebestoption(datas,curi,curp,dirs,goodies,badies,lennys,stopcord,latlong):
    otherp,otheri = getother(datas[curp][curi].cord,curp,datas)
    if dirs[otherp] == None:
        return True,curp,curi
    future_otheri = addone(otheri,lennys[otherp],dirs[otherp])
    future_curi = addone(curi,lennys[curp],dirs[curp])
    other = datas[otherp][future_otheri]
    stay = datas[curp][future_curi]
    if stay.state in goodies[curp] and stay.visited == False:
        # staying gets better --> stay
        return True,curp,curi
    if other.state in goodies[otherp] and other.visited == False:
        # changing goes to better --> change
        return True,otherp,otheri
    if stay.state in badies[curp]:
        ## staying is bad
        return True,otherp,otheri
    if other.state in badies[otherp]:
        # changing is bad
        return True,curp,curi
    if other.visited == False and stay.visited == True:
        return True,otherp,otheri
    if other.visited == True and stay.visited == False:
        return True,curp,curi
    return False,None,None


def trickybestoption(datas,curi,curp,dirs,goodies,badies,lennys,stopcord,latlong):
    otherp,otheri = getother(datas[curp][curi].cord,curp,datas)
    future_otheri = addone(otheri,lennys[otherp],dirs[otherp])
    future_curi = addone(curi,lennys[curp],dirs[curp])
    other = datas[otherp][future_otheri]
    stay = datas[curp][future_curi]
    cur = datas[curp][curi]
    if stay.state!= 0.5 or other.state!=0.5:
        raise Exception()
    if stay.cord == other.cord: 
        # meh, same point
        return True,curp,curi
    if stay.cord == stopcord:
        # reached the end
        return True,curp,curi
    if other.cord == stopcord:
        # reached the end
        return True,otherp,otheri
    if distance(stay.cord,other.cord) < tolerance:
        # meh, close enough
        return True,curp,curi
    stayahead,staylength = lookahead(datas[curp],curi,dirs[curp],goodies[curp],badies[curp],lennys[curp],stopcord)
    otherahead,otherlength = lookahead(datas[otherp],otheri,dirs[otherp],goodies[otherp],badies[otherp],lennys[otherp],stopcord)
    staydist = distance(cur.cord,stay.cord)
    otherdist = distance(cur.cord,other.cord)
    if stayahead == False and otherahead == False:
        #print('sigh',staylength,otherlength)
        #print('ok',staydist,otherdist)
        #print(cur.cord,stay.cord,other.cord)
        if staylength > otherlength:
            return True,curp,curi
        if otherlength > staylength:
            return True,otherp,otheri
        if staydist < otherdist:
            return True,curp,curi
        else:
            return True,otherp,otheri
    if stayahead == True and otherahead == False:
        return True,curp,curi
    if otherahead == True and stayahead == False:
        return True,otherp,otheri
    if staydist < otherdist:
        return True,curp,curi
    else:
        return True,otherp,otheri
    print(stay.state,other.state)
    print(datas[otherp][future_otheri].cord,datas[curp][future_curi].cord)
    raise Exception()
    
def getother(cord,curp,datas):
    otherp = (curp+1)%2
    i = 0
    for pt in datas[otherp]:
        if pt.cord == cord:
            return otherp,i
        i+=1   
    print(cord)
    raise Exception()


def combinepoly_sub(datas,starts,dirs,goodies,badies,latlong):
    poly = []
    stopcord = datas[0][starts[0]].cord
    poly.append(stopcord)
    lennys = [len(datas[0]),len(datas[1])]
    curi = starts[0]
    curp = 0
    oldcuri = curi
    oldcurp = curp
    n = 0
    while True:
        n+=1
        curi = addone(curi,lennys[curp],dirs[curp])
        #print('\t'+str(curi)+' '+str(curp)+' '+str(datas[curp][curi].state))
        pt = datas[curp][curi]
        if pt.cord == stopcord:
            break
        if pt.state in goodies[curp]:
            ## its good, keep getting it
            poly.append(pt.cord)
            pt.visited = True
            oldcuri = curi
            oldcurp = curp
            continue
        if pt.state != 0.5:
            print(pt.state)
            raise Exception()
        curp,curi = pickbestoption(datas,curi,curp,dirs,goodies,badies,lennys,stopcord,latlong)
        poly.append(datas[curp][curi].cord)
        datas[curp][curi].visited = True
        oldcuri = curi
        oldcurp = curp
    return poly,datas[0],datas[1]

def combinedpolygonsub(data1,data2,version,latlong):
    goodies = getgoodies(version)
    baddies = getbaddies(version)
    polys = []
    while True:
        start1,start2,dir1,dir2,stop = getstarts(data1,data2,goodies,baddies)
        #print(start1,start2,dir1,dir2)
        if stop:
            break
        poly,data1,data2 = combinepoly_sub([data1,data2],[start1,start2],[dir1,dir2],goodies,baddies,latlong)
        polys.append(poly)
    return polys







def unionpoly(cords1,cords2,latlong = True,tolerance = TOLERANCE,fast = True):
    data1,data2 = getstatusofpolys(cords1,cords2,latlong,tolerance)
    data1,data2 = addintersections(data1,data2,latlong,tolerance,fast)
    data2,data1 = addintersections(data2,data1,latlong,tolerance,fast)
    
    sol1 = checkstatus(data1)
    sol2 = checkstatus(data2)
    intersect,union,trivial,issues = istrivial(cords1,cords2,sol1,sol2)
    if trivial:
        return [union],issues
    if NOUNION in issues:
        return None,issues
    polys = combinedpolygonsub(data1,data2,UNION,latlong)        
    return polys,issues

def simplifypoly_sub(raw,tolerance,latlong = True):
    poly = []
    old = raw[-1]
    poly.append(old)
    for new in raw:
        if distance(new,old,latlong) > tolerance:
            poly.append(new)
            old = new
    return poly


def removesimilarpoints(rawcords1,rawcords2,tolerance,latlong):
    cords1 = simplifypoly(rawcords1,tolerance,latlong)
    cords2 = simplifypoly(rawcords2,tolerance,latlong)
    if len(cords1) < len(cords2):
        return cords1,cords2
    return cords2,cords1
### two bugs, not adding intersection points.
### start direction of the second poly

### need to think...
def refine(rawcords,tolerance,latlong = True):
    return rawcords
##    j = 0
##    for point in cords:
##        j += 1
##        if j %100 == 0:
##            print('.'),
##        nearby,locs = getnearbytopoly(point,cords,latlong,tolerance)
##        centroid = basiccentroid(nearby,latlong)
##        for i in locs:
##            cords[i] = centroid
##    return cords

def simplifypoly(raw,tolerance,latlong = True):
    clean = raw
    while True:
        cleaner = simplifypoly_sub(clean,tolerance,latlong)
        if len(cleaner) == len(clean):
            return refine(cleaner,tolerance,latlong)
        clean = cleaner


def getthreshold(rawpoly,realmax,latlong):
    distances = []
    old = rawpoly[-1]
    for new in rawpoly:
        dist = distance(new,old,latlong)
        distances.append(dist)
        old = new
    distances = sorted(distances,reverse = True)
    threshold = distances[realmax]
    return threshold

def condenseto(rawpoly,maxnumber,latlong = True):
    realmax = maxnumber
    if type(maxnumber) == type('1'):
        realmax = float(maxnumber)
    if len(rawpoly) <= maxnumber:
        return rawpoly
    lenny = len(rawpoly)
    oldlenny = lenny
    failed = False
    poly = copy.deepcopy(rawpoly)
    threshold = getthreshold(poly,realmax,latlong)
    while lenny > maxnumber:
        poly = simplifypoly(rawpoly,threshold,latlong)
        lenny = len(poly)
        if lenny <= maxnumber:
            return poly
        if lenny == oldlenny or threshold == 0.0:
            if failed == True:
                return poly
            threshold = getthreshold(poly,int(realmax*(1-CONDENSEREDUCTION)),latlong)
            failed = True
        else:
            threshold = getthreshold(poly,realmax,latlong)
        oldlenny = lenny
    return poly
    




def intersectpoly(rawcords1,rawcords2,latlong = True,tolerance = TOLERANCE,fast = False):
    ## this removes points that are really close in the individual polys.
    ## needed as two points really close together will divide and cause instabilities (large rounding errors)
    cords1,cords2 = removesimilarpoints(rawcords1,rawcords2,tolerance,latlong)
    ## here we are assigning the point in poly in to the points --> bulk of work!
    data1,data2 = getstatusofpolys(cords1,cords2,latlong,tolerance)
    ## here we are adding boundary points.
    data1,data2 = addintersections(data1,data2,latlong,tolerance,fast)
    if fast:
        data2,data1 = addintersections(data2,data1,latlong,tolerance,fast)      
    sol1 = checkstatus(data1)
    sol2 = checkstatus(data2)
    intersect,union,trivial,issues = istrivial(cords1,cords2,sol1,sol2)
    if trivial:
        return [intersect],issues
    if NOINTERSECT in issues:
        return None,issues
    if 1 in sol1:
        polys = combinedpolygonsub(data1,data2,INTERSECT,latlong)        
    elif 1 in sol2:
        polys = combinedpolygonsub(data2,data1,INTERSECT,latlong)
    else:
        raise Exception()
    return polys,issues


    
def getfurtherestpointfrom(centroid,polygons,latlong= True):
    maxdist = 0
    for poly in polygons:
        for point in poly:
            dist = distance(centroid,point,latlong)
            if dist > maxdist:
                maxdist = dist
    return maxdist


def infillpolygons(polygons,numpoints = 50,tolerance = TOLERANCE,latlong = True):
    centroid = getcentroidofpolygons(polygons,latlong)
    radius = getfurtherestpointfrom(centroid,polygons,latlong)
    circ = circle(centroid,radius, n = numpoints,latlong = True)
    poly = []
    for point in circ:
        intersect = infillpolygons_sub(centroid,point,polygons,tolerance,latlong)
        if intersect != None:
            poly.append(intersect)
    return poly




def infillpolygons_sub(centroid,point,polygons,tolerance,latlong = True):
    intersects = []
    line = (centroid,point)
    for poly in polygons:
        intersects += infillpolygons_sub_sub(line,poly,tolerance,latlong)
    maxdist = 0
    maxinter = None
    for inter in intersects:
        dist = distance(centroid,inter,latlong)
        if dist > maxdist:
            maxdist = dist
            maxinter = inter
    return maxinter


def infillpolygons_sub_sub(line,poly,tolerance,latlong = True):
    oldpoint = poly[-1]
    intersections = []
    for point in poly:
        intersect = findintersect(line,(oldpoint,point),latlong)    
        if intersect == None:
            continue
        if checkvalid(intersect,line,(oldpoint,point),latlong,tolerance = tolerance):
            intersections.append(intersect)
        oldpoint = point
    return intersections
    
            
    


def getcentroidofpolygons(polygons,latlong = True):
    centroids = [0,0]
    totarea = 0
    for poly in polygons:
        centroid,area = centroidandarea(poly,latlong)
        totarea += area
        for i in range(0,2):
            centroids[i] += centroid[i]*area
    for i in range(0,2):
        centroids[i] = centroids[i]/float(totarea)
    return centroids






def makemaker(kml,name,fname,hname = None,scale = 1,xspot = 0.5,yspot = 0.5, xunit = 'fraction',yunit = 'fraction'):
    kml.write('<StyleMap id="'+name+'">\n')
    kml.write('<Pair><key>normal</key><styleUrl>#sn_'+name+'</styleUrl></Pair>\n')
    kml.write('<Pair><key>highlight</key><styleUrl>#sh_'+name+'</styleUrl></Pair>\n')
    kml.write('</StyleMap>\n')
    highname = fname
    if hname != None:
        highname = hname
    kml.write('<Style id="sh_'+name+'"><IconStyle>\n')
    kml.write('<scale>'+str(scale)+'</scale>\n')
    kml.write('<Icon><href>'+highname+'</href></Icon>\n')
    kml.write('<hotSpot x="'+str(xspot)+'" y="'+str(yspot)+'" xunits="'+xunit+'" yunits="'+yunit+'"/>\n')    
    kml.write('</IconStyle></Style>\n')
    kml.write('<Style id="sn_'+name+'"><IconStyle>\n')
    kml.write('<scale>'+str(scale)+'</scale>\n')
    kml.write('<Icon><href>'+fname+'</href></Icon>\n')
    kml.write('<hotSpot x="'+str(xspot)+'" y="'+str(yspot)+'" xunits="'+xunit+'" yunits="'+yunit+'"/>\n')    
    kml.write('</IconStyle></Style>\n')



    
def kmlclean(string):
    if string == None:
        return 'NA'
    newstring = ''
    for i in range(0,len(string)):
        c = string[i]
        if not BADDIES.has_key(c):
            newstring+=c
            continue
        if c not in BADDIES[c]:
            newstring+=BADDIES[c]
            continue
        j = BADDIES[c].index(c)
        if string[i-j:i-j+len(BADDIES[c])] == BADDIES[c]:
            newstring+=c
            continue
        newstring += BADDIES[c]
    return newstring
                  








          



#kml = initialise('test.kml')
#circ1 = circle((50,50),10)
#circ2 = circle((50.1,50.1),10)
#beginfolder(kml,'twocircles')
#createpoly(kml,circ1,descr = 'one')
#createpoly(kml,circ2,descr = 'two')
#endfolder(kml)
#union,intersect = combinepolygons(circ1,circ2)
#beginfolder(kml,'union')
#createpoly(kml,union,descr = 'union')
#endfolder(kml)
#beginfolder(kml,'intersect')
#createpoly(kml,intersect,descr = 'intersect')
#endfolder(kml)
#end(kml)




