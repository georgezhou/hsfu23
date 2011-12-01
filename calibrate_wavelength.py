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

### The stellar spectrum needs to be extracted and wavelength calibrated.
### Extraction is automatically performed on the brightest star 
### unless interact is turned on.

### The arc spectrum is extracted along the same aperture as the 
### stellar spectrum.

### If all went well, the distortion corrected fits image already
### has a wavelength solution. We use the arc spectra to check 
### this wavelength calibration. We also perform cosmic ray removal
### and normalisation.

### Usage: calibrate_wavelength.py file_path file_name

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

print "This script applies NeAr arc image to calibrate the object spectrum " +file_name

### Get slice numbers and arc images to use
arc_list = functions.read_ascii(file_path_temp + "arcs_to_use.txt")
image_slices = functions.read_ascii(file_path_temp + "stellar_apertures.txt")

### Calculate the fractional weight of each arc 
arc_weight = []
for arc_name in arc_list:
    hdulist = pyfits.open(file_path + arc_name)
    arc_mjd = hdulist[0].header['MJD-OBS']
    hdulist.close()

    arc_weight.append(abs(arc_mjd - object_mjd))

arc_weight = array(arc_weight)
arc_weight = arc_weight / sum(arc_weight)

### Define linelist to use
linelist = grating + "_linelist.dat"

### Define template to use
template = "calibrated_" + grating +"_"+dichroic+ "_template.fits"

###################################
### Perform spectral extraction ###
###################################

program_dir = os.getcwd() + "/" #Save the current working directory
os.chdir(file_path_temp) #Change to ../temp/ dir

print "Using apall to extract the spectrum about the central line in the object image"
os.system("rm -f " + file_path_temp + "*" + string.split(file_name,".")[0] + "*ms*")

os.system("rm database/*" + string.split(file_name,".")[0] + "*")
os.system("rm -f " + file_path_temp + "nearraw_*" + file_name)

### Copy over the template files
os.system("cp -f " + program_dir + "cal_linelists/"  + template + " .")
os.system("cp -f " + program_dir+"cal_linelists/database/idcalibrated_"+grating+"_"+dichroic+"_template " + "database/")
 
interact = 0

### Perform spectral extraction, one image slice at a time
### Then extract corresponding arc spectra from the arc images
### So we have n stellar spectra from n image slices
### And n x m arc spectra from n image slices and m arc images

