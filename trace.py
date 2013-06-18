### Load python modules
from numpy import *
import string
import sys
import os
import pyfits
import functions
import matplotlib.pyplot as plt
from scipy import optimize,interpolate
from pyraf import iraf
import re

iraf.onedspec()

def update_fitsheader(input_header,original_data,image):
    bad_header_names = "SIMPLE,BITPIX,NAXIS,NAXIS1,NAXIS2,BSCALE,BZERO"

    # print input_header
    # sys.exit()
    
    ### correct header
    #input_header = string.split(input_header,"\n")
    corrected_header = []
    for i in range(len(input_header)):
        #print input_header[i]
        if not input_header[i] == "":
            if not input_header[i][0] == " ":
                header_name = re.split(" |=",input_header[i])[0]
                try:
                    header_value = original_data[0].header[header_name]
                    if type(header_value) == str:
                        if len(header_value) > 0:
                            if header_value[0] == "+":
                                header_value = header_value[1:]

                    # else:
                    #     header_value = str(header_value)

                    if not (header_name in bad_header_names):
                        try:            
                            #print header_name,header_value,type(header_value)
                            iraf.hedit(
                                images = image,\
                                fields = header_name,\
                                add = 0,\
                                addonly = 0,\
                                delete = 1,\
                                verify = 0,\
                                show = 0,\
                                update = 0)

                            iraf.hedit(
                                images = image,\
                                fields = header_name,\
                                value = "dummy",\
                                add = 1,\
                                addonly = 0,\
                                delete = 0,\
                                verify = 0,\
                                show = 0,\
                                update = 1)

                            iraf.hedit(
                                images = image,\
                                fields = header_name,\
                                value = header_value,\
                                add = 1,\
                                addonly = 0,\
                                delete = 0,\
                                verify = 0,\
                                show = 0,\
                                update = 1)
                        except iraf.IrafError:
                            print "Hedit insert error",header_name,header_value,type(header_value)

                except KeyError:
                    pass

def fit_quad(input_x,input_y,output_x):


    ### First to an iterated sigma rejection using order=1
    niter = 5
    sigma = 1.5

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

        if len(input_x_temp) > 5:
            input_y = array(input_y_temp)
            input_x = array(input_x_temp)

        # plt.scatter(input_x,input_y,color="b",edgecolor="b")
        # plt.plot(output_x,output_y,"k")
        # plt.show()

    ### The fit using a higher order function

    if len(input_x) > 30:
        order = 2
    else:
        order = 1

    f = polyfit(input_x,input_y,order)
    output_y = polyval(f,output_x)
            
    return output_y

def gaussian(x0,x):
    a0,mu,sigma,c = x0
    f = a0*exp(-1*(x-mu)**2/(2*sigma**2))+c
    return f

def fit_gauss(x,y,mu,bk):

    def minfunc(x0):
        f = gaussian(x0,x)
        f = sum((y - f)**2)

        if x0[0] < 2:
            f = NaN
        #if x0[1] < 0 or x0[1] > len(x)-1:
        if abs(x0[1]-mu) > 5:
            f = NaN
        if x[2] < 0. or x[2] > 5:
            f = NaN

        return f

    ### Find max
    for i in range(len(x)):
        if y[i] == max(y):
            if abs(mu-i)<4:
                mu = i

    x0 = [max(y)-bk,mu,2.,bk]
    x0 = optimize.fmin(minfunc,x0,disp=0)

    f = gaussian(x0,x)

    # plt.plot(x,y)
    # plt.plot(x,f)
    # plt.show()

    return x0[1]

