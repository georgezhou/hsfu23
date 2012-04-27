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
        template_spectrum=spectype_functions.normalise(template_spectrum,flux_normalise_w1,flux_normalise_w2)

    #template_spectrum = spectype_functions.normalise(template_spectrum,start_lambda,end_lambda)
    #data_spectrum = spectype_functions.normalise(data_spectrum,start_lambda,end_lambda)

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

    #template_spectrum = spectype_functions.normalise(template_spectrum,start_lambda,end_lambda)
    #data_spectrum = spectype_functions.normalise(data_spectrum,start_lambda,end_lambda)

    ### Chop both spectra
    data_region = spectype_numerical_functions.chop_spectrum(data_spectrum,start_lambda,end_lambda)
    template_region = spectype_numerical_functions.chop_spectrum(template_spectrum,start_lambda,end_lambda)

    ### Conform template spectrum to data spectrum -> same wavelength scale
    template_region = spectype_numerical_functions.conform_spectrum(data_region,template_region)

    ### Find shift

    data_region_shifted,template_region_shifted = spectype_functions.shift_spectrum(data_region,template_region,shift)
    chisq = spectype_numerical_functions.chisq(data_region_shifted,template_region_shifted)

    # plt.clf()
    # plt.plot(data_region_shifted[0],data_region_shifted[1])
    # plt.plot(template_region_shifted[0],template_region_shifted[1])
    # plt.title(data_type + " " + str(teff) + " " + str(logg) + " " + str(feh) +" " + str(chisq))
    # plt.show()

    return chisq

### For a particular data spectrum, loop over allowable teff, logg, feh to
### find chisq array. Minimise to find best fitting values
def loop_teff_logg(data_type,data_spectrum,teff,logg,feh,start_lambda,end_lambda):

    teff_space = []
    logg_space = []
    chisq_space = []

    teff_min = teff - 1000
    teff_max = teff + 1000

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
    #chisq_space = exp(- chisq_space **2 / 2)
    #chisq_space = spectype_functions.normalise_array(chisq_space)
    # print chisq_space

    ### Crop the chisq space immediately surrounding the absolute min
    teff_space_cropped,logg_space_cropped,cropped_space =spectype_functions.chop_array(teff_space,logg_space,chisq_space,teff_min,logg_min,500,1.0)
    #cropped_space = log(cropped_space)
    cropped_space = -1 *(cropped_space - cropped_space.max())

    ### Use scipy to fit a least sq 2D gaussian to the cropped region
    gauss_fit = spectype_functions.fitgaussian(cropped_space)
    gauss_height = gauss_fit[0]
    gauss_width_x = gauss_fit[3]
    gauss_width_y = gauss_fit[4]

    ### Check if the gaussian fit makes sense
    if gauss_height > 100 or gauss_width_x > 20 or gauss_width_y > 20:
        gauss_height = 0.00001
        gauss_width_x = 99999.
        gauss_width_y = 99999.

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
    for region in region_list:
        if data_type == "norm":
            teff_space,logg_space,chisq_space,gauss_height,gauss_width_x,gauss_width_y=loop_teff_logg("norm",norm_spectrum,teff,logg,feh,region[0],region[1])
        if data_type == "flux":
            teff_space,logg_space,chisq_space,gauss_height,gauss_width_x,gauss_width_y=loop_teff_logg("flux",flux_spectrum,teff,logg,feh,region[0],region[1])
        chisq_space_list.append(chisq_space)
        x_weights.append(gauss_width_x)
        y_weights.append(gauss_width_y)
        height_weights.append(gauss_height)

    x_weights = array(x_weights)
    y_weights = array(y_weights)
    height_weights = array(height_weights)

    weights = (1./3.)*((height_weights**2/sum(height_weights**2))+(1/x_weights**2)/sum(1/x_weights**2)+(1/y_weights**2)/sum(1/y_weights**2))
    #weights=((height_weights**2/sum(height_weights**2))+(sum(x_weights**2)/x_weights**2)+(sum(y_weights**2)/y_weights**2))

    #print weights

    master_chisq = zeros([len(chisq_space_list[0]),len(chisq_space_list[0][0])])
    for i in range(len(chisq_space_list)):
        chisq_space_list[i] = chisq_space_list[i] * weights[i]
        master_chisq = master_chisq + chisq_space_list[i]
    
    probability = exp(-1 * master_chisq / 2)
    probability = probability - probability.min()
    probability = probability / probability.max()
    #probability = probability / probability.sum()

    #spectype_functions.plot_contour(object_name,teff_space,logg_space,probability,5000,0,4.0,0,program_dir)

    return probability

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

print "Initial estimate of teff, logg: ",str(teff_ini),str(logg_ini)

