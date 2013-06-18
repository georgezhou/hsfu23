### Load python modules
from pyraf import iraf
from numpy import *
import string
import sys
import os
import pyfits

### Load functions script (located in the same folder)
import functions

### Load iraf moduels
iraf.noao()
iraf.imred()
iraf.imred.ccdred()
iraf.imred.kpnoslit()
iraf.twodspec()
iraf.longslit()
iraf.noao.rv()
iraf.astutil()

###################
### Description ###
###################

### Correct for spectrograph tilt in the spatial axis
### Method: Using the correction method described in 
### "A user's guide to reducing slit spectra with IRAF" 
### Massey, Valdes, Barnes 1992
### Appendix B

### The emission lines in each row of an image slice for an arc is identified.
### The location of the emission lines forms an array
### allowing transformation of x,y -> u,v.
### We fit for the transformation with fitcoords
### and apply it to form a rectangular image with transform.
### Each pixel is interpolated with a spline3 function
### Flux per pixel is conserved.

### Usage: python correct_distortions.py file_path file_name

########################
### Start of program ###
########################

### Set file_path
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

camera = functions.read_config_file("CAMERA")
grating = functions.read_config_file("GRATING")
dichroic = functions.read_config_file("DICHROIC")

### Get slice numbers and arc images to use
arc_list = functions.read_ascii(file_path_temp + "arcs_to_use.txt")
#image_slices = functions.read_ascii(file_path_temp + "stellar_apertures.txt")
image_slices = loadtxt(file_path_temp+"image_slice_table.txt")
image_slices = arange(len(image_slices))

### Define linelist to use
linelist = grating + "_linelist.dat"

### Define template to use
template = grating +"_"+dichroic+ "_template.fits"

###################################################
### Setup the folders and remove previous files ###
###################################################

program_dir = os.getcwd() + "/" #Save the current working directory
os.chdir(file_path_temp) #Change to ../temp/ dir
os.system("mkdir database")

os.system("rm database/*" + string.split(file_name,".")[0] + "*")

print "Straightening spectroscopic distortions"

