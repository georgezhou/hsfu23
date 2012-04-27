import sys
import os
import string
from numpy import *
import functions
import spectype_functions
import spectype_numerical_functions
import matplotlib
import matplotlib.pyplot as plt
import pyfits
from pyraf import iraf
from scipy import interpolate

iraf.kpnoslit()
iraf.noao()
iraf.rv()

###################
### Description ###
###################

### Take input spectrum

### Find chisq in logg - teff space for every reddenining
### Add over reddening 
### Find min chisq 

### usage: python spectype_main.py file_path file_name
### Takes input params from config_file

#################
### Functions ###
#################

def isNaN(x):
    if str(x) == "nan" or str(x) == "NaN":
        return True
    else:
        return False

def run_fxcor(input_file,input_rv,lines,output,fitshead_update,npoints,functiontype):
    iraf.fxcor(
        objects = input_file, \
        templates = input_rv, \
        apertures = "*", \
        cursor = "",\
        continuum = "none",\
        filter = "both",\
        rebin = "smallest",\
        pixcorr = 0,\
        osample = lines,\
        rsample = lines,\
        apodize = 0.2,\
        function = functiontype,\
        width = npoints,\
        height= 0.,\
        peak = 0,\
        minwidth = npoints,\
        maxwidth = npoints,\
        weights = 1.,\
        background = "INDEF",\
        window = "INDEF",\
        wincenter = "INDEF",\
        output = output,\
        verbose = "long",\
        imupdate = fitshead_update,\
        graphics = "stdgraph",\
        interactive = 0,\
        autowrite = 1,\
        ccftype = "image",\
        observatory = "sso",\
        continpars = "",\
        filtpars = "",\
        keywpars = "")

def loop_input_spectrum(input_wave,input_flux,folder,teff_space,logg_space,feh_space,w1,w2,perform_normalise):
    data = []
    for teff in teff_space:
        for logg in logg_space:
            for feh in feh_space:
                template_spectrum = "template_" + str(teff) + "_" + str(logg) + "_" + str(feh)+".dat"
                #print folder + template_spectrum
                template_spectrum = functions.read_ascii(folder+template_spectrum)
                template_spectrum = functions.read_table(template_spectrum)
                template_spectrum = transpose(array(template_spectrum))

                if folder == model_path_flux:
                    template_spectrum = spectype_functions.normalise(template_spectrum,flux_normalise_w1,flux_normalise_w2)
          

                i1 = w1 - min(input_wave)
                i2 = w2 - min(input_wave)

                input_wave_cropped = input_wave[i1:i2]
                input_flux_cropped = input_flux[i1:i2]

                template_spectrum = spectype_numerical_functions.chop_spectrum(template_spectrum,w1-10,w2+10)
                template_interp = interpolate.splrep(template_spectrum[0],template_spectrum[1],s=0)
                template_flux = interpolate.splev(input_wave_cropped,template_interp,der=0)

                sigma = 3.0

                if perform_normalise:
                    diff_flux = input_flux_cropped/median(input_flux_cropped) - template_flux/median(template_flux)

                else:
                    diff_flux = input_flux_cropped - template_flux

                diff_flux = clip(diff_flux,median(diff_flux) - sigma*std(diff_flux),median(diff_flux)+sigma*std(diff_flux))

                rms = sqrt(sum(diff_flux**2) /float(len(input_wave_cropped)))


                # plt.clf()
                # plt.plot(input_wave_cropped,input_flux_cropped/median(input_flux_cropped))
                # plt.plot(input_wave_cropped,template_flux/median(template_flux))
                # plt.show()
                # #sys.exit()

                #print rms
                data.append(rms)
    return data

