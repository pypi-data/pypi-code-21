from collections import OrderedDict

import pytest
from ruamel.yaml.constructor import DuplicateKeyError


def test_ordereddict():
    from zops.anatomy.yaml import yaml_load
    from zops.anatomy.text import dedent

    contents = yaml_load(
        dedent(
            """
              root:
                alpha: 1
                bravo: 2
                charlie: 3
                echo: 4
                foxtrot: 5
                golf: 6
                hotel: 7
            """
        )
    )
    assert isinstance(contents, OrderedDict)
    assert isinstance(contents['root'], OrderedDict)


def test_duplicate_keys():
    from zops.anatomy.yaml import yaml_load
    from zops.anatomy.text import dedent

    with pytest.raises(DuplicateKeyError):
        yaml_load(
            dedent(
                """
                  root:
                    alpha: 1
                    alpha: 2
                """
            )
        )
