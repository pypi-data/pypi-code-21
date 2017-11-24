import fabio
from numpy import  *
img = fabio.open('E:/2017-01-30-test_0_00082.edf') # Open image file
from matplotlib import pyplot       # Load matplotlib
pyplot.imshow(log(img.data))             # Display as an image
pyplot.show()                       # Show GUI window