import string
import functions
import sys

##############################
### Check RV_Standard_list ###
##############################

### Usage: python check_RV_list.py RV_standard_list

RV_Standard_list = functions.read_ascii(sys.argv[1])

if RV_Standard_list == []:
    print "False"
else:
    print "True"
