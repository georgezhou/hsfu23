import string
import os

os.system("ls HD* > temp")
files = open("temp").read()
files = string.split(files,"\n")
files_temp = []
for i in range(len(files)):
    if not files[i] == "":
        files_temp.append(files[i])
files = files_temp

for i in range(len(files)):
    name = string.split(files[i],"HD")[1]
    name = "hd" + name
    os.system("cp -f " + files[i] + " " + name)

os.system("rm temp")
