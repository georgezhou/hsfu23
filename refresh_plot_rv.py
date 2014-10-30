import functions
import mysql_query
from numpy import *
import os
import sys
import string
import pyfits

start_date = "2013-12-01"
end_date = "2013-12-31"

query_entry = "select distinct SPECobject"
query_entry = query_entry + " from SPEC where SPECutdate >= \""+start_date+"\" and SPECutdate <=\""+end_date+"\" and SPECobject like \"KS%\" and SPECtelescope=\"ANU23\""
#query_entry = query_entry + " from SPEC where SPECobject = \"HATS563-025\" "
query_entry += " and SPECtype = \"RV\""


exposure_info = mysql_query.query_hsmso(query_entry)
#print exposure_info

if len(exposure_info) > 0:
    
    for entry in exposure_info:
        os.system("python plot_cand_RV.py -o "+entry[0])
