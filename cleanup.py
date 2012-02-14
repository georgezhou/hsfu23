import functions
import numpy
import pyfits
import string
import os
import sys

###################
### Description ###
###################

### Remove non-essential temporary files in the temp/ folder

### If an image is not a SpecPhot or RV Standard, we remove the associated
### temporary files.

### usage: python cleanup.py file_path

########################
### Start of program ###
########################

print "Cleaning up"

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

### Change directory to file_path
program_dir = os.getcwd() + "/" #Save the current working directory
os.chdir(file_path) #Change to file_path

### Create image list
os.system("ls *.fits > temp_image_list")
image_list = functions.read_ascii("temp_image_list")
os.system("rm temp_image_list")

for file_name in image_list:
    hdulist = pyfits.open(file_path + file_name)
    image_type = hdulist[0].header["IMAGETYP"]
    comment = hdulist[0].header["NOTES"]
    hdulist.close()

    file_name_short = string.split(file_name,".")[0]

    os.system("rm -f " + file_path_temp + file_name)
    os.system("rm -f " + file_path_temp +"*ccdproc*"+ file_name)
    for i in range(0,12):
        os.system("rm -f " + file_path_temp + "*"+str(i) + "_" + file_name_short+"*")
        
    if image_type == "OBJECT" and comment == "":
        os.system("rm -f "+file_path_temp+"*"+file_name_short+"*")
        os.system("rm -f "+file_path_temp+"database/*"+file_name_short+"*")
