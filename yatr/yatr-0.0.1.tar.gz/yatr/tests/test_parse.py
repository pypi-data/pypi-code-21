import os
from nose.tools import assert_raises

import yatr.context as yc
from yatr import Document, ValidationError
from yatr.parse import get_delete

DIR = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------------------------------------------------
# Utilities

def test_get_delete():
    d1 = dict(a=1, b=2)
    d2 = {}
    get_delete(d1, d2, 'a', 3)
    assert d1 == dict(b=2)
    assert d2 == dict(a=1)

    get_delete(d1, d2, 'b', 3, 'd')
    assert d1 == {}
    assert d2 == dict(a=1, d=2)

    get_delete(d1, d2, 'c', 3)
    assert d1 == {}
    assert d2 == dict(a=1, d=2, c=3)

#-------------------------------------------------------------------------------
# Document

def test_document():
    d = Document(dirname=DIR)
    assert not d.tasks

    d = Document.from_yaml({}, DIR)
    assert not d.tasks

    d = Document.from_yaml(dict(contexts=dict(bash1=dict(instanceof='bash')),
                                tasks=dict(dir='pwd')),
                           DIR)
    outs, errs = d.run('dir')
    assert errs == ['']
    assert outs == [os.getcwd() + '\n']

    path = os.path.join(DIR, 'mod1.py')
    assert_raises(ImportError, Document.from_yaml, {'import': [path]}, DIR)

    assert 'foo' not in yc.CONTEXT_REGISTRY
    path = os.path.join(DIR, 'mod2.py')
    d = Document.from_yaml({'import': [path]}, DIR)
    assert 'foo' in d.env.contexts
    assert 'foo' in yc.CONTEXT_REGISTRY

    path = os.path.join(DIR, 'yatrfile1.yml')
    d = Document.from_yaml(dict(include=[path],
                                macros=dict(a=3)),
                           DIR)
    assert d.env.macros == dict(a=3, b=2)

    assert_raises(ValidationError, Document.from_yaml, dict(foo='a'), DIR)
    assert_raises(ValidationError, Document.from_yaml, dict(include=['/foo/bar']), DIR)
    assert_raises(ValidationError, Document.from_yaml, {'import': ['/foo/bar']}, DIR)
    assert_raises(NotImplementedError, Document.from_yaml, dict(secrets=['a']), DIR)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
