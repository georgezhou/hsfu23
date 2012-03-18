import functions
import os
import sys
import mysql_query
import datetime
import string

#find all hot stars
query_entry = "select SPECobject,SPECimgname,SPECutdate from SPEC where SPECtype=\"ST\" and SPECobject like \"%HATS%\" and SPECteff >=5500"
query_result = mysql_query.query_hsmso(query_entry)

month_list = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

count = 1
for i in query_result:
    candidate_name = i[0]
    file_name = i[1]
    thedate = str(i[2])
    year = string.split(thedate,"-")[0]
    month = int(string.split(thedate,"-")[1])
    month = month_list[month-1]
    date = string.split(thedate,"-")[2]
    file_path = "/mimsy/george/wifes/" + date + month + year +"/spectype/blue/"
    
    print "****************"
    print candidate_name
    print "Task " + str(count) + " out of " + str(len(query_result))
    print file_path,file_name

    os.system("python spectype_main.py " + file_path + " " + file_name)
    os.system("python update_spectype.py " + file_path + " " + file_name)

    count = count + 1
