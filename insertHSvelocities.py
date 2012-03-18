#! /bin/sh
""":"
exec python $0 ${1+"$@"}
"""
#"

import urllib, urllib2, cookielib, os, re, base64, getopt, sys, datetime, \
    subprocess

#sys.path.append("/home/george/python/lib/python")

homedir=os.getenv("HOME")
# try:
#     testfile = open(homedir+'/.insertHSvelocities/passwd',"r")
# except IOError:
#     # It doesn't exist, so prompt for the password
#     from Tkinter import *
#     import Pmw, subprocess, stat

def Usage():
    sys.stderr.write("Usage:\t"+sys.argv[0]+" RVlist\n\n")
    sys.stderr.write("RVlist has the format:\n")
    sys.stderr.write("\tHATSname HJD RV[km/s] RV_err[km/s] Inst Resolution Teff Teff_err[km/s] logg logg_err[km/s] FeH FeH_err Vrot Vrot_err Peak Exptime\n")
    exit(1)

# # Run a shell command
# def runcommand(command):
#     process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
#     os.waitpid(process.pid, 0)
#     return process.stdout.read().strip()


# # Class to hold the dialog for prompting the user for the transit uname/pwd
# class userpwddialog:
#     def __init__(self, parent):
#         self.dialog = Pmw.Dialog(parent,
#                                  buttons = ('OK','Cancel'),
#                                  title = 'transit.php access',
#                                  defaultbutton = 'Ok',
#                                  buttonboxpos = 's',
#                                  command = self.execute)
#         self.dialog.withdraw()
#         self.user = Pmw.EntryField(self.dialog.interior(),
#                                    labelpos = 'w',
#                                    value = '',
#                                    label_text = 'username:')
#         self.password = Pmw.EntryField(self.dialog.interior(),
#                                        labelpos = 'w',
#                                        value = '',
#                                        label_text = 'password:',
#                                        entry_show = '*')

#         self.user.pack(side=TOP)
#         self.password.pack(side=BOTTOM)
#         self.passwordval = ""
#         self.userval = ""
        

#     def activate(self):
#         self.dialog.activate()
#         vals = [self.userval, self.passwordval]
#         return vals

#     def execute(self, result):
#         if result == 'Cancel':
#             exit(1)
#         self.userval = self.user.getvalue()
#         self.passwordval = self.password.getvalue()
#         self.dialog.deactivate()

# procedure to get the uname/pwd for transit.php
def getpasswd():
    # # First check to see if the pwd file exists in the ~/.getflwotransits
    # # directory
    # homedir=os.getenv("HOME")
    # try:
    #     testfile = open(homedir+'/.insertHSvelocities/passwd',"r")
    # except IOError:
    #     # It doesn't exist, so prompt for the password
    #     root = Tk()
    #     dialog = userpwddialog(root)
    #     vals = dialog.activate()
    #     user = vals[0]
    #     pwd = vals[1]
    #     if not os.path.isdir(homedir+'/.insertHSvelocities/'):
    #         runcommand('mkdir -p '+homedir+'/.insertHSvelocities/')
    #     testfile2 = open(homedir+"/.insertHSvelocities/passwd","w")
    #     testfile2.write(base64.b64encode(user) + "\n")
    #     testfile2.write(base64.b64encode(pwd) + "\n")
    #     testfile2.close()
    #     os.chmod(homedir+'/.insertHSvelocities/passwd',(stat.S_IRUSR | stat.S_IWUSR))
    # else:
    #     user = base64.b64decode(testfile.readline())
    #     pwd = base64.b64decode(testfile.readline())
    #     testfile.close()
    # outvals=[user,pwd]
    outvals=["zhou","egghead"]
    return outvals

# parse the command line:
#dateval=""
#datestart=""
#datestop=""
#lon=""
#lat=""
#tz=""
#site="flwo"
#obj=""
#name=""
#ra=""
#dec=""
#per=""
#Tc=""
#q=""
#try:
#    opts, args = getopt.getopt(sys.argv[1:], "d:l:p:q:", ["start=", "stop=", "lon=", "lat=", "tz=", "obj=", "name=", "ra=", "dec=", "tc="])

#except getopt.GetoptError:
#    Usage()
#    sys.exit(2)

