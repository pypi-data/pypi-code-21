'''
Created on Nov 12, 2014

@author: arne
'''

# preparing for Python 3 port
from __future__ import division, print_function
from __future__ import absolute_import
#from __future__ import unicode_literals

HAVE_SYMPY = False
try:
    import sympy
    if int(sympy.__version__.split('.')[1]) >= 7 and int(sympy.__version__.split('.')[2]) >= 4:
        HAVE_SYMPY = True
    else:
        del sympy
except ImportError:
    HAVE_SYMPY = False

import os, time
import numpy
from cbmpy import CBWrite
from cbmpy.CBConfig import __CBCONFIG__ as __CBCONFIG__
__DEBUG__ = __CBCONFIG__['DEBUG']
__version__ = __CBCONFIG__['VERSION']


HAVE_GLPK = False
GLPK_SOLUTION_STATUS = None

try:
    import glpk
    lp = glpk.LPX()
    HAVE_GLPK = True
    del lp
except:
    raise ImportError

# configuration options for GLPK
GLPK_CFG = {'simplex' : {'meth' : glpk.LPX.PRIMAL,
                       #'meth' : glpk.LPX.DUAL,
                       #'meth' : glpk.LPX.DUALP,
                       'tol_bnd' : 1.0e-6,
                       'tol_dj'  : 1.0e-6,
                       'tol_piv' : 1.0e-10
                       }
          }

GLPK_STATUS = {
    1 : 'LPS_UNDEF',
    2 : 'LPS_FEAS',
    3 : 'LPS_INFEAS',
    4 : 'LPS_NOFEAS',
    5 : 'LPS_OPT',
    6 : 'LPS_UNBND'}

GLPK_STATUS2 = {
    'opt' : 'LPS_OPT',
    'undef' : 'LPS_UNDEF',
    'feas' : 'LPS_FEAS',
    'infeas' : 'LPS_INFEAS',
    'nofeas' : 'LPS_NOFEAS',
    'unbnd' : 'LPS_UNBND'}


GLPK_SILENT_MODE = True
GLPK_INFINITY = 1.0e9


from .CBSolver import SolverFactory, Solver

