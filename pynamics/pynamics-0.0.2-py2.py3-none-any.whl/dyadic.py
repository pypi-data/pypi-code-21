# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes
Email: danaukes<at>gmail.com
Please see LICENSE for full license.
"""

class Dyad(object):
    def __init__(self,vector1,vector2):
        self.vector1 = vector1
        self.vector2 = vector2
    def __str__(self):
        return str((self.vector1.symbolic(),self.vector2.symbolic()))
    def __repr__(self):
        return str(self)
    def __rmul__(self,other):
        new = type(self)(other*self.vector1,self.vector2.copy())
        return new
    def __mul__(self,other):
        new = type(self)(self.vector1.copy(),self.vector2*other)
        return new
    def __neg__(self):
        return -1*self
    def dyads(self):
        return [self]

    def dot(self,vector):
        return self.vector1*self.vector2.dot(vector)

    def rdot(self,vector):
        return vector.dot(self.vector1)*self.vector2

    def cross(self,vector):
        return type(self)(self.vector1.copy(),self.vector2.cross(vector))

    def rcross(self,vector):
        return type(self)(vector.cross(self.vector1),self.vector2.copy())

    def __add__(self,other):
        new = Dyadic(self.dyads()+other.dyads())
        return new

    def __radd__(self,other):
        new = Dyadic(other.dyads()+self.dyads())
        return new
        
    def __sub__(self,other):
        new = Dyadic(self.dyads() + [-dyad for dyad in other.dyads()])
        return new

    def __rsub__(self,other):
        new = Dyadic(other.dyads() + [-dyad for dyad in self.dyads()])
        return new
        
class Dyadic(object):
    def __init__(self,dyads):
        self._dyads = dyads
        
    def dyads(self):
        return self._dyads
    
    def __str__(self):
        return ''.join([str(dyad)+'+' for dyad in self._dyads[:-1]]+[str(self._dyads[-1])])

    def __repr__(self):
        return str(self)

    def __add__(self,other):
        new = Dyadic(self.dyads()+other.dyads())
        return new
    def __radd__(self,other):
        new = Dyadic(other.dyads()+self.dyads())
        return new

    def dot(self,vector):
        return sum([dyad.dot(vector) for dyad in self._dyads])

    def rdot(self,vector):
        return sum([vector.dot(dyad) for dyad in self._dyads])

    def cross(self,vector):
        return Dyadic([dyad.cross(vector) for dyad in self._dyads])

    def rcross(self,vector):
        return Dyadic([vector.cross(dyad) for dyad in self._dyads])

    def __rmul__(self,other):
        return Dyadic([other*dyad for dyad in self._dyads])

    def __mul__(self,other):
        return Dyadic([dyad*other for dyad in self._dyads])

    def __neg__(self):
        return -1*self
        
    def __sub__(self,other):
        new = Dyadic(self.dyads() + [-dyad for dyad in other.dyads()])
        return new

    def __rsub__(self,other):
        new = Dyadic(other.dyads() + [-dyad for dyad in self.dyads()])
        return new

    @classmethod
    def build(cls,frame,Ixx = 0,Iyy = 0, Izz = 0,Ixy = 0,Iyz=0,Izx=0):
        result = Ixx*Dyad(frame.x,frame.x)+Iyy*Dyad(frame.y,frame.y)+Izz*Dyad(frame.z,frame.z)+Ixy*Dyad(frame.x,frame.y)+Ixy*Dyad(frame.y,frame.x)+Iyz*Dyad(frame.y,frame.z)+Iyz*Dyad(frame.z,frame.y)+Izx*Dyad(frame.z,frame.x)+Izx*Dyad(frame.x,frame.z)
        return result

    @classmethod
    def unit(cls,frame):
        result = Dyad(frame.x,frame.x)+Dyad(frame.y,frame.y)+Dyad(frame.z,frame.z)
        return result
    
if __name__=='__main__':
    from pynamics.frame import Frame
    A = Frame('A')
    dyad = Dyad(A.x,A.x)
    d = dyad+dyad