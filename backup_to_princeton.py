import functions
import os
import sys
import string
import mysql_query
#from pyraf import iraf
import pyfits

def remove_nonhs(file_path):
    file_list = os.system("ls "+file_path+"*.fits > file_list")
    file_list = open("file_list").read()
    file_list = string.split(file_list)
    for file_name in file_list:
        hdulist = pyfits.open(file_name)
        object_name = hdulist[0].header["OBJECT"]
        comments = hdulist[0].header["NOTES"]
        hdulist.close()

        if not (object_name[:4] == "HATS" or object_name == "Ne-Ar" or object_name == "Flat" or object_name == "bias") and not (comments == "RV Standard" or comments == "SpecPhot"):
            print file_name,object_name,comments
            os.system("rm "+file_name)

    #sys.exit()

def upload(file_path,dateformat):
    file_path_RV = file_path + "/RV/red/"
    file_path_spectype = file_path + "/spectype/blue/"

    ### Do raw files first
    print "Zipping raw files"
    os.chdir(file_path)
    os.system("rm -rf "+dateformat+"*")
    os.system("mkdir "+dateformat)
    os.system("mkdir "+dateformat+"/spectype/")
    os.system("mkdir "+dateformat+"/RV/")

    os.system("cp "+file_path_spectype+"*.fits "+dateformat+"/spectype/")
    os.system("cp "+file_path_RV+"*.fits "+dateformat+"/RV/")

    remove_nonhs(dateformat+"/RV/")
    remove_nonhs(dateformat+"/spectype/")

    os.system("tar -pczf "+dateformat+".tar.gz "+dateformat+"/")

    ### Upload to princeton
    print "Uploading to princeton"
    os.system("ssh gzhou@hatsouth.astro.princeton.edu \'mkdir /S/HSFU/anu23/wifes/RAW/"+dateformat+"\'")
    os.system("scp "+dateformat+".tar.gz gzhou@hatsouth.astro.princeton.edu:/S/HSFU/anu23/wifes/RAW/"+dateformat+"/")

    os.system("rm -rf "+dateformat+"*")

    ### Upload reduced files
    print "Zipping reduced files"
    os.chdir(file_path)
    os.system("rm -rf "+dateformat+"*")
    os.system("mkdir "+dateformat)
    os.system("mkdir "+dateformat+"/spectype/")
    os.system("mkdir "+dateformat+"/RV/")

    os.system("cp "+file_path_spectype+"reduced/fluxcal*.fits "+dateformat+"/spectype/")
    os.system("cp "+file_path_RV+"reduced/normspec*.fits "+dateformat+"/RV/")

    remove_nonhs(dateformat+"/RV/")
    remove_nonhs(dateformat+"/spectype/")

    os.system("tar -pczf "+dateformat+".tar.gz "+dateformat+"/")

    ### Upload to princeton
    print "Uploading to princeton"
    os.system("ssh gzhou@hatsouth.astro.princeton.edu \'mkdir /S/HSFU/anu23/wifes/RED/"+dateformat+"\'")
    os.system("scp "+dateformat+".tar.gz gzhou@hatsouth.astro.princeton.edu:/S/HSFU/anu23/wifes/RED/"+dateformat+"/")

    os.system("rm -rf "+dateformat+"*")

    #sys.exit()

query_entry = "select distinct SPECutdate from SPEC where SPECutdate >= \"2015-02-01\" and SPECutdate <= \"2015-02-30\" and SPECinstrum = \"WiFeS\""
query_result = mysql_query.query_hsmso(query_entry)

month_list = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

count = 1
for i in query_result:
    thedate = str(i[0])
    year = string.split(thedate,"-")[0]
    month = int(string.split(thedate,"-")[1])
    month = month_list[month-1]
    date = string.split(thedate,"-")[2]
    file_path = "/priv/mulga2/george/wifes/" + date + month + year +"/"

    dateformat = string.split(thedate,"-")
    dateformat = dateformat[0]+dateformat[1]+dateformat[2]
    print file_path,dateformat
    
    upload(file_path,dateformat)
    
