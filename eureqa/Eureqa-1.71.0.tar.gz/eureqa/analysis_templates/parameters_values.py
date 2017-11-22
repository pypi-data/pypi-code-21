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

import json

from parameter_value import ParameterValue
from text_parameter_value import TextParameterValue
from data_source_parameter_value import DataSourceParameterValue
from top_level_model_parameter_value import TopLevelModelParameterValue
from variable_parameter_value import VariableParameterValue
from data_file_parameter_value import DataFileParameterValue
from combo_box_parameter_value import ComboBoxParameterValue
from numeric_parameter_value import NumericParameterValue

from collections import OrderedDict

class ParametersValues:
    """Analysis template parameters values

    :param list[Parameter] parameters: The list of parameter values for the template, whether text, variable or datasource value.
    """

    def __init__(self, parameters=None, _execution=None):
        """Initializes a new instance of the ~ParametersValues class
        :param list ~Parameter parameters: the list of parameter values for the template, whether text, variable or datasource value
        """
        self.parameters = parameters if isinstance(parameters, dict) else OrderedDict((p.id, p) for p in parameters) if parameters else parameters
        self._execution = _execution
                
    def _to_json(self):
        body = {}
        if self.parameters is not None and len(self.parameters) > 0:
            body['parameters'] = [x._to_json() for x in self.parameters.itervalues()]
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    _parameter_map = {
        'combo_box': ComboBoxParameterValue,
        'data_file': DataFileParameterValue,
        'datasource': DataSourceParameterValue,
        'numeric': NumericParameterValue,
        'top_level_model': TopLevelModelParameterValue,
        'text': TextParameterValue,
        'text_multiline': TextParameterValue,
        'variable': VariableParameterValue
    }

    @classmethod
    def _from_json(cls, eureqa, body, execution=None):
        ret = ParametersValues()
        if not 'parameters' in body: return ret

        parameters = []
        for element in body['parameters']:
            parameter = ParameterValue(None, None, None)
            ParameterValue._from_json(parameter, element, execution=execution)
            if not parameter._type in cls._parameter_map: raise Exception('Invalid analysis template parameter value type \'%s\' for parameter \'%s\' with value \'%s\'' %(parameter._type, parameter.id, parameter.value))
            parameter = cls._parameter_map[parameter._type]._from_json(eureqa, element, execution=execution)
            parameters.append(parameter)
        ret.parameters = OrderedDict((p.id, p) for p in parameters)
        return ret
