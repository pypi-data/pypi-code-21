#!/usr/bin/env python3
import os

import numpy as np
from matplotlib import pylab
import matplotlib.ticker as ticker


import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()


from PySpice.Spice.Netlist import  Circuit
from PySpice.Spice.Library import  SpiceLibrary
from PySpice.Unit.Units import  *
from PySpice.Physics.SemiConductor import ShockleyDiode

spice_library=SpiceLibrary(os.path.join(os.path.dirname(os.path.abspath(__file__)),'library'))

circuit=Circuit("Inverter")
circuit.include(spice_library['nfet'])
circuit.include(spice_library['pfet'])
#circuit.R(1,'vdd','out','10k')
circuit.MOSFET('pmos', 'out', 'gatein', 'vdd', 'vdd', model='pfet', length='360n', width='720n')
circuit.MOSFET('nmos', 'out','gatein',circuit.gnd,circuit.gnd,model='nfet',length='360n',width='360n')
Vinput=circuit.V('input','gatein',circuit.gnd,'5')
Vsupply=circuit.V('supply', 'vdd', circuit.gnd, '5')
analysis={}
simulator=circuit.simulator(temperature=60,nominal_temperature=60)
analysis=simulator.dc(Vinput=slice(0, 5, .01))
pylab.plot(analysis.gatein,analysis.out)
pylab.plt.show()
