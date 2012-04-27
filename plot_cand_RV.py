import functions
import os
import sys
import mysql_query
import string
from numpy import *
import pyfits

###################
### Description ###
###################

### Plots the object RV points using rv_plot.sh
### Points are taken from the HSMSO database
### t1, period, q phase parameters are taken from HSCAND database

### usage: python plot_cand_RV.py {-f file_path file_name | -o object_name}

########################
### Start of program ###
########################

if sys.argv[1] == "-f":

    ### Set file_path
    file_path = sys.argv[2]
    file_path_temp = file_path + "temp/"
    file_path_reduced = file_path + "reduced/"

    ### Define file_name
    file_name = sys.argv[3]

    ### Extract object name from fits header
    hdulist = pyfits.open(file_path + file_name)
    object_name = hdulist[0].header["OBJECT"]
    hdulist.close()

if sys.argv[1] == "-o":
    object_name = sys.argv[2]

plots_folder = functions.read_param_file("RV_PLOTS_FOLDER")

### Extract rv points from HSMSO
query_entry = "select SPEChjd, SPECrv, SPECrv_err from SPEC where SPECtype=\"RV\" and SPECinstrum=\"WiFeS\" and SPECobject=\"%s\" " % object_name
RV_points = mysql_query.query_hsmso(query_entry)

if len(RV_points) > 0:
    cand_txt = open(plots_folder + object_name + ".txt","w")
    functions.write_table(RV_points,cand_txt)
    cand_txt.close()
else:
    print "ERROR entries not found for " + object_name

if len(RV_points) > 1:
    print "Calculating orbital solution"
    ### Extract candidate phase information from HSCAND
    if object_name[:4]=="HATS":
        print "Using HSCAND for candidate parameters"
        query_entry = "select HATSE,HATSP,HATSq from HATS where HATSname=\'%s\' " % object_name
        cand_params = mysql_query.query_hscand(query_entry)[1]

    else:
        ### Try to find it in "candidatex.txt"
        candidates_txt = functions.read_ascii(plots_folder + "candidates.txt")
        candidates_txt = functions.read_table(candidates_txt)

        object_found = False
        for entry in candidates_txt:
            if entry[0] == object_name:
                print "Using candidates.txt for candidate parameters"
                object_found = True
                cand_params = [entry[5],entry[6],entry[7]]
                break
        if not object_found:
            print "Using default candidate parameters"
            RV_points = transpose(RV_points)
            HJD_points = RV_points[0]
            cand_params = [min(HJD_points),max(HJD_points)-min(HJD_points),0.1]
      
    ### Plot the rv phase curve
    os.system("cp rv_plot.sh " + plots_folder)
    program_dir = os.getcwd() + "/" #Save the current working directory
    os.chdir(plots_folder)

    os.system("./rv_plot.sh "+object_name+" "+str(cand_params[0])+" "+str(cand_params[1])+" "+str(cand_params[2]))

    os.chdir(program_dir)

    if functions.read_config_file("OPEN_RESULT_PDFS") == "true":
        os.system("xpdf "+plots_folder + object_name + ".pdf &")
