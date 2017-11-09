# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes
Email: danaukes<at>gmail.com
Please see LICENSE for full license.
"""

import sympy
import pynamics
import numpy
import scipy

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate
    
class System(object):
    _z = 0
    def __init__(self):
        self.derivatives = {}
        self.constants = []
        self.constant_values = {}
        self.forces = []
        self.effectiveforces = []
#        self.momentum = []
#        self.KE = sympy.Number(0)
        self.bodies = []
        self.particles = []
        self.q = {}
        self.replacements = {}
        self.springs = []
        self.t = sympy.Symbol('t')
        self.ini = {}
        self.error_tolerance = 1e-16
        pynamics.addself(self,pynamics.systemname)

    def set_ini(self,name,val):
        self.ini[name]=val

    def add_q(self,q,ii):
        if ii in self.q:
            self.q[ii].append(q)
        else:
            self.q[ii] = [q]

    def get_q(self,ii):
        if ii in self.q:
            return self.q[ii]
        else:
            return []
        
    def get_state_variables(self):
        state_var = self.get_q(0)+self.get_q(1)
        return state_var
    
    def set_newtonian(self,frame):
        self.newtonian = frame
        
    def generatez(self,number):
        z=sympy.Symbol('z'+str(self._z))
        self.replacements[z]=number
        self._z+=1
        return z

    def addforce(self,force,velocity):
        self.forces.append((force,velocity))

    def add_spring_force(self,k,stretch,velocity):
        force = -k*stretch
        self.forces.append((force,velocity))
        self.springs.append((k,stretch))

    def addeffectiveforce(self,effectiveforce,velocity):
        self.effectiveforces.append((effectiveforce,velocity))

#    def addmomentum(self,momentum,velocity):
#        self.momentum.append((momentum,velocity))

    def get_KE(self):
        KE = sympy.Number(0)
        for item in self.particles+self.bodies:
            KE+= item.KE
        return KE
#    def addKE(self,KE):
#        self.KE+=KE

    def add_derivative(self,expression,variable):
        self.derivatives[expression]=variable

    def add_constant(self,constant):
        self.constants.append(constant)

    def add_constant_value(self,constant,value):
        self.constant_values[constant]=value

    def getPEGravity(self,point):
        PE = pynamics.ZERO
        for body in self.bodies+self.particles:
            if body.gravityvector is not None:
                d = body.pCM - point
                F = body.forcegravity
                PE +=F.dot(d)
        return PE

    def getPESprings(self):
        PE = pynamics.ZERO
        for k,stretch in self.springs:
            PE+=.5*k*stretch.dot(stretch)
        return PE
        
    def addforcegravity(self,gravityvector):
        for body in self.bodies:
            body.addforcegravity(gravityvector)
        for particle in self.particles:
            particle.addforcegravity(gravityvector)

    def getdynamics(self):
        for particle in self.particles:
            particle.adddynamics()
        for body in self.bodies:
            body.adddynamics()

        q_d = self.get_q(1)
        generalizedforce=self.generalize(self.forces,q_d)
        generalizedeffectiveforce=self.generalize(self.effectiveforces,q_d)
        return generalizedforce,generalizedeffectiveforce

    def generalize(self,list1,q_d):
        generalized=[]
        for speed in q_d:
            new = pynamics.ZERO
            for expression,velocity in list1:
                new+=expression.dot(velocity.diff_partial_local(speed))
            generalized.append(new)
        return generalized
        
# =============================================================================
# TODO: fix this!  It doesn't produce the right answer now.    
#     def state_space_pre_invert(self,f,ma,inv_method = 'LU',auto_z= False):
#         '''pre-invert A matrix'''
#         
#         q_state = self.get_state_variables()
# 
#         q_d = self.get_q(1)
#         q_dd = self.get_q(2)
#         
#         f = sympy.Matrix(f)
#         ma = sympy.Matrix(ma)
#         
#         Ax_b = ma-f
#         Ax_b = Ax_b.subs(self.constant_values)
#         A = Ax_b.jacobian(q_dd)
#         b = -Ax_b.subs(dict(list([(item,0) for item in q_dd])))
# 
#         if auto_z:
#             def func1(x):
#                 if x!=pynamics.ZERO:
#                     return self.generatez(x)
#                 else:
#                     return x
#             AA = A.applyfunc(func1)
#             AA_inv = AA.inv(method = inv_method)
#             keys = self.replacements.keys()+[self.t]
# 
#             fAA_inv = sympy.lambdify(keys,AA_inv)
#             A_inv = fAA_inv(*[self.replacements[key] for key in keys])
# 
#         else:
#             A_inv = A.inv(method=inv_method)
#         var_dd = A_inv*b 
#         
#         functions = [sympy.lambdify(q_state,rhs) for rhs in var_dd]
#         indeces = [q_state.index(element) for element in q_d]
#         
#         @static_vars(ii=0)
#         def func(state,time):
#             if func.ii%100==0:
#                 print(time)
#             func.ii+=1
#             
#             x1 = [state[ii] for ii in indeces]
#             x2 = [f(*(state+[time])) for f in functions]
#             x3 = numpy.r_[x1,x2]
#             x4 = x3.flatten().tolist()
# 
#             return x4
# 
#         return func
# =============================================================================

    def state_space_post_invert(self,f,ma,eq_dd = None,eq_active = None,constants = None):
        '''invert A matrix each call'''
        constants = constants or {}
        remaining_constant_keys = list(set(self.constants) - set(constants.keys()))
        
        q_state = self.get_state_variables()

        q_d = self.get_q(1)
        q_dd = self.get_q(2)

        if not not eq_dd:
            eq_active = eq_active or [1]*len(eq_dd)
        else:
            eq_active = eq_active or []

        eq_active = sympy.Matrix(eq_active)
        eq_dd = sympy.Matrix(eq_dd or [])

        f = sympy.Matrix(f)
        ma = sympy.Matrix(ma)
        
        Ax_b = ma-f
        if not not constants:
            Ax_b = Ax_b.subs(constants)
            eq_active = eq_active.subs(constants)
            eq_dd = eq_dd.subs(constants)
            
        A = Ax_b.jacobian(q_dd)
        b = -Ax_b.subs(dict(list([(item,0) for item in q_dd])))

        m = len(q_d)
    
        if not eq_dd:
            A_full = A
            b_full = b
            n=0
        else:
            J = eq_dd.jacobian(q_dd)
            c = -eq_dd.subs(dict(list([(item,0) for item in q_dd])))

            n = len(eq_dd)
            A_full = sympy.zeros(m+n)   
            A_full[:m,:m] = A
            A_full[m:,:m] = J
            A_full[:m,m:] = J.T
        
            b_full = sympy.zeros(m+n,1)
            b_full[:m,0]=b
            b_full[m:,0]=c

           
        state_full = q_state+remaining_constant_keys+[self.t]

        fA = sympy.lambdify(state_full,A_full)
        fb = sympy.lambdify(state_full,b_full)
        factive = sympy.lambdify(state_full,eq_active)

        indeces = [q_state.index(element) for element in q_d]
    
        @static_vars(ii=0)
        def func(state,time,*args):
            if func.ii%1000==0:
                print(time)
            func.ii+=1
            
            try:
                kwargs = args[0]
            except IndexError:
                kwargs = {}

            constant_values = [kwargs['constants'][item] for item in remaining_constant_keys]
            state_i_full = list(state)+constant_values+[time]
                
            Ai = numpy.array(fA(*state_i_full),dtype=float)
            bi = numpy.array(fb(*state_i_full),dtype=float)
            
            active = numpy.array(m*[1]+factive(*state_i_full).flatten().tolist())
            f1 = numpy.eye(m+n)             
            f2 = f1[(active>self.error_tolerance).nonzero()[0],:]
#            
            Ai=(f2.dot(Ai)).dot(f2.T)
            bi=f2.dot(bi)
            
            x1 = [state[ii] for ii in indeces]
            x2 = numpy.array(scipy.linalg.solve(Ai,bi)).flatten()
            x3 = numpy.r_[x1,x2[:m]]
            x4 = x3.flatten().tolist()
            
            return x4
            
        return func        

    def state_space_post_invert2(self,f,ma,eq_dd,eq_d,eq,eq_active=None,constants = None):
        '''invert A matrix each call'''
        constants = constants or {}
        remaining_constant_keys = list(set(self.constants) - set(constants.keys()))

        q_state = self.get_state_variables()

        q_d = self.get_q(1)
        q_dd = self.get_q(2)

        if not not eq_dd:
            eq_active = eq_active or [1]*len(eq_dd)
        else:
            eq_active = eq_active or []
        eq_active = sympy.Matrix(eq_active)
    
        eq = sympy.Matrix(eq or [])
        eq_d = sympy.Matrix(eq_d or [])
        eq_dd = sympy.Matrix(eq_dd or [])

        f = sympy.Matrix(f)
        ma = sympy.Matrix(ma)
        
        Ax_b = ma-f
        if not not constants:
            Ax_b = Ax_b.subs(constants)
            eq_active = eq_active.subs(constants)
            eq = eq.subs(constants)
            eq_d = eq_d.subs(constants)
            eq_dd = eq_dd.subs(constants)
            
        A = Ax_b.jacobian(q_dd)
        b = -Ax_b.subs(dict(list([(item,0) for item in q_dd])))

        m = len(q_d)

        if not eq_dd:
            A_full = A
            b_full = b
            n=0
        else:
            J = eq_dd.jacobian(q_dd)
            c = -eq_dd.subs(dict(list([(item,0) for item in q_dd])))

            n = len(eq_dd)
            A_full = sympy.zeros(m+n)   
            A_full[:m,:m] = A
            A_full[m:,:m] = J
            A_full[:m,m:] = J.T
        
            b_full = sympy.zeros(m+n,1)
            b_full[:m,0]=b
            b_full[m:,0]=c

            
        state_full = q_state+remaining_constant_keys+[self.t]

        fA = sympy.lambdify(state_full,A_full)
        fb = sympy.lambdify(state_full,b_full)
        feq = sympy.lambdify(state_full,eq)
        feq_d = sympy.lambdify(state_full,eq_d)
        factive = sympy.lambdify(state_full,eq_active)

        indeces = [q_state.index(element) for element in q_d]
    
        @static_vars(ii=0)
        def func(state,time,*args):
            if func.ii%1000==0:
                print(time)
            func.ii+=1
            
            try:
                kwargs = args[0]
            except IndexError:
                kwargs = {}

            alpha = kwargs['alpha']
            beta = kwargs['beta']

            constant_values = [kwargs['constants'][item] for item in remaining_constant_keys]
            state_i_full = list(state)+constant_values+[time]
                
            Ai = numpy.array(fA(*state_i_full),dtype=float)
            bi = numpy.array(fb(*state_i_full),dtype=float)
            eqi = numpy.array(feq(*state_i_full),dtype = float)
            eq_di = numpy.array(feq_d(*state_i_full),dtype = float)
            
            bi[m:] = bi[m:]-2*alpha*eq_di-beta**2*eqi

            active = numpy.array(m*[1]+factive(*state_i_full).flatten().tolist())
            f1 = numpy.eye(m+n)             
            f2 = f1[(active>self.error_tolerance).nonzero()[0],:]
            
            Ai=(f2.dot(Ai)).dot(f2.T)
            bi=f2.dot(bi)
            
            x1 = [state[ii] for ii in indeces]
            x2 = numpy.array(scipy.linalg.solve(Ai,bi)).flatten()
            x3 = numpy.r_[x1,x2[:m]]
            x4 = x3.flatten().tolist()
            return x4
        return func       

    @staticmethod
    def assembleconstrained(eq_dyn,eq_con,q_dyn,q_con,method='LU'):
        AC1x_b1 = sympy.Matrix(eq_dyn)
        C2x_b2 = sympy.Matrix(eq_con)
        print('Ax-b')
        
        q_dyn = sympy.Matrix(q_dyn)
        q_con = sympy.Matrix(q_con)
        x = q_dyn.col_join(q_con)
        print('x,l')
        
        MASS = AC1x_b1.jacobian(q_dyn)
        C1 = AC1x_b1.jacobian(q_con)
        C2 = C2x_b2.jacobian(x)
        AA = sympy.Matrix.col_join(sympy.Matrix.row_join(MASS,C1),C2)
        print('A,C1,C2')
        
        b1 = -AC1x_b1.subs(zip(x.T.tolist()[0],[0 for item in x]))
        b2 = -C2x_b2.subs(zip(x.T.tolist()[0],[0 for item in x]))
        b = b1.col_join(b2)
        return AA,b,x    
        
    @classmethod
    def solveconstraineddynamics(cls,eq_dyn,eq_con,q_dyn,q_con,method='LU'):
        AA,b,x = cls.assembleconstrained(eq_dyn,eq_con,q_dyn,q_con,method=method)
        AA_inv = AA.inv(method = method)
        xx = AA_inv*b
        x_dyn = xx[0:len(q_dyn),:]
        x_con = xx[len(q_dyn):,:]
        return x_dyn,x_con    

    def derivative(self,expression):
        for ii,a in enumerate(self.derivatives.keys()):
            if ii==0:
                result = expression.diff(a)*self.derivatives[a]
            else:
                result += expression.diff(a)*self.derivatives[a]
        return result

    def get_ini(self):
        return [self.ini[item] for item in self.get_state_variables()]
                        