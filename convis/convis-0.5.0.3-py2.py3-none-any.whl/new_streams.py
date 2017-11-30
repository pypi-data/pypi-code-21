

class StreamPointer(object):
    def __init__(self, stream, t=0.0, dt=0.001):
        self.stream = stream
        self.t = t
        self.dt = dt
    def __next__(self,i):
        self.t += i * self.dt
        return self.stream.get(self.t)

import scipy.ndimage.interpolation
# sample_image = scipy.ndimage.interpolation.zoom(np.mean(plt.imread(sample_images[image_num%len(sample_images)]),2),zoom)
# padded_sample_image = np.pad(sample_image,[(window[0],window[0]),(window[1],window[1])],mode='reflect')


import numpy as np

class WrapSliceArray(np.ndarray):
    """
        Behaves like a numpy array, but when indexing with two dimensions
        (read only) the array will wrap around.
        
        Example::
        
            wsa = rand((30,30)).view(WrapSliceArray)
            imshow(wsa[5:85,-20:50])

    """
    def __getitem__(self,inds):
        if len(inds) == 2:
            i0,i1 = inds
            if i0.start is not None and i0.start < 0:
                real_start = i0.start%self.shape[0]
                i0 = slice(real_start,i0.stop-i0.start+real_start)
            if i1.start is not None and i1.start < 0:
                real_start = i1.start%self.shape[0]
                i1 = slice(real_start,i1.stop-i1.start+real_start)

            if i0.stop > self.shape[0]:
                indices_0 = []
                indices_0.append(slice(i0.start,self.shape[0]))
                for i0_start in range(i0.start,i0.stop-self.shape[0],self.shape[0]):
                    indices_0.append(slice(0,self.shape[0]))
                indices_0.append(slice(0,i0.stop%self.shape[0]))
            else:
                indices_0 = [i0]
            if i1.stop > self.shape[1]:
                indices_1 = []
                indices_1.append(slice(i1.start,self.shape[1]))
                for i1_start in range(i1.start,i1.stop-self.shape[1],self.shape[1]):
                    indices_1.append(slice(0,self.shape[1]))
                indices_1.append(slice(0,i1.stop%self.shape[1]))
            else:
                indices_1 = [i1]
            ll = []
            for i0 in indices_0:
                l = []
                for i1 in indices_1:
                    l.append(super(WrapSliceArray,self).__getitem__((i0,i1)))
                ll.append(np.concatenate(l,axis=1))
            return np.concatenate(ll,axis=0)
        else:    
            return super(WrapSliceArray,self).__getitem__(inds)

class FlipSliceArray(np.ndarray):
    """
        Behaves like a numpy array, but when indexing with two dimensions
        (read only) the array will wrap around.
        
        Example::
        
            wsa = rand((30,30)).view(WrapSliceArray)
            imshow(wsa[5:85,-20:50])

    """
    def __getitem__(self,inds):
        if len(inds) == 2:
            do_flip = True
            i0,i1 = inds
            flip_0 = False
            flip_1 = False
            if i0.start is not None and i0.start < 0:
                real_start = i0.start%self.shape[0]
                if do_flip:
                    flip_0 = (i0.start/self.shape[0])%2 == 0
                i0 = slice(real_start,i0.stop-i0.start+real_start)
            if i1.start is not None and i1.start < 0:
                real_start = i1.start%self.shape[0]
                if do_flip:
                    flip_1 = (i1.start/self.shape[1])%2 == 0
                i1 = slice(real_start,i1.stop-i1.start+real_start)

            if i0.stop > self.shape[0]:
                indices_0 = []
                indices_0.append(slice(i0.start,self.shape[0]))
                for i0_start in range(i0.start,i0.stop-self.shape[0],self.shape[0]):
                    indices_0.append(slice(0,self.shape[0]))
                indices_0.append(slice(0,i0.stop%self.shape[0]))
            else:
                indices_0 = [i0]
            if i1.stop > self.shape[1]:
                indices_1 = []
                indices_1.append(slice(i1.start,self.shape[1]))
                for i1_start in range(i1.start,i1.stop-self.shape[1],self.shape[1]):
                    indices_1.append(slice(0,self.shape[1]))
                indices_1.append(slice(0,i1.stop%self.shape[1]))
            else:
                indices_1 = [i1]
            ll = []
            flip_1_backup = flip_1
            for i0 in indices_0:
                l = []
                if do_flip:
                    if flip_0:
                        i0 = slice(shape[0]-i0.start,shape[0]-i0.stop,-1)
                    flip_0 = not flip_0
                    flip_1 = flip_1_backup
                for i1 in indices_1:
                    if do_flip:
                        if flip_1:
                            i1 = slice(shape[1]-i1.start,shape[1]-i1.stop,-1)
                        flip_1 = not flip_1
                    l.append(super(FlipSliceArray,self).__getitem__((i0,i1)))
                ll.append(np.concatenate(l,axis=1))
            return np.concatenate(ll,axis=0)
        else:    
            return super(FlipSliceArray,self).__getitem__(inds)
