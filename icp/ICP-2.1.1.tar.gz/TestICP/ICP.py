__version__ = '2.1.0'
__author__  = "Avinash Kak (kak@purdue.edu)"
__date__    = '2017-November-20'
__url__     = 'https://engineering.purdue.edu/kak/distICP/ICP-2.1.0.html'
__copyright__ = "(C) 2017 Avinash Kak. Python Software Foundation."

__doc__ = '''

ICP.py

Version: ''' + __version__ + '''
   
Author: Avinash Kak (kak@purdue.edu)

Date: ''' + __date__ + '''


@title    
CHANGE LOG:

  Version 2.1.0: 

    This is a significant upgrade of the ICP module: (1) The module now
    comes with a new class named ICPImageScanner for dealing with the case
    when different portions of the two images, one for the model and the
    other for the data, are related to each other with different values for
    the translational and rotational offsets.  This can happen when large
    images are recorded by aggregating the data from sensors in motion (as
    is the case with earth imaging satellites that use pushbroom cameras
    and, in some cases, with the cameras mounted in UAVs). (2) The module
    now uses a more commonly available font file for the labels shown in
    the results. The default font is now FreeSerif.ttf from the Freefont
    family.  This version also gives you a constructor option to specify
    your own font file.  And, finally, (3) this version includes a bug fix
    in the calls to the putpixel() function.  This bugfix was needed in
    order for the module to work with the more recent Pillow library for
    PIL.

  Version 2.0:

    This is a Python 3.x compliant version of the module.  You should now
    be able to execute the module code with either Python 2.7 or Python 3.

  Version 1.3:

    This version is a major rewrite of the ICP module. While the previous
    versions of this module were useful primarily for binary images, the
    new version should also work well for grayscale and color images.  The
    new module also contains improvements to the implementation code for
    the core ICP algorithm.  It should be more forgiving should there exist
    no correspondents in one image for some of the pixels chosen for ICP
    calculations in the other image.  Finally, this version gives you two
    options for applying ICP to grayscale and color images: You can carry
    out either edge-based ICP or corner-pixels based ICP.

  Version 1.2:

    This version allows for a movie-like display of the superimposed model
    and data images.  This makes it much easier to see the convergence of
    the registration between the two images.  Another change in Version 1.2
    is a size reduction of large binary images to speed up the
    computations.  The size to which all images are now reduced is set by
    the 'calculation_image_size' parameter of the constructor.  Previously,
    only the color and the grayscale images were subject to such size
    reduction.  Version 1.2 also removes a bug in the mosaicked display of
    the results.

  Version 1.1:

    This version includes a new option for the constructor that lets the
    system decide as to which image to use as the model and which image as
    the data.  In general, for color and grayscale images, you get superior
    registration between the two images if the image that results in fewer
    pixels for ICP processing is used as the data image.  Version 1.1 also
    includes a better (although still extremely primitive) data generator
    for creating simple synthetic binary images that can be used to
    experiment with the ICP algorithm.


@title  
INSTALLATION:
                                                                                                   
    The ICP class was packaged using setuptools.  For installation, execute
    the following command in the source directory (this is the directory
    that contains the setup.py file after you have downloaded and
    uncompressed the package):
                                                                                                   
            sudo python setup.py install                                                           
                                                                                                   
    and/or, for the case of Python 3,                                                               
                                                                                                   
            sudo python3 setup.py install                                                          
                                                                                                   
    On Linux distributions, this will install the module file at a location                        
    that looks like                                                                                
                                                                                                   
             /usr/local/lib/python2.7/dist-packages/                                               
                                                                                                   
    and, for the case of Python 3, at a location that looks like                                    
                                                                                                   
             /usr/local/lib/python3.5/dist-packages/

    If you do not have root access, you have the option of working directly
    off the directory in which you downloaded the software by simply
    placing the following statements at the top of your scripts that use
    the ICP class:

        import sys
        sys.path.append( "pathname_to_ICP_directory" )

    To uninstall the module, simply delete the source directory, locate
    where ICP was installed with "locate ICP" and delete those files.  As
    mentioned above, the full pathname to the installed version is likely
    to look like /usr/local/lib/python2.7/dist-packages/ICP*

    If you want to carry out a non-standard install of the ICP module,
    look up the on-line information on Disutils by pointing your
    browser to

          http://docs.python.org/dist/dist.html


@title
INTRODUCTION:

    ICP stands for the Iterative Closest Point algorithm. ICP algorithms
    are used to align two datasets in a multi-dimensional space by
    iteratively applying rotations and translations to one dataset until it
    is aligned with the other dataset.

    In image processing and computer vision, ICP can be used to align a
    data image recorded through a sensor with a model image that is
    produced by a geographic information system (GIS).  A typical
    application would be a UAV recording images as it flies over a terrain.
    A successful alignment between such sensor produced images and the 
    model images produced by an on-board or satellite-connected GIS system
    would enable precise computation of the position and the orientation 
    of the UAV vis-a-vis the terrain.

    The main goal of the pure-Python implementation of ICP presented here
    is to make it easier to experiment with the different aspects of such
    algorithms.


@title
USAGE:

    You have two modes for applying the ICP algorithm to grayscale and color
    images: You can carry out either edge-based ICP or corner-pixels based
    ICP.  For edge-based ICP, a typical usage example would look like

        import ICP
        icp = ICP.ICP(
               binary_or_color = "color",
               corners_or_edges = "edges",
               auto_select_model_and_data = 1,
               calculation_image_size = 200,
               max_num_of_pixels_used_for_icp = 300,
               pixel_correspondence_dist_threshold = 20,
               iterations = 24,
               model_image =  "SydneyOpera.jpg",
               data_image = "SydneyOpera2.jpg",
               font_file = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
             )
        icp.extract_pixels_from_color_image("model")
        icp.extract_pixels_from_color_image("data")
        icp.icp()
        icp.display_images_used_for_edge_based_icp()
        icp.display_results_as_movie()
        icp.cleanup_directory()

    On the other hand, for corner-pixels based ICP, your usage of this
    module is likely to be:

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
               font_file = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
            )
        icp.extract_pixels_from_color_image("model")
        icp.extract_pixels_from_color_image("data")
        icp.icp()
        icp.display_images_used_for_corner_based_icp()
        icp.display_results_as_movie()
        icp.cleanup_directory()

    When applying this ICP module to binary images, your usage is likely to
    be:

        import ICP
        icp = ICP.ICP(
               binary_or_color = "binary",
               pixel_correspondence_dist_threshold = 40,
               auto_select_model_and_data = 1,
               calculation_image_size = 200,
               iterations = 16,
               model_image = "triangle1.jpg",
               data_image = "triangle2.jpg",
               font_file = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
            )
        icp.extract_pixels_from_binary_image("model")
        icp.extract_pixels_from_binary_image("data")
        icp.icp()
        icp.display_images_used_for_binary_image_icp()
        icp.display_results_as_movie()
        icp.cleanup_directory()


    In the calls shown above, the parameter calculation_image_size controls
    the size of the image that will actually be used for ICP calculations.
    Color (and grayscale) images as output by sensors can be very large and
    it would be impractical to process all of the pixel data in the images.
    This module first smoothly reduces the size of the images so that the
    maximum dimension does not exceed calculation_image_size and then
    carries out ICP processing on the reduced-size images.  The
    pixel_correspondence_dist_threshold parameter controls how wide the net
    will be cast, so to speak, in seeking a model image correspondent for a
    data image pixel.  You will generally get better results if you choose
    the image with a larger number of candidate pixels for ICP calculations
    as the model image. The parameter auto_select_model_and_data, when set
    to 1, lets the module decide as to which image to use for the model and
    which to use as data.

    The other constructor parameters shown in the calls shown above are
    explained further down on this documentation page.

    The module also includes a static method gendata() to illustrate
    how one can create simple synthetic images to experiment with this
    ICP module.  A call to this method looks like

        import ICP
        ICP.ICP.gendata( "triangle", (80,80), (10,10), 30, "newtriangle2.jpg" )

    As currently programmed, the gendata() method constructs images with 
    triangles and straight lines segments.


@title
CONSTRUCTOR PARAMETERS:

    auto_select_model_and_data: Must be set to 0 or 1. When set to 1, the
                         system decides as to which of the two images you
                         supplied to the constructor will actually be used
                         as model and which as data. You generally get
                         better results if the image that yields a larger
                         number of pixels for ICP calculations is used as a
                         model. (DEFAULTS TO 0)

    binary_or_color:     Must be set to 'binary' for binary images and to
                         'color' for grayscale and color images. (REQUIRED)

    calculation_image_size:   The size to which a large image will be reduced
                         for ICP processing.  (DEFAULTS TO 200)

    corner_detection_threshold: When corner pixels are needed for ICP
                         calculations, the module uses the Harris Corner
                         Detector.  To detect a corner, we sum the squares
                         of the x-derivatives, the squares of the
                         y-derivatives, and the product of the two in a 5x5
                         window. We find the trace and the determinant of
                         the 2x2 matrix formed in this manner. This
                         parameter is a threshold for testing the ratio of
                         the determinant to the square of the trace.
                         (DEFAULTS TO 0.2)

    corners_or_edges:    To be used only when binary_or_color is set to 'color'.
                         It must be set to either 'edges' or 'corners'. 
                         (DEFAULTS TO 'edges')

    data_image:          The name of the data image file    (REQUIRED)

    image_polarity:      When the corners_or_edges parameter is set to 'corners',
                         you must specify the image polarity.  The polarity is
                         1 if the object pixels are generally brighter than the
                         background pixels.  Otherwise, it is -1.  (REQUIRED
                         when corners_or_edges is set to "corners")

    iterations:          The maximum number of iterations to try (DEFAULTS
                         TO 24)

    max_num_of_pixels_used_for_icp: Although, in general, as the number of
                         pixels you use for ICP goes up, the quality of the
                         registration improves on account of the averaging
                         effect created by the pixels.  But this works only
                         up to a point, beyond which you only increase the
                         time it takes for each ICP iteration without any
                         additional accuracy in registration.  This
                         parameter lets you set an upper bound on the number
                         of pixels that will be chosen for ICP calculations.
                         (DEFAULTS TO 100)

    model_image:         The name of the model image file   (REQUIRED)    

    pixel_correspondence_dist_threshold:  This parameter controls how far the 
                         the data image will be searched for a corresponding 
                         pixel for a model image pixel. (DEFAULTS TO 100).

    smoothing_low_medium_or_high: A useful parameter when you are applying
                         ICP to color (or grayscale) images in the "corner"
                         mode.  This parameter controls the degree of
                         smoothing that is applied to the two images to
                         segment out the object pixels from the background
                         pixels.  Its value must be either 'low', or
                         'medium', or 'high'.  (DEFAULTS TO 'medium')

    font_file:           For displaying labels on the results, the module 
                         uses the font file 'FreeSerif.ttf' by default. The 
                         module assumes that this file can be located through 
                         the paths stored in 'sys.path', or via the paths 
                         available through your environment variables. If 
                         you don't like the FreeSerif true-type font for 
                         some reason, starting with Version 2.1 you can 
                         specify your own font file through the "font_file" 
                         constructor option.

@title
METHODS:

    (1) extract_pixels_from_color_image()

        This method extracts the pixels to use for ICP calculation for the
        case of color and grayscale images.  It chooses the most prominent
        edge pixels when called with the argument 'edges'.  And it chooses
        the most prominent corner pixels when called with the argument
        'corners'.

    (2) extract_pixels_from_binary_image()
 
        This method extracts the pixels to use for ICP calculations for the
        case of binary images.

    (3) icp() 

        You must call the method icp() for the basic ICP calculations.

    (4) display_images_used_for_edge_based_icp()
        display_images_used_for_corner_based_icp()
        display_images_used_for_binary_image_icp()

        Since the model and the data images are processed differently for
        the three different cases of edge-based color, corner-pixels based
        color, and the binary images, the three display methods listed above
        are customized to what needs to be shown in each case.

    (5) display_results_as_movie()  

        The different iterations of the ICP algorithm are displayed through
        a movie by calling this method.

    (6) cleanup_directory()

        The data image as transformed by the rotation and the translation at
        each iteration is stored in a file whose name begins with the
        '__result' prefix.  These files, stored in the directory in which
        you invoke this module, are used subsequently for the movie
        depiction of the registration process.  By calling this method, you
        can delete these files.


@title
HOW THE RESULTS ARE DISPLAYED:

    The results are displayed using Tkinter graphics (meaning, actually, Tk
    graphics via the Tkinter interface).  To understand the results, you
    must first call one of the three display_images_used_for_xxxx() methods
    listed in item (4) under Methods above in order to see which pixels are
    being used for ICP calculations.  Subsequently, you call the method
    display_results_as_movie() to see an iteration-by-iteration movie of the
    registration between the model image and the data image.


@title
THE EXAMPLES DIRECTORY:

    The best way to become familiar with this module is by executing the
    following scripts in the Examples subdirectory:

    1.  color_image_registration_with_edge_pixels_example1.py

            This script shows registration results with edge-based ICP on
            two color images of Sydney Opera House.  (The registration
            itself is carried out on the grayscale versions of the color
            images.)

    2.  color_image_registration_with_edge_pixels_example2.py 

            This script shows registration results with edge-based ICP on
            overhead photos of a highway interchange.

    3.   color_image_registration_with_edge_pixels_example3.py 

            This script shows registration results on a pair of generic
            images with square blocks.

    4.   color_image_registration_with_corner_pixels_example1.py

            This script shows registration results with corner-pixels based
            ICP on two photos of my wife's earrings.  The model photo is
            from the www.etsy.com website where these earrings are sold.  To
            the best of what I can tell, there are no copyright issues
            related to the use of this photo here.

    5.   binary_image_registration_example1.py

            This is an example of registering two binary images of a
            triangular shape.

    6.   binary_image_registration_example2.py

            This is another example of binary image registration that only
            involves a single straight line in the images.

    It is highly recommended that you play with these example scripts before
    using the module on your own images.


@title 
SHOULD YOU CHOOSE THE 'edges' MODE OR THE 'corners' MODE FOR COLOR
AND GRAYSCALE IMAGES:

    That obviously depends on what your images look like.  For example, the
    Sydney Opera House images used in the script
    color_image_registration_with_edge_pixels_example1.py have strong edges
    and the 'edges' mode works fine for this case.  On the other hand, the
    edges in the earrings images used in the script
    color_image_registration_with_corner_pixels_example1.py are not so
    strong.  The objects in these images are more textured than anything
    else and the 'corners' mode works well in this case.  In general, you
    can expect the 'corners' mode to work well when the images have
    relatively confined objects with textured surfaces.


@title
THEORETICAL BASIS:   

    The first ICP algorithm was proposed by Paul Besl and Neil McKay in
    a now celebrated paper that appeared in 1992 in IEEE Transactions
    on PAMI.  Since then various versions of the algorithm have been
    published by other folks for either speeding up the performance of
    the algorithm or for improving its accuracy.

    The algorithm implemented here is as simple as it can be.  We model
    the relationship between model and data as

          R x_d   +   T    =    x_m 

    where x_d denote the data points and x_m the model points, each a
    two-element vector.  R is a 2x2 rotation matrix and T a 2-element
    translation vector.  Since two planar figures may not be related by
    the above transformation (even when one figure "appears" to be a
    rotated version of the other figure) for an arbitrary location of
    the origin, move the origin to the mean point of the model by

          x_m   =   x_m  -   mean( x_m )
                                                       
          x_d   =   x_d  -   mean( x_m )

    With regard to the calculation of R and T, let's express the data
    points and the CORRESPONDING model points as

         [x_d1, x_d2, ....., x_dn]  

    and their CORRESPONDING model points

         [x_m1, x_m2, ....., x_mn]

    We can now write the following for estimating the rotation matrix:

         R . A   =  B

    where

         A  =  [x_d1, x_d2, ....., x_dn]  

         B  =  [x_m1 - T, x_m2 - T, ....., x_mn - T]

    Both A and B are 2xn matrices.  We can now write

         R . A . A^t =  B . A^t

    where A^t is the transpose of A.  So, we have the following as a
    least mean squares estimate for R:

         R    =    B . A^t . ( A . A^t )^-1

    Since such an R may not obey the strict properties that must apply
    to a rotation matrix (it must be orthonormal), we condition it by
    first subjecting it to a singular value decomposition:

        U.S.V^t  =  svd( R )

    and then writing the following for a better estimate for R:
 
        R    =   U . V^t

    We can now estimate T by

        T    =  mean( x_m )   -   mean( R x_d )        

    The above assumes that we are carrying out an one-shot calculation
    of R and T.  But ICP is iterative.  The following applies to an
    iterative implementation of the above:

    For an iterative assessment of R and T, let's assume that we can
    decompose R as

        R = \deltaR . R_0

    where we have previously calculated R_0 and now we wish to refine
    the estimate with the calculation of \deltaR.  Plugging the above
    in the previous formulation:

        \deltaR . R_0 . A . A^t =  B . A^t

    implying

        \deltaR . R_0   =  B . A^t . ( A . A^t )^-1

    which is to say:

        \deltaR   =  B . A^t . ( A . A^t )^-1 .  R_0^t

    After you have calculated \deltaR, you can update the rotation
    matrix by

        R = \deltaR . R_0

    At the end of each such update of the rotation matrix, the
    calculation of the translation vector remains the same as before

        T    =  mean( x_m )   -   mean( R .  x_d )               

    We can therefore write down the following steps for ICP
    computation:

    STEP 1:
               x_m   =   x_m  -  mean(x_m)
               x_d   =   x_d  -  mean(x_m)


    STEP 2:
               Initialize R and T:

               R  =    1  0
                       0  1

               T  =    0
                       0

               old_error = inf


    STEP 3:     error = (1/N) \sum dist( x_m - (R * x_d + T) )


    STEP 4:     diff_error = abs(old_error - error)
                if (diff_error > threshold):
                    old_error = error
                else:
                    break

    STEP 5:    for each x_d find its closest x_m by finding that x_m which
               minimizes the squared difference between the two sides
               of

                      R . x_d  +   T  =   x_m

    STEP 6:     A  =  [x_d1, x_d2, ....., x_dn]  
                B  =  [x_m1 - T, x_m2 - T, ....., x_mn - T]

                Note that A will remain the same for ICP iterations,
                but B can change with each iteration depending on the
                what corresponding pixels are found for each data
                pixel.

    STEP 7:     AATI =  A^t inverse(A * A^t)

    STEP 8:     R_update =  B * AATI * R.T

    STEP 9:     U,S,VT =  svd(R_update)
                deter =   determinant(U * VT)
                U[0,1] = U[0,1] * determinant
                U[1,1] = U[1,1] * determinant

                R_update = U * VT

    STEP 10:    R =  R_update * R

    STEP 11:    T  =  mean(x_m) - mean( R * x_d )

    STEP 12:    Back to Step 3


@title
THE ICPImageScanner CLASS:

    Starting with Version 2.1.0, you can first chop large model and data
    images into subimages and then apply the ICP algorithm separately to
    each corresponding pair of subimages. When large images are recorded by
    aggregating the data from sensors in motion (as is the case with earth
    imaging satellites that use pushbroom cameras and, in some cases, with
    the cameras mounted in UAVs), the different portions of a recorded
    image may not be characterizable with the same translational and
    rotational offsets vis-a-vis a model image extracted for a GIS
    database.

    The ICPImageScanner class is programmed as a subclass of the main ICP
    class.  Therefore, it inherits all of the functionality of the parent
    ICP class.

    Here is how you'd class the constructor of the ICPImageScanner class if
    you want to chop the original model and data images into a collection
    of non-overlapping subimages:

            model_image_file = "my_large_model_image.jpg"
            data_image_file = "my_large_data_image.jpg"
            scanner = ICPImageScanner.ICPImageScanner(
                           model_image_file = model_image_file,
                           data_image_file = data_image_file,
                           binary_or_color = "color",
                           corners_or_edges = "edges",
                           scanning_window_width = 250,
                           scanning_window_height = 225,
                      )
            scanner.chop_model_and_data_images_into_tiles_interactive()
    
    The code shown above will deposit the subimages into two scanner dump
    directories, one for the model and the other for the data, whose names
    are keyed to the names of the image files.  Subsequently, you can test
    the application of the ICP algorithm to just one pair of corresponding
    subimages through the following constructor call and the invocation
    shown below that:

            model_image_file = "my_large_model_image.jpg"
            data_image_file = "my_large_data_image.jpg"
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
                           iterations = 24,
                           scanning_window_width = 250,
                           scanning_window_height = 225,
                   )
            scanner.calculate_icp_for_one_pair_of_subimages_and_display_results()
            
    Note the additional parameter subimage_index in the call to the
    constructor of the ICPImageScanner class. This parameter identifies the
    subimages to use from the model-image scanner dump and the data-image
    scanner dump A call such as the one depicted above outputs the final
    results of ICP registration through a "movie" that shows the data
    subimage being incrementally rotated and translated as it is registered
    with the model subimage.

    After you have tested image scanning with the call shown above, you can
    make the following constructor call and the two invocations shown below
    that for registering all of the corresponding pairs of subimages in the
    model and data scanner dump directories:

            model_image_file = "my_large_model_image.jpg"
            data_image_file = "my_large_data_image.jpg"
            scanner = ICPImageScanner.ICPImageScanner(
                           model_image_file = model_image_file,
                           data_image_file = data_image_file,
                           binary_or_color = "color",
                           corners_or_edges = "edges",
                           calculation_image_size = 200,
                           max_num_of_pixels_used_for_icp = 300,
                           pixel_correspondence_dist_threshold = 20,
                           iterations = 24,
                           scanning_window_width = 250,
                           scanning_window_height = 225,
                      )
            scanner.apply_icp_to_model_and_data_scanner_dumps_fast()
            scanner.display_results_for_all_subimage_pairs_together_as_a_movie_with_colorization()

    Note the substring "_fast" in the name of the method called in the
    first of the two invocations shown. This method is fast because it does
    NOT show separately the ICP registration for each pair of corresponding
    subimages. On the other hand, the final result that you see is through
    the second invocation shown above, which displays all of the subimage
    based ICP registrations in the form of a composite movie.  If you do
    want to see the ICP registrations for each of the subimage pairs
    individually, you would need to replace the two invocations on the
    scanner object shown above with:

            scanner.apply_icp_to_model_and_data_scanner_dumps_and_show_intermediate_results()
            scanner.display_results_for_all_subimage_pairs_together_as_a_movie()


@title    
CONSTRUCTOR PARAMETERS OF THE ICPImageScanner CLASS:

    model_image_file: This is the name of the original image to be used as
                    the model image for ICP registration.  IMPORTANT NOTE:
                    Even when you are doing ICP registration on just a
                    subimage pair, the value of this parameter must be the
                    name of the original model image from which the
                    subimage was extracted.

    data_image_file: This is the name of the data image to be used for ICP
                    registration. IMPORTANT NOTE: As with the previous
                    parameter, the value of this parameter must be the
                    original data image even when you are doing ICP
                    registration on just a pair of subimages extracted from
                    the original model and the data images.

    binary_or_color: For now you must set it to 'color' for grayscale and
                    color images. (I have not yet allowed for 'binary" in
                    the ICPImageScanner class.  Will add that functionality
                    in a later version.)

    corners_or_edges: For now you must set it to 'edges'.  I have not yet
                    added the 'corners' mode to the ICPImageScanner class.

    calculation_image_size: This is the size to which the subimages will be
                    reduced if it turns out that they are larger than the
                    value of this parameter.

    max_num_of_pixels_used_for_icp: The value of this parameter is passed
                    to the parent instance of the ICP class.  See the
                    documentation on this parameter as presented earlier in
                    the context of the ICP class.

    pixel_correspondence_dist_threshold: The value of this parameter is
                    passed to the parent instance of the ICP class.  See
                    the documentation on this parameter as presented
                    earlier in the context of the ICP class.
 
    iterations: The maximum number of iterations to try for ICP based
                    registration.

    scanning_window_width: As should be obvious by its name, this parameter
                    specifies the width of the scanning window for chopping
                    a large image into subimages.

    scanning_window_height: As with the previous entry, this parameter
                    specifies the height of the scanning window for
                    chopping a large image into subimages.

            
@title
PUBLIC METHODS OF THE ICPImageScanner CLASS:

    (1) apply_icp_to_model_and_data_scanner_dumps_and_show_intermediate_results()

        The purpose of this method is to apply the ICP algorithm to ALL the
        subimage pairs extracted from the supplied model and data images.
        The scanning function (see the fifth method listed below) in the
        ICPImageScanner class creates two dump directories containing the
        subimages, one for the model image and the other for the data
        image.  See the script
        "ICPforScannerDump_show_intermediate_results.py" in the
        ExamplesICPImageScanner directory that illustrates how you can
        invoke this method.
 

    (2) apply_icp_to_model_and_data_scanner_dumps_fast():

        This is a faster version of the previous method.  It is faster
        because it does not show ICP registration results separately for
        each pair of subimages.  See the script
        "ICPforScannerDump_no_intermediate_results.py" in the
        ExamplesICPImageScanner directory that illustrates how you can use
        this method.


    (3) calculate_icp_for_one_pair_of_subimages_and_display_results()

        If you want to carry out ICP registration only for a specific pair
        of subimages, then this is the method to invoke.  Note that the
        identity of the subimage pair is supplied as an integer index to
        the constructor for the ICPImageScanner class. Let us say you
        chopped up the two original images into a 3x3 array of subimages
        and you want to see the result of ICP registration on the subimage
        pair that corresponds to the upper left hand corner of the original
        images, the value of the subimage identity index would be 0 in the
        constructor call. And if you wanted to see ICP registration for the
        subimage at the lower right-hand corner, the subimage identity
        index for that would be 8 for the case of a 3x3 array of subimages.
        See the script "ICPforOneSubimagePair.py" in the
        ExamplesICPImageScanner directory for how to use this method.


    (4) calculate_icp_for_one_pair_of_subimages_fast()

        This is a faster version of the previous method.  It is faster
        because it does not create visual representations of ICP
        registration.  In the current code, it is called by the second
        method listed above.


    (5) chop_model_and_data_images_into_tiles_interactive():

        This is the method to call for chopping your model and data images
        into subimages.  The subimages are dumped in two separate
        directories, one for the model image and the other for the data
        subimage. The names of these directories is keyed to the names of
        the original images.  See the script "RunICPImageScanner.py" in the
        ExamplesICPImageScanner directory for how to invoke this method.


    (6) cleanup_scanner_examples_directory():

        Several of the methods listed here create directories for the
        intermediate results that are subsequently used for a "movie"
        presentation of ICP registration. This is the method to call if you
        want to get rid of those directories, as made evident by the
        example scripts in the ExamplesICPImageScanner directory.  The dump
        directories produced by the scanner are NOT touched by this cleanup
        method.
      

    (7) display_subimage_pair_used_for_edge_based_icp():

        If you are working with just one pair of corresponding subimages in
        the two scanner dump directories and you want to display the
        subimages, the edges extracted from them, and the pixels retained
        for ICP registration, this is the method you want to invoke.  In
        the current code, this functionality is called by the third method
        listed above for displaying the intermediate results on individual
        pairs of subimages.


    (8) display_results_for_all_subimage_pairs_together_as_a_movie():

        This method displays ICP registration for ALL the subimages in the
        form of a composite "movie".  You should invoke this method only if
        your ICP registration was carried out by the invoked
        "apply_icp_to_model_and_data_scanner_dumps_and_show_intermediate_results()".
        The reason for that is that it is the production of the
        intermediate results that colorizes the pixels needed for making
        the movies.  See the script
        "ICPforScannerDump_show_intermediate_results.py" in the
        ExamplesICPImageScanner directory for how to use this method for
        presenting the results in the form of a a movie.


    (9) display_results_for_all_subimage_pairs_together_as_a_movie_with_colorization():

        If you have opted for the fast (meaning no display of intermediate
        results) methods for ICP registration of the corresponding
        subimages, you need to call this method for creating a composite
        movie of the results.  This method differs from the previous movie
        making method in only one aspect: it also colorizes the pixels for
        the movie.  See the script
        "ICPforScannerDump_no_intermediate_results.py" in the
        ExamplesICPImageScanner directory for how to use this method for
        presenting the results in the form of a composite movie.


@title
THE ExamplesICPImageScanner DIRECTORY:

    This directory contains the following scripts:


    (1) RunICPImageScanner.py

        This example script illustrates how to use the ICPImageScanner
        class in the ICP module.  This script scans two images, one for the
        model and the other for the data, in an interactive mode.  What
        that means is that each subimage is shown to the user before moving
        on to the next subimage.  The subimages extracted from the large
        model and data images are dumped in scanner dump directories whose
        names are keyed to the names of the images.


    (2) ICPforOneSubimagePair.py

        This script demonstrates ICP registration of one subimage extracted
        from the large model image with the corresponding subimage
        extracted from the large data image.  For this script to work, you
        have to have previously run the image scanner that chops the large
        images into subimages and dumps them in two scanner dump
        directories, one for the model image and the other for the data
        image.  The names of the dump directories are keyed to the names of
        the images.


    (3) ICPforScannerDump_show_intermediate_results.py

        This script applies the ICP registration algorithm to ALL the
        subimage pairs extracted from the large model and data images.
        Since this script also shows you ICP registrations separately for
        each subimage pair, it is slower than the next script. The final
        output of this script is in the form of a composite movie that
        shows ICP registrations simultaneously for ALL subimage pairs.


    (4) ICPforScannerDump_no_intermediate_results.py

        Like the previous script, this script applies the ICP algorithm to
        ALL of the subimage pairs extracted from the large model and data
        images.  This script should be much faster than the previous script
        listed above.  As for the previous script, the final output of this
        script is in the form of a composite movie that shows ICP
        registrations for ALL subimage pairs simultaneously.


    (5) cleanup_scanner_directory.py

        Ordinarily, the scripts in this directory should clean up after
        themselves.  However, should you want to kill a script midstream or
        should it abort for some reason, you can run this script to clean
        up the directory.  The dump directories produced by the scanner are
        not touched by this cleanup script.


@title
FOR MORE ADVANCED READING ON ICP:

    The reader might want to look up the research publication "UAV Vision:
    Feature Based Accurate Ground Target Localization Through Propagated
    Initializations and Interframe Homographies" by Han, Aeschliman, Park,
    and Kak that appeared in the Proceedings of 2012 Conference on Robotics
    and Automation.  You can download it from

    https://engineering.purdue.edu/RVL/Publications/chad_avi_han_2012.pdf

    The ICP algorithm used in the work described in this publication was
    custom designed for that project.


@title
CAVEATS:

    As to what sort of results you'll get for your images depends a great
    deal on what values you choose for the various constructor parameters
    listed earlier in this documentation.  As a case in point, if the
    parameter pixel_correspondence_dist_threshold is set to 20 for the case
    of the highway interchange images in the script
    color_image_registration_with_edge_pixels_example2.py, the ICP
    algorithm gets stuck in a local minimum.  The good result that the
    script produces is for the value 40 for this parameter.  On the other
    hand, the value of 20 for the same parameter works fine for the Sydney
    Opera House images in the script
    color_image_registration_with_edge_pixels_example1.py.  Note that the
    extent of misregistration between the two images for both scripts is
    roughly the same.


@title                                                                                             
BUGS:                                                                                              
                                                                                               
    Please notify the author if you encounter any bugs.  When sending
    email, please place the string 'ICP' in the subject line.


@title
ABOUT THE AUTHOR:  

    Avi Kak (kak@purdue.edu) recently completed his multi-year "Objects
    Trilogy" project.  See his web page at Purdue for what this project is
    all about.  If nothing else, you will get to enjoy Harry Potter all
    over again.

@title
THANKS:

    Bharath Comandur found a bug in Version 2.0 that caused this module to
    not work with the more recent versions of the Pillow library for PIL.
    Bharath also supplied a fix for the problem, which was to cast to int
    the argument provided to the putpixel function.  This fix was made in
    Version 2.1 of the module.

@endofdocs
'''

