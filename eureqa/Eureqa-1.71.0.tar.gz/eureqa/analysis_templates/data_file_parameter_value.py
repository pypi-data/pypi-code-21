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


from parameter_value import ParameterValue

import json
from eureqa.utils import utils

class DataFileParameterValue(ParameterValue):
    """Combo box parameter description for analysis template

    :param Eureqa eureqa: A eureqa connection.
    :param str id: The id of the parameter.
    :param str file_path: The path to the file that should be uploaded to the server. If running locally, this path will be used to retreive the file directly.

    :var str id: The id of the parameter.
    :var str ~analysis_templates.DataFileParameterValue.file: the contents of the uploaded file
    :var str ~analysis_templates.DataFileParameterValue.value: the file id of the file on the server

    """

    def __init__(self, eureqa, id, file_path):
        """Initializes a new instance of the ~DataFileParameterValue class
        """
        self._eureqa = eureqa
        ParameterValue.__init__(self, id, None, "data_file")
        self.file_path=file_path
        self._execution = None

    def _to_json(self):
        body = {}
        ParameterValue._to_json(self, body)
        if self.file_path is not None:
            body['file_path'] = self.file_path
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    @property
    def file(self):
        contents = ""
        if self._execution is None:
            assert self.file_path is not None
            f = open(self.file_path, 'rb')
            contents = f.read()
            f.close()
        else:
            contents = self._eureqa._session.execute('/analysis_templates/%s/executions/%s/files/%s' %
                                                     (utils.quote(self._execution.template_id),
                                                      utils.quote(self._execution._id),
                                                      utils.quote(self.id)), 'GET', raw_return=True)
        return contents

    def _add_file_to_template(self, template):
        # This is used when calling 'execute()' directly on a template.
        # In that case, we have no matching DataFileParameter object to upload the file for us.
        # So we need a workaround to get the file data uploaded.
        f = open(self.file_path, 'rb')
        resp = self._eureqa._session.execute('/analysis_templates/%s/add_file'% utils.quote(template._id), 'POST', files={'file': (self.file_path,f)})
        self.value = resp['file_id']

    @staticmethod
    def _from_json(eureqa, body, execution=None):
        param = DataFileParameterValue(eureqa, None, None)
        ParameterValue._from_json(param, body)
        param.file_path = body.get('file_path')
        if param._type != "data_file": raise Exception("Invalid type '%s' specified for data file parameter value" % param._type)
        param._execution = execution
        return param
