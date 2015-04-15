import functions
import os
import sys
import mysql_query
import string
from numpy import *
import pyfits
import matplotlib.pyplot as plt

###################
### Description ###
###################

### Plots the object RV vs BIS
### Points are taken from the HSMSO database

### usage: python plot_candidate_bis.py object_name [oname.pdf]


object_name = sys.argv[1]
query_entry = "select SPECbis, SPECrv, SPECrv_err from SPEC where SPECtype=\"RV\" and SPECobject=\"%s\" " % object_name
data = mysql_query.query_hsmso(query_entry)
data = array(data)
print data

plt.errorbar(data[:,1],data[:,0],xerr=data[:,2],linestyle="none",marker="o")
plt.xlabel("RV (km/s)")
plt.ylabel("BIS (km/s)")
plt.title(object_name+" BIS")

if len(sys.argv) == 3:
    plt.savefig(sys.argv[2])

plt.show()
