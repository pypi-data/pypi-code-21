####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit.Units import *

####################################################################################################

circuit = Circuit('Voltage Divider')

# LYYYYYYY n+ n- <value> <mname>
# SXXXXXXX n+ n- nc+ nc- model <on> <off>
# WYYYYYYY n+ n- vname model <on> <off>
# HXXXXXXX n+ n- vname value
# DXXXXXXX n+ n- mname
# QXXXXXXX nc nb ne <ns> mname
#
# VXXXXXXX n+ n- <<dc> dc/tran value> <ac <acmag <acphase>>> <distof1 <f1mag <f1phase>>> <distof2 <f2mag <f2phase>>>

# positional argument:
#   position
#   mandatory from args, else kwargs

circuit.R(1, 'n1', 'n2', kilo(1), temperature=40, noisy=True)
circuit.R(2, 'n1', 'n2', kilo(250), temperature=40)
circuit.C(1, 'n1', 'n2', nano(1), model='m1', temperature=40)
circuit.L(1, 'n1', 'n2', kilo(1), model='m1', temperature=40)
circuit.L(2, 'n1', 'n2', kilo(1), model='m1', temperature=140)
circuit.CoupledInductor(1, 'L1', 'L2', .9)
circuit.VCS(1, 'n1', 'n2', 'n3', 'n4', model='m2', initial_state=True)
circuit.BJT(1, 'n1', 'n2', 'n3', model='1N1111')

print(str(circuit))

####################################################################################################

class MyCircuit(Circuit):

    ##############################################

    def __init__(self, **kwargs):

        super().__init__(title='my circuit', **kwargs)

        self.R(1, 'n1', 'n2', kilo(1), temperature=40)
        self.R(2, 'n1', 'n2', kilo(250), temperature=40)

print(MyCircuit())

####################################################################################################

from PySpice.Spice.BasicElement import Resistor

print(Resistor('1', 'n1', 'n2', 100))