#for opt, arg in opts:
#    if opt == "-d":
#        dateval=arg
#    elif opt == "--start":
#        datestart=arg
#    elif opt == "--stop":
#        datestop=arg
#    elif opt == "-l":
#        site=arg
#    elif opt == "--lon":
#        lon=arg
#    elif opt == "--lat":
#        lat=arg
#    elif opt == "--tz":
#        tz=arg
#    elif opt == "--obj":
#        obj=arg
#    elif opt == "--name":
#        name=arg
#    elif opt == "--ra":
#        ra=arg
#    elif opt == "--dec":
#        dec=arg
#    elif opt == "-p":
#        per=arg
#    elif opt == "--tc":
#        Tc=arg
#    elif opt == "-q":
#        q=arg

#if dateval == "" and (datestart == "" or datestop == ""):
#    Usage()
#    sys.exit(2)

#if lon != "" and (lat == "" or tz == ""):
#    Usage()
#    sys.exit(2)

#if lat != "" and (lon == "" or tz == ""):
#    Usage()
#    sys.exit(2)

#if tz != "" and (lon == "" or lat == ""):
#    Usage()
#    sys.exit(2)

#if lon == "" and lat == "" and tz == "":
#    if site == "flwo":
#        lon="-110.878"
#        lat="31.681"
#        tz="-7"
#    elif site == "keck":
#        lon="-155.477"
#        lat="19.824"
#        tz="-10"
#    elif site == "ftn":
#        lon="-156.2558"
#        lat="20.7075"
#        tz="-10"
#    elif site == "fts":
#	lon="149.0702778"
#        lat="-31.2731944"
#        tz="10"
#    elif site == "lapalma":
#        lon="17.87916"
#        lat="28.7583333"
#        tz="0"
#    else:
#        Usage()
#        sys.exit(2)

#if not (ra == "" and dec == "" and per == "" and Tc == "" and q == "") and \
#        not (ra != "" and dec != "" and per != "" and Tc != "" and q != ""):
#    Usage()
#    sys.exit(2)

#if dateval != "":
#    yrstart=dateval.split('.')[0]
#    mostart=dateval.split('.')[1][0:2]
#    daystart=dateval.split('.')[1][2:]
#    yrstop = yrstart
#    mostop = mostart
#    daystop = daystart
#else:
#    yrstart=datestart.split('.')[0]
#    mostart=datestart.split('.')[1][0:2]
#    daystart=datestart.split('.')[1][2:]
#    yrstop = datestop.split('.')[0]
#    mostop = datestop.split('.')[1][0:2]
#    daystop = datestop.split('.')[1][2:]

# Increase the stop date by one, and the start date by 2 
# (transit.php prints out transits from start -2
# to stop - 1

#datetmp=datetime.date(int(yrstop), int(mostop), int(daystop))+datetime.timedelt#a(1)
#yrstop = datetmp.strftime("%Y")
#mostop = datetmp.strftime("%m")
#daystop = datetmp.strftime("%d")

#datetmp=datetime.date(int(yrstart), int(mostart), int(daystart))+datetime.timedelta(2)
#yrstart = datetmp.strftime("%Y")
#mostart = datetmp.strftime("%m")
#daystart = datetmp.strftime("%d")
    
# set-up cookies

if len(sys.argv) != 2:
    Usage()

infilename=sys.argv[1]

if infilename != "-":
    inlistfile=open(infilename, 'r')
else:
    inlistfile=os.sys.stdin

allinlines=inlistfile.read()
inlistfile.close()

homedir=os.getenv("HOME")

urlopen = urllib2.urlopen
Request = urllib2.Request
cj = cookielib.LWPCookieJar()

COOKIEFILE=homedir+'/.insertHSvelocities/cookies.lwp'
if os.path.isfile(COOKIEFILE):
    cj.load(COOKIEFILE)

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

theurl='http://hatsouth.intersigma.dk/Login.aspx'

req = Request(theurl)

handle = urlopen(req)

data = handle.read()

for f in data.splitlines():
    if re.search('name="__VIEWSTATE" id="__VIEWSTATE" value="', f):
        g=f.split('"')
        viewstate=g[7]
    if re.search('name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="', f):
        g=f.split('"')
        validation=g[7]

if viewstate == '' or validation == '':
    print "Error loading webpage"
    exit(2)

[usr,pwd] =getpasswd()

