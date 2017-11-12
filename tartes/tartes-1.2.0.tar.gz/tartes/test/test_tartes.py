
from tartes import albedo
import numpy


def test_one_layer_diffuse():
    ssa = 20      # in m^2/kg
    wavelength = [450e-9, 650e-9, 850e-9, 1030e-9, 1300e-9]  # in m

    alb = albedo(wavelength, ssa)
    
    res = numpy.array((0.99614203926738309, 0.96047324904990949, 0.88128514422618554, 0.66596004345176796, 0.42830398442634676))
    assert numpy.all(abs(alb - res) < 1e-10)


def test_w1995():
    ssa = 20
    wavelength = 550e-9

    alb = albedo(wavelength, ssa, refrac_index="w1995")
    assert abs(alb - 0.9798191182503498) < 1e-10


def test_one_layer_direct():

    ssa = 20
    wavelength = 850e-9

    alb = albedo(wavelength, ssa, dir_frac=1, theta_inc=30)

    assert abs(alb - 0.8583967584060925) < 1e-10


def test_multilayer():

    ssa = [20, 15, 10]
    density = [200, 250, 300]
    thickness = [0.01, 0.10, 1000]

    wavelength = 650e-9

    alb = albedo(wavelength, ssa, density, thickness)


    res = numpy.array((0.97861955812074553, 0.9545327263717367, 0.87187587848576675))

    assert numpy.all(abs(alb - res)) < 1e-10