for im_slice in image_slices:
    im_slice = str(im_slice)

    ### We only need one arc image as reference for 
    ### straightening out the lines
    ### so use the one taken closest in time to the object exposure
    arc_name = arc_list[0]

    ### Run reidentify on arc_name
    ### on the first row.
    ### This gives a reference starting point 

    ### Copy over the template data from program home
    os.system("cp -f " + program_dir + "cal_linelists/"  + template + " .")
    os.system("cp -f " + program_dir+"cal_linelists/database/id"+grating+"_"+dichroic+"_template " + "database/")
    os.system("rm database/*" + im_slice + "_" + string.split(arc_name,".")[0]+ "*")
 
    # print "Dispersion correcting the central row of pixels"

    # iraf.reidentify(
    #     reference = template, \
    #     images = im_slice + "_" + arc_name,\
    #     answer = "no",\
    #     crval = "",\
    #     cdelt = "",\
    #     interactive = "no",\
    #     section = "first line",\
    #     #section = "middle line",\
    #     newaps = 0,\
    #     override = 1,\
    #     refit = 1,\
    #     trace = 0,\
    #     step = "10",\
    #     nsum = "10",\
    #     shift = "INDEF",\
    #     search = "INDEF",\
    #     nlost = 2,\
    #     cradius = 5.0,\
    #     threshold = 5.0,\
    #     addfeatures = 0,\
    #     coordlist = program_dir + "cal_linelists/" + linelist,\
    #     match = -2.0,\
    #     maxfeatures = 60,\
    #     minsep = 2.0,\
    #     database = "database",\
    #     plotfile = "",\
    #     verbose = 1,\
    #     graphics = "stdgraph",\
    #     cursor = "",\
    #     aidpars = "",\
    #     mode = "ql")

    # print "running reidentify again for each row"

    nlines = pyfits.getdata(im_slice +"_" + arc_name)
    nlines = len(nlines)
    print nlines

    for n in arange(1,nlines+1):

        os.system("rm temp_slice.fits")
        os.system("rm database/*temp_slice*")
        
        iraf.imcopy(
            input = im_slice +"_" + arc_name+"[*,"+str(n)+"]",\
            output = "temp_slice.fits")

        iraf.reidentify(
            reference = template, \
            images = "temp_slice.fits",\
            answer = "no",\
            crval = "",\
            cdelt = "",\
            interactive = "no",\
            section = "first line",\
            #section = "middle line",\
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


        identify_result = open("database/idtemp_slice").read()
        #identify_result = string.split(identify_result,"\n\t")
        #print identify_result
        identify_result = string.replace(identify_result,"temp_slice",im_slice +"_" + string.split(arc_name,".fits")[0]+"[*,"+str(n)+"]")
        f = open("database/temp_text","w")
        f.write(identify_result)
        f.close()

        os.system("cat database/temp_text >> database/id"+im_slice +"_" +string.split(arc_name,".fits")[0])
                 


    # ### Run reidentify again on the same image
    # ### this time run it for every row 
    # ### along the spatial axis, such that we map out
    # ### the distortions
    # iraf.reidentify(
    #     reference = im_slice +"_" + arc_name,\
    #     images = im_slice + "_" + arc_name,\
    #     interactive = "yes",\
    #     section = "first line",\
    #     #section = "middle line",\
    #     newaps = 1,\
    #     override = 1,\
    #     refit = 0,\
    #     trace = 0,\
    #     step = 1,\
    #     nsum = 1,\
    #     shift = "INDEF",\
    #     search = "INDEF",\
    #     nlost = 3,\
    #     cradius = 5.0,\
    #     threshold = 5.0,\
    #     addfeatures = 0,\
    #     coordlist = program_dir + "cal_linelists/" + linelist,\
    #     match = -2.0,\
    #     maxfeatures = 60,\
    #     minsep = 2.0,\
    #     database = "database",\
    #     plotfile = "",\
    #     verbose = 1,\
    #     graphics = "stdgraph",\
    #     cursor = "",\
    #     answer = "yes",\
    #     crval = "",\
    #     cdelt = "",\
    #     aidpars = "")

    ### Run fitcoords to fit coordinate and get ready for transformation
    ### xorder and yorder specifies the fitting orders
    iraf.fitcoords(
        images = im_slice + "_" + string.split(arc_name,".")[0],\
        fitname = "",\
        interactive = 0,\
        combine = 0,\
        database = "database",\
        deletions = "deletions.db",\
        function = "chebyshev",\
        xorder = 6,\
        yorder = 2,\
        logfiles = "STDOUT,logfile",\
        plotfile = "plotfile",\
        graphics = "stdgraph")

    ### Run transform according to the results of fitcoords
    ### This is the final step
    ### The product is a nicely straightened fits file
    os.system("rm -f t" + im_slice + "_" + file_name)
    for i in arc_list:
        os.system("rm -f t" + im_slice + "_" + i)
    
    image_to_reduce = im_slice + "_" + file_name + ","
    output_images = "t" + im_slice + "_" + file_name + ","

    for i in arc_list:
        image_to_reduce = image_to_reduce + im_slice + "_" + i + ","
        output_images = output_images + "t" + im_slice + "_" + i + ","

    print "transforming images " + image_to_reduce
    
    ### Add the parameter dispaxis to the image header
    ### else iraf.transform would query for it
    ### 1 indicates that the x axis is the dispersion axis
    iraf.hedit(images = image_to_reduce,fields="DISPAXIS",value="1",add=1,addonly=0,delete=0,verify=0,show=1,update=1)

    iraf.transform(
        input = image_to_reduce,\
        output = output_images,\
        minput = "",\
        moutput = "",\
        fitnames = im_slice + "_" + string.split(arc_name,".")[0],\
        database = "database",\
        interptype = "spline3",\
        x1 = "INDEF",\
        x2 = "INDEF",\
        dx = "INDEF",\
        nx = "INDEF",\
        xlog = 0,\
        y1 = "INDEF",\
        y2 = "INDEF",\
        dy = "INDEF",\
        ny = "INDEF",\
        ylog = 0,\
        flux = 1,\
        blank = "INDEF",\
        logfile = "STDOUT,logfile",\
        mode = "al")

