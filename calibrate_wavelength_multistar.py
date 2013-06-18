### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import pyfits
import define_aperture
import trace
import matplotlib.pyplot as plt

### Load functions script (located in the same folder)
import functions

### Load iraf moduels
iraf.noao()
iraf.imred()
iraf.imred.ccdred()
iraf.imred.kpnoslit()
iraf.noao.rv()
iraf.astutil()

###################
### Description ###
###################

### The stellar spectrum needs to be extracted and wavelength calibrated.
### Extraction is automatically performed on the brightest star 
### unless interact is turned on.

### The arc spectrum is extracted along the same aperture as the 
### stellar spectrum.

### If all went well, the distortion corrected fits image already
### has a wavelength solution. We use the arc spectra to check 
### this wavelength calibration. We also perform cosmic ray removal
### and normalisation.

### Usage: calibrate_wavelength.py file_path file_name

########################
### Start of program ###
########################

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

hdulist = pyfits.open(file_path + file_name)
object_mjd = hdulist[0].header['MJD-OBS']
hdulist.close()

camera = functions.read_config_file("CAMERA")
grating = functions.read_config_file("GRATING")
dichroic = functions.read_config_file("DICHROIC")
combine_aps = functions.read_config_file("COMBINE_APERTURES")
task = functions.read_config_file("TASK")
no_apertures = eval(functions.read_config_file("NO_APERTURES"))

print "This script applies NeAr arc image to calibrate the object spectrum " +file_name

### Get slice numbers and arc images to use
arc_list = functions.read_ascii(file_path_temp + "arcs_to_use.txt")
coo = functions.read_ascii(file_path_temp+"master_coo")
coo = functions.read_table(coo)

### Calculate the fractional weight of each arc 
arc_weight = []
for arc_name in arc_list:
    hdulist = pyfits.open(file_path + arc_name)
    arc_mjd = hdulist[0].header['MJD-OBS']
    hdulist.close()

    arc_weight.append(abs(arc_mjd - object_mjd))

arc_weight = array(arc_weight)
arc_weight = arc_weight / sum(arc_weight)

### Define linelist to use
linelist = grating + "_linelist.dat"

### Define template to use
template = "calibrated_" + grating +"_"+dichroic+ "_template.fits"

### Determine if the extraction process should be done interactively
interact = 0

interact = functions.read_config_file("INTERACT")
if interact == "true":
    interact = 1
if interact == "false":
    interact = 0

###################################
### Perform spectral extraction ###
###################################

program_dir = os.getcwd() + "/" #Save the current working directory
os.chdir(file_path_temp) #Change to ../temp/ dir

nslice = loadtxt("image_slice_table.txt")

print "Extracting the spectrum "
os.system("rm -f " + file_path_temp + "*" + string.split(file_name,".")[0] + "*ms*")

os.system("rm database/*" + string.split(file_name,".")[0] + "*")
os.system("rm -f " + file_path_temp + "nearraw_*" + file_name)

### Copy over the template files
os.system("cp -f " + program_dir + "cal_linelists/"  + template + " .")
os.system("cp -f " + program_dir+"cal_linelists/database/idcalibrated_"+grating+"_"+dichroic+"_template " + "database/")
 
### Perform spectral extraction, one image slice at a time
### Then extract corresponding arc spectra from the arc images
### So we have n stellar spectra from n image slices
### And n x m arc spectra from n image slices and m arc images