"""
def take_from_tiled(im,inds,do_flip = True):
    i0,i1 = inds
    flip_0 = False
    flip_1 = False
    if i0.start is None:
        i0 = slice(0,i0.stop)
    if i0.stop is None:
        i0 = slice(i0.start,im.shape[0])
    if i1.start is None:
        i1 = slice(0,i1.stop)
    if i1.stop is None:
        i1 = slice(i1.start,im.shape[1])

    if i0.start < 0:
        real_start = i0.start%im.shape[0]
        if do_flip:
            flip_0 = (i0.start/im.shape[0])%2 == 1
        i0 = slice(real_start,i0.stop-i0.start+real_start)
    if i1.start < 0:
        real_start = i1.start%im.shape[0]
        if do_flip:
            flip_1 = (i1.start/im.shape[1])%2 == 1
        i1 = slice(real_start,i1.stop-i1.start+real_start)
    if i0.stop > im.shape[0]:
        indices_0 = []
        indices_0.append(slice(i0.start,im.shape[0]))
        for i0_start in range(i0.start,i0.stop-im.shape[0],im.shape[0]):
            indices_0.append(slice(0,im.shape[0]))
        indices_0.append(slice(0,i0.stop%im.shape[0]))
    else:
        indices_0 = [i0]
    if i1.stop > im.shape[1]:
        indices_1 = []
        indices_1.append(slice(i1.start,im.shape[1]))
        for i1_start in range(i1.start,i1.stop-im.shape[1],im.shape[1]):
            indices_1.append(slice(0,im.shape[1]))
        indices_1.append(slice(0,i1.stop%im.shape[1]))
    else:
        indices_1 = [i1]
    ll = []
    flip_1_backup = flip_1
    for i0 in indices_0:
        l = []
        if do_flip:
            if flip_0:
                i0 = slice(im.shape[0]-i0.start,im.shape[0]-i0.stop,-1)
            flip_0 = not flip_0
            flip_1 = flip_1_backup
        for i1 in indices_1:
            if do_flip:
                if flip_1:
                    i1 = slice(im.shape[1]-i1.start,im.shape[1]-i1.stop,-1)
                flip_1 = not flip_1
            l.append(im.__getitem__((i0,i1)))
        ll.append(np.concatenate(l,axis=1))
    return np.concatenate(ll,axis=0)
"""

