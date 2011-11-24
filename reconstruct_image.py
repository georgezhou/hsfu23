### Load python modules
import pyfits
from numpy import *
import string
import sys
import os
import functions
import matplotlib.pyplot as plt
import time

###################
### Description ###
###################

### Usage: chop_image.py file_path file_temp

########################
### Start of program ###
########################

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

image_slices_list = functions.read_ascii(file_path_temp + "slice_" + file_name+".txt")
image_slices_list = functions.read_table(image_slices_list)
image_slices_list = image_slices_list[1:]

os.chdir(file_path_temp)

########################################################
### Reconstruct array by reading in each image slice ###
########################################################

spatial_image = []
for image_slice in image_slices_list:
    row_image = pyfits.getdata(image_slice[0])
    row_values = []
    
    for i in row_image:
        row_values.append(median(i))

    for i in range(len(row_values),38):
        row_values.append(0)
    spatial_image.append(row_values)

spatial_image = array(spatial_image)
plt.contourf(spatial_image)
plt.show()