class GLPKSolver(Solver):
    
    def __init__(self):
        """
        Create a GLPK LP in memory.
        - *fba* an FBA object
        - *fname* optional filename if defined writes out the constructed lp
    
        """
        # initialize empty lp
        self.lp = glpk.LPX()
        self.varMap = {}
        self.conMap = {}
        
    def copy(self):
        mps_filename = '_{}_.mps'.format(str(time.time()).split('.')[0])
        self.lp.write(mps=mps_filename)
        copylp = GLPKSolver()
        copylp.lp = glpk.LPX(mps=mps_filename)
        copylp.varMap = self.varMap.copy()
        copylp.conMap = self.conMap.copy()
        os.remove(mps_filename)
        return copylp
    
    def solve(self, method='s'):
        """
        Solve the LP and create a status attribute with the solution status
    
         - *method* [default='s'] 's' = simplex, 'i' = interior, 'e' = exact
    
        GLPK solver options can be set in the dictionary GLPK_CFG
        """
        if method == 'i':
            self.lp.interior()
        elif method == 'e':
            self.lp.exact()
        else:
            self.lp.simplex(**GLPK_CFG['simplex'])
    
    
        global GLPK_SOLUTION_STATUS
        GLPK_SOLUTION_STATUS = self.getSolutionStatus()
        
        if GLPK_SOLUTION_STATUS in ['LPS_UNDEF', 'LPS_FEAS', 'LPS_INFEAS', 'LPS_NOFEAS', 'LPS_OPT', 'LPS_UNBND']:
            if not GLPK_SILENT_MODE:
                print('Solution status returned as: {}'.format(GLPK_SOLUTION_STATUS))
                print("Objective value = " , self.lp.obj.value)
            return GLPK_SOLUTION_STATUS
        else:
            print("INFO: No solution available ({})".format(GLPK_SOLUTION_STATUS))
            return None
        
    def getSolutionStatus(self):
        """
        Returns one of:
    
         - *LPS_OPT*: solution is optimal;
         - *LPS_FEAS*: solution is feasible;
         - *LPS_INFEAS*: solution is infeasible;
         - *LPS_NOFEAS*: problem has no feasible solution;
         - *LPS_UNBND*: problem has unbounded solution;
         - *LPS_UNDEF*: solution is undefined.
    
        """
        return GLPK_STATUS2[self.lp.status]
    
    def isDualFeasible(self):
        """ checks if problem has been solved to dual feasibility """
        return self.lp.status_dual == 'feas'
    
    def getSolution(self):
        fba_sol = {}
        try:
            for n in self.lp.cols:
                fba_sol.update({n.name : n.value})
        except Exception as ex:
            print(ex)
            print('WARNING: No solution to get')
            fba_sol = {}
        return fba_sol
    
    def getReducedCosts(self, scaled=False):
        """
        Extract ReducedCosts from LP and return as a dictionary 'Rid' : reduced cost
    
         - *c* a GLPK LP object
         - *scaled* scale the reduced cost by the optimal flux value
    
        """
        s_name = []
        r_costs = []
        s_val = []
    
        for c_ in self.lp.cols:
            s_name.append(c_.name)
            r_costs.append(c_.dual)
            s_val.append(c_.value)
        objf_val = self.lp.obj.value
        output = {}
        for v in range(len(s_name)):
            if scaled:
                try:
                    r_val = r_costs[v]*s_val[v]/objf_val
                except:
                    r_val = float('nan')
            else:
                r_val = r_costs[v]
            output.update({s_name[v] : r_val})
        del s_name, r_costs, s_val
        return output
    
    def getObjectiveValue(self):
        """ returns current objective value (typically valid after solve) """
        return self.lp.obj.value
    
    def getObjectiveId(self):
        """ returns the name of the current objective function """
        return self.lp.obj.name
    
    def getObjectiveCoef(self, obj=None):
        if obj == None:
            obj = {}
            for cidx_ in range(len(self.lp.cols)):
                name = self.lp.cols[cidx_].name
                obj[name] = self.lp.obj[cidx_]
        else:
            for name in obj.keys():
                cidx = self.varMap[name]
                obj[name] = self.lp.obj[cidx]
        return obj
        
    def addLinearConstraint(self, name, coef, rhs, sense):
        """ adds an additional linear constraint.
        
        Warning: Adding constraints manually might be much slower than creating
        the whole model from a metabolic network at once
        """
        baseRows = len(self.lp.rows)
        self.lp.rows.add(1)
    
        # name and coefficients
        newCon = []
        for colname, val in coef.items():
            cidx = self.varMap[colname]
            newCon.append((cidx, val))
