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

import warnings

class DistributionPlot(_Component):
    """Represents a distribution plot card on the server.

    :param eureqa.DataSource datasource: The data source to which the variable belongs.
    :param str variable_name: The name of the variable that will be displayed on the card.

    :var str ~eureqa.analysis_cards.DistributionPlotCard.title: The card title.
    :var str ~eureqa.analysis_cards.DistributionPlotCard.datasource: The datasource used by the card.
    :var str ~eureqa.analysis_cards.DistributionPlotCard.variable: The variable plotted by the coard.
    """

    _component_type_str = 'VARIABLE_DISTRIBUTION_PLOT'

    def __init__(self, datasource=None, variable_name=None, _analysis=None, _component_id=None, _component_type=None):
        if datasource is not None:
            self.datasource = datasource

        if variable_name is not None:
            self._variable_name = variable_name

        super(DistributionPlot, self).__init__(_analysis=_analysis, _component_id=_component_id,
                                                       _component_type=_component_type)

    @property
    def datasource(self):
        """The data source providing data for this component

        :return: data source providing data for this component
        """
        if hasattr(self, "_eureqa"):
            return self._eureqa.get_data_source_by_id(self._datasource_id)

    @datasource.setter
    def datasource(self, val):
        self._datasource_id = val._data_source_id
        self._eureqa = val._eureqa
        self._update()

    @property
    def variable_name(self):
        """
        Name of the variable to plot

        :rtype: str
        """
        return self._variable_name

    @variable_name.setter
    def variable_name(self, val):
        self._variable_name = val
        self._update()


    # For backwards compatibility
    @property
    def variable(self):
        """
        (Deprecated) Name of the variable to plot.  For backwards compatibility.

        :rtype: str
        """
        warnings.warn("Field name 'variable' on DistributionPlot is deprecated; please use 'variable_name'", DeprecationWarning)
        return self.variable_name

    @variable.setter
    def variable(self, val):
        warnings.warn("Field name 'variable' on DistributionPlot is deprecated; please use 'variable_name'", DeprecationWarning)
        self.variable_name = val


    def _fields(self):
        return super(DistributionPlot, self)._fields() + [ 'datasource_id', 'variable_name' ]
