__version__ = '2.1.1'
__author__  = "Avinash Kak (kak@purdue.edu)"
__date__    = '2017-November-25'
__url__     = 'https://engineering.purdue.edu/kak/distICP/ICP-2.1.1.html'
__copyright__ = "(C) 2017 Avinash Kak. Python Software Foundation."


from ICP import ICP

from PIL import Image
from PIL import ImageDraw
from PIL import ImageTk
from PIL import ImageChops
from PIL import ImageFont
import numpy
import sys,os,os.path,glob,signal
import re
import functools
import math
import random
import copy
if sys.version_info[0] == 3:
    import tkinter as Tkinter
    from tkinter.constants import *
    import tkinter.font as tkFont
else:
    import Tkinter    
    from Tkconstants import *
    import tkFont
import pymsgbox
import time

#___________________________________  Utility functions  ____________________________________

def ctrl_c_handler( signum, frame ):             
    print("Killed by Ctrl C")                       
    os.kill( os.getpid(), signal.SIGKILL )       
signal.signal( signal.SIGINT, ctrl_c_handler )   

def file_index(file_name):
    '''
    This function is needed if you are analyzing an image in the scanning mode.
    In this mode, the module runs a non-overlapping scanning window over the image,
    dumps the image data inside the scanning window at each position of the window
    in a directory.  Each file is given a name that includes a numerical index
    indicating its position in the original images.  This function returns the
    numerical index in the name of a file.
    '''
    m = re.search(r'_(\d+)\.jpg$', file_name)
    return int(m.group(1))

#______________________________  ImageScanner Class Definition  ________________________________

