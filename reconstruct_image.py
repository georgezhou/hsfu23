### Load python modules
import pyfits
from numpy import *
import string
import sys
import os
import functions
import matplotlib.pyplot as plt

###################
### Description ###
###################
### This program reconstructs the spatial image captured by WiFeS
### It then finds the star, marks pixels for extraction
### And marks pixels used for background subtraction

### Usage: reconstruct_image file_path file_name

#############
### To do ###
#############

### Will construct a user interface
### to allow the user to redesignate the 
### image slices where the star is located.

### This may be simply vim the file,
### or using matplotlib to move the crosshairs

#################
### Functions ###
#################

def find_max_in_array(data):
    ### Returns position of absolute max
    ### data needs to be a python array
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i,j] == max(max(i) for i in data):
                xpos = i
                ypos = j
    return xpos,ypos

def find_required_apertures(input_list,starting_pos):
    temp = []
    for i in range(len(input_list)):
        temp.append([i,input_list[i]])
    input_list = temp

    sequence = []
    input_list = functions.sort_array(input_list,1)
    n = 0
    i = 1
    while n <= no_apertures-1:
        dist = abs(input_list[len(input_list)-i][0] - starting_pos)
        if dist <= float(no_apertures) /2:
            sequence.append(input_list[len(input_list)-i][0])
            i = i+1
            n = n+1
        else:
            n = n
            i = i+1
    return sequence

########################
### Start of program ###
########################

### Read from config file
no_apertures = int(functions.read_config_file("NO_APERTURES"))

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

image_slices_list = functions.read_ascii(file_path_temp + "slice_" + file_name+".txt")
image_slices_list = functions.read_table(image_slices_list)
image_slices_list = image_slices_list[1:]

hdulist = pyfits.open(file_path + file_name)
object_name = hdulist[0].header['OBJECT']
hdulist.close()

os.chdir(file_path_temp)

########################################################
### Reconstruct array by reading in each image slice ###
########################################################

spatial_image = []
for image_slice in image_slices_list:
    row_image = pyfits.getdata(image_slice[0])
    row_values = []
    
    for i in row_image:
        row_values.append(median(i))

    for i in range(len(row_values),38):
        row_values.append(0)
    spatial_image.append(row_values)

spatial_image = array(spatial_image)

xpos,ypos = find_max_in_array(spatial_image)

## xpos is image slice no.
### ypos is yaxis position on an image slice

### Now find no_apertures image slices in order of brightness

#ysequence = find_required_apertures(spatial_image[xpos],ypos)
xsequence = find_required_apertures(transpose(spatial_image)[ypos],xpos)

stellar_apertures = open(file_path_temp + "stellar_apertures.txt","w")
for i in xsequence:
    stellar_apertures.write(str(i) + "\n")
stellar_apertures.close()

# star_spectra_pos = []
# for i in xsequence:
#     for j in ysequence:
#         star_spectra_pos.append([i,j])

# stellar_apertures = open(file_path_temp + "stellar_apertures.txt","w")
# functions.write_table(star_spectra_pos,stellar_apertures)
# stellar_apertures.close()

# ### Define the background regions used for extraction
# def find_background(input_list):
#     background = []
#     for i in range(len(input_list)):
#         if abs(input_list[i] - median(input_list)) < 0.1 * std(input_list):
#             background.append(int(i))
#     return background

# ybackground = []
# for i in xsequence:
#     ybackground_i = find_background(spatial_image[i])
#     ybackground_i = [list(ones(len(ybackground_i)) * i),ybackground_i]
#     ybackground_i = transpose(ybackground_i)
#     ybackground.extend(ybackground_i)

# background_apertures = open(file_path_temp + "background_apertures.txt","w")
# functions.write_table(ybackground,background_apertures)
# background_apertures.close()

# ################################################
# ### Create spatial plot for future reference ###
# ################################################

# def fill_positions(input_coords,input_color):
#     for i in input_coords:
#         plt.fill([i[1],i[1]+1,i[1]+1,i[1]],[i[0],i[0],i[0]+1,i[0]+1],color=input_color,alpha=0.5)

os.system("rm " + file_path_reduced + "spatial_" + file_name + ".pdf")

plt.clf()
plt.figure(figsize=(17.25,5))
plt.contourf(spatial_image)
plt.scatter(ypos,xpos,color="k",marker="+",s=20)
# fill_positions(star_spectra_pos,"k")
# fill_positions(ybackground,"white")

plt.title(file_name + " " + object_name)
plt.savefig(file_path_reduced + "spatial_" + file_name + ".pdf")
# plt.show()