### Change directory to reduced/
program_dir = os.getcwd() + "/" #Save the current working directory
os.chdir(file_path_reduced) #Change to ../reduced/ dir

### Load in spectra
flux_spectrum = functions.read_ascii("fluxcal_" + file_name + ".dat")
flux_spectrum = functions.read_table(flux_spectrum)
flux_spectrum = transpose(array(flux_spectrum))
flux_spectrum = spectype_functions.normalise(flux_spectrum,flux_normalise_w1,flux_normalise_w2)

norm_spectrum = functions.read_ascii("norm_" + file_name + ".dat")
norm_spectrum = functions.read_table(norm_spectrum)
norm_spectrum = transpose(array(norm_spectrum))

print "Using specific regions for spectral typing"
### Check the temp and define which logg sensitive regions to use
#if teff_ini > 4750 and teff_ini < 5750:
if teff_ini > 4750 and teff_ini < 6250:
    #logg_regions = [[5140,5235]]
    logg_regions = [[5100,5400]]
if teff_ini <= 4750 and teff_ini > 4250:
    logg_regions = [[5100,5400]]
if teff_ini <= 4250:
    logg_regions = [[4730,4810]]
#if teff_ini >= 5750 and teff_ini < 6250:
    #logg_regions = [[3850,4500]]
#    logg_regions = [[3800,3900],[4100,4200],[5100,5400]]
if teff_ini >= 6250:
    logg_regions = [[3700,3900]]

### logg_regions = [[4500,5800]]

### Define the regions used in flux spectra matching
teff_regions = [[3700,4730],[5400,5700]]

#logg_regions = [[]]
#teff_regions = [[3500,5900]]
#################
### Make axes ###
#################

teff_space = []
logg_space = []

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
def gaussian_function(x,mu,sigma):
    value = exp(-(x-mu)**2 / (2*sigma**2))
    return value

master_norm_array = ones([len(logg_space),len(teff_space)])

if len(logg_regions[0]) > 0:

    for i in logg_regions:
        if i[0] >= 4500:
            master_norm_array = master_norm_array * calculate_chisq_from_input_regions("norm",norm_spectrum,teff_ini,logg_ini,feh_ini,[i])
        else:
            master_norm_array = master_norm_array * calculate_chisq_from_input_regions("flux",flux_spectrum,teff_ini,logg_ini,feh_ini,[i])

    ### Apply more weighting to the logg axis by multiply with a logg vector
    teff_pos_min,logg_pos_min = spectype_functions.find_2d_max(master_norm_array)
    teff_min = teff_space[teff_pos_min]
    logg_min = logg_space[logg_pos_min]

    ### Crop the chisq space immediately surrounding the absolute min
    teff_space_cropped,logg_space_cropped,cropped_space =spectype_functions.chop_array(teff_space,logg_space,master_norm_array,teff_min,logg_min,500,1.0)

    ### Use scipy to fit a least sq 2D gaussian to the cropped region
    gauss_fit = spectype_functions.fitgaussian(cropped_space)
    gauss_width_logg = gauss_fit[3]

    for i in range(len(master_norm_array)):
        weight = gaussian_function(i,logg_pos_min,gauss_width_logg)
        for j in range(len(master_norm_array[i])):
            #master_norm_array[i,j] = master_norm_array[i,j]
            master_norm_array[i,j] = master_norm_array[i,j]*weight
            #master_norm_array[i,j] = weight
            #master_norm_array[i,j] = max(master_norm_array[i])

    # plt.clf()
    # plt.contourf(teff_space,logg_space,master_norm_array,20,cmap=plt.get_cmap("jet"))
    # plt.scatter(teff_min,logg_min,s=200,color="r",marker="x")
    # plt.xlabel("T_eff")
    # plt.ylabel("logg")
    # plt.xlim(max(teff_space),min(teff_space))
    # plt.ylim(max(logg_space),min(logg_space))
    # plt.title("Master Norm Space " + object_name + " " + str(teff_ini))
    # plt.show()

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

count = 0
for flux_spectrum in reddening_list:

    reddening = float(string.split(flux_spectrum,"_")[1])
    reddening_values.append(reddening)

    print "Trying reddening value E(B-V) = " + str(reddening)

    ### Load in flux spectrum of different reddening
    flux_spectrum = functions.read_ascii(flux_spectrum)
    flux_spectrum = functions.read_table(flux_spectrum)
    flux_spectrum = transpose(array(flux_spectrum))
    flux_spectrum = spectype_functions.normalise(flux_spectrum,flux_normalise_w1,flux_normalise_w2)

    reddening_chisq_list.append(master_norm_array * calculate_chisq_from_input_regions("flux",flux_spectrum,teff_ini,logg_ini,feh_ini,teff_regions))
    #spectype_functions.plot_contour(object_name,teff_space,logg_space,reddening_chisq_list[count],5000,0,4.0,0,program_dir)
    count = count+1

