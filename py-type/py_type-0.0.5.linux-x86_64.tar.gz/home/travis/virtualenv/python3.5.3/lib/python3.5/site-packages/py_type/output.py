class Output:
    def __init__(self):
        pass
    debug = False
    check_enabled = True

    check_level = 'all'

    levels = {'all'   : 1,
              'trace' : 2,
              'debug' : 3,
              'info'  : 4,
              'warn'  : 5,
              'error' : 6,
              'fatal' : 7,
              'off'   : 8}

    @staticmethod
    def error_func(s):
        raise Exception(s)

    def do_check(self, level):
        if self.debug:
            print('check-enabled: ' + str(self.check_enabled) + ', level: ' + level + ', check-level: ' + self.check_level)
        return self.check_enabled & (self.levels[self.check_level] <= self.levels[level])


output = Output()