import json

from globus_sdk.base import safe_stringify
from globus_cli.helpers import outformat_is_json
from globus_cli.safeio.write import safeprint


class PrintableErrorField(object):
    """
    A glorified tuple with a kwarg in its constructor.
    Coerces name and value fields to unicode for output consistency
    """
    TEXT_PREFIX = 'Globus CLI Error:'

    def __init__(self, name, value, multiline=False):
        self.name = safe_stringify(name)
        self.value = safe_stringify(value)
        self.multiline = multiline
        self._format_value()

    @property
    def _text_prefix_len(self):
        return len(self.TEXT_PREFIX)

    def _format_value(self):
        """
        formats self.value to be good for textmode printing
        self.value must be unicode before this is called, and will remain so
        """
        name = self.name + ':'
        if not self.multiline or '\n' not in self.value:
            self.value = u'{0} {1}'.format(name.ljust(self._text_prefix_len),
                                           self.value)
        else:
            spacer = '\n' + ' '*(self._text_prefix_len + 1)
            self.value = u'{0}{1}{2}'.format(
                name, spacer, spacer.join(self.value.split('\n')))


def write_error_info(error_name, fields, message=None):

    if outformat_is_json():
        # dictify joined tuple lists and dump to json string
        message = json.dumps(
            dict(
                [('error_name', error_name)] +
                [(f.name, f.value) for f in fields]),
            indent=2)
    if not message:
        message = u'A{0} {1} Occurred.\n{2}'.format(
            "n" if error_name[0] in "aeiouAEIOU" else "",
            error_name, '\n'.join(f.value for f in fields))
        message = u'{0} {1}'.format(PrintableErrorField.TEXT_PREFIX, message)

    safeprint(message, write_to_stderr=True)