from PIL import Image
from PIL import ImageFilter
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageChops
from PIL import ImageTk
import numpy
import numpy.linalg
import math
import re
import sys, os, os.path, glob
import functools
try:        # for Python3
    import tkinter as Tkinter
    from tkinter.constants import *
    import tkinter.font as tkFont
except:     # for Python 2
    import Tkinter
    from Tkconstants import *
    import tkFont

#---------------------------------------- Support Functions ---------------------------------------
def _euclidean(p, q):
    '''
    Calculates the Euclidean distance between two points p and q and
    returns the distance as a scalar:
    '''
    p,q = numpy.array(p), numpy.array(q)
    return numpy.sqrt( numpy.dot(p-q,p-q) )

def _indexAndLeastDistance(distList):
    minVal = min(distList)
    return distList.index(minVal), minVal    

def _difference(p,q):
    return p[0]-q[0],p[1]-q[1]

def _mean_coordinates(coords_list):
    '''
    Returns a pair of values in the form of a tuple, the pair
    consisting of the mean values for the x and the y coordinates:
    '''
    mean = functools.reduce(lambda x,y: x+y, [x[0] for x in coords_list]), \
           functools.reduce(lambda x,y: x+y, [x[1] for x in coords_list])

    mean = mean[0]/float(len(coords_list)), mean[1]/float(len(coords_list))
    return mean

