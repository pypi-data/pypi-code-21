from shuup_testutils.generators import ShuupModelsGen

from attrim.testutils.generators.attrim import AttrimGen


class ModelsGen(ShuupModelsGen):
    def __init__(self):
        super().__init__()
        self.attrim = AttrimGen()
