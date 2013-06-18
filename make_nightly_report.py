import mysql_query
import functions
import os
import sys
import string

date = "2013-05-01"

query_entry = "select SPECobject,SPECtelescope,SPECinstrum,SPECresolution,SPECtype from SPEC where SPECutdate>\""+date + "\" and SPECobject like \"HATS%\" and SPECtelescope = \"ANU23\""

query_output = mysql_query.query_hsmso(query_entry)

for entry in query_output:
    object_name = entry[0]
    telescope = entry[1]
    instrument = entry[2]
    grating = entry[3]
    obstype = entry[4]
    if instrument == "echelle" and telescope == "ANU23" and obstype == "RV":
        obstype = "RV"
    if instrument == "WiFeS" and obstype == "RV" and telescope == "ANU23":
        obstype = "RECON_RV"
    if obstype == "ST" and telescope == "ANU23":
        obstype = "RECON_SPECTYPE"
    
    print object_name,date,telescope,instrument,"NULL",grating,"Zhou","Bayliss",obstype
