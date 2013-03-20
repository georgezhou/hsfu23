from numpy import *
import sys
import string
import functions
import pyfits
import os
import matplotlib.pyplot as plt

###################
### Description ###
###################
### Calculate width and BIS of the CCF.

### Use the ccf derived from synthetic CC. Fit gaussian to CCF to approximate
### the FWHM. Calculate bisector inverse span according to Queloz et al. 2001.

### Save plot of CCF, save data into ascii file.

### usage: python analyse_ccf.py file_path file_name

#################
### Functions ###
#################
from scipy import optimize
def gaussian(height, center_x, center_y, width_x, width_y):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y:height*exp(-(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

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
    return abs(height), x, y, abs(width_x), abs(width_y)

def fitgaussian(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit"""
    params = moments(data)
    errorfunction = lambda p: ravel(gaussian(*p)(*indices(data.shape)) - data)
    p, success = optimize.leastsq(errorfunction, params)
    return p

def gaussian1d(height,centre,width,xmin,xmax):
    x_list = []
    xstep = abs(xmin-xmax)/100
    i = xmin
    while i <= xmax:
        x_list.append(i)
        i = i + xstep
    x_list = array(x_list)

    y_list = height * exp(-(x_list - centre)**2 / (2 * (width)**2))
    return x_list,y_list


def find_nearest_point(input_list,input_value):
    input_list = array(input_list)
    dist_list = abs(input_list - input_value)
    for i in range(len(dist_list)):
        if dist_list[i] == min(dist_list):
            break
    return i

def interpolate(x_list,y_list,yvalue,direction):
    ### direction 1 ->
    ### direction 0 <-
    nearest_pos = find_nearest_point(y_list,yvalue)

    if direction == 1:
        if (y_list[nearest_pos] > yvalue or nearest_pos == 0) and not nearest_pos == len(x_list)-1:
            next_nearest_pos = nearest_pos + 1
        else:
            next_nearest_pos = nearest_pos - 1
        
    if direction == 0:
        if y_list[nearest_pos] > yvalue or nearest_pos == len(x_list)-1:
            next_nearest_pos = nearest_pos - 1
        else:
            next_nearest_pos = nearest_pos + 1

    x1 = x_list[nearest_pos]
    y1 = y_list[nearest_pos]

    x2 = x_list[next_nearest_pos]
    y2 = y_list[next_nearest_pos]

    xvalue = (x2 * y1 - x1 * y2 + x1 * yvalue - x2 * yvalue) / (y1 - y2)

    return xvalue

def monotonicize(x_list,y_list,direction):
    ### direction 1 ->
    ### direction 0 <-

    if direction == 1:
        i = 1
        #cutoff = -1
        cutoff = len(x_list)
        while i < len(x_list):
            y_list_prev = y_list[i-1]
            if y_list[i] >= y_list_prev:
                cutoff = i-1
                i = len(x_list)
            i = i + 1
        x_list = x_list[:cutoff]
        y_list = y_list[:cutoff]
        
    if direction == 0:
        i = len(x_list)-2
        #cutoff = len(x_list)-1
        cutoff = 0
        while i >= 0:
            y_list_prev = y_list[i+1]
            if y_list[i] >= y_list_prev:
                cutoff = i+1
                i = -1
            i = i - 1
        x_list = x_list[cutoff:]
        y_list = y_list[cutoff:]

    return x_list,y_list

def bisector_analysis(x_list,y_list,height,centre,width):
    #height_step = (max(y_list)-min(y_list)) /22 ### we want 20 points for analysis
    height_step = 0.4 * height / 22
    height_list = []
    #i = max(y_list) - height_step
    i = 0.8 * height
    while i > 0.4 * height:
        height_list.append(i)
        i = i - height_step

    ### Find maximum position
    #max_pos = find_nearest_point(x_list,centre)
    max_pos = find_nearest_point(y_list,max(y_list))

    ### Split data into two
    x_list_left = x_list[:max_pos+1]
    y_list_left = y_list[:max_pos+1]
    
    x_list_right = x_list[max_pos:]
    y_list_right = y_list[max_pos:]

    ### Make sure the lists are monotonic from centre
    x_list_left,y_list_left = monotonicize(x_list_left,y_list_left,0)
    x_list_right,y_list_right = monotonicize(x_list_right,y_list_right,1)

    ### Perform bisector analysis on every height_list
    bisector_list = []
    for height_i in height_list:
        x_left = interpolate(x_list_left,y_list_left,height_i,0)
        x_right = interpolate(x_list_right,y_list_right,height_i,1)

        x_mean = mean([x_left,x_right])

        plt.scatter(x_mean,height_i,s=5,color="k")
        plt.plot([x_left,x_right],[height_i,height_i],"b-",lw=0.5)
        bisector_list.append(x_mean)

    return bisector_list,height_list

########################
### Start of program ###
########################

### Set file path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

### Set file name
file_name = sys.argv[2]

### Set program dir and change working directory
program_dir = os.getcwd() + "/" #Save the current working directory
os.chdir(file_path_reduced) #Change to ../temp/ dir
os.system("mkdir ccf_pdfs")
os.system("rm ccf_pdfs/*" + file_name + "*")

################
### Load ccf ###
################
plt.clf()

hdulist = pyfits.open(file_path + file_name)
candidate = hdulist[0].header["OBJECT"]
hdulist.close()

ccf = functions.read_ascii("ccf_" + file_name + ".txt")
ccf = functions.read_table(ccf)

### Find max
max_ccf = max(transpose(ccf)[1])
max_pos = 0

for i in range(len(ccf)):
    if ccf[i][1] == max_ccf:
        max_pos = i
        break

#ccf = ccf[i-200:i+200]
ccf = ccf[i-40:i+40]
ccf = transpose(ccf)

### Define plotting axes
shift = ccf[0]
ccf_cor = ccf[1]

### find noise median
temp_list = []
for i in ccf_cor:
    if i < 0.15:
        temp_list.append(i)

ccf_cor = list(array(ccf_cor) - median(temp_list))

#########################
### Find Gaussian fit ###
#########################

best_fit = fitgaussian(array([ccf_cor,ccf_cor]))
height = abs(best_fit[0])
centre = best_fit[2]
width = abs(best_fit[4])
scale = (max(shift) - min(shift)) / (len(shift)-1)
centre = min(shift) + centre * scale
width = width * scale

xfit,yfit = gaussian1d(height,centre,width,min(shift),max(shift))

### Plot
plt.plot(shift,ccf_cor,"b-",lw=2,label="data")
plt.plot(xfit,yfit,"r--",label="model")

#########################
### Bisector analysis ###
#########################
bisector_list,height_list =bisector_analysis(shift,ccf_cor,height,centre,width)

### Calculate bisector velocity at the top and bottom of the CCF
v_top = median(bisector_list[:5])
delta_v_top = std(bisector_list[:5])

v_bottom = median(bisector_list[len(bisector_list)-5:])
delta_v_bottom = std(bisector_list[len(bisector_list)-5:])

#BIS = (v_top - v_bottom)/height
BIS = (v_top - v_bottom) / 0.4
BIS_err = abs(BIS * sqrt((delta_v_top / v_top)**2 + (delta_v_bottom / v_bottom)**2))

print "BIS is " + str(BIS) + "+/-" + str(BIS_err)

#################
### Save plot ###
#################

### Set plot titles
plt.xlim(min(shift),max(shift))
plt.ylim(min(ccf_cor) - 0.01, max(ccf_cor) + 0.01)

width = width * 2.355 ### Change from sigma to FWHM
plt.xlabel("velocity shift (km/s)")
plt.ylabel("CC")
plt.title("CCF " + file_name + " " + candidate + " Peak " + str(round(height,2)) + "\n FWHM " + str(round(width,2)) + " Bisector gradient " + str(round(BIS,3)) + " +/- " + str(round(BIS_err,3)))
plt.savefig(file_path_reduced + "ccf_pdfs/ccf_" + file_name + ".pdf")
#plt.show()

plt.hold(False)
plt.clf()

os.system("rm ccf_pdfs/ccf_all.pdf")
os.system("gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=ccf_pdfs/ccf_all.pdf ccf_pdfs/ccf*.pdf")

print "FWHM = " + str(width) + " km/s"
print "CCF plot saved"
#######################
### Create log file ###
#######################

### log format
### file_name object_name height width BIS BIS_err

new_entry = [file_name, candidate, height, width, BIS, BIS_err]

### check if log file exists
if os.path.exists(file_path_reduced + "ccf_log.txt"):
    ccf_log = functions.read_ascii(file_path_reduced + "ccf_log.txt")
    ccf_log = functions.read_table(ccf_log)

    new_log = []
    entry_exists = False

    for exposure in ccf_log:
        if exposure[0] == file_name:
            new_log.append(new_entry)
            entry_exists = True
        else:
            new_log.append(exposure)
    if not entry_exists:
        new_log.append(new_entry)

else:
    new_log = [new_entry]

ccf_out = open(file_path_reduced + "ccf_log.txt","w")
ccf_out.write("#file_name candidate height width BIS BIS_err \n")
functions.write_table(new_log,ccf_out)
ccf_out.close
    
