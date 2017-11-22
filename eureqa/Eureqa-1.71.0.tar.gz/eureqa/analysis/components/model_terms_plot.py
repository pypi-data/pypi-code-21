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

from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class ModelTermsPlot(_Component):
    """A model terms plot card. See also :any:`Analysis.create_model_terms_plot_card`

    For example::

        p = ModelTermsPlot(solution=s)
        analysis.create_card(p)

    :param Solution solution: The solution that will be displayed in the plot
    """
    _component_type_str = 'TERMS_IN_TIME'

    def __init__(self, solution=None, _analysis=None, _component_id=None, _component_type=None):

        if solution is not None:
            self.solution = solution

        super(ModelTermsPlot, self).__init__(_analysis=_analysis, _component_id=_component_id,
                                           _component_type=_component_type)


    @property
    def solution(self):
        """The Solution to be displayed in the plot

        :rtype: Solution
        """
        if hasattr(self, "_eureqa"):
            return self._eureqa._get_solution_by_id(self._datasource_id, self._search_id, self._solution_id)

    @solution.setter
    def solution(self, val):
        self._solution_id = val._id
        self._search_id = val._search_id
        self._datasource_id = val._datasource_id
        self._eureqa = val._eureqa
        self._update()

    def _fields(self):
        return super(ModelTermsPlot, self)._fields() + [ 'datasource_id', 'search_id', 'solution_id' ]
