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

class TextParameter(Parameter):
    """Text parameter description for analysis template

    :param str id: The id of the parameter that will be passed together with its value to an analysis script.
    :param str label: The parameter label that will be shown in UI.
    :param bool text_multiline: Indicates that the text should be split across multiple lines.

    :var str id: The id of the parameter that will be passed together with its value to an analysis script.
    :var str TextParameter.label: The parameter label that will be shown in UI.
    """

    def __init__(self, id, label, text_multiline=False):
        """Initializes a new instance of the ~TextParameter class
        """
        Parameter.__init__(self, id, label, "text_multiline" if text_multiline else "text")

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    @staticmethod
    def _from_json(body):
        param = TextParameter(None, None)
        param.from_json(body)
        if param._type not in ["text", "text_multiline"]: raise Exception("Invalid type '%s' specified for text parameter" % param._type)
        return param
