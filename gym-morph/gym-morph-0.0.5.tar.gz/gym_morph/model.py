#!/usr/bin/env python
# model.py - build the species and task models

import numpy as np
from mujoco_py import load_model_from_xml

from gym_morph import SPECIES

XML = '''
<mujoco>
  <compiler angle="degree" coordinate="local" inertiafromgeom="true"/>
  <option integrator="RK4" timestep="0.01"/>
  <default>
    <joint armature="1" damping="1" limited="true"/>
    <geom conaffinity="0" condim="3" density="5.0" friction="1 0.5 0.5" margin="0.01" rgba="0.8 0.6 0.4 1" type="capsule"/>
    <motor ctrllimited="true" ctrlrange="-1.0 1.0" gear="150"/>
  </default>
  <worldbody>
    <site name="origin" pos="0 0 0" rgba="1 0 0 1" size=".1"/>
    <geom name="floor" conaffinity="1" condim="3" pos="0 0 0" rgba="0.8 0.9 0.8 1" size="40 40 40" type="plane"/>
    <body name="torso" pos="0 0 1">
      <geom size="0.25" type="sphere"/>
      <joint armature="0" damping="0" limited="false" margin="0.01" name="root" pos="0 0 0" type="free"/>
      {legs}
    </body>
  </worldbody>
  <actuator>
    {motors}
  </actuator>
</mujoco>
'''

LEG = '''
  <body name="{name}" pos="0 0 0">
    <geom fromto="0.0 0.0 0.0 {pos}" size="0.08"/>
    <body pos="{pos}">
      <joint axis="0 0 1" name="{name}_j1" pos="0.0 0.0 0.0" range="-30 30" type="hinge"/>
      <geom fromto="0.0 0.0 0.0 {pos}" size="0.08"/>
      <body pos="{pos}">
        <joint axis="{axis}" name="{name}_j2" pos="0.0 0.0 0.0" range="30 70" type="hinge"/>
        <geom fromto="0.0 0.0 0.0 {pos2}" size="0.08"/>
      </body>
    </body>
  </body>
'''
MOTOR = '''
  <motor joint="{name}_j1"/>
  <motor joint="{name}_j2"/>
'''


def vec2str(v):
    return ' '.join(str(i) for i in v)


def build_robot(species):
    ''' Build and return a MuJoCo model for a given species. '''
    assert species in SPECIES
    if species == 'ant':
        legs = ''
        motors = ''
        for i, angle in enumerate(np.arange(0, np.pi * 2, np.pi / 2)):
            pos = np.array([np.sin(angle), np.cos(angle), 0]) * .28284
            axis = np.cross([0, 0, 1], pos)
            name = 'leg_{}'.format(i)
            legs += LEG.format(name=name, pos=vec2str(pos),
                               pos2=vec2str(2 * pos), axis=vec2str(axis))
            motors += MOTOR.format(name=name)
        xml = XML.format(legs=legs, motors=motors)
        return load_model_from_xml(xml)
