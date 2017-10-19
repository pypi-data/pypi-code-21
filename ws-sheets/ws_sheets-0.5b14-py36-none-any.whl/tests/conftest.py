
import pytest

import modconf

@pytest.fixture(scope='module')
def settings():
    return modconf.import_conf('ws_sheets.tests.conf.simple').Settings

