import os
import sys
import functions
from numpy import *

file_path = sys.argv[1]
file_name = sys.argv[2]
csh_script = sys.argv[3]

try:
    nostars = len(functions.read_ascii(file_path+"temp/master_coo"))
except IOError:
    nostars = 1

for i in range(nostars):
    suffix = unichr(65+i)

    os.system("./"+csh_script+" "+file_path+" "+suffix+"_"+file_name)
    
