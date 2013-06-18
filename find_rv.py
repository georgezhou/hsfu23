### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import pyfits
import glob

### Load functions script (located in the same folder)
import functions

### Load iraf moduels
iraf.imred()
iraf.imred.ccdred()
iraf.imred.kpnoslit()

###################
### Description ###
###################

### Identifies and appends to list all RV standard stars in file_path

### Usage: python find_arc.py file_path

#################
### Functions ###
#################

def check_head(input_list,head_param,check_string):
    match = []
    for i in range(len(input_list)):
        file_location = object_list[input_list[i]][0]
        hdulist = pyfits.open(file_location)
        head_param_out = hdulist[0].header[head_param]
        if head_param_out == check_string:
            match.append(input_list[i])
    return match

########################
### Start of program ###
########################

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

################################################
### Open file_path and find all RV_standards ###
################################################

RV_list = open(file_path_temp + "RV_Standard_list","w")


os.chdir(file_path)
file_list = glob.glob("*.fits")
for file_name in file_list:
    hdulist = pyfits.open(file_name)
    notes = hdulist[0].header["NOTES"]
    if notes == "RV Standard":
        file_name_short = string.split(file_name,".fits")[0]
        RV_list.write(file_name_short+"\n")
RV_list.close()


# ### Get a list of fits files with objects begining in "HD"
# object_list = functions.ccdlist_extract(iraf.ccdlist(file_path +"*.fits",Stdout = 1))
# HD_match = functions.ccdlist_identify_HD(object_list)

# ### Open those images and check if NOTES says "RV Standard"
# RV_match = check_head(HD_match,"NOTES","RV Standard")

# ### Write the file_names to temp textfile
# for i in range(len(RV_match)):
#     file_name = object_list[RV_match[i]][2] + "\n"
#     RV_list.write(file_name)
# RV_list.close()



