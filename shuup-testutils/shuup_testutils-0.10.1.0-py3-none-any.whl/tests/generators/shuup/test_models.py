from shuup_testutils.cases import SnakeTestCase
from shuup_testutils.generators import ShuupModelsGen


class ShuupModelsGenTest(SnakeTestCase):
    def test_person_contact(self):
        gen = ShuupModelsGen()
        gen.person_contact()
