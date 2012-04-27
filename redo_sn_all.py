from numpy import *
import string
import sys
import os
import functions
import mysql_query

print "Query HSMSO"
query_entry = "select SPECutdate, SPECimgname from SPEC where SPECtype=\"RV\""
hsmso_result = mysql_query.query_hsmso(query_entry)

month_list = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

for entry in hsmso_result:
    year = str(entry[0].year)
    month = month_list[entry[0].month - 1]
    day = str(entry[0].day)
    if entry[0].day < 10:
        day = "0"+day

    file_path = "/mimsy/george/wifes/"

    if float(year) == 2010:
        file_path = file_path + "2010/"

    else:
        file_path = file_path + day+month+year
        file_path = file_path + "/RV/red/"

    file_name = entry[1]

    print file_path,file_name
    if entry[0].day < 10:
        os.system("./redo_sn.csh "+file_path+" "+file_name)
