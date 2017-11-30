# -*- coding: utf-8 -*-

"""
Written by Daniel M. Aukes
Email: danaukes<at>gmail.com
Please see LICENSE for full license.
"""

import sympy
import pynamics

class Vector(object):
    def __init__(self,components=None):
        self.components = {}
        if components!=None:
            for frame,vec in components.items():
                self.add_component(frame,vec)
        self.clean()
            
    def add_component(self,frame,vector):
        try:
            self.components[frame]+=vector
        except KeyError:
            self.components[frame]=sympy.Matrix(vector)
#        self.clean()

    def __str__(self):
        return str(self.symbolic())

    def __repr__(self):
        return str(self)

    def __mul__(self,other):
        newvec = Vector(self.components.copy())
        for key,value in newvec.components.items():
            newvec.components[key] *= other
        newvec.clean()
        return newvec

    def __rmul__(self,other):
        return self.__mul__(other)

    def __add__(self,other):
        newvec = Vector()
        newvec.components = self.components.copy()
        if other==0:
            return newvec
            newvec.clean()
        else:
            for frame,vector in other.components.items():
                newvec.add_component(frame,vector)
            newvec.clean()
            return newvec

    def __radd__(self,other):
        return self.__add__(other)

    def __sub__(self,other):
        newvec = Vector()
        newvec.components = self.components.copy()
        for frame,vector in other.components.items():
            newvec.add_component(frame,-vector)
        newvec.clean()
        return newvec

    def __neg__(self):
        newvec = Vector()
        newvec.components = self.components.copy()
        for frame,vector in newvec.components.items():
            newvec.components[frame]=-vector
        newvec.clean()
        return newvec
    
    def dot(self,other,frame='source'):
        from pynamics.dyadic import Dyad,Dyadic
        result = sympy.Number(0)
        if isinstance(other,Dyad) or isinstance(other,Dyadic):
            return other.rdot(self)
        return self.product_simplest(other,result,'dot',self.frame_dot,frame='mid')
#        return self.product_simple(other,result,'dot',self.frame_dot)
#        return self.product_by_basis_vectors(other,result,'dot',self.frame_dot)

    def cross(self,other,frame='source'):
        from pynamics.dyadic import Dyad,Dyadic
        result = Vector()
        if isinstance(other,Dyad) or isinstance(other,Dyadic):
            return other.rcross(self)
        result = self.product_simplest(other,result,'cross',self.frame_cross,frame='mid')
#        result = self.product_simple(other,result,'cross',self.frame_cross)
#        result = self.product_by_basis_vectors(other,result,'cross',self.frame_cross)
        result.clean()
        return result
    
    def length(self):
        return (self.dot(self))**.5
    
    def simplify(self):
        newvec = Vector()
        newvec.components = self.components.copy()
        for frame,vector in newvec.components.items():
            vector.simplify()
        return newvec
        
    @staticmethod
    def frame_dot(v1,v2,frame):
        return sympy.Matrix.dot(v1.components[frame],v2.components[frame])

    @staticmethod
    def frame_cross(v1,v2,frame):
        return Vector({frame:sympy.Matrix.cross(v1.components[frame],v2.components[frame])})

#    def product_in_parts(self,other,result,function,method='source'):  
#        from pynamics.frame import Frame
#        
#        for frame1,vector1 in self.components.items():
#            if method=='source':
#                frame = frame1                
#            for frame2,vector2 in other.components.items():
#                if method=='dest':
#                    frame = frame2      
#                elif isinstance(method,Frame):
#                    frame = method
#                v1 = Vector({frame1:vector1})
#                v1 = v1.express(frame)
#                v2 = Vector({frame2:vector2})
#                v2 = v2.express(frame)
#                localresult = function(v1,v2,frame)
#                result=result+localresult
##        result.clean()
#        return result

    def copy(self):
        newvec = Vector(self.components.copy())
        newvec.clean()
        return newvec
    
    def product_by_basis_vectors(self,other,result_seed,function,inner_function):
        self = self.copy()
        other = other.copy()        
        
        a = self.split_by_nonzero_basis_vectors()
        b = other.split_by_nonzero_basis_vectors()
        
        result = result_seed.copy()
        for frame1 in a.keys():
            for frame2 in b.keys():
                if frame1!=frame2:
                    rep = frame1.efficient_rep(frame2,function)
                    for bv1 in a[frame1][0]:
                        for bv2 in b[frame2][0]:
                            efficient_frame = rep[frozenset((bv1[0],bv2[0]))]
                            v1 = bv1[1].express(efficient_frame)
                            v2 = bv2[1].express(efficient_frame)
                            result+=inner_function(v1,v2,efficient_frame)
                else:
                    v1 = a[frame1][1]
                    v2 = b[frame2][1]
                    result+=inner_function(v1,v2,frame1)
#        result.clean()
        if len(str(result))<len(str(result.expand())):
            return result
        else:
            return result.expand()
