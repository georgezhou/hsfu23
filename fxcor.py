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
### Performs fxcor RV measurement of the RV measurement
### outputs fxcor_stellar.txt file containing RV measurement from each
### template spectrum.

### The templates are RV standard stars taken on the same night

### usage: python fxcor.py file_path file_name

#################
### Functions ###
#################

### Function running fxcor
### Requires one or more input files and input_rv in the form of string
### EG "r0036.fits,r0037.fits" etc
### Requires specification of lines in the form of string
### EG "a6275-6290,a6867-6882"
### Requires name of output database
### fitshead_update is 1 or 0
### and asks whether you want to write out a ccf file

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
        continuum = "both",\
        filter = "both",\
        rebin = "smallest",\
        pixcorr = 0,\
        osample = lines,\
        rsample = lines,\
        apodize = 0.2,\
        function = "gaussian",\
        width = 7.0,\
        height= 0.,\
        peak = 0,\
        minwidth = 7.0,\
        maxwidth = 7.0,\
        weights = 1.,\
        background = "INDEF",\
        window = "INDEF",\
        wincenter = "INDEF",\
        output = output,\
        verbose = "long",\
        imupdate = fitshead_update,\
        graphics = "stdgraph",\
        interactive = interact,\
        autowrite = 1,\
        ccftype = "text",\
        observatory = "sso",\
        continpars = "",\
        filtpars = "",\
        keywpars = "")

### Hedit VHELIO
def append_VHELIO(image_file,v_value): #Note v_value must be string!
    iraf.hedit(
        images = image_file,\
        fields = "VHELIO",\
        value = v_value,\
        add = 1,\
        addonly = 0,\
        delete = 0,\
        verify = 0,\
        show = 1,\
        update = 1)

### Retrieve VHELIO information by searching database
def retrieve_RV(star_name,database):
    VHELIO = "ERROR"
    for i in range(len(database)):
        if database[i][0] == star_name:
            VHELIO = database[i][1]
            break
    return VHELIO

########################
### Start of program ###
########################

file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

### Read in spectral regions for RV cc
stellar_region = functions.read_param_file("STELLAR_REGION")

### Find out number of apertures used
if functions.read_config_file("COMBINE_APERTURES") == "false":
    no_apertures = int(functions.read_config_file("NO_APERTURES"))
else:
    no_apertures = 1

print "This script uses iraf.fxcor to find RV solution of " +file_name

program_dir = os.getcwd() + "/" #Save the current working directory

### Change directory to reduced/
os.chdir(file_path_reduced) #Change to ../reduced/ dir

#################################
### Load all the RV_standards ###
#################################

RV_list = functions.read_ascii(file_path_temp + "RV_Standard_list")

for i in range(len(RV_list)):
    RV_list[i] = "normspec_" + RV_list[i] + ".fits"
    print RV_list[i]


### Check that it exists, else take it out of the list
temp_list = []
for i in range(len(RV_list)):
    if os.path.exists(file_path_reduced + RV_list[i]):
        temp_list.append(RV_list[i])
        print RV_list[i]

RV_list = temp_list
if len(RV_list) > 0:

    ### Create string list RV_Standards to feed into iraf
    RV_Standards = ""
    for i in range(len(RV_list)):
        RV_Standards = RV_Standards + RV_list[i] + ","

    ### Append VHELIO to all RV standard stars - this requires 
    ### Ascii file RV_standard.dat to be present in program/

    ### Read in RV_standard.dat
    RV_standard_dat = functions.read_ascii(program_dir + "RV_standard.dat")
    RV_standard_dat = functions.read_table(RV_standard_dat)

    ### Hedit VHELIO by matching object_name to RV_standard_dat
    for i in range(len(RV_list)):
        ### Find star name
        file_location = file_path_reduced + RV_list[i]
        hdulist = pyfits.open(file_location)
        object_name = hdulist[0].header["OBJECT"]
        hdulist.close()

        ### Find corresponding RV information in database    
        VHELIO = retrieve_RV(object_name,RV_standard_dat)
        append_VHELIO(file_location,str(VHELIO))

    ############################
    ### Apply header changes ###
    ############################

    ### Apply setJD to both images
    iraf.setjd(
        images = "normspec_"+file_name + "," + RV_Standards,\
        observatory = ")_.observatory",\
        date = "date-obs",\
        time = "ut",\
        exposure = "exptime",\
        ra = "ra",\
        dec = "dec",\
        epoch = "equinox",\
        jd = "jd",\
        hjd = "hjd",\
        ljd = "ljd",\
        utdate = 1,\
        uttime = 1,\
        listonly = 0)

    ### Add required header information to both images
    ### Add EPOCH keyward to fits header
    iraf.hedit(
        images = "normspec_" + file_name+ "," + RV_Standards,\
        fields = "EPOCH",\
        value = "2000.0",\
        add = 1,\
        addonly = 0,\
        delete = 0,\
        verify = 0,\
        show = 1,\
        update = 1)

    ##################################################################
    ### Separate out the apertures of the RV standard star spectra ###
    ##################################################################
    ### This is because fxcor doesn't recognise multispec templates
    ### So each template will have to be a oned object.
    ### The object spectrum doesn't suffer from the same problem
    ### so that doesn't have to be separated.

    if no_apertures > 1:
        RV_Standards_templist = ""
        RV_Standards = string.split(RV_Standards,",")
        for star in RV_Standards:
            if not star == "":
                for i in range(1,no_apertures+1):
                    iraf.scopy(
                        input = star,\
                        output = str(i)+"_"+star,\
                        w1 = 0.0,\
                        w2 = 20000,\
                        apertures = i,\
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
                    RV_Standards_templist = RV_Standards_templist + str(i) + "_" + star + ","
            RV_Standards = RV_Standards_templist

    #################
    ### Run fxcor ###
    #################

    ### Makesure keywpars is set at default
    iraf.unlearn(iraf.keywpars)
    iraf.filtpars.setParam("f_type","square",check=1,exact=1)
    iraf.filtpars.setParam("cuton",50,check=1,exact=1)
    iraf.filtpars.setParam("cutoff",1500,check=1,exact=1)

    ### Then apply fxcor to the stellar regions for RV measurement
    os.system("rm fxcor_stellar*")
    run_fxcor("normspec_" + file_name,RV_Standards,stellar_region,"fxcor_stellar",0,False)

    os.chdir(program_dir) #Change directory back to the program directory

else:
    print "No RV Standards! Cannot apply fxcor"
