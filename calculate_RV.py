from numpy import *
import sys
import string
import functions
import pyfits
import os
from pyraf import iraf
from pytools.irafglobals import *

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
### This script takes the output of fxcor
### and performs weighted average to optimally derive an RV solution.
### The weights take into account the flux per image slice, 
### fxcor ccf height, and fxcor rv error.

#################
### Functions ###
#################
### Analyse the amount of flux in each aperture
### output the fractional flux as weights list
def find_flux_weights(file_name):

    os.chdir(program_dir)

    if functions.read_config_file("COMBINE_APERTURES") == "false":

        no_apertures = eval(functions.read_config_file("NO_APERTURES"))

        multispec_name = "spec_"+file_name

        os.chdir(file_path_reduced)

        ### Load spectrum
        print "Finding best aperture"

        aperture_flux = []
        i = 1
        while i <= no_apertures:
            try:
                os.system("rm -f " + file_path_reduced + "aperture.fits")
                iraf.scopy(
                    input = file_path_reduced + multispec_name,\
                    output = file_path_reduced + "aperture.fits",\
                    w1 = region_w1,\
                    w2 = region_w2,\
                    apertures = i,\
                    bands = "",\
                    beams = "",\
                    apmodulus = 0,\
                    format = "multispec",\
                    renumber = 1,\
                    offset = 0,\
                    clobber = 1,\
                    merge = 1,\
                    rebin = 1,\
                    verbose = 1)

                spectrum_maximum = iraf.imstat(
                    images = file_path_reduced + "aperture.fits",\
                    fields = "midpt",\
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

                spectrum_maximum = float(spectrum_maximum[1])
                aperture_flux.append(spectrum_maximum)
                os.system("rm -f " + file_path_reduced + "aperture.fits")

                i = i + 1

            except (IrafError,ValueError):
                print "Aperture " + str(i) + " not found"
                aperture_flux.append(0)
                i = i + 1

        aperture_flux = array(aperture_flux)
        aperture_flux = aperture_flux / sum(aperture_flux)
        os.chdir(program_dir)
    else:
        aperture_flux = array([1.])
    return aperture_flux

### Extracts defined elements from a table
### Input is a list
### Output is a new truncated table with only the elements needed
def extract_elements(table,input_list):
    output_table = []
    for i in range(len(table)):
        output_i = []
        for j in range(len(input_list)):
            output_i.append(table[i][input_list[j]])
        output_table.append(output_i)
    return output_table

# ### Calculate linear error
# def linear_error(error_list,value_list):
#     error_list = array(error_list)
#     error = sqrt(sum(error_list**2))
    
### Combine two tables
### Both need to have the same number of rows
def combine_tables(table1,table2):
    output_table = []
    for i in range(len(table1)):
        output_i = table1[i] + table2[i]
        output_table.append(output_i)

    return output_table

### Compute weighted average
def waverage(data,error):
    data = array(data)
    error = array(error)
    weight = 1 / (error**2)
    numerator = sum(data * weight)
    denom = sum(weight)
    return numerator / denom

### Compute weighted stdev
### 1/1-V2 sum (Wi (Xi - mean(xi))**2)
def wstd(data,error):
    avg = waverage(data,error)
    data = array(data)
    error = array(error)
    weight = 1 / (error**2)
    V2 = sum(weight**2)
    sumlist = []
    for i in range(len(data)):
        element_i = weight[i] * (data[i] - avg)**2
        sumlist.append(element_i)
    wvar = (1 / (1-V2)) * sum(sumlist)
    return sqrt(wvar)

### Use output of RV_out.dat, return RV info of a particular star
def calc_RV(RV_out,file_name):
    ### Find the columns related
    related = []
    file_name = string.split(file_name,".")[0]
    for i in range(len(RV_out)):
        row_name = RV_out[i][1]
        row_name = string.split(row_name,".")[0]
        row_name = string.split(row_name,"_")[1]
        if file_name == row_name:
            related.append(RV_out[i])

    RV_table = []
    for i in range(len(related)):
        print related[i]
        JD = related[i][3]
        stellar_height = related[i][5]
        vhelio = related[i][7]
        vhelio_err = related[i][8]
        aperture = int(related[i][4]) - 1
        flux_weight = aperture_weights[aperture]

        if functions.is_number(stellar_height) and functions.is_number(JD) and functions.is_number(vhelio) and functions.is_number(vhelio_err):
            if stellar_height > 0.20: ### NORMAL
            #if stellar_height > 0.0: ### Manual
                RV_table.append([JD,vhelio,vhelio_err,stellar_height,flux_weight])

    if RV_table == []:
        print "Lowering ccf_height threshold"
        ### Lower the bar on ccf_height
        for i in range(len(related)):
            print related[i]
            JD = related[i][3]
            stellar_height = related[i][5]
            vhelio = related[i][7]
            vhelio_err = related[i][8]
            aperture = int(related[i][4]) - 1
            flux_weight = aperture_weights[aperture]

            if functions.is_number(stellar_height) and functions.is_number(JD) and functions.is_number(vhelio) and functions.is_number(vhelio_err):
                if stellar_height > 0.10: ### NORMAL
                #if stellar_height > 0.0: ### Manual
                    RV_table.append([JD,vhelio,vhelio_err,stellar_height,flux_weight])

    if RV_table == []:
        ### If it still doesn't work, return INDEF
        return ["INDEF","INDEF","INDEF","INDEF"]

    else:

        ### Use (fxcor telluric error + telluric height + stellar error +
        ### stellar height) * (1/flux_weight) as weights
        ### For final velocity calculations

        JD = array(transpose(RV_table)[0])
        vhelio = array(transpose(RV_table)[1])
        vhelio_err = array(transpose(RV_table)[2])
        stellar_height = array(transpose(RV_table)[3])
        flux_weights = array(transpose(RV_table)[4])

        fxcor_err = average(vhelio_err)

        if JD == []:
            return ["INDEF","INDEF","INDEF"]
        if len(JD) == 1:
            return JD[0],vhelio[0],vhelio_err[0],stellar_height[0]
        if len(JD) == 2:
            velocity = vhelio
            weights = (1/flux_weights) * (vhelio_err / sum(vhelio_err) + (1/stellar_height) / sum(1/stellar_height))
            return JD[0],waverage(velocity,weights),average(vhelio_err),average(stellar_height)
        if len(JD) >= 3:
            v_list = []
            err_list = []
            stellar_height_list = []
            flux_weights_list = []
            for i in range(len(vhelio)):
                if (abs(vhelio[i] - median(vhelio)) < 10.0) and (vhelio_err[i] < 10.0):
                    v_list.append(vhelio[i])
                    err_list.append(vhelio_err[i])
                    stellar_height_list.append(stellar_height[i])
                    flux_weights_list.append(flux_weights[i])

            if len(v_list) == 0:
                v_list = []
                err_list = []
                stellar_height_list = []
                flux_weights_list = []
                for i in range(len(vhelio)):
                    if (abs(vhelio[i] - median(vhelio)) < 50.0) and (vhelio_err[i] < 50.0):
                        v_list.append(vhelio[i])
                        err_list.append(vhelio_err[i])
                        stellar_height_list.append(stellar_height[i])
                        flux_weights_list.append(flux_weights[i])

            err_list = array(err_list)
            stellar_height_list = array(stellar_height_list)
            flux_weights_list = array(flux_weights_list)

            poisson_factor = (1/flux_weights_list) * (err_list/sum(err_list) +(1/stellar_height_list)/sum(1/stellar_height_list))
            poisson_factor = 1 / poisson_factor
            poisson_factor = poisson_factor / max(poisson_factor)
            poisson_factor = sqrt(sum(poisson_factor)/nstandards)

            v_err = std(v_list)
            velocity = waverage(v_list,(1/flux_weights_list) * (err_list/sum(err_list) + (1/stellar_height_list)/sum(1/stellar_height_list)))
            error = sqrt(waverage(err_list,1/flux_weights_list)**2 + v_err**2)/poisson_factor 
            return JD[0],velocity,error,average(stellar_height_list)

###################################
### Load fxcor output txt files ###
###################################

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

program_dir = os.getcwd() + "/" #Save the current working directory

### Load fxcor RV measurements
fxcor_stellar = functions.read_ascii(file_path_reduced + "fxcor_stellar.txt")
fxcor_stellar = functions.read_table(fxcor_stellar)

### Load grating / camera settings
grating = functions.read_config_file("GRATING")
dichroic = functions.read_config_file("RT560")

region_w1 = functions.read_param_file(grating+"_"+dichroic+"_w1")
region_w2 = functions.read_param_file(grating+"_"+dichroic+"_w2")

########################
### Start of program ###
########################

### Find weights according flux of each aperture
aperture_weights = find_flux_weights(file_name)
print "weights for each aperture"
print aperture_weights

### Check if previous entries exist
### If so, delete them
if os.path.isfile(file_path_reduced + "RV_out.dat"):
    RV_out = functions.read_ascii(file_path_reduced + "RV_out.dat")
    RV_out = functions.read_table(RV_out)
    temp_table = []
    for i in RV_out:
        row_name = i[1]
        row_name = string.split(row_name,".")[0]
        row_name = string.split(row_name,"_")[1]
        if not string.split(file_name,".")[0] == row_name:
            temp_table.append(i)
    RV_out = temp_table
else:
    RV_out = []

### Extract the important elements from fxcor_stellar.txt
### And save those into a table "RV_out.dat"
extracted_list = extract_elements(fxcor_stellar,[0,1,2,3,4,7,8,12,13])

RV_out = RV_out + extracted_list

extract_output = open(file_path_reduced + "RV_out.dat","w")
extract_output.write("#object image reference HJD aperture stellar_height stellar_fwhm vhelio vhelio_verr \n")
functions.write_table(RV_out,extract_output)
extract_output.close()
 
#############################################################################
### Perform averaging of RV standards from RV_out.dat to estimate real RV ###
#############################################################################

### Open the image header for more info
hdulist = pyfits.open(file_path + file_name)
object_name = hdulist[0].header['OBJECT']
exptime = hdulist[0].header['EXPTIME']
hdulist.close()

### Find number of RV standards
os.system("python find_rv.py "+file_path)
nstandards = open(file_path_temp + "RV_Standard_list").read()
if not nstandards == "":
    nstandards = string.split(nstandards)
    nstandards = float(len(nstandards))
else:
    nstandards = 1.0
os.system("rm "+file_path_temp+" RV_Standard_list")

RV_out = functions.read_ascii(file_path_reduced + "RV_out.dat")
RV_out = functions.read_table(RV_out)

JD,RV,RV_err,height = calc_RV(RV_out,file_name)

print "#Object_name file_name JD RV(km/s) RV_err(km/s) CCF_Height"
print object_name, file_name, JD, RV, RV_err, height

RV_dat = open(file_path_reduced + "RV.dat","a")
RV_dat.write(str(object_name) + " " + str(file_name) + " " + str(JD) + " " + str(RV) + " " + str(RV_err) + " " + str(height) + " " + str(exptime) + "\n")
RV_dat.close()
