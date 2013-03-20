import os
import sys
import pyfits
import string
from pyraf import iraf

iraf.onedspec()
iraf.noao()

file_path = sys.argv[1]
file_name = sys.argv[2]
file_name_short = string.split(file_name,".")[0]

os.system("cp -f "+file_path+file_name+" "+file_path+file_name_short+"B.fits")

hdulist = pyfits.open(file_path + file_name)

mjdobs = hdulist[0].header["MJD-OBS"]
mjdobs = mjdobs + 0.000001
object_name = hdulist[0].header["OBJECT"]
object_name = object_name+"B"
hdulist.close()

iraf.hedit(
    images = file_path+file_name_short+"B.fits",\
    fields = "OBJECT",\
    value = object_name,\
    add = 0,\
    addonly = 0,\
    delete = 0,\
    verify = 0,\
    update = 1,\
    show = 1)

iraf.hedit(
    images = file_path+file_name_short+"B.fits",\
    fields = "MJD-OBS",\
    value = mjdobs,\
    add = 0,\
    addonly = 0,\
    delete = 0,\
    verify = 0,\
    update = 1,\
    show = 1)
