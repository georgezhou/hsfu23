### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os

### Load functions script (located in the same folder)
import functions

### Load iraf moduels
iraf.noao()
iraf.imred()
iraf.imred.ccdred()
iraf.imred.kpnoslit()

###################
### Description ###
###################
### Combine the individual spectra from each image slice into a 
### combined spectrum.

### The config file option COMBINE_APERTURES defines how the data gets
### combined.

### In the case of RV measurements, this is a multispec object
### where each image slice is stored in a separate aperture.

### In the case spectral typing, the spectra should be average combined
### into a single spectrum, to boost S/N.

### Usage: python combine_apertures.py file_path file_name

########################
### Start of program ###
########################

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

image_slices = functions.read_ascii(file_path_temp + "stellar_apertures.txt")

camera = functions.read_config_file("CAMERA")
grating = functions.read_config_file("GRATING")
dichroic = functions.read_config_file("DICHROIC")

spectrum_w1 = functions.read_param_file(grating+"_"+dichroic+"_w1")
spectrum_w2 = functions.read_param_file(grating+"_"+dichroic+"_w2")

sample_w1 = functions.read_param_file("FLUX_NORMALISE_w1")
sample_w2 = functions.read_param_file("FLUX_NORMALISE_w2")
sample_region = "a"+sample_w1+"-"+sample_w2

combine_apertures = functions.read_config_file("COMBINE_APERTURES")

program_dir = os.getcwd() + "/" #Save the current working directory
os.chdir(file_path_temp) #Change to ../temp/ dir

print "Combining spectra from multiple image slices into a single spectral object"

#####################################################################
### Check if the required spectra exists, and create combine list ###
#####################################################################

combine_list_norm = ""
combine_list_flux = ""

for im_slice in image_slices:
    image_name = im_slice + "_" + file_name
    if os.path.exists("norm_" + image_name):
        combine_list_norm = combine_list_norm + "norm_" +image_name + ","

        iraf.scopy(
            input = "norm_" + image_name,\
            output = "norm_" + image_name,\
            w1 = spectrum_w1,\
            w2 = spectrum_w2,\
            apertures = "",\
            bands = "",\
            beams = "",\
            apmodulus = 0,\
            format = "multispec",\
            renumber = 0,\
            offset = 0,\
            clobber = 1,\
            merge = 0,\
            rebin= 1,\
            verbose = 1)

    if os.path.exists("cray_" + image_name):
        combine_list_flux = combine_list_flux + "cray_" +image_name + ","   
        iraf.scopy(
            input = "cray_" + image_name,\
            output = "cray_" + image_name,\
            w1 = spectrum_w1,\
            w2 = spectrum_w2,\
            apertures = "",\
            bands = "",\
            beams = "",\
            apmodulus = 0,\
            format = "multispec",\
            renumber = 0,\
            offset = 0,\
            clobber = 1,\
            merge = 0,\
            rebin= 1,\
            verbose = 1)

os.system("rm normspec_" + file_name)
os.system("rm spec_" + file_name)

###############
### RV case ###
###############
### use scopy to combine the spectra into 
### a multispec object, preserving the image slices

if combine_apertures == "false":

    iraf.scopy(
        input = combine_list_norm,\
        output = "normspec_" + file_name,\
        w1 = spectrum_w1,\
        w2 = spectrum_w2,\
        apertures = "*",\
        bands = "",\
        beams = "",\
        apmodulus = 0,\
        format = "multispec",\
        renumber = 1,\
        offset = 0,\
        clobber = 1,\
        merge = 0,\
        rebin = 0,\
        verbose = 1)

    iraf.scopy(
        input = combine_list_flux,\
        output = "spec_" + file_name,\
        w1 = spectrum_w1,\
        w2 = spectrum_w2,\
        apertures = "*",\
        bands = "",\
        beams = "",\
        apmodulus = 0,\
        format = "multispec",\
        renumber = 1,\
        offset = 0,\
        clobber = 1,\
        merge = 0,\
        rebin = 0,\
        verbose = 1)

###############################
### SPECTYPE and NONE cases ###
###############################
### Use scombine to sum the spectra from multiple apertures.
### Sum is better than average as it preserve the flux ratio
### from each aperture, kind of like weighted average.

if combine_apertures == "true":

    iraf.scombine(
        input = combine_list_flux,\
        output = "spec_" + file_name,\
        noutput = "",\
        logfile = "STDOUT",\
        apertures = "*",\
        group = "all",\
        combine = "average",\
        reject = "minmax",\
        first = 1,\
        w1 = spectrum_w1,\
        w2 = spectrum_w2,\
        dw = "INDEF",\
        nw = "INDEF",\
        log = 0,\
        scale = "median",\
        zero = "none",\
        weight = "median",\
        sample = sample_region,\
        nlow = 1,\
        nhigh = 1,\
        nkeep = 1,\
        mclip = 1,\
        lsigma = 2.0,\
        hsigma = 2.0,\
        rdnoise = 0,\
        gain = 1,\
        snoise = 0,\
        sigscale = 0.1,\
        pclip = -0.5,\
        grow = 0,\
        blank = 0.0,\
        mode = "al")

    iraf.scopy(
        input = "spec_" + file_name,\
        output = "spec_" + file_name,\
        w1 = spectrum_w1,\
        w2 = spectrum_w2,\
        apertures = "*",\
        bands = "",\
        beams = "",\
        apmodulus = "0",\
        format = "multispec",\
        renumber = 0,\
        offset = 0,\
        clobber = 1,\
        merge = 0,\
        rebin = 0,\
        verbose = 1)

    ### Then normalise this spectrum (rather than combining the normalised 
    ### spectra from each aperture... easier!)

    iraf.continuum(
        input = "spec_" + file_name,\
        output = "normspec_" + file_name,\
        type = "ratio",\
        replace = 0,\
        wavescale = 1,\
        logscale = 0,\
        override = 1,\
        listonly = 0,\
        logfiles = "logfile",\
        interactive = 0,\
        function  = "spline3",\
        order = 15,\
        low_reject = 5.0,\
        high_reject = 0.0,\
        niterate = 2,\
        grow = 1,\
        ask = "no",)
