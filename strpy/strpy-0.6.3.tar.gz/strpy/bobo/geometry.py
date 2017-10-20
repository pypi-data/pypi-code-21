import numpy as np
import cv2
import math
import numpy.linalg
import scipy.spatial

def covariance_to_ellipse(cov):
    """2x2 covariance matrix to rotated bounding box"""
    (d,V) = numpy.linalg.eig(cov)
    return (d[0], d[1], math.atan2(V[1,0],V[0,0]))  # (major_axis_len, minor_axis_len, angle_in_radians)

def dehomogenize(p):
    return np.float32(p[0:-1, :]) / np.float32(p[-1,:])

def homogenize(p):
    return np.float32(np.vstack( (p, np.ones((1,p.shape[1]))) ))

def apply_homography(H,p):
    return dehomogenize(H*homogenize(p))

def similarity_imtransform2D(c=(0,0), r=0, s=1):
    # cv2 rotation is in degrees
    deg = r * 180. / math.pi
    A = cv2.getRotationMatrix2D(c, deg, s)
    return A

def similarity_imtransform(txy=(0,0), r=0, s=1):
    R = np.mat([[np.cos(r), -np.sin(r), 0], [np.sin(r), np.cos(r), 0], [0,0,1]])
    S = np.mat([[s,0,0], [0, s, 0], [0,0,1]])
    T = np.mat([[0,0,txy[0]], [0,0,txy[1]], [0,0,0]])
    return S*R + T  # composition


def affine_imtransform(txy=(0,0), r=0, sx=1, sy=1, kx=0, ky=0):
    R = np.mat([[np.cos(r), -np.sin(r), 0], [np.sin(r), np.cos(r), 0], [0,0,1]])
    S = np.mat([[sx,0,0], [0, sy, 0], [0,0,1]])
    K = np.mat([[1,ky,0], [kx,1,0], [0,0,1]])
    T = np.mat([[0,0,txy[0]], [0,0,txy[1]], [0,0,0]])
    return K*S*R + T  # composition

def random_affine_imtransform(txy=((0,0),(0,0)), r=(0,0), sx=(1,1), sy=(1,1), kx=(0,0), ky=(0,0)):
    return affine_imtransform(txy=(uniform_random_in_range(txy[0]), uniform_random_in_range(txy[1])),
                              r=uniform_random_in_range(r),
                              sx=uniform_random_in_range(sx),
                              sy=uniform_random_in_range(sy),
                              kx=uniform_random_in_range(kx),
                              ky=uniform_random_in_range(ky))

def imtransform2D(im, A):
    return cv2.warpAffine(im, A, (im.shape[1], im.shape[0]))

def imtransform(im, A):
    # cv2.warpPerspective(src, M, dsize[, dst[, flags[, borderMode[, borderValue]]]]) -> dst
    return cv2.warpPerspective(im, A, (im.shape[1], im.shape[0]))

def frame_to_bbox(fr):
    """ bbox = [ (xmin,ymin,width,height), ... ] """
    return [ (x[0]-x[2]/2, x[1]-x[2]/2, x[0]+x[2]/2, x[1]+x[2]/2) for x in fr]

def sub2ind(i, j, rows):
    return (i*rows + j)

def sqdist(d_obs, d_ref):
    """Given d_obs of size (MxD) ad d_ref of size (NxD) return (MxN) matrix of pairwise euclidean distances"""
    return scipy.spatial.distance.cdist(np.array(d_obs), np.array(d_ref), 'euclidean')  # small number of descriptors only

def normalize(x):
    return x / (np.linalg.norm(x.astype(np.float64))+1E-16)




