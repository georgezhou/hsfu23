import os
import sys
import string
import functions

### This is a program meant for testing!
### usage: python run_spectype_all.py

file_path = functions.read_config_file("FILE_PATH")

program_dir = os.getcwd() + "/"
os.chdir(file_path + "/reduced/")

os.system("ls fluxcal_*.fits > file_list")
file_list = functions.read_ascii("file_list")
os.system("rm file_list")

os.chdir(program_dir)

for file_name in file_list:
    file_name = string.split(file_name,"_")
    file_name = file_name[1]
    print "******"
    print file_name
    os.system("python spectype_main.py " + file_path + " " + file_name)


