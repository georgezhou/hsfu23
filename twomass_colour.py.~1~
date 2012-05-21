### Load python modules
from numpy import *
import string
import sys
import os
import pyfits
import urllib

### Load functions script (located in the same folder)
import functions

###################
### Description ###
###################

### Query 2mass for J-K temp

### Usage: python twomass_colour.py file_path file_name

#################
### Functions ###
#################
# Convert HH:MM:SS.SSS into Degrees :
def convHMS(ra):
   try :
      sep1 = ra.find(':')
      hh=int(ra[0:sep1])
      sep2 = ra[sep1+1:].find(':')
      mm=int(ra[sep1+1:sep1+sep2+1])
      ss=float(ra[sep1+sep2+2:])
   except:
      raise
   else:
      pass
   
   return(hh*15.+mm/4.+ss/240.)

# Convert +DD:MM:SS.SSS into Degrees :
def convDMS(dec):

   Csign=dec[0]
   if Csign=='-':
      sign=-1.
      off = 1
   elif Csign=='+':
      sign= 1.
      off = 1
   else:
      sign= 1.
      off = 0

   try :
      sep1 = dec.find(':')
      deg=int(dec[off:sep1])
      sep2 = dec[sep1+1:].find(':')
      arcmin=int(dec[sep1+1:sep1+sep2+1])
      arcsec=float(dec[sep1+sep2+2:])
   except:
      raise
   else:
      pass

   return(sign*(deg+(arcmin*5./3.+arcsec*5./180.)/100.))

def try_webpage(url):
    try:
        urllib.urlopen(url)
        return True
    except IOError:
        return False

def find_2mass(ra,dec):
    print "Trying ",ra,dec

    ra = convHMS(ra)
    dec = convDMS(dec)
    
    ra = str(ra)
    if dec >= 0:
        dec = "+"+str(dec)
    else:
        dec = str(dec)

    page_url = "http://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query?outfmt=1&objstr="
    page_url = page_url + ra +"+" +dec
    page_url = page_url + "&spatial=Cone&radius=60&radunits=arcsec&catalog=fp_psc&selcols=ra,dec,j_m,h_m,k_m "

    print page_url

    if try_webpage(page_url):

        twomass = urllib.urlopen(page_url)
        twomass = twomass.read()

        if twomass.find("ERROR") == -1:

            twomass = string.split(twomass,"\n")
            twomass_temp = []
            for i in twomass:
                if not i == "":
                    if not (i[0] == "|" or i[0] == "\\"):
                        twomass_temp.append(i)

            if not twomass_temp == []:

                twomass = functions.read_table(twomass_temp)

                dist = transpose(twomass)[8]
                dist_temp = []
                for i in dist:
                    dist_temp.append(float(i))
                dist = dist_temp

                for star in twomass:
                    if float(star[8]) == min(dist):
                        print "Found star with distance of ",min(dist)
                        magJ = float(star[4])
                        magK = float(star[6])
                        teff = -3590. * (magJ - magK) + 7290.
                        print "2MASS temp of",teff
                        break
            else:
                print "Could not find star"
                teff = "INDEF"
        else:
            print "Could not connect to 2mass catalogue"
            teff = "INDEF"           
                    
    else:
        print "Could not connect to 2mass catalogue"
        teff = "INDEF"
    
    return teff

########################
### Start of program ###
########################

def teff_from_2mass(file_path,file_name):

    hdulist = pyfits.open(file_path + file_name)
    object_name = hdulist[0].header["OBJECT"]
    ra = hdulist[0].header["RA"]
    dec = hdulist[0].header["DEC"]
    hdulist.close()

    print "Query 2mass catalogue for colours to ",object_name,ra,dec
    teff = find_2mass(ra,dec)
    return teff

