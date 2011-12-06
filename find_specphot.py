### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import pyfits

### Load functions script (located in the same folder)
import functions

### Load iraf moduels
iraf.imred()
iraf.imred.ccdred()
iraf.imred.kpnoslit()

###################
### Description ###
###################

### Identifies and appends to list all specphot in file_path

### Usage: python find_specphot.py file_path

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
#file_path = "/priv/miner3/hat-south/george/Honours/data/wifes/2010/"
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

############################################
### Open file_path and find all SpecPhot ###
############################################

### Get a list of fits files with objects begining in "HD"
object_list = functions.ccdlist_extract(iraf.ccdlist(file_path +"*.fits",Stdout = 1))
HD_match = functions.ccdlist_identify_HD(object_list)

HD_match = []
for i in range(len(object_list)):
    HD_match.append(i)

### Open those images and check if NOTES says "RV Standard"
SP_match = check_head(HD_match,"NOTES","SpecPhot")

### Write the file_names to temp textfile
SP_list = open(file_path_temp + "SpecPhot_list","w")
for i in range(len(SP_match)):
    file_name = object_list[SP_match[i]][2] + "\n"
    SP_list.write(file_name)
