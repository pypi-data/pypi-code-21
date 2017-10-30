from assets.storage import ManifestTree

def test_init():
    root = ManifestTree(path='test/subdir/A')
    assert list(root.list_dirs()) == ['subdir']
    assert list(root['subdir'].list_dirs()) == ['A']
    assert list(root['subdir']['A'].list_dirs()) == []


def test_frompath():
    root, leaf = ManifestTree.from_path(path='test/subdir/A')
    assert list(root.list_dirs()) == ['subdir']
    assert list(root['subdir'].list_dirs()) == ['A']
    assert list(root['subdir']['A'].list_dirs()) == []
    assert leaf.name == 'A'
    assert list(leaf.list_dirs()) == []

def test_iterfiles():
    root = ManifestTree()
    sub = ManifestTree('sub')
    sub._files['testC'] = 'C'
    root.append_tree(sub)
    root._files['testA'] = 'A'
    root._files['testB'] = 'B'
    root.append_tree(sub)
    assert set(root.iter_files()) == set([('testA','A'),('testB','B'),('sub/testC','C')])
