#!/usr/bin/env python3

# internal modules
from numericalmodel.equations import PrognosticEquation

# external modules
import numpy as np

class AnemometerAngularMomentumEquation(PrognosticEquation):
    r"""
    This is an equation to simulate the **rotation frequency** :math:`f` of a
    `cup anemometer <https://en.wikipedia.org/wiki/Anemometer#Cup_anemometers>`_
    with four cups.

    .. math::

        \frac{df}{dt} = \frac{1}{2} \frac{\rho A R}{2 \pi I} 
            \left[ c_{w1} \left( max\left(u,v\right) - u \right) ^ 2
            - c_{w2} 2 u ^2 - c_{w2} \left(v+u\right)^2 \right] + F_R

    with the rotation velocity :math:`u`:

    .. math::

       u = 2 \pi R f 

    and the moment of inertia :math:`I`:

    .. math::

       I = 4 m_{cup} R ^ 2

    **Assumptions:**

    - four cups
    - rigid body
    - the one cup open to the wind is accelerated
    - all cups are slowed down by stream drag force

        - accelerated cup :math:`\left[c_{w1} \left( max\left(u,v\right)-u \right) ^ 2\right]`
        - opposite cup :math:`\left[c_{w2}(v+u)^2\right]`
        - two other cups :math:`\left[c_{w2}u^2\right]`

    - static and dynamic friction :math:`F_R` 
    """
    def derivative(self, time = None, variablevalue = None):
        """ 
        The frequency tendency at time ``time`` and frequency ``variablevalue``.
        """
        def i(var): 
            if not variablevalue is None and var == self.variable.id: 
                return variablevalue # return the specified value
            return self.input[var](time)
        u = 2 * np.pi * i("f") * i("R")
        v_f = max(i("v"),u)
        I = 4 * i("m") * i("R") ** 2
        factor = 1/2 * (i("rho")*i("A")*i("cw2")*i("R")) / (2*np.pi*I)
        windforce = factor * \
            ( i("cw1")/i("cw2") * (v_f-u)**2 - 2*u**2 - (i("v")+u)**2)
        if i("f") == 0: # does not turn
            if windforce > i("F_s"):
                friction = - i("F_s")
            else:
                friction = - windforce
        else: # turns
            dynfriction = (i("F_fa") * i("f") + i("F_f0"))
            if windforce > dynfriction:
                friction = - dynfriction
            else:
                fkrit = 1e-2
                if i("f") < fkrit:
                    # This is a little magic to prevent the anemometer from
                    # turning backwards because the dynamic friction is greater
                    # than the wind-driven angular moments.
                    # The divisor 2 is an arbitrary choice.
                    friction = - (windforce/2)
                else:
                    friction = - dynfriction

        return windforce + friction

