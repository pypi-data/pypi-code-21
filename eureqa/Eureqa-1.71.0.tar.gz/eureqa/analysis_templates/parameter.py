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

class Parameter(object):
    """Base class for all analysis templates parameters

    :param str id: The unique identifier for this Parameter.
    :param str label: The human-readable label to be associated with this Parameter.
    """

    def __init__(self, id, label, _type):
        self.id = id
        self.label = label
        self._type = _type
        self._body = {}
        
    def _to_json(self):
        body = self._body
        body['id'] = self.id
        body['label'] = self.label
        body['type'] = self._type
        return body

    def from_json(self, body):
        self.id = body['id']
        self.label = body['label']
        self._type = body['type']
        self._body = body
        
    @staticmethod
    def _from_json(body):
        p = Parameter(None, None, None)
        p.from_json(body)
        return p

