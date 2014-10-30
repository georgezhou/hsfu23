from pyraf import iraf
from numpy import *
import string
import sys
import os
import matplotlib.pyplot as plt

def quit_figure(event):
    if event.key=="q":
        plt.close(event.canvas.figure)


### Check of number is NaN
def isnan(num):
    return num == num

### Check if string is number
def is_number(s):
    test = False
    try:
        float(s)
        test = True
    except ValueError:
        test = False

    if test:
        test = isnan(s)
    return test

### Read ascii file function
def read_ascii(file_location):
    ascii_file_temp = []
    ascii_file = open(file_location).read()
    ascii_file = string.split(ascii_file,"\n")
    for i in range(len(ascii_file)):
        if not ascii_file[i] == "":
            if not ascii_file[i][0] == "#":
                ascii_file_temp.append(ascii_file[i])
    return ascii_file_temp

### Tables are passed on from read_ascii to read_table
def read_table(input_list):
    for i in range(len(input_list)):
        input_list[i] = string.split(input_list[i])
        input_list_temp = []
        for j in range(len(input_list[i])):
            if not input_list[i][j] == "":
                input_list_temp.append(input_list[i][j])
        input_list[i] = input_list_temp
        for j in range(len(input_list[i])):
            if is_number(input_list[i][j]):
                input_list[i][j] = float(input_list[i][j])
    return input_list

### Write table to output_file
def write_table(table,output_file):
    for i in range(len(table)):
        line_i = ""
        for j in range(len(table[i])):
            line_i = line_i + str(table[i][j]) + " "
        line_i = line_i + "\n"
        output_file.write(line_i)

### Write string to output file
def write_string_to_file(input_string,output_file):
    output_file = open(output_file,"w")
    output_file.write(input_string)
    output_file.close()

### Read field in config_file
def read_config_file(field):
    os.system("grep " + field + " config_file | awk '{print $2}' > temp")
    field_entry = open("temp").read()
    field_entry = string.split(field_entry)[0]
    os.system("rm temp")
    return field_entry

### Read field in param_file
def read_param_file(field):
    os.system("grep " + field + " param_file | awk '{print $2}' > temp")
    field_entry = open("temp").read()
    field_entry = string.split(field_entry)[0]
    os.system("rm temp")
    return field_entry

### takes raw ccdlist output and turns it into format of 
### [file_location,object]
def ccdlist_extract(ccdlist_info):
    for i in range(len(ccdlist_info)):
        ccdlist_info[i] = string.split(ccdlist_info[i],":")
        ccdlist_info[i][0] = string.split(ccdlist_info[i][0],"[")
        ### Identify the actual file name, excluding the path
        ccdlist_info_i = string.split(ccdlist_info[i][0][0],"/")
        ccdlist_info_file_name = ccdlist_info_i[len(ccdlist_info_i)-1]
        ccdlist_info_file_name = string.split(ccdlist_info_file_name,'.')
        ccdlist_info_file_name = ccdlist_info_file_name[0] #we don't want the .fits part
        ccdlist_info[i] = [ccdlist_info[i][0][0],ccdlist_info[i][1],ccdlist_info_file_name]
    return ccdlist_info

### takes output from ccdlist_extract and identifies 
### images of objects matching string target
### outputs list location of those images
def ccdlist_identify(ccdlist_info,target):
    match = []
    for i in range(len(ccdlist_info)):
        if ccdlist_info[i][1] == target:
            match.append(i)
    return match

### takes output from ccdlist_extract and identifies 
### objects starting with HD
def ccdlist_identify_HD(ccdlist_info):
    match = []
    for i in range(len(ccdlist_info)):
        if ccdlist_info[i][1][:2] == "HD":
            match.append(i)
    return match

### Sort array according to a specific column
def sort_array(input_array,column):
    column_to_sort = transpose(input_array)[column]
    sorted_indicies = column_to_sort.argsort()
    temp_array = []
    for index in sorted_indicies:
        temp_array.append(input_array[index])
    return temp_array

### Round value
### eg. round 2456 to nearest 250: round_value(2456,250) = 2500
def round_value(value,round_step):
    value = value / round_step
    value = round(value)
    value = value * round_step
    return value
    
### Calculate teff from J-K Colour
### Connect to HSCAND database in princeton
import mysql_query
def teff_from_colour(candidate):
    print "Connecting to HSCAND to retrieve J-K colour to estimate teff"
    query_command = "select HATSmagJ, HATSmagK from HATS where HATSname = \'"+ candidate + "\'"

    try:
        query_output = mysql_query.query_hscand(query_command)
    except IOError:
        query_output = []


    if len(query_output) > 1:
        magJ = query_output[1][0]
        magK = query_output[1][1]

        ### Use thesis results to calculate teff
        teff = -3590. * (magJ - magK) + 7290.
        return teff
        
    else:
        print "ERROR: Cannot connect or candidate does not exist"
        return "INDEF"

### Determine the best estimate of teff and logg
### Priority of source
### 2.3m follow-up teff and logg
### J-K colour for teff, and default logg
### Default teff and logg from config_file
### Inputs: estimate_teff_logg(candidate,hscand_connect,default_teff,default_logg)
# def estimate_teff_logg(candidate,hscand_connect,default_teff,default_logg):
#     ### If dont connect with hscand
#     if hscand_connect == "false":
#         print "Using default teff and logg"
#         return int(round_value(default_teff,250)), round_value(default_logg,0.5)

#     ### If using hscand
#     if hscand_connect == "true":
#         print "Estimating teff via J-K Colour"
#         teff = teff_from_colour(candidate)
#         if not teff == "INDEF":
#             return int(round_value(teff,250)),round_value(default_logg,0.5)
#         else:
#             return int(round_value(default_teff,250)),round_value(default_logg,0.5)

def estimate_teff_logg(file_path,file_name,candidate,hsmso_connect,hscand_connect,default_teff,default_logg):
    found_properties = False

    if hsmso_connect == "true":
        print "Query HSMSO"
        query_entry = "select SPECteff, SPEClogg, SPECsn from SPEC where SPECtype=\"ST\" and SPECobject=\"%s\" " % candidate
        hsmso_result = mysql_query.query_hsmso(query_entry)

        if len(hsmso_result) > 0:
            found_properties = True
            hsmso_result = transpose(hsmso_result)
            for i in range(len(hsmso_result[0])):
                if hsmso_result[2][i] == max(hsmso_result[2]):
                    teff = int(round_value(hsmso_result[0][i],250))
                    logg = round_value(hsmso_result[1][i],0.5)
                    break
        else:
            print "ERROR: cannot find an entry for " + candidate + " in HSMSO"

    if not found_properties and hscand_connect == "true":
        print "Query HSCAND"
        teff = teff_from_colour(candidate)
        if not teff == "INDEF":
            found_properties = True
            teff = int(round_value(teff,250))
            logg = round_value(default_logg,0.5)
            if teff < 3500:
                found_properties = False

    if not found_properties:
        import twomass_colour
        teff = twomass_colour.teff_from_2mass(file_path,file_name)
        if not teff == "INDEF":
            found_properties = True
            teff = int(round_value(teff,250))
            logg = round_value(default_logg,0.5)
            if teff < 3500:
                found_properties = False

    if not found_properties:
        print "Using default teff logg values"
        teff = int(round_value(default_teff,250))
        logg = round_value(default_logg,0.5)

    if logg > 5.0:
        logg = 5.0
    if logg < 0.0:
        logg = 0.0
    
    return teff,logg
