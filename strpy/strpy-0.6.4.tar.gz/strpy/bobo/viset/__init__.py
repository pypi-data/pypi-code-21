"""viset package initialization"""

# HACK: create a new builtin function object 'keyboard' to simplify package debugging
from pdb import set_trace as keyboard
import __builtin__
__builtin__.keyboard = keyboard

