#!/usr/bin/env python

## ICPforScannerDump_show_intermediate_results.py

##  This script applies the ICP registration algorithm to ALL the subimage pairs 
##  extracted from the large model and the data images.
##
##  Since this script shows you ICP registration separately for each subimage 
##  pair, is is slower than the other similar script in this directory that
##  does NOT show the imtermediate results.
##
##  As mentioned elsewhere, you use the following script in this directory:
##
##                 RunICPImageScanner.py
##
##  to chop large model and data images into subimages that are dumped into 
##  scanner dump directories whose names are keyed to the names of the model
##  and the data images.
##
##  The final output of this script is in the form of a composite movie that shows 
##  ICP registration for ALL subimage pairs simultaneously.



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


scanner.apply_icp_to_model_and_data_scanner_dumps_and_show_intermediate_results()

print("\n\nWILL NOW SHOW ALL RESULTS IN A COMPOSITE MOVIE")

scanner.display_results_for_all_subimage_pairs_together_as_a_movie()

scanner.cleanup_scanner_examples_directory()




