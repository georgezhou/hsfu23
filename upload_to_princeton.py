import functions
import os
import sys
import string
import mysql_query

def upload(file_path,dateformat):
    file_path_RV = file_path + "RV/red/"
    file_path_spectype = file_path + "spectype/blue/"

    ### Do raw files first
    os.chdir(file_path)
    os.system("rm -rf "+dateformat)
    os.system("mkdir "+dateformat)
    os.system("mkdir "+dateformat+"/spectype/")
    os.system("mkdir "+dateformat+"/RV/")

    os.system("cp "+file_path_spectype+"*.fits "+dateformat+"/spectype/")
    os.system("cp "+file_path_RV+"*.fits "+dateformat+"/RV/")

    os.system("tar -pczf "+dateformat+".tar.gz "+dateformat+"/")



query_entry = "select distinct SPECutdate from SPEC where SPECutdate >= \"2011-01-01\" and SPECutdate <= \"2012-12-31\" and SPECinstrum = \"WiFeS\""
query_result = mysql_query.query_hsmso(query_entry)

month_list = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

count = 1
for i in query_result:
    thedate = str(i[0])
    year = string.split(thedate,"-")[0]
    month = int(string.split(thedate,"-")[1])
    month = month_list[month-1]
    date = string.split(thedate,"-")[2]
    file_path = "/mimsy/george/wifes/" + date + month + year +"/"

    dateformat = string.split(thedate,"-")
    dateformat = dateformat[0]+dateformat[1]+dateformat[2]
    print file_path,dateformat
    
    upload(file_path,dateformat)

    break
    
