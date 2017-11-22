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

class ParameterValue(object):
    """Base class for all analysis templates parameters values

    :param str id: The unique identifier for this parameter.
    :param str value: The value of this parameter.
    """

    def __init__(self, id, value, _type):
        """ ParameterValue init """
        self.id = id
        self.value = value
        self._type = _type

    def _to_json(self, body):
        body['id'] = self.id
        body['value'] = self.value
        body['type'] = self._type

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    def _from_json(self, body, execution=None):
        self.id = body['id']
        self.value = body['value']
        self._type = body['type']
