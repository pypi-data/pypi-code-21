import os
import click


class TaskPath(click.ParamType):
    def __init__(self, base_dir=None, coerce_to_dir=False, normalize=True,
                 require_absolute=False):
        """
        Task Paths are paths for passing into Transfer or Delete tasks.
        They're only slightly more than string types: they can join themselves
        with a base dir path, and they can coerce themselves to the dir format
        by appending a trailing slash if it's absent.

        For us to toggle and talk about behaviors as necessary, normalization
        is an option that defaults to True.
        Also can enforce that the path is absolute.
        """
        self.base_dir = base_dir
        self.coerce_to_dir = coerce_to_dir
        self.normalize = normalize
        self.require_absolute = require_absolute

        # the "real value" of this path holder
        self.path = None
        # the original path, as consumed before processing
        self.orig_path = None

    def convert(self, value, param, ctx):
        if value is None or (ctx and ctx.resilient_parsing):
            return
        if isinstance(value, TaskPath):
            return value

        self.orig_path = self.path = value

        if self.base_dir:
            self.path = os.path.join(self.base_dir, self.path)
        if self.coerce_to_dir and not self.path.endswith('/'):
            self.path += '/'
        if self.normalize:
            self.path = os.path.normpath(self.path)

        if self.require_absolute and not (self.path.startswith('/') or
                                          self.path.startswith('~')):
            self.fail('{} is not absolute (abspath required)'
                      .format(self.path), param=param, ctx=ctx)

        return self

    def __repr__(self):
        return "TaskPath({})".format(
            ','.join(
                "{}={}".format(name, getattr(self, name))
                for name in
                ('base_dir', 'coerce_to_dir', 'normalize', 'path',
                 'orig_path'))
        )

    def __str__(self):
        return str(self.path)
