### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import functions

### Load iraf moduels
iraf.imred()
iraf.imred.ccdred()
iraf.imred.kpnoslit()

###################
### Description ###
###################

### We chop the image up such that each image slice is its own file
### This makes it easier to treat in subsequent steps
### Eg. makes it easier to straighten the lines, or reconstruct
### a spatial image

### Usage: chop_image.py file_path file_temp

########################
### Start of program ###
########################

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]
biassubtracted_file_name = "out_ccdproc_" + file_name

### Load in the image slices table
### This table was created by define_image_slices.py
### and contains locations of the image slices
### according to a flat field frame
image_slices = functions.read_ascii(file_path_temp + "image_slice_table.txt")
image_slices = functions.read_table(image_slices)

### Loop through and cut out each slice
### save in individual files

print "Chopping image into its image slices"

os.chdir(file_path_temp)

slices_file_list = ""
for i in range(len(image_slices)):
    start_column = int(image_slices[i][0])
    end_column = int(image_slices[i][1])
    region = '[1:4093,' + str(start_column) + ':'+str(end_column)+']'
    print region
    os.system("rm " + str(i) +"_"+ file_name)

    iraf.imcopy(
        input = biassubtracted_file_name + region,\
        output = str(i) +'_'+ file_name,\
        verbose =1)

    ### Save the names of the output files into a list
    slices_file_list = slices_file_list + str(i)+"_" + file_name + "\n"

### Save this list of output files into an ascii file
### This is called on by future programs
image_slices_file_list = open("slice_"+file_name + ".txt","w")
image_slices_file_list.write(slices_file_list)
image_slices_file_list.close()
