import ICP
import unittest

check_data_list = [(14, 34), (14, 35), (14, 36), (15, 32), (15, 33), (16, 29), (16, 30), (16, 31), (17, 26), (17, 27), (17, 28), (18, 23), (18, 24), (18, 25), (19, 21), (19, 22), (20, 18), (20, 19), (20, 20), (21, 15), (21, 16), (21, 17), (22, 12), (22, 13), (22, 14), (23, 9), (23, 10), (23, 11), (24, 7), (24, 8), (25, 4), (25, 5), (25, 6), (26, 3)]


class TestPixelAcquisitionData(unittest.TestCase):

    def setUp(self):
        self.icp = ICP.ICP(model_image="linemodel.jpg", data_image="linedata.jpg",binary_or_color="binary")
        self.icp.extract_pixels_from_binary_image("data")
        self.datalist  = self.icp.data_list

    def test_data_pixels_xoords(self):
        print("testing pixel acquisitin for data images --- x-coordinates")
        x_data  = [p[0] for p in self.datalist]
        x_data_check = [p[0] for p in check_data_list]
        self.assertEqual(  len(x_data), len(x_data_check) )
        self.assertEqual(  x_data.sort(), x_data_check.sort() )

    def test_data_pixels_ycoords(self):
        print("testing pixel acquisition for data images --- y-coordinates")
        y_data = [p[1] for p in self.datalist]
        y_data_check = [p[1] for p in check_data_list]       
        self.assertEqual(  len(y_data), len(y_data_check) )
        self.assertEqual(  y_data.sort(), y_data_check.sort() )

def getTestSuites(type):
    return unittest.TestSuite([
            unittest.makeSuite(TestPixelAcquisitionData, type)
                             ])                    
if __name__ == '__main__':
    unittest.main()

