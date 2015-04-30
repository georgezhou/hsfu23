#! /usr/bin/env python

import sys
import os, commands
import pyfits
#import wifes_calib

#stdstar_list = wifes_calib.ref_fname_lookup.keys()

# get directory to be parsed
try:
    data_dir = os.path.abspath(sys.argv[1])+'/'
except:
    data_dir = os.getcwd()+'/'

# get list of all fits files in directory
all_files = commands.getoutput('ls T2*.fits').split('\n')
blue_obs = []
red_obs = []
obs_date = None
for fn in all_files:
    obs = fn
    if obs_date == None:
        try:
            f = pyfits.open(data_dir+fn)
            obs_date = f[0].header['DATE-OBS'].replace('-', '')
            f.close()
        except:
            continue
        #obs_date = obs[7:15]
    try:
        f = pyfits.open(data_dir+fn)
        camera = f[0].header['CAMERA']
        f.close()
    except:
        continue
    if camera == 'WiFeSBlue':
        if obs in blue_obs:
            continue
        else:
            blue_obs.append(obs)
    if camera == 'WiFeSRed':
        if obs in red_obs:
            continue
        else:
            red_obs.append(obs)
#print blue_obs
#print red_obs
#print obs_date

#---------------------------------------------
#  ***  BLUE CHANNEL  ***
#---------------------------------------------
# classify each obs
blue_bias = []
blue_domeflat = []
blue_twiflat = []
blue_dark = []
blue_arc = []
blue_wire = []
blue_rvstd = []
blue_specphot= []
blue_science = []

for obs in blue_obs:
    fn = data_dir+obs
    f = pyfits.open(fn)
    imagetype = f[0].header['IMAGETYP'].upper()
    objtype = f[0].header['OBJECT'].upper()
    try: objname=  f[0].header['OBJNAME']
    except Exception: pass
    f.close()
    #---------------------------
    # check if it is within a close distance to a standard star
    # if so, fix the object name to be the good one from the list!
    #try:
    #    near_std, std_dist = wifes_calib.find_nearest_stdstar(fn)
    #    if std_dist < 100.0:
    #        objtype = near_std
    #except:
    #    pass
    #---------------------------
    # 1 - bias frames
    if imagetype == 'ZERO':
        blue_bias.append(obs)
    # 2 - quartz flats
    if imagetype == 'FLAT':
        blue_domeflat.append(obs)
    # 3 - twilight flats
    if imagetype == 'SKYFLAT':
        blue_twiflat.append(obs)
    # 4 - dark frames
    if imagetype == 'DARK':
        blue_dark.append(obs)
    # 5 - arc frames
    if imagetype == 'ARC':
        blue_arc.append(obs)
    # 6 - wire frames
    if imagetype == 'WIRE':
        blue_wire.append(obs)
    # all else are science targets
    if imagetype == 'OBJECT':
        if 'STANDARD' in objtype:
            blue_rvstd.append(obs)
        elif 'SPECPHOT' in objtype:
            blue_specphot.append(obs)
        else:
            blue_science.append(obs)

#------------------------------------------------------
if len(blue_obs)!=0:
    # write to metadata save script!
    f = open('image_types_blue.py', 'w')

    dsplit = '#' + 54*'-'

    #------------------
    # headers
    #print >> f, 'import pickle'
    #print >> f, ''

    #------------------
    # calibrations
    print >> f, dsplit

    # 1 - bias
    print >> f, 'bias_obs = ['
    for obs in blue_bias:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    # 2 - domeflat
    print >> f, 'domeflat_obs = ['
    for obs in blue_domeflat:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    # 3 - twiflat
    print >> f, 'twiflat_obs = ['
    for obs in blue_twiflat:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    # 4 - dark
    print >> f, 'dark_obs = ['
    for obs in blue_dark:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    # 5 - arc
    print >> f, 'arc_obs = ['
    for obs in blue_arc:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    # 6 - wire
    print >> f, 'wire_obs = ['
    for obs in blue_wire:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    #------------------
    # science
    print >> f, dsplit
    print >> f, 'sci_obs = ['
    for obs in blue_science:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    #------------------
    # rvstds
    print >> f, dsplit
    print >> f, 'rvstd_obs = ['
    for obs in blue_rvstd:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    #------------------
    # specphot
    print >> f, dsplit
    print >> f, 'specphot_obs = ['
    for obs in blue_specphot:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''



    f.close()

#---------------------------------------------
#  ***  RED CHANNEL  ***
#---------------------------------------------
# classify each obs
red_bias = []
red_domeflat = []
red_twiflat = []
red_dark = []
red_arc = []
red_wire = []
red_rvstd = []
red_science = []
red_specphot=[]

for obs in red_obs:
    fn = data_dir+obs
    f = pyfits.open(fn)
    imagetype = f[0].header['IMAGETYP'].upper()
    objtype = f[0].header['OBJECT'].upper()
    try: objname=  f[0].header['OBJNAME']
    except Exception: pass
    f.close()
    #---------------------------
    # check if it is within a close distance to a standard star
    # if so, fix the object name to be the good one from the list!
    #try:
    #    near_std, std_dist = wifes_calib.find_nearest_stdstar(fn)
    #    if std_dist < 100.0:
    #        objtype = near_std
    #except:
    #    pass
    #---------------------------
    # 1 - bias frames
    if imagetype == 'ZERO':
        red_bias.append(obs)
    # 2 - quartz flats
    if imagetype == 'FLAT':
        red_domeflat.append(obs)
    # 3 - twilight flats
    if imagetype == 'SKYFLAT':
        red_twiflat.append(obs)
    # 4 - dark frames
    if imagetype == 'DARK':
        red_dark.append(obs)
    # 5 - arc frames
    if imagetype == 'ARC':
        red_arc.append(obs)
    # 6 - wire frames
    if imagetype == 'WIRE':
        red_wire.append(obs)
    # all else are science targets
    if imagetype == 'OBJECT':
        if 'STANDARD' in objtype:
            red_rvstd.append(obs)
        elif 'SPECPHOT' in objtype:
            red_specphot.append(obs)
        else:
            red_science.append(obs)



#------------------------------------------------------
if len(red_obs)!=0:
    # write to metadata save script!
    f = open('image_types_red.py', 'w')

    dsplit = '#' + 54*'-'

    #------------------
    # headers
    print >> f, 'import pickle'
    print >> f, ''

    #------------------
    # calibrations
    print >> f, dsplit

    # 1 - bias
    print >> f, 'bias_obs = ['
    for obs in red_bias:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    # 2 - domeflat
    print >> f, 'domeflat_obs = ['
    for obs in red_domeflat:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    # 3 - twiflat
    print >> f, 'twiflat_obs = ['
    for obs in red_twiflat:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    # 4 - dark
    print >> f, 'dark_obs = ['
    for obs in red_dark:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    # 5 - arc
    print >> f, 'arc_obs = ['
    for obs in red_arc:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    # 6 - wire
    print >> f, 'wire_obs = ['
    for obs in red_wire:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    #------------------
    # science
    print >> f, dsplit
    print >> f, 'sci_obs = ['
    for obs in red_science:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    #------------------
    # rvstds
    print >> f, dsplit
    print >> f, 'rvstd_obs = ['
    for obs in red_rvstd:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''

    #------------------
    # specphot
    print >> f, dsplit
    print >> f, 'specphot_obs = ['
    for obs in red_specphot:
        print >> f, '   \'%s\',' % obs
    print >> f, '    ]'
    print >> f, ''


    f.close()
