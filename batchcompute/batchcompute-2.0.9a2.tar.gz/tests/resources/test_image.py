import unittest

from batchcompute.resources.image import *

class ImageDescriptionTest(unittest.TestCase):
    def setUp(self):
        self.image_name = "batchcompute_image"
        self.image_desc = "batchcompute_image created by batchcompute"
        self.image_id = "m-23rjvafd9"

    def get_image_description(self):
        img_desc = ImageDescription()

        img_desc.Name = self.image_name
        img_desc.Platform = "Windows" 
        img_desc.ECSImageId = self.image_id 
        return img_desc

    def testImageDescription(self):
        self.get_image_description()

if __name__ == '__main__':
    unittest.main()
