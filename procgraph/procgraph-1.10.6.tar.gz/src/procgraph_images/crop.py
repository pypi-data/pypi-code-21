from procgraph import simple_block


@simple_block
def crop(rgb, left=0, right=0, top=0, bottom=0):
    ''' Crops an image by the given values'''

    #print('Cropping %s' % (str(rgb.shape)))
    height = rgb.shape[0]
    width = rgb.shape[1]
    

    rgb2 = rgb[top:(height-bottom), left:(width-right), :]

    if rgb2.shape[0] == 0 or rgb2.shape[1] == 0:
        msg = ('Obtained empty image (t %s, r %s, b %s, l %s) on (%s,%s)' % 
                (top,right,bottom,left, height, width))
        raise ValueError(msg)
    
#     print('cropping %s -> %s' % (str(rgb.shape), str(rgb2.shape)))

#    if left > 0:
#        rgb = rgb[:, left:, :]
#
#    if right > 0:
#        rgb = rgb[:, :-right, :]
#
#    if top > 0:
#        rgb = rgb[top:, :, :]
#
#    if bottom > 0:
#        rgb = rgb[:-bottom, :, :]
    return rgb2


