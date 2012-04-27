import functions
import mysql_query
from numpy import *
import os
import sys
import string
import pyfits

###################
### Description ###
###################

### Update hatsouth.intersigma

########################
### Start of program ###
########################

query_entry = "select SPECtype,SPECobject,SPECmjd,SPEChjd,SPECrv,SPECrv_err,SPECtelescope,SPECresolution,SPECteff,SPECteff_err,SPEClogg,SPEClogg_err,SPECfeh,SPECfeh_err,SPECccfheight,SPECexptime,SPECsn"
query_entry = query_entry + " from SPEC where SPECutdate >= \"2010-01-01\" and SPECutdate <=\"2012-04-16\" and SPECobject like \"HATS%\""
#query_entry = query_entry + " from SPEC where SPECobject = \"HATS551-013\" "

exposure_info = mysql_query.query_hsmso(query_entry)
#print exposure_info

if len(exposure_info) > 0:
    output = ""
    
    for entry in exposure_info:
        if entry[0] == "RV":
            output = output + entry[1] + " " #name
            output = output + str(2400000 + entry[3]) + " " #hjd
            output = output + str(entry[4]) + " " #RV
            output = output + str(entry[5]) + " " #RVerr
            output = output + str(entry[6]) + " " #tel
            output = output + str(entry[7]) + " " #res
            output = output + "0 0 0 0 0 0 0 0 " #teff terr logg loggerr feh feherr vrot vroterr
            output = output + str(entry[14]) + " " #ccfheight
            output = output + str(entry[15]) + " " #exptime
            output = output + str(entry[16]) + "\n" #S/N

        if entry[0] == "ST":
            output = output + entry[1] + " " #name
            output = output + str(2400000 + entry[2]) + " " #mjd
            output = output + "-999 -999 " #rv rverr
            output = output + str(entry[6]) + " " #tel
            output = output + str(entry[7]) + " " #res            
            output = output + str(entry[8]) + " 300 " #teff
            #output = output + str(entry[9]) + " " 
            output = output + str(entry[10]) + " 0.3 " #logg
            #output = output + str(entry[11]) + " " 
            output = output + "0 0 0 0 0 " #feh feherr vrot vroterr ccfheight
            output = output + str(entry[15]) + " " #exptime
            output = output + str(entry[16]) + "\n" #S/N

    output_file = open("HSintersigma_output","w")
    output_file.write(output)
    output_file.close()
    print output
    print "No. of observations: ",len(exposure_info)
    
    update = raw_input("Update hatsouth.intersigma webpage? (y/n): ")
    if update == "y":
        os.system("./insertHSvelocities.py HSintersigma_output")

    remove_temp = raw_input("Remove HSintersigma_output temporary ascii file? (y/n): ")
    if remove_temp == "y":
        os.system("rm HSintersigma_output")
