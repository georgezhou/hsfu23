import sys
import os
import string
from numpy import *
import functions
import matplotlib.pyplot as plt
from scipy import optimize
import spectype_numerical_functions

######################################
### Functions for spectype_main.py ###
######################################

### Normalise input spectrum
def normalise(spectrum,start_lambda,end_lambda):
    norm_region = spectype_numerical_functions.chop_spectrum(spectrum,start_lambda,end_lambda)
    norm_factor = mean(norm_region[1])
    spectrum[1] = spectrum[1] / norm_factor
    return spectrum

### Find min
### Returns position(i) for the min
def find_min(input_list):
    i = 0
    for i in range(len(input_list)):
        if input_list[i] == min(input_list):
            break
    return i

### Plot spectrum
def plot_spectrum(spectrum):
    spectrum = transpose(spectrum)
    plt.plot(spectrum[0],spectrum[1])

### Shift spectrum to take away RV shift effect
def shift_spectrum(data_spectrum,template_spectrum,shift):
    if shift == 0:
        return data_spectrum,template_spectrum
    else:
        data_wave = data_spectrum[0]
        data_flux = data_spectrum[1]
        template_wave = template_spectrum[0]
        template_flux = template_spectrum[1]

        if shift < 0:
            shift = abs(shift)

            data_wave = data_wave[:len(data_wave)-shift]
            data_flux = data_flux[:len(data_flux)-shift]

            template_wave = data_wave
            template_flux = template_flux[shift:]

            shift = -1 * shift

        if shift > 0:
            shift = abs(shift)
            data_wave = data_wave[shift:]
            data_flux = data_flux[shift:]

            template_wave = data_wave
            template_flux = template_flux[:len(template_flux) - shift]

        data_spectrum = transpose(array([data_wave,data_flux]))
        template_spectrum = transpose(array([template_wave,template_flux]))

        return data_spectrum,template_spectrum

### crop array 
def chop_array(x_list,y_list,input_array,x,y,x_rad,y_rad):
    x_min = x - x_rad
    x_max = x + x_rad

    y_min = y - y_rad
    y_max = y + y_rad

    ### Check to make sure the boundaries are not out of bounds
    if x_min < min(x_list):
        x_min = min(x_list)
    if x_max > max(x_list):
        x_max = max(x_list)
    if y_min < min(y_list):
        y_min = min(y_list)
    if y_max > max(y_list):
        y_max = max(y_list)

    ### Find boundaries:
    for i in range(len(x_list)):
        if x_list[i] == x_min:
            x_min_pos = i
        if x_list[i] == x_max:
            x_max_pos = i
            break
    for i in range(len(y_list)):
        if y_list[i] == y_min:
            y_min_pos = i
        if y_list[i] == y_max:
            y_max_pos = i
            break
    
    ### ChopChop !!!
    x_list = x_list[x_min_pos:x_max_pos+1]
    y_list = y_list[y_min_pos:y_max_pos+1]

    output_array = input_array[y_min_pos:y_max_pos+1,x_min_pos:x_max_pos+1]
    return x_list,y_list,output_array

### Round value
def round_value(value,round_step):
    value = value / round_step
    value = round(value)
    value = value * round_step
    return value

### Find the minimum of a 2D array
def find_2d_min(input_array):
    min_array = input_array.min()

    for i in range(len(input_array)):
        found_min = False
        for j in range(len(input_array[i])):
            if input_array[i,j] == min_array:
                found_min = True
                break
        if found_min:
            break
    return j,i

def plot_isochrones(program_dir,style,lwidth):
    isochrones = functions.read_ascii(program_dir + "isochrone.dat")
    isochrones = functions.read_table(isochrones)

    isochrones = isochrones[:len(isochrones)-1]

    isochrones = transpose(isochrones)
    teff = 10**array(isochrones[4])
    logg = array(isochrones[5])

    plt.plot(teff,logg,style,linewidth=lwidth)

def plot_contour(object_name,teff_space,logg_space,chisq_space,teff_min,teff_err,logg_min,logg_err,iso_dir):

    plt.clf()
    plot_isochrones(iso_dir,"k-",0.5)
    contour_plot = plt.contourf(teff_space,logg_space,chisq_space,25,cmap=plt.get_cmap("jet"))
    plt.errorbar(teff_min,logg_min,xerr=teff_err,yerr=logg_err,color="r",marker="o")
    #plt.scatter(teff_min,logg_min,s=50,color="r",marker="x")
    #plt.text(teff_min,logg_min,"+",size="xx-large",color="r")
    cbar = plt.colorbar(contour_plot)
    #cbar.ax.set_ylabel("Log(Chi^2)")
    cbar.ax.set_ylabel("Probability")
    plt.xlabel("T_eff")
    plt.ylabel("logg")
    plt.xlim(max(teff_space),min(teff_space))
    plt.ylim(max(logg_space),min(logg_space))
    plt.title(object_name +" Teff=" + str(int(round(teff_min))) + " logg=" + str(round(logg_min,1)))
    #plt.show()
    plt.savefig("spectype_plots/" + object_name + "_contour.pdf")

def normalise_array(input_array):
    
    input_array = input_array - input_array.min()
    input_array = input_array / input_array.max()

    return input_array

def collapse_array(input_array):
    array_to_list = []
    for line in input_array:
        array_to_list = array_to_list + list(line)
    return array_to_list

def gen_gaussian(height, center_x, center_y, width_x, width_y):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y: height*exp(-(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

def moments(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    X, Y = indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = sqrt(abs((arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = sqrt(abs((arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max()
    return height, x, y, width_x, width_y

def fitgaussian(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit"""
    params = moments(data)
    errorfunction = lambda p: ravel(gen_gaussian(*p)(*indices(data.shape)) - data)
    p, success = optimize.leastsq(errorfunction, params)
    return p
