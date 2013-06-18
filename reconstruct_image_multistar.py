### Load python modules
import pyfits
from numpy import *
import string
import sys
import os
import functions
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import detect_stars


def fit(input_x,input_y,output_x):

    niter = 10
    sigma = 2.0

    for i in range(niter):
        # plt.clf()
        # plt.scatter(input_x,input_y,s=2,color="r",edgecolor="r")

        f = polyfit(input_x,input_y,1)
        output_y = polyval(f,output_x)
        model_y = polyval(f,input_x)

        ### Perform sigma clipping
        diff = model_y - input_y
        stdev = std(diff)
        
        input_x_temp = []
        input_y_temp = []
        for i in range(len(diff)):
            if abs(diff[i]) > sigma * stdev:
                #input_y_temp.append(model_y[i])
                #input_y_temp.append(NaN)
                pass

            else:
                input_x_temp.append(input_x[i])
                input_y_temp.append(input_y[i])

        input_y = array(input_y_temp)
        input_x = array(input_x_temp)

        # plt.scatter(input_x,input_y,color="b",edgecolor="b")
        # plt.plot(output_x,output_y,"k")
        # plt.show()
    return output_y

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
no_stars = int(functions.read_config_file("NO_STARS"))
se_path = functions.read_param_file("SE_PATH")
program_dir = os.getcwd()+"/"

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
object_notes = hdulist[0].header['NOTES']
hdulist.close()

if object_notes in ["RV Standard","SpecPhot","Smooth","Sky","Flat","Ne-Ar"]:
    no_stars = 1

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

### Remove spatial gradient

# ### Remove horizontal gradient

x = []
for i in range(len(spatial_image)):
    x.append(median(spatial_image[i]))
x = array(x)
xmodel = fit(arange(len(x)),x,arange(len(x)))
for i in range(len(spatial_image)):
    spatial_image[i] = spatial_image[i] - xmodel[i]

### Remove vertical gradient
spatial_image = transpose(spatial_image)
x = []
for i in range(len(spatial_image)):
    x.append(median(spatial_image[i]))
x = array(x)
xmodel = fit(arange(len(x)),x,arange(len(x)))
for i in range(len(spatial_image)):
    spatial_image[i] = spatial_image[i] - xmodel[i]

spatial_image = transpose(spatial_image)

### Write to file

os.system("rm image.fits")
os.system("cp "+program_dir+"default.sex .")
os.system("cp "+program_dir+"default.param .")

hdu = pyfits.PrimaryHDU(spatial_image)
hdulist = pyfits.HDUList([hdu])
hdulist.writeto("image.fits")

detect_stars.detect_stars("image.fits",se_path,no_stars)

os.system("cat master_coo")
coo = functions.read_ascii("master_coo")
coo = functions.read_table(coo)

print coo



#sys.exit()

# xpos = coo[0][1]-1
# ypos = coo[0][0]-1

# print xpos,ypos
# ## xpos is image slice no.
# ### ypos is yaxis position on an image slice

# ### Now find no_apertures image slices in order of brightness
# xsequence = find_required_apertures(transpose(spatial_image)[ypos],xpos)

# stellar_apertures = open(file_path_temp + "stellar_apertures.txt","w")
# for i in xsequence:
#     stellar_apertures.write(str(i) + "\n")
# stellar_apertures.close()

os.system("rm " + file_path_reduced + "spatial_" + file_name + ".pdf")

###################
### Plot figure ###
###################
#plt.clf()
plt.figure(figsize=(17.25,6))
#plt.contourf(log10(spatial_image-spatial_image.min()+1))
plt.imshow(log10(spatial_image-spatial_image.min()+1),interpolation="nearest")
for i in range(len(coo)):
    #plt.scatter(coo[i][0]-1,coo[i][1]-1)
    chrtext = i+ord("A")
    plt.text(coo[i][0]-1,coo[i][1]-1,chr(chrtext),horizontalalignment="center",verticalalignment="center")


#plt.savefig(file_path_reduced + "spatial_" + file_name + ".pdf")
#plt.show()

# if interactive == "true":
#     print "current stars:"
#     for i in range(len(coo)):
#         print [i,coo[i][0]-1,coo[i][1]-1]

#     print "Input stars in the same format, one by one"

#     plt.clf()
#     plt.figure(figsize=(17.25,6))
#     #plt.contourf(log10(spatial_image-spatial_image.min()+1))
#     #p, = plt.plot(ypos,xpos,color="red",linestyle="None",marker="+",markersize=100)
#     plt.imshow(log10(spatial_image-spatial_image.min()+1),interpolation="nearest")
#     for i in range(len(coo)):
#         plt.scatter(coo[i][0]-1,coo[i][1]-1)

#     plt.show()

#     query = "[]"
#     while query != "Done":
#         query = raw_input("[star#,x,y] OR Done: ")
#         try:
#             query = eval(query)
#             if query[0]+1 > len(coo):
#                 print "adding"
#             else:
#                 print "updating"


#         except:
#             pass


### If interactive, allow user to define image slice
if interactive=="true":

    p, = plt.plot(coo[i][0]-1,coo[i][1]-1,color="red",linestyle="None",marker="+",markersize=100)


    axcolor = 'lightgoldenrodyellow'
    ax_y = plt.axes([0.16, 0.05, 0.7, 0.03], axisbg=axcolor)
    ax_x  = plt.axes([0.16, 0.0, 0.7, 0.03], axisbg=axcolor)

    yval = Slider(ax_y,'yval', 0., 38., valinit=coo[i][0]-1)
    xval = Slider(ax_x,'xval', 0., 10., valinit=coo[i][1]-1)

    def update(val):
        ypos = yval.val
        xpos = xval.val
        p.set_xdata(ypos)
        p.set_ydata(xpos)
        plt.draw()
    xval.on_changed(update)
    yval.on_changed(update)

    bottonax = plt.axes([0.05, 0.5, 0.05, 0.04])
    button = Button(bottonax, 'Set', color=axcolor, hovercolor='0.975')

    cnt = 0

    def setpos(event):
        global cnt
        xpos = xval.val
        ypos = yval.val
        print "Star"+str(cnt),ypos,xpos

        if cnt + 1 <= len(coo):
            print "updating existing star"
            coo[cnt][0] = ypos+1
            coo[cnt][1] = xpos+1

        else:
            print "Adding new star"
            coo.append([ypos+1,xpos+1,0,0,0,0,0])

        cnt = cnt+1


    button.on_clicked(setpos)

    plt.show()


    plt.clf()
    plt.figure(figsize=(17.25,6))
    #plt.contourf(log10(spatial_image-spatial_image.min()+1))
    plt.imshow(log10(spatial_image-spatial_image.min()+1),interpolation="nearest")
    for i in range(len(coo)):
        #plt.scatter(coo[i][0]-1,coo[i][1]-1)
        chrtext = i+ord("A")
        plt.text(coo[i][0]-1,coo[i][1]-1,chr(chrtext),horizontalalignment="center",verticalalignment="center")


    os.system("rm " + file_path_reduced + "spatial_" + file_name + ".pdf")
    plt.savefig(file_path_reduced + "spatial_" + file_name + ".pdf")


    o = open("master_coo","w")
    functions.write_table(coo,o)
    o.close()

    print "Coordinate file updated"
    os.system("cat master_coo")

else:
    plt.savefig(file_path_reduced + "spatial_" + file_name + ".pdf")

