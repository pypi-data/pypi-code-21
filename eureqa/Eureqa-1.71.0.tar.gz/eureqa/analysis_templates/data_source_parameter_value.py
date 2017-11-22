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
from variable_parameter_value import VariableParameterValue

import json

class DataSourceParameterValue(ParameterValue):
    """Data source parameter description for analysis template

    :param Eureqa eureqa: A eureqa connection.
    :param str id: The id of the parameter.
    :param str value: The parameter value.
    :param list[eureqa.analysis_templates.VariableParameterValue] variables: The parameters values for variables that belong to this data source.
    """

    def __init__(self, eureqa, id, value, variables):
        """Initializes a new instance of the ~DataSourceParameter class
        """
        ParameterValue.__init__(self, id, value, 'datasource')
        self.variables = variables
        self._eureqa = eureqa

    def get_data_source(self):
        return self._eureqa.get_data_source_by_id(self.value)

    def _to_json(self):
        body = {}
        ParameterValue._to_json(self, body)
        if self.variables is not None and len(self.variables) > 0:
            body['parameters'] = [x._to_json() for x in self.variables]
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    @staticmethod
    def _from_json(eureqa, body, execution=None):
        ret = DataSourceParameterValue(eureqa, None, None, None)
        ParameterValue._from_json(ret, body)
        if ret._type != "datasource": raise Exception("Invalid type '%s' specified for datasource parameter value" % ret._type)
        ret.variables = []
        if 'parameters' in body:
            ret.variables = [VariableParameterValue._from_json(eureqa, x) for x in body['parameters'] if 'type' in x and x['type'] == 'variable']
        return ret
