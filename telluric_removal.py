### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import pyfits
from scipy import interpolate
import matplotlib.pyplot as plt
from scipy import optimize
### Load functions script (located in the same folder)
import functions

### Load iraf moduels
iraf.noao.rv()
iraf.astutil()
iraf.onedspec()

#################
### Functions ###
#################
def find_min(input_x,input_y):

    for i in range(len(input_y)):
        if input_y[i] == min(input_y):
            minpos = input_x[i]

    # fitfunc = lambda p, x: abs(p[0])*(x-p[1])**2 + p[2] # Target function
    # errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function
    # p0 = [1,1.0,0] # Initial guess for the parameters
    # p1, success = optimize.leastsq(errfunc, p0[:], args=(input_x,input_y))
    # print p1[1]
    # #plt.plot(input_x,abs(p1[0])*(input_x-p1[1])**2 + p1[2])

    # if abs(p1[1] - minpos) < 0.1:
    #     minpos = p1[1]

    return minpos

def run_fxcor(input_file,input_rv,lines):
    iraf.unlearn(iraf.keywpars)

    iraf.filtpars.setParam("f_type","square",check=1,exact=1)
    iraf.filtpars.setParam("cuton",50,check=1,exact=1)
    iraf.filtpars.setParam("cutoff",2000,check=1,exact=1)

    os.system("rm fxcor_shift*")
    iraf.fxcor(
        objects = input_file, \
        templates = input_rv, \
        apertures = "*", \
        cursor = "",\
        continuum = "both",\
        filter = "both",\
        rebin = "smallest",\
        pixcorr = 0,\
        osample = lines,\
        rsample = lines,\
        apodize = 0.2,\
        function = "gaussian",\
        width = 15,\
        height= 0.,\
        peak = 0,\
        minwidth = 15,\
        maxwidth = 15,\
        weights = 1.,\
        background = "INDEF",\
        window = "INDEF",\
        wincenter = "INDEF",\
        output = "fxcor_shift",\
        verbose = "long",\
        imupdate = 0,\
        graphics = "stdgraph",\
        interactive = 0,\
        autowrite = 1,\
        ccftype = "image",\
        observatory = "sso",\
        continpars = "",\
        filtpars = "",\
        keywpars = "")

    vel_shift = functions.read_ascii("fxcor_shift.txt")
    vel_shift = functions.read_table(vel_shift)
    vel_shift = str(vel_shift[0][11])

    if vel_shift == "INDEF":
        vel_shift = 0
    print "shifting by ",vel_shift,"km/s"

    return vel_shift

########################
### Start of program ###
########################

### Define telluric regions ### FXCOR format
TELLURIC_REGION_O2_1 = "a6853-7114"
TELLURIC_REGION_O2_2 = "a7450-7812"
TELLURIC_REGION_H2O = "a7116-7425,a7804-8436"

spectrum = sys.argv[1]

camera = "red"
grating = "R3000"
dichroic = "RT560"
program_dir = os.getcwd() + "/" #Save the current working directory

os.system("mkdir temp_folder")
os.system("rm -f temp_folder/*")
os.system("cp "+spectrum+" temp_folder/")
os.chdir("temp_folder")

spectrum_name = string.split(spectrum,"/")[-1]