def take_from_tiled(im,inds,do_flip = True):
    """
        Takes a slice of an n dimensional array, but wraps
        or flips the array at the borders.
        So you can `take` parts that are much larger than 
        the array!
        
        Values outside the array are wrapped around.
        If `do_flip` is True, every second revolution
        of the array is flipped, such that at each border
        the values are mirrored.
        
    """
    im = np.array(im)
    if len(im.shape) > len(inds):
        # trying to extend the indices array
        if len(inds) == 2:
            if len(im.shape) == 3:
                inds = np.array([slice(None),inds[0],inds[1]])
            elif len(im.shape) == 5:
                inds = np.array([slice(None),slice(None),slice(None),inds[0],inds[1]])
            else:
                raise Exception('Length of im.shape (= %d) and inds (= %d) does not match!'%(len(im.shape), len(inds)))
        elif len(inds) == 3 and len(im.shape) == 5:
            inds = np.array([slice(None),inds[0],slice(None),inds[1],inds[2]])
        else:
            raise Exception('Length of im.shape (= %d) and inds (= %d) does not match!'%(len(im.shape), len(inds)))
    elif len(im.shape) < len(inds):
        raise Exception('Length of im.shape (= %d) and inds (= %d) does not match!'%(len(im.shape), len(inds)))
    all_indices = [] # holds a list 
    flips = [False]*len(inds)
    for i,i0 in enumerate(inds):
        # For each dimension we generate a list
        # of slices in the original array that 
        # concatenated give the desired slice.
        # Flipping will be done later.
        if i0.start is None:
            i0 = slice(0,i0.stop)
        if i0.stop is None:
            i0 = slice(i0.start,im.shape[i])

        if i0.start < 0:
            real_start = i0.start%im.shape[i]
            if do_flip:
                flips[i] = (i0.start/im.shape[i])%2 == 1
            i0 = slice(real_start,i0.stop-i0.start+real_start)
        if i0.stop > im.shape[i]:
            indices_0 = []
            # we start with a partial slice
            indices_0.append(slice(i0.start,im.shape[i]))
            for i0_start in range(i0.start,i0.stop-im.shape[i],im.shape[i]):
                # we add a number of full slices
                indices_0.append(slice(0,im.shape[i]))
            # And lastly we add another partial slice
            indices_0.append(slice(0,i0.stop%im.shape[i]))
        else:
            indices_0 = [i0]
        all_indices.append(indices_0)
    def rec_for(rec_inds,*args):
        i = len(args)
        if len(rec_inds) >= 1:
            flip = flips[i]
            l = []
            for ind in rec_inds[0]:
                if flip:
                    # flipping
                    ind = slice(im.shape[i]-ind.start+2,im.shape[i]-ind.stop,-1)
                flip = not flip
                args = list(args)
                l.append(rec_for(rec_inds[1:],*(args+[ind])))
            return np.concatenate(l,axis=i)
        else:
            return im.__getitem__(tuple(args))
    return rec_for(all_indices)



class BaseStream(object):
    """Basic stream that gives zeros"""
    def __init__(self, size=(50,50), pixel_per_degree=10, t_zero = 0.0, t=0.0, dt=0.001):
        self.size = list(size)
        self.pixel_per_degree = pixel_per_degree
        self.t = t
        self.t_zero = t_zero
        self.dt = dt
        self.pointers = []
    def time_to_bin(self,t):
        return (t-self.t_zero)/self.dt
    def available(self,l=1):
        return True
    def get(self,i):
        self.t += i * self.dt
        return np.zeros([i]+self.size)
    def put(self,s):
        raise Exception("Not implemented for basic stream.")
    def close(self):
        pass
    def _web_repr_(self,name,namespace):
        import cgi
        s= "Image Stream Object:<br>"
        s+= " + class: "+cgi.escape(str(self.__class__))+"<br>"
        try:
            s+= " + time: "+str(self.t)+"<br>"
        except:
            pass
        try:
            s+= " + length: "+str(len(self))+"<br>"
        except:
            s+= " + length: -- <br>"
        if hasattr(self,'get_image'):
            s+= '<img class="mjpg" src="/mjpg/'+name+'" alt="'+name+'" height="400"/>'
        return s
    @property
    def buffered(self):
        return 0
    def __iter__(self):
        return StreamPointer(self,t=0,dt=self.dt)



class SequenceStream(Stream):
    """ 3d Numpy array that represents a sequence of images"""
    def __init__(self, sequence=np.zeros((0,50,50)), size=None, zoom=1.0, pixel_per_degree=10):
        self.size = sequence.shape[1:]
        self.pixel_per_degree = pixel_per_degree
        self.sequence = sequence.view(FlipSliceArray)
        self.zoom = zoom
        self.i = 0
        self.max_frames = 50
    def __len__(self):
        return len(self.sequence)
    def available(self,l=1):
        return (len(self.sequence) - self.i) > l
    def get_image(self):
        try:
            if self.i < 1:
                return self.sequence[-1]
            return self.sequence[self.i]
        except:
            return np.zeros(self.sequence.shape[1:])
    def __getitem__(ind):
        return self.sequence[int(ind.start):int(ind.stop):int(ind.step)]
    def get(self,i):
        self.i += i
        return self.sequence[int(self.i-i):self.i]
    def put(self,s):
        if self.sequence.shape[1:] == s.shape[1:]:
            if len(self.sequence) + len(s) > self.max_frames:
                self.sequence = np.concatenate([self.sequence,s],axis=0)[-self.max_frames:]
            else:
                self.sequence = np.concatenate([self.sequence,s],axis=0)
        else:
            if len(s) > self.max_frames:
                self.sequence = s[-self.max_frames:]
            else:
                self.sequence = s




