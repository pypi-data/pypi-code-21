import numpy as np
from procgraph import Block
from contracts import contract


class DepthBuffer(Block):
    
    Block.alias('depth_buffer')

    Block.input('rgba')
    Block.output('rgba')
    Block.output('line')
    Block.output('depth')
    
    def init(self):
        self.depth = None
        
    def update(self):
        rgba = self.input.rgba
        if self.depth is None:
            H, W = rgba.shape[0:2]
            self.depth = np.zeros((H, W))
            self.depth.fill(0)

        d = get_depth(rgba)
        
        mask = rgba[:, :, 3] > 0
        closer = np.logical_and(self.depth < d, mask) 
        farther = np.logical_not(closer)

        self.depth[closer] = d
        
        rgba = rgba.copy()
        rgba[farther, 3] = 0
             
        with_line = rgba[:, :, 0:3].copy()
        with_line[d, :, 0] = 255
        with_line[d, :, 1] = 55
        
        depth = self.depth.copy()
        depth[depth == 0] = np.nan
        self.output.rgba = rgba
        self.output.line = with_line
        self.output.depth = depth
        
        
@contract(rgba='array[HxWx4](uint8)', returns='float,>=0,<=H-1')
def get_depth(rgba):
    alpha = rgba[:, :, 3]
    H, _ = alpha.shape

    a = 0
    w = 0
    for i in range(H):
        line = alpha[i, :].astype('float32')
        a += i * np.sum(line) 
        w += np.sum(line)
    a = a / w
    return a


