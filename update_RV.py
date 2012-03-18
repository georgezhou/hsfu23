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
### This program is specific for updating RV observations
### Requires the files RV.dat, ccf_log.txt, image_quality.txt to have been
### created first

### usage: python update_RV.py file_path file_name

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
RV_dat = functions.read_ascii("RV.dat")
RV_dat = functions.read_table(RV_dat)

for entry in RV_dat:
    if entry[0] == object_name and entry[1] == file_name:
        if functions.is_number(entry[2]):
            hjd = entry[2] + 50000
            RV = entry[3]
            RV_err = entry[4]
            ccf_height = entry[5]

ccf_log = functions.read_ascii("ccf_log.txt")
ccf_log = functions.read_table(ccf_log)

for entry in ccf_log:
    if entry[0] == file_name and entry[1] == object_name:
        ccf_fwhm = entry[3]
        bis = entry[4]
        bis_err = entry[5]

image_quality = functions.read_ascii("image_quality.dat")
image_quality = functions.read_table(image_quality)

for entry in image_quality:
    if entry[0] == file_name and entry[1] == object_name:
        sn = entry[5]

mysql_insert.db_rv_entry(object_name,file_name,grating,resolution,dichroic,dateobs,mjd,hjd,RV,RV_err,ccf_fwhm,ccf_height,bis,bis_err,sn,exptime,comment)
