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
from variable_parameter import VariableParameter

import json

class DataSourceParameter(Parameter):
    """Data source parameter description for analysis template

    :param str id: The id of the parameter that will be passed together with its value to an analysis script.
    :param str label: The parameter label that will be shown in UI.
    :param list[eureqa.analysis_templates.VariableParameter] variables: The parameters for variables that belong to the datasource described
        by this parameter.
    """

    def __init__(self, id, label, variables):
        """Initializes a new instance of the ~DataSourceParameter class
        :param str id: The id of the parameter that will be passed together with its value to an analysis script.
        :param str label: The parameter label that will be shown in UI.
        :var list[eureqa.analysis_templates.VariableParameter] variables: The parameters for variables that belong to the datasource described
        by this parameter.
        """
        Parameter.__init__(self, id, label, "datasource")
        self.variables = variables

    def _to_json(self):
        body = Parameter._to_json(self)
        if self.variables is not None and len(self.variables) > 0:
            body['parameters'] = [x._to_json() for x in self.variables]
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    @staticmethod
    def _from_json(body):
        ret = DataSourceParameter(None, None, None)
        Parameter.from_json(ret, body)
        if ret._type != "datasource": raise Exception("Invalid type '%s' specified for datasource parameter" % ret._type)
        ret.variables = []
        if 'parameters' in body:
            ret.variables = [VariableParameter._from_json(x) for x in body['parameters'] if 'type' in x and x['type'] == "variable"]
        return ret
