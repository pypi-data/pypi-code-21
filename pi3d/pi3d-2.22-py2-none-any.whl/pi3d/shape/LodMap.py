from __future__ import absolute_import, division, print_function, unicode_literals

import math
import sys, os

import sys
sys.path.insert(1,'/home/patrick/pi3d')
import pi3d

from PIL import Image, ImageOps

import numpy as np

# a rectangular surface where elevation is defined by a greyscal image
class LodMap(pi3d.Shape):
  ''' 3d model inherits from Shape
  '''
  def __init__(self, mapfile, camera=None, light=None, name='',
               width=1125.0, height=10.0,
               position=(0.0, 0.0),
               x=0.0, y=0.0, z=0.0, rx=0.0, ry=0.0, rz=0.0,
               sx=1.0, sy=1.0, sz=1.0, cx=0.0, cy=0.0, cz=0.0):
    '''uses standard constructor for Shape plus
    
    Arguments:
      *mapfile*
        Image path/file, string. RGB converted to L (luminance) to use
        as height. The default resolution is 1125x1125 image mapping to
        1126 world units i.e. 1 pixel per unit for the inner 16x16 vertices,
        5 pixels per middle range vertex and 75 pixels for the outer vertices.

    Keyword arguments:
      *width, height*
        Of the map in world units. map is always square
      *position*
        'camera' position around which point to make highest resolution
        part of terrain.
    '''
    self.width = width
    self.height = height
    super(LodMap, self).__init__(camera, light, name, x, y, z, rx, ry, rz,
                                       sx, sy, sz, cx, cy, cz)
     # load initial grid
    self.verts = np.loadtxt('lod_map_verts.txt')
    faces = np.loadtxt('lod_map_faces.txt') - 1 # obj vert index starts at 1 TODO check if we need to keep a copy 
    normals = np.zeros(self.verts.shape, dtype="float32")
    tex_coords = np.zeros((self.verts.shape[0], 2), dtype="float32")
    self.buf = [pi3d.Buffer(self, self.verts, tex_coords, faces, normals)]
    # create selectors from grid
    self.wh = [np.where((np.abs(self.verts[:,0]) >= 50.0) | (np.abs(self.verts[:,2]) >= 50.0))[0],
               np.where((np.abs(self.verts[:,0]) < 50.0) & 
                        (np.abs(self.verts[:,2]) < 50.0) & 
                       ((np.abs(self.verts[:,0]) >= 10.0) | (np.abs(self.verts[:,2]) >= 10.0)))[0],
               np.where((np.abs(self.verts[:,0]) < 10.0) & (np.abs(self.verts[:,2]) < 10.0))[0]]
    print(len(self.wh[0]), len(self.wh[1]), len(self.wh[2]), self.verts.shape)
    # load map file
    im = Image.open(mapfile).convert('L')
    # generate scaled versions and convert to numpy arrays 1 : 1/5 : 1/75 (-1/2 pixel each side) or
    # 1126:226:16
    self.N = (15, 225, 1125)
    self.ht = [np.array(im.resize((self.N[i] + 1, self.N[i] + 1), Image.LANCZOS)) for i in range(3)]
    #print(self.ht[0].shape, self.ht[1].shape, self.ht[2].shape)

  def _regenerate(self, x, z):
    ''' put the vertices in the correct x, z locations to match relevant pixel
    map pixel locations. change y values to match L value of pixel x height
    '''
    a, b = self.x(), self.z() # offset of map
    ab = self.buf[0].array_buffer # alias for brevity
    ix = []
    for i in range(3):
      ix.append(np.floor((self.verts[self.wh[i],0:3:2] + [x, z] - [a, b]) * self.N[i] / 
                                      self.N[2] + self.N[i] / 2.0 + 0.5).astype(np.int))
      #ab[self.wh[i],0:3:2] = (ix[i][:,:] - self.N[i] / 2.0) * self.N[2] / self.N[i] # x, z values
      ab[self.wh[i],0:3:2] = (ix[i][:,:] - self.N[i] / 2.0) * self.width / self.N[i] # x, z values
      # TODO scale width and depth
      ix[i] %= (self.N[i] + 1) # put into range of image pixels
      ab[self.wh[i], 1] = self.ht[i][ix[i][:,0], ix[i][:,1]] * self.height / 256.0 # y values
      ab[self.wh[i], 6:8] = ab[self.wh[i],0:3:2] / self.width - [0.5, 0.5] # uv coordinates
    ab[:,3:6] = self.buf[0].calc_normals()
    
    #print(ab[self.wh[1]][:20,:3], self.verts[self.wh[1]][:20,0:3:2])

display = pi3d.Display.create(w=1600, h=1200)
camera = pi3d.Camera()
light = pi3d.Light((10, -1, -5), (1.0, 0.8, 0.7),(0.0, 0.0, 0.2))
shader = pi3d.Shader('uv_light')
tex = pi3d.Texture('/home/patrick/pi3d_demos/textures/mountains3_512.jpg')
test = LodMap('/home/patrick/pi3d_demos/textures/mountainsHgt2.png', width=3000.0, height=250.0)
test.set_draw_details(shader, [tex])
test._regenerate(0.0, 0.0)
test.buf[0].re_init()

mouse = pi3d.Mouse(restrict=False)
mouse.start()
keys = pi3d.Keyboard()
rot = 0.0
tilt = 0.0
xloc = 0.0
yloc = 220.0
zloc = 0.0
while display.loop_running():
  mx, my = mouse.position()
  rot = - mx * 0.2
  tilt = my * 0.2
  xtmp, ytmp, ztmp = camera.relocate(rot, tilt, point=[xloc, yloc, zloc], distance=[0.5, 0.5, 0.5])

  test.draw()

  k = keys.read()
  if k > -1:
    if k == ord('w'):
      xloc, yloc, zloc = xtmp, ytmp, ztmp
    elif k == ord('r'):
      test._regenerate(xtmp, ztmp)
      test.buf[0].re_init()
    elif k == 27:
      break
