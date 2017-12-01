from jinja2 import nodes
from jinja2.ext import Extension


class CommentIfExtension(Extension):
    """Put a string before each line to comment out a block
    based on a boolean expression.

    Example::

        {% set comment=True %}
        {% commentif "#" comment %}
        My text
        should be comment if "comment" is True.
        {% endcommentif %}
    """
    tags = set(['commentif'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        args = [parser.parse_expression(), parser.parse_expression()]
        body = parser.parse_statements(['name:endcommentif'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_comment_if', args),
                               [], [], body).set_lineno(lineno)

    def _comment_if(self, escapestr, boolexpr, caller):
        rawinput = caller()
        if not boolexpr:
            return rawinput
        lines = rawinput.splitlines()
        output = '\n'.join(["%s%s" % (escapestr, l) for l in lines])
        return output
