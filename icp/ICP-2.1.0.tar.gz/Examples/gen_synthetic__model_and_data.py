#!/usr/bin/env python 

import ICP

'''
   arg1:  feature, must be either 'line' or 'triangle'

   arg2:  (width,height) tuple indicating the size of the output image

   arg3:  (x,y) tuple indicating the position of the feature 

                 For a line, the line must pass through the position.

                 The position is with respect to the center of the image
                 center for the triangle.

   arg4:  an integer indicating the orientation of the feature

   arg5:  a string that is supposed to be the name of the output file
'''

ICP.ICP.gendata( "line", (40,40), (15,15), 30, "newline1.jpg" )

ICP.ICP.gendata( "line", (60,60), (20,20), 80, "newline2.jpg" )

ICP.ICP.gendata( "triangle", (60,60), (0,0), 10, "newtriangle1.jpg" )

ICP.ICP.gendata( "triangle", (80,80), (10,10), 30, "newtriangle2.jpg" )



