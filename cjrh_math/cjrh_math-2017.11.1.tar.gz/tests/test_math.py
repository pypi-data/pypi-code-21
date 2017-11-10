import random
import statistics
from hypothesis import given
from hypothesis.strategies import integers
import cjrh_math


@given(integers(), integers())
def test_up_mean(a, b):
    if a >= b:
        return
    data = [random.randrange(a, b) for i in range(20)]
    m0 = statistics.mean(data)
    m1 = statistics.mean(data[:-1])
    delta = abs(m0 - cjrh_math.update_mean(19, m1, data[-1]))
    if m0 != 0:
        assert delta / m0 < 1e-8


def test_up_pvar():
    data = [random.randrange(1, 100) for i in range(20)]
    m1 = statistics.mean(data[:-1])
    pvar0 = statistics.pvariance(data)
    pvar1 = statistics.pvariance(data[:-1])
    delta = abs(pvar0 - cjrh_math.update_pvariance(19, m1, pvar1, data[-1]))
    assert delta < 1e-8


def test_up_var():
    data = [random.randrange(1, 100) for i in range(20)]
    m1 = statistics.mean(data[:-1])
    var0 = statistics.variance(data)
    var1 = statistics.variance(data[:-1])
    delta = abs(var0 - cjrh_math.update_variance(19, m1, var1, data[-1]))
    assert delta < 1e-8
