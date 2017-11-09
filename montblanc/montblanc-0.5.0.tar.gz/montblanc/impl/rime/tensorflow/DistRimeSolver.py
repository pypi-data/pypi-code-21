from montblanc.solvers import MontblancTensorflowSolver
from montblanc.config import RimeSolverConfig as Options

class DistRimeSolver(MontblancTensorflowSolver):
    def __init__(self, slvr_cfg):
        """
        RimeSolver Constructor

        Parameters:
            slvr_cfg : SolverConfiguration
                Solver Configuration variables
        """
        super(DistRimeSolver, self).__init__(slvr_cfg)