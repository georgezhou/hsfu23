from numpy import *
import functions
import os
import sys

candidate = "HATS562-002"
#parent_dir = "/priv/miner3/hat-south/george/Honours/data/wifes/2011/"
parent_dir = "/mimsy/george/wifes/"

### Import the database file and find the candidate exposures
database = functions.read_ascii("database.txt")
database = functions.read_table(database)

os.system("rm RV.dat")
#os.system("rm aperture_RV.dat")

month_list = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

RV_dat_list = []

### Format = #HJD file_name ap1 RV ap2 RV
#aperture_RV = []

os.chdir("..")

### Loop through each exposure
for exposure in database:
    if exposure[0] == candidate:
        file_name = exposure[1]
        year = exposure[2][:4]
        month = exposure[2][5:7]
        month = month_list[int(month)-1]
        date = exposure[2][8:10]
        
        folder = date + month + year + "/red/"
        file_path = parent_dir + folder

        print file_path + " " + file_name
        os.system("rm -rf " + file_path + "reduced")
        os.system("rm -rf " + file_path + "temp")
        os.system("./main.csh " + file_path + " " + file_name)

        if os.path.exists(file_path + "reduced/RV.dat") and os.path.exists(file_path + "reduced/RV_out.dat"):

            RV_dat = functions.read_ascii(file_path + "reduced/RV.dat")
            RV_dat = functions.read_table(RV_dat)

            RV_dat_list.append(RV_dat[0])

            # stellar_apertures = functions.read_ascii(file_path + "temp/stellar_apertures.txt")
            # stellar_apertures = functions.read_table(stellar_apertures)

            # RV_out = functions.read_ascii(file_path + "reduced/RV_out.dat")
            # RV_out = functions.read_table(RV_out)

            # ap1_RVs = []
            # ap2_RVs = []
            # for cc in RV_out:
            #     if cc[0] == candidate and cc[4] == 1:
            #         ap1_RVs.append(cc[7])
            #         hjd = cc[3]
            #     if cc[0] == candidate and cc[4] == 2:
            #         ap2_RVs.append(cc[7])

            # if len(ap1_RVs) > 0:
            #     ap1_RVs = median(ap1_RVs)
            # else:
            #     ap1_RVs = "INDEF"

            # if len(ap2_RVs) > 0:
            #     ap2_RVs = median(ap2_RVs)
            # else:
            #     ap2_RVs = "INDEF"

            # aperture_RV.append([hjd,file_name,stellar_apertures[0][0],ap1_RVs,stellar_apertures[1][0],ap2_RVs])
        
os.chdir("test_candidate")

file_out = open("RV.dat","w")
functions.write_table(RV_dat_list,file_out)
file_out.close()

#file_out = open("aperture_RV.dat","w")
#functions.write_table(aperture_RV,file_out)
#file_out.close()        
        
print RV_dat_list
#print aperture_RV
