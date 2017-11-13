

class CommandError(Exception):
    """Custom exception class."""

    def __init__(self, problem, solution=''):
        super(Exception, self).__init__()
        # Note: we can add localization here
        self.problem = problem
        self.solution = solution

    def __str__(self):
        s = self.problem
        if self.solution:
            s += '\n' + self.solution
        return s
