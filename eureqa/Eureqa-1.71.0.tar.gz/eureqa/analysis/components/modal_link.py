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

class ModalLink(_Component):
    """Represents a link which opens a popup window (modal) which can contain other components.

    The use of this class is typically hidden by the Modal classes link method.

    Example:
    # create a modal which is activated if a link is clicked
    text_block = TextBlock("This text is inside the modal")
    modal = Modal(title="This is the modal title", size='medium', icon_file_path='path/to/icon', component=text_block)
    h = HtmlBlock('Click this link to open a modal: {0}'.format(analysis.html_ref(modal.link('link text'))))
    layout.add_component(h)

    # create another link to the above modal
    h = HtmlBlock('OR click this other link to open the same modal: {0}'.format(analysis.html_ref(modal.link('different link text'))))
    layout.add_component(h)

    :param eureqa.analysis.components.modal.Modal modal: the Modal which this component will link to
    :param str link_text: The HTML which the link to open the modal will be wrapped around
    """

    _component_type_str = 'MODAL_LINK'

    def __init__(self, modal=None, link_text=None,
                 _analysis=None, _component_id=None, _component_type=None):
        if modal is not None:
            self._modal_component = modal
        self._link_text = link_text or 'Modal Link'

        super(ModalLink, self).__init__(_analysis=_analysis, _component_id=_component_id,
                                        _component_type=_component_type)

        if hasattr(self, '_modal_component') and hasattr(self._modal_component, '_component_id'):
            self._modal_component_id = modal._component_id

    @property
    def link_text(self):
        """
        Text of the link as rendered by the component
        """
        return self._link_text

    @property
    def modal_component_id(self):
        """
        The ID of the modal_component to be linked to
        """
        return getattr(self, "_modal_component_id", None)

    def _walk_children(self):
        if hasattr(self, "_modal_component"):
            yield self._modal_component

    def _register(self, analysis):
        if hasattr(self, '_modal_component') and hasattr(self._modal_component, "_component_id"):
            self._modal_component_id = self._modal_component._component_id

        super(ModalLink, self)._register(analysis)

    def _associate_with_table(self, analysis):
        content_json = []
        if hasattr(self, '_modal_component'):
            content_json += self._modal_component._associate_with_table(analysis)
            self._modal_component_id = self._modal_component._component_id
        return super(ModalLink, self)._associate_with_table(analysis) + content_json

    def _fields(self):
        return super(ModalLink, self)._fields() + [ 'link_text', 'modal_component_id' ]
