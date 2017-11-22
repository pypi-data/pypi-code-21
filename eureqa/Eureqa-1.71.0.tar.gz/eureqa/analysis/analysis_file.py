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

from cStringIO import StringIO
from eureqa.utils import utils

class AnalysisFile(object):
    """
    AnalysisFile object

    Represents a file that is attached to an Analysis, and can be
    embedded in various places within the Analysis.
    AnalysisFiles are often either images (.jpg, .png, etc) or
    raw data files (.csv, .xls, etc), but any type of file is supported.

    Do not construct this class directly. Use :meth:`AnalysisFile.create`

    """

    def __init__(self, _analysis, _file_id, _filename=None):
        # Analysis object
        self._analysis = _analysis
        # File ID (string); must be a valid ID of a file on the server
        self._file_id = _file_id
        self._filename = _filename

    @classmethod
    def create(_cls, analysis, file, filename=None):
        """
        Upload a new file to an Eureqa Analysis.

        :param eureqa.analysis.Analysis analysis: Analysis to upload the file to
        :param str file: File to upload.  Can be either a string, in which case it is treated as the binary data of a file, or an actual Python file object or file-like object.
        :param str filename: The default name of file when downloaded
        :rtype: AnalysisFile
        """
        needs_close = False
        if isinstance(file, basestring):
            file = StringIO(file)

        if not filename:
            filename = "file"

        res = analysis._eureqa._session.execute("/analysis/%s/files" % utils.quote(analysis._id),
                                                "POST", files={"file": (filename, file)})

        return _cls(analysis, res["file_id"], filename)

    def update(self, file):
        """
        Update the contents of an existing file on the server.  Overwrites the file's previous data.

        :param str file: File to upload.  Can be either a string, in which case it is treated as the binary data of a file, or an actual Python file object or file-like object.
        """
        needs_close = False
        if isinstance(file, basestring):
            file = StringIO(file)

        filename = getattr(file, "name", str(self._file_id))

        self._analysis._eureqa._session.execute("/analysis/%s/files/%s" % (utils.quote(self._analysis._id),
                                                                           utils.quote(self._file_id)),
                                                "PUT", files={"file": (filename, file)})

    def get(self):
        """
        Return the raw data of this file

        :rtype: AnalysisFile.file
        """
        data = self._analysis._eureqa._session.execute("/analysis/%s/files/%s" % (self._analysis._id, self._file_id),
                                                       "GET", raw_return=True)
        return StringIO(data)

    @classmethod
    def _get_for_analysis(cls, analysis):
        """
        :param eureqa.analysis.Analysis analysis: Analysis to consider
        :return: Return a list of all file objects that are present in 'analysis'
        """
        files_json = analysis._eureqa._session.execute("/analysis/%s/files" % (analysis._id), "GET")
        files_list = [cls(analysis, x["file_id"], x.get("file_name")) for x in files_json]
        return files_list

    def delete(self):
        """
        Delete this file from the server
        """
        self._analysis._eureqa._session.execute("/analysis/%s/files/%s" % (self._analysis._id, self._file_id),
                                                "DELETE")

    def url(self):
        """
        :return: URL that this image can be reached from
        """
        return "/api/%(organization)s/analysis/%(analysis_id)s/files/%(file_id)s" % {
            "organization": self._analysis._eureqa._session.organization,
            "analysis_id": self._analysis._id,
            "file_id": self._file_id
        }