#            print(newCon[-1])
        self.lp.rows[baseRows].name = name
        self.lp.rows[baseRows].matrix = newCon
        self.conMap[name] = baseRows
    
        # sense and rhs
        if sense in ['<=','<','L']:
            self.lp.rows[baseRows].bounds = None, rhs
        elif sense in ['>=','>','G']:
            self.lp.rows[baseRows].bounds = rhs, None
        elif sense in ['=','E']:
            self.lp.rows[baseRows].bounds = rhs
        else:
            raise RuntimeError('INFO: invalid operator: %s' % sense)
        
    def addVariables(self, names, lb=None, ub=None, obj=None):
        """ adds additional variables.
        
        - *names* list of variable names
        - *lb* list of lower bounds
        - *ub* list of upper bounds
        - *obj* list of objective values
        
        if only one variable should be added, the lists can also be replaced by
        plain values
        
        Warning: Adding constraints manually might be much slower than creating
        the whole model from a metabolic network at once
        """
        
        basecols = len(self.lp.cols)
        if isinstance(names, list):
            self.lp.cols.add(len(names))
            if lb == None:
                lb = len(names)*[None]
            if ub == None:
                ub = len(names)*[None]
            for v_ in range(len(names)):
                self.lp.cols[basecols+v_].name = names[v_]
                self.lp.cols[basecols+v_].bounds = lb[v_], ub[v_]
                self.varMap[names[v_]] = basecols+v_
                if obj != None:
                    self.lp.obj[basecols+v_] = obj[v_]
        else:
            self.lp.cols.add(1)
            self.lp.cols[basecols].name = names
            self.lp.cols[basecols].bounds = lb, ub
            self.varMap[names] = basecols
            if obj != None:
                self.lp.obj[basecols] = obj

    
    def setBounds(self, bounds):
        """ sets lower bounds of given variables
        
        bounds should be a dictionary mapping variable names to the new bounds
        the new bounds for each variable are given by the pair (lb, ub)
        """
        for colName, colBound in bounds.items():
            cidx = self.varMap[colName]
            self.lp.cols[cidx].bounds = colBound
            
    def getBounds(self, bounds=None):
        """ fetches the bounds of the given variables 
        
        - bounds: dictionary that has variable names as keys, the bounds will
            be written in the corresponding values.
            If bounds is None, a new dictionary for all variables is created
        """
        if bounds == None:
            bounds = {}
            for cidx_ in range(len(self.lp.cols)):
                name = self.lp.cols[cidx_].name
                bounds[name] = self.lp.cols[cidx_].bounds
        else:
            for name in bounds.keys():
                cidx = self.varMap[name]
                bounds[name] = self.lp.cols[cidx].bounds
        return bounds
    
    def setLowerBounds(self, bounds):
        """ sets lower bounds of given variables
        
        bounds should be a dictionary mapping variable names to the new bounds
        """
        for colName, colBound in bounds.items():
            cidx = self.varMap[colName]
            oldlb, oldub = self.lp.cols[cidx].bounds
            self.lp.cols[cidx].bounds = colBound, oldub
    
    def setUpperBounds(self, bounds):
        """ sets upper bounds of given variables
        
        bounds should be a dictionary mapping variable names to the new bounds
        """
        for colName, colBound in bounds.items():
            cidx = self.varMap[colName]
            oldlb, oldub = self.lp.cols[cidx].bounds
            self.lp.cols[cidx].bounds = oldlb, colBound
    
    def setObjective(self, name='obj', coef=None, sense='maximize', reset=True):
        """ sets the objective
        
        - *name* name of the objective
        - *coef* dictionary mapping variable names to the new coefficients
        - *sense* objective sense, can be one of 'min' or 'max'
        - *reset* if all other objective coefficients should be reset
        """
        sense = sense.lower()
        if sense == 'max': sense = 'maximize'
        if sense == 'min': sense = 'minimize'
        if sense in ['maximise', 'minimise']:
            sense = sense.replace('se','ze')
        assert sense in ['maximize', 'minimize'], "\nsense must be ['maximize', 'minimize'] not %s" % sense
    
        if coef != None:
            if reset:
                for cidx_ in range(len(self.lp.cols)):
                    name = self.lp.cols[cidx_].name
                    if coef.has_key(name):
                        self.lp.obj[cidx_] = coef[name]
                    else:
                        self.lp.obj[cidx_] = 0.0
            
            else:
                for name, val in coef.items():
                    idx = self.varMap[name]
                    self.lp.obj[idx] = val
        elif reset:
            for cidx_ in range(len(self.lp.cols)):
                    name = self.lp.cols[cidx_].name
                    self.lp.obj[cidx_] = 0.0
    
        self.lp.obj.name = name
    
        if sense == 'minimize':
            self.lp.obj.maximize = False
            if __DEBUG__: print('Set minimizing')
        else:
            self.lp.obj.maximize = True
            if __DEBUG__: print('Set maximizing')

    
    def setRHS(self, rhs):
        """ sets right-hand sides of given constraints
        
        rhs should be a dictionary mapping constraint names to the new rhs
        """
        for rowName, rowRHS in rhs.items():
            ridx = self.conMap[rowName]
            oldlhs, oldrhs = self.lp.rows[ridx].bounds
            if oldlhs != None:
                if oldrhs != None:
                    self.lp.rows[ridx].bounds = rowRHS
                else:
                    self.lp.rows[ridx].bounds = (rowRHS, None)  
            else:
                self.lp.rows[ridx].bounds = (None, rowRHS)
        
    def setSense(self, sense):
        """ sets the sense of given constraints
        
        sense should be a dictionary mapping constraint names to the new sense
        """
        for rowName, rowSense in sense.items():
            ridx = self.conMap[rowName]
            oldlhs, oldrhs = self.lp.rows[ridx].bounds
            if oldlhs != None:
                if oldrhs != None:
                    assert oldlhs == oldrhs, 'we can not deal with this feature'
                old = oldlhs
            else:
                old = oldrhs
            # sense and rhs
            if rowSense in ['<=','<','L']:
                self.lp.rows[ridx].bounds = None, old
            elif rowSense in ['>=','>','G']:
                self.lp.rows[ridx].bounds = old, None
            elif rowSense in ['=','E']:
                self.lp.rows[ridx].bounds = old
            else:
                raise RuntimeError('INFO: invalid operator: %s' % sense)

    def deleteVariables(self, variables):
        """ deletes the variables with specified names """
        pass
    
    def deleteConstraints(self, cons):
        """ delete constraints with specified names """
        pass

    def write(self, filename, title=None, Dir=None):
        """
        Write out a GLPK model as an LP format file
    
        """
        if Dir != None:
            filename = os.path.join(Dir, filename)
        #if title != None:
            #c.set_problem_name(title)
        #c.write(filename+'.lp', filetype='lp')
        self.lp.write(cpxlp=filename+'.lp')
        print('LP output as {}'.format(filename+'.lp'))


