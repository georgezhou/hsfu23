import functions
from numpy import *
import string
import pyfits
import sys
import os
import mysql_insert

###################
### Description ###
###################

### Connect to HSMSO follow-up database
### Insert / update entry for file_name
### This program is specific for updating spectype observations
### Requires the files spectype.txt, image_quality.txt to have been
### created first

### usage: python update_spectype.py file_path file_name

########################
### Start of program ###
########################

### Set file path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

### Set file name
file_name = sys.argv[2]

### Find info from config file
grating = functions.read_config_file("GRATING")
resolution = int(grating[1:])
dichroic = functions.read_config_file("DICHROIC")

### Set program dir and change working directory
program_dir = os.getcwd() + "/" #Save the current working directory
os.chdir(file_path_reduced) #Change to ../temp/ dir

### Find info from the fits header
hdulist = pyfits.open(file_path + file_name)
object_name = hdulist[0].header["OBJECT"]
dateobs = hdulist[0].header["DATE-OBS"]
mjd = hdulist[0].header["MJD-OBS"]
exptime = hdulist[0].header["EXPTIME"]
comment = hdulist[0].header["NOTES"]
hdulist.close()

### Read info from text files in reduced/
spectype = functions.read_ascii("spectype.txt")
spectype = functions.read_table(spectype)

for entry in spectype:
    if entry[1] == object_name and entry[0] == file_name:
        teff = entry[2]
        logg = entry[4]
        feh = entry[6]

image_quality = functions.read_ascii("image_quality.dat")
image_quality = functions.read_table(image_quality)

for entry in image_quality:
    if entry[0] == file_name and entry[1] == object_name:
        sn = entry[5]

mysql_insert.db_spectype_entry(object_name,file_name,grating,resolution,dichroic,dateobs,mjd,teff,logg,feh,sn,exptime,comment)
