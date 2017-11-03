import os.path
import pytest

from latest.shortcuts import *


@pytest.fixture
def template_file(res_dir):
    return os.path.join(res_dir, 'template.tmpl')


@pytest.fixture
def expected_file(res_dir):
    return os.path.join(res_dir, 'expected.tex')


@pytest.fixture
def expected(expected_file):
    with open(expected_file, 'r') as f:
        return f.read()


def test_render(template_file, data_file, expected):
    assert render(template_file, data_file) == expected
