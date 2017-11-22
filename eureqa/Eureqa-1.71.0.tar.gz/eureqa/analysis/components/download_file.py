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
from eureqa.analysis.analysis_file import AnalysisFile

class DownloadFile(_Component):
    """
    DownloadFile component
    Represents a Download link for a file within an Analysis, including the contents of that file.

    For example::

        df = DownloadFile(file_content="The file content", link_text="The link Text", filename="download.txt")
        analysis.create_html_card('Download file here: {0}'.format(analysis.html_ref(df)))


    :param str file_content: The contents of the file as a str() or eureqa.analysis.analysis_file.AnalysisFile
    :param str link_text: The text of the HTML download link in the Analysis
    :param str filename: The name of the downloaded file
    """

    _component_type_str = 'DOWNLOAD_FILE'

    def __init__(self, file_content=None, link_text=None, filename=None,
                 _analysis=None, _component_id=None, _component_type=None):
        if link_text is not None:
            self._link_text = link_text

        self._file_content = file_content
        self._filename = filename

        super(DownloadFile, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)

    @property
    def link_text(self):
        """
        Text of the link as rendered by the component
        """
        return getattr(self, "_link_text", None)

    @link_text.setter
    def link_text(self, val):
        self._link_text = val
        self._update()

    @property
    def file(self):
        """
        :rtype: eureqa.analysis.analysis_file.AnalysisFile
        """
        if hasattr(self, "_file_id") and hasattr(self, "_analysis") and not hasattr(self, "_file"):
            self._file = AnalysisFile(self._analysis, self._file_id)
        return getattr(self, "_file", None)

    def _upload_file(self, analysis):
        # Associate with the provided AnalysisFile
        if isinstance(self._file_content, AnalysisFile):
            self._file = self._file_content
            self._file_id = self._file._file_id
        # Or, if that doesn't exist, make one
        elif self._file_content is not None:
            file = self._file_content
            self._file = AnalysisFile.create(analysis, file, filename=self._filename)
            self._file_id = self._file._file_id

    def _pre_associate(self, analysis):
        self._upload_file(analysis)

    def _associate_with_table(self, analysis):
        self._upload_file(analysis)

        # ideally, file_url should be returned by the app server, but if we do a
        # POST to the app server here, it requires another network operation and
        # the component goes into analysis' main component list, which isn't
        # desired for components used in table
        self._file_url = ("/api/%s/analysis/%s/files/%s" % (analysis._organization, analysis._id, self._file_id))
        return super(DownloadFile, self)._associate_with_table(analysis)


    def _fields(self):
        return super(DownloadFile, self)._fields() + [ "link_text", "file_id", "file_url" ]
