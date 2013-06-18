import pyfits
import os
import sys
from numpy import *
from pyraf import iraf
import functions

### Usage: python cc_mdwarf.py /data/file/directory/reduced/ spec_A_r0050.fits
### Works on not normalised spectra
iraf.noao.rv()

def normalise(input_spectrum):
    ### Apply normalisation with continuum
    print "Fitting continuum and normalising spectrum"
    os.system("rm temp.fits")
    iraf.continuum(
        input = input_spectrum,\
        output = "temp.fits",\
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
        order = 1,\
        low_reject = 1.5,\
        high_reject = 3.0,\
        niterate = 5,\
        grow = 2,\
        ask = "no",)

def run_fxcor(input_file,input_rv,lines,output,fitshead_update,write_ccf):
    if write_ccf:
        ccf_command = program_dir + "fxcor_cursor_command.txt"
        interat = 1
    else:
        ccf_command = ""
        interact = 0

    iraf.fxcor(
        objects = input_file, \
        templates = input_rv, \
        apertures = "*", \
        cursor = ccf_command,\
        #cursor = "",\
        continuum = "none",\
        filter = "both",\
        rebin = "smallest",\
        pixcorr = 0,\
        osample = lines,\
        rsample = lines,\
        apodize = 0.2,\
        function = "gaussian",\
        width = 15.0,\
        height= 0.,\
        peak = 0,\
        minwidth = 15.0,\
        maxwidth = 15.0,\
        weights = 1.,\
        background = "INDEF",\
        #window = "INDEF",\
        #wincenter = "INDEF",\
        window = 500,\
        wincenter = 0.0,\
        output = output,\
        verbose = "long",\
        imupdate = fitshead_update,\
        graphics = "stdgraph",\
        interactive = interact,\
        #interactive = 1,\
        autowrite = 1,\
        ccftype = "text",\
        observatory = "sso",\
        continpars = "",\
        filtpars = "",\
        keywpars = "")


### Find info from config file
grating = functions.read_config_file("GRATING")
resolution = int(grating[1:])
dichroic = functions.read_config_file("DICHROIC")

file_path = sys.argv[1]
file_name = sys.argv[2]

program_dir = os.getcwd() + "/" #Save the current working directory

os.system("cp mdwarf_template_norm.fits "+ file_path)

### Change directory to reduced/
os.chdir(file_path)

### Makesure keywpars is set at default
iraf.unlearn(iraf.keywpars)
iraf.filtpars.setParam("f_type","square",check=1,exact=1)
iraf.filtpars.setParam("cuton",50,check=1,exact=1)
iraf.filtpars.setParam("cutoff",5000,check=1,exact=1)

iraf.unlearn(iraf.continpars)
iraf.continpars.setParam("c_interactive",0,check=1,exact=1)
iraf.continpars.setParam("order",2,check=1,exact=1)
iraf.continpars.setParam("low_reject",2.0,check=1,exact=1)
iraf.continpars.setParam("high_reject",2.0,check=1,exact=1)

### Then apply fxcor to the stellar regions for RV measurement
os.system("rm fxcor_stellar*")
#region = "*"
#region = "a5700-6100"
region = "a5250-6815"
normalise(file_name)

run_fxcor("temp.fits","mdwarf_template_norm.fits",region,"fxcor_stellar",0,False)
os.system("cat fxcor_stellar.txt")

### Now calculate RV
data = functions.read_ascii("fxcor_stellar.txt")
data = functions.read_table(data)

rv = []
rverr = []
for i in data:
    if functions.is_number(i[3]):
        hjd = i[3]+50000

    if functions.is_number(i[12]):
        if abs(i[12]) < 500 and abs(i[13]) < 500:
            rv.append(i[12])
            rverr.append(i[13])
    
RV = median(rv)
RV_err = median(rverr)

print "!!!!!!!!!!!"
print "RV",RV,"RVERR",RV_err

### Update database
import mysql_insert



### Find info from the fits header
hdulist = pyfits.open(file_name)
object_name = hdulist[0].header["OBJECT"]
dateobs = hdulist[0].header["DATE-OBS"]
mjd = hdulist[0].header["MJD-OBS"]
#hjd = hdulist[0].header["hjd"]
exptime = hdulist[0].header["EXPTIME"]
comment = hdulist[0].header["NOTES"]
hdulist.close()

ccf_fwhm = 0
ccf_height = 0
bis = 0
bis_err = 0
sn = 0

mysql_insert.db_rv_entry(object_name,file_name,grating,resolution,dichroic,dateobs,mjd,hjd,RV,RV_err,ccf_fwhm,ccf_height,bis,bis_err,sn,exptime,comment)

