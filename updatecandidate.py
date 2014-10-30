#!/usr/bin/python
"""Upload candidate data to canditrack interface

The format of the data in the input file (space separated)
BJD RV(km/s) RV_err(km/s) Inst. Resolution Teff Teff_err logg logg_err [Fe/H] [Fe/H]_err Vrot(km/s) Vrot_err(km/s) Peak Exptime(s) SNRe
"""

import urllib2, urllib, contextlib,sys

from optparse import OptionParser


# parser = argparse.ArgumentParser()
# parser.add_argument('-c', '--candidate', help='candidate name')
# parser.add_argument('-u', '--username', help='username')
# parser.add_argument('-p', '--password', help='password')
# parser.add_argument('-i', '--input', help='input file')
# parser.add_argument('-u', '--upload', help='upload file')
# parser.add_argument('-d', '--description', default=None,
#                     help='description of upload file')
# args = parser.parse_args()

def parse_command_line():
    """ Parses the command line and returns an options structure specifying
    how the plot should be generated and a list of files to make a plot for. 
    """

    parser=OptionParser(usage="%prog [options] ",
                        description=" updates tracker" )
    parser.add_option("-c", "--candidate", action="store", type="string",
                      dest="candidate", default="", help="candidate name")
    parser.add_option("-u", "--username", action="store", type="string",
                      dest="username", default="gzhou",
                      help="username")
    parser.add_option("-p","--password", action="store",
                      dest="password", default="egghead", help="password")
    parser.add_option("-i","--input", action="store",
                      dest="input", default="tracker_temp.txt", help="Input file")    
    parser.add_option("-l","--upload", action="store",
                      dest="upload", default=None, help="upload file")   
    parser.add_option("-d","--description", action="store",
                      dest="description", default=None, help="descirption")   
    (options, args)=parser.parse_args()

    return options, args

args,dummy = parse_command_line()

def login(login_url, username=None, password=None):
    """authenticate with urllib2 to access HTTPS django web service
    """
    cookies = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookies)
    urllib2.install_opener(opener)

    opener.open(login_url)

    try:
        token = [x.value for x in cookies.cookiejar if x.name == 'csrftoken'][0]
    except IndexError:
        return None, "no csrftoken"

    params = dict(username=username, password=password,
        this_is_the_login_form=True,
        csrfmiddlewaretoken=token,
         )
    encoded_params = urllib.urlencode(params)

    req = urllib2.Request(login_url, encoded_params)
    # set the HTTP Referer header to the login page url
    req.add_header('Referer', login_url)
    with contextlib.closing(opener.open(req)) as f:
        html = f.read()


# login_url= "https://phs5.astro.princeton.edu/accounts/login/"
# exposures_url = "https://phs5.astro.princeton.edu/hatsouth/{0}/exposure_list/".format(args.candidate)
# upload_url = "https://phs5.astro.princeton.edu/hatsouth/{0}/upload/".format(args.candidate)


login_url= "https://hatsouth.astro.princeton.edu/accounts/login/"
exposures_url = "https://hatsouth.astro.princeton.edu/hatsouth/{0}/exposure_list/".format(args.candidate)
upload_url = "https://hatsouth.astro.princeton.edu/hatsouth/{0}/upload/".format(args.candidate)



login(login_url, args.username, args.password)

# urlencode the exposures data

with open(args.input) as f:
    post_req = urllib2.Request(exposures_url)
    data = {"exposures" : f.read()}
    data = urllib.urlencode(data)
    post_req.add_data(data)

if args.upload:
    post_req = urllib2.Request(upload_url)
    data = {"exposures" : args.upload,
            "description": args.description}
    data = urllib.urlencode(data)
    post_req.add_data(data)

try:
    result = urllib2.urlopen(post_req)
    print result.read()
    #print "upload successful"
except urllib2.URLError, e:
    print e
