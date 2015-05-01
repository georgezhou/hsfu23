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
iraf.astutil()

###################
### Description ###
###################

### Finds the bias files from file_path
### Apply bias subtraction to image

### Usage: python bias_subtraction.py file_path file_name

#############################
### Read from config file ###
#############################

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

hdulist = pyfits.open(file_path + file_name)
object_name = hdulist[0].header["OBJNAME"]
camera = hdulist[0].header["CAMERA"].lower()
dichroic = hdulist[0].header["BEAMSPLT"]
if 'red' in camera:
    grating = hdulist[0].header["GRATINGR"]
    import image_type_red as image_types
else:
    grating = hdulist[0].header["GRATINGB"]
    import image_type_blue as image_types
hdulist.close()

print "This script applies bias subtraction to the image " + file_name

if "red" in camera:
    trimsec_value = functions.read_param_file("RED_TRIMSEC")
    biassec_value = functions.read_param_file("RED_BIASSEC")
    region1 = functions.read_param_file("RED_REGION1")
    region2 = functions.read_param_file("RED_REGION2")
    use_regions = functions.read_param_file("RED_USEREGIONS")
    reflect = functions.read_param_file("RED_REFLECT")

if "blue" in camera:
    trimsec_value = functions.read_param_file("BLUE_TRIMSEC")
    biassec_value = functions.read_param_file("BLUE_BIASSEC")
    region1 = functions.read_param_file("BLUE_REGION1")
    region2 = functions.read_param_file("BLUE_REGION2")
    use_regions = functions.read_param_file("BLUE_USEREGIONS")
    reflect = functions.read_param_file("BLUE_REFLECT")


print trimsec_value, biassec_value, region1, region2

########################
### Start of program ###
########################

### Make the required folders
print "Making directories temp and reduced"
os.system("mkdir " + file_path + "temp")
os.system("mkdir " + file_path + "reduced")

########################
### Form master bias ###
########################
### Find the bias images
os.system("rm " + file_path_temp + "master_bias.fits")

if len(image_types.bias_obs) == 0:
    print "!!!!!!! No Bias frames found, using default bias !!!!!!!"
    os.system("cp default_cal_frames/bias.fits " + file_path_temp + "master_bias.fits")
else:
    print "The bias files found are:"
    print image_types.bias_obs
    iraf.combine(
        input = ",".join(image_types.bias_obs),\
        output = file_path_temp + "master_bias.fits",\
        combine = "average",\
        reject = "sigclip",\
        project = 0,\
        outtype = "real",\
        offsets = "none",\
        masktype = "none",\
        maskvalue = 0,\
        blank = 0,\
        scale = "none",\
        zero = "none",\
        weight = "none",\
        statsec = "",\
        lthreshold = "INDEF",\
        hthreshold = "INDEF",\
        nlow = 1,\
        nhigh = 1,\
        mclip = 1,\
        nkeep = 1,\
        lsigma = 3,\
        hsigma = 3,\
        rdnoise = 0.,\
        mode = "ql")


########################
### Form master flat ###
########################

if functions.read_config_file("DIVIDE_FLAT") == "true" and (not object_name == "Ne-Ar"):
    ### Find the flat images
    os.system("rm " + file_path_temp + "master_flat.fits")
    flatcor_option = 1
    flat_option = file_path_temp + "master_flat.fits"
    if len(image_types.domeflat_obs)==0:
        print "!!!!!! No flat frames found, using default flat !!!!!!!!"
        os.system("cp default_cal_frames/" + grating + "_" + dichroic +"_flat.fits " + file_path_temp + "master_flat.fits")
    else:
        print "The flat files found are:"
        print image_types.domeflat_obs
        iraf.combine(
            input = ",".join(image_types.domeflat_obs),\
            output = file_path_temp + "master_flat.fits",\
            combine = "average",\
            reject = "sigclip",\
            project = 0,\
            outtype = "real",\
            offsets = "none",\
            masktype = "none",\
            maskvalue = 0,\
            blank = 0,\
            scale = "none",\
            zero = "none",\
            weight = "none",\
            statsec = "",\
            lthreshold = "INDEF",\
            hthreshold = "INDEF",\
            nlow = 1,\
            nhigh = 1,\
            mclip = 1,\
            nkeep = 1,\
            lsigma = 3,\
            hsigma = 3,\
            rdnoise = 0.,\
            mode = "ql")
