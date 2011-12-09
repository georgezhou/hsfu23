import sys
import os
import string
from numpy import *
import functions
import spectype_functions
import spectype_numerical_functions
import matplotlib.pyplot as plt
import pyfits

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

### Find the pixel shift for best matching
### data_type is ("flux"/"norm")
def find_shift(data_type,data_spectrum,teff,logg,feh,start_lambda,end_lambda):
    ### Import the template spectrum
    template_spectrum = "template_" + str(teff) + "_" + str(logg) + "_" + str(feh) + ".dat"

    if data_type=="flux":
        template_spectrum = functions.read_ascii(model_path_flux + template_spectrum)
    if data_type=="norm":
        template_spectrum = functions.read_ascii(model_path_norm + template_spectrum)

    template_spectrum = functions.read_table(template_spectrum)
    template_spectrum = transpose(array(template_spectrum))

    if data_type=="flux":
        template_spectrum = spectype_functions.normalise(template_spectrum,flux_normalise_w1,flux_normalise_w2)

    ### Chop both spectra
    data_region = spectype_numerical_functions.chop_spectrum(data_spectrum,start_lambda,end_lambda)
    template_region = spectype_numerical_functions.chop_spectrum(template_spectrum,start_lambda,end_lambda)

    ### Conform template spectrum to data spectrum -> same wavelength scale
    template_region = spectype_numerical_functions.conform_spectrum(data_region,template_region)

    ### Find shift
    chisq_shift = []

    shift_limit = 20
    shift  = -1*shift_limit
    while shift <= shift_limit:
        data_region_shifted,template_region_shifted = spectype_functions.shift_spectrum(data_region,template_region,shift)
        chisq_shift.append(spectype_numerical_functions.chisq(data_region_shifted,template_region_shifted))
        shift = shift + 1

    chisq_min = spectype_functions.find_min(chisq_shift)
    best_shift = chisq_min - shift_limit
    return best_shift

def test_template(data_type,data_spectrum,teff,logg,feh,start_lambda,end_lambda,shift):
    ### Import a template spectrum - test
    template_spectrum = "template_" + str(teff) + "_" + str(logg) + "_" + str(feh) + ".dat"

    if data_type=="flux":
        template_spectrum = functions.read_ascii(model_path_flux + template_spectrum)
    if data_type=="norm":
        template_spectrum = functions.read_ascii(model_path_norm + template_spectrum)

    template_spectrum = functions.read_table(template_spectrum)
    template_spectrum = transpose(array(template_spectrum))

    if data_type=="flux":
        template_spectrum = spectype_functions.normalise(template_spectrum,flux_normalise_w1,flux_normalise_w2)

    ### Chop both spectra
    data_region = spectype_numerical_functions.chop_spectrum(data_spectrum,start_lambda,end_lambda)
    template_region = spectype_numerical_functions.chop_spectrum(template_spectrum,start_lambda,end_lambda)

    ### Conform template spectrum to data spectrum -> same wavelength scale
    template_region = spectype_numerical_functions.conform_spectrum(data_region,template_region)

    ### Find shift

    data_region_shifted,template_region_shifted = spectype_functions.shift_spectrum(data_region,template_region,shift)
    chisq = spectype_numerical_functions.chisq(data_region_shifted,template_region_shifted)

    return chisq

