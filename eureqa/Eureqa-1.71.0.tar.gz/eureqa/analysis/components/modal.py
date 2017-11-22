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

import os.path

from eureqa.analysis.analysis_file import AnalysisFile
from eureqa.analysis.components.modal_link import ModalLink
from eureqa.analysis.components.base import _Component

class Modal(_Component):
    """Represents a popup window (modal) which can contain other components.

    Example:
    # create a modal which is activated if a link is clicked
    text_block = TextBlock("This text is inside the modal")
    modal = Modal(title="This is the modal title", size='medium', icon_file_path='path/to/icon', component=text_block)
    h = HtmlBlock('Click this link to open a modal: {0}'.format(analysis.html_ref(modal.link('link text'))))
    layout.add_component(h)

    :param str title: The title of the modal
    :param str size: (optional) modal size. Options are 'small', 'medium' or 'large'
    :param str icon_file_path: (optional) path to an icon file to display in the corner of the modal
    :param Component component: The component to display in the modal
    """

    _component_type_str = 'MODAL'

    def __init__(self, title=None, size=None, icon_file_path=None, component=None,
                 _analysis=None, _component_id=None, _component_type=None):
        self._title = title or ''
        self._size = size or 'small'
        if icon_file_path is not None:
            self._icon_file_path = icon_file_path
        if component is not None:
            self._content_component = component

        super(Modal, self).__init__(_analysis=_analysis, _component_id=_component_id,
                                    _component_type=_component_type)

        # call to self._associate may have been triggered by super.__init__ above
        # so we set up the content component after that call, to get the component id if there is one
        if hasattr(self, '_content_component') and hasattr(component, '_component_id'):
                self._content_component_id = component._component_id

    @property
    def content_component_id(self):
        """The id of the component to be displayed in the modal

        :rtype: str
        """
        return getattr(self, "_content_component_id", None)

    @property
    def title(self):
        """The title of the modal

        :rtype: str
        """
        return getattr(self, "_title", None)

    @property
    def size(self):
        """The size of the modal

        :rtype: str
        """
        return getattr(self, "_size", None)

    @property
    def icon_file_url(self):
        """The url of an icon file to be displayed in the corner of the modal

        :rtype: str
        """
        return getattr(self, "_icon_file_url", None)

    @property
    def icon_file_id(self):
        """The id of an icon file to be displayed in the corner of the modal

        :rtype: str
        """
        return getattr(self, "_icon_file_id", None)

    def _walk_children(self):
        if hasattr(self, "_content_component"):
            yield self._content_component

    def _register(self, analysis):
        updated_content = False
        if hasattr(self, '_content_component'):
            self._content_component_id = self._content_component._component_id
            updated_content = True

        if hasattr(self, '_icon_file_path') and not hasattr(self, "_icon_file_url"):
            icon_file_name = os.path.basename(self._icon_file_path)
            icon_file = open(self._icon_file_path, 'rb')
            self._icon_file = AnalysisFile.create(analysis, icon_file, filename=icon_file_name)
            self._icon_file_url = ("/api/%s/analysis/%s/files/%s" % (analysis._organization, analysis._id, self._icon_file._file_id))
            self._icon_file_id = self._icon_file._file_id
            updated_content = True

        super(Modal, self)._register(analysis)

    def _associate_with_table(self, analysis):
        content_json = []
        if hasattr(self, '_content_component'):
            content_json += self._content_component._associate_with_table(analysis)
            self._content_component_id = self._content_component._component_id

        if hasattr(self, '_icon_file_path'):
            icon_file_name = os.path.basename(self._icon_file_path)
            icon_file = open(self._icon_file_path, 'rb')
            self._icon_file = AnalysisFile.create(analysis, icon_file, filename=icon_file_name)
            self._icon_file_url = ("/api/%s/analysis/%s/files/%s" % (analysis._organization, analysis._id, self._icon_file._file_id))
            self._icon_file_id = self._icon_file._file_id

        return super(Modal, self)._associate_with_table(analysis) + content_json

    def _fields(self):
        return super(Modal, self)._fields() + [ 'content_component_id', 'title', 'size', 'icon_file_url', 'icon_file_id' ]

    def link(self, link_text=None):
        """
        Returns a ModalLink component which represents a link to this modal

        :param str link_text: (optional) link text to use in the ModalLink instead of default text
        :rtype: eureqa.analysis.components.modal_link.ModalLink
        """
        return ModalLink(modal=self, link_text=link_text)