def plot_spectrum(rms_data,input_spectrum):
    rms_data = functions.read_ascii(rms_data)
    rms_data = functions.read_table(rms_data)
    rms_data = transpose(rms_data)

    ### Find min
    for i in range(len(rms_data[0])):
        if rms_data[3][i] == min(rms_data[3]):
            teff_min = rms_data[0][i]
            logg_min = rms_data[1][i]
            feh_min = rms_data[2][i]
            break

    print teff_min,logg_min,feh_min

    teff_list = []
    logg_list = []
    rms_list = []
    
    for i in range(len(rms_data[0])):
        if rms_data[2][i] == feh_min:
            teff_list.append(rms_data[0][i])
            logg_list.append(rms_data[1][i])
            rms_list.append(rms_data[3][i])

    plt.subplot(211)
    cm = matplotlib.cm.get_cmap('jet')
    sc = plt.scatter(teff_list, logg_list, c=rms_list, vmin=min(rms_list), vmax=max(rms_list), s=70, cmap=cm,edgecolor="w")
    cbar = plt.colorbar(sc)
    cbar.ax.set_ylabel("RMS")

    plt.scatter(teff_min,logg_min,color="r",s=70,marker="+")

    spectype_functions.plot_isochrones(program_dir,"r-",1)

    plt.xlim(max(teff_list)+250,min(teff_list)-250)
    plt.ylim(max(logg_list)+.25,min(logg_list)-0.25)

    plt.xlabel("Teff (K)")
    plt.ylabel("Logg")

    plt.subplot(212)
    data_spectrum = functions.read_ascii(input_spectrum)
    data_spectrum = functions.read_table(data_spectrum)
    data_spectrum = transpose(array(data_spectrum))
    data_spectrum = spectype_functions.normalise(data_spectrum,flux_normalise_w1,flux_normalise_w2)

    template_spectrum = "template_" + str(int(teff_min)) + "_" + str(logg_min) + "_" + str(feh_min)+".dat"
    template_spectrum = functions.read_ascii(model_path_flux+template_spectrum)
    template_spectrum = functions.read_table(template_spectrum)
    template_spectrum = transpose(array(template_spectrum))
    template_spectrum = spectype_functions.normalise(template_spectrum,flux_normalise_w1,flux_normalise_w2)

    plt.plot(data_spectrum[0],data_spectrum[1],"b-")
    plt.plot(template_spectrum[0],template_spectrum[1],"g-")
    plt.xlim(3700,5800)
    
    plt.xlabel("Wavelength (A)")
    plt.ylabel("Normalised flux")

    plt.show()

def find_min_index(input_list):
    for i in range(len(input_list)):
        if input_list[i] == min(input_list):
            return i

########################
### Start of program ###
########################
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

### Read from param and config files
model_path_flux = functions.read_param_file("MODEL_PATH_FLUX")
model_path_norm = functions.read_param_file("MODEL_PATH_NORM")

### Find the region within which to flux normalise
flux_normalise_w1 = eval(functions.read_param_file("NORM_REGION_w1"))
flux_normalise_w2 = eval(functions.read_param_file("NORM_REGION_w2"))

### Find initial estimate of properties
hdulist = pyfits.open(file_path + file_name)
object_name = hdulist[0].header["OBJECT"]
hdulist.close()

print "Analysing ",object_name

hsmso_connect = functions.read_config_file("HSMSO_CONNECT")
hscand_connect = functions.read_config_file("HSCAND_CONNECT")
default_teff = float(functions.read_config_file("TEFF_ESTIMATE"))
default_logg = float(functions.read_config_file("LOGG_ESTIMATE"))
teff_ini,logg_ini = functions.estimate_teff_logg(object_name,hsmso_connect,hscand_connect,default_teff,default_logg)
feh_ini = 0.0
ini_template_spectrum = "template_" + str(teff_ini) + "_" + str(logg_ini) + "_" + str(feh_ini)

print "Initial estimate of teff, logg: ",str(teff_ini),str(logg_ini)

#################
### Make axes ###
#################

teff_space = []
logg_space = []
feh_space = []

teff_min = teff_ini - 1000
teff_max = teff_ini + 1000

if teff_ini < 4500:
    teff_min = int(3500)

if teff_ini > 8000:
    teff_max = int(9000)

### Create grid
teff_i = teff_min
while teff_i <= teff_max:
    teff_space.append(teff_i)
    teff_i = teff_i + 250

logg_i = 0.0
while logg_i <= 5.0:
    logg_space.append(logg_i)
    logg_i = logg_i + 0.5

feh_i = -2.5
while feh_i <= 0.5:
    feh_space.append(feh_i)
    feh_i = feh_i + 0.5

teff_space = array(teff_space)
logg_space = array(logg_space)
feh_space = array(feh_space)

teff_table_list = []
logg_table_list = []
feh_table_list = []

for teff in teff_space:
    for logg in logg_space:
        for feh in feh_space:
            teff_table_list.append(teff)
            logg_table_list.append(logg)
            feh_table_list.append(feh)

######################
### Define regions ###
######################

print "Using specific regions for spectral typing"
### Check the temp and define which logg sensitive regions to use
if teff_ini > 4750 and teff_ini < 5750:
#if teff_ini > 4750 and teff_ini < 6250:
    #logg_regions = [[5140,5235]]
    logg_regions = [[5100,5400]]
