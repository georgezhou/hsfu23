import os,sys,functions,string
from numpy import *
import mysql_query
from pyraf import iraf

SPECobject = "PTFO8-8695"
SPECtype = "RV"

output_folder = "/mimsy/george/wifes/PTF_spectra/"

os.system("mkdir "+output_folder)
os.system("mkdir "+output_folder+"temp")
os.system("mkdir "+output_folder+"reduced")

query = "select SPECimgname,SPECutdate from SPEC"
query += " where SPECtype=\""+SPECtype+"\""
query += " and SPECobject =\""+SPECobject+"\""

print query
query_result = mysql_query.query_hsmso(query)
print query_result

month_list = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

for i in range(len(query_result)):

    file_name = query_result[i][0]
    thedate = str(query_result[i][1])
    year = string.split(thedate,"-")[0]
    month = int(string.split(thedate,"-")[1])
    month = month_list[month-1]
    date = string.split(thedate,"-")[2]
    file_path = "/mimsy/george/wifes/" + date + month + year +"/RV/red/reduced/"

    spec = file_path + "spec_"+file_name
    normspec = file_path + "normspec_"+file_name
    print normspec


    os.system("cp "+spec+" "+output_folder+""+str(i)+".fits")    
    os.system("cp "+spec+" "+output_folder+"reduced/spec_A_"+str(i)+".fits")
    os.system("cp "+normspec+" "+output_folder+"reduced/normspec_A_"+str(i)+".fits")

    
    if i ==0:
        iraf.hedit(
            images = output_folder+"0.fits",\
            fields = "NOTES",\
            value = "RV Standard",\
            add = 1,\
            addonly = 0,\
            delete = 0,\
            verify = 0,\
            show = 1,\
            update =1)

        iraf.hedit(
            images = output_folder+"0.fits",\
            fields = "VHELIO",\
            value = "0.0",\
            add = 1,\
            addonly = 0,\
            delete = 0,\
            verify = 0,\
            show = 1,\
            update =1)

        iraf.hedit(
            images = output_folder+"reduced/normspec_A_0.fits",\
            fields = "NOTES",\
            value = "RV Standard",\
            add = 1,\
            addonly = 0,\
            delete = 0,\
            verify = 0,\
            show = 1,\
            update =1)

        iraf.hedit(
            images = output_folder+"reduced/normspec_A_0.fits",\
            fields = "VHELIO",\
            value = "0.0",\
            add = 1,\
            addonly = 0,\
            delete = 0,\
            verify = 0,\
            show = 1,\
            update =1)

        iraf.hedit(
            images = output_folder+"reduced/spec_A_0.fits",\
            fields = "NOTES",\
            value = "RV Standard",\
            add = 1,\
            addonly = 0,\
            delete = 0,\
            verify = 0,\
            show = 1,\
            update =1)

        iraf.hedit(
            images = output_folder+"reduced/spec_A_0.fits",\
            fields = "VHELIO",\
            value = "0.0",\
            add = 1,\
            addonly = 0,\
            delete = 0,\
            verify = 0,\
            show = 1,\
            update =1)



    os.system("python run_csh_script.py "+output_folder+" "+str(i)+".fits radial_velocity.csh")