def _display_data_matrix(data_matrix):
    print("\ndata matrix:")
    for col in data_matrix:
        print(str(col))

def _print_points(msg, points_arr):
    print(msg,)
    print(str( ['(' + ("%.1f, %.1f")%(x,y) + ')' for (x,y) in points_arr] ) )

def _print_points_in_dict(msg, points_dict):
    print(msg,)
    print( [item[0]+" : "+'('+("%.1f, %.1f")%(points_dict[item[0]][0],points_dict[item[0]][1])+')' 
                    for item in sorted(points_dict.items(), 
                             lambda x,y: cmp(int(x[0].lstrip('md')),int(y[0].lstrip('md'))))] )

def _print_float_values_dict(msg, dict_with_float_vals):
    print(msg,)
    print( [item[0]+" : " + ("%.2f")%(dict_with_float_vals[item[0]]) 
             for item in sorted(dict_with_float_vals.items(), 
                    lambda x,y: cmp(int(x[0].lstrip('md')),int(y[0].lstrip('md'))))
                            if dict_with_float_vals[item[0]] is not None] )

def _least_dist_mapping(data_dict, model_dict, dist_threshold):
    mapping = {d : None for d in data_dict}
    error_dict = {d : None for d in data_dict}
    for d in sorted(data_dict.keys(), key = lambda x: x.lstrip('md')):
        dist_values = {m : _euclidean(data_dict[d],model_dict[m]) for m in model_dict}
        for mlabel in sorted(dist_values.keys(), key = lambda x: dist_values[x]):
            if dist_values[mlabel] < dist_threshold:
                mapping[d] = mlabel
                error_dict[d] = dist_values[mlabel]
                break;
    return mapping, error_dict

