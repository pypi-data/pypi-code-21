"""
tmpld.core.tags
~~~~~~~~~~~~~~

Jinja2 Tags for tmpld.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import jinja2
import jinja2.ext

from . import util


class FileTag(jinja2.ext.Extension):
    """
    This will give us an {% file '/path/to/file' %} tag.
    """

    tags = set(['file'])

    def _parse_tokens(self, parser):
        path = util.Path(parser.filename)
        next(parser.stream)  # skip the tag name
        include_path = parser.parse_expression().value

        parser.stream.skip_if('comma')
        default = parser.stream.next_if('string')
        if default:
            default = default.value

        parser.stream.skip_if('comma')
        if parser.stream.skip_if('name:strip'):
            parser.stream.skip(1)
            strip = parser.parse_expression().value
        else:
            strip = True

        parser.stream.skip_if('comma')
        if parser.stream.skip_if('name:strip_comments'):
            parser.stream.skip(1)
            strip_comments = parser.parse_expression().value
        else:
            strip_comments = False

        full_path = util.build_path(include_path, path.absdir)
        return full_path, default, strip, strip_comments

    def parse(self, parser):
        contents = util.get_file(*self._parse_tokens(parser))
        node = jinja2.nodes.TemplateData(contents)
        return jinja2.nodes.Output([node])