if teff_ini <= 4750 and teff_ini > 4250:
    logg_regions = [[5100,5400]]
if teff_ini <= 4250:
    logg_regions = [[4730,4810]]
if teff_ini >= 5750 and teff_ini < 6250:
    #logg_regions = [[3850,4500]]
    logg_regions = [[3800,3900],[4100,4200],[5100,5400]]
if teff_ini >= 6250:
    logg_regions = [[3700,3900]]

### logg_regions = [[4500,5800]]
if teff_ini <= 5500:
    feh_regions = [[3900,4000],[4280,4320],[4450,4500]]
if teff_ini > 5500:
    feh_regions = [[3900,4250]]

### Define the regions used in flux spectra matching
if teff < 6000:
    teff_regions = [[3700,4730],[5400,5700]] #Use continuum
if teff >= 6000:
    teff_regions = [[3810,3855],[3900,4000],[4080,4130],[4330,4375],[4840,4880]] #Balmer series
#teff_regions = [[3800,5500]]

#logg_regions = [[]]
#teff_regions = [[3500,5900]]

##########################
### Start the analysis ###
##########################

### Change directory to reduced/
program_dir = os.getcwd() + "/" #Save the current working directory
os.chdir(file_path_reduced) #Change to ../reduced/ dir

### Load in spectra
norm_spectrum = functions.read_ascii("norm_" + file_name + ".dat")
norm_spectrum = functions.read_table(norm_spectrum)
norm_spectrum = transpose(array(norm_spectrum))

flux_spectrum = functions.read_ascii("fluxcal_" + file_name + ".dat")
flux_spectrum = functions.read_table(flux_spectrum)
flux_spectrum = transpose(array(flux_spectrum))
flux_spectrum = spectype_functions.normalise(flux_spectrum,flux_normalise_w1,flux_normalise_w2)


### Find shift
os.system("rm apshift*")

### Makesure keywpars is set at default
iraf.unlearn(iraf.keywpars)

iraf.filtpars.setParam("f_type","square",check=1,exact=1)
iraf.filtpars.setParam("cuton",50,check=1,exact=1)
iraf.filtpars.setParam("cutoff",2000,check=1,exact=1)

os.system("cp "+model_path_norm+"fits_files/"+ini_template_spectrum+".fits .")

run_fxcor("norm_"+ file_name,ini_template_spectrum+".fits","*","apshift",0,15,"gaussian")
vel_shift = functions.read_ascii("apshift.txt")
vel_shift = functions.read_table(vel_shift)
vel_shift = vel_shift[0][11]
if vel_shift == "INDEF":
    vel_shift = 0.0
if abs(vel_shift) > 500.:
    vel_shift = 0.0

os.system("rm "+ini_template_spectrum+".fits")
os.system("rm apshift*")
print "Velocity shift of ",vel_shift

### Correct shift
flux_wave = flux_spectrum[0]
flux_flux = flux_spectrum[1]
norm_wave = norm_spectrum[0]
norm_flux = norm_spectrum[1]

c = 3.0 * 10**5

norm_wave = norm_wave / ((vel_shift / c) + 1)

### Interpolate onto a 1A grid
master_flux_wave = arange(3700,5700,1.)
master_norm_wave = arange(4550,5900,1.)

flux_interp = interpolate.splrep(flux_wave,flux_flux,s=0)
flux_flux = interpolate.splev(master_flux_wave,flux_interp,der=0)
norm_interp = interpolate.splrep(norm_wave,norm_flux,s=0)
norm_flux = interpolate.splev(master_norm_wave,norm_interp,der=0)

######################################
### Start Chi^2 array calculations ###
######################################

os.system("mkdir spectype_plots")
os.system("rm spectype_plots/" + object_name + "*.pdf")

###################################################
### Perform logg-weighted spectrum calculations ###
###################################################
print "Calculating logg weighted rms"

rms_logg = zeros(len(teff_table_list))

count = 1
for region in logg_regions:
    w1 = region[0]
    w2 = region[1]
    if w1 < 4550:
        folder = model_path_flux
        input_wave = master_flux_wave
        input_spec = flux_flux
    else:
        folder = model_path_norm
        input_wave = master_norm_wave
        input_spec = norm_flux

    rms = array(loop_input_spectrum(input_wave,input_spec,folder,teff_space,logg_space,feh_space,w1,w2,True))
    rms_logg = rms_logg + rms
    count = count + 1

