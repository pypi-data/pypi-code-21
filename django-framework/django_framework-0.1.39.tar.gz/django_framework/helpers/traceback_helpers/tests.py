from nose.tools import assert_equal, assert_not_equal, assert_raises


from traceback_helpers import traceback_to_str
class TestTracebackException():
    
    def test_returns_string(self):
        '''Test that the return is a string'''
        try:
            raise AttributeError()
        except Exception, e:
            my_str = traceback_to_str(e)

        assert_equal(type(my_str), str)

    def test_works(self):
        '''Test that we can find the AttributeError we raised!'''
        try:
            raise AttributeError()
        except Exception, e:
            my_str = traceback_to_str(e)

        assert_equal(my_str.find('AttributeError()') > 0, True)