################################
### Sum the reddening arrays ###
################################

### Find weights!
height= []
x = []
y = []
for chisq_space in reddening_chisq_list:
    ### Find min
    teff_min,logg_min = spectype_functions.find_2d_max(chisq_space)
    teff_min = teff_space[teff_min]
    logg_min = logg_space[logg_min]

    ### Crop the chisq space immediately surrounding the absolute min
    teff_space_cropped,logg_space_cropped,cropped_space =spectype_functions.chop_array(teff_space,logg_space,chisq_space,teff_min,logg_min,500,1.0)
    #cropped_space = log(cropped_space)
    #cropped_space = -1 *(cropped_space - cropped_space.max())

    ### Use scipy to fit a least sq 2D gaussian to the cropped region
    gauss_fit = spectype_functions.fitgaussian(cropped_space)
    gauss_height = gauss_fit[0]
    gauss_x = gauss_fit[1]
    gauss_y = gauss_fit[2]
    gauss_width_x = gauss_fit[3]
    gauss_width_y = gauss_fit[4]

    ### Check if the gaussian fit makes sense
    if gauss_height > 100 or abs(gauss_x) > 20 or abs(gauss_y) > 20 or gauss_width_x > 20 or gauss_width_y > 20:
        gauss_height = 0.000001
        gauss_x = 0
        guass_y = 0
        gauss_width_x = 99999.
        gauss_width_y = 99999.

    height.append(gauss_height)
    x.append(gauss_x)
    y.append(gauss_y)

# x_weights = array(x_weights)
# y_weights = array(y_weights)
# height_weights = array(height_weights)
# weights = (1./3.)*((height_weights**2/sum(height_weights**2))+(1/x_weights**2)/sum(1/x_weights**2)+(1/y_weights**2)/sum(1/y_weights**2))
# #weights=((height_weights**2/sum(height_weights**2))+(sum(x_weights**2)/x_weights**2)+(sum(y_weights**2)/y_weights**2))
# #print weights
# ### Weighted sum
# master_logg_teff =ones([len(reddening_chisq_list[0]),len(reddening_chisq_list[0][0])])

# for i in range(len(reddening_chisq_list)):
#     master_logg_teff = master_logg_teff * (reddening_chisq_list[i] **
#     weights[i])

for i in range(len(reddening_chisq_list)):
    if height[i] == max(height):
        master_logg_teff = reddening_chisq_list[i]
        best_reddening = reddening_values[i]
        break


#####################################
### Analysis of teff - logg space ###
#####################################

 ### Find absolute min
teff_min,logg_min = spectype_functions.find_2d_max(master_logg_teff)
teff_min_array_index = teff_min
logg_min_array_index = logg_min
teff_min = teff_space[teff_min]
logg_min = logg_space[logg_min]

print teff_min, logg_min

### Perform gaussian fit to the minimum
### Crop the chisq space immediately surrounding the absolute min
teff_space_cropped,logg_space_cropped,master_cropped_space=spectype_functions.chop_array(teff_space,logg_space,master_logg_teff,teff_min,logg_min,250,0.5)
#master_cropped_space = log(master_cropped_space)
#master_cropped_space = -1 *(master_cropped_space - master_cropped_space.max())

### Use scipy to fit a least sq 2D gaussian to the cropped region
gauss_fit = spectype_functions.fitgaussian(master_cropped_space)
#logg_err = 0.5*gauss_fit[3]
#teff_err = 250*gauss_fit[4]

def interpolate_min(space,minval):
    val1 = space[int(minval)]
    val2 = space[int(minval)+1]
    result = (val2-val1) * (minval - int(minval)) + val1
    return result

#teff_min = interpolate_min(teff_space_cropped,gauss_fit[2])
#logg_min = interpolate_min(logg_space_cropped,gauss_fit[1])

teff_min = min(teff_space_cropped) + gauss_fit[2] * 250
logg_min = min(logg_space_cropped) + gauss_fit[1] * 0.5 

if logg_min < 0.0:
    logg_min = 0.0
if logg_min > 5.0:
    logg_min = 5.0

print "Best fitting Teff is " + str(teff_min)
print "Best fitting Logg is " + str(logg_min)

### Also find best reddening
reddening_chisq_min_list = []
for chisq_space in reddening_chisq_list:
    reddening_chisq_min_list.append(chisq_space[logg_min_array_index,teff_min_array_index])
    #spectype_functions.plot_contour(object_name,teff_space,logg_space,chisq_space,teff_min,0,logg_min,0,program_dir)

