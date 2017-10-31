import pytest

from zops.anatomy.assertions import assert_file_contents
from zops.anatomy.layers.tree import AnatomyFile, AnatomyTree, merge_dict

import os


def test_anatomy_file(datadir):

    # Prepare
    f = AnatomyFile(
        'gitignore',
        """
            a
            b
        """
    )

    # Execute
    f.apply(datadir, variables={})

    # Check
    assert_file_contents(
        datadir + '/gitignore',
        """
            a
            b
        """
    )


def test_anatomy_file_executable(datadir):

    # Prepare
    f = AnatomyFile(
        'gitignore',
        """
            a
            b
        """,
        executable=True
    )

    # Execute
    f.apply(datadir, variables={})

    # Check
    assert_file_contents(
        datadir + '/gitignore',
        """
            a
            b
        """
    )
    assert os.access(datadir + '/gitignore', os.X_OK)


def test_anatomy_file_with_filenames_using_variables(datadir):
    f = AnatomyFile("{{filename}}", 'This is alpha.')
    f.apply(datadir, variables={'filename': 'alpha.txt'})
    assert_file_contents(
        datadir + '/alpha.txt',
        """
            This is alpha.
        """
    )


def test_anatomy_file_replace_filename_with_variable(datadir):
    f = AnatomyFile("alpha.txt", 'This is alpha.')
    f.apply(datadir, variables={}, filename='zulu.txt')
    assert not os.path.isfile(datadir + '/alpha.txt')
    assert_file_contents(
        datadir + '/zulu.txt',
        """
            This is alpha.
        """
    )


def test_anatomy_tree(datadir):

    # Prepare
    tree = AnatomyTree()
    tree.create_file('.gitignore', 'line 1\n{% for i in gitignore.blocks %}{{ i }}{% endfor %}\n')
    tree.add_variables(dict(gitignore=dict(blocks=['line 2'])), left_join=False)

    # Execute
    tree.apply(datadir)

    # Check
    assert_file_contents(
        datadir + '/.gitignore',
        """
            line 1
            line 2
        """
    )


def test_anatomy_tree_with_variables(datadir):

    # Prepare
    tree = AnatomyTree()
    tree.create_file('alpha.txt', 'This is {{ name }}.')

    # Without defined variables
    with pytest.raises(RuntimeError):
        tree.apply(datadir)

    # With defined variables
    tree.add_variables(
        {'name': 'ALPHA'},
        left_join=False
    )
    tree.apply(datadir)
    assert_file_contents(
        datadir + '/alpha.txt',
        """
            This is ALPHA.
        """
    )


def test_merge_dict():

    # Error if the right dict has keys that doesn't exist on the left dict...

    # ... in the first level
    with pytest.raises(RuntimeError):
        merge_dict(dict(a=1), dict(z=9), left_join=True)

    # ... in the second level
    with pytest.raises(RuntimeError):
        merge_dict(dict(a=dict(a=1)), dict(a=dict(z=9)), left_join=True)

    # ... in the third level we ignore this differences.
    assert merge_dict(
        dict(a=dict(a=dict(a=1))),
        dict(a=dict(a=dict(z=9)))
    ) == dict(a=dict(a=dict(a=1, z=9)))

    # With left_join=False we ignore keys on the right dict that doesn't exist on the left dict.
    assert merge_dict(dict(a=1), dict(b=2), left_join=False) == dict(a=1, b=2)


    assert merge_dict({'a': 1}, {'a': 2}) == {'a': 2}
    assert merge_dict({'a': [1]}, {'a': [2]}) == {'a': [1, 2]}
    assert merge_dict({'a': {'aa': [1]}}, {'a': {'aa': [2]}}) == {'a': {'aa': [1, 2]}}
    assert merge_dict(
        {'a': {'aa': [1]}},
        {'a': {'aa': [2]}}
    ) == {'a': {'aa': [1, 2]}}
    assert merge_dict(
        {'PROJECT': {'code_name': 'alpha'}},
        {'PROJECT': {'code_name': 'zulu'}}
    ) == {'PROJECT': {'code_name': 'zulu'}}
