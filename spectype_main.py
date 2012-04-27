import sys
import os
import string
from numpy import *
import functions
import spectype_functions
import spectype_numerical_functions
import matplotlib
import matplotlib.pyplot as plt
import pyfits
from pyraf import iraf
from scipy import interpolate
import urllib
from numpy.fft import rfft, irfft

iraf.kpnoslit()
iraf.noao()
iraf.rv()

###################
### Description ###
###################

### Take input spectrum

### Find chisq in logg - teff space for every reddenining
### Add over reddening 
### Find min chisq 

### usage: python spectype_main.py file_path file_name
### Takes input params from config_file

#################
### Functions ###
#################
def try_webpage(url):
    try:
        urllib.urlopen(url)
        return True
    except IOError:
        return False

def find_max_reddening(ra,dec):
    print "Trying ",ra,dec
    page_url = "http://irsa.ipac.caltech.edu/cgi-bin/DUST/nph-dust?locstr="
    page_url = page_url + ra + "+" + dec + "+equ+j2000"

    print page_url

    if try_webpage(page_url):

        schlegel = urllib.urlopen(page_url)
        schlegel = schlegel.read()

        schlegel = string.split(schlegel,"<meanValue>")[1]
        schlegel = string.split(schlegel)

        max_reddening = float(schlegel[0])
    else:
        print "Could not connect to Schlegel database"
        print "Default max reddening = 0.10"
        max_reddening = 0.1
    return max_reddening


def isNaN(x):
    if str(x) == "nan" or str(x) == "NaN":
        return True
    else:
        return False

def run_fxcor(input_file,input_rv,lines,output,fitshead_update,npoints,functiontype):
    iraf.fxcor(
        objects = input_file, \
        templates = input_rv, \
        apertures = "*", \
        cursor = "",\
        continuum = "none",\
        filter = "both",\
        rebin = "smallest",\
        pixcorr = 0,\
        osample = lines,\
        rsample = lines,\
        apodize = 0.2,\
        function = functiontype,\
        width = npoints,\
        height= 0.,\
        peak = 0,\
        minwidth = npoints,\
        maxwidth = npoints,\
        weights = 1.,\
        background = "INDEF",\
        window = "INDEF",\
        wincenter = "INDEF",\
        output = output,\
        verbose = "long",\
        imupdate = fitshead_update,\
        graphics = "stdgraph",\
        interactive = 0,\
        autowrite = 1,\
        ccftype = "image",\
        observatory = "sso",\
        continpars = "",\
        filtpars = "",\
        keywpars = "")

########################
### Start of program ###
########################
file_path = sys.argv[1]
file_path_temp = file_path + "temp/"
file_path_reduced = file_path + "reduced/"

file_name = sys.argv[2]

program_dir = os.getcwd() + "/" #Save the current working directory

### Read from param and config files
model_path_flux = functions.read_param_file("MODEL_PATH_FLUX")
model_path_norm = functions.read_param_file("MODEL_PATH_NORM")

### Find the region within which to flux normalise
flux_normalise_w1 = eval(functions.read_param_file("FLUX_NORMALISE_w1"))
flux_normalise_w2 = eval(functions.read_param_file("FLUX_NORMALISE_w2"))

### Find initial estimate of properties
hdulist = pyfits.open(file_path + file_name)
object_name = hdulist[0].header["OBJECT"]
ra = hdulist[0].header["RA"]
dec = hdulist[0].header["DEC"]
max_reddening = find_max_reddening(ra,dec)
print "Regional maximum reddening of E(B-V):",max_reddening
hdulist.close()

print "Analysing ",object_name

hsmso_connect = functions.read_config_file("HSMSO_CONNECT")
hscand_connect = functions.read_config_file("HSCAND_CONNECT")
default_teff = float(functions.read_config_file("TEFF_ESTIMATE"))
default_logg = float(functions.read_config_file("LOGG_ESTIMATE"))
teff_ini,logg_ini = functions.estimate_teff_logg(object_name,hsmso_connect,hscand_connect,default_teff,default_logg)
feh_ini = 0.0
ini_template_spectrum = "template_" + str(teff_ini) + "_" + str(logg_ini) + "_" + str(feh_ini)

print "Initial estimate of teff, logg: ",str(teff_ini),str(logg_ini)

