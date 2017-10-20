import toml
import pytest

@pytest.fixture(scope='module')
def settings():
    with open('ws_sheets.toml') as f:
        return toml.loads(f.read())

