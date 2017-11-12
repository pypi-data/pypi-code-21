import re;
import numpy as np
import collections
from collections import defaultdict
import pandas as pd;

class DDict(dict):
     __getattr__ = dict.get
     __setattr__ = dict.__setitem__
     __delattr__ = dict.__delitem__


