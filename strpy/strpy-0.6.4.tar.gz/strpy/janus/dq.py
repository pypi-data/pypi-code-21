import numpy as np
from bobo.image import ImageDetection
from bobo.video import VideoDetection
from scipy.fftpack import *
from numpy.fft import *
import cv2
import os.path

ytf = None
sc = None
vids = None
def _DBG_sample_vids(n=5, datadir='/proj/janus/data/', force_reload=False):
    from viset.youtubefaces import YouTubeFaces
    import bobo.app
    global ytf
    global sc
    global vids
    if sc is None or force_reload:
        sc = bobo.app.init("janus_detection_quality")
    if ytf is None or force_reload:
        ytf = YouTubeFaces(datadir=datadir)
    if vids is None or force_reload:
        vids = ytf.rdd(sparkContext=sc, max_num_subjects=n).collect()
    return vids

def _vid_pp(vid, dilate=1.5):
    return vid.clone().map(lambda frame: frame.boundingbox(dilate=dilate).crop().resize(cols=300))

def _DBG_sample_vids_pp(n=5, datadir='/proj/janus/data/', force_reload=False):
    return map(_vid_pp, _DBG_sample_vids(n,datadir,force_reload))

def _vid_dir(vid): return os.path.dirname(vid[0].filename())

def apply_fft(im,reflect=False):
    im = im.clone()
    data = im.grayscale().data
    if reflect:
        data = np.concatenate((data,data[::-1,:]),0)
        data = np.concatenate((data,data[:,::-1]),1)
    im.data = fft2(data)
    im.setattribute('colorspace', 'fourier')
    return im

def _d3_impl(a):
    m,n = a.shape
    return a.reshape((m,n,1))
def _d3(*A): return [_d3_impl(a) for a in A]

def ft_variance(im):
    f0,f1 = map(fftfreq,im.data.shape)
    f0 = np.reshape(f0,(-1,1))
    f1 = np.reshape(f1,(1,-1))
    x = np.hypot(f0,f1)
    p = np.abs(im.data)**2
    p[0,0] = 0 # ignore DC component of FT
    ps = np.sum(p) - p[0,0]
    average = np.average(x,weights=p)
    variance = np.average((x-average)**2, weights=p)
    return variance
    mu = np.sum(p*x)/ps
    nu = np.sum(p*x*x)/ps
    return nu-mu*mu,variance

def im_variance(im,reflect=True): return ft_variance(apply_fft(im,reflect))
def im_px_per_cycle(im,reflect=True): return ft_variance(apply_fft(im,reflect))**-0.5
def vid_px_per_cycle(vid,reflect=True): return [im_px_per_cycle(frame,reflect) for frame in vid]
class PxStats(object):
    def __init__(self, px_per_cycles, vid=None):
        self.px_per_cycles = px_per_cycles
        self.vid = vid

        self.mean = np.average(px_per_cycles)
        self.std = np.std(px_per_cycles)
        self.minidx = np.argmin(px_per_cycles)
        self.maxidx = np.argmax(px_per_cycles)

        self.viddir = _vid_dir(vid) if vid is not None else None

    def __str__(self):
        return "<PxStats:%s mean=%.2f, std=%.2f, minidx=%i, maxidx=%i>"%(
                str(self.viddir), self.mean, self.std, self.minidx, self.maxidx)

    def show(self, vid=None, figure=None):
        import matplotlib.pyplot as plt
        vid = self.vid if vid is None else vid
        if vid is None: raise Exception("Both self.vid and vid argument are None")

        if figure is not None:
            figure = plt.figure(figure)
            figure.clf()
        else:
            figure = plt.figure()
        #plt.subplot(131)
        vid[self.minidx].show(figure=figure)
        #plt.subplot(132)
        #vid[self.maxidx].show(figure=figure)
        #plt.subplot(133)
        #plt.plot(self.px_per_cycles, figure=figure)
        return figure

def fourierim(im, norm_power=2, abs_power=2, q=99.0):
    im = im.clone()
    F = fftshift(im.data)
    h = np.mod(np.angle(F, deg=True) + 360,360)
    s = np.ones(F.shape)
    v = np.abs(F)
    #normalizer = np.max(v[1:])
    normalizer = np.percentile(v,q)
    v = np.minimum(v**abs_power / normalizer**norm_power, 1)
    h = (h*0.5).astype(np.uint8)
    v = (v*255).astype(np.uint8)
    s = (s*255).astype(np.uint8)
    #im.setattribute('colorspace','gray')
    #return im.bgr()
    hsv = np.concatenate(_d3(h,s,v),axis=2)
    im.data = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    im.setattribute('colorspace', 'bgr')
    return im

