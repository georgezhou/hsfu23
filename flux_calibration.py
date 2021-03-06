### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import pyfits
import re
### Load functions script (located in the same folder)
import functions
from scipy import interpolate

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

def update_fitsheader(input_header,original_data,image):
    bad_header_names = "SIMPLE,BITPIX,NAXIS,NAXIS1,NAXIS2,BSCALE,BZERO"

    # print input_header
    # sys.exit()
    
    ### correct header
    #input_header = string.split(input_header,"\n")
    corrected_header = []
    for i in range(len(input_header)):
        #print input_header[i]
        if not input_header[i] == "":
            if not input_header[i][0] == " ":
                header_name = re.split(" |=",input_header[i])[0]
                try:
                    header_value = original_data[0].header[header_name]
                    if type(header_value) == str:
                        if len(header_value) > 0:
                            if header_value[0] == "+":
                                header_value = header_value[1:]

                    # else:
                    #     header_value = str(header_value)

                    if not (header_name in bad_header_names):
                        try:            
                            #print header_name,header_value,type(header_value)
                            iraf.hedit(
                                images = image,\
                                fields = header_name,\
                                add = 0,\
                                addonly = 0,\
                                delete = 1,\
                                verify = 0,\
                                show = 0,\
                                update = 0)

                            iraf.hedit(
                                images = image,\
                                fields = header_name,\
                                value = "dummy",\
                                add = 1,\
                                addonly = 0,\
                                delete = 0,\
                                verify = 0,\
                                show = 0,\
                                update = 1)

                            iraf.hedit(
                                images = image,\
                                fields = header_name,\
                                value = header_value,\
                                add = 1,\
                                addonly = 0,\
                                delete = 0,\
                                verify = 0,\
                                show = 0,\
                                update = 1)
                        except iraf.IrafError:
                            print "Hedit insert error",header_name,header_value,type(header_value)

                except KeyError:
                    pass

def divide_smooth(input_file):
    os.system("rm smoothdiv*_"+input_file)

    print wave_w1,wave_w2
    
    iraf.sarith(
        input1 = "spec_" + input_file,\
        op = "/",\
        input2 = "master_smooth.fits",\
        output = "smoothdivtemp_"+input_file,\
        w1 = wave_w1,\
        w2 = wave_w2,\
        apertures = "*",\
        bands = "",\
        beams = "",\
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
        low_reject = 30.0,\
        high_reject = 30.0,\
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
for i in range(len(SpecPhot_list)):
    SpecPhot_list[i] = "A_"+SpecPhot_list[i]

#################################################
### Divide object by black body star spectrum ###
#################################################
print "Dividing by black body smooth spectrum"
os.system("cp " + program_dir + "smooth_dir/" + grating + "_" + dichroic +"_smooth.fits ./master_smooth.fits")

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

### Apply high/low rejection again to remove cosmic rays
os.system("rm temp.fits")
iraf.continuum(
    input = "fluxcal_"+ file_name,\
    output = "temp.fits",\
    ask = "no",\
    lines = "*",\
    bands = "*",\
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
    order = 15,\
    low_reject = 30.0,\
    high_reject = 30.0,\
    niterate = 10,\
    grow = 1.0)

os.system("rm fluxcal_" + file_name)
os.system("mv temp.fits fluxcal_" + file_name)

### Move spectrum to reduced/
#os.system("rm " + file_path_reduced + "spec_" + file_name)
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

