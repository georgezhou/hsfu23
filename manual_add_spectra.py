import os
import sys
import functions
import mysql_query
from numpy import *
import string
from pyraf import iraf
import pyfits
import matplotlib.pyplot as plt

iraf.onedspec()

object_name = sys.argv[1]

query_command = "select SPECimgname,SPECutdate,SPECobject,SPECrv from SPEC where SPECinstrum = \"WiFeS\" and SPECutdate >= \"2012-01-01\" and SPECutdate <= \"2012-12-31\" and SPECobject = \"" + object_name + "\" and SPECtype=\"RV\""
query_result = mysql_query.query_hsmso(query_command)
outdir = "high_sn/"
master_dir = "/mimsy/george/wifes/"

os.system("mkdir "+outdir)
os.system("mkdir "+outdir+"temp/")
os.system("rm "+outdir+"temp/*")

months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

count = 1
for entry in query_result:

    object_name = entry[2]
    file_name = entry[0]
    utdate = str(entry[1])
    utdate = string.split(utdate,"-")

    mon = int(float(utdate[1]))
    mon = months[mon-1]

    file_path_date = utdate[2]+mon+utdate[0]

    fits_file = master_dir+file_path_date+"/RV/red/reduced/spec_"+file_name
    print fits_file

    RV_val = entry[3]

    if os.path.exists(fits_file):
        order = 1
        while order < 5:
            try:
                iraf.scopy(
                    input = fits_file,\
                    output = outdir+"temp/"+str(count)+".fits",\
                    w1 = "INDEF",\
                    w2 = "INDEF",\
                    apertures = order,\
                    bands = "*",\
                    beams = "*",\
                    format = "multispec",\
                    renumber = 1,\
                    offset = 0,\
                    clobber = 1,\
                    merge = 0,\
                    rebin = 1,\
                    verbose = 1)

                iraf.dopcor(
                    input = outdir+"temp/"+str(count)+".fits",\
                    output = outdir+"temp/"+str(count)+".fits",\
                    redshift = RV_val,\
                    isvelocity=1,\
                    add = 1,\
                    dispersion = 1,\
                    flux = 0)

                count = count + 1
                order = order + 1

            except iraf.IrafError:
                count = count
                order = order + 1
                print "No order exist"

print "Combining spectra"

os.chdir(outdir+"temp")
os.system("ls *.fits > combine_list")

iraf.scombine(
    input = "@combine_list",\
    output = "combine.fits",\
    group = "all",\
    combine = "average",\
    reject = "sigclip",\
    first = 1,\
    w1 = "INDEF",\
    w2 = "INDEF",\
    dw = "INDEF",\
    nw = "INDEF",\
    log = 0,\
    scale = "median",\
    zero = "none",\
    weight = "median",\
    nlow = 5,\
    nhigh = 5,\
    mclip = 1,\
    lsigma = 2.0,\
    hsigma = 2.0)

os.system("mv combine.fits ../"+object_name+".fits")
