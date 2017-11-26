#!/usr/bin/env python

## RunICPImageScanner.py

##  This example script illustrates how to use the ICP ImageScanner class
##  in the ICP module.

##  This script scans the image in an interactive mode.  What that means is
##  that each subimage is shown to the user before moving on to the next
##  subimage.  

##  The subimages extracted from the large model and data images are dumped 
##  into scanner dump directories whose names are keyed to the names of the 
##  images.


import pkg_resources
pkg_resources.require("ICP>=2.1.0")
import ICPImageScanner

#  For these two images, use scanning_window_width=220   and   scanning_window_height=216
#model_image_file = "tommy_chang1.jpg"
#data_image_file = "tommy_chang2.jpg"

#model_image_file = "tommy_chang3.jpg"
#data_image_file = "tommy_chang4.jpg"

model_image_file = "tommy_chang5.jpg"
data_image_file = "tommy_chang6.jpg"
scanning_window_width = 740
scanning_window_height = 630


scanner = ICPImageScanner.ICPImageScanner(
               model_image_file = model_image_file,
               data_image_file = data_image_file,
               binary_or_color = "color",
               corners_or_edges = "edges",
               calculation_image_size = 200,
               max_num_of_pixels_used_for_icp = 300,
               scanning_window_width = scanning_window_width,
               scanning_window_height = scanning_window_height,
       )

scanner.chop_model_and_data_images_into_tiles_interactive()

