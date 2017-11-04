import unittest

from .training_sample_store import TrainingSampleStore


class TestTrainingSampleStore(unittest.TestCase):
    def test_no_data_at_init(self):
        ms = TrainingSampleStore()
        self.assertEqual(len(ms), 0)

    def test_add_data(self):
        ms = TrainingSampleStore()
        for idx in range(10):
            ms.add(sample_x=idx, sample_y=idx + 1)
            self.assertEqual(len(ms), idx + 1)

    def test_get_train_x_empty(self):
        ms = TrainingSampleStore()
        train_x = ms.get_train_x()
        self.assertEqual(len(train_x), 0)

    def test_get_train_x(self):
        ms = TrainingSampleStore()
        for idx in range(10):
            sample_x = [idx, idx + 1, idx + 2]
            sample_y = [idx + 3, idx + 4]
            ms.add(sample_x=sample_x, sample_y=sample_y)
        train_x = ms.get_train_x()
        self.assertEqual(len(train_x), 10)
        for idx in range(10):
            sample_x = [idx, idx + 1, idx + 2]
            self.assertCountEqual(train_x[idx], sample_x)

    def test_get_train_y_empty(self):
        ms = TrainingSampleStore()
        train_y = ms.get_train_y()
        self.assertEqual(len(train_y), 0)

    def test_get_train_y(self):
        ms = TrainingSampleStore()
        for idx in range(10):
            sample_x = [idx, idx + 1, idx + 2]
            sample_y = [idx + 3, idx + 4]
            ms.add(sample_x=sample_x, sample_y=sample_y)
        train_y = ms.get_train_y()
        self.assertEqual(len(train_y), 10)
        for idx in range(10):
            sample_y = [idx + 3, idx + 4]
            self.assertCountEqual(train_y[idx], sample_y)