# ### Calculate best reddening
# for i in range(len(reddening_values)):
#     if reddening_chisq_min_list[i] == max(reddening_chisq_min_list):
#         best_reddening = reddening_values[i]
#         break

print "The best reddening estimate is E(B-V) = " + str(best_reddening)

round_teff_min = int(spectype_functions.round_value(teff_min,250))
if round_teff_min < 3500:
    round_teff_min = 3500
if round_teff_min > 9000:
    round_teff_min = 9000

round_logg_min = spectype_functions.round_value(logg_min,0.5)
if round_logg_min < 0.0:
    round_logg_min = 0.0
if round_logg_min > 5.0:
    round_logg_min = 5.0
#############################
### Plotting logg vs teff ###
#############################
os.chdir(file_path_reduced)
#probability_array = log10(master_logg_teff)
probability_array = master_logg_teff
#probability_array = exp(-1* probability_array /2)
probability_array = probability_array / probability_array.sum()
spectype_functions.plot_contour(object_name,teff_space,logg_space,probability_array,teff_min,0,logg_min,0,program_dir)

######################
### Analyse [Fe/H] ###
######################
feh_region = [3900,5900]

### Load in flux spectrum of best reddening value
flux_spectrum = file_path_reduced + "deredden/deredden_"+str(best_reddening)+"_"+file_name+".dat"
flux_spectrum = functions.read_ascii(flux_spectrum)
flux_spectrum = functions.read_table(flux_spectrum)
flux_spectrum = transpose(array(flux_spectrum))
flux_spectrum = spectype_functions.normalise(flux_spectrum,flux_normalise_w1,flux_normalise_w2)

# ### Find shift
# shift  = find_shift("flux",flux_spectrum,round_teff_min,round_logg_min,0.0,min(flux_spectrum[0]),max(flux_spectrum[0]))

# feh_chisq_list = []
# feh_list = []
# feh = -2.5
# while feh <= 0.5:
#     feh_list.append(feh)
#     feh_chisq_list.append(test_template("flux",flux_spectrum,round_teff_min,round_logg_min,feh,min(flux_spectrum[0]),max(flux_spectrum[0]),shift))
#     feh = feh + 0.5

# ### Load in normalised spectrum and use that for feh determination
# shift =find_shift("norm",norm_spectrum,round_teff_min,round_logg_min,0.0,feh_region[0],feh_region[1])
# feh_chisq_list = []
# feh_list = []
# feh = -2.5
# while feh <= 0.5:
#     feh_list.append(feh)
#     feh_chisq_list.append(test_template("norm",norm_spectrum,round_teff_min,round_logg_min,feh,feh_region[0],feh_region[1],shift))
#     feh = feh + 0.5

### Load in the flux spectrum and use that for feh determination
shift =find_shift("flux",flux_spectrum,round_teff_min,round_logg_min,0.0,feh_region[0],feh_region[1])
feh_chisq_list = []
feh_list = []
feh = -2.5
while feh <= 0.5:
    feh_list.append(feh)
    feh_chisq_list.append(test_template("flux",flux_spectrum,round_teff_min,round_logg_min,feh,feh_region[0],feh_region[1],shift))
    feh = feh + 0.5

### Find best fitting feh
for i in range(len(feh_list)):
    if feh_chisq_list[i] == min(feh_chisq_list):
        feh_min = feh_list[i]

print "Best fitting [Fe/H] is " + str(feh_min)

plt.clf()
plt.plot(feh_list,feh_chisq_list)
plt.xlabel("[Fe/H]")
plt.ylabel("X^2")
plt.savefig("spectype_plots/" + object_name + "_feh.pdf")

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

#template_spectrum = "template_" + str(round_teff_min) + "_" + str(round_logg_min) + "_" + str(feh_min) +".dat"
template_spectrum = "template_" + str(round_teff_min) + "_" + str(round_logg_min) + "_0.0" +".dat"
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
plt.xlim(min(flux_wave)+200.,max(flux_wave)-200.)
plt.title(object_name +" Template Teff=" + str(int(round(teff_min))) + " logg=" + str(round(logg_min,1)) +" feh=" + str(feh_min) + " reddening=" + str(best_reddening))
plt.legend()
plt.savefig("spectype_plots/" + object_name + "_spectrum.pdf")
#plt.show()

### Log data into spectype.txt
spectype_log = open("spectype.txt","a")
entry = file_name + " " + object_name + " " + str(int(round(teff_min))) + " 0.0 " + str(round(logg_min,1)) + " 0.0 " + str(feh_min) + " 0.0\n"
spectype_log.write(entry)
spectype_log.close()

os.chdir(program_dir)
if functions.read_config_file("OPEN_RESULT_PDFS") == "true":
    os.system("xpdf "+file_path_reduced+"spectype_plots/"+object_name+"_spectrum.pdf &")
