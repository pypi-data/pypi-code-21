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

from eureqa.analysis_cards.analysis_card import AnalysisCard

import json
import types

class Button(object):
    """ **BETA**
    An HTML button inside an HtmlCard

    :param str title: Title of the card
    """

    class Events:
        """ Constants that identify the types of events that can trigger an action """
        CLICK = "click"
        DBLCLICK = "dblclick"
        MOUSEUP = "mouseup"
        MOUSEDOWN = "mousedown"
        MOUSEENTER = "mouseenter"
        MOUSELEAVE = "mouseleave"

    def __init__(self, title, _actions=None):
        """ init """
        self.title = title
        self._actions = _actions if _actions else []

    def add_action(self, card_action, args=None, kwargs=None, event=Events.CLICK):
        """ Add an action to this button, to be performed when the specified event happens

        :param instancemethod card_action: Method on an analysis-card instance to invoke.  For example, `card.replace`.
        :param tuple args: Arguments to the `card_action` method
        :param dict kwargs: Keyword arguments to the `card_action` method
        :param str event: Event that triggers this action
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        assert hasattr(card_action, 'im_class') and issubclass(card_action.im_class, AnalysisCard),\
            "'card_action' must be a member function on an analysis-card class"
        assert hasattr(card_action, 'im_func') and hasattr(card_action, 'im_self'),\
            "'card_action' must be a member function on an analysis-card class"
        assert len(args) == card_action.im_func.func_code.co_argcount - 1,\
            "Expected %d arguments; got %d" % (card_action.im_func.func_code.co_argcount - 1, len(args))

        action_map = {
            card_action.im_class.replace.im_func: "replaceCardData"
        }

        if card_action.im_func not in action_map:
            raise AssertionError,\
                "'card_action' argument '%s.%s' is not a supported callback function.  Must be one of: (%s)"  \
                   % (card_action.im_class.__name__, card_action.__name__,
                      ', '.join('%s.%s' % (card_action.im_class.__name__, x.__name__) for x in action_map.iterkeys()))

        self._actions.append(_Action(args[0], event, card_action.im_self._private_channel, action_map[card_action.im_func]))

    def add_replace_action(self, target_card, replacement_card, event=Events.CLICK):
        """ Add a 'Replace' action to the specified card.
        Equivalent to `add_action(target_card.replace, (replacement_card,), event=event)`.

        :param eureqa.analysis_card.AnalysisCard target_card: Card to be replaced
        :param eureqa.analysis_card.AnalysisCard replacement_card: Card to replace `target_card` with
        :param Events event: Event to trigger the replacement
        """
        self._actions.append(_Action(replacement_card, event, target_card._private_channel, "replaceCardData"))

    def to_html(self, html_tag='a', **kwargs):
        """ Render this button as an HTML tag

        For example:  to_html('Go!', html_tag='button', style='color: blue;') would return
        "<button style='color: blue;' (...)>Go!</button>"

        :param str html_tag: Tag name.  For example, 'a', 'input', 'button', 'div'
        :param \**kwargs: Tag parameters.  For example, "style='color: blue;'"
        :return: HTML string representation of this button
        """

        # Hack/workaround for HTML links
        # Links don't respond helpfully to clicks unless they have a 'href'
        if html_tag == 'a' and 'href' not in kwargs:
            kwargs['href'] = '#'

        # '&#39;' is the HTML escape code for single-quote
        # HTML allows property strings to be wrapped in either single or double quotes.
        # Use single quotes:  At least one of these properties is a big JSON blob;
        # escaped JSON is much more readable if double-quote is not a special character.
        params = ' '.join("%s='%s'" % (key, value.replace("'", '&#39;')) for key, value in kwargs.iteritems())

        data = json.dumps(self.to_json()['actions']).replace("'", '&#39;')

        return "<%(html_tag)s%(param_space)s%(params)s data-analysis_events='%(data)s'>%(title)s</%(html_tag)s>" % {
            'html_tag': html_tag,
            'param_space': ' ' if params else '',
            'params': params,
            'data': data,
            'title': self.title
        }

    def to_json(self):
        return {
            'title': self.title,
            'actions': [x.to_json() for x in self._actions]
        }

    @classmethod
    def from_json(cls, data):
        return cls(data['title'], [_Action.from_json(x) for x in data['actions']])


class _Action(object):
    def __init__(self, payload, event, channel, action):
        self.payload = payload
        self.event = event
        self.channel = channel
        self.action = action

    def to_json(self):
        """
        :return: This _Action, represented as primitive JSON-serializable objects
        """
        return {
            'payload': self.payload.to_json(),
            'event': self.event,
            'channels': [ str(self.channel) ],
            'action': self.action
        }

    @classmethod
    def from_json(cls, data):
        assert len(data['channels']) in [0, 1]
        return cls(AnalysisCard.from_json(data['payload']), data['event'], data['channels'][0], data['action'])
