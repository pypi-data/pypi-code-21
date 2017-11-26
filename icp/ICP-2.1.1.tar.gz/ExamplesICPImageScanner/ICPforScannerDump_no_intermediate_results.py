#!/usr/bin/env python

## ICPforScannerDump_no_intermediate_results.py

##  This script applies the ICP algorithm to ALL of the subimage pairs extracted
##  from the large model and data images.  As mentioned elsewhere, you use the 
##  following script in this directory:
##
##                 RunICPImageScanner.py
##
##  to chop large model and data images into subimages that are dumped into 
##  scanner dump directories whose names are keyed to the names of the model
##  and the data images.
##
##  This script for applying ICP to all subimage pairs should be much faster than
##  the other script in this directory that does the same thing:
##
##                 ICPforScannerDump_show_intermediate_results.py 
##
##  The output of 
##
##                 ICPforScannerDump_no_intermediate_results.py 
##
##  is in the form of a composite movie that shows ICP registration for ALL 
##  subimage pairs simultaneously.


import pkg_resources
pkg_resources.require("ICP>=2.1.0")
import ICPImageScanner


model_image_file = "tommy_chang1.jpg"
data_image_file = "tommy_chang2.jpg"
scanning_window_width = 220
scanning_window_height = 216

scanner = ICPImageScanner.ICPImageScanner(
               model_image_file = model_image_file,
               data_image_file = data_image_file,
               binary_or_color = "color",
               corners_or_edges = "edges",
               calculation_image_size = 200,
               max_num_of_pixels_used_for_icp = 300,
               pixel_correspondence_dist_threshold = 20,
               iterations = 60,
               scanning_window_width = scanning_window_width,
               scanning_window_height = scanning_window_height,
          )


scanner.apply_icp_to_model_and_data_scanner_dumps_fast()

print("\n\nWILL NOW SHOW ALL RESULTS IN A COMPOSITE MOVIE")

scanner.display_results_for_all_subimage_pairs_together_as_a_movie_with_colorization()

scanner.cleanup_scanner_examples_directory()