#-------------------------------------- ICP Class Definition --------------------------------------

class ICP(object):

    def __init__(self, *args, **kwargs ):
        if args:
            raise ValueError(  
                   '''ICP constructor can only be called with keyword arguments for 
                      the following keywords: model_image, data_image, binary_or_color,
                      calculation_image_size, iterations, corners_or_edges, 
                      corner_detection_threshold, pixel_correspondence_dist_threshold, 
                      edge_detection_threshold, max_num_of_pixels_used_for_icp,
                      image_polarity, auto_select_model_and_data, 
                      smoothing_low_medium_or_high, font_file, debug1, and debug2''')       
        model_image=data_image=calculation_image_size=iterations=corner_detection_threshold=None
        corners_or_edges=edge_detection_threshold=pixel_correspondence_dist_threshold=None
        max_num_of_pixels_used_for_icp=smoothing_low_medium_or_high=subimage_index=None
        image_polarity=auto_select_model_and_data=font_file=debug1=debug2=None

        if 'model_image' in kwargs                 :              model_image=kwargs.pop('model_image')
        if 'data_image' in kwargs                  :               data_image=kwargs.pop('data_image')
        if 'binary_or_color' in kwargs             :      binary_or_color=kwargs.pop('binary_or_color')
        if 'binary_or_color' in kwargs             :      binary_or_color=kwargs.pop('binary_or_color')
        if 'iterations' in kwargs                  :                iterations=kwargs.pop('iterations')
        if 'corners_or_edges' in kwargs            :    corners_or_edges=kwargs.pop('corners_or_edges')
        if 'image_polarity' in kwargs              :        image_polarity=kwargs.pop('image_polarity')
        if 'subimage_index' in kwargs              :        subimage_index=kwargs.pop('subimage_index')
        if 'font_file' in kwargs                   :                  font_file=kwargs.pop('font_file')
        if 'debug1' in kwargs                      :                        debug1=kwargs.pop('debug1')
        if 'debug2' in kwargs                      :                        debug2=kwargs.pop('debug2')
        if 'calculation_image_size' in kwargs      :  \
                                            calculation_image_size=kwargs.pop('calculation_image_size')
        if 'corner_detection_threshold' in kwargs  :  \
                                    corner_detection_threshold=kwargs.pop('corner_detection_threshold')
        if 'edge_detection_threshold' in kwargs    :  \
                                        edge_detection_threshold=kwargs.pop('edge_detection_threshold')
        if 'pixel_correspondence_dist_threshold' in kwargs:  \
                  pixel_correspondence_dist_threshold=kwargs.pop('pixel_correspondence_dist_threshold')
        if 'auto_select_model_and_data' in kwargs: \
                                    auto_select_model_and_data=kwargs.pop('auto_select_model_and_data')
        if 'max_num_of_pixels_used_for_icp' in kwargs: \
                            max_num_of_pixels_used_for_icp=kwargs.pop('max_num_of_pixels_used_for_icp')
        if 'smoothing_low_medium_or_high' in kwargs: \
                                smoothing_low_medium_or_high=kwargs.pop('smoothing_low_medium_or_high')
        if len(kwargs) != 0:
                                  raise ValueError('''You have provided unrecognizable keyword args''')
        if model_image: 
            self.model_im = Image.open(model_image)
            self.original_model_im = Image.open(model_image)
        else:
            self.model_im = None
        if data_image: 
            self.data_im =  Image.open(data_image)
            self.original_data_im = Image.open(data_image)
        else:
            self.data_im = None
        if binary_or_color:
            self.binary_or_color = binary_or_color
        else:
            raise ValueError('''You must specify either "binary" or "color" ''')
        if font_file:
            self.font_file = font_file
        elif os.path.isfile("FreeSerif.ttf"):
            self.font_file = "FreeSerif.ttf"
        elif os.path.isfile("/usr/share/fonts/truetype/freefont/FreeSerif.ttf"):
            self.font_file = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
        else:
            print("Unable to find the font file 'FreeSerif.ttf' needed for displaying the results")
            print("Use the 'font_file' option in the constructor to specify your own font file")
            sys.exit(1)
        if corners_or_edges:
            self.corners_or_edges = corners_or_edges
        else:
            self.corners_or_edges = "edges"
        if smoothing_low_medium_or_high:
            self.smoothing_low_medium_or_high = smoothing_low_medium_or_high
        else:
            self.smoothing_low_medium_or_high = "medium"  
        if image_polarity:
            self.image_polarity = image_polarity
        elif corners_or_edges == "corners":
            raise ValueError('''\n\nYou must specify image_polarity as 1 or -1 when using '''
                             '''corner-based ICP. The polarity is 1 when the object pixels are '''
                             '''generally brighter than the background pixels. Otherwise it is -1.''')
        if subimage_index is None: 
            self.subimage_index = None
        else:
            self.subimage_index = subimage_index
        if calculation_image_size:
            self.calculation_image_size = calculation_image_size
        elif self.model_im.size[0] <= 100:
                self.calculation_image_size = self.model_im.size[0]
        else:
            self.calculation_image_size = 200
        if iterations:
            self.iterations = iterations
        else:
            self.iterations = 24
        if corner_detection_threshold:
            self.corner_detection_threshold = corner_detection_threshold
        else:
            self.corner_detection_threshold = 0.2
        if edge_detection_threshold:
            self.edge_detection_threshold = edge_detection_threshold
        else:
            self.edge_detection_threshold = 50
        if pixel_correspondence_dist_threshold:
            self.pixel_correspondence_dist_threshold = pixel_correspondence_dist_threshold
        else:
            self.pixel_correspondence_dist_threshold = 100
        if max_num_of_pixels_used_for_icp:
            self.max_num_of_pixels_used_for_icp = max_num_of_pixels_used_for_icp
        else:
            self.max_num_of_pixels_used_for_icp = 100
        if debug1:
            self.debug1 = debug1
        else:
            self.debug1 = 0
        if debug2:
            self.debug2 = debug2
        else:
            self.debug2 = 0
        if auto_select_model_and_data:
            self.auto_select_model_and_data = auto_select_model_and_data
        else:
            self.auto_select_model_and_data = 0
        self.model_rval =  None
        self.data_rval  =  None
        self.model_segmentation = None
        self.model_all_corners = None
        self.model_list = []
        self.data_segmentation = None
        self.data_all_corners = None
        self.data_list = []
        self.model_edge_map = None
        self.data_edge_map = None

    def extract_pixels_from_color_image(self, model_or_data):
        if model_or_data == "model":
            im = self.model_im
        else:
            im = self.data_im
        im = im.convert('L')        ## convert to gray level
        im.thumbnail( (self.calculation_image_size, self.calculation_image_size), Image.ANTIALIAS )
        if self.debug1: im.show()
        width,height = im.size
        if self.debug1: print("width: %d    height: %d" % (width, height))
        if self.corners_or_edges == "edges":
            dx = numpy.zeros((height, width), dtype="float")
            dy = numpy.zeros((height, width), dtype="float")
            rval = numpy.zeros((height, width), dtype="float")  # rval at a pixel = determinant / trace^2
            result_im = Image.new("1", (width,height), 0)
            edge_im = Image.new("L", (width,height), 0)
            edge_pixel_list = []    
            corner_pixels = []
            # Note that array indexing is 'opposite' of the image indexing with the first index along 
            # what is y for the image and the second index along what is x for the image.  For the image,
            # x is the horizontal axis to the right, y is the vertical axis pointing downwards.  In what 
            # follows, we treat i and j as the image coordinates.  That is, i increments horizontally to 
            # the right and j increments vertically downwards:
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
            if self.debug1: result_im.show()
            if model_or_data == "model":
                if self.debug1: result_im.save("model_image_pixels_retained.jpg")
                self.model_im = result_im
                self.model_list = edge_pixel_list
                self.model_edge_map = edge_im
                if self.debug1: edge_im.save("model_edge_image.jpg")
            else:
                if self.debug1: result_im.save("data_image_pixels_retained.jpg")
                self.data_im = result_im
                self.data_list = edge_pixel_list
                self.data_edge_map = edge_im
                if self.debug1: edge_im.save("data_edge_image.jpg")
        else:
            # We want to use corners for ICP:
            im2 = im.copy()
            if self.smoothing_low_medium_or_high == "low":
                how_much_smoothing = 1
            elif self.smoothing_low_medium_or_high == "medium":
                how_much_smoothing = 5
            elif self.smoothing_low_medium_or_high == "high":
                how_much_smoothing = 10
            else:
                sys.exit('''\n\nYour value for smoothing_low_medium_or_high parameter must be '''
                         '''either "low", or "medium", or "high" ''')
            for i in range(how_much_smoothing):
                im2 = im2.filter(ImageFilter.BLUR) 
            if self.debug1: im2.show()
            hist = im2.histogram()
            total_count = functools.reduce(lambda x,y: x+y, hist)
            coarseness = 8              # make it a divisor of 256
            probs = [functools.reduce(lambda x,y: x+y, hist[coarseness*i:coarseness*i+coarseness])/float(total_count)
                                                     for i in range(int(len(hist)/coarseness))]
            prob_times_graylevel = [coarseness * i * probs[i] for i in range(len(probs))]
            mu_T = functools.reduce(lambda x,y: x+y, prob_times_graylevel)       # mean for the image
            prob_times_graysquared = [(coarseness * i - mu_T)**2 * probs[i] for i in range(len(probs))]
            sigma_squared_T = functools.reduce(lambda x,y: x+y, prob_times_graysquared)
            m0 = [functools.reduce(lambda x,y: x+y, probs[:k]) for k in range(1,len(probs)+1)]
            m1 = [functools.reduce(lambda x,y: x+y, prob_times_graylevel[:k]) for k in range(1,len(probs)+1)]
            sigmaB_squared = [None] * len(m0)          # for between-class variance as a func of threshold
            sigmaW_squared = [None] * len(m0)          # for within-class variance as a func of threshold
            variance_ratio = [None] * len(m0)          # for the ratio of the two variances
            for k in range(len(m0)):
                if 0 < m0[k] < 1.0:
                    sigmaB_squared[k] = (mu_T * m0[k] - m1[k])**2 / (m0[k] * (1.0 - m0[k]))
                    sigmaW_squared[k] = sigma_squared_T - sigmaB_squared[k]
                    variance_ratio[k] = sigmaB_squared[k] / sigmaW_squared[k]
            variance_ratio_without_none = [x for x in variance_ratio if x is not None ]
            otsu_threshold = variance_ratio.index(max(variance_ratio_without_none)) * coarseness
            if self.debug1: print( "\nbest threshold: %s" % str(otsu_threshold))
            segmented_im2 = Image.new("1", (width,height), 0)            
            for i in range(width):
                for j in range(height):
                    if self.image_polarity == 1:
                        if im2.getpixel((i,j)) > otsu_threshold: segmented_im2.putpixel((i,j), 255)
                    elif self.image_polarity == -1:
                        if im2.getpixel((i,j)) < otsu_threshold: segmented_im2.putpixel((i,j), 255)
                    else:
                        sys.exit("You did not specify image polarity")
            if self.debug1: segmented_im2.show()
            dx = numpy.zeros((height, width), dtype="float")
            dy = numpy.zeros((height, width), dtype="float")
            rval = numpy.zeros((height, width), dtype="float")  # rval at a pixel = determinant / trace^2
            corner_pixels = []
            # Note that array indexing is 'opposite' of the image indexing with the first index along what 
            # is y for the image and the second index along what is x for the image.  For the image, x is 
            # the horizontal axis to the right, y is the vertical axis pointing downwards.  In what follows, 
            # we treat i and j as the image coordinates.  That is, i increments horizontally to the right
            # and j increments vertically downwards:
            for i in range(3,width-3):
                for j in range(3,height-3):
                    if segmented_im2.getpixel((i,j)) == 255:
                        ip1,im1,jp1,jm1 = i+1,i-1,j+1,j-1
                        dx[(j,i)] = (im.getpixel((ip1,jm1)) + 2*im.getpixel((ip1,j)) + \
                                     im.getpixel((ip1,jp1))) -  (im.getpixel((im1,jm1)) + \
                                     2*im.getpixel((im1,j)) + im.getpixel((im1,jp1))) 
                        dy[(j,i)] = (im.getpixel((im1,jp1)) + 2*im.getpixel((i,jp1)) + \
                                     im.getpixel((ip1,jp1))) -  (im.getpixel((im1,jm1)) + \
                                     2*im.getpixel((i,jm1)) + im.getpixel((ip1,jm1))) 
            if self.debug1:
                self.display_array_as_image(dx)
                self.display_array_as_image(dy)
            corners_im = Image.new("1", (width,height), 0)
            for i in range(3,width-3):                 # i is for horizontal axis to the right
                for j in range(3,height-3):            # j is for vertical axis to the bottom
                    if segmented_im2.getpixel((i,j)) == 255:
                        Cmatrix = numpy.zeros((2, 2), dtype="float")
                        c11=c12=c22=0.0
                        for k in range(i-2,i+3):            # k is horizontal
                            for l in range(j-2,j+3):        # l is vertical
                                c11 += dx[(l,k)] * dx[(l,k)] 
                                c12 += dx[(l,k)] * dy[(l,k)] 
                                c22 += dy[(l,k)] * dy[(l,k)] 
                        Cmatrix[(0,0)] = c11
                        Cmatrix[(0,1)] = c12
                        Cmatrix[(1,0)] = c12
                        Cmatrix[(1,1)] = c22
                        determinant = numpy.linalg.det(Cmatrix)
                        trace       = numpy.trace(Cmatrix)                
                        ratio = 0.0
                        if trace != 0.0:
                            ratio = determinant / (trace * trace)
                        rval[(j,i)] = ratio
                        if abs(ratio) > self.corner_detection_threshold:
                            corner_pixels.append((i,j))
                            corners_im.putpixel((i,j), 255)
            if self.debug1: corners_im.show()
            singular_corners_im = Image.new("1", (width,height), 0)      
            singular_corners = []
            for candidate in corner_pixels:
                i,j = candidate
                non_singular_corner_found = False
                for corner in corner_pixels:
                    if corner == candidate: continue
                    k,l = corner
                    if abs(i-k) <=1 and abs(j-l) <= 1:
                        if rval[(j,i)] <= rval[(l,k)]:
                            non_singular_corner_found = True
                            break
                if non_singular_corner_found: continue
                singular_corners.append(candidate)
                singular_corners_im.putpixel((i,j), 255)
            singular_corners.sort(key = lambda x: rval[(x[1],x[0])], reverse=True)
            sorted_singular_corners_im = Image.new("1", (width,height), 0)      
            if len(singular_corners) > self.max_num_of_pixels_used_for_icp:
                singular_corners = singular_corners[0:self.max_num_of_pixels_used_for_icp]
            for corner in singular_corners:
                sorted_singular_corners_im.putpixel(corner, 255)
            if self.debug1: sorted_singular_corners_im.show()
            if model_or_data == "model":
                if self.debug1: sorted_singular_corners_im.save("model_corners.jpg")
                self.model_im = sorted_singular_corners_im
                self.model_segmentation = segmented_im2
                self.model_all_corners = corners_im
                self.model_list = singular_corners
                self.model_rval = rval
            else:
                if self.debug1: sorted_singular_corners_im.save("data_corners.jpg")
                self.data_im = sorted_singular_corners_im
                self.data_segmentation = segmented_im2
                self.data_all_corners = corners_im
                self.data_list = singular_corners
                self.data_rval = rval

    def condition_data(self):
        '''
        If your model and data images are such that the pixel extraction
        functions yield very different number of pixels for ICP computations for
        the model and the data images, you may be able to improve your results
        by calling this method before you call icp().
        '''
        cutoff = 1.0
        num_of_data_pixels = len(self.data_list)
        num_of_model_pixels = len(self.model_list)
        diff = abs(num_of_data_pixels - num_of_model_pixels)
        min_count = min(num_of_data_pixels, num_of_model_pixels)
        if diff < cutoff * min_count: return
        if num_of_data_pixels > num_of_model_pixels:
            how_many = int( num_of_model_pixels + cutoff * min_count )
            self.data_list = self.data_list[0:how_many]
        else:
            how_many = int( num_of_data_pixels + cutoff * min_count )
            self.model_list = self.model_list[0:how_many]
        if self.debug1:
            _print_points("\nmodel list (in pixel coords) in `condition_data()': ", self.model_list)
            _print_points("\ndata list (in pixel coords) in `condition_data()': ", self.data_list)
        self.display_pixel_list_as_image(self.model_list)
        self.display_pixel_list_as_image(self.data_list)      
        self.save_pixel_list_as_image(self.model_list, "final_pixels_retained_model.jpg")
        self.save_pixel_list_as_image(self.data_list, "final_pixels_retained_data.jpg")

    def display_pixel_list_as_image(self, pixel_list):
        width,height = self.model_im.size
        display_im = Image.new("1", (width,height), 0)
        for pixel in pixel_list:
            display_im.putpixel(pixel, 255)
        display_im.show()

    def save_pixel_list_as_image(self, pixel_list, filename):
        width,height = self.model_im.size
        save_im = Image.new("1", (width,height), 0)
        for pixel in pixel_list:
            save_im.putpixel(pixel, 255)
        save_im.save(filename)

    def display_array_as_image(self, numpy_arr):
        height,width = numpy_arr.shape
        display_im = Image.new("L", (width,height), 0)
        for i in range(3,width-3):
            for j in range(3,height-3):
                display_im.putpixel((i,j), int(abs(numpy_arr[(j,i)])))
        display_im.show()

    def save_array_as_image(self, numpy_arr, label):
        height,width = numpy_arr.shape
        save_im = Image.new("L", (width,height), 0)
        for i in range(3,width-3):
            for j in range(3,height-3):
                save_im.putpixel((i,j), int(abs(numpy_arr[(j,i)])))
        save_im.save(label + ".jpg")

    def extract_pixels_from_binary_image(self, model_or_data):
        if model_or_data == "model":
            self.model_list = []
            if self.model_im.size[0] > 100:
                self.model_im.thumbnail( (self.calculation_image_size,\
                                 self.calculation_image_size), Image.ANTIALIAS )
            self.model_im = self.model_im.convert("L").convert("1")
            width, height =  self.model_im.size
            for i in range(3,width-3): 
                for j in range(3,height-3):
                    if ( self.model_im.getpixel((i,j)) != 0 ):  
                        self.model_list.append( (i,j) )       
        elif model_or_data == "data":
            self.data_list = []
            if self.data_im.size[0] > 100:
                self.data_im.thumbnail( (self.calculation_image_size,\
                                     self.calculation_image_size), Image.ANTIALIAS )
            self.data_im = self.data_im.convert("L").convert("1")
            width, height =  self.data_im.size
            for i in range(3,width-3): 
                for j in range(3,height-3):
                    if ( self.data_im.getpixel((i,j)) != 0 ):  
                        self.data_list.append( (i,j) )       
        else: sys.exit("Wrong arg used for extract_pixels_from_binary_image()")
        if self.debug1:
            if model_or_data == "model":    
                print("model pixel list %s" % str(self.model_list))
                print("\nnumber of pixels in model_list: %s" % str(len(self.model_list)))
            else:
                print("\ndata pixel list %s" % str(self.data_list))
                print("\nnumber of pixels in data_list: %s" % str(len(self.data_list)))

    def move_to_model_origin(self):
        '''
        Since two patterns that are situated at different places in a plane may not be
        related by a Euclidean transform for an arbitrary placement of the origin
        even when one pattern appears to be a rotated version of the other, we will
        assume that the origin for ICP calculations will be at the "center" of the
        model image.  Now our goal becomes to find an R and a T that will make the
        data pattern congruent with the model pattern with respect to this origin.

        '''
        self.model_mean = (numpy.matrix(list(_mean_coordinates(self.model_list)))).T

        self.zero_mean_model_list = [(p[0] - self.model_mean[0,0], \
                                p[1] - self.model_mean[1,0]) for p in self.model_list]
        self.zero_mean_data_list = [(p[0] - self.model_mean[0,0], \
                                p[1] - self.model_mean[1,0]) for p in self.data_list]
        if self.debug1:
            print("\nmodel mean in pixel coords: %s\n" % str(self.model_mean))
            _print_points("\nzero mean model list (pixel coords): ", self.zero_mean_model_list)
            _print_points("\nzero mean data list (pixel coords): ", self.zero_mean_data_list)

    def icp(self):
        if self.auto_select_model_and_data:
            if len(self.data_list) > len(self.model_list):
                print("\n>>>> SWAPPING THE MODEL AND THE DATA IMAGES <<<<\n\n")
                self.data_im, self.model_im = self.model_im, self.data_im
                self.data_list, self.model_list = self.model_list, self.data_list
                self.data_rval, self.model_rval = self.model_rval, self.data_rval
                self.data_segmentation, self.model_segmentation = \
                                  self.model_segmentation, self.data_segmentation
                self.data_all_corners, self.model_all_corners = \
                                    self.model_all_corners, self.data_all_corners
                self.data_edge_map, self.model_edge_map = self.model_edge_map, self.data_edge_map
        self.move_to_model_origin()
        old_error = float('inf')
        R = numpy.matrix( [[1.0, 0.0],[0.0, 1.0]] )
        T = (numpy.matrix([[0.0, 0.0]])).T
        self.R = R
        self.T = T
        self.R_for_iterations = {i : None for i in range(self.iterations)}
        self.T_for_iterations = {i : None for i in range(self.iterations)}
        model = self.zero_mean_model_list
        data = self.zero_mean_data_list
        model_dict = {"m" + str(i) : model[i] for i in range(len(model))}
        data_dict  = {"d" + str(i) : data[i] for i in range(len(data))}
        if self.debug2:
            _print_points_in_dict("\nmodel dict: ", model_dict)
            _print_points_in_dict("\ndata_dict: ", data_dict)
        error_for_iterations = []
        iteration = 0
        self.dir_name_for_results = "__result_" + str(self.subimage_index)
        if os.path.exists(self.dir_name_for_results):
            files = glob.glob(self.dir_name_for_results + "/*")
            map(lambda x: os.remove(x), files)
        else:
            os.mkdir(self.dir_name_for_results)
        while 1:
            if iteration == self.iterations: 
                print("\n\n\n***** FINAL RESULTS ****** FINAL RESULTS ****** FINAL RESULTS ****** FINAL RESULTS ****")
                print("\n\nImage size used in calculations:  width: %d  height: %d" % self.data_im.size)
                print("\nModel mean used for calculations: ") 
                print(str(self.model_mean))
                print("\nFinal rotation and translation of the data image with respect to the model mean: ")
                print("\nRotation:")
                print(str(self.R)) 
                print("\nTranslation:")
                print(str(self.T))
                print("\nData to Model Image Registration Error as a function of iterations: %s" % str(error_for_iterations))
                break
            if self.subimage_index is None:
                print("\n\n             STARTING ITERATION %s OUT OF %s\n" % (str(iteration+1), str(self.iterations)))
            else:
                print("\n\n  For subimages indexed %s   ==>  STARTING ITERATION %s OUT OF %s\n" % (str(self.subimage_index), str(iteration+1), str(self.iterations)))
            if self.debug2: _print_points_in_dict("\ndata_dict in loop: ", data_dict)
            xformed_data_dict = {d : R * (numpy.matrix( list(data_dict[d]) )).T + T for d in data_dict}
            xformed_data_dict = {d : (xformed_data_dict[d][0,0], xformed_data_dict[d][1,0]) \
                                                                        for d in xformed_data_dict}
            if self.debug2: _print_points_in_dict("\ntransformed data_dict in loop: ", xformed_data_dict)
            leastDistMapping, error_dict = \
              _least_dist_mapping(xformed_data_dict,model_dict,self.pixel_correspondence_dist_threshold)
            number_of_points_matched = len([x for x in leastDistMapping \
                                               if leastDistMapping[x] is not None])
            if self.debug2:
                print("\nleastDistMapping: ", [item[0]+"=>"+item[1] for item in sorted(leastDistMapping.items(),
                    lambda x,y: cmp(int(x[0].lstrip('md')),int(y[0].lstrip('md')))) if item[1] is not None])
            if self.debug2: _print_float_values_dict("\nerror values at data points: ", error_dict)
            if self.debug2: print("\nnumber of points matched: %s" % str(number_of_points_matched))
            error = functools.reduce(lambda x, y: x + y, [error_dict[x] for x in error_dict if error_dict[x] is not None])
            error = error / number_of_points_matched
            error_for_iterations.append(error)
            if self.debug2: print("\nold_error: %s    error: %s" % (str(old_error), str(error)))
            old_error = error
            # Which model and data points participated in matching:
            data_labels_used = [d for d in leastDistMapping.keys() if leastDistMapping[d] is not None]
            data_labels_used.sort(key = lambda x: int(x.lstrip('md')))
            model_labels_used = [leastDistMapping[d] for d in data_labels_used]
            if self.debug2: print("\ndata labels used: %s" % str(data_labels_used))
            if self.debug2: print("\nmodel labels used: %s" % str(model_labels_used)) 
            # Construct A matrix from data pixels:
            A = numpy.matrix([[data_dict[d][0] for d in data_labels_used],[data_dict[d][1] for d in data_labels_used]])
            if self.debug2: print("\nA matrix: %s" % str(A))
            # Now construct AATI matrix:
            AATI = A.T * numpy.linalg.inv( A * A.T )
            if self.debug2: print("\nAATI matrix: %s" % str(AATI))
            # Next construct B matrix from model pixels:
            B =  numpy.matrix([ [model_dict[m][0] - T[0,0] for m in model_labels_used], 
                                [model_dict[m][1] - T[1,0] for m in model_labels_used] ])
            if self.debug2: print("\nB matrix: %s" % str(B))
            matched_model_mean = numpy.matrix(list(_mean_coordinates([(model_dict[m][0], 
                                          model_dict[m][1]) for m in model_labels_used]))).T
            if self.debug2: print("\nmatched model mean: %s" % str(matched_model_mean))
            R_update = B * AATI * R.T
            [U,S,VT] = numpy.linalg.svd(R_update)
            U,VT = numpy.matrix(U), numpy.matrix(VT) 
            deter = numpy.linalg.det(U * VT)
            U[0,1] = U[0,1] * deter
            U[1,1] = U[1,1] * deter
            R_update = U * VT
            R = R_update * R
            print("\nRotation:")
            print (R)
            # Rotate the data for estimating the translation T
            data_matrix2 = R * A
            data_transformed_mean = numpy.matrix(list(_mean_coordinates([(data_matrix2[0,j], 
                                   data_matrix2[1,j]) for j in range(data_matrix2.shape[1])]))).T
            if self.debug2: print("\ndata transformed mean: %s" % str(data_transformed_mean))
            T = matched_model_mean - data_transformed_mean  
            print("\nTranslation:")
            print(T)
            # This is just for the binary case in the old icp()
            data_matrix_new = [ R * (numpy.matrix( list(data[p]))).T + T for p in range(len(data)) ] 
            data_transformed_new = \
                [ ( p[0,0] + self.model_mean[0,0], p[1,0] + self.model_mean[1,0] ) for p in data_matrix_new]
            displayWidth,displayHeight = self.data_im.size
            result_im = Image.new("1", (displayWidth,displayHeight), 0)
            for p in data_transformed_new:
                x,y = int(p[0]), int(p[1])
                if ( (0 <= x < displayWidth) and (0 <= y < displayHeight ) ):
                    result_im.putpixel( (x,y), 255 )
            result_im.save( self.dir_name_for_results + "/__result" + str(iteration) + ".jpg")
            iteration = iteration + 1
            self.R,self.T = R,T

    def display_results_as_movie(self):
        mw = Tkinter.Tk()                       
        tkFont.nametofont('TkDefaultFont').configure(size=20)    
        helv36 = tkFont.Font(family="Helvetica", size=28, weight='bold')    
        width, height = mw.winfo_screenwidth()-500, mw.winfo_screenheight()-100
        mw.title('''SHOW ITERATIONS AS A MOVIE   (red pixels are from the model and green '''
                 '''pixels from the data)''')
        mw.geometry( "%dx%d+100+100" % (width,height) )
        mw.focus_set()
        mw.bind("<Escape>", lambda e: e.widget.destroy())
        tkim = [None] * self.iterations
        model_image = self.model_im
        w_model, h_model =  model_image.size
        model_image_for_movie = Image.new("RGB", (w_model,h_model), (0,0,0))
        (model_mingray,model_maxgray) = model_image.getextrema()
        for i in range(w_model):
            for j in range(h_model):
                if model_image.getpixel((i,j)) > 0:
                    color_val = model_image.getpixel((i,j)) * int(255/model_maxgray)
                    model_image_for_movie.putpixel((i,j),(color_val,0,0))
        model_image = model_image_for_movie
        if w_model > h_model:
            w_display = int(0.5 * width)
            h_display = int(w_display * (h_model/float(w_model)))
        else:
            h_display = int(0.5 * height)
            w_display = int(h_display * (w_model/float(h_model)))
        imageframe = Tkinter.Frame(mw, width=w_display, height=h_display+50).pack()
        iterationIndexFrame = Tkinter.Frame(mw, width=w_display, height=10).pack()
        iterationLabelText = Tkinter.StringVar()
        Tkinter.Label(iterationIndexFrame,
                      textvariable = iterationLabelText,
                      anchor = 'c',
                      relief = 'groove',
                     ).pack(side='top', padx=10, pady=10)
        separator = Tkinter.Frame(mw, height=2, bd=1, relief=Tkinter.SUNKEN)
        separator.pack(fill=Tkinter.X, padx=5, pady=5)
        buttonframe = Tkinter.Frame(mw, width=w_display, height=10).pack()
        Tkinter.Button(buttonframe, 
                       text = 'Play movie again',                
                       anchor = 'c',
                       relief = 'raised',
                       font = helv36,
                       command = lambda: self.callbak(mw)
                      ).pack(side='top', padx=10, pady=5)

        separator = Tkinter.Frame(mw, height=2, bd=1, relief=Tkinter.SUNKEN)
        separator.pack(fill=Tkinter.X, padx=5, pady=5)    
        messageFrame = Tkinter.Frame(mw, width=w_display, height=10).pack()
        messageLabelText = Tkinter.StringVar()
        Tkinter.Label(messageFrame,
                      textvariable = messageLabelText,
                      anchor = 'c',
                      relief = 'groove',
                     ).pack(side='top', padx=10, pady=10)
        messageLabelText.set('''NOTE: It is best to NOT close this window until all the '''
                             '''iterations are completed''')
        self.iteration_control_flag = 1
        xpos = int( (width - w_display)/2 )
        ypos = 20
        for i in range(0,self.iterations):
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
        while self.iteration_control_flag:
            for i in range(0,self.iterations):
                try:
                    tkim[i] = Image.open(self.dir_name_for_results + "/__result_color" + str(i) + ".jpg")
                    out_image = ImageChops.add( model_image, tkim[i] )
                    out_out_image = out_image.resize((w_display,h_display), 
                                                     Image.ANTIALIAS)
                    out_photo_image = ImageTk.PhotoImage( out_out_image )
                    label_image = Tkinter.Label(imageframe,image=out_photo_image )
                    label_image.place(x=xpos,y=ypos,width=w_display,height=h_display)
                    iterationLabelText.set( "Iteration Number: " + str(i+1) )
                    self.iteration_control_flag = 0
                    if i < self.iterations - 1: mw.after(1000, mw.quit)       
                    mw.mainloop(0)
                except IOError: pass       

    def callbak(self,arg):
        arg.quit()
        self.iteration_control_flag = 1

    def displayImage6(self, argimage, title=""):
        '''
        This does the same thing as displayImage3() except that it also provides for
        "save" and "exit" buttons. Note that 'argimage' must be of type Image.
        '''
        width,height = argimage.size
        mw = Tkinter.Tk()
        winsize_x,winsize_y = None,None
        screen_width,screen_height = mw.winfo_screenwidth(),mw.winfo_screenheight()
        if screen_width <= screen_height:
            winsize_x = int(0.5 * screen_width)
            winsize_y = int(winsize_x * (height * 1.0 / width))            
        else:
            winsize_y = int(0.5 * screen_height)
            winsize_x = int(winsize_y * (width * 1.0 / height))
        display_image = argimage.resize((winsize_x,winsize_y), Image.ANTIALIAS)
        mw.title(title)   
        canvas = Tkinter.Canvas( mw,                         
                             height = winsize_y,
                             width = winsize_x,
                             cursor = "crosshair" )   
        canvas.pack( side = 'top' )                               
        frame = Tkinter.Frame(mw)                            
        frame.pack( side = 'bottom' )                             
        Tkinter.Button( frame,         
                text = 'Save',                                    
                command = lambda: canvas.postscript(file = title.partition(' ')[0] + ".jpg") 
              ).pack( side = 'left' )                             
        Tkinter.Button( frame,                        
                text = 'Exit',                                    
                command = lambda: mw.destroy(),                    
              ).pack( side = 'right' )                            
        photo = ImageTk.PhotoImage(argimage.resize((winsize_x,winsize_y), Image.ANTIALIAS))
        canvas.create_image(winsize_x/2,winsize_y/2,image=photo)
        mw.mainloop()

    def display_images_used_for_edge_based_icp(self):
        tk_images = []
        image_labels = []
        rootWindow = Tkinter.Tk()
        screen_width,screen_height =rootWindow.winfo_screenwidth(),rootWindow.winfo_screenheight()
        rootWindow.geometry( str(int(0.8 * screen_width)) + "x" + str(int(0.9 * screen_height)) + "+50+50") 
        canvas = Tkinter.Canvas(rootWindow)
        canvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=Tkinter.TRUE)
        scrollbar = Tkinter.Scrollbar(rootWindow,orient=Tkinter.HORIZONTAL,command=canvas.xview)
        scrollbar.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        canvas.configure(xscrollcommand=scrollbar.set)
        def set_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        frame = Tkinter.Frame(canvas)
        canvas.create_window((0,0), window=frame, anchor=Tkinter.NW)
        frame.bind('<Configure>', set_scrollregion)
        cellwidth = 2* self.data_im.size[0]
        padding = 10
        if cellwidth > 80:
            fontsize = 25
        else:
            fontsize = 15
        font = ImageFont.truetype(self.font_file, fontsize)
        data_image_width, data_image_height = self.data_im.size
        orig_image_width,orig_image_height = self.original_model_im.size
        original_model_im = self.original_model_im.copy()
        displayWidth,displayHeight = None,None
        if data_image_width > data_image_height:
            displayWidth = int(0.9 * cellwidth)
            displayHeight = int(displayWidth * data_image_height * 1.0 / data_image_width)
        else:
            displayHeight = int(0.9 * cellwidth)
            displayWidth = int(displayHeight * data_image_width * 1.0 / data_image_height )
        original_model_im.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        model_edge_map = self.model_edge_map.copy()
        model_edge_map = model_edge_map.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        model_edge_map.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        model_im = self.model_im.copy()
        model_im = model_im.resize((orig_image_width,orig_image_height), Image.ANTIALIAS)
        model_im.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        original_data_im = self.original_data_im.copy()
        original_data_im = original_data_im.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        original_data_im.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        data_edge_map = self.data_edge_map.copy()
        data_edge_map = data_edge_map.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        data_edge_map.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        data_im = self.data_im.copy()
        data_im = data_im.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        data_im.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        textImage7 = Image.new( "F", (displayWidth,displayHeight), 200 )
        draw = ImageDraw.Draw(textImage7)
        draw.text((10,10), "Close this window", font=font) 
        draw.text((10,30), "to see a movie of", font=font) 
        draw.text((10,50), "image registration", font=font) 
        image_labels.append("Model")
        tk_images.append(ImageTk.PhotoImage( original_model_im ))
        image_labels.append("Model Edge Map")
        tk_images.append(ImageTk.PhotoImage( model_edge_map ))
        image_labels.append("Model Edge Pixels\nRetained for ICP")
        tk_images.append(ImageTk.PhotoImage( model_im ))
        image_labels.append("Data")
        tk_images.append(ImageTk.PhotoImage( original_data_im ))
        image_labels.append("Data Edge Map")
        tk_images.append(ImageTk.PhotoImage( data_edge_map ))
        image_labels.append("Data Edge Pixels\nRetained for ICP")
        tk_images.append(ImageTk.PhotoImage( data_im ))
        tk_images.append(ImageTk.PhotoImage( textImage7 ))
        for i in range(3):
            Tkinter.Label(frame,image=tk_images[i], text=image_labels[i], font=fontsize, compound=Tkinter.BOTTOM, width=cellwidth).grid(row=0,column=i,padx=10,pady=30)
        for i in range(3,6):
            Tkinter.Label(frame,image=tk_images[i], text=image_labels[i], font=fontsize, compound=Tkinter.BOTTOM, width=cellwidth).grid(row=1,column=i-3,padx=10,pady=30)
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

    def display_images_used_for_corner_based_icp(self):
        tk_images = []
        image_labels = []
        rootWindow = Tkinter.Tk()
        screen_width,screen_height =rootWindow.winfo_screenwidth(),rootWindow.winfo_screenheight()
        rootWindow.geometry( str(int(0.8 * screen_width)) + "x" + str(int(0.9 * screen_height)) + "+50+50") 