class BoundingBox():
    def __init__(self, xmin=None, ymin=None, xmax=None, ymax=None, centroid=None, xcentroid=None, ycentroid=None, width=None, height=None, label=None, score=None, mask=None):

        if xmin is not None and ymin is not None and xmax is not None and ymax is not None:
            self.xmin = float(xmin)
            self.ymin = float(ymin)
            self.xmax = float(xmax)
            self.ymax = float(ymax)
        elif xmin is not None and ymin is not None and width is not None and height is not None:
            self.xmin = float(xmin)
            self.ymin = float(ymin)
            self.xmax = self.xmin + float(width)
            self.ymax = self.ymin + float(height)
        elif centroid is not None and width is not None and height is not None:
            self.xmin = float(centroid[0]) - float(width)/2.0
            self.ymin = float(centroid[1]) - float(height)/2.0
            self.xmax = float(centroid[0]) + float(width)/2.0
            self.ymax = float(centroid[1]) + float(height)/2.0                                                
        elif xcentroid is not None and ycentroid is not None and width is not None and height is not None:
            self.xmin = float(xcentroid) - float(width)/2.0
            self.ymin = float(ycentroid) - float(height)/2.0
            self.xmax = float(xcentroid) + float(width)/2.0
            self.ymax = float(ycentroid) + float(height)/2.0                                                
        elif mask is not None:
            # Convex hull of non-zero pixels in a mask image
            imx = np.sum(mask, axis=0)
            imy = np.sum(mask, axis=1)            
            self.xmin = np.argwhere(imx > 0)[0]
            self.ymin = np.argwhere(imy > 0)[0]
            self.xmax = np.argwhere(imx > 0)[-1]
            self.ymax = np.argwhere(imy > 0)[-1]
        else:
            self.xmin = float('nan')
            self.ymin = float('nan')
            self.xmax = float('nan')
            self.ymax = float('nan')

        self.label = label
        self.score = score

    def clone(self):
        return BoundingBox(xmin=self.xmin, xmax=self.xmax, ymin=self.ymin, ymax=self.ymax, label=self.label, score=self.score)
        
    def __repr__(self):
        xmin = '%1.1f' % float(self.xmin) if not math.isnan(self.xmin) else 'nan'
        ymin = '%1.1f' % float(self.ymin) if not math.isnan(self.ymin) else 'nan'
        xmax = '%1.1f' % float(self.xmax) if not math.isnan(self.xmax) else 'nan'
        ymax = '%1.1f' % float(self.ymax) if not math.isnan(self.ymax) else 'nan'                
        return str('<bobo.boundingbox: xmin=%s, ymin=%s, xmax=%s, ymax=%s>'% (xmin, ymin, xmax, ymax))

    def __str__(self):
        return self.__repr__()

    def invalid(self):
        is_undefined = math.isnan(self.xmin) or math.isnan(self.ymin) or math.isnan(self.xmax) or math.isnan(self.ymax)
        is_degenerate =  ((self.xmax-self.xmin)<1) or ((self.ymax-self.ymin)<1) or (self.xmin >= self.xmax) or (self.ymin >= self.ymax)
        return is_undefined or is_degenerate

    def translate(self, dx=0, dy=0):
        self.xmin = self.xmin + dx
        self.ymin = self.ymin + dy
        self.xmax = self.xmax + dx
        self.ymax = self.ymax + dy
        return self

    def valid(self):
        return not self.invalid()

    def isvalid(self):
        return self.valid()
            
    def width(self):
        return self.xmax - self.xmin

    def setwidth(self, w):
        if w <= 0:
            raise ValueError('invalid width')
        self.xmax += (w - self.width()) / 2.0
        self.xmin -= (w - self.width()) / 2.0        
        return self
    
    def setheight(self, h):
        if h <= 0:
            raise ValueError('invalid height')
        self.ymax += (h - self.height()) / 2.0
        self.ymin -= (h - self.height()) / 2.0        
        return self
        
    def height(self):
        return self.ymax - self.ymin
    
    def centroid(self):
        return [self.xmin + (float(self.width())/2.0), self.ymin + (float(self.height())/2.0)]
            
    def x_centroid(self):
        return self.centroid()[0]

    def y_centroid(self):
        return self.centroid()[1]
        
    def area(self):
        return self.width() * self.height()

    def to_xywh(self):
        """Convert corners to (x,y,width,height) format"""
        return [self.xmin, self.ymin, self.width(), self.height()]

    def dx(self, bb):
        return bb.xmin - self.xmin

    def dy(self, bb):
        return bb.ymin - self.ymin

    def sqdist(self, bb):
        return np.power(self.dx(bb), 2.0) + np.power(self.dy(bb), 2.0)
    
    def islabel(self, label):
        return self.label.lower() == label.lower()
    
    def overlap(self, bb):
        """area of intersection / area of union"""
        w = min(self.xmax, bb.xmax) - max(self.xmin, bb.xmin);
        h = min(self.ymax, bb.ymax) - max(self.ymin, bb.ymin);
        if ((w < 0) or (h < 0)):
            iou = 0;   # invalid (no overlap)
        else:
            area_intersection = w*h;
            area_union = (self.area() + bb.area() - area_intersection);
            iou = area_intersection / area_union;
        return iou;

    def intersection(self, bb):
        """Intersection of two bounding boxes"""
        self.xmin = max(bb.xmin, self.xmin)
        self.ymin = max(bb.ymin, self.ymin)
        self.xmax = min(bb.xmax, self.xmax)
        self.ymax = min(bb.ymax, self.ymax)
        return self
                    
    def union(self, bb):
        """Union of two bounding boxes"""
        self.xmin = min(bb.xmin, self.xmin)
        self.ymin = min(bb.ymin, self.ymin)
        self.xmax = max(bb.xmax, self.xmax)
        self.ymax = max(bb.ymax, self.ymax)
        return self
        
    def inside(self, p):
        return (p[0] >= self.xmin) and (p[1] >= self.ymin) and (p[0] <= self.xmax) and (p[1] <= self.ymax)

    def dilate(self, scale=1):
        """Change scale of bounding box keeping centroid constant"""
        w = self.width()
        h = self.height()
        c = self.centroid()
        self.xmin = c[0]-(float(w)/2.0)*scale
        self.ymin = c[1]-(float(h)/2.0)*scale
        self.xmax = c[0]+(float(w)/2.0)*scale
        self.ymax = c[1]+(float(h)/2.0)*scale
        return self

    def dilate_height(self, scale=1):
        """Change scale of bounding box in y direction keeping centroid constant"""
        h = self.height()
        c = self.centroid()
        self.ymin = c[1]-(float(h)/2.0)*scale
        self.ymax = c[1]+(float(h)/2.0)*scale
        return self

    def dilate_topheight(self, scale=1):
        """Change scale of bounding box in positive y direction only, changing centroid"""
        h = self.height()
        c = self.centroid()
        self.ymin = c[1]-(float(h)/2.0)*scale
        return self
        
    def rescale(self, scale=1):
        self.xmin = scale * self.xmin
        self.ymin = scale * self.ymin
        self.xmax = scale * self.xmax
        self.ymax = scale * self.ymax                        
        return self

    def imscale(self, im):
        w = (1.0 / float(im.width()))
        h = (1.0 / float(im.height()))
        self.xmin = w * self.xmin
        self.ymin = h * self.ymin
        self.xmax = w * self.xmax
        self.ymax = h * self.ymax                        
        return self
    
    def maxsquare(self):
        w = max(self.width(), self.height())
        h = max(self.height(), self.width())
        c = self.centroid()
        self.xmin = c[0]-(float(w)/2.0)
        self.ymin = c[1]-(float(h)/2.0)
        self.xmax = c[0]+(float(w)/2.0)
        self.ymax = c[1]+(float(h)/2.0)
        return self
        
    def imclip(self, img):
        """Clip bounding box to image rectangle"""
        self.intersection(BoundingBox(xmin=0, ymin=0, xmax=img.shape[1], ymax=img.shape[0]))
        return self
        
    def convexhull(self, fr):
        self.xmin = np.min(fr[:,0])
        self.ymin = np.min(fr[:,1])
        self.xmax = np.max(fr[:,0])
        self.ymax = np.max(fr[:,1])
        return self

    def aspectratio(self):
        return float(self.height()) / float(self.width())

    def shape(self):
        return (self.height(), self.width())

