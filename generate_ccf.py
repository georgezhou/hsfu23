### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import pyfits
from pytools.irafglobals import *

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

### Generates the CCF of the input spectrum by CC the object spectrum against a 
### synthetic of matching teff and logg. 

### Uses fxcor to generate a .dat file of the CCF and writes it into the file_path/reduced/ 
### directory

### Usage: python generate_ccf.py file_path file_name

#############
### To Do ###
#############
### Analyse the amount of flux in each aperture
### output the fractional flux as weights list
### This is the same function as that in calculate_RV.py
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

### Function running fxcor
### Requires specification of lines in the form of string
### EG "a6275-6290,a6867-6882"
### Requires name of output database
### fitshead_update is 1 or 0

def run_fxcor(input_file,input_rv,lines,output,fitshead_update,write_ccf):
    if write_ccf:
        ccf_command = program_dir + "fxcor_cursor_command.txt"
        if best_aperture == 1:
            use_apertures = "*"
        else:
            use_apertures = str(best_aperture)
        interact = 1
    else:
        ccf_command = ""
        use_apertures = "*"
        interact = 0

    iraf.fxcor(
        objects = input_file, \
        templates = input_rv, \
        apertures = use_apertures, \
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

########################
### Start of program ###
########################

file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

print "This script uses iraf.fxcor to generate a CCF for " +file_name + " using synthetic templates"

program_dir = os.getcwd() + "/" #Save the current working directory
### Load fxcor RV measurements
fxcor_stellar = functions.read_ascii(file_path_reduced + "fxcor_stellar.txt")
fxcor_stellar = functions.read_table(fxcor_stellar)

### Load grating / camera settings
grating = functions.read_config_file("GRATING")
dichroic = functions.read_config_file("RT560")

region_w1 = functions.read_param_file(grating+"_"+dichroic+"_w1")
region_w2 = functions.read_param_file(grating+"_"+dichroic+"_w2")

### Load location of library
synthetic_library = functions.read_param_file("RV_SPECTRAL_LIBRARY")

### Load RV fxcor region
stellar_region = functions.read_param_file("STELLAR_REGION")

### Determine best aperture
### by finding the flux ratios of apertures
### We use only the best aperture for generating the CCF
aperture_weights = list(find_flux_weights(file_name))

best_aperture = 1
for i in range(len(aperture_weights)):
    if aperture_weights[i] == max(aperture_weights):
        best_aperture = i+1
        break

print "best aperture is ", best_aperture

### Estimate teff and logg
hdulist = pyfits.open(file_path_reduced + "normspec_"+file_name)
object_name = hdulist[0].header['OBJECT']
hdulist.close()

hsmso_connect = functions.read_config_file("HSMSO_CONNECT")
hscand_connect = functions.read_config_file("HSCAND_CONNECT")
default_teff = float(functions.read_config_file("TEFF_ESTIMATE"))
default_logg = float(functions.read_config_file("LOGG_ESTIMATE"))
teff,logg = functions.estimate_teff_logg(file_path,file_name,object_name,hsmso_connect,hscand_connect,default_teff,default_logg)

### Change directory to reduced/
os.chdir(file_path_reduced) #Change to ../reduced/ dir

###########################
### Determine synthetic ###
###########################

### Check if synthetic template exists
### If not, use the closest one in logg
synthetic_template = "template_" + str(teff) + "_" + str(logg) + "_0.0.fits"
if os.path.exists(synthetic_library + synthetic_template):
    print "Using synthetic template " + synthetic_template
else:
    print "no template exists, using closest matching template"
    while logg <= 5.0:
        logg = logg + 0.5
        synthetic_template = "template_" + str(teff) + "_" + str(logg) + "_0.0.fits"
        if os.path.exists(synthetic_library + synthetic_template):
            print "Using synthetic template " + synthetic_template
            break

### Copy the template over
os.system("cp -f " + synthetic_library + synthetic_template + " " +file_path_reduced + "synthetic.fits")

### Apply normalisation to synthetic

def trim_spectra(spectrum_name):
    iraf.scopy(
        input = spectrum_name,\
        output = spectrum_name,\
        w1 = region_w1,\
        w2 = region_w2,\
        apertures = "",\
        bands = "",\
        beams = "",\
        apmodulus = "0",\
        format = "multispec",\
        renumber = 0,\
        offset = "0",\
        clobber = 1,\
        rebin = 1,\
        verbose = 1,\
        mode = "ql")

trim_spectra("synthetic.fits")

print "Fitting continuum and normalising synthetic spectrum"
iraf.continuum(
    input = "synthetic",\
    output = "n_synthetic",\
    lines = "*",\
    bands = 1,\
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
    high_reject = 0.0,\
    niterate = 5,\
    grow = 1,\
    ask = "no")

os.system("mv -f n_synthetic.fits synthetic.fits")

#################
### Run fxcor ###
#################

### Apply setJD to object image
iraf.setjd(
    images = "normspec_" + file_name,\
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

### Add required header information to object image
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

### Makesure keywpars is set at default
iraf.unlearn(iraf.keywpars)

iraf.filtpars.setParam("f_type","square",check=1,exact=1)
iraf.filtpars.setParam("cuton",50,check=1,exact=1)
iraf.filtpars.setParam("cutoff",5000,check=1,exact=1)

### Run fxcor to record ccf of best aperture
os.system("rm " + file_path_reduced + "new_ccf.txt")
os.system("rm " + file_path_reduced + "fxcor_synthetic*")
run_fxcor("normspec_" + file_name,"synthetic.fits",stellar_region,"fxcor_synthetic",0,True)
os.system("mv new_ccf.txt " + "ccf_" + file_name + ".txt")