#        rootWindow.geometry("1400x750+50+50") 
        canvas = Tkinter.Canvas(rootWindow)
        canvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=Tkinter.TRUE)
        scrollbar = Tkinter.Scrollbar(rootWindow,orient=Tkinter.HORIZONTAL,command=canvas.xview)
        scrollbar.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        canvas.configure(xscrollcommand=scrollbar.set)
        def set_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        frame = Tkinter.Frame(canvas)
        canvas.create_window((0,0), window=frame, anchor=Tkinter.NW)
        frame.bind('<Configure>', set_scrollregion)
        cellwidth = 3 * self.data_im.size[0]
        padding = 10
        if cellwidth > 80:
            fontsize = 25
        else:
            fontsize = 15
        font = ImageFont.truetype(self.font_file, fontsize)
        data_image_width, data_image_height = self.data_im.size
        orig_image_width,orig_image_height = self.original_model_im.size
        original_model_im = self.original_model_im.copy()
        displayWidth,displayHeight = None,None
        if data_image_width > data_image_height:
            displayWidth = int(0.9 * cellwidth)
            displayHeight = int(displayWidth * data_image_height * 1.0 / data_image_width)
        else:
            displayHeight = int(0.9 * cellwidth)
            displayWidth = int(displayHeight * data_image_width * 1.0 / data_image_height )
        image_labels.append("Model")
        original_model_im.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)                       # 1
        image_labels.append("Model\nSegmentation")
        model_segmentation = self.model_segmentation.copy()                                              # 2
        model_segmentation = model_segmentation.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        model_segmentation.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        image_labels.append("Model\nCorner Pixels")
        model_all_corners = self.model_all_corners.copy()                                                # 3
        model_all_corners = model_all_corners.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        model_all_corners.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        image_labels.append("Model Corners\nRetained for ICP")
        model_corners_retained = self.model_im.copy()                                                    # 4
        model_corners_retained = model_corners_retained.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        model_corners_retained.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        image_labels.append("Data")
        original_data_im = self.original_data_im.copy()                                                  # 5
        original_data_im = original_data_im.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        original_data_im.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        image_labels.append("Data\nSegmentation")
        data_segmentation = self.data_segmentation.copy()                                                # 6
        data_segmentation = data_segmentation.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        data_segmentation.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)        
        image_labels.append("Data\nCorner Pixels")
        data_all_corners = self.data_all_corners.copy()                                                  # 7
        data_all_corners = data_all_corners.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        data_all_corners.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        image_labels.append("Data Corners\nRetained for ICP")
        data_corners_retained = self.data_im.copy()                                                      # 8
        data_corners_retained = data_corners_retained.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        data_corners_retained.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        tk_images.append(ImageTk.PhotoImage( original_model_im ))
        tk_images.append(ImageTk.PhotoImage( model_segmentation ))
        tk_images.append(ImageTk.PhotoImage( model_all_corners ))
        tk_images.append(ImageTk.PhotoImage( model_corners_retained ))
        tk_images.append(ImageTk.PhotoImage( original_data_im ))
        tk_images.append(ImageTk.PhotoImage( data_segmentation ))
        tk_images.append(ImageTk.PhotoImage( data_all_corners ))
        tk_images.append(ImageTk.PhotoImage( data_corners_retained ))
        for i in range(4):
            Tkinter.Label(frame,image=tk_images[i], text=image_labels[i], font=fontsize, compound=Tkinter.BOTTOM, width=cellwidth).grid(row=0,column=i,padx=10,pady=30)
        for i in range(4,8):
            Tkinter.Label(frame,image=tk_images[i], text=image_labels[i], font=fontsize, compound=Tkinter.BOTTOM, width=cellwidth).grid(row=1,column=i-4,padx=10,pady=30)
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

    def display_images_used_for_binary_image_icp(self):
        tk_images = []
        image_labels = []
        rootWindow = Tkinter.Tk()
        screen_width,screen_height =rootWindow.winfo_screenwidth(),rootWindow.winfo_screenheight()
        rootWindow.geometry( str(int(0.8 * screen_width)) + "x" + str(int(0.9 * screen_height)) + "+50+50") 
