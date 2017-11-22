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

class TopLevelModelParameter(Parameter):
    """TopLevelModel parameter description for analysis template. For selecting a single model (either an existing one within a datasource and search, or a custom one).

    :param str id: The id of the parameter that will be passed together with its value to an analysis script.
    :param str label: The parameter label that will be shown in UI.
    :param bool custom_disabled: Whether to block the user from setting a custom expression

    :var str id: The id of the parameter that will be passed together with its value to an analysis script.
    :var str TopLevelModelParameter.label: The parameter label that will be shown in UI.
    :var bool custom_disabled: Whether to block the user from setting a custom expression
    """

    def __init__(self, id, label, custom_disabled):
        """Initializes a new instance of the ~TopLevelModelParameter class
        """
        Parameter.__init__(self, id, label, "top_level_model")
        self.custom_disabled = custom_disabled

    def _to_json(self):
        body = Parameter._to_json(self)
        if self.custom_disabled is not None:
            body["custom_disabled"] = self.custom_disabled
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    @staticmethod
    def _from_json(body):
        ret = TopLevelModelParameter(None, None, None)
        Parameter.from_json(ret, body)
        if ret._type != "top_level_model": raise Exception("Invalid type '%s' specified for top_level_model parameter" % ret._type)
        if 'custom_disabled' in body:
            ret.custom_disabled = body["custom_disabled"]
        return ret
