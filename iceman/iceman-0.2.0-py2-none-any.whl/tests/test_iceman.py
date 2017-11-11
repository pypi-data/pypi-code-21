import iceman

class TestIceman(object):
    def test_version(self):
        subject = iceman.__version__
        assert subject != None
