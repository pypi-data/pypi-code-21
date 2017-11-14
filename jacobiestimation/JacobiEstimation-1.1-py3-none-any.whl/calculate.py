import math as m
import cmath as cm

class Jacobi:

    C = 1
    W = complex(1, 2)
    J = complex(1, 5)

    # invoke me!
    def processN(self, gamma, betta, k = 10):
        steps = range(0, k)
        delta = self._findDelta(gamma, betta, steps)
        max = self._findMax(gamma, betta, steps)
        return list(map(lambda delta: max / delta + 0.5, delta))

    # ////////////////

    def _findDelta(self, gamma, betta, steps):
        resV = self._funcV_(gamma, betta, steps, True)
        return list(map(lambda resV1, b1: m.sqrt((8 * b1) / m.fabs(resV1)), resV, betta))


    def _findMax(self, gamma, betta, steps):
        resV = self._funcV_(gamma, betta, steps, False)
        conditionArray1 = list(filter(lambda i: 2 < i < 10, resV))
        conditionArray2 = list(filter(lambda i: -7 < i < 3, resV))
        return max([max(conditionArray1 or [0]), max(conditionArray2 or [0])])


    def _funcV_(self, gamma, betta, steps, isOriginal):
        return list(map(lambda ki:
                            self._main_func(ki,
                                        gamma[ki],
                                        betta[ki],
                                        self._wj_func_with_phase() if isOriginal
                                            else self._wj_func_with_w_only()),
                        steps))


    def _main_func(self, ki, gamma, betta, wj_func):
        p = range(1, betta)
        res1_0 = 1
        for pi in p:
            res1_0 *= (((2 * ki + 2 * pi + 1) * self.C * gamma) / 2) + wj_func
        res1 = (pow(pow(self.C, 2) * gamma, betta + 1) * (2 * ki + betta + 1) * (m.factorial(betta + ki))) / (
        m.factorial(ki) * res1_0)

        res2 = 0
        for si in range(0, ki):
            res_inter_1 = m.factorial(ki) / (m.factorial(si) * m.factorial((ki - si)))
            res_inter_2 = pow(m.factorial(ki + si) / (m.factorial(si) * m.factorial(ki + si + 1)), -1)
            res_inter_3 = 1 / ((((2 * si + 1) * self.C * gamma) / 2) + wj_func)
            res2 += res_inter_1 * res_inter_2 * res_inter_3
        return res1 * res2

    # /////////////////
    def _wj_func_with_phase(self):
        return (cm.phase(self.W) * cm.phase(self.J))

    def _wj_func_with_w_only(self):
        return cm.phase(self.W)

