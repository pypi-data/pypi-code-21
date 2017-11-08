####################################################################################################
import os

import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

#! libraries_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'libraries')
libraries_path = os.path.abspath('.')
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

# cm# buck-converter.m4
circuit = Circuit('Buck Converter')


#circuit.include(spice_library['1N5822']) # Schottky diode
#circuit.include(spice_library['irf150'])

circuit.include(spice_library['CCM1']) # Average Switch Model

Vin = 24@u_V
Vgate = 0.5@u_V
Lin = 75@u_uH
C = 33@u_uF
Rload = 20@u_Ω

frequency = 100@u_kHz
period = frequency.period

print('Vin =', Vin)
print('Vgate =', Vgate)
print('L =', Lin)
print('C =', C)
print('Rload =', Rload)

circuit.V('in', 'in', circuit.gnd, Vin)
circuit.X('SW', 'CCM1', 'in', 'source', 'source', circuit.gnd,'gate')
circuit.V('gate','gate',circuit.gnd,Vgate)
circuit.L('L', 'source', 'out', Lin)
circuit.C('C', 'out', circuit.gnd, C) # , initial_condition=0@u_V
circuit.R('load', 'out', circuit.gnd, Rload)

print(circuit)

###simulator = circuit.simulator(temperature=25, nominal_temperature=25)
###analysis = simulator.transient(step_time=period/100, end_time=period*100)
###
###figure = plt.figure(1, (20, 10))
###axe = plt.subplot(111)
###
###plot(analysis.out, axis=axe)
###plot(analysis['source'], axis=axe)
#### plot(analysis['source'] - analysis['out'], axis=axe)
#### plot(analysis['gate'], axis=axe)
####plt.axhline(y=float(Vout), color='red')
####plt.legend(('Vout [V]', 'Vsource [V]'), loc=(.8,.8))
###plt.grid()
###plt.xlabel('t [s]')
###plt.ylabel('[V]')
###
###plt.tight_layout()
###plt.show()
