#!/usr/bin/env python 

##         color_image_registration_with_edge_pixels_example2.py

##  This example is for the grayscale images highway.jpg and highway2.jpg
##  in the Examples directory.  We must set the binary_or_color parameter
##  to 'color' in this case since the 'color' value for this parameter
##  means both grayscale and color images.  We want the ICP registration to
##  be carried out in 'edges' mode.

import ICP

icp = ICP.ICP( 
               binary_or_color = "color",
               corners_or_edges = "edges",
               auto_select_model_and_data = 1,
               calculation_image_size = 200,
               max_num_of_pixels_used_for_icp = 200,
               pixel_correspondence_dist_threshold = 40,
               iterations = 24,
               model_image =  "highway.jpg",
               data_image = "highway2.jpg",
            )

icp.extract_pixels_from_color_image("model")
icp.extract_pixels_from_color_image("data")
icp.icp()
icp.display_images_used_for_edge_based_icp()
icp.display_results_as_movie()
icp.cleanup_directory()

