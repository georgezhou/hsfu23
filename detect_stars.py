### Load python modules
import pyfits
from numpy import *
import string
import sys
import os
import functions
import pyfits
import matplotlib.pyplot as plt
from scipy import optimize
import fit_2d_gauss

from pyraf import iraf
iraf.imred()
iraf.imred.ccdred()
iraf.astutil()
iraf.digiphot()
iraf.daophot()
iraf.apphot()


### Set parameters to datapars
def set_datapars(bksigma):
    iraf.unlearn(iraf.datapars)
    iraf.datapars.setParam("scale",1.0,check=1,exact=1)
    iraf.datapars.setParam("fwhmpsf",2.0,check=1,exact=1)
    iraf.datapars.setParam("emission",1,check=1,exact=1)
    iraf.datapars.setParam("sigma",bksigma,check=1,exact=1)
    iraf.datapars.setParam("datamin","INDEF",check=1,exact=1)
    iraf.datapars.setParam("datamax","INDEF",check=1,exact=1)
    iraf.datapars.setParam("noise","poisson",check=1,exact=1)
    iraf.datapars.setParam("ccdread","",check=1,exact=1)
    iraf.datapars.setParam("gain","",check=1,exact=1)
    iraf.datapars.setParam("readnoise",0.0,check=1,exact=1)
    iraf.datapars.setParam("epadu",1.0,check=1,exact=1)
    iraf.datapars.setParam("airmass","",check=1,exact=1)
    iraf.datapars.setParam("filter","",check=1,exact=1)
    iraf.datapars.setParam("obstime","",check=1,exact=1)
    iraf.datapars.setParam("itime",1.0,check=1,exact=1)
    iraf.datapars.setParam("xairmass","INDEF",check=1,exact=1)
    iraf.datapars.setParam("ifilter","INDEF",check=1,exact=1)
    iraf.datapars.setParam("otime","INDEF",check=1,exact=1)

### Set parameters to findpars
def set_findpars():
    iraf.unlearn(iraf.findpars)
    iraf.findpars.setParam("threshold",5.0,check=1,exact=1)
    iraf.findpars.setParam("nsigma",2.0,check=1,exact=1)
    iraf.findpars.setParam("ratio",1.0,check=1,exact=1)
    iraf.findpars.setParam("theta",0.0,check=1,exact=1)
    iraf.findpars.setParam("sharplo",0.0,check=1,exact=1)
    iraf.findpars.setParam("sharphi",1.0,check=1,exact=1)
    iraf.findpars.setParam("roundlo",-1.0,check=1,exact=1)
    iraf.findpars.setParam("roundhi",1.0,check=1,exact=1)
    iraf.findpars.setParam("mkdetections",0,check=1,exact=1)

def run_daofind(input_image,output_coo,verbosity):

    ### Find bksigma
    data = pyfits.getdata(input_image)
    oned = []
    for i in range(len(data)):
        for j in range(len(data)):
            oned.append(data[i,j])

    niter = 5
    sig = 2.0
    for i in range(niter):
        bksigma = std(oned)
        med = median(oned)
        temp = []
        for n in oned:
            if abs(n-med) < sig*bksigma:
                temp.append(n)
        if len(temp) > 1:
            oned = temp

    bksigma = std(oned)

    os.system("rm "+output_coo)
    iraf.unlearn(iraf.daofind)
    set_datapars(bksigma)
    set_findpars()

    iraf.daofind(
        image = input_image,\
        output = output_coo,\
        starmap = "",\
        skymap = "",\
        boundary = "nearest",\
        constant = 0.0,\
        interactive = 0,\
        icommands = "",\
        gcommands = "",\
        wcsout = "logical",\
        cache = 0,\
        verify = 0,\
        update = 0,\
        verbose = verbosity)


def circle(x,y,radius,image):
    weights_image = zeros([len(image),len(image[0])])
    for i in range(len(image)):
        for j in range(len(image[i])):
            if sqrt((x-i)**2+(y-j)**2)<radius:
                weights_image[i,j]=1.
            else:
                weights_image[i,j]=0.
            
    # plt.imshow(image,)
    # plt.imshow(weights_image,cmap="gray",alpha=0.5)
    # plt.show()
    # sys.exit()
    return weights_image


def detect_stars(input_image,se_path,no_stars):
    
    image_data = pyfits.getdata(input_image)

    oned = []
    for i in range(len(image_data)):
        for j in range(len(image_data)):
            oned.append(image_data[i,j])

    med = median(oned)

    run_daofind(input_image,"master_coo",1)

    os.system("rm coords.cat")
    SEcommand = se_path+" "+input_image+" -c default.sex"
    SEcommand = SEcommand+" -BACK_TYPE MANUAL -BACK_VALUE "+str(med)
    os.system(SEcommand)

    os.system("cat coords.cat")

    SE_coo = functions.read_ascii("coords.cat")
    SE_coo = functions.read_table(SE_coo)

    temp = []
    for i in SE_coo:
        if i[0] < 36.:
            temp.append(i)
    SE_coo = temp

    phot_coo = functions.read_ascii("master_coo")
    phot_coo = functions.read_table(phot_coo)

    temp = []
    for i in phot_coo:
        if i[0] < 36.:
            temp.append(i)
    phot_coo  = temp

    ### Check if the objects in phot_coo exists also in SE_coo
    confirmed_objects = []

    for phot_obj in phot_coo:
        phot_obj_x = phot_obj[0]
        phot_obj_y = phot_obj[1]
        for SE_obj in SE_coo:
            SE_obj_x = SE_obj[0]
            SE_obj_y = SE_obj[1]
            SE_obj_fwhm = SE_obj[4]

            SE_obj_fwhm = 6
            
            # if SE_obj_fwhm < 5. or SE_obj_fwhm > 10.0:
            #     SE_obj_fwhm = 5

            if abs(phot_obj_x-SE_obj_x)<SE_obj_fwhm and abs(phot_obj_y-SE_obj_y)<SE_obj_fwhm:
                confirmed_objects.append(phot_obj)
                break

    if len(confirmed_objects) == 0 and len(SE_coo) > 0:
        print "NO matching objects, using SE coordinates"
        confirmed_objects = []
        for SE_obj in SE_coo:
            confirmed_objects.append([SE_obj[0],SE_obj[1],"INDEF",0.5,0.5,0.5,SE_obj[0]])

    elif len(confirmed_objects) == 0 and len(phot_coo) > 0:
        print "NO matching objects, using iraf.phot coordinates"
        confirmed_objects = phot_coo

    elif len(confirmed_objects)==0 and len(phot_coo)==0 and len(SE_coo)==0:
        print "NO objects detected!!!"
        sys.exit()


    ### Order by brightness


    flux_list = []
    for i in confirmed_objects:

        aperture = circle(i[1]-1,i[0]-1,2.0,image_data)
        flux = aperture*image_data - aperture*med
        flux = flux.sum()
        flux_list.append(flux)

    flux_list_sorted = sorted(flux_list,reverse=True)

    print "flux",flux_list_sorted

    temp = []
    for i in range(len(flux_list_sorted)):
        j = flux_list.index(flux_list_sorted[i])
        temp.append(confirmed_objects[j])
        
    confirmed_objects = temp
            
    ### remove unwanted objects
    if no_stars > 0:
        confirmed_objects = confirmed_objects[:no_stars]

    master_out = open("master_coo","w")
    functions.write_table(confirmed_objects,master_out)
    master_out.close()