class ICPImageScanner(ICP):
    '''
    This class is useful when you want to apply ICP to two very large images and when there is
    reason to believe that the different sections of the images are not related in exactly the
    same manner with regard to the translational and rotational offsets. This will usually not
    be the case when the images are recorded with the regular frame cameras.  However, you can
    see non-constant offset relationships between the different regions of two images of the
    same scene when the images are put together by recording the pixels with sensors that are
    in motion. One example of this would be the satellites that are used for earth imaging --- 
    the satellites construct large images using what are known as pushbroom cameras.
    '''

    def __init__(self, *args, **kwargs ):
        if args:
            raise ValueError(  
                   '''ICPImageScanner constructor can only be called with keyword arguments for 
                      the following keywords: model_image_file, data_image_file, binary_or_gray_or_color,
                      corners_or_edges, size_for_calculations, scanning_window_width, scanning_window_height, 
                      iterations, subimage_index, and debug''')   
        model_image_file = data_image_file = scanning_window_width = scanning_window_height = subimage_index = min_brightness_level = min_area_threshold = max_area_threshold = iterations = corners_or_edges = debug = None
        if 'model_image_file' in kwargs              :   model_image_file = kwargs.pop('model_image_file')
        if 'data_image_file' in kwargs               :   data_image_file = kwargs.pop('data_image_file')
        if 'corners_or_edges' in kwargs              :   corners_or_edges=kwargs.pop('corners_or_edges')
        if 'subimage_index' in kwargs                :   subimage_index = kwargs.pop('subimage_index')
        if 'iterations' in kwargs                    :   iterations = kwargs.pop('iterations')
        if 'scanning_window_width' in kwargs         :   scanning_window_width = kwargs.pop('scanning_window_width')
        if 'scanning_window_height' in kwargs        :   scanning_window_height = kwargs.pop('scanning_window_height')
        ICP.__init__(self, **kwargs)
        if corners_or_edges == "corners":
            sys.exit("The scanner is not yet set for ICP with corner features. Sorry!")
        elif corners_or_edges == "edges":
            self.corners_or_edges = "edges"
        self.model_im_file = model_image_file
        self.data_im_file = data_image_file
        self.model_im = Image.open(model_image_file)
        self.data_im = Image.open(data_image_file)
        self.iterations = iterations
        self.scanning_window_width, self.scanning_window_height  =  scanning_window_width, scanning_window_height
        self.model_im_width, self.model_im_height = self.model_im.size[0], self.model_im.size[1]
        self.scanner_dump_directory_model = os.path.splitext(model_image_file)[0] + "_scanner_dump"
        self.scanner_dump_directory_data = os.path.splitext(data_image_file)[0] + "_scanner_dump"
        if subimage_index is not None:
            self.subimage_index = subimage_index
            self.model_subimage_file = self.scanner_dump_directory_model + "/subimage_" + str(subimage_index) +".jpg"
            self.data_subimage_file = self.scanner_dump_directory_data + "/subimage_" + str(subimage_index) + ".jpg"
            self.model_subimage = Image.open(self.model_subimage_file)
            self.data_subimage = Image.open(self.data_subimage_file)
        self.model_subimages_with_retained_pixels = None
        self.total_num_window_pos = None
        if debug:                             
            self.debug = debug
        else:
            self.debug = 0

    def apply_icp_to_model_and_data_scanner_dumps_and_show_intermediate_results(self):
        '''
        The purpose of this method is to apply ICP to ALL the subimage pairs in the two scanner dump
        directories, one for the model image and the other for the data image.  This method visually
        displays the results of ICP matching for EACH pair of subimages (one for the model and the
        other for the data) produced by the scanner in the form a movie.  This method also displays 
        the intermediate results obtained for each pair of subimages.
        '''
        if ( (not os.path.exists(self.scanner_dump_directory_model)) or 
             (len(glob.glob(self.scanner_dump_directory_model + "/*")) == 0) or
             (not os.path.exists(self.scanner_dump_directory_data)) or 
             (len(glob.glob(self.scanner_dump_directory_data + "/*")) == 0) ):
            sys.exit("Before you call apply_icp_to_model_and_data_scanner_dumps_and_show_intermediate_results(), you must create a scan dump by running the scanner.  See image scanning scripts in the ExamplesICPImageScanner directory for why.")
        self.displayImage6(self.model_im, "input model image -- close window when done viewing")
        self.displayImage6(self.data_im, "input data image -- close window when done viewing")
        self.model_image_width, self.model_image_height = self.model_im.size
        self.data_image_width, self.data_image_height = self.data_im.size
        print("size of the model image is: %s" % str((self.model_image_width,self.model_image_height)))
        print("size of the data image is: %s" % str((self.data_image_width,self.data_image_height)))
        self.horiz_positions_of_scan_window = self.model_im_width // self.scanning_window_width
        self.vert_positions_of_scan_window = self.model_im_height // self.scanning_window_height
        total_scan_window_positions = self.horiz_positions_of_scan_window * self.vert_positions_of_scan_window
        self.model_subimages_with_retained_pixels = [None] * total_scan_window_positions
        for modelfile,datafile in zip( sorted(glob.glob(self.scanner_dump_directory_model + "/*"), key=lambda x: file_index(x)),
                                       sorted(glob.glob(self.scanner_dump_directory_data + "/*"), key=lambda x: file_index(x)) ):
            try:
                print("\n\nApplying ICP to image blocks in files %s and %s" % (modelfile,datafile))
                self.calculate_icp_for_one_pair_of_subimages_and_display_results(modelfile, datafile, file_index(modelfile))
            except: pass

    def apply_icp_to_model_and_data_scanner_dumps_fast(self):

        '''
        Like the previous method, the purpose of this method is also to apply ICP to ALL the subimage 
        pairs in the two scanner dump directories, one for the model image and the other for the data image. 
        This method, however, does NOT display separately the ICP matching results for each pair of
        subimages.
        '''
        if ( (not os.path.exists(self.scanner_dump_directory_model)) or 
             (len(glob.glob(self.scanner_dump_directory_model + "/*")) == 0) or
             (not os.path.exists(self.scanner_dump_directory_data)) or 
             (len(glob.glob(self.scanner_dump_directory_data + "/*")) == 0) ):
            sys.exit("Before you call apply_icp_to_model_and_data_scanner_dumps_and_show_intermediate_results(), you must create a scan dump by running the scanner.  See image scanning scripts in the ExamplesICPImageScanner directory for why.")
        self.model_image_width, self.model_image_height = self.model_im.size
        self.data_image_width, self.data_image_height = self.data_im.size
        self.horiz_positions_of_scan_window = self.model_im_width // self.scanning_window_width
        self.vert_positions_of_scan_window = self.model_im_height // self.scanning_window_height
        total_scan_window_positions = self.horiz_positions_of_scan_window * self.vert_positions_of_scan_window
        self.model_subimages_with_retained_pixels = [None] * total_scan_window_positions
        for modelfile,datafile in zip( sorted(glob.glob(self.scanner_dump_directory_model + "/*"), key=lambda x: file_index(x)),
                                       sorted(glob.glob(self.scanner_dump_directory_data + "/*"), key=lambda x: file_index(x)) ):
            try:
                print("\n\nApplying ICP to image blocks in files %s and %s" % (modelfile,datafile))
                self.calculate_icp_for_one_pair_of_subimages_fast(modelfile, datafile, file_index(modelfile))
            except: pass

    def calculate_icp_for_one_pair_of_subimages_and_display_results(self, modelfile=None, datafile=None, subimage_index=None):
        '''
        Assuming that you have already run the image scanner on the model and the data images, you invoke
        this method to apply ICP to one corresponding pair of subimages in the two scanner dump directories.
        '''
        if (( not os.path.exists(self.scanner_dump_directory_model)) or 
            (len(glob.glob(self.scanner_dump_directory_model + "/*")) == 0) or 
            (not os.path.exists(self.scanner_dump_directory_data)) or 
            (len(glob.glob(self.scanner_dump_directory_data + "*")) == 0)):
            sys.exit("Before invoking caculate_icp_for_one_pair_of_subimages_and_display_results(), you must first create scan dump of subimages by invoking the image scanner code.  See the relevant example script in the ExamplesScanner directory for why.")
        if (modelfile is None) and (datafile is None):
            model_subimage_file = self.model_subimage_file
            data_subimage_file = self.data_subimage_file
        else:
            model_subimage_file = modelfile
            data_subimage_file = datafile  
            self.model_subimage = Image.open(modelfile)
            self.data_subimage = Image.open(datafile)
            self.subimage_index = subimage_index
        # Make sure we have the info on how many positions of the scanning window horizontally and vertically:
        if self.model_subimages_with_retained_pixels is None:
            self.horiz_positions_of_scan_window = self.model_im_width // self.scanning_window_width
            self.vert_positions_of_scan_window = self.model_im_height // self.scanning_window_height
            total_scan_window_positions = self.horiz_positions_of_scan_window * self.vert_positions_of_scan_window
            self.model_subimages_with_retained_pixels = [None] * total_scan_window_positions
        # Now construct an instance of the ICP class:
        icp = ICP(
               binary_or_color = self.binary_or_color,
               corners_or_edges = self.corners_or_edges,
               calculation_image_size = 200,
               max_num_of_pixels_used_for_icp = 300,
               pixel_correspondence_dist_threshold = 20,
               iterations = self.iterations,
               model_image =  model_subimage_file,
               data_image = data_subimage_file,
               subimage_index = self.subimage_index,
            )
        # Extract low-level information from the two corresponding subimages:
        self._extract_pixels_from_subimage('model')
        self._extract_pixels_from_subimage('data') 
        # Initialize the variables in the ICP instance:
        icp.model_list = self.model_list
        icp.data_list = self.data_list
        icp.model_im = self.model_subim_result
        icp.data_im = self.data_subim_result
        # Store away the pixels retained for ICP calculation.     
        self.model_subimages_with_retained_pixels[self.subimage_index] = self.model_subim_result
        # Now call the ICP algorithm:
        icp.icp()
        self.display_subimage_pair_used_for_edge_based_icp()
        icp.display_results_as_movie()
