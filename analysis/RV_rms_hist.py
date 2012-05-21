from numpy import *
import os
import sys
import matplotlib.pyplot as plt
import functions
import mysql_query

def rms(input_array):
    values = []
    for i in input_array:
        values.append(i)
    values = array(values)
    values = values - mean(values)
    numerator = sum(values**2)
    rms_val = sqrt(numerator / len(values))
    return rms_val

i = 0.0
rms_ax = []
while i < 5.0:
    rms_ax.append(i)
    i = i + 0.5

###############################
### Plot Flat HS candidates ###
###############################

hscand_q = "select HATSname from HATS where HATSclass NOT LIKE '%EB%' and HATSclass NOT LIKE '%TR%'"
print hscand_q
good_candidates = mysql_query.query_hscand(hscand_q)
good_candidates = good_candidates[1:]

candidates_RMS = []
for candidate in good_candidates:
    candidate_name = candidate[0]
    hsmso_q = "select SPECrv from SPEC where SPECobject=\"" + candidate_name +"\" and SPECtype=\"RV\""
    candidate_RV = mysql_query.query_hsmso(hsmso_q)

    if len(candidate_RV) > 2:
        candidates_RMS.append(rms(candidate_RV))
        if rms(candidate_RV) > 5.0:
            print candidate_name

plt.hist(candidates_RMS,bins=rms_ax,histtype="step",hatch="/",color="b")
print max(candidates_RMS),median(candidates_RMS),min(candidates_RMS)

rms_out = open("candidate_rms.txt","w")
functions.write_table([candidates_RMS],rms_out)
rms_out.close()

#########################
### Plot RV Standards ###
#########################
query = "select distinct SPECobject from SPEC where SPECtype = \"RV\" and SPECcomment=\"RV Standard\""

RV_standards = mysql_query.query_hsmso(query)

RV_standards_RMS = []
for i in RV_standards:
    object_name = i[0]
    hsmso_q = "select SPECrv from SPEC where SPECobject=\"" + object_name +"\" and SPECtype=\"RV\""
    object_RV = mysql_query.query_hsmso(hsmso_q)

    if len(object_RV) > 2:
        RV_standards_RMS.append(rms(object_RV))

plt.hist(RV_standards_RMS,bins=rms_ax,histtype="step",hatch="/",color="r")
print max(RV_standards_RMS),median(RV_standards_RMS),min(RV_standards_RMS)

####################
### Plot options ###
####################

plt.xlabel("RV RMS (km/s)")
plt.ylabel("N")
plt.show()


    