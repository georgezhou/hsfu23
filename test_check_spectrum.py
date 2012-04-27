import sys
import os
import string
from numpy import *
import functions
import spectype_functions
import spectype_numerical_functions
import matplotlib.pyplot as plt
import pyfits

file_name = "b0064.fits"
file_path = "/mimsy/george/wifes/15Mar2012/spectype/blue/"

best_reddening = 0.04842
teff = 6000
logg = 4.5
feh = 0.0

### Read from param and config files
model_path_flux = functions.read_param_file("MODEL_PATH_FLUX")
model_path_norm = functions.read_param_file("MODEL_PATH_NORM")

##########################
### Plot FLUX spectrum ###
##########################

flux_spectrum = "deredden_"+str(best_reddening)+"_"+file_name+".dat"
flux_spectrum = functions.read_ascii(file_path + "reduced/deredden/" +flux_spectrum)
flux_spectrum = functions.read_table(flux_spectrum)
flux_spectrum = transpose(array(flux_spectrum))
flux_spectrum = spectype_functions.normalise(flux_spectrum,4400.,4600.)

flux_wave = flux_spectrum[0]
flux_flux = flux_spectrum[1]

template_spectrum = "template_" + str(teff) + "_" + str(logg) + "_"+str(feh)+".dat"
template_spectrum = functions.read_ascii(model_path_flux + template_spectrum)
template_spectrum = functions.read_table(template_spectrum)
template_spectrum = transpose(array(template_spectrum))
template_spectrum = spectype_functions.normalise(template_spectrum,4400.,4600.)

template_wave = template_spectrum[0]
template_flux = template_spectrum[1]

plt.clf()
plt.plot(template_wave,template_flux,"g-",label="synthetic")
plt.plot(flux_wave,flux_flux,"b-",label="data",alpha=0.5)
plt.xlim(min(flux_wave),max(flux_wave))
plt.xlabel("Wavelength (A)")
plt.ylabel("Flux")
plt.xlim(min(flux_wave)+200.,max(flux_wave)-200.)
plt.title("Template Teff=" + str(teff) + " logg=" + str(logg) +" feh=" + str(feh) + " reddening=" + str(best_reddening))
plt.legend()
plt.show()

##########################
### Plot NORM spectrum ###
##########################

norm_spectrum = "norm_"+file_name+".dat"
norm_spectrum = functions.read_ascii(file_path + "reduced/" +norm_spectrum)
norm_spectrum = functions.read_table(norm_spectrum)
norm_spectrum = transpose(array(norm_spectrum))

norm_wave = norm_spectrum[0]
norm_flux = norm_spectrum[1]

template_spectrum = "template_" + str(teff) + "_" + str(logg) + "_"+str(feh)+".dat"
template_spectrum = functions.read_ascii(model_path_norm + template_spectrum)
template_spectrum = functions.read_table(template_spectrum)
template_spectrum = transpose(array(template_spectrum))

template_wave = template_spectrum[0]
template_flux = template_spectrum[1]

plt.clf()
plt.plot(template_wave,template_flux,"g-",label="synthetic")
plt.plot(norm_wave,norm_flux,"b-",label="data",alpha=0.5)
plt.xlim(min(norm_wave),max(norm_wave))
plt.xlabel("Wavelength (A)")
plt.ylabel("Normalised Flux")
plt.xlim(min(norm_wave)+200.,max(norm_wave)-200.)
#plt.xlim(4830,4900)
plt.title("Template Teff=" + str(teff) + " logg=" + str(logg) +" feh=" + str(feh) + " reddening=" + str(best_reddening))
plt.legend()
plt.show()
#plt.savefig("outputs/"+str(teff)+"_"+str(logg)+".pdf")
