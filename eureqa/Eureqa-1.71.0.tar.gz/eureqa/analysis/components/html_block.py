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

class HtmlBlock(_Component):
    """Contains free-form user-specified HTML, including references to
    other components.

    Example::

        h = HtmlBlock('This will render on a Card in an Analysis')
        analysis.create_card(h)


    Example of using :class:`HtmlBlock` with a :class:`~eureqa.analysis.components.variable_link.VariableLink`::

        vl = VariableLink(d, 'X')
        h = HtmlBlock('Formatted <b>Card</b> in the Analysis, with reference to {0}'.format(analysis.html_ref(vl)))
        analysis.create_card(h)


    :param str html: Body of the card.

    :var str eureqa.analysis.components.html_block.HtmlBlock.html: Body of the card.

    If you need particular styles or JS libraries, you MUST define
    and/or load them as part of the HtmlBlock where they are needed.
    Any styles or JS objects defined by Eureqa may change or be
    removed from release to release.

    Embedding custom JavaScript (or CSS, which can contain JavaScript)
    from a malicious third-party source can grant that source access
    to your site.  Only embed content from trusted sources.

    """

    _component_type_str = 'ANALYSIS_HTML_BLOCK'

    def __init__(self, html='', _analysis=None, _component_id=None, _component_type=None):
        if html is not None:
            self._html = html

        super(HtmlBlock, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)


    @property
    def html(self):
        """ The body of this card.

        :return: body of this card
        :rtype: str"""
        return self._html

    @html.setter
    def html(self, val):
        self._html = val
        self._update()

    def _fields(self):
        return super(HtmlBlock, self)._fields() + [ 'html' ]
