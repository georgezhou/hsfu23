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

### The script will also automatically identify the NeAr_arc file needed. It
### will search within the file_path folder for the arc file taken nearest in
### JD to the object exposure.

### Usage: python find_arc.py file_path file_name

########################
### Start of program ###
########################

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

os.chdir(file_path)

#######################################################################
### Find the Ne Ar arc lamp exposure closest to the object exposure ###
#######################################################################

### Find object JD
hdulist = pyfits.open(file_name)
object_MJD = hdulist[0].header['MJD-OBS'] 
hdulist.close()

### Compile list of NeAr arcs
object_list = functions.ccdlist_extract(iraf.ccdlist("*.fits",Stdout = 1))
NeAr_match = functions.ccdlist_identify(object_list,"Ne-Ar")

### Open each fine and find its MJD
arc_MJD = []
for i in range(len(NeAr_match)):
    hdulist = pyfits.open(object_list[NeAr_match[i]][0])
    arc_MJD.append([abs(hdulist[0].header['MJD-OBS'] - object_MJD),object_list[NeAr_match[i]][0]])
    hdulist.close()

### Sort arc_MJD according to closest time to object exposure
arc_MJD = functions.sort_array(arc_MJD,0)

### Choose 2 arc images if the 2nd arc frame was taken <30min from object
if len(arc_MJD) > 1:
    if arc_MJD[1][0] < 0.02:
        arc_names = arc_MJD[0][1] + "\n" + arc_MJD[1][1] + "\n"
    else:
        arc_names = arc_MJD[0][1] + "\n"
else:
    arc_names = arc_MJD[0][1] + "\n"

print "Using arc frames:"
print arc_names

arc_file = open(file_path_temp + "arcs_to_use.txt","w")
arc_file.write(arc_names)
