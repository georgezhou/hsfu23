### Load python modules
import pyfits
from numpy import *
import string
import sys
import os
import functions
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

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
        if dist <= float(no_apertures):
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

interactive = functions.read_config_file("INTERACT")

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
print xpos,ypos
## xpos is image slice no.
### ypos is yaxis position on an image slice

### Now find no_apertures image slices in order of brightness
xsequence = find_required_apertures(transpose(spatial_image)[ypos],xpos)

stellar_apertures = open(file_path_temp + "stellar_apertures.txt","w")
for i in xsequence:
    stellar_apertures.write(str(i) + "\n")
stellar_apertures.close()

os.system("rm " + file_path_reduced + "spatial_" + file_name + ".pdf")

###################
### Plot figure ###
###################

plt.clf()
plt.figure(figsize=(17.25,6))
plt.contourf(log10(spatial_image))
p, = plt.plot(ypos,xpos,color="red",linestyle="None",marker="+",markersize=100)

### If interactive, allow user to define image slice
if interactive=="true":

    axcolor = 'lightgoldenrodyellow'
    ax_y = plt.axes([0.16, 0.05, 0.7, 0.03], axisbg=axcolor)
    ax_x  = plt.axes([0.16, 0.0, 0.7, 0.03], axisbg=axcolor)

    yval = Slider(ax_y,'yval', 0., 38., valinit=ypos)
    xval = Slider(ax_x,'xval', 0., 10., valinit=xpos)

    def update(val):
        ypos = int(round(yval.val))
        xpos = int(round(xval.val))
        p.set_xdata(ypos)
        p.set_ydata(xpos)
        plt.draw()
    xval.on_changed(update)
    yval.on_changed(update)

    bottonax = plt.axes([0.05, 0.5, 0.05, 0.04])
    button = Button(bottonax, 'Set', color=axcolor, hovercolor='0.975')

    def setpos(event):
        xpos = int(round(xval.val))
        ypos = int(round(yval.val))
        print "New position:",xpos,ypos
        os.system("rm " + file_path_reduced + "spatial_" + file_name + ".pdf")
        plt.savefig(file_path_reduced + "spatial_" + file_name + ".pdf")

        ### Save the xpos
        xsequence = find_required_apertures(transpose(spatial_image)[ypos],xpos)

        stellar_apertures = open(file_path_temp + "stellar_apertures.txt","w")
        for i in xsequence:
            stellar_apertures.write(str(i) + "\n")
        stellar_apertures.close()

    button.on_clicked(setpos)

    plt.show()

else:
    plt.savefig(file_path_reduced + "spatial_" + file_name + ".pdf")

