import functions
import mysql_query
from numpy import *
import os
import sys
import string
import pyfits

start_date = "2012-04-10"
end_date = "2012-04-15"

program_dir = os.getcwd() + "/" #Save the current working directory

os.system("mkdir outputs")
os.system("rm -rf outputs/*")

month_list = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

### Deal with RV observations

query_entry = "select SPECutdate,SPECimgname,SPECobject,SPEChjd,SPECrv,SPECrv_err,SPECccfheight,SPECbis,SPECbis_err"
query_entry = query_entry + " from SPEC where SPECutdate >= \""+start_date+"\" and SPECutdate <=\""+end_date+"\" and SPECobject like \"HATS%\" and SPECtype = \"RV\""

exposure_info = mysql_query.query_hsmso(query_entry)

if len(exposure_info)>0:
    os.system("mkdir outputs/RV_plots")
    os.system("mkdir outputs/ccf_plots")

    for i in exposure_info:

        candidate_name = i[2]
        file_name = i[1]
        thedate = str(i[0])
        year = string.split(thedate,"-")[0]
        month = int(string.split(thedate,"-")[1])
        month = month_list[month-1]
        date = string.split(thedate,"-")[2]
        file_path = "/mimsy/george/wifes/" + date + month + year +"/RV/red/"

        print file_path,file_name,candidate_name
        os.system("mkdir outputs/ccf_plots/"+candidate_name)

        os.system("cp " + file_path + "reduced/ccf_pdfs/ccf_" + file_name + ".pdf outputs/ccf_plots/"+candidate_name+"/"+str(i[3])+".pdf")
        os.system("cp /mimsy/george/wifes/candidates/RV_plots/"+candidate_name+".pdf outputs/RV_plots/")

    os.chdir("outputs/RV_plots/")
    os.system("gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=RV_ANU23.pdf HATS*.pdf")

    os.chdir(program_dir)
    os.chdir("outputs/")
    os.system("cp RV_plots/RV_ANU23.pdf .")
    os.system("tar -cvzpf ccf_plots.tar.gz ccf_plots/")

    RV_dat = open("temp.dat","w")
    RV_dat.write("#utdate imagename #candidate hjd RV(km/s) RVerr(km/s) ccf_height bis(km/s) bis_err(km/s)\n")
    functions.write_table(exposure_info,RV_dat)
    RV_dat.close()
    os.system("cat temp.dat | awk '{print $3,$4,$5,$6,$7,$8,$9}' > RV_ANU23.dat")
    os.system("rm temp.dat")

################ Deal with spectral typing observations
os.chdir(program_dir)

query_entry = "select SPECutdate,SPECobject,SPECteff,SPEClogg"
query_entry = query_entry + " from SPEC where SPECutdate >= \""+start_date+"\" and SPECutdate <=\""+end_date+"\" and SPECobject like \"HATS%\" and SPECtype = \"ST\""

exposure_info = mysql_query.query_hsmso(query_entry)

if len(exposure_info)>0:
    os.system("mkdir outputs/spectype/")

    for i in exposure_info:

        candidate_name = i[1]
        thedate = str(i[0])
        year = string.split(thedate,"-")[0]
        month = int(string.split(thedate,"-")[1])
        month = month_list[month-1]
        date = string.split(thedate,"-")[2]
        file_path = "/mimsy/george/wifes/" + date + month + year +"/spectype/blue/"

        os.system("cp "+file_path+"reduced/spectype_plots/"+candidate_name+"_contour.pdf outputs/spectype/")
        os.system("cp "+file_path+"reduced/spectype_plots/"+candidate_name+"_spectrum.pdf outputs/spectype/")

    os.chdir("outputs/spectype/")
    os.system("gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=spectype.pdf HATS*.pdf")

    os.chdir(program_dir)
    os.chdir("outputs/")
    os.system("cp spectype/spectype.pdf .")

    spectype_dat = open("temp.dat","w")
    spectype_dat.write("#utdate #candidate teff(K) logg\n")
    functions.write_table(exposure_info,spectype_dat)
    spectype_dat.close()
    os.system("cat temp.dat | awk '{print $2,$3,$4}' > spectype.dat")
    os.system("rm temp.dat")
