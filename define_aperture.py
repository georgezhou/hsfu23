### Load python modules
from numpy import *
import string
import sys
import os
import functions
from scipy import optimize
import pyfits
import matplotlib.pyplot as plt

def iter_polyfit(x,y,sigma=3,niter=3):
    fit = polyfit(x,y,1)
    for i in range(niter):
        fit = polyval(fit,x)
        mask = abs(y-fit) < sigma*std(y-fit)
        x = x[mask]
        y = y[mask]
        fit = polyfit(x,y,1)
        #print fit

    return fit
    

def gaussian(x0,x):
    a0,mu,sigma,m,c = x0
    f = a0*exp(-1*(x-mu)**2/(2*sigma**2))+m*x+c
    return f

def fit_gauss(x,y):
    x = x[1:]
    y = y[1:]

    def minfunc(x0):
        f = gaussian(x0,x)
        f = sum((y - f)**2)

        if x0[0] < 2:
            f = NaN
        if x0[1] < 0 or x0[1] > (len(x)-1):
            f = NaN
        if x[2] < 0. or x[2] > 5:
            f = NaN
        #print x0,f
        return f

    ### Find loc of max
    midpt = len(x)/2
    #y_fit = polyfit(x,y,1)
    y_fit_param = iter_polyfit(x,y)
    y_fit = polyval(y_fit_param,x)
    y_fit = y-y_fit
    #y_fit = y
    for i in range(len(x)):
        if y_fit[i] == max(y_fit):
            if i > 1 and i < len(x)-2:
                midpt = i
                break


    x0 = array([max(y),midpt,2.,y_fit_param[0],median(y)])
    
    x0 = optimize.fmin(minfunc,x0)#,disp=0)
    print x0
    f = gaussian(x0,x)
    #plt.plot(x,y)
    #plt.plot(x,f)
    #plt.show()
    
    return f,x0[2]

def define_aperture(imslice,coo,star):

    coo_x = coo[star][0]
    coo_y = coo[star][1]

    imslice = pyfits.getdata(imslice)
    
    x = []
    y = []

    for i in range(len(imslice)):
        x.append(i)
        midpt = len(imslice[i])/2
        y.append(median(imslice[i,midpt-200:midpt+200]))

    x,y = array(x),array(y)

    f,sigma = fit_gauss(x,y)
    if sigma > 5:
        sigma = 5
    if sigma < 1:
        sigma = 1


    xlist = transpose(coo)[0]
    temp = []
    for i in xlist:
        try:
            temp.append(float(i))
        except:
            temp.append(eval(i))
    xlist = temp

    x1 = min(temp)-3.*sigma-1
    x2 = max(temp)+3.*sigma-1

    # x1 = round(x1-len(x)/2,0)
    # x2 = round(x2-len(x)/2,0)

    # background = ""

    # if x1 > -1*len(x)/2:
    #     background = background+str(-1*len(x)/2)+":"+str(x1)
    # if x2 < len(x)/2:
    #     if not background == "":
    #         background = background + ","
    #     background = background+str(x2)+":"+str(int(len(x)/2))

    # print background

    # llimit = round(coo_x - sigma - len(x)/2-1,0)
    # ulimit = round(coo_x + sigma - len(x)/2-1,0)

    # return llimit,ulimit,background

    background = []

    if x1 > 1:
        background.append([1,x1])
    if x2 < len(x):
        background.append([x2,len(x)])

    return sigma,background
