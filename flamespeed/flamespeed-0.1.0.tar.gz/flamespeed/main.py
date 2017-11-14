"""Module to run chemical kintetics library."""

import numpy as np
from flamespeed import chemkin

# Specie concentrations
x = np.array([2.0, 1.0, 0.5, 1.0, 1.0])

# Import reaction data
a = chemkin.ReactionRate()
a.read_XML('../data/rxns_hw5.xml')
print(a)

# Set temperature
a.set_temp(750)

# Progress rate
r = a.get_reaction_rate(x)
print("Reaction rate:\n")
print(r)
