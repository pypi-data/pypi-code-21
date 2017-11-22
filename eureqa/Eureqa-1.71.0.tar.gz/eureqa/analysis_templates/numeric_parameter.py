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

class NumericParameter(Parameter):
    """Numeric parameter description for analysis template

    :param str id: The id of the parameter that will be passed together with its value to an analysis script.
    :param str label: The parameter label that will be shown in UI.
    :param float min: The minimum value to allow.
    :param float max: The maximum value to allow.
    :param bool require_int: Indicates that the number should be an integer.

    :var str id: The id of the parameter that will be passed together with its value to an analysis script.
    :var str NumericParameter.label: The parameter label that will be shown in UI.
    :var float min: The minimum value to allow.
    :var float max: The maximum value to allow.
    :var bool reqire_int: Indicates that the number should be an integer.
    """

    def __init__(self, id, label, min=None, max=None, require_int=False):
        """Initializes a new instance of the ~TextParameter class
        """
        Parameter.__init__(self, id, label, "numeric")
        self.min = min
        self.max = max
        self.require_int = require_int

    def _to_json(self):
        body = Parameter._to_json(self)
        if self.min is not None:
            body["min"] = self.min
        if self.max is not None:
            body["max"] = self.max
        if self.require_int is not None:
            body["require_int"] = self.require_int
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    @staticmethod
    def _from_json(body):
        param = NumericParameter(None, None)
        param.from_json(body)
        if param._type != "numeric": raise Exception("Invalid type '%s' specified for numeric parameter" % param._type)
        if 'min' in body:
            param.min = body["min"]
        if 'max' in body:
            param.max = body["max"]
        if 'require_int' in body:
            param.require_int = body["require_int"]
        return param
