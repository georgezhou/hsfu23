import string
import pyfits
import sys
import functions
from numpy import *

###################
### Description ###
###################

### Takes a raw image list output from ls
### Removes individual images that are calibration frame
### Pass the image list on for further reduction to be done on them

### usage: python mod_imagelist.py file_path imagelist

#################
### Functions ###
#################

def write_list_to_file(list,file):
	output_table = open(file,"w")
	for i in range(len(list)):
		output_table.write(list[i] + "\n")
	output_table.close()

########################
### Start of program ###
########################

### Set file_path
file_path = sys.argv[1]

### Load imagelist
imagelist = functions.read_ascii(file_path + "image_list")

#disallowed = ["Arc","Ne-Ar","Flat","Quartz","bias","","SkyFlat"]
disallowed = ["arc","Ne-Ar","Flat","Quartz","bias","","SkyFlat","zero","wire"]
imagelist_temp = []

for i in imagelist:
        ### Find object type
        hdulist = pyfits.open(file_path + i)
        object_name = hdulist[0].header["IMAGETYP"]
        if object_name.lower() not in map(str.lower,disallowed):
                imagelist_temp.append(i)

imagelist = imagelist_temp

print imagelist

write_list_to_file(imagelist,file_path + "image_list")