class Ellipse():
    def __init__(self, semi_major, semi_minor, xcenter, ycenter, phi):
        self.major = semi_major
        self.minor = semi_minor
        self.center_x = xcenter
        self.center_y = ycenter
        self.phi = phi

    def area(self):
        return math.pi * self.major * self.minor

    def center(self):
        return (int(self.center_x), int(self.center_y))

    def axes(self):
        return (int(self.major), int(self.minor))

    def angle(self):
        return int(self.phi * 180 / math.pi)

    def rescale(self, scale):
        self.major *= scale
        self.minor *= scale
        self.center_x *= scale
        self.center_y *= scale
        return self

    def estimate_boundingbox(self):
        """ Estimate an equivalent bounding box based on scaling to a common area.
        Note, this does not factor in rotation.
        (c*l)*(c*w) = a_e  --> c = \sqrt(a_e / a_r) """

        bbox = BoundingBox(width=2*self.minor, height=2*self.major, xcentroid=self.center_x, ycentroid=self.center_y)
        a_r = bbox.area()
        c = (self.area() / a_r) ** 0.5
        bbox2 = bbox.clone().dilate(c)
        # print 'start area bbox: %f' % bbox.area()
        # print 'end   area bbox: %f' % bbox2.area()
        # print 'area ellipse   : %f' % self.area()
        return bbox2
