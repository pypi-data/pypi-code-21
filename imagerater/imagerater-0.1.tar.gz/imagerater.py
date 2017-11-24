#!/usr/bin/env python

import time
from PIL import Image
import glob
from matplotlib import pyplot as plt
import numpy as np
import sys, getopt

plt.ion()
filelocation=""
question=""
try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:x:f:q:",["minimum=","maximum=","filelocation=","question="])
except getopt.GetoptError:
	print('imagerater.py -f <filelocation> -i <minimum> -x <maximum> -q <question>')
	sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('imagerater.py -f <filelocation> -i <minimum> -x <maximum> -q <question>')
        sys.exit()
    elif opt in ("-i", "--minimum"):
        min = int(arg)
    elif opt in ("-x", "--maximum"):
        max = int(arg)
    elif opt in ("-f", "--filelocation"):
        filelocation = arg
    elif opt in ("-q", "--question"):
        question = arg

print('Minimum is {}'.format(min))
print('Maximum is {}'.format(max))
print('Filelocation is {}'.format(filelocation))
print('Question is "{}"'.format(question))

def get_rating(question, min, max):
    while True:
        try:
            value = int(input(question))
        except ValueError:
            print("Please enter a valid integer.")
            continue

        if (value < min or value > max):
            print("Sorry, your input must be between {} and {}.".format(min, max))
            continue

        else:
            break
    return value

def showAndRateImages(filelocation,min,max,question):
    #Get dimension of first image
    firstFile = glob.glob(filelocation)[0]
    firstImage = Image.open(firstFile)
    firstImageSize = np.array(list(firstImage.getdata())).flatten()
    #print(firstImageSize.shape)
    imageAndRating = np.zeros((1, firstImageSize.shape[0] + 1), dtype=np.int8)
    i = 0
    for filename in glob.glob(filelocation):
        #Open image
        im=Image.open(filename)
        #Flatten image
        imageFlat=np.array(list(im.getdata())).flatten()
        imageFlat_reshaped = imageFlat.reshape(imageFlat.shape[0], -1).T
        #Normalize image
        imageFlat_reshaped_normalized = imageFlat_reshaped/255.
        plt.close()
        plt.figure()
        plt.imshow(im)
        plt.draw()
        rating = get_rating(question, min, max)
        rating = np.array(rating).reshape(1,1)
        ratedData = np.append(imageFlat_reshaped_normalized, rating, axis=1)
        if(ratedData.shape[1] == imageAndRating.shape[1]):
            imageAndRating = np.append(imageAndRating, ratedData, axis=0)
        else:
            print("Image at i={} with filename: {} skipped".format(i, filename))
        i += 1
        #Delete first row of zeros
        if(i==1):
            imageAndRating = np.delete(imageAndRating, (0), axis=0)
        if (i % 10 == 0):
    	    np.save('imageAndRatingMatrix' + str(i), imageAndRating)
    	    print(imageAndRating.shape)
    	    print("You have rated and saved {} images.".format(i))
    	    #print(imageAndRating)
    	    continue
#TODO: abfangen, wenn keine file location gegeben wurde und wenn keine min, max oder question mitgegeben wurden
showAndRateImages(filelocation,min,max,question)








