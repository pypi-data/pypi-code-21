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
from text_parameter import TextParameter
from data_source_parameter import DataSourceParameter
from top_level_model_parameter import TopLevelModelParameter
from variable_parameter import VariableParameter
from data_file_parameter import DataFileParameter
from combo_box_parameter import ComboBoxParameter
from numeric_parameter import NumericParameter

import json
from collections import OrderedDict

class Parameters:
    """Analysis template parameters definition

    :param list[Parameter] parameters: The list of parameters for the template, whether text, variable or datasource.

    """

    def __init__(self, parameters=None):
        """Initializes a new instance of the ~Parameters class
        """
        self.parameters = OrderedDict((p.id, p) for p in parameters) if parameters is not None else parameters

    def _to_json(self):
        body = {}
        if self.parameters is not None:
            body['parameters'] = [x._to_json() for x in self.parameters.itervalues()]
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    _parameter_map = {
        'combo_box': ComboBoxParameter,
        'data_file': DataFileParameter,
        'datasource': DataSourceParameter,
        'numeric': NumericParameter,
        'top_level_model': TopLevelModelParameter,
        'text': TextParameter,
        'text_multiline': TextParameter,
        'variable': VariableParameter
    }

    @classmethod
    def _from_json(cls, body):
        ret = Parameters()
        if not 'parameters' in body: return ret

        parameters = []
        for element in body['parameters']:
            parameter = Parameter._from_json(element)
            if not parameter._type in cls._parameter_map: raise Exception('Invalid analysis template parameter type \'%s\' for parameter \'%s\' with label \'%s\'' %(parameter._type, parameter.id, parameter.label))
            parameter = cls._parameter_map[parameter._type]._from_json(element)
            parameters.append(parameter)
        ret.parameters = OrderedDict((p.id, p) for p in parameters)
        return ret
