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

import logging
logger = logging.getLogger('pynamics.system')

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
        pynamics.addself(self,pynamics.systemname,override = True)

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

    def add_spring_force1(self,k,stretch,velocity):
        force = -k*stretch
        self.forces.append((force,velocity))
        self.springs.append((k,stretch))

    def add_spring_force2(self,k,stretch,v1,v2):
        force = -k*stretch
        self.forces.append((force,v1))
        self.forces.append((-force,v2))
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
                PE += F.dot(d)
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

    def getdynamics(self,q_speed = None):
        logger.info('getting dynamic equations')
        
        for particle in self.particles:
            particle.adddynamics()
        for body in self.bodies:
            body.adddynamics()

        q_d = q_speed or self.get_q(1)
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
        
    
    def solve_f_ma(self,f,ma,q_dd,inv_method = 'LU',constants = None):
        constants = constants or {}
        
        f = sympy.Matrix(f)
        ma = sympy.Matrix(ma)
        
        Ax_b = ma-f
        Ax_b = Ax_b.subs(constants)
        A = Ax_b.jacobian(q_dd)
        b = -Ax_b.subs(dict(list([(item,0) for item in q_dd])))

        var_dd = A.solve(b,method = inv_method)
        return var_dd
        
    def state_space_pre_invert(self,f,ma,inv_method = 'LU',constants = None,q_acceleration = None, q_speed = None, q_position = None):
        logger.info('solving a = f/m and creating function')
        '''pre-invert A matrix'''
        constants = constants or {}
        remaining_constant_keys = list(set(self.constants) - set(constants.keys()))

        q = q_position or self.get_q(0)
        q_d = q_speed or self.get_q(1)
        q_dd = q_acceleration or self.get_q(2)
        q_state = q+q_d
        

        var_dd =self.solve_f_ma(f,ma,q_dd,inv_method,constants)
        state_full = q_state+remaining_constant_keys+[self.t]
        
        f_var_dd = sympy.lambdify(state_full,var_dd)

        position_derivatives = [self.derivative(item) for item in q]
        indeces = [q_state.index(element) for element in position_derivatives]
        
        @static_vars(ii=0)
        def func(state,time,*args):
            if func.ii%1000==0:
                logger.info('integration at time {0:07.2f}'.format(time))
            func.ii+=1
            
            try:
                kwargs = args[0]
            except IndexError:
                kwargs = {}

            constant_values = [kwargs['constants'][item] for item in remaining_constant_keys]
            state_i_full = list(state)+constant_values+[time]
            
            x1 = [state[ii] for ii in indeces]
            x2 = numpy.array(f_var_dd(*(state_i_full))).flatten()
            x3 = numpy.r_[x1,x2]
            x4 = x3.flatten().tolist()
            
            return x4
        logger.info('done solving a = f/m and creating function')

        return func

    def state_space_post_invert(self,f,ma,eq_dd = None,eq_active = None,constants = None,q_acceleration = None, q_speed = None, q_position = None):
        '''invert A matrix each call'''
        logger.info('solving a = f/m and creating function')
        
        constants = constants or {}
        remaining_constant_keys = list(set(self.constants) - set(constants.keys()))
        
        q = q_position or self.get_q(0)
        q_d = q_speed or self.get_q(1)
        q_dd = q_acceleration or self.get_q(2)
        q_state = q+q_d
        
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

        m = len(q_dd)
    
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

        position_derivatives = [self.derivative(item) for item in q]
        indeces = [q_state.index(element) for element in position_derivatives]
    
        @static_vars(ii=0)
        def func(state,time,*args):
            if func.ii%1000==0:
                logger.info('integration at time {0:07.2f}'.format(time))
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
        logger.info('done solving a = f/m and creating function')
        return func        

    def state_space_post_invert2(self,f,ma,eq_dd,eq_d,eq,eq_active=None,constants = None,q_acceleration = None, q_speed = None, q_position = None):
        '''invert A matrix each call'''
        logger.info('solving a = f/m and creating function')
        
        constants = constants or {}
        remaining_constant_keys = list(set(self.constants) - set(constants.keys()))

        q = q_position or self.get_q(0)
        q_d = q_speed or self.get_q(1)
        q_dd = q_acceleration or self.get_q(2)
        q_state = q+q_d
        
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

        m = len(q_dd)

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

        position_derivatives = [self.derivative(item) for item in q]
        indeces = [q_state.index(element) for element in position_derivatives]
    
        @static_vars(ii=0)
        def func(state,time,*args):
            if func.ii%1000==0:
                logger.info('integration at time {0:07.2f}'.format(time))
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
        logger.info('done solving a = f/m and creating function')
        return func       

    @staticmethod
    def assembleconstrained(eq_dyn,eq_con,q_dyn,q_con,method='LU'):
        logger.info('solving constrained')
        AC1x_b1 = sympy.Matrix(eq_dyn)
        C2x_b2 = sympy.Matrix(eq_con)
        logger.info('solving Ax-b')
        
        q_dyn = sympy.Matrix(q_dyn)
        q_con = sympy.Matrix(q_con)
        x = q_dyn.col_join(q_con)
        logger.info('finding x, l')
        
        MASS = AC1x_b1.jacobian(q_dyn)
        C1 = AC1x_b1.jacobian(q_con)
        C2 = C2x_b2.jacobian(x)
        AA = sympy.Matrix.col_join(sympy.Matrix.row_join(MASS,C1),C2)
        logger.info('finding A,C1,C2')
        
        b1 = -AC1x_b1.subs(zip(x.T.tolist()[0],[0 for item in x]))
        b2 = -C2x_b2.subs(zip(x.T.tolist()[0],[0 for item in x]))
        b = b1.col_join(b2)
        logger.info('finished solving constrained')
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
                        