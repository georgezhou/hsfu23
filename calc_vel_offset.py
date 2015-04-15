### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import pyfits
from scipy import integrate

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

def gaussian(x,x0):
    #f_norm = exp(-1*(x0[2]-x0[0])**2/(2*x0[1]**2))
    f = exp(-1*(x-x0[0])**2/(2*x0[1]**2))#/f_norm
    return f

def xgaussian(x,x0):
    #f_norm = exp(-1*(x0[2]-x0[0])**2/(2*x0[1]**2))
    f = x*exp(-1*(x-x0[0])**2/(2*x0[1]**2))#/f_norm
    return f

def run_fxcor(input_file,input_rv,lines,output,fitshead_update,write_ccf):
    if write_ccf:
        ccf_command = program_dir + "fxcor_cursor_command.txt"
        interact = 1
    else:
        ccf_command = ""
        interact = 0

    iraf.fxcor(
        objects = input_file, \
        templates = input_rv, \
        apertures = "*", \
        cursor = ccf_command,\
        #cursor = "",\
        continuum = "both",\
        filter = "both",\
        rebin = "smallest",\
        pixcorr = 0,\
        osample = lines,\
        rsample = lines,\
        apodize = 0.2,\
        function = "gaussian",\
        width = 9.0,\
        height= 0.,\
        peak = 0,\
        minwidth = 9.0,\
        maxwidth = 9.0,\
        weights = 1.,\
        background = "INDEF",\
        window = "INDEF",\
        wincenter = "INDEF",\
        #window = 500,\
        #wincenter = 0.0,\
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
    VHELIO = "0.0"
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
file_name_floor = string.split(file_name,"_")[-1]
file_name_floor = string.split(file_name_floor,".fits")[0]
fits = pyfits.open(file_path+file_name_floor+".fits")
candidate = fits[0].header["OBJECT"]

star_no = sys.argv[3]

### Read in spectral regions for RV cc
stellar_region = functions.read_param_file("STELLAR_REGION")
print stellar_region
### Find out number of apertures used
if functions.read_config_file("COMBINE_APERTURES") == "false":
    no_apertures = int(functions.read_config_file("NO_APERTURES"))
else:
    no_apertures = 1

program_dir = os.getcwd() + "/" #Save the current working directory

### Change directory to reduced/
os.chdir(file_path_temp) #Change to ../reduced/ dir
stellar_apertures = loadtxt("stellar_apertures.txt")
#os.system("cp "+program_dir+"G_template.fits .")

#################################
### Load all the RV_standards ###
#################################

#RV_list = functions.read_ascii(file_path_temp + "RV_Standard_list")
RV_list = [file_name_floor]

for i in range(len(RV_list)):
    RV_list[i] = "normspec_" + RV_list[i] + ".fits"
    print RV_list[i]


### Check that it exists, else take it out of the list
temp_list = []
for i in range(len(RV_list)):
    if os.path.exists(file_path_temp + RV_list[i]):
        temp_list.append(RV_list[i])
        print RV_list[i]

RV_list = temp_list
if len(RV_list) > 0:

    ### Create string list RV_Standards to feed into iraf
    RV_Standards = ""
    for i in range(len(RV_list)):
        RV_Standards = RV_Standards + RV_list[i] + ","

    # ### Append VHELIO to all RV standard stars - this requires 
    # ### Ascii file RV_standard.dat to be present in program/

    # ### Read in RV_standard.dat
    # RV_standard_dat = functions.read_ascii(program_dir + "RV_standard.dat")
    # RV_standard_dat = functions.read_table(RV_standard_dat)

    # ### Hedit VHELIO by matching object_name to RV_standard_dat
    # for i in range(len(RV_list)):
    #     ### Find star name
    #     file_location = file_path_reduced + RV_list[i]
    #     append_VHELIO(file_location,"0.0")

    # ############################
    # ### Apply header changes ###
    # ############################

#if True:

    ### Apply setJD to both images
    iraf.setjd(
        images = "normspec_"+file_name,\
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
        images = "normspec_" + file_name,\
        fields = "EPOCH",\
        value = "2000.0",\
        add = 1,\
        addonly = 0,\
        delete = 0,\
        verify = 0,\
        show = 1,\
        update = 1)

    # ##################################################################
    # ### Separate out the apertures of the RV standard star spectra ###
    # ##################################################################
    # ### This is because fxcor doesn't recognise multispec templates
    # ### So each template will have to be a oned object.
    # ### The object spectrum doesn't suffer from the same problem
    # ### so that doesn't have to be separated.

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
                    if os.path.exists(str(i)+"_"+star):
                        RV_Standards_templist = RV_Standards_templist + str(i) + "_" + star + ","
            RV_Standards = RV_Standards_templist

    #################
    ### Run fxcor ###
    #################

    ### Makesure keywpars is set at default
    iraf.unlearn(iraf.keywpars)
    iraf.filtpars.setParam("f_type","square",check=1,exact=1)
    iraf.filtpars.setParam("cuton",50,check=1,exact=1)
    iraf.filtpars.setParam("cutoff",5000,check=1,exact=1)

    iraf.unlearn(iraf.continpars)
    iraf.continpars.setParam("c_interactive",0,check=1,exact=1)
    iraf.continpars.setParam("order",5,check=1,exact=1)
    iraf.continpars.setParam("low_reject",2.0,check=1,exact=1)
    iraf.continpars.setParam("high_reject",2.0,check=1,exact=1)


    ### Then apply fxcor to the stellar regions for RV measurement
    os.system("rm fxcor_stellar*")
    #run_fxcor("normspec_" + file_name,"G_template.fits",stellar_region,"fxcor_stellar",0,False)
    run_fxcor("normspec_" + file_name,RV_Standards,stellar_region,"fxcor_stellar",0,False)

    os.system("cat fxcor_stellar.txt")
    #os.system("mv fxcor_stellar.txt "+file_path_reduced+"veloffsets_"+file_name+".dat")


    ### Calculate offsets
    offsets = genfromtxt("fxcor_stellar.txt",invalid_raise=False)#[:len(stellar_apertures)]

    star_coords = loadtxt(file_path_reduced+"coords_"+file_name+".dat")
    if len(shape(star_coords)) == 1:
        star_coords = array([star_coords])
    star_coords = star_coords[star_no]

    print stellar_apertures
    
    fill_list = []
    for slit in stellar_apertures:
        slitfill = integrate.quad(gaussian,slit,slit+1.,args=([star_coords[2],star_coords[3]]))
        slitfill_x = integrate.quad(xgaussian,slit,slit+1.,args=([star_coords[2],star_coords[3]]))
        fill_centre = slitfill_x[0]/slitfill[0]
        #print slit,slitfill,slitfill_x,slitfill_x[0]/slitfill[0]
        print slit,fill_centre
        fill_list.append(fill_centre)
        
    fill_list = array(fill_list)
    best_slit = argmin(abs(fill_list-floor(fill_list)-0.5))
    quality = 0
    if min(abs(fill_list-floor(fill_list)-0.5)) > 0.05:
        quality = 1


    vel = offsets[:,11]
    vel -= vel[best_slit]

    fill_data = open("/home/george/hsfu23_3/slitfill_data","a")


    for i in range(len(fill_list)):
        fill_data.write(str(fill_list[i])+" "+str(vel[i])+" "+str(quality)+"\n")

    os.chdir(program_dir) #Change directory back to the program directory
    
    


else:
    print "No RV Standards! Cannot apply fxcor"
