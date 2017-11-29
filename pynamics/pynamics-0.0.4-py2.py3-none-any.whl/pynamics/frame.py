# -*- coding: utf-8 -*-

"""
Written by Daniel M. Aukes
Email: danaukes<at>gmail.com
Please see LICENSE for full license.
"""

import pynamics
from pynamics.tree_node import TreeNode
from pynamics.vector import Vector
from pynamics.rotation import Rotation
from pynamics.name_generator import NameGenerator

import sympy

class Frame(TreeNode,NameGenerator):
    def __init__(self,name = None):
        super(Frame,self).__init__()
        self.connections = {}
        self.precomputed = {}
        self.reps = {}

        name = name or self.generate_name()
        self.name = name
        
        self.x = Vector()
        self.y = Vector()
        self.z = Vector()

        self.x_sym = sympy.Symbol(name+'.x')
        self.y_sym = sympy.Symbol(name+'.y')
        self.z_sym = sympy.Symbol(name+'.z')
        self.syms = sympy.Matrix([self.x_sym,self.y_sym,self.z_sym])
        
        self.x.add_component(self,[1,0,0])
        self.y.add_component(self,[0,1,0])
        self.z.add_component(self,[0,0,1])
        self.add_rotation(Rotation(self,self,sympy.Matrix.eye(3),sympy.Number(0)*self.x))
        pynamics.addself(self,name)
        
    def add_rotation(self,rotation):
        self.connections[rotation.other(self)] = rotation
        
    def add_precomputed(self,rotation):
        self.precomputed[rotation.other(self)] = rotation
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return str(self)

    def calc(self,other):
        if other in self.connections:
            return self.connections[other]
        elif other in self.precomputed:
            return self.precomputed[other]
        else: 
            path = self.path_to(other)
            from_frames = path[:-1]
            to_frames = path[1:]
            Rs = [from_frame.connections[to_frame].to_other(from_frame) for from_frame,to_frame in zip(from_frames,to_frames)]
            w_s = [from_frame.connections[to_frame].w__from(from_frame) for from_frame,to_frame in zip(from_frames,to_frames)]
            R_final = Rs.pop(0)      
            w_final = w_s.pop(0)    
            for R,w_,to_frame in zip(Rs,w_s,to_frames[1:]):
                R_final = R*R_final
                w_final += w_
                rotation = Rotation(self,to_frame,R_final,w_final)
                self.add_precomputed(rotation)
                to_frame.add_precomputed(rotation)
#            rotation = Rotation(self,to_frame,R_final,w_final)
            return rotation

    def getR(self,other):
        return self.calc(other).to_other(self)

    def getw_(self,other):
        return self.calc(other).w__from(self)

    def rotate_fixed_axis(self,fromframe,axis,q,sys = None):
        sys = sys or pynamics.get_system()

        rotation = Rotation.build_fixed_axis(fromframe,self,axis,q,sys)
        self.add_rotation(rotation)
        fromframe.add_rotation(rotation)

    def rotate_fixed_axis_directed(self,fromframe,axis,q,sys=None):
        sys = sys or pynamics.get_system()
        
        self.rotate_fixed_axis(fromframe,axis,q,sys)
        fromframe.add_branch(self)        
        
    def efficient_rep(self,other,functionname):
        key = (other,functionname)
        if key in self.reps:
            return self.reps[key]
        else:
            path = self.path_to(other)
            dot = {}
            for mysym,myvec in zip(self.syms,[self.x,self.y,self.z]):
                for othersym,othervec in zip(other.syms,[other.x,other.y,other.z]):
                    min_dot_len = 0
                    for frame in path:
                        v1 = myvec.express(frame).components[frame]
                        v2 = othervec.express(frame).components[frame]
                        function = getattr(v1,functionname)
                        dot_rep = function(v2)
                        dot_len = len(str(dot_rep))
                        if min_dot_len==0 or dot_len<min_dot_len:
                            min_dot_len=dot_len
                            min_dot_frame = frame
                        elif dot_len==min_dot_len:
                            if min_dot_frame in frame.decendents:
                                min_dot_frame = frame
                    dot[frozenset((mysym,othersym))] = min_dot_frame
            self.reps[key] = dot
            return dot
                
