class AssertEqualSubtestsForFunc:
    def __init__(self, test_case, func):
        self.tests = []
        self.test_case = test_case
        self.func = func

    def add(self, inputs, outputs):
        self.tests.append((inputs, outputs))

    def run(self):
        for ipt, opt in self.tests:
            self.test_case.assertEqual(self.func(ipt), opt)


def debug_msg(*args, **kwargs):
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe().f_back)
    print('DEBUG MSG FROM:', frameinfo.filename, frameinfo.lineno)
    print(*args, **kwargs)
    print('DEBUG MSG END========================================')
