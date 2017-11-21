#!/usr/bin/env python 

##         binary_image_registration_example2.py

##  This example is for the binary images newline1.jpg and newline2.jpg
##  in the Examples directory.  We must set the binary_or_color parameter
##  to 'binary' in this case since we are dealing with binary images.


import ICP

icp = ICP.ICP( 
           binary_or_color = "binary",
           pixel_correspondence_dist_threshold = 40,
           auto_select_model_and_data = 1,
           calculation_image_size = 100,
           iterations = 16,
           model_image = "newline1.jpg",
           data_image = "newline2.jpg",
       )

icp.extract_pixels_from_binary_image("model")
icp.extract_pixels_from_binary_image("data")
icp.icp()
icp.display_images_used_for_binary_image_icp()
icp.display_results_as_movie()
icp.cleanup_directory()
