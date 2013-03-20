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

disallowed = ["Arc","Ne-Ar","Flat","Quartz","bias","","SkyFlat"]

imagelist_temp = []
for i in range(len(imagelist)):
	### Find object type
	image_name = imagelist[i]
	hdulist = pyfits.open(file_path + image_name)
	object_name = hdulist[0].header["OBJECT"]
	allowed = True
	for i in range(len(disallowed)):
		if object_name == disallowed[i]:
			allowed = False
			break
	if allowed == True:
		imagelist_temp.append(image_name)

imagelist = imagelist_temp

print imagelist

write_list_to_file(imagelist,file_path + "image_list")
