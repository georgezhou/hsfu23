import string
import functions
import sys

##############################
### Check SpechPhot_list ###
##############################

### Usage: python check_SpecPhot_list.py SpecPhot_list

SpecPhot_list = functions.read_ascii(sys.argv[1])

if SpecPhot_list == []:
    print "False"
else:
    print "True"
