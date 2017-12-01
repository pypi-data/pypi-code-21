import unittest
import jinja2_commentif

from jinja2 import Environment


class CommentIfExtensionTestCase(unittest.TestCase):

    def _get_env(self):
        return Environment(extensions=['jinja2_commentif.CommentIfExtension'],
            trim_blocks=True, lstrip_blocks=True)

    def test_python_tpl(self):
        env = self._get_env()
        tpl = env.from_string(
            """{% commentif "# " True %}Commented out text\nMultiline{% endcommentif %}""")
        assert tpl.render() == "# Commented out text\n# Multiline"

    def test_python_tpl_autoescape(self):
        env = self._get_env()
        env.add_extension("jinja2.ext.autoescape")
        tpl = env.from_string(
            """{% autoescape true %}
            {% commentif "# " True %}
            Commented out text
            Multiline
            {% endcommentif %}
            {% endautoescape %}""")
        assert tpl.render() == "# %sCommented out text\n# %sMultiline" % (
            " " * 12, " " * 12)