### For a particular data spectrum, loop over allowable teff, logg, feh to
### find chisq array. Minimise to find best fitting values
def loop_teff_logg(data_type,data_spectrum,teff,logg,feh,start_lambda,end_lambda):

    teff_space = []
    logg_space = []
    chisq_space = []

    teff_min = teff - 750
    teff_max = teff + 750

    if teff < 4500:
        teff_min = int(3500)

    if teff > 8000:
        teff_max = int(9000)

    shift = find_shift(data_type,data_spectrum,teff,logg,feh,start_lambda,end_lambda)

    ### Create grid
    teff_i = teff_min
    while teff_i <= teff_max:
        teff_space.append(teff_i)
        teff_i = teff_i + 250

    logg_i = 0.0
    while logg_i <= 5.0:
        logg_space.append(logg_i)
        logg_i = logg_i + 0.5

    teff_space = array(teff_space)
    logg_space = array(logg_space)

    (X,Y) = meshgrid(teff_space,logg_space)

    ### Create chisq array

    teff_i = teff_min
    while teff_i <= teff_max:
        logg_line = []
        logg_i = 0.0
        while logg_i <= 5.0:
            chisq_i = test_template(data_type,data_spectrum,teff_i,logg_i,0.0,start_lambda,end_lambda,shift)
            logg_line.append(chisq_i)
            logg_i = logg_i + 0.5
        chisq_space.append(logg_line)
        teff_i = teff_i + 250

    chisq_space = array(chisq_space)
    chisq_space = transpose(chisq_space)
    # chisq_space = spectype_functions.normalise_array(chisq_space)
    # chisq_space = log(chisq_space)

    ### Find min
    teff_min,logg_min = spectype_functions.find_2d_min(chisq_space)
    teff_min = teff_space[teff_min]
    logg_min = logg_space[logg_min]

    # ### Normalise the array
    # chisq_space = exp(- chisq_space **2 / 2)
    # chisq_space = spectype_functions.normalise_array(chisq_space)
    # print chisq_space

    ### Crop the chisq space immediately surrounding the absolute min
    teff_space_cropped,logg_space_cropped,cropped_space =spectype_functions.chop_array(teff_space,logg_space,chisq_space,teff_min,logg_min,250,1.0)
    cropped_space = log(cropped_space)
    cropped_space = -1 *(cropped_space - cropped_space.max())

    ### Use scipy to fit a least sq 2D gaussian to the cropped region
    gauss_fit = spectype_functions.fitgaussian(cropped_space)
    gauss_height = gauss_fit[0]
    gauss_width_x = gauss_fit[3]
    gauss_width_y = gauss_fit[4]
    
    # plt.clf()
    # plt.contourf(teff_space,logg_space,chisq_space,20,cmap=plt.get_cmap("jet"))
    # plt.scatter(teff_min,logg_min,s=50,color="r",marker="x")
    # plt.xlabel("T_eff")
    # plt.ylabel("logg")
    # plt.xlim(max(teff_space),min(teff_space))
    # plt.ylim(max(logg_space),min(logg_space))
    # plt.title(object_name +" " + str(start_lambda) + "-" + str(end_lambda) + "A, Teff=" + str(teff_min) + " logg=" + str(logg_min))
    # plt.show()

    return teff_space,logg_space,chisq_space,gauss_height,gauss_width_x,gauss_width_y

### Test a particular data_spectrum over a range of regions defined by
### region_list
### Region list format: [[w1,w2],[w1,w2]...]
def calculate_chisq_from_input_regions(data_type,data_spectrum,teff,logg,feh,region_list):
    ### Define list for chisq spaces
    chisq_space_list = []

    ### Define the weights lists
    x_weights=[]
    y_weights=[]
    height_weights = []

    ### For each region, calculate a chisq array and weights
    for region in logg_regions:
        teff_space,logg_space,chisq_space,gauss_height,gauss_width_x,gauss_width_y=loop_teff_logg("norm",norm_spectrum,teff,logg,feh,region[0],region[1])
        chisq_space_list.append(chisq_space)
        x_weights.append(gauss_width_x)
        y_weights.append(gauss_width_y)
        height_weights.append(gauss_height)

    x_weights = array(x_weights)
    y_weights = array(y_weights)
    height_weights = array(height_weights)

    weights = (1./3.)*((height_weights**2/sum(height_weights**2))+(1/x_weights**2)/sum(1/x_weights**2)+(1/y_weights**2)/sum(1/y_weights**2))
    master_chisq = zeros([len(chisq_space_list[0]),len(chisq_space_list[0][0])])
    for i in range(len(chisq_space_list)):
        chisq_space_list[i] = chisq_space_list[i] * weights[i]
        master_chisq = master_chisq + chisq_space_list[i]

    return master_chisq

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

program_dir = os.getcwd() + "/" #Save the current working directory

### Change directory to reduced/
os.chdir(file_path_reduced) #Change to ../reduced/ dir

### Find initial estimate of properties
hdulist = pyfits.open(file_path + file_name)
object_name = hdulist[0].header["OBJECT"]
hdulist.close()

teff_ini = 6000
logg_ini = 4.0
feh_ini = 0.0

### Load in spectra
flux_spectrum = functions.read_ascii("fluxcal_" + file_name + ".dat")
flux_spectrum = functions.read_table(flux_spectrum)
flux_spectrum = transpose(array(flux_spectrum))
flux_spectrum = spectype_functions.normalise(flux_spectrum,flux_normalise_w1,flux_normalise_w2)

