import mysql_query
#include <iostream>
import functions
import os
import sys
import string

date = "2014-10-01"
#CAMERA red ### WiFeS camera (red/blue)
#GRATING B3000 ### WiFeS grating (B3000/R3000/R7000/I7000)

query_entry = "select SPECobject,SPECtelescope,SPECinstrum,SPECresolution,SPECtype,SPECutdate from SPEC where SPECutdate>\""+date + "\" and SPECobject like \"HATS%\" and SPECtelescope = \"ANU23\""

query_output = mysql_query.query_hsmso(query_entry)

for entry in query_output:
    object_name = entry[0]
    telescope = entry[1]
    instrument = entry[2]
    grating = entry[3]
    obstype = entry[4]
    date = entry[5]
    if instrument == "echelle" and telescope == "ANU23" and obstype == "RV":
        obstype = "RV"
    if instrument == "WiFeS" and obstype == "RV" and telescope == "ANU23":
        obstype = "RECON_RV"
    if obstype == "ST" and telescope == "ANU23":
        obstype = "RECON_SPECTYPE"
    
    print object_name,date,telescope,instrument,"NULL",grating,"Zhou","Bayliss",obstype
