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


start_date = "2013-05-24"
end_date = "2013-05-25"

query_entry = "select SPECtype,SPECobject,SPECmjd,SPEChjd,SPECrv,SPECrv_err,SPECtelescope,SPECresolution,SPECteff,SPECteff_err,SPEClogg,SPEClogg_err,SPECfeh,SPECfeh_err,SPECccfheight,SPECexptime,SPECsn"
query_entry = query_entry + " from SPEC where SPECutdate >= \""+start_date+"\" and SPECutdate <=\""+end_date+"\" and SPECobject like \"HATS%\" and SPECtelescope=\"ANU23\""
#query_entry = query_entry + " from SPEC where SPECobject = \"HATS563-025\" "

exposure_info = mysql_query.query_hsmso(query_entry)
#print exposure_info

if len(exposure_info) > 0:
    
    for entry in exposure_info:
        output = ""

        if entry[0] == "RV":
            #output = output + entry[1] + " " #name
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
            #output = output + entry[1] + " " #name
            output = output + str(2400000 + entry[2]) + " " #mjd
            output = output + "-999 -999 " #rv rverr
            output = output + str(entry[6]) + " " #tel
            output = output + str(entry[7]) + " " #res            
            output = output + str(entry[8]) + " 300 " #teff
            #output = output + str(entry[9]) + " " 
            output = output + str(entry[10]) + " 0.3 " #logg
            #output = output + str(entry[11]) + " " 
            output = output + str(entry[12]) + " 0.5 " #feh
            output = output + "0 0 0 " #feh feherr vrot vroterr ccfheight
            output = output + str(entry[15]) + " " #exptime
            output = output + str(entry[16]) + "\n" #S/N

        print entry[1],output
        f = open("tracker_temp.txt","w")
        f.write(output)
        f.close()

        candidate = entry[1]
        
        tracker_command = "./updatecandidate.py -c "+candidate

        os.system(tracker_command)




####################
### RV Standards ###
####################

query_entry = "select SPECtype,SPECobject,SPECmjd,SPEChjd,SPECrv,SPECrv_err,SPECtelescope,SPECresolution,SPECteff,SPECteff_err,SPEClogg,SPEClogg_err,SPECfeh,SPECfeh_err,SPECccfheight,SPECexptime,SPECsn"
query_entry = query_entry + " from SPEC where SPECutdate >= \""+start_date+"\" and SPECutdate <=\""+end_date+"\" and SPECinstrum=\"echelle\""
query_entry = query_entry + " and (SPECobject=\"HD100623\""
query_entry = query_entry + " or SPECobject=\"HD97343\""
query_entry = query_entry + " or SPECobject=\"HD96700\""
query_entry = query_entry + " or SPECobject=\"HD37213\""
query_entry = query_entry + " or SPECobject=\"HD34721\""
query_entry = query_entry + " or SPECobject=\"HD196761\""
query_entry = query_entry + " or SPECobject=\"HD189625\""
query_entry = query_entry + " or SPECobject=\"HD198802\""
query_entry = query_entry + ")"

exposure_info = mysql_query.query_hsmso(query_entry)
#print exposure_info

if len(exposure_info) > 0:
    
    for entry in exposure_info:
        output = ""
        if entry[0] == "RV":
            #output = output + entry[1] + " " #name
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
            #output = output + entry[1] + " " #name
            output = output + str(2400000 + entry[2]) + " " #mjd
            output = output + "-999 -999 " #rv rverr
            output = output + str(entry[6]) + " " #tel
            output = output + str(entry[7]) + " " #res            
            output = output + str(entry[8]) + " 300 " #teff
            #output = output + str(entry[9]) + " " 
            output = output + str(entry[10]) + " 0.3 " #logg
            #output = output + str(entry[11]) + " " 
            output = output + str(entry[12]) + " 0.5 " #feh
            output = output + "0 0 0 " #feh feherr vrot vroterr ccfheight
            output = output + str(entry[15]) + " " #exptime
            output = output + str(entry[16]) + "\n" #S/N

        print entry[1],output
        f = open("tracker_temp.txt","w")
        f.write(output)
        f.close()

        candidate = entry[1]
        
        tracker_command = "./updatecandidate.py -c "+candidate

        os.system(tracker_command)

