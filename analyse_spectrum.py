import pyfits
from numpy import *
import string
import sys
import os
import functions
#import matplotlib.pyplot as plt

###################
### Description ###
###################

### Open fits spectrum
### Extract exposure information and record
### This is used as an analysis tool to determine how well the star was recorded

### usage: python analyse_spectrum.py file_path file_name

#################
### Functions ###
#################

########################
### Start of program ###
########################
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

### Read in the correct image slice to analyse
slices = functions.read_ascii(file_path_temp + "stellar_apertures.txt")
slices = functions.read_table(slices)
slice_to_use = slices[0][0]

image_data = pyfits.getdata(file_path_temp + str(int(slice_to_use)) + "_" + file_name)
slice_data = image_data

### Chop the 200 columns in the centre of the image
image_data = transpose(image_data)
image_data = image_data[len(image_data)/2 - 100:len(image_data)/2 + 100]
image_data = transpose(image_data)
median_list = []
for i in image_data:
    median_list.append(median(i))

for i in range(len(median_list)):
    if median_list[i] == max(median_list):
        max_column = i
        break

column_data = slice_data[i]
column_data = sort(column_data)
column_data = column_data[len(column_data)-200:]

spectrum_maximum = median(column_data)

### Load the fits header information 
hdulist = pyfits.open(file_path + file_name)
object_name = hdulist[0].header["OBJECT"]
JD = hdulist[0].header["MJD-OBS"]
exptime = hdulist[0].header["EXPTIME"]
hdulist.close()

### Calculate signal/noise
i_signal = spectrum_maximum
i_sky = 0.03
i_dark = 0.001
i_RN = 5
gain = 0.9

signal_noise = (gain*spectrum_maximum) / (sqrt((i_signal*gain) + (i_sky * exptime)**2 + (i_dark* exptime)**2 + i_RN**2))
signal_noise = signal_noise * 2.3 ### convert from sn/pixel to sn/resolution element

print "The signal to noise is ",signal_noise

### Write information to table
### Format
### file_name object_name HJD max S/N flag(1=saturate)
info = [[file_name,object_name,JD,exptime,spectrum_maximum,signal_noise]]

### Write to log file
if os.path.exists(file_path_reduced + "image_quality.dat"):
	image_quality_file = functions.read_ascii(file_path_reduced + "image_quality.dat")
	image_quality_file = functions.read_table(image_quality_file)

	for image in image_quality_file:
		if not image[0] == file_name and not image[1] == object_name:
			info.append(image)

image_quality = open(file_path_reduced + "image_quality.dat","w")
functions.write_table(info,image_quality)
image_quality.close()
