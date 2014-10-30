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
    os.system("rm -rf " + file_path_reduced + "*")
    os.system("rm -rf " + file_path + "temp/*")
    os.system("./reduce_image.csh " + file_path + " " + file_name)
    os.system("cp " + file_path_reduced + "spec_A_" + file_name+" smooth_dir/smooth_" + str(count) + ".fits")
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

file_path = "/priv/mulga2/george/wifes/"
folders_to_search = ["02Jun2014/spectype/blue/"]

grating = functions.read_config_file("GRATING")
dichroic = functions.read_config_file("DICHROIC")
wave1 = functions.read_param_file(grating+"_"+dichroic+"_w1")
wave2 = functions.read_param_file(grating+"_"+dichroic+"_w2")

program_dir = os.getcwd() + "/" #Save the current working directory

### Remove existing files in the "smooth" directory
#os.system("rm -rf smooth_dir")
os.system("rm *smooth.fits")

### Create a folder of smooth images in program dir
os.system("mkdir smooth_dir")
os.system("rm smooth_dir/master_smooth.fits")
os.system("rm smooth_dir/smooth_*.fits")

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

# iraf.imcombine(
#     input = smooth_files_list,\
#     output = "master_smooth.fits",\
#     combine = "sum",\
#     reject = "none",\
#     mode = "ql")

print smooth_files_list
iraf.scombine(
    input = smooth_files_list,\
    output = "master_smooth.fits",\
    apertures = "",\
    group = "all",\
    combine = "average",\
    reject = "none",\
    first = 1,\
    w1 = wave1,\
    w2 = wave2,\
    dw = "INDEF",\
    nw = "INDEF",\
    log = 0,\
    scale = "median",\
    zero = "none",\
    weight = "median",\
    sample = "",\
    lthreshold="INDEF",\
    hthreshold="INDEF",\
    nlow = 1,\
    nhigh = 1,\
    nkeep = 1,\
    mclip = 0,\
    lsigma = 0,\
    hsigma = 0,\
    rdnoise = 0,\
    gain = 1,\
    snoise = 0,\
    pclip = -0.5)

iraf.scopy(
    input = "master_smooth.fits",\
    output = "master_smooth.fits",\
    w1 = wave1,\
    w2 = wave2,\
    apertures = "",\
    bands = "",\
    beams = "",\
    apmodulus = 0,\
    format = "multispec",\
    renumber = 0,\
    clobber = 1,\
    merge = 0,\
    rebin = 1,\
    verbose = 1)


# ### Normalise the smooth spectrum
# smooth_min = iraf.imstat(
#     images = "master_smooth.fits[*,1,1]",\
#     fields = "min",\
#     lower = "INDEF",\
#     upper = "INDEF",\
#     nclip = 1,\
#     lsigma = 5.0,\
#     usigma = 5.0,\
#     binwidth = 0.1,\
#     format = 1,\
#     cache = 1,\
#     mode = "al",\
#     Stdout = 1)

# iraf.imarith(
#     operand1 = "master_smooth.fits",\
#     op = "-",\
#     operand2 = smooth_min[1],\
#     result = "temp_master_smooth.fits",\
#     title = "",\
#     divzero = 0.,\
#     hparams = "",\
#     pixtype = "",\
#     calctype = "",\
#     verbose = 1,\
#     noact = 0,\
#     mode = "ql")    

# os.system("rm " + "master_smooth.fits")
# os.system("mv " + "temp_master_smooth.fits master_smooth.fits")

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
    operand2 = smooth_max[1],\
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
    lines = "*",\
    bands = "*",\
    type = "fit",\
    replace = 0,\
    wavescale = 1,\
    logscale = 0,\
    override = 1,\
    listonly = 0,\
    logfiles = "logfile",\
    interactive = 1,\
    function  = "spline3",\
    order = 100,\
    low_reject = 5.0,\
    high_reject = 5.0,\
    niterate = 5,\
    grow = 1,\
    ask = "yes",)

os.system("mv continuum_fit.fits " + grating + "_" + dichroic + "_smooth.fits")
