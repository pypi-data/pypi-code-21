# coding=utf-8
import os

from fullmonty.tmp_dir import TmpDir


def test_tmp_dir():
    path = None

    with TmpDir() as dir:
        path = dir
        assert os.path.isdir(dir)

    assert not os.path.isdir(path)
