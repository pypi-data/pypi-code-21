import pytest
from unittest import mock

from fant_sizer.fant_sizer import os
from fant_sizer import fant_sizer


@pytest.fixture()
def mock_os_walk(monkeypatch):
    def _set_dirs(a_list_of_dirs: list):
        with mock.patch('os.walk') as mockwalk:
            mockwalk.return_value = a_list_of_dirs
            monkeypatch.setattr('fant_sizer.fant_sizer', os)
    return _set_dirs
