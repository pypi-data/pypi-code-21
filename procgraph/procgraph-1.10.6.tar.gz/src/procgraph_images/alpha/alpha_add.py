from procgraph.core.registrar_other import simple_block
from contracts import contract
import numpy as np


@simple_block
@contract(bg='array[HxWx(3|4)]', moving='array[HxWx4]')
def alpha_add(moving, bg):
    H, W = bg.shape[0:2]
    res = np.zeros((H, W, 3), 'uint8')
    
    im1 = bg
    im2 = moving
    alpha2 = moving[:, :, 3] 
#     alpha2 = alpha2 / 255.0 #np.max(alpha2)
    alpha2 = alpha2 > 0
    alpha1 = 1.0 - alpha2
    
    for i in range(3):
        res[:, :, i] = im1[:, :, i] * alpha1 + im2[:, :, i] * alpha2

    return res
