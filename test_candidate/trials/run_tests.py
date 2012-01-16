import functions
import os
import sys
from numpy import *
import matplotlib.pyplot as plt

def rms(input_list):
    rms = sqrt(sum(input_list**2) / len(input_list))
    return rms

def to_numbers(input_list):
    temp = []
    for i in input_list:
        temp.append(eval(i))
    return temp

#trial_no = "trial8"

trial_no = sys.argv[1]
               
RV = functions.read_ascii(trial_no + ".dat")
RV = functions.read_table(RV)

RV = transpose(RV)

RV_values = array(to_numbers(RV[3])) - median(to_numbers(RV[3]))
RV_err = to_numbers(RV[4])
ccf_height = to_numbers(RV[5])

print "RV RMS = ", rms(RV_values)
plt.clf()
plt.hist(RV_values,bins=10,histtype="step",hatch="/")
plt.xlabel("RV")
plt.show()

print "Median RV err = ", median(RV_err)
plt.clf()
plt.hist(RV_err,bins=10,histtype="step",hatch="/")
plt.xlabel("RV Error")
plt.show()

print "Median CCF height = ", median(ccf_height)
plt.clf()
plt.hist(ccf_height,bins=10,histtype="step",hatch="/")
plt.xlabel("CCF Height")
plt.show()