#        rootWindow.geometry("1400x750+50+50") 
        canvas = Tkinter.Canvas(rootWindow)
        canvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=Tkinter.TRUE)
        scrollbar = Tkinter.Scrollbar(rootWindow,orient=Tkinter.HORIZONTAL,command=canvas.xview)
        scrollbar.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        canvas.configure(xscrollcommand=scrollbar.set)
        def set_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        frame = Tkinter.Frame(canvas)
        canvas.create_window((0,0), window=frame, anchor=Tkinter.NW)
        frame.bind('<Configure>', set_scrollregion)
        cellwidth = 5 * self.data_im.size[0]
        padding = 10
        if cellwidth > 80:
            fontsize = 25
        else:
            fontsize = 15
        font = ImageFont.truetype(self.font_file, fontsize)
        data_image_width, data_image_height = self.data_im.size
        orig_image_width,orig_image_height = self.original_model_im.size
        orig_image_width,orig_image_height = 5 * orig_image_width, 5 * orig_image_height
        original_model_im = self.original_model_im.copy()
        displayWidth,displayHeight = None,None
        if data_image_width > data_image_height:
            displayWidth = int(0.9 * cellwidth)
            displayHeight = int(displayWidth * data_image_height * 1.0 / data_image_width)
        else:
            displayHeight = int(0.9 * cellwidth)
            displayWidth = int(displayHeight * data_image_width * 1.0 / data_image_height )
        image_labels.append("Model")
        original_model_im = original_model_im.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        original_model_im.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)                  
        image_labels.append("Data")
        original_data_im = self.original_data_im.copy()
        original_data_im = original_data_im.resize((orig_image_width, orig_image_height), Image.ANTIALIAS)
        original_data_im.thumbnail((displayWidth,displayHeight), Image.ANTIALIAS)
        tk_images.append(ImageTk.PhotoImage( original_model_im ))
        tk_images.append(ImageTk.PhotoImage( original_data_im ))
        for i in range(2):
            Tkinter.Label(frame,image=tk_images[i], text=image_labels[i], font=fontsize, compound=Tkinter.BOTTOM, width=cellwidth).grid(row=0,column=i,padx=10,pady=30)
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

    def cleanup_directory(self):
        for filename in glob.glob( self.dir_name_for_results + '/__result*.jpg' ): os.unlink(filename)

