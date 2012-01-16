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
iraf.noao()
iraf.imred()
iraf.imred.ccdred()
iraf.imred.kpnoslit()
iraf.noao.rv()
iraf.astutil()

###################
### Description ###
###################

### For accurate RV measurements, the telluric lines can be another 
### way to calibrate our stellar spectrum. The telluric lines are stable
### to 10m/s over a long period, so they can provide a first order 
### shift calibration that can be applied to the spectrum.

### We cross correlate the Oxygen telluric lines against an UVES spectrum
### of the same region, and apply the shift correction.

### HOWEVER, since the telluric lines are not in the same region as the 
### stellar lines used for RV CC, this helps but does not correct everything.

### usage: telluric_correction.py file_path file_name

#################
### Functions ###
#################

def run_fxcor(input_file,input_rv,lines,output,fitshead_update):
    iraf.fxcor(
        objects = input_file, \
        templates = input_rv, \
        apertures = "*", \
        cursor = "",\
        continuum = "both",\
        filter = "both",\
        rebin = "smallest",\
        pixcorr = 0,\
        osample = lines,\
        rsample = lines,\
        apodize = 0.2,\
        function = "gaussian",\
        width = 10.0,\
        height= 0.,\
        peak = 0,\
        minwidth = 15.0,\
        maxwidth = 15.0,\
        weights = 1.,\
        background = "INDEF",\
        window = "INDEF",\
        wincenter = "INDEF",\
        output = output,\
        verbose = "long",\
        imupdate = fitshead_update,\
        graphics = "stdgraph",\
        interactive = 0,\
        autowrite = 1,\
        ccftype = "image",\
        observatory = "sso",\
        continpars = "",\
        filtpars = "",\
        keywpars = "")

########################
### Start of program ###
########################

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

hdulist = pyfits.open(file_path + file_name)
object_mjd = hdulist[0].header['MJD-OBS']
hdulist.close()

camera = functions.read_config_file("CAMERA")
grating = functions.read_config_file("GRATING")
dichroic = functions.read_config_file("DICHROIC")

telluric_region = functions.read_param_file("TELLURIC_REGION")

### Copy telluric line spectra to working directory
telluric_fits = grating + "_telluric.fits"
os.system("cp -f telluric_fits/" + telluric_fits + " " + file_path_temp+"telluric.fits")

### Get slice numbers
image_slices = functions.read_ascii(file_path_temp + "stellar_apertures.txt")

### We want to change directory to ../temp/
### This is because of some stupid way autoidentify names database files
program_dir = os.getcwd() + "/" #Save the current working directory
os.chdir(file_path_temp) #Change to ../temp/ dir

##################
### Find shift ###
##################

for im_slice in image_slices:
    print "CC with telluric for wavelength calibration"
    os.system("rm apshift*")

    ### Makesure keywpars is set at default
    iraf.unlearn(iraf.keywpars)

    iraf.filtpars.setParam("f_type","square",check=1,exact=1)
    iraf.filtpars.setParam("cuton",50,check=1,exact=1)
    iraf.filtpars.setParam("cutoff",10000,check=1,exact=1)

    run_fxcor("norm_" + im_slice + "_" + file_name,"telluric.fits",telluric_region,"apshift",0)
    vel_shift = functions.read_ascii("apshift.txt")
    vel_shift = functions.read_table(vel_shift)
    vel_shift = str(vel_shift[0][11])
    print "Applying pixel shift of (km/s)"
    print vel_shift

    if vel_shift == "INDEF":
        vel_shift = 0.0

    ###################
    ### Apply shift ###
    ###################

    os.system("rm temp.fits")
    iraf.dopcor(
        input = "norm_" + im_slice + "_" + file_name,\
        output = "temp.fits",\
        redshift = vel_shift,\
        isvelocity = 1,\
        add = 1,\
        dispersion = 1,\
        flux = 0,\
        apertures = "*",\
        verbose = 1)

    os.system("rm norm_" + im_slice + "_" + file_name)
    os.system("mv temp.fits norm_" + im_slice + "_" + file_name)