class GLPKFactory(SolverFactory):
    
    def createEmpty(self):
        """ creates a new empty solver instance """
        return GLPKSolver()
    
    def create(self, fba=None, fname=None):
        """creates a new solver instance.
        
        If an fba instance (metabolic network) is given, the solver is setup
        to solve the fba instance. 
        Otherwise an empty problem is returned for manual setup.
        
        - *fba* optional FBA object
        - *fname* optional filename if defined writes out the constructed lp (if fba is given)
        """
        if fba == None:
            return self.createEmpty()
        else:
            _Stime = time.time()
    
            solver = GLPKSolver()
            # we want to work directly on the glpk instance, so fetch it!
            lp = solver.lp
            lp.name = fba.getPid()
            lp.cols.add(len(fba.N.col))
        
        
            if HAVE_SYMPY and fba.N.__array_type__ == sympy.MutableDenseMatrix:
                print('INFO: GLPK requires floating point, converting N')
                Nmat = numpy.array(fba.N.array).astype('float')
                RHSmat = numpy.array(fba.N.RHS).astype('float')
                if fba.CM != None:
                    CMmat = numpy.array(fba.CM.array).astype('float')
                    CMrhs = numpy.array(fba.CM.RHS).astype('float')
            else:
                Nmat = fba.N.array
                RHSmat = fba.N.RHS
                if fba.CM != None:
                    CMmat = fba.CM.array
                    CMrhs = fba.CM.RHS
        
            varMap = {}
            for n_ in range(Nmat.shape[1]):
                varMap[fba.N.col[n_]] = n_
                lp.cols[n_].name = fba.N.col[n_]
        
            #print varMap
        
            # define objective
            osense = fba.getActiveObjective().operation.lower()
            if osense in ['minimize', 'minimise', 'min']:
                lp.obj.maximize = False
            elif osense in ['maximize', 'maximise', 'max']:
                lp.obj.maximize = True
            else:
                raise RuntimeError('\n%s - is not a valid objective operation' % osense)
            lp.obj.name = fba.getActiveObjective().getPid()
            for fo_ in fba.getActiveObjective().fluxObjectives:
                lp.obj[varMap[fo_.reaction]] = fo_.coefficient
        
            # create N constraints
            lp.rows.add(Nmat.shape[0])
            
            conMap = {}
            for n_ in range(Nmat.shape[0]):
                conMap[fba.N.row[n_]] = n_
                #lp.rows[n_].name = fba.N.row[n_]
        
            #tnew = time.time()
            for r_ in range(Nmat.shape[0]):
                # name and coefficients
                newCon = []
                for c_ in range(Nmat.shape[1]):
                    newCon.append((c_, Nmat[r_,c_]))
                lp.rows[r_].name = fba.N.row[r_]
                lp.rows[r_].matrix = newCon
        
                # sense and rhs
                rhs = RHSmat[r_]
                if fba.N.operators[r_] in ['<=','<','L']:
                    lp.rows[r_].bounds = None, rhs
                elif fba.N.operators[r_] in ['>=','>','G']:
                    lp.rows[r_].bounds = rhs, None
                elif fba.N.operators[r_] in ['=','E']:
                    lp.rows[r_].bounds = rhs
                else:
                    raise RuntimeError('INFO: invalid operator: %s' % fba.N.operators[r_])
        
            # add user defined constraints
            if fba.CM != None:
                baseRows = len(lp.rows)
                lp.rows.add(CMmat.shape[0])
                for r_ in range(CMmat.shape[0]):
                    # name and coefficients
                    newCon = []
                    for c_ in range(CMmat.shape[1]):
                        newCon.append((c_, CMmat[r_, c_]))
                    lp.rows[baseRows+r_].name = fba.CM.row[r_]
                    lp.rows[baseRows+r_].matrix = newCon
                    conMap[fba.CM.row[r_]] = Nmat.shape[0] + r_
        
                    # sense and rhs
                    rhs = CMrhs[r_]
                    if fba.CM.operators[r_] in ['<=','<','L']:
                        lp.rows[baseRows+r_].bounds = None, rhs
                    elif fba.CM.operators[r_] in ['>=','>','G']:
                        lp.rows[baseRows+r_].bounds = rhs, None
                    elif fba.CM.operators[r_] in ['=','E']:
                        lp.rows[baseRows+r_].bounds = rhs
                    else:
                        raise RuntimeError('INFO: invalid operator: %s' % fba.N.operators[r_])
        
            # add bounds
            for r_ in fba.reactions:
                lb = ub = None
                lb = fba.getReactionLowerBound(r_.getPid())
                ub = fba.getReactionUpperBound(r_.getPid())
        
                if lb in ['Infinity', 'inf', 'Inf', 'infinity']:
                    lb = GLPK_INFINITY
                elif lb in ['-Infinity', '-inf', '-Inf', '-infinity', None]:
                    lb = -GLPK_INFINITY
                elif numpy.isinf(lb):
                    if lb < 0.0:
                        lb = -GLPK_INFINITY
                    else:
                        lb = GLPK_INFINITY
                if ub in ['Infinity', 'inf', 'Inf', 'infinity', None]:
                    ub = GLPK_INFINITY
                elif ub in ['-Infinity', '-inf', '-Inf', '-infinity']:
                    ub = -GLPK_INFINITY
                elif numpy.isinf(ub):
                    if ub < 0.0:
                        ub = -GLPK_INFINITY
                    else:
                        ub = GLPK_INFINITY
        
                if ub != GLPK_INFINITY and lb != -GLPK_INFINITY and ub == lb:
                    lp.cols[varMap[r_.getPid()]].bounds = lb
                elif ub != GLPK_INFINITY and lb != -GLPK_INFINITY:
                    lp.cols[varMap[r_.getPid()]].bounds = lb, ub
                elif ub != GLPK_INFINITY:
                    lp.cols[varMap[r_.getPid()]].bounds = None, ub
                elif lb != -GLPK_INFINITY:
                    lp.cols[varMap[r_.getPid()]].bounds = lb, None
                else:
                    lp.cols[varMap[r_.getPid()]].bounds = None
        
            solver.varMap = varMap
            solver.conMap = conMap
            #print('\ngplk_constructLPfromFBA time: {}\n'.format(time.time() - _Stime))
            if fname != None:
                lp.write(cpxlp=fname+'.lp')
            return solver
    
        
    
    def fluxVariabilityAnalysis(self, fba, selected_reactions=None, pre_opt=True, objF2constr=True, rhs_sense='lower', optPercentage=100.0, work_dir=None, quiet=True, debug=False, oldlpgen=False, markupmodel=True, default_on_fail=False, roundoff_span=10):
        """
        Perform a flux variability analysis on an fba model:
    
         - *fba* an FBA model object
         - *selected reactions* [default=None] means use all reactions otherwise use the reactions listed here
         - *pre_opt* [default=True] attempt to presolve the FBA and report its results in the ouput, if this is disabled and *objF2constr* is True then the vid/value of the current active objective is used
         - *tol*  [default=None] do not floor/ceiling the objective function constraint, otherwise round of to *tol*
         - *rhs_sense* [default='lower'] means objC >= objVal the inequality to use for the objective constraint can also be *upper* or *equal*
         - *optPercentage* [default=100.0] means the percentage optimal value to use for the RHS of the objective constraint: optimal_value*(optPercentage/100.0)
         - *work_dir* [default=None] the FVA working directory for temporary files default = cwd+fva
         - *debug* [default=False] if True write out all the intermediate FVA LP's into work_dir
         - *quiet* [default=False] if enabled supress CPLEX output
         - *objF2constr* [default=True] add the model objective function as a constraint using rhs_sense etc. If
           this is True with pre_opt=False then the id/value of the active objective is used to form the constraint
         - *markupmodel* [default=True] add the values returned by the fva to the reaction.fva_min and reaction.fva_max
         - *default_on_fail* [default=False] if *pre_opt* is enabled replace a failed minimum/maximum with the solution value
         - *roundoff_span* [default=10] number of digits is round off (not individual min/max values)
    
        Returns an array with columns Reaction, Reduced Costs, Variability Min, Variability Max, abs(Max-Min), MinStatus, MaxStatus and a list containing the row names.
    
        """
        if work_dir == None:
            work_dir = os.getcwd()
        else:
            assert os.path.exists(work_dir), '\nWhat did you think would happen now!'
        if debug:
            debug_dir = os.path.join(work_dir,'DEBUG')
            if not os.path.exists(debug_dir):
                os.mkdir(debug_dir)
        s2time = time.time()
        # generate a presolution
        
        
        pre_sol = pre_oid = pre_oval = None
        REDUCED_COSTS = {}
        cpx, pre_sol, pre_oid, pre_oval, OPTIMAL_PRESOLUTION, REDUCED_COSTS = self.presolve(fba, pre_opt, objF2constr, quiet=quiet, oldlpgen=oldlpgen)
    
        # if required add the objective function as a constraint
        if objF2constr:
            cpx.setObjectiveAsConstraint(rhs_sense, pre_oval, optPercentage)
        if debug:
            cpx.write(cpxlp=os.path.join(debug_dir, 'FVA_base.lp'))
    
        # do the FVA
        NUM_FLX = len(fba.reactions)
        print('Total number of reactions: {}'.format(NUM_FLX))
        if selected_reactions != None:
            rids = fba.getReactionIds()
            for r in selected_reactions:
                assert r in rids, "\n%s is not a valid reaction name" % r
        else:
            selected_reactions = fba.getReactionIds()
        NUM_FLX = len(selected_reactions)
        print('Number of user selected variables: {}'.format(NUM_FLX))
        try:
            OUTPUT_ARRAY = numpy.zeros((NUM_FLX, 7), numpy.double)
        except AttributeError:
            OUTPUT_ARRAY = numpy.zeros((NUM_FLX, 7))
        OUTPUT_NAMES = []
        cntr = 0
        tcnt = 0
        # this is a memory hack --> prevents solver going berserk
        mcntr = 0
        mcntr_cntrl = 3
        mps_filename = '_{}_.mps'.format(str(time.time()).split('.')[0])
        cpx.lp.write(mps=mps_filename)
        for Ridx in range(NUM_FLX):
            R = selected_reactions[Ridx]
            OUTPUT_NAMES.append(R)
            max_error_iter = 1
            GOMIN = True
            gomin_cntr = 0
            method = 's'
            while GOMIN:
                MIN_STAT = 0
                # MIN
                # TODO: bgoli: see whether this also works with 'minimize'
                cpx.setObjective('min%s' % R, {R:1}, 'min', reset=True)
                ##  cplx_setBounds(c, id, min=None, max=None) # think about this
                MIN_STAT = cpx.solve(method=method)
                if MIN_STAT == 'LPS_OPT':
                    MIN_STAT = 1
                elif MIN_STAT == 'LPS_UNBND':
                    MIN_STAT = 2
                elif MIN_STAT == 'LPS_NOFEAS':
                    MIN_STAT = 3
                else:
                    MIN_STAT = 4
                if MIN_STAT == 1: # solved
                    min_oval = cpx.lp.obj.value
                elif MIN_STAT == 2: # unbound
                    min_oval = -numpy.Inf
                elif MIN_STAT == 3:
                    #min_oval = pre_sol[R]
                    min_oval = numpy.NaN
                else: # other failure
                    min_oval = numpy.NaN
                if debug:
                    cpx.write(cpxlp=os.path.join(debug_dir, '%smin.lp' % R))
                if MIN_STAT >= 3:
                    if gomin_cntr == 0:
                        cpx.erase()
                        del cpx
                        time.sleep(0.1)
                        cpx = glpk.LPX(mps=mps_filename)
                        gomin_cntr += 1
                    #elif gomin_cntr == 1:
                        #method = 'i'
                        #gomin_cntr += 1
                    else:
                        GOMIN = False
                else:
                    GOMIN = False
                if gomin_cntr >= max_error_iter:
                    GOMIN = False
    
            GOMAX = True
            gomax_cntr = 0
            method = 's'
            while GOMAX:
                MAX_STAT = 0
                # MAX
                cpx.setObjective('max%s' % R, coef=None, sense='max', reset=False)
                ##  cplx_setBounds(c, id, min=None, max=None) # think about this
                MAX_STAT = cpx.solve(method=method)
                if MAX_STAT == 'LPS_OPT':
                    MAX_STAT = 1
                elif MAX_STAT == 'LPS_UNBND':
                    MAX_STAT = 2
                elif MAX_STAT == 'LPS_NOFEAS':
                    MAX_STAT = 3
                else:
                    MAX_STAT = 4
                if MAX_STAT == 1: # solved
                    max_oval = cpx.lp.obj.value
                elif MAX_STAT == 2: # unbound
                    max_oval = numpy.Inf
                elif MAX_STAT == 3: # infeasable
                    #max_oval = pre_sol[R]
                    max_oval = numpy.NaN
                else: # other fail
                    max_oval = numpy.NaN
    
                if MAX_STAT >= 3:
                    if gomax_cntr == 0:
                        cpx.lp.erase()
                        del cpx.lp
                        time.sleep(0.1)
                        cpx.lp = glpk.LPX(mps=mps_filename)
                        gomax_cntr += 1
                    #elif gomax_cntr == 1:
                        #method = 'i'
                        #gomax_cntr += 1
                    else:
                        GOMAX = False
                else:
                    GOMAX = False
                if gomax_cntr >= max_error_iter:
                    GOMAX = False
    
    
            # check for solver going berserk
            if MIN_STAT > 1 and MAX_STAT > 1:
                print(Ridx)
                time.sleep(1)
    
            # enables using the default value as a solution if the solver fails
            if pre_opt and default_on_fail:
                if MAX_STAT > 1 and not MIN_STAT > 1:
                    max_oval = pre_sol[R]
                if MIN_STAT > 1 and not MAX_STAT > 1:
                    min_oval = pre_sol[R]
    
            if debug:
                cpx.write(cpxlp=os.path.join(debug_dir, '%smax.lp' % R))
    
            OUTPUT_ARRAY[Ridx,0] = pre_sol[R]
            if R in REDUCED_COSTS:
                OUTPUT_ARRAY[Ridx,1] = REDUCED_COSTS[R]
            OUTPUT_ARRAY[Ridx,2] = min_oval
            OUTPUT_ARRAY[Ridx,3] = max_oval
            OUTPUT_ARRAY[Ridx,4] = round(abs(max_oval - min_oval), roundoff_span)
            OUTPUT_ARRAY[Ridx,5] = MIN_STAT
            OUTPUT_ARRAY[Ridx,6] = MAX_STAT
            if markupmodel:
                REAC = fba.getReaction(R)
                REAC.setValue(pre_sol[R])
                REAC.fva_min = min_oval
                REAC.fva_max = max_oval
                REAC.fva_status = (MIN_STAT, MAX_STAT)
                if R in REDUCED_COSTS:
                    REAC.reduced_costs = REDUCED_COSTS[R]
            if not quiet and MAX_STAT > 1 or MIN_STAT > 1:
                print('Solver fail for reaction \"{}\" (MIN_STAT: {} MAX_STAT: {})'.format(R, MIN_STAT, MAX_STAT))
            cntr += 1
            if cntr == 200:
                tcnt += cntr
                print('FVA has processed {} of {} reactions'.format(tcnt, NUM_FLX))
                cntr = 0
    
        os.remove(mps_filename)
    
        #cpx.write(cpxlp='thefinaldebug.lp')
        del cpx
        print('\nSinglecore FVA took: {} min (1 process)\n'.format((time.time()-s2time)/60.))
        print('Output array has columns:')
        print('Reaction, Reduced Costs, Variability Min, Variability Max, abs(Max-Min), MinStatus, MaxStatus')
        return OUTPUT_ARRAY, OUTPUT_NAMES
       