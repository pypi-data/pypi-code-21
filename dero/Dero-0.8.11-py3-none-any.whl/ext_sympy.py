
import datetime, os, sys
import multiprocessing as mp
from sympy import solve

class EquationSolver:
    
    def __init__(self, log_dir=None, debug=False):
        self.log_dir = log_dir
        self.debug = debug
        
        if self.log_dir:
            self.log_list = []
        
    def create_log_file(self):
        process = mp.current_process()._identity
        process_num = str(process[0])
        #name = 'log_' + str(datetime.datetime.now().replace(microsecond=0)).replace(':','.') + '_' + process_num + '.txt'
        name = 'log_' + process_num + '.txt'
        #name = 'log_' + str(datetime.datetime.now().replace(microsecond=0)).replace(':','.') + '.txt'
        if not os.path.exists(self.log_dir): os.makedirs(self.log_dir)
        self.log_path = os.path.join(self.log_dir, name)
                    
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w') as f:
                f.write('\n')
    
    def log(self, message, error=False, neverprint=False):       
        self.create_log_file()
        
        if error:
            message = 'ERROR: ' + message
        if message != '\n':
            time = datetime.datetime.now().replace(microsecond=0)
            message = str(time) + ': ' + message
        if self.debug and not neverprint:
            sys.stdout.write(message + '\n')
            sys.stdout.flush() #forces output now
        try:
            with open(self.log_path, 'a') as f:
                [f.write(item) for item in self.log_list] #log anything saved in memory that couldn't be written before
                f.write(message)
                f.write('\n')
            self.log_list = []
        except PermissionError: #if someone happened to write to the file at the same time
            self.log_list.append(message) #save it to log later
            self.log_list.append('\n')
            

    def solve_equations(self, selected_tuple, equations=None, params=None):
        """
        Solves a subset of a set of equations. For use with parallel_loop_with_timeout. Combining the two gets
        all possible solutions for an overidentified system using parallel processing. Doing this without the
        timeout can cause sympy to get stuck on some sets of equations.

        Arguments:
        selected_tuple: tuple, indices of the equations to select. Typically created by itertools.combinations.
        equations: full list of equations to solve. The subset of equations will be pulled from this list.
        params: parameters to solve the system in terms of. 

        Typical usage:
        import sympy
        sympy.init_session()
        eqs = []
        eqs.append(Eq(3*x + y, 2))
        eqs.append(Eq(2*x + y, 5))
        eqs.append(Eq(4*x + 2*y, 6))
        params = [x, y]
        
        log_dir ='C:\\Users\\derobertisna.UFAD\\Dropbox\\UF\\Nimal\\V PIN\\Modeling\\Testing\\Equations'
        
        combinations = list(itertools.combinations(range(len(equations)), len(params)))
        solve = dero.EquationSolver(log_dir=log_dir)
        solutions = dero.parallel_loop_with_timeout(solve.solve_equations, combinations, timeout=120,
                                                         equations=eqs, params=params)
        print([sol for sol in solutions if sol[1] not in ([],'timeout')])

        """
        assert equations != None
        assert params != None

        solve_eqs = [equations[i] for i in selected_tuple]

        if self.log_dir: #if we are logging
            self.log('Solving equation set {}:'.format(selected_tuple))
            [self.log(str(eq)) for eq in solve_eqs]

        result = solve(solve_eqs, params)

        if self.log_dir: #if we are logging
            self.log('Result for set {}:'.format(selected_tuple))
            self.log(str(result))

        return result