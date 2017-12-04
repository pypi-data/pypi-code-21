import numpy as np
from .constants import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class Plane():
    def __init__(self, n, d):
        self.n = n
        self.d = d
        self.a, self.b, self.c = self.n

    def getZ(self, x, y):
        z = self.a*x + self.b*y - self.d
        if self.c == 0:
            return -z
        else:
            return -z/self.c

def findPlane(p1, p2, p3):
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)
    p1 = p1 - p3
    p2 = p2 - p3
    n = np.cross(p1, p2)
    d = n.dot(p3)
    return Plane(n, d)
