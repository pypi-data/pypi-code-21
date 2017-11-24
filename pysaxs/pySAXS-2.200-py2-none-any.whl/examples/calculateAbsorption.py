'''
example of use for the absorption module
'''

from pySAXS.LS import absorption
try:
        from pySAXS import xraylib
        from pySAXS.LS import absorptionXRL
        print "xraylib found. AbsorptionXRL imported"
        WITH_XRAYLIB=True
except :
        print "xraylib could not be found"
        WITH_XRAYLIB=False
        
from numpy import *

energy=8.03 #8 kev
formula="H 2 O 1"
density=1.0
thickness=0.1 #1 mm

print "---- calculation without xraylib ----"
print "Calculate Mu from formula for water : ",formula
mu=absorption.getMuFormula(formula,energy)
print "mu : ", mu
print "X-ray transmission = ",exp(-density*mu*thickness)

if WITH_XRAYLIB:
    print "---- calculation WITH xraylib ----"
    source='Cu'
    energy=absorptionXRL.getEnergyFromSource(source)
    print "energy for ",source," : ",energy," keV"
    print "Calculate Mu from formula for water : ",formula
    mu=absorptionXRL.getMuFormula(formula,energy)
    print "mu : ", mu
    print "X-ray transmission for 0.1cm = ",absorptionXRL.getTransmission(formula,density=density,thickness=0.1,energy=energy)
    print "X-ray transmission for 0.2cm = ",absorptionXRL.getTransmission(formula,density=density,thickness=0.2,energy=energy)
    print "-----------------------"
    source='Mo'
    energy=absorptionXRL.getEnergyFromSource(source)
    print "energy for ",source," : ",energy," keV"
    print "Calculate Mu from formula for water : ",formula
    mu=absorptionXRL.getMuFormula(formula,energy)
    print "mu : ", mu
    print "X-ray transmission for 0.1 cm = ",absorptionXRL.getTransmission(formula,density=density,thickness=0.1,energy=energy)
    print "X-ray transmission for 0.3 cm = ",absorptionXRL.getTransmission(formula,density=density,thickness=0.2,energy=energy)
    print "X-ray transmission for 1 cm = ",absorptionXRL.getTransmission(formula,density=density,thickness=1.0,energy=energy)
    

    