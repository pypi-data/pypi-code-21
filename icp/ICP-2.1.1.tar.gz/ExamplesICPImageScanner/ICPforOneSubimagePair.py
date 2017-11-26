#!/usr/bin/env python

## ICPforOneSubimagePair.py

##   This script demonstrates ICP registration of one subimage extracted from
##   the large model image with the corresponding subimage extracted from the
##   large data image.

##   For this script to work, you have to have previously run the image scanner
##   that chops the large images into subimages and dumps into two scanner dump 
##   directories, one for the model image and the other for the data subimage.

##   The image scanner script in this example directory is 
##
##                  RunICPImageScanner.py


import pkg_resources
pkg_resources.require("ICP>=2.1.0")
import ICPImageScanner

model_image_file = "tommy_chang1.jpg"
data_image_file = "tommy_chang2.jpg"
scanning_window_width = 220
scanning_window_height = 216

subimage_index = 0

scanner = ICPImageScanner.ICPImageScanner(
               model_image_file = model_image_file,
               data_image_file = data_image_file,
               subimage_index = subimage_index,
               binary_or_color = "color",
               corners_or_edges = "edges",
               calculation_image_size = 200,
               max_num_of_pixels_used_for_icp = 300,
               pixel_correspondence_dist_threshold = 20,
               iterations = 60,
               scanning_window_width = scanning_window_width,
               scanning_window_height = scanning_window_height,
          )

scanner.calculate_icp_for_one_pair_of_subimages_and_display_results()

scanner.cleanup_scanner_examples_directory()