else:
    flatcor_option = 0
    flat_option = ""

##################################
### Sort out the image headers ###
##################################

### Copy the files we are operating on into temp
print "Copying required files into temp/"
os.system("cp -f " + file_path + file_name + " " + file_path_temp + file_name)

### Do this by using specphot
print "Updating settings on specphot"
iraf.setinstrument(instrument="specphot",site="kpno",directory="ccddb$",query="specphot",review=0)



### Remove image header information on image sections
### These may be wrong, since wifes data formats keep on changing
### They are also only valid for 1x bin
### Better to check these manually at the start of an observing run!

images_to_edit = file_path_temp+"master_bias.fits,"
if functions.read_config_file("DIVIDE_FLAT") == "true":
    images_to_edit = images_to_edit + file_path_temp + "master_flat.fits,"
images_to_edit = images_to_edit + file_path_temp + file_name

iraf.hedit(images=images_to_edit,fields = "CCDSEC",value="",delete=1, verify=0, show=1, update=1)
iraf.hedit(images=images_to_edit,fields = "BIASSEC",value="",delete=1, verify=0, show=1, update=1)
iraf.hedit(images=images_to_edit,fields = "DATASEC",value="",delete=1, verify=0, show=1, update=1)
iraf.hedit(images=images_to_edit,fields = "TRIMSEC",value="",delete=1, verify=0, show=1, update=1)

#############################################################
### Apply bias subtraction and flat division with ccdproc ###
#############################################################

### Delete any old file
os.system("rm -f " + file_path_temp + "ccdproc_" + file_name)

print "Using ccdproc to apply bias subtraction and trimming"

iraf.ccdproc(
    images = file_path_temp + file_name,\
    output = file_path_temp + "ccdproc_" + file_name, \
    noproc = 0, \
    fixpix = 0, \
    overscan = 1,\
    trim = 1, \
    zerocor = 1,\
    darkcor = 0,\
    flatcor = flatcor_option,\
    illumcor = 0,\
    fringecor = 0,\
    readcor = 0,\
    scancor = 0,\
    readaxis = "line",\
    fixfile = "",\
    biassec = biassec_value,\
    trimsec = trimsec_value,\
    dark = "",\
    zero = file_path_temp + "master_bias.fits",\
    flat = flat_option,\
    illum = "",\
    fringe = "",\
    minreplace = 1.0,\
    scantype = "shortscan",\
    nscan = 1,\
    interactive = 0,\
    function = "chebyshev",\
    order = 1,\
    sample = "*",\
    naverage = 1,\
    niterate = 1,\
    low_reject = 3.0,\
    high_reject = 3.0,\
    grow = 1.0)

if reflect == "true":
   iraf.imcopy(
        input = file_path_temp+"ccdproc_"+file_name+"[-*,*]",\
        output = file_path_temp+"ccdproc_"+file_name)


if use_regions == "true":

    ### The ccd has an overscan and a blank in the middle. 
    ### So we need to cut the two useful regions out, then join them together

    print "Splitting the image into two regions to remove the central blank strip"

    ### Delete any previous files
    os.system("rm -f " + file_path_temp + "*_" + "ccdproc_" + file_name)

    ### Extract region 1
    iraf.imcopy(
        input = file_path_temp + "ccdproc_" + file_name+ region1, \
        output = file_path_temp + "1_" + "ccdproc_" + file_name)

    ### Extract region 2
    iraf.imcopy(
        input = file_path_temp + "ccdproc_" + file_name+ region2, \
        output = file_path_temp + "2_" + "ccdproc_" + file_name)

    ### Join region 1 and 2 together
    iraf.imjoin(
        input = file_path_temp + "1_" + "ccdproc_"+file_name + "," + file_path_temp + "2_" + "ccdproc_"+file_name ,\
        output = file_path_temp + "out_" + "ccdproc_" + file_name,\
        join_dimension = 1)

    print "Image joined together"
    print "Reduced image: " + file_path_temp + "out_ccdproc_" + file_name

else:
    os.system("mv "+file_path_temp + "ccdproc_" + file_name+" "+file_path_temp + "out_ccdproc_" + file_name)