for im_slice in image_slices:
    
    iraf.apall(
        input = "t"+im_slice+"_"+file_name, \
        output = "",\
        format = "multispec",\
        references = "",\
        apertures = 1,\
        interactive = interact, \
        find = 1,\
        recenter = 1,\
        resize = 1,\
        edit =interact,\
        trace = 1,\
        fittrace = 0,\
        extract = 1,\
        extras = 1,\
        review = 0,\
        line = "INDEF",\
        nsum = -100,\
        lower = -10.0,\
        upper = 10.0,\
        b_sample = "-20:-8,8:20",\
        b_order = 1,\
        b_naverage = -3,\
        b_niterate = 0,\
        b_low_reject = 3.0,\
        b_high_reject = 3.0,\
        b_grow = 0.0,\
        width = 5.0,\
        radius = 10.0,\
        threshold = 0.0,\
        nfind = 1,\
        ylevel = 0.5,\
        peak = 1,\
        bkg = 1,\
        t_nsum = 100,\
        t_step = 10,\
        t_nlost = 3,\
        t_function = "spline3",\
        t_order = 2,\
        t_naverage = -10,\
        t_niterate = 1,\
        t_low_reject = 3.0,\
        t_high_reject = 3.0,\
        t_grow = 0.0,\
        background = "fit",\
        weights = "variance",\
        clean = 1,\
        lsigma = 20.0,\
        usigma = 3.0,\
        saturation = 64000,\
        readnoise = 3.8,\
        gain = 0.9)
        
    ### Extract NeAr arc lamp spectrum
    print "Using apall to extract the arc spectrum according to the same aperture as the object spectrum"
    count = 1
    for arc_name in arc_list:
        ### For each arc image, perform extraction at the same
        ### aperture as the stellar spectrum
        os.system("rm database/*"+im_slice+"*" + string.split(arc_name,".")[0] + "*")
        os.system("rm nearraw_" + im_slice + "_" + arc_name)
        
        ### Use apall to extract along the same lines
        ### as that used in the stellar extraction
        iraf.apall(
            input = "t" + im_slice + "_" + arc_name, \
            output = "nearraw_" + im_slice + "_" + arc_name,\
            references = "t"+im_slice+"_" + file_name,\
            apertures = "",\
            find = 0,\
            recenter = 0,\
            resize = 0,\
            edit = 0,\
            trace = 0,\
            back = "none",\
            nfind = "",\
            interactive = 0)

        ### Using reidentify to find a dispersion solution
        print "reidentifying the lines - to make sure of the dispersion solution"
        iraf.reidentify(
            reference = template, \
            images = "nearraw_"+im_slice + "_" + arc_name,\
            answer = "yes",\
            crval = "",\
            cdelt = "",\
            interactive = "yes",\
            section = "first line",\
            newaps = 0,\
            override = 1,\
            refit = 1,\
            trace = 0,\
            step = "10",\
            nsum = "10",\
            shift = "INDEF",\
            search = "INDEF",\
            nlost = 2,\
            cradius = 5.0,\
            threshold = 5.0,\
            addfeatures = 0,\
            coordlist = program_dir + "cal_linelists/" + linelist,\
            match = -2.0,\
            maxfeatures = 60,\
            minsep = 2.0,\
            database = "database",\
            plotfile = "",\
            verbose = 1,\
            graphics = "stdgraph",\
            cursor = "",\
            aidpars = "",\
            mode = "ql")

        ### Apply dispersion solution to object spectrum
        ### First add REFSPEC to the object header using hedit
        iraf.hedit(
            images="t" + im_slice + "_" +string.split(file_name,".")[0]+".ms.fits",\
            fields ="REFSPEC" + str(int(count)),\
            value ="nearraw_" + im_slice+ "_" + arc_name+" "+str(arc_weight[count-1]),\
            add = 1,\
            verify = 0,\
            show = 1,\
            update = 1)

        count = count + 1

    ### Run dispcor to calibrate the object spectrum according to the dispersion
    ### solution
    print "Using dispcor to apply the dispersion solution to the object image"

    os.system("rm dispcorr_" + im_slice + "_" + file_name)

    iraf.dispcor(
        input = "t" + im_slice + "_" + string.split(file_name,".")[0] + ".ms.fits",\
        output = "dispcorr_" + im_slice + "_" + file_name,\
        linearize = "no",\
        database = "database",\
        log = 0,\
        flux = 1,\
        samedisp = 0,\
        ignoreaps = 0,\
        confirm = 0,\
        listonly = 0,\
        verbose = 1)

    iraf.hedit(images="dispcorr_" + im_slice + "_" + file_name,fields="SFIT",value="1",add=0,delete=1,verify=0,show=1,update=1)
    iraf.hedit(images="dispcorr_" + im_slice + "_" + file_name,fields="SFITB",value="1",add=0,delete=1,verify=0,show=1,update=1)

    ### Apply high rejection to remove cosmic rays, dead pixels, etc.
    print "Applying high rejection"
    os.system("rm cray_" + im_slice + "_" + file_name)
    iraf.continuum(
        input = "dispcorr_" + im_slice + "_" + file_name,\
        output = "cray_" + im_slice + "_" + file_name,\
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
        low_reject = 15.0,\
        high_reject = 5.0,\
        niterate = 5,\
        grow = 1.0)

    iraf.hedit(images="cray_" + im_slice + "_" + file_name,fields="SFIT",value="1",add=0,delete=1,verify=0,show=1,update=1)
    iraf.hedit(images="cray_" + im_slice + "_" + file_name,fields="SFITB",value="1",add=0,delete=1,verify=0,show=1,update=1)

    ### Apply normalisation with continuum
    print "Fitting continuum and normalising spectrum"
    os.system("rm norm_" + im_slice + "_" + file_name)
    iraf.continuum(
        input = "cray_" + im_slice + "_" + file_name,\
        output = "norm_" + im_slice + "_" + file_name,\
        lines = "*",\
        bands = "*",\
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
        low_reject = 2.0,\
        high_reject = 3.0,\
        niterate = 5,\
        grow = 1,\
        ask = "no",)
