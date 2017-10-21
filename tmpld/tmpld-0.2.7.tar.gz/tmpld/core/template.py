"""
tmpld.core.template
~~~~~~~~~~~~~~

Jinja2 Template wrapper for tmpld.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import os
import shutil
import textwrap

from . import util, frontmatter


class Template(frontmatter.FrontMatterFile):
    def __init__(self, file):
        frontmatter.FrontMatterFile.__init__(self, file)
        self.rendered = False
        self.written = False
        self._set_defaults()

    def __repr__(self):
        def format_attr(attr):
            template = '{0}: {{0.{0}!r}}'.format(attr)
            return template.format(self)

        attrs = ('rendered', 'written', 'metadata')
        return ('{}({}, {}, content: {})').format(
            type(self).__name__,
            self.file,
            ', '.join(format_attr(attr) for attr in attrs),
            textwrap.shorten(self.content, 60)
        )

    def _set_defaults(self):
        if not self.metadata.get('target'):
            self.metadata['target'] = self._guess_missing_target()

        if not self.metadata.get('owner'):
            self.metadata['owner'] = self._guess_missing_owner()

        if not self.metadata.get('mode'):
            self.metadata['mode'] = self._guess_missing_mode()

    def _guess_missing_target(self):
        if self.file in ('-', '/dev/stdin'):
            return '/dev/stdout'
        else:
            if self.file.endswith('.j2'):
                return self.file.rsplit('.', 1)[0]
            else:
                return self.file

    def _guess_missing_owner(self):
        if self.file not in ('-', '/dev/stdin'):
            return ':'.join(util.get_ownership(self.file))

    def _guess_missing_mode(self):
        if self.file not in ('-', '/dev/stdin'):
            return util.get_mode(self.file)

    @property
    def target(self):
        return self.metadata.get('target')

    def save(self):
        """Write jinja template to disk with ownership and mode."""
        target = self.metadata['target']
        owner = self.metadata['owner']
        mode = self.metadata['mode']

        # if not self.content.endswith('\n\n'):
        #     content+='\n\n'
        with util.smart_open(target, 'w') as fd:
            fd.write(self.content)

        if owner:
            shutil.chown(target, *util.parse_user_group(owner))
        if mode:
            os.chmod(target, util.octalize(mode))
