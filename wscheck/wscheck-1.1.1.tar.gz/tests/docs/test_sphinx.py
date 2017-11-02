import os
import sphinx

__SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs'))
__BUILD_DIR = os.path.join(__SOURCE_DIR, '_build')


def test_doctest():
    assert sphinx.make_main([__file__, '-M', 'doctest', __SOURCE_DIR, __BUILD_DIR]) == 0
