from unittest import TestCase
import gmql as gl


class TestGMQLDataset(TestCase):

    input_path = "/home/luca/Documenti/resources/hg_narrowPeaks_short"
    dataset = gl.load_from_path(local_path=input_path, parser=gl.parsers.NarrowPeakParser())

    def test_take(self):
        self.skipTest("too much time")
        result = self.dataset.take(10)
        print(result.regs)
        print(result.meta)

    def test_dag_serialization(self):
        new_dataset = self.dataset.reg_select(self.dataset.start > 10000)
        serialized_dag = new_dataset._get_serialized_dag()
        print(serialized_dag)
