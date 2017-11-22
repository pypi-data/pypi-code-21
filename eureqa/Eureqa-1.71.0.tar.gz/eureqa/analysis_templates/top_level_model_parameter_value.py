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

class TopLevelModelParameterValue(ParameterValue):
    """TopLevelModel parameter value for analysis template

    :param Eureqa eureqa: A eureqa connection.
    :param str id: The id of the parameter.
    :param str value: The parameter value.
    :param str datasource_id: The parameter value for the datasource the expression belongs to.
    :param str search_id: The parameter value for the search the expression belongs to.
    :param str solution_id: The parameter value for the solution the expression belongs to.

    :var str id: The id of the parameter.
    :var str TopLevelModelParameterValue.value: The parameter value.
    """

    def __init__(self, eureqa, id, value, datasource_id, search_id, solution_id):
        """Initializes a new instance of the ~TopLevelModelParameter class
        """
        ParameterValue.__init__(self, id, value, 'top_level_model')
        self.datasource_id = datasource_id
        self.search_id = search_id
        self.solution_id = solution_id
        self._eureqa = eureqa

    def get_solution(self):
        if self.datasource_id is not None and self.search_id is not None and self.solution_id is not None:
            data_source = self._eureqa.get_data_source_by_id(self.datasource_id)
            return self._eureqa._get_solution_by_id(data_source._data_source_id, self.search_id, self.solution_id)
        else:
            return None

    def _to_json(self):
        body = {}
        ParameterValue._to_json(self, body)
        if self.datasource_id is not None:
            body["datasource_id"] = self.datasource_id
        if self.search_id is not None:
            body["search_id"] = self.search_id
        if self.solution_id is not None:
            body["solution_id"] = self.solution_id
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    @staticmethod
    def _from_json(eureqa, body, execution=None):
        param = TopLevelModelParameterValue(eureqa, None, None, None, None, None)
        ParameterValue._from_json(param, body)
        if param._type != "top_level_model": raise Exception("Invalid type '%s' specified for top_level_model parameter value" % param._type)
        if "datasource_id" in body and "search_id" in body and "solution_id" in body:
            param.datasource_id = body["datasource_id"]
            param.search_id = body["search_id"]
            param.solution_id = body["solution_id"]
        return param
