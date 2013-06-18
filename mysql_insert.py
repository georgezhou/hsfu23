import functions
from numpy import *
import MySQLdb
import string

### object[0],name[1],grating[2],resolution[3],dichroic[4],dateobs[5],mjd[6],hjd[7],rv[8],rv_err[9],ccf_fwhm[10],ccf_height[11],bis[12],bis_err[13],sn[14],exptime[15],comment[16]
### str[0],str[1],str[2],int[3],str[4],fits_date[5],double[6],double[7],double[8],double[9],float[10],float[11],double[12],double[13],float[14],float[15],str[16]
def db_rv_entry(object_name,file_name,grating,resolution,dichroic,dateobs,mjd,hjd,rv,rv_err,ccffwhm,ccfheight,bis,bis_err,sn,exptime,comment):

    sql_date = string.split(dateobs,"T")[0]
    sql_time = string.split(dateobs,"T")[1]

    print "Connecting to database"
    db=MySQLdb.connect(host="mutant.anu.edu.au",user="daniel",passwd="h@ts0uthDB",db="daniel1")

    c = db.cursor()
    #c.execute("""SELECT SPECid FROM SPEC WHERE SPECmjd=""" + str(mjd) + """ and SPECobject=\"%s\" """ % object_name)
    c.execute("""SELECT SPECid FROM SPEC WHERE SPECmjd=""" + str(mjd))

    duplicate = c.fetchone()
    if duplicate == None:
        print "Creating entry"
        
        command = """INSERT INTO SPEC """
        command = command+"""(SPECobject,SPECimgname,SPECtelescope,SPECinstrum,SPECgrating,SPECresolution,SPECdichroic,SPECtype,"""
        command = command+"""SPECutdate,SPECuttime,SPECmjd,SPEChjd,SPECrv,SPECrv_err,SPECccffwhm,SPECccfheight,SPECbis,SPECbis_err,"""
        command = command+"""SPECsn,SPECexptime,SPECcomment) """
        command = command+"""VALUES """
        command = command+"""(\"%s\" """ % object_name + """,\"%s\" """ % file_name 
        command = command+""","ANU23","WiFeS",\"%s\" """ % grating + """,""" + str(resolution)
        command = command+""",\"%s\" """ % dichroic + ""","RV",\"%s\" """ % sql_date +""",\"%s\" """ % sql_time 
        command = command+""",""" + str(mjd) + """,""" + str(hjd) + """,""" + str(rv) + """,""" + str(rv_err) + """,""" + str(ccffwhm)+ """,""" + str(ccfheight)
        command = command+ """,""" + str(bis) + """,""" + str(bis_err)
        command = command+ """,""" + str(sn) + """,""" + str(exptime) +""",\"%s\" """ % comment
        command = command+ """)"""

        print command
        c.execute(command)

    else:
        print "Updating entry"

        command = """UPDATE SPEC SET """
        command = command+"""SPECobject=\"%s\" """ % object_name
        command = command+""",SPECimgname=\"%s\" """ % file_name
        command = command+""",SPECtelescope="ANU23" """
        command = command+""",SPECinstrum="WiFeS" """
        command = command+""",SPECgrating=\"%s\" """ % grating
        command = command+""",SPECresolution=""" + str(resolution)
        command = command+""",SPECdichroic=\"%s\" """ % dichroic
        command = command+""",SPECtype="RV" """
        command = command+""",SPECutdate=\"%s\" """ % sql_date
        command = command+""",SPECuttime=\"%s\" """ % sql_time
        command = command+""",SPECmjd=""" + str(mjd)
        command = command+""",SPEChjd=""" + str(hjd)
        command = command+""",SPECrv=""" + str(rv)
        command = command+""",SPECrv_err=""" + str(rv_err)
        command = command+""",SPECccffwhm=""" + str(ccffwhm)
        command = command+""",SPECccfheight=""" + str(ccfheight)
        command = command+""",SPECbis=""" + str(bis)
        command = command+""",SPECbis_err=""" + str(bis_err)
        command = command+""",SPECsn=""" + str(sn)
        command = command+""",SPECexptime=""" + str(exptime)
        command = command+""",SPECcomment=\"%s\" """ % comment
        command = command+""" WHERE SPECmjd=""" + str(mjd) + """ and SPECobject=\"%s\" """ % object_name

        print command
        c.execute(command)


def db_spectype_entry(object_name,file_name,grating,resolution,dichroic,dateobs,mjd,teff,logg,feh,sn,exptime,comment):
    sql_date = string.split(dateobs,"T")[0]
    sql_time = string.split(dateobs,"T")[1]

    print "Connecting to database"
    db=MySQLdb.connect(host="mutant.anu.edu.au",user="daniel",passwd="h@ts0uthDB",db="daniel1")

    c = db.cursor()
    c.execute("""SELECT SPECid FROM SPEC WHERE SPECmjd=""" + str(mjd))

    duplicate = c.fetchone()
    if duplicate == None:
        print "Creating entry"
        
        command = """INSERT INTO SPEC """
        command = command+"""(SPECobject,SPECimgname,SPECtelescope,SPECinstrum,SPECgrating,SPECresolution,SPECdichroic,SPECtype,"""
        command = command+"""SPECutdate,SPECuttime,SPECmjd,SPECteff,SPEClogg,SPECfeh,"""
        command = command+"""SPECsn,SPECexptime,SPECcomment) """
        command = command+"""VALUES """
        command = command+"""(\"%s\" """ % object_name + """,\"%s\" """ % file_name 
        command = command+""","ANU23","WiFeS",\"%s\" """ % grating + """,""" + str(resolution)
        command = command+""",\"%s\" """ % dichroic + ""","ST",\"%s\" """ % sql_date +""",\"%s\" """ % sql_time 
        command = command+""",""" + str(mjd) + """,""" + str(teff) + """,""" + str(logg) + """,""" + str(feh)
        command = command+ """,""" + str(sn) + """,""" + str(exptime) +""",\"%s\" """ % comment
        command = command+ """)"""

        print command
        c.execute(command)

    else:
        print "Updating entry"

        command = """UPDATE SPEC SET """
        command = command+"""SPECobject=\"%s\" """ % object_name
        command = command+""",SPECimgname=\"%s\" """ % file_name
        command = command+""",SPECtelescope="ANU23" """
        command = command+""",SPECinstrum="WiFeS" """
        #command = command+""",SPECgrating=\"%s\" """ % grating
        #command = command+""",SPECresolution=""" + str(resolution)
        #command = command+""",SPECdichroic=\"%s\" """ % dichroic
        command = command+""",SPECtype="ST" """
        command = command+""",SPECutdate=\"%s\" """ % sql_date
        command = command+""",SPECuttime=\"%s\" """ % sql_time
        command = command+""",SPECmjd=""" + str(mjd)
        command = command+""",SPECteff=""" + str(teff)
        command = command+""",SPEClogg=""" + str(logg)
        command = command+""",SPECfeh=""" + str(feh)
        command = command+""",SPECsn=""" + str(sn)
        command = command+""",SPECexptime=""" + str(exptime)
        command = command+""",SPECcomment=\"%s\" """ % comment
        command = command+""" WHERE SPECmjd=""" + str(mjd) + """ and SPECobject=\"%s\" """ % object_name

        print command
        c.execute(command)

