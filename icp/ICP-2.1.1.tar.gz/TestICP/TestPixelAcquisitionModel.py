import ICP
import unittest

check_model_list= [(3, 26), (4, 25), (5, 25), (6, 25), (7, 24), (8, 24), (9, 24), (10, 23), (11, 23), (12, 22), (13, 22), (14, 22), (15, 21), (16, 21), (17, 20), (18, 20), (19, 20), (20, 19), (21, 19), (22, 19), (23, 18), (24, 18), (25, 17), (26, 17), (27, 17), (28, 16), (29, 16), (30, 15), (31, 15), (32, 15), (33, 14), (34, 14), (35, 14), (36, 13)]

class TestPixelAcquisitionModel(unittest.TestCase):

    def setUp(self):
        self.icp = ICP.ICP(model_image="linemodel.jpg", data_image="linedata.jpg",binary_or_color="binary")
        self.icp.extract_pixels_from_binary_image("model")
        self.modellist = self.icp.model_list

    def test_model_pixels_xcoords(self):
        print("testing pixel acquisition for model images --- x-coordinates")
        x_model = [p[0] for p in self.modellist]
        x_model_check = [p[0] for p in check_model_list]
        self.assertEqual(  len(x_model), len(x_model_check) )
        self.assertEqual(  x_model.sort(), x_model_check.sort() )

    def test_model_pixels_ycoords(self):
        print("testing pixel acquisition for model images --- y-coordinates")
        y_model = [p[1] for p in self.modellist]
        y_model_check = [p[1] for p in check_model_list]       
        self.assertEqual(  len(y_model), len(y_model_check) )
        self.assertEqual(  y_model.sort(), y_model_check.sort() )

def getTestSuites(type):
    return unittest.TestSuite([
            unittest.makeSuite(TestPixelAcquisitionModel, type)
                             ])                    

if __name__ == '__main__':
    unittest.main()

