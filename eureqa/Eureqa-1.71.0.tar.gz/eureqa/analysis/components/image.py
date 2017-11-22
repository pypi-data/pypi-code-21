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

import os.path

class Image(_Component):
    """
    Image component
    Represents an image which can be used in an Analysis.

    For example::

        i = Image('camel.png')
        analysis.create_html_card('Image here: {0}'.format(analysis.html_ref(i)))

    :param str image_path: path to the image file
    :param int width:  (optional) a specific width to display the image with
    :param int height: (optional) a specific height to display the image with
    """

    _component_type_str = 'IMAGE'

    _SUPPORTED_IMAGE_TYPES = ['.svg', '.jpg', '.jpeg', '.png', '.gif']

    def __init__(self, image_path=None, width=None, height=None,
                 _analysis=None, _component_id=None, _component_type=None):
        if image_path is not None:
            if not os.path.isfile(image_path):
                raise Exception('Image file located at "' + image_path + '" does not exist')
            self._image_path = image_path
            self._image_file_name = os.path.basename(self._image_path)
            image_file_ext = os.path.splitext(self._image_file_name)[-1].lower()
            if image_file_ext not in self._SUPPORTED_IMAGE_TYPES:
                raise Exception('Image file "' + self._image_file_name + '" is not supported. ' +
                                'Valid types are ' + ', '.join(self._SUPPORTED_IMAGE_TYPES))

        if width is not None:
            self._width = width
        if height is not None:
            self._height = height

        super(Image, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)

    @property
    def image_url(self):
        return getattr(self, '_image_url', None)

    @property
    def image_file_id(self):
        return getattr(self, '_image_file_id', None)

    @property
    def width(self):
        return getattr(self, '_width', None)

    @property
    def height(self):
        return getattr(self, '_height', None)

    @property
    def file(self):
        """
        :rtype: eureqa.analysis.analysis_file.AnalysisFile
        """
        if hasattr(self, "_image_file_id") and hasattr(self, "_analysis") and not hasattr(self, "_file"):
            self._file = AnalysisFile(self._analysis, self._image_file_id)
        return getattr(self, "_file", None)

    def _upload_image(self, analysis):
        with open(self._image_path, 'rb') as image_file:
            self._file = AnalysisFile.create(analysis, image_file, filename=self._image_file_name)
            self._image_file_id = self._file._file_id
        self._image_url = ("/api/%s/analysis/%s/files/%s" % (analysis._organization, analysis._id, self._image_file_id))

    def _pre_associate(self, analysis):
        if hasattr(self, '_image_path') and not hasattr(self, '_image_url'):
            self._upload_image(analysis)
            # ideally, image_url should be returned by the app server, but if we do a
            # POST to the app server here, it requires another network operation and
            # the component goes into analysis' main component list, which isn't
            # desired for components used in table

    def _fields(self):
        return super(Image, self)._fields() + [ "image_url", "image_file_id", "width", "height" ]
