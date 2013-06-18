import sys
import os
import string
from numpy import *
import functions
import pyfits
from pyraf import iraf

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

### Normalise the object spectrum
### Prepare for use in spectraltyping later

### Usage: python normalise_for_spectype.py file_path file_name

########################
### Start of program ###
########################

file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

### Read in param_files settings
norm_w1 = functions.read_param_file("NORM_REGION_w1")
norm_w2 = functions.read_param_file("NORM_REGION_w2")

program_dir = os.getcwd() + "/" #Save the current working directory

### Change directory to reduced/
os.chdir(file_path_temp) #Change to ../reduced/ dir

###########################
### Operate on spectrum ###
###########################

### Chop out section norm_w1 - norm_w2 (according to param_file)
### This avoids the balmer jump and all the Ca lines
### Which are hard to normalise

os.system("rm trim_" + file_name)

iraf.scopy(
    input = "fluxcal_" + file_name,\
    output = "trim_" + file_name,\
    w1 = norm_w1,\
    w2 = norm_w2,\
    apertures = "*",\
    bands = "",\
    beams = "",\
    apmodulus = 0,\
    format = "multispec",\
    renumber = 0,\
    offset = 0,\
    clobber = 1,\
    merge = 0,\
    rebin = 1,\
    verbose = 1)

### Apply continuum to normalise
os.system("rm norm_" + file_name)

iraf.continuum(
    input = "trim_" + file_name,\
    output = "norm_" + file_name,\
    lines = "*",\
    bands = "1",\
    type = "ratio",\
    replace = 0,\
    wavescale = 1,\
    logscale = 0,\
    override = 1,\
    listonly = 0,\
    logfiles = "logfile",\
    interactive = 0,\
    sample = "*",\
    naverage = 1,\
    function = "spline3",\
    order = 3,\
    low_reject = 1.5,\
    high_reject = 4.0,\
    niterate = 10,\
    markrej = 1,\
    graphics = "stdgraph",\
    cursor = "",\
    ask = "no",\
    mode = "ql")

#######################
### Convert to .dat ###
#######################

os.system("rm norm_" + file_name + ".dat")

iraf.wspectext("norm_" + file_name +"[*,1,1]", "norm_" + file_name + ".dat")

spectrum = functions.read_ascii("norm_" + file_name + ".dat")
spectrum = functions.read_table(spectrum)
temp = []
for i in spectrum:
    if len(i) == 2:
        if functions.is_number(i[0]):
            temp.append(i)
spectrum = temp
spectrum = spectrum[1:len(spectrum)-2]

output_spectrum = open("norm_" + file_name + ".dat","w")
functions.write_table(spectrum,output_spectrum)
output_spectrum.close()

os.system("cp norm_" + file_name + "* " + file_path_reduced)
