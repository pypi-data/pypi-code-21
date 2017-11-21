#!/usr/bin/env python 

##     color_image_registration_with_corner_pixels_example1.py

##  This example is for the textured earrings images texture.jpg and
##  texture2.jpg in the Examples directory.  We must set the
##  binary_or_color parameter to 'color' in this case since we are dealing
##  with color images.  We want the ICP registration to be carried out in
##  'coners' mode.

##  The images used in this example are for my wife's earrings.  The photo
##  used is from the www.etsy.com website where these earrings are sold.
##  To the best of what I can tell, there are no copyright issues related
##  to the use of these images here.

import ICP

icp = ICP.ICP( 
               binary_or_color = "color",
               corners_or_edges = "corners",
               calculation_image_size = 200,
               image_polarity = -1,
               smoothing_low_medium_or_high = "medium",
               corner_detection_threshold = 0.2,
               pixel_correspondence_dist_threshold = 40,
               auto_select_model_and_data = 1,
               max_num_of_pixels_used_for_icp = 100,
               iterations = 16,
               model_image =  "textured.jpg",
               data_image = "textured2.jpg",
            )

icp.extract_pixels_from_color_image("model")
icp.extract_pixels_from_color_image("data")
icp.icp()
icp.display_images_used_for_corner_based_icp()
icp.display_results_as_movie()
icp.cleanup_directory()
