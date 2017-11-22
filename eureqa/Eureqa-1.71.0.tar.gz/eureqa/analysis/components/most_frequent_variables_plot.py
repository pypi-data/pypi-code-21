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

class MostFrequentVariablesPlot(_Component):
    """A most frequent variables plot card. See also :any:`Analysis.create_most_frequent_variables_plot_card`

    For example::

        p = MostFrequentVariablesPlot(search=s)
        analysis.create_card(p)


    :param Search search: The search whose variable frequencies will be displayed on the card.
    """
    _component_type_str = 'VARIABLE_HISTOGRAM'

    def __init__(self, search=None, _analysis=None, _component_id=None, _component_type=None):

        if search is not None:
            self.search = search

        super(MostFrequentVariablesPlot, self).__init__(_analysis=_analysis, _component_id=_component_id,
                                           _component_type=_component_type)


    @property
    def search(self):
        """The Search the variables belong to

        :rtype: Search
        """
        if hasattr(self, "_eureqa"):
            return self._eureqa._get_search_by_search_id(self._datasource_id, self._search_id)

    @search.setter
    def search(self, val):
        self._search_id = val._id
        self._datasource_id = val._data_source_id
        self._eureqa = val._eureqa
        self._update()

    def _fields(self):
        return super(MostFrequentVariablesPlot, self)._fields() + [ 'datasource_id', 'search_id' ]