def calculate_spectral_params(teff_ini,logg_ini,feh_ini):

    def find_shift(input1,input2,i1,i2):
        shift_rms = []
        shift_range = 0
        shift_list = []
        for shift in range(-1*shift_range,shift_range+1):
            input1_cropped = input1[i1:i2]
            input2_cropped = input2[i1+shift:i2+shift]

            diff = input1_cropped/median(input1_cropped) - input2_cropped/median(input2_cropped)

            rms = sqrt(sum(diff**2) /float(len(diff)))
            shift_rms.append(rms)
            shift_list.append(shift)

        for i in range(len(shift_rms)):
            if shift_rms[i] == min(shift_rms):
                break
        
        #print "Applying a shift of ",shift_list[i]
        return shift_list[i]
        

    def loop_input_spectrum(input_wave,input_flux,folder,teff_space,logg_space,feh_space,w1,w2,perform_normalise):

        i1 = w1 - min(input_wave)
        i2 = w2 - min(input_wave)

        i = 0
        for teff in teff_space:
            for logg in logg_space:
                for feh in feh_space:
                    if teff == teff_ini and logg == logg_ini and feh == feh_ini:
                        if folder == model_path_flux:
                            template_flux = spec_database[i]
                        if folder == model_path_norm:
                            template_flux = normspec_database[i]

                        shift = find_shift(input_flux,template_flux,i1,i2)

                        break
                    else:
                        i = i+1
        i = 0
        data = []
        for teff in teff_space:
            for logg in logg_space:
                for feh in feh_space:

                    if folder == model_path_flux:
                        template_flux = spec_database[i]
                    if folder == model_path_norm:
                        template_flux = normspec_database[i]

                    input_wave_cropped = input_wave[i1:i2]
                    input_flux_cropped = input_flux[i1:i2]
                    template_flux_cropped = template_flux[i1+shift:i2+shift]

                    sigma = 5.0

                    if perform_normalise:
                        diff_flux = input_flux_cropped/median(input_flux_cropped) - template_flux_cropped/median(template_flux_cropped)

                    else:
                        diff_flux = input_flux_cropped - template_flux_cropped

                    diff_flux = clip(diff_flux,median(diff_flux) - sigma*std(diff_flux),median(diff_flux)+sigma*std(diff_flux))

                    rms = sqrt(sum(diff_flux**2) /float(len(input_wave_cropped)))


                    # shift_rms = []
                    # shift_range = 0
                    # for shift in range(-1*shift_range,shift_range+1):
                    #     input_wave_cropped = input_wave[i1:i2]
                    #     input_flux_cropped = input_flux[i1:i2]
                    #     template_flux_cropped = template_flux[i1+shift:i2+shift]

                    #     sigma = 5.0

                    #     if perform_normalise:
                    #         diff_flux = input_flux_cropped/median(input_flux_cropped) - template_flux_cropped/median(template_flux_cropped)

                    #     else:
                    #         diff_flux = input_flux_cropped - template_flux_cropped

                    #     diff_flux = clip(diff_flux,median(diff_flux) - sigma*std(diff_flux),median(diff_flux)+sigma*std(diff_flux))

                    #     rms = sqrt(sum(diff_flux**2) /float(len(input_wave_cropped)))
                    #     shift_rms.append(rms)

                    # rms = min(shift_rms)

                    ### Weight against feh
                    feh_index = (feh - min(feh_space))/0.5
                    logg_index = (logg - min(logg_space))/0.5
                    rms = rms * feh_weights[int(feh_index)] * logg_weights[int(logg_index)]

                    # plt.clf()
                    # plt.plot(input_wave_cropped,input_flux_cropped/median(input_flux_cropped))
                    # plt.plot(input_wave_cropped,template_flux_cropped/median(template_flux_cropped))
                    # plt.plot(input_wave_cropped,diff_flux)
                    # plt.show()
                    # #sys.exit()

                    # print rms
                    data.append(rms)
                    i = i+1
        return data

    def plot_spectrum(rms_data,input_spectrum):

        print "Plotting ",input_spectrum

        rms_data = functions.read_ascii(rms_data)
        rms_data = functions.read_table(rms_data)
        rms_data = transpose(rms_data)

        ### Find min
        for i in range(len(rms_data[0])):
            if rms_data[3][i] == min(rms_data[3]):
                teff_min = rms_data[0][i]
                logg_min = rms_data[1][i]
                feh_min = rms_data[2][i]
                break

        print teff_min,logg_min,feh_min,min(rms_data[3])

        teff_list = []
        logg_list = []
        rms_list = []

        for i in range(len(rms_data[0])):
            if rms_data[2][i] == feh_min:
                teff_list.append(rms_data[0][i])
                logg_list.append(rms_data[1][i])
                rms_list.append(rms_data[3][i])

        ### Create 2D space
        teff_space = arange(min(teff_list),max(teff_list)+250,250)
        logg_space = arange(min(logg_list),max(logg_list)+0.5,0.5)

        rms_space = zeros([len(teff_space),len(logg_space)])

        for i in range(len(rms_list)):
            x_index = int((teff_list[i] - min(teff_list)) / 250.)
            y_index = int((logg_list[i] - min(logg_list)) / 0.5)
            rms_space[x_index,y_index] = rms_list[i]


        ### Crop 2D space to perform gaussian fit for min
        teff_space_cropped,logg_space_cropped,rms_space_cropped=spectype_functions.chop_array(teff_space,logg_space,transpose(rms_space),teff_min,logg_min,250,0.5)
        rms_space_cropped = -1*(rms_space_cropped - rms_space_cropped.max())
        print rms_space_cropped
        try:
            gauss_fit = spectype_functions.fitgaussian(rms_space_cropped)
            teff_min_fit = min(teff_space_cropped) + gauss_fit[2] * 250
            logg_min_fit = min(logg_space_cropped) + gauss_fit[1] * 0.5
        except TypeError:
            print "Bad gaussian fit, using abs min"
            teff_min_fit = teff_min
            logg_min_fit = logg_min

        if logg_min_fit < 0.0:
            logg_min_fit = 0.0
        if logg_min_fit > 5.0:
            logg_min_fit = 5.0

        teff_min = int(spectype_functions.round_value(teff_min_fit,250.))
        logg_min = spectype_functions.round_value(logg_min_fit,0.5)

        ### Plot teff_logg space
        plt.figure(figsize=(7,5))
        plt.subplot(211)

        plt.title(object_name+" "+file_name+" "+str(int(round(teff_min_fit,0)))+" "+str(round(logg_min_fit,1))+" "+str(feh_min)+" \n RMS="+str(round(min(rms_data[3]),4)))

        v_min = min(rms_list)
        v_max = min(rms_list)+((max(rms_list)-min(rms_list))/3.)
        rms_space = clip(rms_space,v_min,v_max)

        cm = matplotlib.cm.get_cmap('jet')
        sc = plt.contourf(teff_space,logg_space,transpose(rms_space),100,cmap=cm)

        #sc = plt.scatter(teff_list, logg_list, c=rms_list, vmin=min(rms_list), vmax=(max(rms_list)-min(rms_list))/3+min(rms_list), s=150, cmap=cm,edgecolor="w")
        cbar = plt.colorbar(sc)
        cbar.ax.set_ylabel("RMS")

        plt.scatter(teff_min_fit,logg_min_fit,color="r",s=70,marker="+")

        spectype_functions.plot_isochrones(program_dir,"r-",1)
        plt.xlim(max(teff_list),min(teff_list))
        plt.ylim(max(logg_list),min(logg_list))
        #plt.xlim(max(teff_list)+250,min(teff_list)-250)
        #plt.ylim(max(logg_list)+.25,min(logg_list)-0.25)

        plt.xlabel("Teff (K)")
        plt.ylabel("Logg")

        ### Plot spectrum
        plt.subplot(212)
        data_spectrum = functions.read_ascii(input_spectrum)
        data_spectrum = functions.read_table(data_spectrum)
        data_spectrum = transpose(array(data_spectrum))
        data_spectrum = spectype_functions.normalise(data_spectrum,flux_normalise_w1,flux_normalise_w2)

        template_spectrum = "template_" + str(int(teff_min)) + "_" + str(logg_min) + "_" + str(feh_min)+".dat"
        template_spectrum = functions.read_ascii(model_path_flux+template_spectrum)
        template_spectrum = functions.read_table(template_spectrum)
        template_spectrum = transpose(array(template_spectrum))
        template_spectrum = spectype_functions.normalise(template_spectrum,flux_normalise_w1,flux_normalise_w2)

        data_wave = data_spectrum[0]
        data_flux = data_spectrum[1]
        template_wave = template_spectrum[0]
        template_flux = template_spectrum[1]

        c = 3.0 * 10**5

        data_wave = data_wave / ((vel_shift / c) + 1)

        data_interp = interpolate.splrep(data_wave,data_flux,s=0)
        data_flux = interpolate.splev(master_flux_wave,data_interp,der=0)

        template_interp = interpolate.splrep(template_wave,template_flux,s=0)
        template_flux = interpolate.splev(master_flux_wave,template_interp,der=0)


        plt.plot(master_flux_wave,data_flux,"b-",label="data")
        plt.plot(master_flux_wave,template_flux,"g-",label="template")
        plt.xlim(3600,5800)

        plt.legend(loc="lower right",ncol=2)

        plt.xlabel("Wavelength (A)")
        plt.ylabel("Normalised flux")

        os.system("rm "+file_path_reduced+"spectype_plots/"+object_name+"_"+file_name+".pdf")
        plt.savefig(file_path_reduced+"spectype_plots/"+object_name+"_"+file_name+".pdf")
        #plt.show()

        return teff_min_fit,logg_min_fit,feh_min

    def find_min_index(input_list):
        for i in range(len(input_list)):
            if input_list[i] == min(input_list):
                return i

    #################
    ### Make axes ###
    #################

    teff_space = []
    logg_space = []
    feh_space = []

    teff_min = teff_ini - 750
    teff_max = teff_ini + 750

    if teff_min < 3500:
        teff_min = int(3500)

    if teff_max > 8000:
        teff_max = int(8000)

    ### Create grid
    teff_i = teff_min
    while teff_i <= teff_max:
        teff_space.append(teff_i)
        teff_i = teff_i + 250

    logg_i = 0.0
    while logg_i <= 5.0:
        logg_space.append(logg_i)
        logg_i = logg_i + 0.5

    feh_i = -2.5
    while feh_i <= 0.5:
        feh_space.append(feh_i)
        feh_i = feh_i + 0.5

    teff_space = array(teff_space)
    logg_space = array(logg_space)
    feh_space = array(feh_space)

    ######################
    ### Define regions ###
    ######################

    print "Using specific regions for spectral typing"
    ### Check the temp and define which logg sensitive regions to use
    if teff_ini > 4750 and teff_ini < 5750:
    #if teff_ini > 4750 and teff_ini < 6250:
        #logg_regions = [[5140,5235]]
        logg_regions = [[3800,3900],[3900,4000],[4900,5100]]
    if teff_ini <= 4750 and teff_ini > 4250:
        logg_regions = [[4100,4200],[5100,5400]]
    if teff_ini <= 4250:
        logg_regions = [[4720,4810]]
    if teff_ini >= 5750 and teff_ini < 6250:
        #logg_regions = [[3850,4500]]
        logg_regions = [[3670,3715],[3900,4000],[4900,5100]]
    if teff_ini >= 6250:
        logg_regions = [[3670,3715],[3800,3900],[3900,4000]]

    ### logg_regions = [[4500,5800]]
    if teff_ini <= 4000:
        feh_regions = [[4800,5000],[5000,5100],[5200,5500],[4500,5700]]
    if teff_ini <= 4750 and teff_ini > 4000:
        feh_regions = [[4450,4500],[4800,5000],[5000,5100],[5200,5500]]
    if teff_ini <= 5500 and teff_ini > 4750:
        feh_regions = [[3900,4000],[4450,4500],[5100,5400]]
    if teff_ini > 5500:
        feh_regions = [[3900,4100],[4280,4320],[5100,5200]]

    ### Define the regions used in flux spectra matching
    teff_regions = [[3900,5700]]

    feh_weights = ones(len(feh_space))
    logg_weights = ones(len(logg_space))

    ##########################
    ### Start the analysis ###
    ##########################

    ### Change directory to reduced/
    os.chdir(file_path_reduced) #Change to ../reduced/ dir

    ### Load in spectra
    norm_spectrum = functions.read_ascii("norm_" + file_name + ".dat")
    norm_spectrum = functions.read_table(norm_spectrum)
    norm_spectrum = transpose(array(norm_spectrum))

    flux_spectrum = functions.read_ascii("fluxcal_" + file_name + ".dat")
    flux_spectrum = functions.read_table(flux_spectrum)
    flux_spectrum = transpose(array(flux_spectrum))
    flux_spectrum = spectype_functions.normalise(flux_spectrum,flux_normalise_w1,flux_normalise_w2)


    ### Find shift
    os.system("rm apshift*")

    ### Makesure keywpars is set at default
    iraf.unlearn(iraf.keywpars)

    iraf.filtpars.setParam("f_type","square",check=1,exact=1)
    iraf.filtpars.setParam("cuton",50,check=1,exact=1)
    iraf.filtpars.setParam("cutoff",2000,check=1,exact=1)

    os.system("cp "+model_path_norm+"fits_files/"+ini_template_spectrum+".fits .")

    run_fxcor("norm_"+ file_name,ini_template_spectrum+".fits","*","apshift",0,15,"gaussian")
    vel_shift = functions.read_ascii("apshift.txt")
    vel_shift = functions.read_table(vel_shift)
    vel_shift = vel_shift[0][11]
    if vel_shift == "INDEF":
        vel_shift = 0.0
    if abs(vel_shift) > 1000.:
        vel_shift = 0.0

    os.system("rm "+ini_template_spectrum+".fits")
    os.system("rm apshift*")
    print "Velocity shift of ",vel_shift

    ### Correct shift
    flux_wave = flux_spectrum[0]
    flux_flux = flux_spectrum[1]
    norm_wave = norm_spectrum[0]
    norm_flux = norm_spectrum[1]

    c = 3.0 * 10**5

    norm_wave = norm_wave / ((vel_shift / c) + 1)

    ### Interpolate onto a 1A grid
    master_flux_wave = arange(3600,5900,1.)
    master_norm_wave = arange(4550,5900,1.)

    flux_interp = interpolate.splrep(flux_wave,flux_flux,s=0)
    flux_flux = interpolate.splev(master_flux_wave,flux_interp,der=0)
    norm_interp = interpolate.splrep(norm_wave,norm_flux,s=0)
    norm_flux = interpolate.splev(master_norm_wave,norm_interp,der=0)

    ######################################
    ### Start Chi^2 array calculations ###
    ######################################

    os.system("mkdir spectype_plots")
    os.system("rm spectype_plots/" + object_name + "*.pdf")

    #################################
    ### Read database into memory ###
    #################################
    print "Reading database into memory"

    spec_database = []
    normspec_database = []

    teff_table_list = []
    logg_table_list = []
    feh_table_list = []

    for teff in teff_space:
        print teff
        for logg in logg_space:
            for feh in feh_space:
                ### Read in spec
                template_spectrum = "template_" + str(teff) + "_" + str(logg) + "_" + str(feh)+".dat"
                #template_spectrum = functions.read_ascii(model_path_flux+template_spectrum)
                #template_spectrum = functions.read_table(template_spectrum)

                template_spectrum = loadtxt(model_path_flux+template_spectrum,comments='#')
                template_spectrum = transpose(array(template_spectrum))
                template_spectrum = spectype_functions.normalise(template_spectrum,flux_normalise_w1,flux_normalise_w2)

                template_interp = interpolate.splrep(template_spectrum[0],template_spectrum[1],s=0)
                template_flux = interpolate.splev(master_flux_wave,template_interp,der=0)

                spec_database.append(template_flux)

                ### Read in normspec
                template_spectrum = "template_" + str(teff) + "_" + str(logg) + "_" + str(feh)+".dat"
                #template_spectrum = functions.read_ascii(model_path_norm+template_spectrum)
                #template_spectrum = functions.read_table(template_spectrum)
                template_spectrum = loadtxt(model_path_norm+template_spectrum,comments='#')
                template_spectrum = transpose(array(template_spectrum))

                template_interp = interpolate.splrep(template_spectrum[0],template_spectrum[1],s=0)
                template_flux = interpolate.splev(master_norm_wave,template_interp,der=0)

                normspec_database.append(template_flux)

                teff_table_list.append(teff)
                logg_table_list.append(logg)
                feh_table_list.append(feh)


    master_weight = min(loop_input_spectrum(master_flux_wave,flux_flux,model_path_flux,teff_space,logg_space,feh_space,3900,5700,False))
    print "Reference rms of ",master_weight 
    ###################################################
    ### Perform logg-weighted spectrum calculations ###
    ###################################################
    print "Calculating logg weighted rms"

    rms_logg = zeros(len(teff_table_list))

    count = 1
    for region in logg_regions:
        w1 = region[0]
        w2 = region[1]
        if w1 <= 4000:
            to_normalise = False
        else:
            to_normalise = True

        if w1 < 4550:
            folder = model_path_flux
            input_wave = master_flux_wave
            input_spec = flux_flux
        else:
            folder = model_path_norm
            input_wave = master_norm_wave
            input_spec = norm_flux

        rms = array(loop_input_spectrum(input_wave,input_spec,folder,teff_space,logg_space,feh_space,w1,w2,to_normalise))
        i = find_min_index(rms)
        print teff_table_list[i],logg_table_list[i],feh_table_list[i],rms[i]
        #rms_logg = rms_logg + rms
        rms_logg = rms_logg + (master_weight / min(rms))*rms
        count = count + 1

    rms_logg = rms_logg / float(count)
    i = find_min_index(rms_logg)
    print teff_table_list[i],logg_table_list[i],feh_table_list[i],rms_logg[i]
    logg_min = logg_table_list[i]
    logg_min_index = int((logg_min - min(logg_space))/0.5)

    for i in range(len(logg_weights)):
        logg_weights[i] = (abs(i - logg_min_index)/15.)+1.

    # rms_logg_table = transpose([teff_table_list,logg_table_list,feh_table_list,rms_logg])

    # output_rms_table = open("temp_rms_table","w")
    # functions.write_table(rms_logg_table,output_rms_table)
    # output_rms_table.close()

    # plot_spectrum("temp_rms_table","fluxcal_"+file_name+".dat")

    # sys.exit()

    ##################################################
    ### Perform feh-weighted spectrum calculations ###
    ##################################################
    print "Calculating feh weighted rms"

    rms_feh = zeros(len(teff_table_list))

    count = 1
    for region in feh_regions:
        w1 = region[0]
        w2 = region[1]
        if w1 < 4550:
            folder = model_path_flux
            input_wave = master_flux_wave
            input_spec = flux_flux
        else:
            folder = model_path_norm
            input_wave = master_norm_wave
            input_spec = norm_flux

        rms = array(loop_input_spectrum(input_wave,input_spec,folder,teff_space,logg_space,feh_space,w1,w2,True))
        i = find_min_index(rms)
        print teff_table_list[i],logg_table_list[i],feh_table_list[i],rms[i]
        #rms_feh = rms_feh + rms
        rms_feh = rms_feh + (master_weight / min(rms))*rms
        count = count + 1

    rms_feh = rms_feh / float(count)
    i = find_min_index(rms_feh)
    print teff_table_list[i],logg_table_list[i],feh_table_list[i],rms_feh[i]

    feh_min = feh_table_list[i]
    feh_min_index = int((feh_min - min(feh_space))/0.5)

    for i in range(len(feh_weights)):
        feh_weights[i] = (abs(i - feh_min_index)/10.)+1.

    # rms_feh_table = transpose([teff_table_list,logg_table_list,feh_table_list,rms_feh])

    # output_rms_table = open("temp_rms_table","w")
    # functions.write_table(rms_feh_table,output_rms_table)
    # output_rms_table.close()

    # plot_spectrum("temp_rms_table","fluxcal_"+file_name+".dat")

    ###############################################################################
    ### Calculate the corresponding chisq array for a range of reddening values ###
    ###############################################################################
    print "Calculating teff weighted rms"

    ### Change directory to reduced/deredden/
    os.chdir(file_path_reduced + "deredden/") #Change to ../reduced/deredden dir

    ### Determine and create reddening loop
    os.system("ls *" + string.split(file_name,".")[0] + "*.dat > reddening_list")
    reddening_list = functions.read_ascii("reddening_list")
    os.system("rm reddening_list")
    os.system("rm ./*rms_table")

    reddening_values = []
    reddening_rms = []

    for flux_spectrum in reddening_list:

        reddening = float(string.split(flux_spectrum,"_")[1])
        reddening_values.append(reddening)

        print "Trying reddening value E(B-V) = " + str(reddening)

        ### Load in flux spectrum of different reddening
        flux_spectrum = functions.read_ascii(flux_spectrum)
        flux_spectrum = functions.read_table(flux_spectrum)
        flux_spectrum = transpose(array(flux_spectrum))
        flux_spectrum = spectype_functions.normalise(flux_spectrum,flux_normalise_w1,flux_normalise_w2)

        ### Correct shift
        flux_wave = flux_spectrum[0]
        flux_flux = flux_spectrum[1]

        c = 3.0 * 10**5

        flux_wave = flux_wave / ((vel_shift / c) + 1)

        ### Interpolate onto a 1A grid
        flux_interp = interpolate.splrep(flux_wave,flux_flux,s=0)
        flux_flux = interpolate.splev(master_flux_wave,flux_interp,der=0)

        rms_teff = zeros(len(teff_table_list))
        count = 1
        for region in teff_regions:
            rms = array(loop_input_spectrum(master_flux_wave,flux_flux,model_path_flux,teff_space,logg_space,feh_space,region[0],region[1],False))
            rms = 0.5*rms + 0.25*rms_logg + 0.25*rms_feh
            #rms_teff = rms_teff + rms
            
            rms_teff = rms_teff + (master_weight / min(rms))*rms
            count = count+1

        rms_teff = rms_teff / float(count)

        reddening_weight_factor = 0.75

        ### Weight against reddening
        if reddening >= 0.0 and reddening <= max_reddening:
            reddening_weight = 1.0
        if reddening > max_reddening:
            reddening_weight = (reddening - max_reddening)/reddening_weight_factor + 1
        if reddening < 0.0:
            reddening_weight = abs(reddening)/reddening_weight_factor + 1

        rms_teff = rms_teff * reddening_weight

        i = find_min_index(rms_teff)
        print teff_table_list[i],logg_table_list[i],feh_table_list[i],rms_teff[i]

        rms_red_table = transpose([teff_table_list,logg_table_list,feh_table_list,rms_teff])

        output_rms_table = open(str(reddening)+"_rms_table","w")
        functions.write_table(rms_red_table,output_rms_table)
        output_rms_table.close()

        reddening_rms.append(min(rms_teff))

    ###########################
    ### Find best reddening ###
    ###########################

    for i in range(len(reddening_values)):
        if reddening_rms[i] == min(reddening_rms):
            best_reddening = reddening_values[i]
            break

    print "Best reddeining value of E(B-V):",best_reddening
    teff_min,logg_min,feh_min=plot_spectrum(str(best_reddening)+"_rms_table",reddening_list[i])
    print object_name,teff_min,logg_min,feh_min

    os.system("rm ./*_rms_table")
    os.chdir(file_path_reduced)

    return teff_min,logg_min,feh_min


run_again = True
nround = 1
while run_again and nround <= 5:
    print "################### Running round "+str(nround)+" #######################"
    teff_min,logg_min,feh_min = calculate_spectral_params(teff_ini,logg_ini,feh_ini)
    teff_new_ini = int(spectype_functions.round_value(teff_min,250))
    logg_new_ini = spectype_functions.round_value(logg_min,0.5)
    feh_new_ini = spectype_functions.round_value(feh_min,0.5)

    if teff_new_ini == teff_ini:
        run_again = False
    else:
        teff_ini = teff_new_ini
        logg_ini = logg_new_ini
        feh_ini = feh_new_ini
        run_again = True
        nround = nround+1


### Log data into spectype.txt
spectype_log = open("spectype.txt","a")
entry = file_name + " " + object_name + " " + str(int(round(teff_min))) + " 250 " + str(round(logg_min,1)) + " 0.5 " + str(feh_min) + " 0.5\n"
spectype_log.write(entry)
spectype_log.close()

os.chdir(program_dir)
if functions.read_config_file("OPEN_RESULT_PDFS") == "true":
    os.system("evince "+file_path_reduced+"spectype_plots/"+object_name+"_"+file_name+".pdf &")
