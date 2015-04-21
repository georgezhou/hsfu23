### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import pyfits


### Load iraf moduels
iraf.imred()
iraf.imred.ccdred()
iraf.imred.kpnoslit()
iraf.astutil()

###################
### Description ###
###################

### Runs setairmass on the original files

### python setairmass.py file_path file_name

########################
### Start of program ###
########################

### Set file_path
file_path = sys.argv[1]

file_name = sys.argv[2]
### Run setairmass to make sure the airmass parameter is correct
iraf.hedit(
    images = file_path + file_name,\
    fields = "EPOCH",\
    value = 2000,\
    add = 1,\
    addonly = 0,\
    delete = 0,\
    verify = 0,\
    show = 1,\
    update = 1)

iraf.setairmass(
    images = file_path + file_name,\
    observatory = "SSO",\
    intype = "beginning",\
    outtype = "effective",\
    ra = "RA",\
    dec = "DEC",\
    equinox = "EPOCH",\
    st = "LST-OBS",\
    ut = "UTC-OBS",\
    date = "DATE-OBS",\
    exposure = "EXPTIME",\
    airmass = "AIRMASS",\
    utmiddle = "UTCMID",\
    scale = 750.0,\
    show = 1,\
    update = 1,\
    override = 1)