txdata=urllib.urlencode({'__EVENTARGUMENT': '', '__EVENTTARGET': '', '__EVENTVALIDATION': validation, '__VIEWSTATE': viewstate, 'ctl00$cpMainContent$btnLogin': 'Login', 'ctl00$cpMainContent$tbPassword': pwd, 'ctl00$cpMainContent$tbUserName': usr})

#txdata=urllib.urlencode({'user': usr, 'pass': pwd})

txheaders = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'Referer': 'http://hatsouth.intersigma.dk/Login.aspx'}
# fake a user agent, some websites (like google) don't like automated exploration

req = Request(theurl,txdata,txheaders)

handle = urlopen(req)

data = handle.read()

for f in data.splitlines():
    if re.search('name="__VIEWSTATE" id="__VIEWSTATE" value="', f):
        g=f.split('"')
        viewstate=g[7]
    if re.search('name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="', f):
        g=f.split('"')
        validation=g[7]
    if re.search('name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="', f):
        g=f.split('"')
        prevpage=g[7]

theurl='http://hatsouth.intersigma.dk/Default.aspx'

#candname='HATS551-008'

txdata=urllib.urlencode({'__EVENTARGUMENT': '', '__EVENTTARGET': 'ctl00$cpMainContent$tbSearch', '__EVENTVALIDATION': validation, '__LASTFOCUS': '', '__PREVIOUSPAGE': prevpage, '__VIEWSTATE': viewstate, '__VIEWSTATEENCRYPTED': '', 'ctl00$cpMainContent$ddlNdays': 5, 'ctl00$cpMainContent$ddlTargetsPrPage': 10000, 'ctl00$cpMainContent$tbMagnitude': '', 'ctl00$cpMainContent$tbObsGroup': '', 'ctl00$cpMainContent$tbPhaseDate': '', 'ctl00$cpMainContent$tbPhaseSlack': 0.1, 'ctl00$cpMainContent$tbPreferredNight': '', 'ctl00$cpMainContent$tbPriority_lc': '', 'ctl00$cpMainContent$tbPriority_spec': '', 'ctl00$cpMainContent$tbRAgt': '', 'ctl00$cpMainContent$tbRAlt': '', 'ctl00$cpMainContent$tbSearch': '', 'ctl00$cpMainContent$tbType': '', 'ctl00$cpMainContent$tbVPDate': '25-04-2011 05:00'})

txheaders = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'Referer': 'http://hatsouth.intersigma.dk/Default.aspx'}

req = Request(theurl,txdata,txheaders)

handle = urlopen(req)

data = handle.read()

candids={}

for f in data.splitlines():
    if re.search('a href="Candidate_Edit.aspx',f) and \
            re.search('candidateID=',f) and \
            re.search('HATS',f):
        candidateid = f.split("=")[2].split('"')[0]
        candname = f.split(">")[1].split("<")[0]
        candids[candname] = candidateid
#        if re.search(candname, f):
#            candidateid = f.split("=")[2].split('"')[0]

#print candname

for lines in allinlines.splitlines():
    f = lines.split()
    if candids.has_key(f[0]) and len(f) == 16:
        idval=candids[f[0]]
        velline=f[1]
        for g in f[2:16]:
            velline=velline+" "+g

        inserturl=urllib.urlencode({'candidateid': idval})
        inserturl="http://hatsouth.intersigma.dk/add_velocity.aspx?"+inserturl
        inserturl2="http://hatsouth.intersigma.dk/add_velocity.aspx"
        req = Request(inserturl)
        handle = urlopen(req)
        data = handle.read()
        for f2 in data.splitlines():
            if re.search('name="__VIEWSTATE" id="__VIEWSTATE" value="', f2):
                g=f2.split('"')
                viewstate=g[7]
            if re.search('name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="', f2):
                g=f2.split('"')
                validation=g[7]
        txdata=urllib.urlencode({'__EVENTVALIDATION': validation, '__VIEWSTATE': viewstate, 'ctl00$cpMainContent$ctl00': 'Upload', 'ctl00$cpMainContent$tbVellines': velline})

        txheaders = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'Referer': inserturl}
        

        req = Request(inserturl,txdata,txheaders)

        handle = urlopen(req)

        data = handle.read()
        
        res=""
        for f2 in data.splitlines():
            if re.search("Adding velocity at HJD", f2):
                print "Inserted: "+lines
                res="yes"
        if res == "":
            print "Failed to insert: "+lines

exit()
            