rms_logg = rms_logg / float(count)
i = find_min_index(rms_logg)
print teff_table_list[i],logg_table_list[i],feh_table_list[i],rms_logg[i]

# rms_logg_table = transpose([teff_table_list,logg_table_list,feh_table_list,rms_logg])

# output_rms_table = open("temp_rms_table","w")
# functions.write_table(rms_logg_table,output_rms_table)
# output_rms_table.close()

# plot_spectrum("temp_rms_table","fluxcal_"+file_name+".dat")

sys.exit()

##################################################
### Perform feh-weighted spectrum calculations ###
##################################################
print "Calculating feh weighted rms"

rms_feh = zeros(len(teff_table_list))

count = 1
for region in feh_regions:
    w1 = region[0]
    w2 = region[1]
    if w1 < 4550:
        folder = model_path_flux
        input_wave = master_flux_wave
        input_spec = flux_flux
    else:
        folder = model_path_norm
        input_wave = master_norm_wave
        input_spec = norm_flux

    rms = array(loop_input_spectrum(input_wave,input_spec,folder,teff_space,logg_space,feh_space,w1,w2,True))
    rms_feh = rms_feh + rms
    count = count + 1

rms_feh = rms_feh / float(count)
i = find_min_index(rms_feh)
print teff_table_list[i],logg_table_list[i],feh_table_list[i],rms_feh[i]

# rms_feh_table = transpose([teff_table_list,logg_table_list,feh_table_list,rms_feh])

# output_rms_table = open("temp_rms_table","w")
# functions.write_table(rms_feh_table,output_rms_table)
# output_rms_table.close()

# plot_spectrum("temp_rms_table","fluxcal_"+file_name+".dat")

###############################################################################
### Calculate the corresponding chisq array for a range of reddening values ###
###############################################################################
print "Calculating teff weighted rms"

reddening_chisq_list = []

### Change directory to reduced/deredden/
os.chdir(file_path_reduced + "deredden/") #Change to ../reduced/deredden dir

### Determine and create reddening loop
os.system("ls *" + string.split(file_name,".")[0] + "*.dat > reddening_list")
reddening_list = functions.read_ascii("reddening_list")
os.system("rm reddening_list")
os.system("rm *rms_table")

reddening_values = []
reddening_rms = []

for flux_spectrum in reddening_list:

    reddening = float(string.split(flux_spectrum,"_")[1])
    reddening_values.append(reddening)

    print "Trying reddening value E(B-V) = " + str(reddening)

    ### Load in flux spectrum of different reddening
    flux_spectrum = functions.read_ascii(flux_spectrum)
    flux_spectrum = functions.read_table(flux_spectrum)
    flux_spectrum = transpose(array(flux_spectrum))
    flux_spectrum = spectype_functions.normalise(flux_spectrum,flux_normalise_w1,flux_normalise_w2)

    ### Correct shift
    flux_wave = flux_spectrum[0]
    flux_flux = flux_spectrum[1]

    c = 3.0 * 10**5

    flux_wave = flux_wave / ((vel_shift / c) + 1)

    ### Interpolate onto a 1A grid
    flux_interp = interpolate.splrep(flux_wave,flux_flux,s=0)
    flux_flux = interpolate.splev(master_flux_wave,flux_interp,der=0)

    rms_teff = zeros(len(teff_table_list))
    count = 1
    for region in teff_regions:
        rms = array(loop_input_spectrum(master_flux_wave,flux_flux,model_path_flux,teff_space,logg_space,feh_space,region[0],region[1],True))
        rms = (rms + rms_logg + rms_feh) / 3.
        rms_teff = rms_teff + rms
        count = count+1
    
    rms_teff = rms_teff / float(count)

    i = find_min_index(rms_teff)
    print teff_table_list[i],logg_table_list[i],feh_table_list[i],rms_teff[i]

    rms_red_table = transpose([teff_table_list,logg_table_list,feh_table_list,rms])

    output_rms_table = open(str(reddening)+"_rms_table","w")
    functions.write_table(rms_red_table,output_rms_table)
    output_rms_table.close()

    reddening_rms.append(min(rms_teff))

###########################
### Find best reddening ###
###########################

for i in range(len(reddening_values)):
    if reddening_rms[i] == min(reddening_rms):
        best_reddening = reddening_values[i]
        print best_reddening
        break

plot_spectrum(str(best_reddening)+"_rms_table",reddening_list[0])