#   Destructor:
#    def __del__(self):
#        if not self.save_output_images:
#            os.system('rm __result*.jpg')

    @staticmethod
    def gendata( feature, imagesize, position, orientation, output_image_name ):
        '''
        Permissible values for feature:  'line', 'triangle'

        Permissible values for imagesize: (m,n) tuple for the size of the output image

        Permissible values for position:  (x,y) pixel coordinates

        Permissible values for orientation:  integer value for degrees

        The code here is just the simplest example of synthetic data
        generation for experimenting with ICP.  You can obviously 
        construct more complex model and data images by calling on the
        other shape drawing primitives of the ImageDraw class.  When
        specifying coordinates, note the following

               .----------> positive x
               |
               |
               |        
               V
             positive y

        A line is drawn from the first pair (x,y) coordinates to the
        second pair.
        '''
        width,height = imagesize
        x,y = position
        theta = orientation
        tan_theta = scipy.tan( theta * scipy.pi / 180 )
        cos_theta =  scipy.cos( theta * scipy.pi / 180 )
        sin_theta =  scipy.sin( theta * scipy.pi / 180 )

        im = Image.new( "L", imagesize, 0 )
        draw = ImageDraw.Draw(im)

        if feature == 'line':
            delta =  y / tan_theta
            if delta <= x:
                x1 = x - y / tan_theta
                y1 = 0
            else:
                x1 = 0
                y1 = y - x * tan_theta
            x2 = x1 + height / tan_theta
            y2 = height
            if x2 > width:
                excess = x2 - width
                x2 = width
                y2 = height - excess * tan_theta
            draw.line( (x1,y1,x2,y2), fill=255)
            del draw
            im.save( output_image_name )

        elif feature == "triangle":
            x1 = int(width/2.0)
            y1 = int(0.7*height)
            x2 = x1 -  int(width/4.0)
            y2 = int(height/4.0)
            x3 = x1 +  int(width/4.0)
            y3 = y2
            draw.line( (x1,y1,x2,y2), fill=255 )
            draw.line( (x1,y1,x3,y3), fill=255 )
            draw.line( (x2,y2,x3,y3), fill=255 )
            del draw
            h2 = int(height/2)
            w2 = int(width/2)
            im = im.transform(imagesize, Image.AFFINE, \
              (cos_theta,sin_theta,-x,-sin_theta,cos_theta,-y), Image.BICUBIC )
            im.save( output_image_name )

