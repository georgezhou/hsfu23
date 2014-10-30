import functions
import mysql_query
from numpy import *
import os
import sys
import string
import pyfits

start_date = "2014-10-01"
end_date = "2014-10-31"

program_dir = os.getcwd() + "/" #Save the current working directory

### Deal with RV observations

query_entry = "select distinct SPECobject"
query_entry = query_entry + " from SPEC where SPECutdate >= \""+start_date+"\" and SPECutdate <=\""+end_date+"\" and SPECtelescope=\"ANU23\""
query_entry = query_entry + " and SPECobject like \"HATS%\""
query_entry = query_entry + " ORDER BY SPECobject"

print query_entry


candidate_list = mysql_query.query_hsmso(query_entry)

for entry in candidate_list:
    candidate = entry[0]
    
    query_entry = "select SPECteff,SPEClogg,SPECfeh"
    query_entry = query_entry + " from SPEC where SPECobject = \""+candidate+"\""
    query_entry = query_entry + " and SPECtype = \"ST\""
    ST = mysql_query.query_hsmso(query_entry)

    if len(ST) == 0:
        ST_report = "No ST Obs"

    if len(ST) == 1:
        ST_report = "Teff="
        ST_report += str(round(float(ST[0][0])))
        ST_report += " logg="
        ST_report += str(float(ST[0][1]))    
        ST_report += " [Fe/H]="
        ST_report += str(float(ST[0][2]))

    if len(ST) > 1:
        ST_report = "Multiple obs, check!"

    ##########

    query_entry = "select SPECrv"
    query_entry = query_entry + " from SPEC where SPECobject = \""+candidate+"\""
    query_entry = query_entry + " and SPECtype = \"RV\""
    RV = mysql_query.query_hsmso(query_entry)    

    if len(RV) == 0:
        RV_report = "No RV observations"
    if len(RV) == 1:
        RV_report = "1 RV observation"
    if len(RV) > 1:
        RV_report = str(len(RV))+" RV observations"

    print candidate
    print ST_report
    print RV_report
    print "\n"
