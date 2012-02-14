import functions
from numpy import *
import MySQLdb

db=MySQLdb.connect(host="marbles.anu.edu.au",user="daniel",passwd="h@ts0uthDB",db="daniel1")
print db

object_name = 'HATStest'
mjd = 55998.99
rv = 99.9

c = db.cursor()
c.execute("""SELECT SPECid FROM SPEC WHERE SPECmjd=""" + str(mjd) + """ and SPECobject=\"%s\" """ % object_name)

duplicate = c.fetchone()
if duplicate == None:
    print "Creating entry"
    c.execute("""INSERT INTO SPEC (SPECobject,SPECtelescope,SPECinstrum,SPECmjd,SPECrv) VALUES (\"%s\" """ % object_name + ""","ANU23","WIFES",""" + str(mjd) + "," + str(rv) + """)""")
else:
    print "Updating entry"
    c.execute("""UPDATE SPEC SET SPECrv=""" + str(rv) + """ WHERE SPECmjd=""" + str(mjd) + """ and SPECobject=\"%s\" """ % object_name)
