# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Test for PatchManager
# :Created:   mer 24 feb 2016 16:37:44 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

from __future__ import unicode_literals


def test_manager():
    from metapensiero.sphinx.patchdb.contexts import ExecutionContext
    from metapensiero.sphinx.patchdb.manager import PatchManager
    from metapensiero.sphinx.patchdb.patch import make_patch

    ctx = ExecutionContext()
    pm = PatchManager()
    first = make_patch('first', 'script',
                       dict(revision=1,
                            language='test',
                            depends='second'))
    pm['first'] = first
    second = make_patch('second', 'script',
                        dict(revision=2,
                             language='test',
                             depends='third'))
    pm['second'] = second
    third = make_patch('third', 'script',
                       dict(depends='second@1',
                            preceeds='first',
                            language='test'))
    pm['third'] = third
    always_beg = make_patch('always_beg', 'script',
                            dict(always='first', language='test'))
    pm['always_beg'] = always_beg
    always_last = make_patch('always_last', 'script',
                             dict(always='last', language='test'))
    pm['always_last'] = always_last

    assert ['%s' % p for p in pm.neededPatches(ctx)] == [
        str(always_beg),
        str(third),
        str(second),
        str(first),
        str(always_last),
        ]


def test_persistent_patch_manager():
    from io import open
    from os import unlink
    from tempfile import mktemp
    from metapensiero.sphinx.patchdb.manager import PersistentPatchManager
    from metapensiero.sphinx.patchdb.patch import make_patch

    tempfile = mktemp(suffix='.yaml')
    pm = PersistentPatchManager(tempfile)
    first = make_patch('first', 'script',
                       dict(revision=1, language='test',
                            depends='second'),
                       'This patch costs € 0.1')
    pm['first'] = first
    second = make_patch('second', 'script',
                        dict(revision=2, language='test'))
    pm['second'] = second
    third = make_patch('third', 'script',
                       dict(depends='second@1',
                            preceeds='first',
                            language='test'))
    pm['third'] = third
    pm.save()
    with open(tempfile, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'This patch costs ' in content
    pm.load()
    assert 'This patch costs € 0.1' == pm['first'].description
    unlink(tempfile)


def test_double_jump():
    from metapensiero.sphinx.patchdb.contexts import ExecutionContext
    from metapensiero.sphinx.patchdb.manager import PatchManager
    from metapensiero.sphinx.patchdb.patch import make_patch

    ctx = ExecutionContext({
        'table a': 1
    })

    pm = PatchManager()

    table_a = make_patch('table a', 'script',
                         dict(revision=3,
                              language='test'))
    pm['table a'] = table_a

    transition_1_2 = make_patch('to table a2', 'script',
                                dict(revision=1,
                                     language='test',
                                     depends='table a@1',
                                     brings='table a@2'))
    pm['to table a2'] = transition_1_2

    transition_2_3 = make_patch('to table a3', 'script',
                                dict(revision=1,
                                     language='test',
                                     depends='table a@2',
                                     brings='table a@3'))
    pm['to table a3'] = transition_2_3

    content_table_a = make_patch('content table a', 'script',
                                 dict(revision=1,
                                      language='test',
                                      depends='table a@3'))
    pm['content table a'] = content_table_a

    applied = []
    for patch in pm.neededPatches(ctx):
        ctx.apply(patch, None)
        applied.append(str(patch))

    assert applied == [
        str(transition_1_2),
        str(transition_2_3),
        str(content_table_a),
    ]