class StreamPointer(object):
    def __init__(self, stream, i=0, **kwargs):
        self.stream = stream
        self.i = i
        self.kwargs = kwargs
        self.dt = 0.0
        self.t = 0.0
        self.iter_length = None # if None: images, if int: 3d or 5d chunks
        self.ndims = 3 # 3 or 5
        self.__dict__.update(kwargs)
    def __iter__(self):
        return StreamPointer(self.stream,self.i,**self.kwargs)
    def __len__(self):
        return len(self.stream)
    def __next__(self):
        return self.next()
    def next(self):
        self.i += 1
        if self.i >= len(self.stream):
            raise StopIteration()
        if getattr(self,'size',None) is not None:
            self.offset = (0,0) # for now
            center = self.stream.shape[0]/2.0,self.stream.shape[1]/2.0
            a = (int(center[0] - self.size[0]/2.0 + self.offset[0]),
                 int(center[1] - self.size[1]/2.0 + self.offset[1]))
            b = int(a[0] + self.size[0]), int(a[1] + self.size[1])
            #return self.stream[self.i].view(FlipSliceArray)[a[0]:b[0],a[1]:b[1]]
            return take_from_tiled(self.stream[self.i],(slice(a[0],b[0]),slice(a[1],b[1])))
        return self.stream[self.i]
    def min(self):
        return self.stream.min()
    def max(self):
        return self.stream.max()


class SequenceStream(BaseStream):
    """ 3d Numpy array that represents a sequence of images"""
    def __init__(self, sequence=np.zeros((0,50,50)), size=None, zoom=1.0, pixel_per_degree=10):
        self.size = sequence.shape[1:]
        self.shape = sequence.shape[1:]
        self.pixel_per_degree = pixel_per_degree
        self.sequence = sequence
        self.zoom = zoom
        self.i = 0
        self.max_frames = 50
        self.min_ = np.min(sequence)
        self.max_ = np.max(sequence)
        if self.min_ == self.max_:
            self.min_ = 0.0
            self.max_ = 1.0
    def __len__(self):
        return len(self.sequence)
    def available(self,l=1):
        return (len(self.sequence) - self.i) > l
    def get_image(self):
        try:
            if self.i < 1:
                return self.sequence[-1]
            return self.sequence[self.i]
        except:
            return np.zeros(self.sequence.shape[1:])
    def __getitem__(self,ind):
        if type(ind) is slice:
            return self.sequence[int(ind.start):int(ind.stop):int(ind.step)]
        return self.sequence.__getitem__(ind)
    def get(self,i):
        self.i += i
        return self.sequence[int(self.i-i):self.i]
    def put(self,s):
        if self.sequence.shape[1:] == s.shape[1:]:
            if len(self.sequence) + len(s) > self.max_frames:
                self.sequence = np.concatenate([self.sequence,s],axis=0)[-self.max_frames:]
            else:
                self.sequence = np.concatenate([self.sequence,s],axis=0)
        else:
            if len(s) > self.max_frames:
                self.sequence = s[-self.max_frames:]
            else:
                self.sequence = s
    def __iter__(self):
        return StreamPointer(self)
        #for t in range(len(self))
        #    yield self[t]
    def view(self,i=0,dt=1.0,size=None,offset=None):
        return StreamPointer(self,i=i,dt=dt,size=size,offset=offset)
    def min(self):
        return self.min_
    def max(self):
        return self.max_


class Stream(BaseStream):
    def __init__(self, stream,type=None):
        """
            the input argument stream can be:

                * a filename
                    - opencv video / webcam 
                    - npy
                    - inr
                * a filename pattern
                    - sequence of images
                    - sequence of files?
                * a numpy array
                * an iterator
                
            The actual iteration is done by the Pointers/Views,
            the stream only remembers the inital conditions and
            maybe some information to keep different views in 
            sync?

            Resizing / zooming is also done by the view.

            when we call iter on a static stream, the view starts back at 0.
            If we call iter on a view or a dynamic stream, the view will
            start at the same point as the original.
                -> static stream just means that Stream.i is fixed to 0?

            Do we want a global offset to shift the image? Probably not since
            two different views are at different points in time.

        """
        self.stream = stream
        if type is None:
            # start guessing:
            if type(stream) is str:
                # if filename pattern (ie. has it a *)

                # if filename
                pass
            # if numpy array
            if hasattr(stream,'__array__'):
                # we can use it as an array
                # isn't that the same as using the iterator? :/
                pass
            # if iterator
            if hasattr(stream,'__iter__'):
                # it is an iterator!
                # it will be iterated over by any view that we create
                pass