def remove_molecule(molecule,spec_name,outspec_name):

    telluric_region = eval("TELLURIC_REGION_"+molecule)
    telluric_region_list = string.split(telluric_region,",")
    for n in range(len(telluric_region_list)):
        region = telluric_region_list[n][1:]
        region = string.split(region,"-")
        temp = []
        for i in region:
            temp.append(float(i))
        telluric_region_list[n] = temp

    ### Copy telluric line spectra to working directory
    telluric_fits = grating + "_"+molecule+".fits"

    os.system("cp -f "+program_dir+"telluric_fits/" + telluric_fits + " telluric.fits")
    os.system("rm temp_norm*")
    os.system("rm temp_spec*")
    os.system("cp -f "+spec_name+" temp_spec.fits")

    iraf.continuum(
        input = spec_name,\
        output = "temp_norm.fits",\
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
        sample = "*",\
        naverage = 1,\
        function = "spline3",\
        order = 20,\
        low_reject = 2.0,\
        high_reject = 5.0,\
        niterate = 5,\
        grow = 2.0,\
        ask = "yes")

    ##################
    ### Find shift ###
    ##################
    shift = run_fxcor("telluric.fits","temp_norm.fits",telluric_region)
    os.system("rm telluric.dat")
    iraf.dopcor(
        input = "telluric.fits",\
        output = "telluric.fits",\
        redshift = shift,\
        isvelocity = 1,\
        add = 1,\
        dispersion = 1,\
        flux = 0,\
        verbose = 0)

    iraf.wspectext(
        input = "telluric.fits",\
        output = "telluric.dat",\
        header = 0)

    ######################################
    ### Iterative telluric subtraction ###
    ######################################

    def iterate():
        os.system("rm temp_norm.dat")
        iraf.wspectext(
            input = "temp_norm.fits",\
            output = "temp_norm.dat",\
            header = 0)

        data_spec = transpose(loadtxt("temp_norm.dat"))
        wave = arange(min(data_spec[0]),max(data_spec[0]),1)
        data_flux = interpolate.splrep(data_spec[0],data_spec[1])
        data_flux = interpolate.splev(wave,data_flux)

        telluric_spec = transpose(loadtxt("telluric.dat"))
        telluric_flux = interpolate.splrep(telluric_spec[0],telluric_spec[1])
        telluric_flux = interpolate.splev(wave,telluric_flux)

        ### Loop through telluric scaling
        telluric_scaling = []
        rms_list = []

        maxscale = 1.08
        for scale in arange(0.0,maxscale,0.01):
            scatter_list = []
            for region in telluric_region_list:
                temp_flux = []
                temp_tel = []

                for i in range(len(wave)):
                    if wave[i] > region[0] and wave[i] < region[1]:
                        temp_flux.append(data_flux[i])
                        temp_tel.append(telluric_flux[i])
                    if wave[i] > region[1]:
                        break

                temp_flux = array(temp_flux)
                temp_tel = array(temp_tel)
                scatter = temp_flux / (temp_tel * scale + (1-scale))

                # plt.plot(scatter)
                # plt.show()

                scatter_list.append(std(scatter))

            telluric_scaling.append(scale)
            rms_list.append(average(scatter_list))

        telluric_scaling,rms_list = array(telluric_scaling),array(rms_list)
        best_scale = find_min(telluric_scaling,rms_list)
        if best_scale > maxscale:
            best_scale = maxscale
        if best_scale < 0:
            best_scale = 0

        print "scaling telluric by",best_scale

        # plt.plot(telluric_scaling,rms_list)
        # plt.show()

        os.system("cp telluric.fits telluric_temp.fits")

        iraf.sarith(
            input1 = "telluric_temp.fits",\
            op = "*",\
            input2 = best_scale,\
            output = "telluric_temp.fits",\
            w1 = "INDEF",\
            w2 = "INDEF",\
            apertures = "",\
            bands = "",\
            beams = "",\
            apmodulus = 0,\
            reverse = 0,\
            ignoreaps = 1,\
            format = "multispec",\
            renumber = 0,\
            offset = 0,\
            clobber = 1,\
            merge = 0,\
            rebin = 0,\
            verbose = 0)

        iraf.sarith(
            input1 = "telluric_temp.fits",\
            op = "+",\
            input2 = 1-best_scale,\
            output = "telluric_temp.fits",\
            w1 = "INDEF",\
            w2 = "INDEF",\
            apertures = "",\
            bands = "",\
            beams = "",\
            apmodulus = 0,\
            reverse = 0,\
            ignoreaps = 1,\
            format = "multispec",\
            renumber = 0,\
            offset = 0,\
            clobber = 1,\
            merge = 0,\
            rebin = 0,\
            verbose = 0)

        iraf.sarith(
            input1 = "temp_spec.fits",\
            op = "/",\
            input2 = "telluric_temp.fits",\
            output = "temp_spec",\
            w1 = "INDEF",\
            w2 = "INDEF",\
            apertures = "",\
            bands = "",\
            beams = "",\
            apmodulus = 0,\
            reverse = 0,\
            ignoreaps = 1,\
            format = "multispec",\
            renumber = 0,\
            offset = 0,\
            clobber = 1,\
            merge = 0,\
            rebin = 0,\
            verbose = 0)

        iraf.sarith(
            input1 = "temp_norm.fits",\
            op = "/",\
            input2 = "telluric_temp.fits",\
            output = "temp_norm",\
            w1 = "INDEF",\
            w2 = "INDEF",\
            apertures = "",\
            bands = "",\
            beams = "",\
            apmodulus = 0,\
            reverse = 0,\
            ignoreaps = 1,\
            format = "multispec",\
            renumber = 0,\
            offset = 0,\
            clobber = 1,\
            merge = 0,\
            rebin = 0,\
            verbose = 0)

        return best_scale

    best_scaling = 1.0
    while best_scaling > 0.05:
        best_scaling = iterate()

    os.system("cp temp_spec.fits "+outspec_name)

####################
### Main program ###
####################

os.system("rm inprogress.fits")
os.system("rm telcor_"+spectrum_name)

if camera == "red":

    print "removing tellurics for ",spectrum_name
    remove_molecule("H2O",spectrum_name,"inprogress.fits")
    remove_molecule("O2_1","inprogress.fits","inprogress.fits")
    remove_molecule("O2_2","inprogress.fits","telcor_"+spectrum_name)

