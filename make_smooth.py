### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import os.path

### Load functions script (located in the same folder)
import functions

### Load iraf moduels
iraf.imred()
iraf.imred.ccdred()
iraf.imred.kpnoslit()

###################
### Description ###
###################

### User specifies a list of smooth star exposures
### This program reduces the individual exposures
### And combines them into master smooth

### The final spectrum is normalised to between 0 and 1
### And is used in divide_smooth.py

### Usage: python make_smooth.py

#################
### Functions ###
#################

def reduce_image(file_path,file_name,file_path_reduced,smooth_files_list,count):
    os.system("./reduce_image.csh " + file_path + " " + file_name)
    os.system("cp " + file_path_reduced + "spec_" + file_name+" smooth_dir/smooth_" + str(count) + ".fits")
    smooth_files_list.append("smooth_" + str(count) + ".fits")
    count = count + 1
    return smooth_files_list,count

def make_string_from_list(input_list):
    string_output = ""
    for i in range(len(input_list)):
        string_output = string_output + input_list[i] + ","
    return string_output

########################
### Start of program ###
########################

file_path = "/mimsy/george/wifes/"
folders_to_search = ["17Sep2011/spectype/blue/","18Sep2011/spectype/blue/"]

program_dir = os.getcwd() + "/" #Save the current working directory

### Remove existing files in the "smooth" directory
os.system("rm -rf smooth_dir")
os.system("rm *smooth.fits")

### Create a folder of smooth images in program dir
os.system("mkdir smooth_dir")

### Go through the folders, identify and reduce each smooth image
smooth_files_list = []

stars_to_try = ["ltt4364","eg131"]

for star in stars_to_try:
    count = 1

    for i in range(len(folders_to_search)):
        file_path_current = file_path + folders_to_search[i]

        ### Find any smooth star exposures
        ccdlist_info = iraf.ccdlist(file_path_current + "*.fits", Stdout = 1)
        ccdlist_info = functions.ccdlist_extract(ccdlist_info)
        ccdlist_match = functions.ccdlist_identify(ccdlist_info,star)

        ### Reduce any such exposures
        if len(ccdlist_match) > 0:
            for j in range(len(ccdlist_match)):
                file_name = ccdlist_info[ccdlist_match[j]][2] + ".fits"
                file_path_temp = file_path_current + "temp/"
                file_path_reduced = file_path_current + "reduced/"
                print "currently reducing image " + file_path_current + file_name

                smooth_files_list,count = reduce_image(file_path_current,file_name,file_path_reduced,smooth_files_list,count)

    ### If exposures were found for starX, then break the for loop
    if count > 1:
        break

### Add each smooth image
smooth_files_list = make_string_from_list(smooth_files_list)
os.chdir("smooth_dir") #Change to smooth_dir

os.system("rm master_smooth.fits")
os.system("rm temp_master_smooth.fits")

iraf.imcombine(
    input = smooth_files_list,\
    output = "master_smooth.fits",\
    combine = "sum",\
    mode = "ql")

### Normalise the smooth spectrum
smooth_min = iraf.imstat(
    images = "master_smooth.fits[*,1,1]",\
    fields = "min",\
    lower = "INDEF",\
    upper = "INDEF",\
    nclip = 1,\
    lsigma = 5.0,\
    usigma = 5.0,\
    binwidth = 0.1,\
    format = 1,\
    cache = 1,\
    mode = "al",\
    Stdout = 1)

iraf.imarith(
    operand1 = "master_smooth.fits",\
    op = "-",\
    operand2 = str(float(smooth_min[1])),\
    result = "temp_master_smooth.fits",\
    title = "",\
    divzero = 0.,\
    hparams = "",\
    pixtype = "",\
    calctype = "",\
    verbose = 1,\
    noact = 0,\
    mode = "ql")    

os.system("rm " + "master_smooth.fits")
os.system("mv " + "temp_master_smooth.fits master_smooth.fits")

smooth_max = iraf.imstat(
    images = "master_smooth.fits[*,1,1]",\
    fields = "max",\
    lower = "INDEF",\
    upper = "INDEF",\
    nclip = 1,\
    lsigma = 5.0,\
    usigma = 5.0,\
    binwidth = 0.1,\
    format = 1,\
    cache = 1,\
    mode = "al",\
    Stdout = 1)

iraf.imarith(
    operand1 = "master_smooth.fits",\
    op = "/",\
    operand2 = str(float(smooth_max[1])),\
    result = "temp_master_smooth.fits",\
    title = "",\
    divzero = 0.,\
    hparams = "",\
    pixtype = "",\
    calctype = "",\
    verbose = 1,\
    noact = 0,\
    mode = "ql")    

os.system("rm " + "master_smooth.fits")
os.system("mv " + "temp_master_smooth.fits master_smooth.fits")

### Apply continuum 
os.system("rm continuum_fit.fits")

iraf.hedit(images="master_smooth",fields = "SFIT",value="",add=0,delete=1,verify=0, show=1, update=1)

iraf.continuum(
    input = "master_smooth.fits",\
    output = "continuum_fit.fits",\
    lines = 1,\
    bands = 1,\
    type = "fit",\
    replace = 0,\
    wavescale = 1,\
    logscale = 0,\
    override = 0,\
    listonly = 0,\
    logfiles = "logfile",\
    interactive = 0,\
    function  = "spline3",\
    order = 15,\
    low_reject = 2.0,\
    high_reject = 2.0,\
    niterate = 5,\
    grow = 1,\
    ask = "no",)

os.system("mv continuum_fit.fits master_smooth.fits")