norm_spectrum = functions.read_ascii("norm_" + file_name + ".dat")
norm_spectrum = functions.read_table(norm_spectrum)
norm_spectrum = transpose(array(norm_spectrum))

print "Using specific regions for spectral typing"
#logg_regions = [[4600,4750],[5140,5235]]
### Check the temp and define which logg regions to use
if teff_ini > 4500 and teff_ini < 6000:
    logg_regions = [[5140,5235]]
if teff_ini <= 4500:
    logg_regions = [[4730,4810],[5140,5235]]
if teff_ini >= 6000:
    logg_regions = [[5140,5235]]
    ### This is because the MgH feature is only visible for 
    ### Low temp stars

### Beyond 6000K, the Mgb regions is no longer that sensitive
### We use flux spectrum 
if teff_ini < 6000:
    teff_regions = [[3900,4500],[5500,5900]]
if teff_ini >= 6000:
    teff_regions = [[3850,3900],[3900,4500],[5500,5900]]

#################
### Make axes ###
#################

teff_space = []
logg_space = []

teff_min = teff_ini - 750
teff_max = teff_ini + 750

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

teff_space = array(teff_space)
logg_space = array(logg_space)

######################################
### Start Chi^2 array calculations ###
######################################

os.system("mkdir spectype_plots")
os.system("rm spectype_plots/" + object_name + "*.pdf")

##########################################################
### Calculate a master chisq array for normalised data ###
##########################################################

master_norm_array = calculate_chisq_from_input_regions("norm",norm_spectrum,teff_ini,logg_ini,feh_ini,logg_regions)

###############################################################################
### Calculate the corresponding chisq array for a range of reddening values ###
###############################################################################
reddening_chisq_list = []

### Change directory to reduced/deredden/
os.chdir(file_path_reduced + "deredden/") #Change to ../reduced/deredden dir

### Determine and create reddening loop
os.system("ls *" + string.split(file_name,".")[0] + "*.dat > reddening_list")
reddening_list = functions.read_ascii("reddening_list")
os.system("rm reddening_list")

reddening_values = []

for flux_spectrum in reddening_list:

    reddening = float(string.split(flux_spectrum,"_")[1])
    reddening_values.append(reddening)

    print "Trying reddening value E(B-V) = " + str(reddening)

    ### Load in flux spectrum of different reddening
    flux_spectrum = functions.read_ascii(flux_spectrum)
    flux_spectrum = functions.read_table(flux_spectrum)
    flux_spectrum = transpose(array(flux_spectrum))
    flux_spectrum = spectype_functions.normalise(flux_spectrum,flux_normalise_w1,flux_normalise_w2)

    reddening_chisq_list.append(master_norm_array + calculate_chisq_from_input_regions("flux",flux_spectrum,teff_ini,logg_ini,feh_ini,teff_regions))

################################
### Sum the reddening arrays ###
################################

### Find weights!
height_weights = []
x_weights = []
y_weights = []
for chisq_space in reddening_chisq_list:
    ### Find min
    teff_min,logg_min = spectype_functions.find_2d_min(chisq_space)
    teff_min = teff_space[teff_min]
    logg_min = logg_space[logg_min]

    ### Crop the chisq space immediately surrounding the absolute min
    teff_space_cropped,logg_space_cropped,cropped_space =spectype_functions.chop_array(teff_space,logg_space,chisq_space,teff_min,logg_min,250,1.0)
    cropped_space = log(cropped_space)
    cropped_space = -1 *(cropped_space - cropped_space.max())

    ### Use scipy to fit a least sq 2D gaussian to the cropped region
    gauss_fit = spectype_functions.fitgaussian(cropped_space)
    gauss_height = gauss_fit[0]
    gauss_width_x = gauss_fit[3]
    gauss_width_y = gauss_fit[4]

    height_weights.append(gauss_height)
    x_weights.append(gauss_width_x)
    y_weights.append(gauss_width_y)

x_weights = array(x_weights)
y_weights = array(y_weights)
height_weights = array(height_weights)
weights = (1./3.)*((height_weights**2/sum(height_weights**2))+(1/x_weights**2)/sum(1/x_weights**2)+(1/y_weights**2)/sum(1/y_weights**2))

