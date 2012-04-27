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

image_quality = functions.read_ascii("image_quality.dat")
image_quality = functions.read_table(image_quality)

for entry in image_quality:
    if entry[0] == file_name and entry[1] == object_name:
        sn = entry[5]

import MySQLdb
sql_date = string.split(dateobs,"T")[0]
sql_time = string.split(dateobs,"T")[1]

print "Connecting to database"
db=MySQLdb.connect(host="marbles.anu.edu.au",user="daniel",passwd="h@ts0uthDB",db="daniel1")

c = db.cursor()
c.execute("""SELECT SPECid FROM SPEC WHERE SPECmjd=""" + str(mjd) + """ and SPECobject=\"%s\" """ % object_name)

duplicate = c.fetchone()
if not duplicate == None:
    print "Updating entry"

    command = """UPDATE SPEC SET """
    command = command+"""SPECsn=""" + str(sn)
    command = command+""" WHERE SPECmjd=""" + str(mjd) + """ and SPECobject=\"%s\" """ % object_name

    print command
    c.execute(command)