def trace(image,coo_x,bk):

    #coo_x = coo[0][0]

    image = pyfits.getdata(image)
    image = transpose(image)


    ### First find the peak of the image
    crop = image
    crop = transpose(crop)

    x = []
    y = []

    bk_i = []

    for j in range(len(crop)):
        x.append(j)
        y.append(median(crop[j]))

    #     for n in bk:
    #         if x[j] > n[0] and x[j] < n[1]:
    #             bk_i.append(median(crop[j]))


    # x,y = array(x),array(y)
    # if len(bk_i) < 1:
    #     bk_i = [median(y),median(y)]

    # if max(y)-median(bk_i)>3.*std(bk_i):
    #     coo_x = fit_gauss(x,y,coo_x,median(bk_i))

    for j in range(len(x)):
        if y[j] == max(y):
            if j > 3 and j < len(x)-3:
                coo_x = j


    ### Now iterate through using the new coo_x

    line = []
    peak = []

    step = 200

    i = 200
    while i+step < len(image)-200:

        if i <= step/2.+1:
            l1 = 0
            l2 = step
        elif i >= len(image) - step/2.-1:
            l1 = len(image) - step
            l2 = len(image) - 1
        else:
            l1 = i - int(step / 2.)
            l2 = i + int(step / 2.)

        crop = image[l1:l2]
        crop = transpose(crop)

        x = []
        y = []

        bk_x = []
        bk_i = []

        for j in range(len(crop)):
            x.append(j)
            y.append(median(crop[j]))

            for n in bk:
                if j > n[0]-3 and j < n[1]+3 and j > 2 and j < len(crop)-2:
                    bk_i.append(median(crop[j]))
                    bk_x.append(j)

        x,y = array(x),array(y)
        if len(bk_i) < 5:
            bk_x = [1,2]
            bk_i = [median(y),median(y)]
        # else:
        #     bk_i = sort(bk_i)
        #     bk_i = bk_i[:-3]

        #print len(bk_i),std(bk_i)
        #print max(y)-median(bk_i)

        #plt.plot(bk_i)

        ### Remove background gradient
        bk_f = polyfit(bk_x,bk_i,1)
        bk_f = polyval(bk_f,x)
        
        y = y - bk_f

        bk_f = polyfit(bk_x,bk_i,1)
        bk_f = polyval(bk_f,bk_x)
        bk_i = bk_i - bk_f

        peak_i = fit_gauss(x,y,coo_x,median(bk_i))

        i_pos = int(round(peak_i))
        if i_pos < 0:
            i_pos = 0
        if i_pos >= len(x):
            i_pos = len(x)-1

        if y[i_pos]-median(bk_i)>3*std(bk_i):
            if abs(peak_i)-coo_x < 5:
                line.append(i)
                peak.append(peak_i)

        i = i + step/10
        #i = i+step

    if len(line) > 5:
        line,peak = array(line),array(peak)
    else:
        crop = image
        crop = transpose(crop)

        x = []
        y = []

        bk_i = []

        for j in range(len(crop)):
            x.append(j)
            y.append(median(crop[j]))

            for n in bk:
                if x[j] > n[0] and x[j] < n[1]:
                    bk_i.append(median(crop[j]))


        x,y = array(x),array(y)
        if len(bk_i) < 1:
            bk_i = [median(y),median(y)]

        if max(y)-median(bk_i)>3.*std(bk_i):
            coo_x = fit_gauss(x,y,coo_x,median(bk_i))

        line = arange(len(image))
        peak = coo_x*ones(len(image))

    peakfit = fit_quad(line,peak,arange(len(image)))

    ### Uncomment this to see the trace!
    # plt.clf()
    # plt.scatter(line,peak)
    # plt.plot(arange(len(image)),peakfit)
    # plt.show()

    return peakfit

def extract(image,trace,sigma,bk):

    if sigma < 1.:
        sigma = 1.

    #sigma = sigma*2
    #print sigma,"sigma"

    original_file = pyfits.open(image)
    original_header = iraf.imheader(images=image,longheader=1,Stdout=1)

    image = pyfits.getdata(image)
    image = transpose(image)

    line = []
    peak = []

    step = 200

    i = 0
    while i < len(image):
        crop = image[i]

        bk_i = []
        signal_i = []

        ### uncomment this to see where the extraction is taking place

        # plt.plot(crop)
        # plt.axvline(x=trace[i])
        # plt.show()

        x = arange(0,len(crop)+0.1-1,0.1)
        y = interpolate.interp1d(arange(0,len(crop)),crop)
        y = y(x)
        weights = []

        for j in range(len(x)):
            for n in bk:
                if x[j] > n[0] and x[j] < n[1]:
                    bk_i.append(y[j])
            
            if x[j] > trace[i] - sigma and x[j] < trace[i] + sigma:
                signal_i.append(y[j])

                weights.append(gaussian([1,trace[i],sigma,0],x[j]))

        if len(bk_i) > 0:
            bk_i = median(bk_i)
        else:
            bk_i = 0

        if len(signal_i) > 0:
            pass
        else:
            signal_i = [0]
            weights = [1]

        signal_i = array(signal_i)
        weights = array(weights)

        line.append(i+1)
        peak.append(sum(signal_i)-bk_i*len(signal_i))
        #peak.append(sum(signal_i*weights)-sum(bk_i*weights))

        i = i + 1    

    ### Uncomment to plot spectrum
    # plt.clf()
    # plt.plot(line,peak)
    # plt.show()

    data = transpose(array([line,peak]))
    f = open("spectrum.flux","w")
    functions.write_table(data,f)
    f.close()

    os.system("rm spectrum.fits")
    iraf.rspectext(
        input = "spectrum.flux",\
        output = "spectrum.fits",\
        title = "",\
        flux = 0,\
        dtype = "interp")
    
    update_fitsheader(original_header,original_file,"spectrum.fits")
    original_file.close()
