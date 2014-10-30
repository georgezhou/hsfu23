#!/usr/bin/python
"""Upload candidate data to canditrack interface

The format of the data in the input file (space separated) is:
target classification file instrument BJD RV Teff log(g) mh Vrot Ap ccfPeak exp_time fiber
"""
2
import urllib2, urllib, contextlib#, argparse

# parser = argparse.ArgumentParser()
# parser.add_argument('-u', '--username', help='username')
# parser.add_argument('-p', '--password', help='password')
# parser.add_argument('-f', '--filename', help='input file name')
# args = parser.parse_args()

from optparse import OptionParser

def parse_command_line():
    """ Parses the command line and returns an options structure specifying
    how the plot should be generated and a list of files to make a plot for. 
    """

    parser=OptionParser(usage="%prog [options] ",
                        description=" updates tracker" )
    #parser.add_option("-c", "--candidate", action="store", type="string",
    #                  dest="candidate", default="", help="candidate name")
    parser.add_option("-u", "--username", action="store", type="string",
                      dest="username", default="gzhou",
                      help="username")
    parser.add_option("-p","--password", action="store",
                      dest="password", default="blueskies123_89", help="password")
    parser.add_option("-f","--filename", action="store",
                      dest="filename", default="tracker_temp.txt", help="Input file")    
    #parser.add_option("-l","--upload", action="store",
    #                  dest="upload", default=None, help="upload file")   
    #parser.add_option("-d","--description", action="store",
    #                  dest="description", default=None, help="descirption")   
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

login_url= "http://hat.astro.princeton.edu/accounts/login/"
login(login_url, args.username, args.password)

# upload data
single_order_url = "http://hat.astro.princeton.edu/hatnet/single_order/"

# urlencode the exposures data
with open(args.filename) as f:
    data = urllib.urlencode({"exposures" : f.read()})
    post_req = urllib2.Request(single_order_url, data)

    try:
        result = urllib2.urlopen(post_req)
        print result.read()
    except urllib2.URLError, e:
        print e
