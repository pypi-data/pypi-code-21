# coding: utf-8

from task_list_dev import tools


def test_get_list():
    assert isinstance(tools.get_list(), str)
