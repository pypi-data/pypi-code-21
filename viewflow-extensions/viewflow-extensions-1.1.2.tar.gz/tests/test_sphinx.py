import os
import subprocess
from io import StringIO
from shutil import rmtree

import pytest
from django.conf import settings
from sphinx.application import Sphinx


class TestSphinx:
    docs_dir = os.path.join(settings.BASE_DIR, 'docs')

    @pytest.yield_fixture(autouse=True)
    def clean(self):
        build_dir = os.path.join(self.docs_dir, '_build')
        yield
        if os.path.exists(build_dir):
            rmtree(build_dir)

    def test_extension(self):
        stdout = StringIO()
        s = Sphinx(
            self.docs_dir,
            self.docs_dir,
            '%s/_build/html' % self.docs_dir,
            '%s/_build/doctrees' % self.docs_dir,
            'html',
            status=stdout,
        )
        s.build()
        stdout.seek(0)
        output = stdout.read()
        assert 'copying images...' in output
        assert 'build succeeded.' in output

    def test_multiprocessing(self):
        output = subprocess.check_output([
            'sphinx-build',
            '-b',
            'html',
            '-j 2',
            '.',
            '_build/html',
        ], cwd=self.docs_dir, stderr=subprocess.STDOUT)
        assert b'waiting for workers' in output
        assert b'copying images...' in output
        assert b'build succeeded.' in output
