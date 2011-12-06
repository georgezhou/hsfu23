### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import pyfits
import urllib

### Load functions script (located in the same folder)
import functions

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

### Deredden the data spectrum
### Using deredden task in iraf
### Create 10 spectra of different deredden values, upto max 
### Max found from Schlegel extinction map

### Usage: python deredden.py file_path file_name

#################
### Functions ###
#################

def try_webpage(url):
    try:
        urllib.urlopen(url)
        return True
    except IOError:
        return False

def find_max_reddening(ra,dec):
    page_url = "http://irsa.ipac.caltech.edu/cgi-bin/DUST/nph-dust?locstr="
    page_url = page_url + ra + "+" + dec + "+equ+j2000"

    if try_webpage(page_url):

        schlegel = urllib.urlopen(page_url)
        schlegel = schlegel.read()

        schlegel = string.split(schlegel,"<meanValue>")[1]
        schlegel = string.split(schlegel)

        max_reddening = float(schlegel[0])

    else:
        print "Could not connect to Schlegel database"
        print "Default max reddening = 0.10"
        max_reddening = 0.10

    return max_reddening

########################
### Start of program ###
########################

file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

print "This script applies reddening to " +file_name

program_dir = os.getcwd() + "/" #Save the current working directory

### Change directory to temp/
os.chdir(file_path_reduced) #Change to ../temp/

### Create deredden folder
os.system("mkdir deredden")
os.system("rm deredden/" +"*"+ string.split(file_name,".")[0] + "*")

### Define max reddening
#redden_max = 0.13

hdulist = pyfits.open(file_path + file_name)
object_name = hdulist[0].header["OBJECT"]
ra = hdulist[0].header["RA"]
dec = hdulist[0].header["DEC"]
hdulist.close()

redden_max = find_max_reddening(ra,dec)
print "Max reddening ", redden_max
n = 10

redden_step = redden_max / n

##################
### Start loop ###
##################

redden = 0.0
while redden <= redden_max:
    redden_name = "deredden_" + str(redden) + "_" + file_name
    
    ### Apply deredden
    iraf.deredden(
        input = "fluxcal_" + file_name,\
        output = redden_name,\
        value = redden,\
        R = 3.1,\
        type = "E(B-V)",\
        apertures = "*",\
        override = 1,\
        uncorrect = 0,\
        mode = "al")

    ### Create .dat file out of fits file redden_name
    
    os.system("rm " + redden_name + ".dat")

    iraf.wspectext(redden_name + "[*,1,1]", redden_name + ".dat")

    spectrum = functions.read_ascii(redden_name + ".dat")
    spectrum = functions.read_table(spectrum)
    temp = []
    for i in spectrum:
        if len(i) == 2:
            if functions.is_number(i[0]):
                temp.append(i)
    spectrum = temp
    spectrum = spectrum[1:len(spectrum)-2]

    output_spectrum = open(redden_name + ".dat","w")
    functions.write_table(spectrum,output_spectrum)
    output_spectrum.close()

    os.system("mv " + redden_name + ".dat deredden")
    os.system("mv " + redden_name + " deredden")

    redden = redden + redden_step
