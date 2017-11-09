import unittest
from depgraph import FIFO, BufferFull, BufferEmpty

class BufferTests(unittest.TestCase):

    def test_push(self):
        fifo = FIFO(size=5)
        for i in range(5):
            fifo.push(i)

        with self.assertRaises(BufferFull):
            fifo.push(5)

    def test_pop(self):
        fifo = FIFO(size=5)
        for i in range(5):
            fifo.push(i)

        for i in range(5):
            j = fifo.pop()
            self.assertEqual(i, j)

        with self.assertRaises(BufferEmpty):
            fifo.pop()

if __name__ == "__main__":

    unittest.main()