#        result = result.expand()
#        return result
#        result2 = self.product_simple(other,result_seed,function,inner_function).expand()
#        if len(str(result))<=len(str(result2)):
#            print('1',result,result2)
#            return  result
#        else:
#            print('2',result,result2)
#            return  result2
                

    def product_simplest(self,other,result_seed,function,inner_function,frame = 'source'):
        result = result_seed.copy()
        for frame2,vec2 in other.components.items():
            vector2 = Vector({frame2:vec2})
            for frame1,vec1 in self.components.items():
                if frame == 'source':
                    expressed_frame = frame1                    
                elif frame == 'dest':
                    expressed_frame = frame2
                elif frame == 'mid':
                    path = frame1.path_to(frame2)
                    m = len(path)
                    if m%2==0:
                        ii = int(m/2)-1
                    else:
                        ii = int(m/2)
                    expressed_frame = path[ii]
                else:
                    expressed_frame = frame1                    

                vector1 = Vector({frame1:vec1})
                localresult = inner_function(vector1.express(expressed_frame),vector2.express(expressed_frame),expressed_frame)
                result+=localresult
#        result.clean()
        return result
    
    def product_simple(self,other,result_seed,function,inner_function):
        allframes = []
        frames_self = self.components.keys()
        frames_other = other.components.keys()
        for frame1 in frames_self:
            for frame2 in frames_other:
                allframes.extend(frame1.path_to(frame2))
        results = []
        for frame in allframes:
            v1 = self.express(frame)
            v2 = other.express(frame)
            results.append(result_seed+inner_function(v1,v2,frame))
        lens = [len(str(item)) for item in results]
        shortest = sorted(lens)[0]
        result = results[lens.index(shortest)]
#        result.clean()
        return result

    def time_derivative(self,reference_frame = None,sys=None):    
        sys = sys or pynamics.get_system()
        reference_frame = reference_frame  or sys.newtonian
        
        result = Vector()
        for frame,vector in self.components.items():
            result+= Vector({frame:sys.derivative(vector)})
            v1 = Vector({frame:vector})
            w_ = reference_frame.getw_(frame).express(frame)
            result+=w_.cross(v1,frame = 'mid')
        result.clean()
        return result
            
    def express(self,other):
        self = self.copy()
#        results = []
        try:
#            results.append(self.components.pop(other))
            result = Vector({other:self.components.pop(other)})
        except KeyError:
            result = Vector()
#            pass
        for frame,vec in self.components.items():
            R = frame.getR(other)
            result+=Vector({other:R*vec})
#            results.append()
#        result = results.pop()
#        while not not results:
#            result+=results.pop()
#        new = Vector({other:result})
        result.clean()
        return result

    def symbolic(self):
        result = sympy.Number(0)
        for frame,vec in self.components.items():
            result+=frame.syms.dot(vec)
        return result

#    def diff_local(self,sys = None):
#        newvec = Vector()
#        for frame,expression in self.components.items():
#            result = sys.derivative(expression)
#            newvec.components[frame] = result
#        return newvec
        
    def diff_partial_local(self,var):
        newvec = Vector()
        for frame,vec in self.components.items():
            result = vec.diff(var)
            newvec.components[frame] = result
        newvec.clean()
        return newvec
        
    def diff_simple(self,frame,sys=None):
        sys = sys or pynamics.get_system()

        v = self.express(frame).components[frame]
        dv = sys.derivative(v)
        newvec = Vector({frame:dv})
        newvec.clean()
        return newvec

    def split_by_frame(self):
        output_vectors = []
        for frame,vec in self.components.items():
            output_vectors.append(Vector({frame:vec}))
        return output_vectors
        
    def nonzero_basis_vectors(self):
        bvs = []
        for frame, vec in self.components.items():
            for val,sym in zip(vec,frame.syms):
                if val!=0:
                    bvs.append(sym)
        return bvs

    def split_by_nonzero_basis_vectors(self):
        bvs = {}
        for frame, vec in self.components.items():
            if vec!=sympy.Matrix([0,0,0]):
                bvs[frame] = [],Vector({frame:vec})
            for val,sym,bv in zip(vec,frame.syms,[frame.x,frame.y,frame.z]):
                if val!=0:
                    bvs[frame][0].append((sym,val*bv))
        return bvs
        
    def expand(self):
        new = self.copy()
        for key in new.components:
            new.components[key] = new.components[key].expand()
        return new

    def atoms(self,*args,**kwargs):
        atoms = []
        for value in self.components.values():
            atoms.extend(value.atoms(*args,**kwargs))
        return set(atoms)

    def clean(self):
        zero_keys = [frame for frame,vector in self.components.items() if vector.is_zero]
        for key in zero_keys:
            self.components.pop(key)
        return self
            
    def frames(self):
        nonzero_frames = [frame for frame,vector in self.components.items() if vector.is_zero==False]
        return nonzero_frames
                
        