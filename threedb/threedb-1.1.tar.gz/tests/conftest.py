
import pytest


@pytest.fixture
def create_test_data(tmpdir):
    for num in range(10):
        name = "000%d" % (num)
        f = tmpdir.mkdir(name).join("%s.txt" % (name))
        f.write("lala")
    return str(tmpdir)