#        icp.cleanup_directory()

    def calculate_icp_for_one_pair_of_subimages_fast(self, modelfile=None, datafile=None, subimage_index=None):
        '''
        Assuming that you have already run the image scanner on the model and the data images, you invoke
        this method to apply ICP to one corresponding pair of subimages in the two scanner dump directories.
        '''
        if (( not os.path.exists(self.scanner_dump_directory_model)) or 
            (len(glob.glob(self.scanner_dump_directory_model + "/*")) == 0) or 
            (not os.path.exists(self.scanner_dump_directory_data)) or 
            (len(glob.glob(self.scanner_dump_directory_data + "*")) == 0)):
            sys.exit("Before invoking caculate_icp_for_one_pair_of_subimages_and_display_results(), you must first create scan dump of subimages by invoking the image scanner code.  See the relevant example script in the ExamplesScanner directory for why.")
        if (modelfile is None) and (datafile is None):
            model_subimage_file = self.model_subimage_file
            data_subimage_file = self.data_subimage_file
        else:
            model_subimage_file = modelfile
            data_subimage_file = datafile  
            self.model_subimage = Image.open(modelfile)
            self.data_subimage = Image.open(datafile)
            self.subimage_index = subimage_index
        # Make sure we have the info on how many positions of the scanning window horizontally and vertically:
        if self.model_subimages_with_retained_pixels is None:
            self.horiz_positions_of_scan_window = self.model_im_width // self.scanning_window_width
            self.vert_positions_of_scan_window = self.model_im_height // self.scanning_window_height
            total_scan_window_positions = self.horiz_positions_of_scan_window * self.vert_positions_of_scan_window
            self.model_subimages_with_retained_pixels = [None] * total_scan_window_positions
        # Now construct an instance of the ICP class:
        icp = ICP(
               binary_or_color = self.binary_or_color,
               corners_or_edges = self.corners_or_edges,
               calculation_image_size = 200,
               max_num_of_pixels_used_for_icp = 300,
               pixel_correspondence_dist_threshold = 20,
               iterations = self.iterations,
               model_image =  model_subimage_file,
               data_image = data_subimage_file,
               subimage_index = self.subimage_index,
            )
        # Extract low-level information from the two corresponding subimages:
        self._extract_pixels_from_subimage('model')
        self._extract_pixels_from_subimage('data') 
        # Initialize the variables in the ICP instance:
        icp.model_list = self.model_list
        icp.data_list = self.data_list
        icp.model_im = self.model_subim_result
        icp.data_im = self.data_subim_result
        # Store away the pixels retained for ICP calculation.          
        self.model_subimages_with_retained_pixels[self.subimage_index] = self.model_subim_result
        # Now call the ICP algorithm:
        icp.icp()

    def display_subimage_pair_used_for_edge_based_icp(self):
        '''
        For a given a subimage pair, one from the model image and the other from the data image, this
        method displays in the first row the overall model and data images along with a red-outlined
        rectangle in each to indicate what portion of the large images corresponds to the subimages.
        In the second row, this method shows the extracted model subimage, its edge map, and the retained
        edge pixels.  Finally, in the third row, this method shows the same as in the second row but
        for the data image.
        '''
        tk_images = []
        image_labels = []
        rootWindow = Tkinter.Tk()
        screen_width,screen_height =rootWindow.winfo_screenwidth(),rootWindow.winfo_screenheight()
        rootWindow.geometry( str(int(0.8 * screen_width)) + "x" + str(int(0.9 * screen_height)) + "+50+50") 
        canvas = Tkinter.Canvas(rootWindow)
        canvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=Tkinter.TRUE)
        scrollbar_x = Tkinter.Scrollbar(rootWindow,orient=Tkinter.HORIZONTAL,command=canvas.xview)
        scrollbar_y = Tkinter.Scrollbar(rootWindow,orient=Tkinter.VERTICAL,command=canvas.yview)
        scrollbar_x.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        scrollbar_y.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        canvas.configure(xscrollcommand=scrollbar_x.set)
        canvas.configure(yscrollcommand=scrollbar_y.set)
        def set_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        frame = Tkinter.Frame(canvas)
        canvas.create_window((0,0), window=frame, anchor=Tkinter.NW)
        frame.bind('<Configure>', set_scrollregion)
        cellwidth =  500
        padding = 10
        if cellwidth > 80:
            fontsize = 25
        else:
            fontsize = 15
        font = ImageFont.truetype(self.font_file, fontsize)

        model_image_width, model_image_height = self.model_im_width, self.model_im_height

        original_model_im = self.model_im.copy()
        original_data_im  = self.data_im.copy()

        self.num_horiz_positions_for_subimages = model_image_width // self.scanning_window_width
        self.num_vert_positions_for_subimages = model_image_height // self.scanning_window_height
        vert_pos_index_for_subimage = self.subimage_index // self.num_horiz_positions_for_subimages
        horz_pos_index_for_subimage = self.subimage_index - vert_pos_index_for_subimage * self.num_horiz_positions_for_subimages
        ulcx = upper_left_corner_x = horz_pos_index_for_subimage * self.scanning_window_width
        ulcy = upper_left_corner_y = vert_pos_index_for_subimage * self.scanning_window_height

        draw1 = ImageDraw.Draw(original_model_im)
        draw2 = ImageDraw.Draw(original_data_im)
        outline_width = 10
        for i in range(outline_width):
            draw1.rectangle((ulcx+i, ulcy+i, ulcx+self.scanning_window_width+i, ulcy+self.scanning_window_height+i), fill=None, outline='red')
            draw2.rectangle((ulcx+i, ulcy+i, ulcx+self.scanning_window_width+i, ulcy+self.scanning_window_height+i), fill=None, outline='red')

        original_model_subimage = self.model_subimage.copy()
        original_data_subimage = self.data_subimage.copy()
        displayWidth,displayHeight = None,None
        if model_image_width > model_image_height:
            displayWidth = int(0.9 * cellwidth)
            displayHeight = int(displayWidth * model_image_height * 1.0 / model_image_width)
        else:
            displayHeight = int(0.9 * cellwidth)
            displayWidth = int(displayHeight * model_image_width * 1.0 / model_image_height )
        # These thumbnails are needed for the first row of the display.
        original_model_im.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        original_data_im.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        # make thumbnail of the original model subimage 
        original_model_subimage = original_model_subimage.resize((model_image_width, model_image_height), Image.ANTIALIAS)
        original_model_subimage.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        # make thumbnail of the original data subimage
        original_data_subimage = original_data_subimage.resize((model_image_width, model_image_height), Image.ANTIALIAS)
        original_data_subimage.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        # make thumbnail of the model edge map subimage
        model_edge_map = self.model_subim_edge_map.copy()
        model_edge_map = model_edge_map.resize((model_image_width, model_image_height), Image.ANTIALIAS)
        model_edge_map.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        # make thumbnail of the model edge-pixels-retained subimage
        model_im_res = self.model_subim_result.copy()
        model_im_res = model_im_res.resize((model_image_width,model_image_height), Image.ANTIALIAS)
        model_im_res.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        # make thumbnail of the data edge map subimage
        data_edge_map = self.data_subim_edge_map.copy()
        data_edge_map = data_edge_map.resize((model_image_width, model_image_height), Image.ANTIALIAS)
        data_edge_map.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        # make thumbnail of the data edge-pixels-retained subimage
        data_im_res = self.data_subim_result.copy()
        data_im_res = data_im_res.resize((model_image_width, model_image_height), Image.ANTIALIAS)
        data_im_res.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        # show the original model and the data images side by side:
        image_labels.append("Original Model Image")
        tk_images.append(ImageTk.PhotoImage( original_model_im ))
        image_labels.append("Original Data Image")
        tk_images.append(ImageTk.PhotoImage( original_data_im ))
        # model subimage, followed by its edge map, followed by the edge pixels retained:
        image_labels.append("Model Subimage")
        tk_images.append(ImageTk.PhotoImage( original_model_subimage ))
        image_labels.append("Model Edge Map")
        tk_images.append(ImageTk.PhotoImage( model_edge_map ))
        image_labels.append("Edge Pixels Retained")
        tk_images.append(ImageTk.PhotoImage( model_im_res ))
        # data subimage, followed by its edge map, followed by the edge pixels retained:
        image_labels.append("Data Subimage")
        tk_images.append(ImageTk.PhotoImage( original_data_subimage ))
        image_labels.append("Data Edge Map")
        tk_images.append(ImageTk.PhotoImage( data_edge_map ))
        image_labels.append("Edge Pixels Retained")
        tk_images.append(ImageTk.PhotoImage( data_im_res ))
        # now stuff images into the frame object associated with the canvas:
        ##  NOTE that the arguments to range() are hardcoded to integers because this display is supposed
        ##    to show ONLY two images in the first row, one for the model image and the other for the data image.
        ##    The for loop then creates two more rows of image displays, with the first of these for the model
        ##    subimage and the second for the data subimage.  In each of these two rows, you start with the 
        ##    subimage, followed by its edge map, and followed by the map of the edge pixels retained.
        for i in range(2):
            Tkinter.Label(frame,image=tk_images[i], text=image_labels[i], font=fontsize, compound=Tkinter.BOTTOM, width=cellwidth).grid(row=0,column=i,padx=10,pady=30)
        for i in range(2,8):
            Tkinter.Label(frame,image=tk_images[i], text=image_labels[i], font=fontsize, compound=Tkinter.BOTTOM, width=cellwidth).grid(row=1,column=i-2,padx=10,pady=30)
        '''
        for i in range(2,5):
            Tkinter.Label(frame,image=tk_images[i], text=image_labels[i], font=fontsize, compound=Tkinter.BOTTOM, width=cellwidth).grid(row=1,column=i-2,padx=10,pady=30)
        for i in range(5,8):
            Tkinter.Label(frame,image=tk_images[i], text=image_labels[i], font=fontsize, compound=Tkinter.BOTTOM, width=cellwidth).grid(row=2,column=i-5,padx=10,pady=30)
        '''
        messageFrame = Tkinter.Frame(frame, width=displayWidth, height=displayHeight).grid(row=2,padx=10,pady=50)
        messageLabelText = Tkinter.StringVar()
        Tkinter.Label(messageFrame,
                      textvariable = messageLabelText,
                      font = 2 * fontsize,
                      anchor = 'c',
                      relief = 'groove',
                     ).pack(side='top', padx=10, pady=10)
        messageLabelText.set('''Close this window to see a movie of image registration''')
        Tkinter.mainloop()
        
    def chop_model_and_data_images_into_tiles_interactive(self):
        '''
        This method creates a dump of subimages extracted from large model and data images.  The
        method is interactive in the sense that it shows the user each subimage for his/her 
        examination before storing it in a dump directory.
        '''
        for image_type in ('model','data'):
            scanner_dump_directory = self.scanner_dump_directory_model if image_type == 'model' else self.scanner_dump_directory_data
            self.displayImage6(self.model_im if image_type == 'model' else self.data_im, "input_image -- close window when done viewing")
            M,N = self.scanning_window_width, self.scanning_window_height
            image = self.model_im.copy() if image_type == 'model' else self.data_im.copy()
            self.image_width,self.image_height = self.model_im.size if image_type == 'model' else self.data_im.size
            print("size of the image is: %s" % str((self.image_width,self.image_height)))
            self.array_R = numpy.zeros((N, M), dtype="int")
            self.array_G = numpy.zeros((N, M), dtype="int")
            self.array_B = numpy.zeros((N, M), dtype="int")
            mw = Tkinter.Tk()
            winsize_x,winsize_y = None,None
            screen_width,screen_height = mw.winfo_screenwidth(),mw.winfo_screenheight()
            if screen_width <= screen_height:
                winsize_x = int(0.5 * screen_width)
                winsize_y = int(winsize_x * (self.image_height * 1.0 / self.image_width))            
            else:
                winsize_y = int(0.5 * screen_height)
                winsize_x = int(winsize_y * (self.image_width * 1.0 / self.image_height))
            image = image.resize((winsize_x,winsize_y), Image.ANTIALIAS)
            mw.title( "Image scanner in action" ) 
            mw.configure( height = winsize_y, width = winsize_x )         
            self.canvas = Tkinter.Canvas( mw,                         
                                 height = winsize_y,            
                                 width = winsize_x,             
                                 cursor = "crosshair" )   
            self.canvas.pack(fill=BOTH, expand=True)
            photo = ImageTk.PhotoImage( image )
            self.canvas.create_image(winsize_x//2,winsize_y//2,image=photo)
            self.scale_x = winsize_x / (self.image_width * 1.0)
            self.scale_y = winsize_y / (self.image_height * 1.0) 
            print("\nx_scale: %f" % self.scale_x)
            print("y_scale: %f" % self.scale_y)
            horizontal_positions_of_scan_window = self.image_width // self.scanning_window_width
            vertical_positions_of_scan_window = self.image_height // self.scanning_window_height
            total_scan_window_positions = horizontal_positions_of_scan_window * vertical_positions_of_scan_window
            self.rect = self.canvas.create_rectangle((0, 0, int(M*self.scale_x), 
                                                             int(N*self.scale_y)), width='7', outline='red') 
            self.canvas.update()
            self.horizontal_positions_of_scan_window = horizontal_positions_of_scan_window
            self.vertical_positions_of_scan_window = vertical_positions_of_scan_window
            if os.path.exists(scanner_dump_directory):
                files = glob.glob(scanner_dump_directory + "/*")
                map(lambda x: os.remove(x), files)
            else:
               os.mkdir(scanner_dump_directory)
            self.moves_horizontal = self.image_width // self.scanning_window_width - 1
            self.moves_vertical = self.image_height // self.scanning_window_height - 1
            self.delta_x = int(self.scanning_window_width * self.scale_x)
            self.delta_y = int(self.scanning_window_height * self.scale_y)
            self.x_incr, self.y_incr = 0,0
            self.old_posx, self.old_posy = 0,0
            self.total_num_window_pos = (self.moves_horizontal + 1) * (self.moves_vertical + 1)
            self.num_remaining_pos = self.total_num_window_pos
            self.block_index = 0
            print("horizontal moves max index: %d" % self.moves_horizontal)
            print("vertical moves max index: %d" % self.moves_vertical)
            self._move(image_type)
            mw.mainloop()

    def display_results_for_all_subimage_pairs_together_as_a_movie(self):
        '''
        This method shows in the form of a "movie" the ICP matching for ALL the subimages extracted
        from the large model and data images.  This method is meant to be called when you DO WANT 
        to see the intermediate results for each subimage.  Production of the intermediate results
        also colorizes the pixels of the data subimages for all different iterations.
        '''
        if (self.horiz_positions_of_scan_window is None) or (self.vert_positions_of_scan_window is None):
            self.horiz_positions_of_scan_window = self.model_im_width // self.scanning_window_width
            self.vert_positions_of_scan_window = self.model_im_height // self.scanning_window_height
        total_scan_window_positions = self.horiz_positions_of_scan_window * self.vert_positions_of_scan_window
        if self.scanning_window_width > self.scanning_window_height:
            cell_width = cell_height = self.scanning_window_width + 10
        else:
            cell_width = cell_height = self.scanning_window_height + 10
        def onFrameConfigure(canvas):
            '''Reset the scroll region to encompass the inner frame'''
            canvas.configure(scrollregion=canvas.bbox("all"))
        root = Tkinter.Tk()
        # set the dimensions of the movie window and where it is placed
        w = int(0.7 * root.winfo_screenwidth())
        h = int(0.7 * root.winfo_screenheight())
        x = int(0.1 * root.winfo_screenwidth())
        y = int(0.1 * root.winfo_screenheight())
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        root.title("the movie window")
        canvasroot = Tkinter.Canvas(root, width=int(0.5 * w), height=int(0.5 * h))
        # Create a rootframe on the canvas for showing the movie.  We need the canvas
        # widget because of its support for the scrollbars:
        rootframe = Tkinter.Frame(canvasroot, background="#ffffff")
        canvasroot.create_window((4,4), window=rootframe, anchor="nw", tags="rootframe")
        vsb = Tkinter.Scrollbar(root, orient="vertical", command=canvasroot.yview)
        hsb = Tkinter.Scrollbar(root, orient="horizontal", command=canvasroot.xview)
        canvasroot.configure(yscrollcommand=vsb.set)
        canvasroot.configure(xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="top", fill="x")     
        canvasroot.pack(side="left", fill="both", expand=True)
        rootframe.place(relx=0.5, rely=0.35, anchor=CENTER)
        rootframe.bind("<Configure>", lambda event, canvas=canvasroot: onFrameConfigure(canvasroot))
        imageframe = rootframe
        # Declare the array variables to be used later:
#        colors = ('white','blue','red','black')
        colors = ('white','white','white','white')
        frames = [ [None for _ in range(self.horiz_positions_of_scan_window)] 
                                                for _ in range(self.vert_positions_of_scan_window)]
        model_images = [ [None for _ in range(self.horiz_positions_of_scan_window)] 
                                                for _ in range(self.vert_positions_of_scan_window)]
        model_color_images = [ [None for _ in range(self.horiz_positions_of_scan_window)] 
                                                for _ in range(self.vert_positions_of_scan_window)]
        tkim = [ [ [None for _ in range(self.iterations)] for _ in range(self.horiz_positions_of_scan_window)] 
                                                for _ in range(self.vert_positions_of_scan_window)]
        label_image = [ [ [None for _ in range(self.iterations)] for _ in range(self.horiz_positions_of_scan_window)] 
                                                for _ in range(self.vert_positions_of_scan_window)]
        out_photo_image = [ [ [None for _ in range(self.iterations)] 
                                                    for _ in range(self.horiz_positions_of_scan_window)] 
                                                    for _ in range(self.vert_positions_of_scan_window)]
        # Create a grid structure for the movie with cell consisting of a Tkinter Frame object.
        for row in range(self.vert_positions_of_scan_window):
            for col in range (self.horiz_positions_of_scan_window):
                frames[row][col] = Tkinter.Frame(imageframe, width=cell_width, height=cell_height, bg=colors[(row*self.horiz_positions_of_scan_window+col) % len(colors)])
                frames[row][col].grid(row=row, column=col, sticky=W+E+N+S)
                model_im_index = row * self.horiz_positions_of_scan_window + col  
                model_images[row][col] = self.model_subimages_with_retained_pixels[model_im_index]
        colspan = self.horiz_positions_of_scan_window
        rownext = self.vert_positions_of_scan_window
        # Now add the notification widgets:
        iterationIndexFrame = Tkinter.Frame(canvasroot, height=50)
        iterationLabelText = Tkinter.StringVar()
        Tkinter.Label(iterationIndexFrame,
                      textvariable = iterationLabelText,
                      anchor = 'c',
                      relief = 'groove',
                     ).pack(side='top', padx=10, pady=10)
        iterationLabelText.set( "This is for showing the iterations" )
        iterationIndexFrame.place(relx=0.5, rely=0.7, anchor=CENTER)
        buttonframe = Tkinter.Frame(canvasroot)
        tkFont.nametofont('TkDefaultFont').configure(size=15)    
        helv36 = tkFont.Font(family="Helvetica", size=18, weight='bold')    
        Tkinter.Button(buttonframe, 
                       text = 'Play movie again',                
                       anchor = 'c',
                       relief = 'raised',
                       font = helv36,
                       command = lambda: self.callbak(canvasroot)
                      ).pack(side='top', padx=10, pady=5)
        buttonframe.place(relx=0.5, rely=0.8, anchor=CENTER)
        messageFrame = Tkinter.Frame(canvasroot)
        messageLabelText = Tkinter.StringVar()
        Tkinter.Label(messageFrame,
                      textvariable = messageLabelText,
                      anchor = 'c',
                      relief = 'groove',
                     ).pack(side='top', padx=10, pady=10)
        messageLabelText.set("NOTE: It is best to NOT close this window\nuntil all iterations are completed.")
        messageFrame.place(relx=0.5, rely=0.9, anchor=CENTER)
        # colorize the model subimages:
        print("\nColorizing the retained-pixels images as obtained from the model subimages --- could take a while")
        for row in range(self.vert_positions_of_scan_window):
            for col in range (self.horiz_positions_of_scan_window):
                print("colorizing model subimage at (%d,%d)" % (row,col))
                imwidth,imheight = model_images[row][col].size
                (mingray,maxgray) = model_images[row][col].getextrema()
                model_color_images[row][col] = Image.new("RGB", (imwidth,imheight), (0,0,0))
                for m in range(imwidth):
                    for n in range(imheight):
                        color_val = model_images[row][col].getpixel((m,n)) * int(255/maxgray)
                        model_color_images[row][col].putpixel((m,n), (color_val, 0, 0))
                        dir_index = row * self.horiz_positions_of_scan_window + col  
        # Now run the movie:
        self.iteration_control_flag = 1
        while self.iteration_control_flag:
            for i in range(0,self.iterations):
                try:
                    for row in range(self.vert_positions_of_scan_window):
                        for col in range(self.horiz_positions_of_scan_window):        
                            dir_index = row * self.horiz_positions_of_scan_window + col  
                            tkim[row][col][i] = Image.open("__result_" + str(dir_index) + "/__result_color" + str(i) + ".jpg")
                            out_image = ImageChops.add( model_color_images[row][col], tkim[row][col][i] )
                            out_out_image = out_image.resize((self.scanning_window_width,self.scanning_window_height), Image.ANTIALIAS)
                            out_photo_image[row][col][i] = ImageTk.PhotoImage( out_out_image )
                            label_image[row][col][i] = Tkinter.Label(frames[row][col],image=out_photo_image[row][col][i],borderwidth=2,relief="solid")
                            label_image[row][col][i].place(relx=0.02,rely=0.02,relwidth=0.98,relheight=0.98)
                    iterationLabelText.set( "Iteration Number: " + str(i+1) + "/" + str(self.iterations) )
                    self.iteration_control_flag = 0
                    if i < self.iterations - 1: root.after(1000, root.quit)       
                    root.mainloop(0)
                except IOError: pass

    def display_results_for_all_subimage_pairs_together_as_a_movie_with_colorization(self):
        '''
        This method shows in the form of a "movie" the ICP matching for ALL the subimages extracted
        from the large model and data images.  This method is meant to be called when you do NOT 
        want to see the intermediate results for each subimage.  Note that it is the production of
        the intermediate results that colorizes the pixels needed for the movie display.  Therefore
        when for the sake of speed you opt for not seeing the intermediate results, you need to 
        execute the pixel colorization code separately.  That is the main difference between the
        previous method and this method.
        '''
        if (self.horiz_positions_of_scan_window is None) or (self.vert_positions_of_scan_window is None):
            self.horiz_positions_of_scan_window = self.model_im_width // self.scanning_window_width
            self.vert_positions_of_scan_window = self.model_im_height // self.scanning_window_height
        total_scan_window_positions = self.horiz_positions_of_scan_window * self.vert_positions_of_scan_window
        if self.scanning_window_width > self.scanning_window_height:
            cell_width = cell_height = self.scanning_window_width + 10
        else:
            cell_width = cell_height = self.scanning_window_height + 10
        def onFrameConfigure(canvas):
            '''Reset the scroll region to encompass the inner frame'''
            canvas.configure(scrollregion=canvas.bbox("all"))
        root = Tkinter.Tk()
        # set the dimensions of the movie window and where it is placed
        w = int(0.7 * root.winfo_screenwidth())
        h = int(0.7 * root.winfo_screenheight())
        x = int(0.1 * root.winfo_screenwidth())
        y = int(0.1 * root.winfo_screenheight())
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        root.title("the movie window")
        canvasroot = Tkinter.Canvas(root, width=int(0.5 * w), height=int(0.5 * h))
        # Create a rootframe on the canvas for showing the movie.  We need the canvas
        # widget because of its support for the scrollbars:
        rootframe = Tkinter.Frame(canvasroot, background="#ffffff")
        canvasroot.create_window((4,4), window=rootframe, anchor="nw", tags="rootframe")
        vsb = Tkinter.Scrollbar(root, orient="vertical", command=canvasroot.yview)
        hsb = Tkinter.Scrollbar(root, orient="horizontal", command=canvasroot.xview)
        canvasroot.configure(yscrollcommand=vsb.set)
        canvasroot.configure(xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="top", fill="x")     
        canvasroot.pack(side="left", fill="both", expand=True)
        rootframe.place(relx=0.5, rely=0.35, anchor=CENTER)
        rootframe.bind("<Configure>", lambda event, canvas=canvasroot: onFrameConfigure(canvasroot))
        imageframe = rootframe
        # Declare the array variables to be used later:
#        colors = ('white','blue','red','black')
        colors = ('white','white','white','white')
        frames = [ [None for _ in range(self.horiz_positions_of_scan_window)] 
                                                for _ in range(self.vert_positions_of_scan_window)]
        model_images = [ [None for _ in range(self.horiz_positions_of_scan_window)] 
                                                for _ in range(self.vert_positions_of_scan_window)]
        model_color_images = [ [None for _ in range(self.horiz_positions_of_scan_window)] 
                                                for _ in range(self.vert_positions_of_scan_window)]
        tkim = [ [ [None for _ in range(self.iterations)] for _ in range(self.horiz_positions_of_scan_window)] 
                                                for _ in range(self.vert_positions_of_scan_window)]
        label_image = [ [ [None for _ in range(self.iterations)] for _ in range(self.horiz_positions_of_scan_window)] 
                                                for _ in range(self.vert_positions_of_scan_window)]
        out_photo_image = [ [ [None for _ in range(self.iterations)] 
                                                    for _ in range(self.horiz_positions_of_scan_window)] 
                                                    for _ in range(self.vert_positions_of_scan_window)]
        # Create a grid structure for the movie with cell consisting of a Tkinter Frame object.
        for row in range(self.vert_positions_of_scan_window):
            for col in range (self.horiz_positions_of_scan_window):
                frames[row][col] = Tkinter.Frame(imageframe, width=cell_width, height=cell_height, bg=colors[(row*self.horiz_positions_of_scan_window+col) % len(colors)])
                frames[row][col].grid(row=row, column=col, sticky=W+E+N+S)
                model_im_index = row * self.horiz_positions_of_scan_window + col  
                model_images[row][col] = self.model_subimages_with_retained_pixels[model_im_index]
        colspan = self.horiz_positions_of_scan_window
        rownext = self.vert_positions_of_scan_window
        # Now add the notification widgets:
        iterationIndexFrame = Tkinter.Frame(canvasroot, height=50)
        iterationLabelText = Tkinter.StringVar()
        Tkinter.Label(iterationIndexFrame,
                      textvariable = iterationLabelText,
                      anchor = 'c',
                      relief = 'groove',
                     ).pack(side='top', padx=10, pady=10)
        iterationLabelText.set( "This is for showing the iterations" )
        iterationIndexFrame.place(relx=0.5, rely=0.7, anchor=CENTER)
        buttonframe = Tkinter.Frame(canvasroot)
        tkFont.nametofont('TkDefaultFont').configure(size=15)    
        helv36 = tkFont.Font(family="Helvetica", size=18, weight='bold')    
        Tkinter.Button(buttonframe, 
                       text = 'Play movie again',                
                       anchor = 'c',
                       relief = 'raised',
                       font = helv36,
                       command = lambda: self.callbak(canvasroot)
                      ).pack(side='top', padx=10, pady=5)
        buttonframe.place(relx=0.5, rely=0.8, anchor=CENTER)
        messageFrame = Tkinter.Frame(canvasroot)
        messageLabelText = Tkinter.StringVar()
        Tkinter.Label(messageFrame,
                      textvariable = messageLabelText,
                      anchor = 'c',
                      relief = 'groove',
                     ).pack(side='top', padx=10, pady=10)
        messageLabelText.set("NOTE: It is best to NOT close this window\nuntil all iterations are completed.")
        messageFrame.place(relx=0.5, rely=0.9, anchor=CENTER)
        # colorize the model subimages:
        print("\nColorizing the retained-pixels images as obtained from the model subimages --- could take a while")
        for row in range(self.vert_positions_of_scan_window):
            for col in range (self.horiz_positions_of_scan_window):
                print("colorizing model subimage at (%d,%d)" % (row,col))
                imwidth,imheight = model_images[row][col].size
                (mingray,maxgray) = model_images[row][col].getextrema()
                model_color_images[row][col] = Image.new("RGB", (imwidth,imheight), (0,0,0))
                for m in range(imwidth):
                    for n in range(imheight):
                        color_val = model_images[row][col].getpixel((m,n)) * int(255/maxgray)
                        model_color_images[row][col].putpixel((m,n), (color_val, 0, 0))
                        dir_index = row * self.horiz_positions_of_scan_window + col  
        # Construct color versions of the result images (these are images with the retained pixels) in 
        # the __result_X drectories:
        print("""\nColorizing the retained-pixels images as obtained from the data subimages for each of the iterations"""
              """ of the ICP algorithm.  Depending on the number of iterations, this step could take a while.""")
        self.dir_rootname_for_results = "__result_"
        for row in range(self.vert_positions_of_scan_window):
            for col in range (self.horiz_positions_of_scan_window):
                for i in range(0,self.iterations):
                    dir_index = row * self.horiz_positions_of_scan_window + col  
                    self.dir_name_for_results = self.dir_rootname_for_results + str(dir_index)
                    result_im = Image.open(self.dir_name_for_results + "/__result" + str(i) + ".jpg")
                    (mingray,maxgray) = result_im.getextrema()
                    rwidth,rheight = result_im.size
                    result_color_im = Image.new("RGB", (rwidth,rheight), (0,0,0))
                    for m in range(rwidth):
                        for n in range(rheight):
                            if result_im.getpixel((m,n)) > 0:
                                color_val = result_im.getpixel((m,n)) * int(255/maxgray)
                                result_color_im.putpixel((m,n),(0,color_val,0))
                    result_color_im.save( self.dir_name_for_results + "/__result_color" + str(i) + ".jpg")
        # Now run the movie:
        self.iteration_control_flag = 1
        while self.iteration_control_flag:
            for i in range(0,self.iterations):
                try:
                    for row in range(self.vert_positions_of_scan_window):
                        for col in range(self.horiz_positions_of_scan_window):        
                            dir_index = row * self.horiz_positions_of_scan_window + col  
                            tkim[row][col][i] = Image.open("__result_" + str(dir_index) + "/__result_color" + str(i) + ".jpg")
                            out_image = ImageChops.add( model_color_images[row][col], tkim[row][col][i] )
                            out_out_image = out_image.resize((self.scanning_window_width,self.scanning_window_height), Image.ANTIALIAS)
                            out_photo_image[row][col][i] = ImageTk.PhotoImage( out_out_image )
                            label_image[row][col][i] = Tkinter.Label(frames[row][col],image=out_photo_image[row][col][i],borderwidth=2,relief="solid")
                            label_image[row][col][i].place(relx=0.02,rely=0.02,relwidth=0.98,relheight=0.98)
                    iterationLabelText.set( "Iteration Number: " + str(i+1) + "/" + str(self.iterations) )
                    self.iteration_control_flag = 0
                    if i < self.iterations - 1: root.after(1000, root.quit)       
                    root.mainloop(0)
                except IOError: pass

    def cleanup_scanner_examples_directory(self):
        for filename in glob.glob( '__result*/*' ):
            os.unlink(filename)
        for filename in glob.glob( '__model/*' ):
            os.unlink(filename)
        for directory_name in glob.glob( '__result*' ):
            os.rmdir(directory_name)
        os.rmdir('__model')

    #______________________  Private Methods of the ICPImageScanner Class  ____________________

    def _extract_pixels_from_subimage(self, model_or_data):
        if model_or_data == "model":
            im = self.model_subimage
        else:
            im = self.data_subimage
        im = im.convert('L')        ## convert to gray level
        im.thumbnail( (self.calculation_image_size, self.calculation_image_size), Image.ANTIALIAS )
        if self.debug: im.show()
        width,height = im.size
        if self.debug: print("width: %d    height: %d" % (width, height))
        dx = numpy.zeros((height, width), dtype="float")
        dy = numpy.zeros((height, width), dtype="float")
        rval = numpy.zeros((height, width), dtype="float")  # rval at a pixel = determinant / trace^2
        result_im = Image.new("1", (width,height), 0)
        edge_im = Image.new("L", (width,height), 0)
        edge_pixel_list = []    
        corner_pixels = []
        # Note that array indexing is 'opposite' of the image indexing with the first index along what 
        # is y for the image and the second index along what is x for the image.  For the image, x is 
        # the horizontal axis to the right, y is the vertical axis pointing downwards.  In what follows, 
        # we treat i and j as the image coordinates.  That is, i increments horizontally to the right
        # and j increments vertically downwards.
        for i in range(3,width-3):
            for j in range(3,height-3):
                ip1,im1,jp1,jm1 = i+1,i-1,j+1,j-1
                dx[(j,i)] = (im.getpixel((ip1,jm1)) + 2*im.getpixel((ip1,j)) + \
                             im.getpixel((ip1,jp1))) -  (im.getpixel((im1,jm1)) + \
                             2*im.getpixel((im1,j)) + im.getpixel((im1,jp1))) 
                dy[(j,i)] = (im.getpixel((im1,jp1)) + 2*im.getpixel((i,jp1)) + \
                             im.getpixel((ip1,jp1))) -  (im.getpixel((im1,jm1)) + \
                             2*im.getpixel((i,jm1)) + im.getpixel((ip1,jm1))) 
        edge_pixel_dict = {}
        for i in range(3,width-3):                 # i is for horizontal axis to the right
            for j in range(3,height-3):            # j is for vertical axis to the bottom
                edge_strength = math.sqrt(dx[(j,i)]**2 + dy[(j,i)]**2)
                edge_im.putpixel((i,j), int(edge_strength))   
                if edge_strength > self.edge_detection_threshold:            
                    edge_pixel_dict["e_" + str(i) + "_" + str(j)] = edge_strength
        sorted_edge_pixels = sorted(edge_pixel_dict.keys(), \
                                      key=lambda x: edge_pixel_dict[x], reverse=True)
        if len(sorted_edge_pixels) > self.max_num_of_pixels_used_for_icp:
            sorted_edge_pixels = sorted_edge_pixels[0:self.max_num_of_pixels_used_for_icp]
        for pixel_label in sorted_edge_pixels: 
            parts = re.split(r'_', pixel_label)
            i_index,j_index = int(parts[-2]), int(parts[-1])
            edge_pixel_list.append((i_index,j_index))
            result_im.putpixel((i_index,j_index), 255)
        if self.debug: result_im.show()
        if model_or_data == "model":
            if os.path.exists("__model"):
                files = glob.glob("__model/*")
                map(lambda x: os.remove(x), files)
            else:
               os.mkdir("__model")
            result_im.save("__model/__model_subimage" + str(self.subimage_index) + ".jpg")
            self.model_subim_result = result_im
            self.model_list = edge_pixel_list
            self.model_subim_edge_map = edge_im
            if self.debug: edge_im.save("model_edge_image.jpg")
        else:
            if self.debug: result_im.save("data_image_pixels_retained.jpg")
            self.data_subim_result = result_im
            self.data_list = edge_pixel_list
            self.data_subim_edge_map = edge_im
            if self.debug: edge_im.save("data_edge_image.jpg")

    def _move(self, image_type):
        self.num_remaining_pos -= 1
        print("Creating pixel values array for local window at block index: %d" % self.block_index)
        original_im = self.model_im if image_type == 'model' else self.data_im
        scanner_dump_directory = self.scanner_dump_directory_model if image_type == 'model' else self.scanner_dump_directory_data
        for x in range(self.x_incr * self.scanning_window_width, (self.x_incr + 1) * self.scanning_window_width):        
            for y in range(self.y_incr * self.scanning_window_height, (self.y_incr + 1) * self.scanning_window_height):
                r,g,b = original_im.getpixel((x,y))
                self.array_R[y % self.scanning_window_height, x % self.scanning_window_width] = r
                self.array_G[y % self.scanning_window_height, x % self.scanning_window_width] = g
                self.array_B[y % self.scanning_window_height, x % self.scanning_window_width] = b
        height,width = self.array_R.shape
        newimage = Image.new("RGB", (width,height), (0,0,0))
        for i in range(0, height):
            for j in range(0, width):
                r,g,b = self.array_R[i,j], self.array_G[i,j], self.array_B[i,j]
                newimage.putpixel((j,i), (r,g,b))
        newimage.save(scanner_dump_directory +  "/subimage_" + str(self.block_index) + ".jpg")
        width,height = newimage.size
        tk2 = Tkinter.Toplevel(takefocus = True)
        winsize_x,winsize_y = None,None
        screen_width,screen_height = tk2.winfo_screenwidth(),tk2.winfo_screenheight()
        if screen_width <= screen_height:
            winsize_x = int(0.5 * screen_width)
            winsize_y = int(winsize_x * (height * 1.0 / width))            
        else:
            winsize_y = int(0.5 * screen_height)
            winsize_x = int(winsize_y * (width * 1.0 / height))
        display_image = newimage.resize((winsize_x,winsize_y), Image.ANTIALIAS)
        tk2.title("scanned window")   
        frame = Tkinter.Frame(tk2, relief=RIDGE, borderwidth=2)
        frame.pack(fill=BOTH,expand=1)
        photo_image = ImageTk.PhotoImage( display_image )
        label = Tkinter.Label(frame, image=photo_image)
        label.pack(fill=X, expand=1)
        tk2.update()
        print("========= done with scan window display =========")
        response = pymsgbox.confirm("Done with viewing scan window?")
        if response == "OK": 
            tk2.after(10, self._callback, tk2)
        new_posx = self.old_posx + self.delta_x
        if new_posx + self.delta_x < int(self.image_width * self.scale_x):
            self.canvas.move( self.rect, self.delta_x, 0)
            self.old_posx = new_posx
            self.x_incr += 1
        elif self.old_posy + 2 * self.delta_y < int(self.image_height * self.scale_y):
            self.canvas.move( self.rect, -1 * self.moves_horizontal * self.delta_x, self.delta_y ) 
            self.old_posx = 0
            self.x_incr = 0
            self.old_posy += self.delta_y
            self.y_incr += 1    
        self.canvas.update()
        self.block_index += 1
        if self.num_remaining_pos > 0:
            self._move(image_type)

    def _move_noninteractive(self):
        if self.block_index == 0:
            time.sleep(1)             # one second
        self.num_remaining_pos -= 1
        print("Creating pixel values array for local window at block index: %d" % self.block_index)
        for x in range(self.x_incr * self.scanning_window_width, (self.x_incr + 1) * self.scanning_window_width):        
            for y in range(self.y_incr * self.scanning_window_height, (self.y_incr + 1) * self.scanning_window_height):
                r,g,b = self.original_im.getpixel((x,y))
                self.array_R[y % self.scanning_window_height, x % self.scanning_window_width] = r
                self.array_G[y % self.scanning_window_height, x % self.scanning_window_width] = g
                self.array_B[y % self.scanning_window_height, x % self.scanning_window_width] = b
        height,width = self.array_R.shape
        newimage = Image.new("RGB", (width,height), (0,0,0))
        for i in range(0, height):
            for j in range(0, width):
                r,g,b = self.array_R[i,j], self.array_G[i,j], self.array_B[i,j]
                newimage.putpixel((j,i), (r,g,b))
        newimage.save(self.scanner_dump_directory + "/subimage_" + str(self.block_index) + ".jpg")
        new_posx = self.old_posx + self.delta_x
        if new_posx + self.delta_x < int(self.image_width * self.scale_x):
            self.canvas.move( self.rect, self.delta_x, 0)
            self.old_posx = new_posx
            self.x_incr += 1
        elif self.old_posy + 2 * self.delta_y < int(self.image_height * self.scale_y):
            # we need to bring the window back from the last col to the first col in the next row:
            self.canvas.move( self.rect, -1 * self.moves_horizontal * self.delta_x, self.delta_y ) 
            self.old_posx = 0
            self.x_incr = 0
            self.old_posy += self.delta_y
            self.y_incr += 1
        self.canvas.update()
        self.block_index += 1
        if self.num_remaining_pos > 0:
            self._move_noninteractive()

    def _callback(self,arg):
        arg.destroy()

#_________________________  End of ICPImageScanner Class Definition ___________________________