### Weighted sum
master_logg_teff =zeros([len(reddening_chisq_list[0]),len(reddening_chisq_list[0][0])])

for i in range(len(reddening_chisq_list)):
    master_logg_teff = master_logg_teff + reddening_chisq_list[i] * weights[i]

#####################################
### Analysis of teff - logg space ###
#####################################
### Find min
teff_min,logg_min = spectype_functions.find_2d_min(master_logg_teff)
teff_min_array_index = teff_min
logg_min_array_index = logg_min
teff_min = teff_space[teff_min]
logg_min = logg_space[logg_min]

print "Best fitting Teff is " + str(teff_min)
print "Best fitting Logg is " + str(logg_min)

### Also find best reddening
reddening_chisq_min_list = []
for chisq_space in reddening_chisq_list:
    reddening_chisq_min_list.append(chisq_space[logg_min_array_index,teff_min_array_index])

### Calculate best reddening
for i in range(len(reddening_values)):
    if reddening_chisq_min_list[i] == min(reddening_chisq_min_list):
        best_reddening = reddening_values[i]
        break

print "The best reddening estimate is E(B-V) = " + str(best_reddening)

#############################
### Plotting logg vs teff ###
#############################
os.chdir(file_path_reduced)
spectype_functions.plot_contour(object_name,teff_space,logg_space,log10(master_logg_teff),teff_min,0,logg_min,0)

######################
### Analyse [Fe/H] ###
######################
### Load in flux spectrum of best reddening value
flux_spectrum = file_path_reduced + "deredden/deredden_"+str(best_reddening)+"_"+file_name+".dat"
flux_spectrum = functions.read_ascii(flux_spectrum)
flux_spectrum = functions.read_table(flux_spectrum)
flux_spectrum = transpose(array(flux_spectrum))
flux_spectrum = spectype_functions.normalise(flux_spectrum,flux_normalise_w1,flux_normalise_w2)

### Find shift
shift  = find_shift("flux",flux_spectrum,teff_min,logg_min,0.0,min(flux_spectrum[0]),max(flux_spectrum[0]))

feh_chisq_list = []
feh_list = []
feh = -2.5
while feh <= 0.5:
    feh_list.append(feh)
    feh_chisq_list.append(test_template("flux",flux_spectrum,teff_min,logg_min,feh,min(flux_spectrum[0]),max(flux_spectrum[0]),shift))
    feh = feh + 0.5

### Find best fitting feh
for i in range(len(feh_list)):
    if feh_chisq_list[i] == min(feh_chisq_list):
        feh_min = feh_list[i]

print "Best fitting [Fe/H] is " + str(feh_min)

########################################
### Plot data and model in same plot ###
########################################

### Load in spectra
flux_spectrum = "deredden_"+str(best_reddening)+"_"+file_name+".dat"
flux_spectrum = functions.read_ascii("deredden/" + flux_spectrum)
flux_spectrum = functions.read_table(flux_spectrum)
flux_spectrum = transpose(array(flux_spectrum))
flux_spectrum = spectype_functions.normalise(flux_spectrum,flux_normalise_w1,flux_normalise_w2)

flux_wave = flux_spectrum[0]
flux_flux = flux_spectrum[1]

template_spectrum = "template_" + str(teff_min) + "_" + str(logg_min) + "_" + str(feh_min) +".dat"
template_spectrum = functions.read_ascii(model_path_flux + template_spectrum)
template_spectrum = functions.read_table(template_spectrum)
template_spectrum = transpose(array(template_spectrum))
template_spectrum = spectype_functions.normalise(template_spectrum,flux_normalise_w1,flux_normalise_w2)

template_wave = template_spectrum[0]
template_flux = template_spectrum[1]

plt.clf()
plt.plot(template_wave,template_flux,"g-",label="synthetic")
plt.plot(flux_wave,flux_flux,"b-",label="data",alpha=0.5)
plt.xlim(min(flux_wave),max(flux_wave))
plt.xlabel("Wavelength (A)")
plt.ylabel("Flux")
plt.xlim(min(flux_wave),max(flux_wave))
plt.title(object_name +" Template Teff=" + str(teff_min) + " logg=" + str(logg_min) +" feh=" + str(feh_min) + " reddening=" + str(best_reddening))
plt.legend()
plt.savefig("spectype_plots/" + object_name + "_spectrum.pdf")
#plt.show()