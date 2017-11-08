from unittest import TestCase
import test_utilities
import gmql as gl


class TestFrom_pandas(TestCase):
    def test_from_pandas(self):
        df = test_utilities.build_random_region_dataframe()
        print(df)
        gframe = gl.from_pandas(df, sample_name="sample_name")
        try:
            dataset = gframe.to_GMQLDataset()
            print(dataset.schema)
        except Exception:
            self.fail()




