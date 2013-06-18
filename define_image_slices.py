import pyfits
from numpy import *
import string
import sys
import os
import functions

###################
### Description ###
###################

### Work out start and end of each order in the WiFeS raw data
### Use flats to do so
### This then allows us to remove parts of the image that do not contain data
### Step can be omitted to save time

### Usage: define_image_slices.py file_path

########################
### Start of Program ###
########################

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

### Check if we have a master flat file
### If so use this to gauge where the image slices are
if os.path.exists(file_path_temp + "master_flat.fits"):
    print "Using master_flat.fits to find the positions of each image slice"
    ### Use pyfits to readin master flats
    master_flat = file_path_temp + "master_flat.fits"
    master_flat = pyfits.getdata(master_flat)
    master_flat = transpose(master_flat)
    master_flat = master_flat[2000:2100] ### Choose only the central 100 columns
    master_flat = transpose(master_flat)

    ### Find the median value across the column
    median_values = []
    for i in range(len(master_flat)):
        median_values.append(median(master_flat[i]))

    ### Find the start and end of each image slice
    initial_value = median_values[0]
    threshold = mean(median_values)/2.
    region_table = []
    for i in range(1,len(median_values)):
        if median_values[i] > threshold and median_values[i-1] < threshold:
            region_table.append([i+1,i+38])
            #region_table.append([i+5,i+33])

    ### Write the table into a text file
    image_slice_table = open(file_path_temp + "image_slice_table.txt","w")
    functions.write_table(region_table,image_slice_table)
    image_slice_table.close()

### If no master flat exists, use default table
else:
    print "Using default image slice positions"
    camera = functions.read_config_file("CAMERA")
    if camera == "red":
        os.system("cp image_slice_table_red.txt " + file_path_temp + "image_slice_table.txt")
    if camera == "blue":
        os.system("cp image_slice_table_blue.txt " + file_path_temp + "image_slice_table.txt")

