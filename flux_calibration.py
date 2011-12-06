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
iraf.onedspec()

###################
### Description ###
###################

### Applies flux correction to object spectrum
### Requires reduced spectra of flux standard stars

### Usage: python flux_calibration.py file_path file_name
### flux_standards_ascii_list
        
#################
### Functions ###
#################

def divide_smooth(input_file):
    os.system("rm smoothdiv*_"+input_file)

    iraf.sarith(
        input1 = "spec_" + input_file,\
        op = "/",\
        input2 = "master_smooth.fits",\
        output = "smoothdivtemp_"+input_file,\
        w1 = wave_w1,\
        w2 = wave_w2,\
        apertures = 1,\
        bands = 1,\
        beams = 1,\
        apmodulus = 0,\
        reverse = 0,\
        ignoreaps = 1,\
        format = "multispec",\
        renumber = 1,\
        offset = 0,\
        clobber = 1,\
        merge = 0,\
        rebin = 1,\
        errval = 0.0,\
        verbose = 1)

    ### Apply continuum to remove artifacts from the division
    iraf.continuum(
        input = "smoothdivtemp_" + input_file,\
        output = "smoothdiv_" + input_file,\
        ask = "no",\
        lines = "*",\
        bands = "1",\
        type = "data",\
        replace = 1,\
        wavescale = 1,\
        logscale = 0,\
        override = 1,\
        listonly = 0,\
        logfiles = "logfile",\
        interactive = 0,\
        sample = "*",\
        naverage = 1,\
        function = "spline3",\
        order = 10,\
        low_reject = 15.0,\
        high_reject = 4.0,\
        niterate = 1,\
        grow = 5.0)

########################
### Start of program ###
########################

file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

### read in param files
camera = functions.read_config_file("CAMERA")
grating = functions.read_config_file("GRATING")
dichroic = functions.read_config_file("DICHROIC")
wave_w1 = functions.read_param_file(grating+"_"+dichroic+"_w1")
wave_w2 = functions.read_param_file(grating+"_"+dichroic+"_w2")

print "This script applies flux calibration to " +file_name

program_dir = os.getcwd() + "/" #Save the current working directory
os.chdir(file_path_temp) #Change to ../temp/

### read in all flux standard exposures
SpecPhot_list = functions.read_ascii(file_path_temp + "SpecPhot_list")

#################################################
### Divide object by black body star spectrum ###
#################################################
print "Dividing by black body smooth spectrum"
os.system("cp " + program_dir + "smooth_dir/master_smooth.fits .")

divide_smooth(file_name)
for specphot in SpecPhot_list:
    specphot_name = specphot + ".fits"
    divide_smooth(specphot_name)

##############################
### Apply flux calibration ###
##############################

### Check new_data_test to see if we need to create new sensfunc
new_data_test = open("new_data_test").read()
new_data_test = string.split(new_data_test,"\n")[0]
if new_data_test == "True":

    ### Setup kpnoslit
    iraf.kpnoslit(
        extinction = program_dir + "flux_data/extinsso.tab",\
        caldir = program_dir + "flux_data/",\
        observatory = "SSO",\
        interp = "poly5",\
        dispaxis = 2,\
        nsum = "1",\
        database = "database",\
        verbose = 1,\
        logfile = "logfile")

    ### Run iraf.standard
    os.system("rm std")
    for i in range(len(SpecPhot_list)):
        flux_name = "smoothdiv_"+SpecPhot_list[i] + ".fits"
        hdulist = pyfits.open(flux_name)
        name = hdulist[0].header['OBJECT']
        air_mass = hdulist[0].header['AIRMASS']
        exposure_time = hdulist[0].header['EXPTIME']

        iraf.standard(
            input = flux_name,\
            output = "std",\
            star_name = name,\
            airmass = air_mass,\
            exptime = exposure_time,\
            mag = "",\
            magband = "V",\
            teff = "",\
            answer = "yes",\
            samestar = 1,\
            beam_switch = 0,\
            apertures = "",\
            bandwidth = "INDEF",\
            bandsep = "INDEF",\
            fnuzero = "3.68e-20",\
            extinction = program_dir + "flux_data/extinsso.tab",\
            caldir = program_dir + "flux_data/",\
            observatory = "SSO",\
            interact = 0,\
            graphics = "stdgraph",\
            cursor = "",\
            mode = "al")

    ### Apply sensfunc
    os.system("rm sens*.fits")
    iraf.sensfunc(
        standards = "std",\
        sensitivity = "sens",\
        answer = "yes",\
        apertures = "",\
        ignoreaps = 1,\
        logfile = "logfile",\
        extinction = program_dir + "flux_data/extinsso.tab",\
        newextinctio = "extinct.dat",\
        observatory = "SSO",\
        function = "spline3",\
        order = 15,\
        interactive = 1,\
        graphs = "sr",\
        marks = "plus cross box",\
        colors = "2 1 3 4",\
        cursor = "",\
        device = "stdgraph",\
        mode = "al")

### Apply calibration to file_name
hdulist = pyfits.open("smoothdiv_" + file_name)
air_mass = hdulist[0].header['AIRMASS']
exposure_time = hdulist[0].header['EXPTIME']

os.system("rm fluxcal_" + file_name )

iraf.calibrate(
    input = "smoothdiv_" + file_name,\
    output = "fluxcal_" + file_name,\
    airmass = air_mass,\
    exptime = exposure_time,\
    extinct = 1,\
    flux = 1,\
    extinction = program_dir + "flux_data/extinsso.tab",\
    observatory = "SSO",\
    ignoreaps = 1,\
    sensitivity = "sens",\
    fnu = 0,\
    mode = "al")

os.system("rm " + file_path_reduced + "spec_" + file_name)
os.system("cp -f " + "fluxcal_" + file_name + " " + file_path_reduced)

########################
### Create .dat file ###
########################

### This file will later be read in for spectral matching

os.chdir(file_path_reduced)
os.system("rm fluxcal_" + file_name + ".dat")
iraf.wspectext("fluxcal_" + file_name+"[*,1,1]", "fluxcal_" + file_name + ".dat")

### rewrite it in the form #wavelength flux
spectrum = functions.read_ascii("fluxcal_" + file_name + ".dat")
spectrum = functions.read_table(spectrum)
temp = []
for i in spectrum:
    if len(i) == 2:
        if functions.is_number(i[0]):
            temp.append(i)
spectrum = temp
spectrum = spectrum[1:len(spectrum)-2]

output_spectrum = open("fluxcal_" + file_name + ".dat","w")
functions.write_table(spectrum,output_spectrum)
output_spectrum.close()

