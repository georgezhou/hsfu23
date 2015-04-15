import os,sys,functions,mysql_query,string
from numpy import *

query = "select SPECimgname,SPECutdate from SPEC where SPECutdate > \"2014-01-01\" and SPECtype=\"RV\" and SPECcomment=\"RV Standard\" and SPECinstrum=\"WiFeS\""
query_result = mysql_query.query_hsmso(query)

month_list = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

for i in query_result:

    try:
        file_name = i[0]
        file_name = string.split(file_name,"A_")[1]
        thedate = str(i[1])
        year = string.split(thedate,"-")[0]
        month = int(string.split(thedate,"-")[1])
        month = month_list[month-1]
        date = string.split(thedate,"-")[2]
        file_path = "/priv/mulga2/george/wifes/" + date + month + year +"/RV/red/"

        print file_path,file_name
        os.system("./main.csh "+file_path+" "+file_name)

    except IndexError:
        pass