for i in range(len(coo)):

    coo_x=coo[i][0]
    coo_y=coo[i][1]
    sigma,bk = define_aperture.define_aperture("t"+str(int(round(coo_y)))+"_"+file_name,coo,i)

    os.system("rm database/apt*_"+file_name)
    os.system("rm t*_" +string.split(file_name,".")[0]+".ms.fits")
    
    slice_flux = []
    ### Define image slice
    for n in range(len(nslice)):
        
        image = pyfits.getdata("t"+str(n)+"_"+file_name)
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

            for k in bk:
                if x[j] > k[0] and x[j] < k[1]:
                    bk_i.append(median(crop[j]))

        x,y = array(x),array(y)

        slice_flux.append([n,(y[int(round(coo_x))]-median(bk_i))/std(bk_i)])

    slice_flux = functions.sort_array(slice_flux,1)
    print slice_flux

    print coo_y

    image_slices = []
    n = len(slice_flux)-1
    while n >= 0:
        if abs(slice_flux[n][0] - coo_y) < no_apertures:
            image_slices.append(slice_flux[n][0])
        if len(image_slices) < no_apertures:
            n = n-1
        else:
            n = -1

    print "using image slices",image_slices

    f = open("stellar_apertures.txt","w")
    for n in image_slices:
        f.write(str(n)+"\n")
    f.close()

    for im_slice in image_slices:
        im_slice = str(im_slice)

        #lo,up,bk = define_aperture.define_aperture("t"+im_slice+"_"+file_name,coo,i)
        sigma,bk = define_aperture.define_aperture("t"+im_slice+"_"+file_name,coo,i)

        #print sigma,bk

        # if len(coo) > 1:
        #     sigma = sigma /2

        ### Trace along the brigthest star (coo[0])
        signal_trace = trace.trace("t"+im_slice+"_"+file_name,coo[0][0],bk)
        dist = []
        for k in range(len(coo)):
            dist.append(abs(median(signal_trace)-coo[k][0]))
        for k in range(len(dist)):
            if dist[k] == min(dist):
                signal_trace = signal_trace + (coo[0][0]-coo[k][0])
                break

        print "t"+im_slice+"_"+file_name

        ### Make trace plot
        #plt.clf()
        plt.figure(figsize=(17.25,6))
        image = pyfits.getdata("t"+im_slice+"_"+file_name)

        image_clip = 0.05
        stdev = std(image)
        med = median(image)
        #med = med - 0.5*stdev

        plt.imshow(image,cmap="gray",origin="lower",vmin=med-image_clip*stdev,vmax=med+image_clip*stdev,aspect="auto",interpolation=None)

        #plt.imshow(image)
        #plt.contourf(log10(image-image.min()+1))
        for k in range(len(coo)):
            signal_trace_k = signal_trace + (coo[k][0] - coo[0][0])
            plt.plot(signal_trace_k,"r--")

        plt.xlim(0,len(image[0]))
        plt.ylim(0,len(image))

        os.system("rm "+file_path_reduced+"trace_t"+im_slice+"_"+file_name+".pdf")
        plt.savefig(file_path_reduced+"trace_t"+im_slice+"_"+file_name+".pdf")
        
        #plt.show()
        
        #sys.exit()


        ### Offset that trace to the star you want
        signal_trace = signal_trace + (coo[i][0] - coo[0][0])

        trace.extract("t"+im_slice+"_"+file_name,signal_trace,sigma,bk)
        
        os.system("mv spectrum.fits "+"t" + im_slice + "_" +string.split(file_name,".")[0]+".ms.fits")

        ### Extract NeAr arc lamp spectrum
        print "Extracting the arc spectrum according to the same aperture as the object spectrum"
        count = 1
        for arc_name in arc_list:
            ### For each arc image, perform extraction at the same
            ### aperture as the stellar spectrum
            os.system("rm database/*"+im_slice+"*" + string.split(arc_name,".")[0] + "*")
            os.system("rm nearraw_" + im_slice + "_" + arc_name)

            trace.extract("t"+im_slice+"_"+arc_name,signal_trace,sigma,[])

            os.system("mv spectrum.fits "+"nearraw_" + im_slice + "_" + arc_name)
                        
            # ### Use apall to extract along the same lines
            # ### as that used in the stellar extraction
            # iraf.apall(
            #     input = "t" + im_slice + "_" + arc_name, \
            #     output = "nearraw_" + im_slice + "_" + arc_name,\
            #     references = "t"+im_slice+"_" + file_name,\
            #     apertures = "",\
            #     find = 0,\
            #     recenter = 0,\
            #     resize = 0,\
            #     edit = 0,\
            #     trace = 0,\
            #     back = "none",\
            #     nfind = "",\
            #     interactive = 0)

            ### Using reidentify to find a dispersion solution
            print "reidentifying the lines - to make sure of the dispersion solution"
            iraf.reidentify(
                reference = template, \
                images = "nearraw_"+im_slice + "_" + arc_name,\
                answer = "no",\
                crval = "",\
                cdelt = "",\
                interactive = "no",\
                section = "first line",\
                newaps = 0,\
                override = 1,\
                refit = 1,\
                trace = 0,\
                step = "10",\
                nsum = "10",\
                shift = "INDEF",\
                search = "INDEF",\
                nlost = 2,\
                cradius = 5.0,\
                threshold = 5.0,\
                addfeatures = 0,\
                coordlist = program_dir + "cal_linelists/" + linelist,\
                match = -2.0,\
                maxfeatures = 60,\
                minsep = 2.0,\
                database = "database",\
                plotfile = "",\
                verbose = 1,\
                graphics = "stdgraph",\
                cursor = "",\
                aidpars = "",\
                mode = "ql")

            ### Apply dispersion solution to object spectrum
            ### First add REFSPEC to the object header using hedit
            iraf.hedit(
                images="t" + im_slice + "_" +string.split(file_name,".")[0]+".ms.fits",\
                fields ="REFSPEC" + str(int(count)),\
                value ="nearraw_" + im_slice+ "_" + arc_name+" "+str(arc_weight[count-1]),\
                add = 1,\
                verify = 0,\
                show = 1,\
                update = 1)

            count = count + 1

        ### Run dispcor to calibrate the object spectrum according to the dispersion
        ### solution
        print "Using dispcor to apply the dispersion solution to the object image"

        os.system("rm dispcorr_" + im_slice + "_" + file_name)

        iraf.dispcor(
            input = "t" + im_slice + "_" + string.split(file_name,".")[0] + ".ms.fits",\
            output = "dispcorr_" + im_slice + "_" + file_name,\
            linearize = "no",\
            database = "database",\
            log = 0,\
            flux = 1,\
            samedisp = 0,\
            ignoreaps = 0,\
            confirm = 0,\
            listonly = 0,\
            verbose = 1)

        iraf.hedit(images="dispcorr_" + im_slice + "_" + file_name,fields="SFIT",value="1",add=0,delete=1,verify=0,show=1,update=1)
        iraf.hedit(images="dispcorr_" + im_slice + "_" + file_name,fields="SFITB",value="1",add=0,delete=1,verify=0,show=1,update=1)

        ### Apply high rejection to remove cosmic rays, dead pixels, etc.
        print "Applying high rejection"

        ### Be more lenient if apertures will be combined
        if combine_aps == "true":
            lowrej = 50.0
            highrej = 50.0
            nit = 2
        else:
            lowrej = 15.0
            highrej = 25.0
            nit = 2

        os.system("rm cray_" + im_slice + "_" + file_name)
        iraf.continuum(
            input = "dispcorr_" + im_slice + "_" + file_name,\
            output = "cray_" + im_slice + "_" + file_name,\
            ask = "no",\
            lines = "*",\
            bands = "*",\
            type = "data",\
            replace = 1,\
            wavescale = 1,\
            logscale = 0,\
            override = 1,\
            listonly = 0,\
            logfiles = "logfile",\
            interactive = 0,\
            sample = "*",\
            naverage = 1,\
            function = "spline3",\
            order = 15,\
            low_reject = lowrej,\
            high_reject = highrej,\
            niterate = nit,\
            grow = 1.0)

        iraf.hedit(images="cray_" + im_slice + "_" + file_name,fields="SFIT",value="1",add=0,delete=1,verify=0,show=1,update=1)
        iraf.hedit(images="cray_" + im_slice + "_" + file_name,fields="SFITB",value="1",add=0,delete=1,verify=0,show=1,update=1)

        ### Apply normalisation with continuum
        print "Fitting continuum and normalising spectrum"
        os.system("rm norm_" + im_slice + "_" + file_name)
        iraf.continuum(
            input = "cray_" + im_slice + "_" + file_name,\
            output = "norm_" + im_slice + "_" + file_name,\
            lines = "*",\
            bands = "*",\
            type = "ratio",\
            replace = 0,\
            wavescale = 1,\
            logscale = 0,\
            override = 1,\
            listonly = 0,\
            logfiles = "logfile",\
            interactive = 0,\
            function  = "spline3",\
            order = 15,\
            low_reject = 2.0,\
            high_reject = 3.0,\
            niterate = 5,\
            grow = 1,\
            ask = "no",)

    ### correct and combine

    os.chdir(program_dir)
    print "correct and combine"

    if task == "RV":
        os.system("python telluric_correction.py "+file_path+" "+file_name)
    
    os.system("python combine_apertures.py "+file_path+" "+file_name)

    if grating == "R3000":
        os.system("python telluric_removal.py "+file_path_temp+"spec_"+file_name)
        os.system("mv "+program_dir+"temp_folder/telcor_spec_"+file_name+" "+file_path_temp+"spec_"+file_name)
    os.chdir(file_path_temp)

    hdulist = pyfits.open(file_path+file_name)
    object_name = hdulist[0].header["OBJECT"]
    hdulist.close()

    suffix = unichr(ord("A")+i)

    if i > 0:

        try:
            iraf.hedit(
                images = "spec_"+file_name,\
                fields = "OBJECT",\
                value = object_name+suffix,\
                add = 1,\
                addonly = 0,\
                delete = 0,\
                verify = 0,\
                show = 1,\
                update = 1)
        except iraf.IrafError:
            pass

        try:
            iraf.hedit(
                images = "normspec_"+file_name,\
                fields = "OBJECT",\
                value = object_name+suffix,\
                add = 1,\
                addonly = 0,\
                delete = 0,\
                verify = 0,\
                show = 1,\
                update = 1)
        except iraf.IrafError:
            pass
        
    os.system("cp spec_"+file_name+" spec_"+suffix+"_"+file_name)
    os.system("cp normspec_"+file_name+" normspec_"+suffix+"_"+file_name)
