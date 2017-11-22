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


from parameter import Parameter

import json

class DataFileParameter(Parameter):
    """Data file parameter description for analysis template

    :param str id: The id of the parameter that will be passed together with its value to an analysis script.
    :param str label: The parameter label that will be shown in UI.
    :param str description: A description that will be shown in UI.
    :param list[str] filetypes: The list of accepted filetypes.

    :var str eureqa.analysis_templates.DataFileParameter.id: The id of the parameter that will be passed together with its value to an analysis script.
    :var str eureqa.analysis_templates.DataFileParameter.label: The parameter label that will be shown in UI.
    :var str eureqa.analysis_templates.DataFileParameter.description: A description that will be shown in UI.
    :var list[str] filetypes: The list of accepted filetypes.
    """

    def __init__(self, id, label, description, filetypes):
        """Initializes a new instance of the ~DataFileParameter class
        """
        Parameter.__init__(self, id, label, "data_file")
        self.description = description
        self.filetypes = filetypes

    def _to_json(self):
        body = Parameter._to_json(self)
        if self.description is not None:
            body["description"] = self.description
        if self.filetypes is not None and len(self.filetypes) > 0:
            body['filetypes'] = [x for x in self.filetypes]
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    @staticmethod
    def _from_json(body):
        ret = DataFileParameter(None, None, None, None)
        Parameter.from_json(ret, body)
        if ret._type != "data_file": raise Exception("Invalid type '%s' specified for data_file parameter" % ret._type)
        if 'description' in body:
            ret.description = body["description"]
        if 'filetypes' in body:
            ret.filetypes = [x for x in body['filetypes']]
        return ret