#        elif feature == "ellipse":
#            bounding_box = ( int(0.3*width), int(0.3*height), \
#                                     int(0.7*width), height-1 )
#            draw.ellipse( bounding_box, Image.BICUBIC )
#            del draw
#            im.transform(imagesize, Image.AFFINE, \
#                   (cos_theta,sin_theta,-x,-sin_theta,cos_theta,-y) )
#            im.save( output_image_name )       

        else:
            print("unknown feature requested")
            sys.exit(0)
        
#-------------------------------- End of ICP Class Definition  ------------------------------------

#----------------------------------    Test code follows         ----------------------------------

if __name__ == '__main__': 

    #ICP.gendata( "triangle", (80,80), (10,10), 30, "newtriangle2.jpg" )

    icp = ICP( 
               binary_or_color = "color",
               corners_or_edges = "edges",
               auto_select_model_and_data = 1,
               calculation_image_size = 200,
               max_num_of_pixels_used_for_icp = 300,
               pixel_correspondence_dist_threshold = 20,
               iterations = 24,
               model_image =  "Examples/SydneyOpera.jpg",
               data_image = "Examples/SydneyOpera2.jpg",
            )

    icp.extract_pixels_from_color_image("model")
    icp.extract_pixels_from_color_image("data")
    icp.condition_data()
    icp.icp()
    icp.display_images_used_for_edge_based_icp()
    icp.display_results_as_movie()
    icp.cleanup_directory()

