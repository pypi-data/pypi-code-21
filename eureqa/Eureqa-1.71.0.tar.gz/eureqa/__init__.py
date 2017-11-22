# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from analysis import Analysis
from complexity_weights import ComplexityWeights
from data_source import DataSource
import data_splitting
from data_splitting import DataSplitting
import error_metric
from eureqa import Eureqa
import math_block
from math_block import MathBlock
import missing_value_policies
from search import Search
import search_settings
from search_settings import SearchSettings
from solution import Solution
import variable_options
from variable_options import VariableOptions

__all__ = ['Analysis', 'ComplexityWeights', 'DataSource', 'data_splitting',
           'DataSplitting', 'error_metric', 'Eureqa', 'math_block', 'MathBlock', 'missing_value_policies',
           'Search', 'search_settings', 'SearchSettings', 'Solution', 'variable_options', 'VariableOptions']

# Enable deprecation warnings by default
import warnings
warnings.filterwarnings("default", category=DeprecationWarning, module=r"eureqa")
warnings.filterwarnings("default", category=DeprecationWarning, module=r"eureqa\..*")
