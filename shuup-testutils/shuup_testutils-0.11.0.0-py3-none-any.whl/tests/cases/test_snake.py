from shuup_testutils.cases import SnakeTestCase


class SnakeTestCaseTest(SnakeTestCase):
    is_set_up_class_works = False
    is_set_up_works = False

    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        cls.is_set_up_class_works = True

    def set_up(self):
        self.is_set_up_works = True

    def test_set_up(self):
        self.assert_true(self.is_set_up_works)

    def test_set_up_class(self):
        self.assert_true(self.is_set_up_class_works)
