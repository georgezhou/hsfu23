cimport numpy
import numpy

###################
### Description ###
###################

### Contains cython functions to be used for spectral typing
### cython compiles to c, and is faster for those highly 
### computational parts of the program 

### The functions are called on from spectype_main.py

#################
### Functions ###
#################
### Function to trim the spectrum according to wavelength
def chop_spectrum(numpy.ndarray[double, ndim=2] spectrum,double start_lambda,double end_lambda):
    cdef int i
    output_spectrum = []
    i = 0

    for i in range(len(spectrum[0])):
        if spectrum[0,i] > start_lambda and spectrum[0,i] < end_lambda:
            output_spectrum.append([spectrum[0,i],spectrum[1,i]])
        if spectrum[0,i] > end_lambda:
            break

    output_spectrum = numpy.transpose(numpy.array(output_spectrum))
    return output_spectrum

### Transform template spectrum to the same wavelength scale
### as the data spectrum
def conform_spectrum(numpy.ndarray[double,ndim=2] data_spectrum,numpy.ndarray[double,ndim=2] template_spectrum):

    cdef int i,j,match_pos
    cdef double l1,l2,f1,f2,flux_i
    cdef numpy.ndarray[double,ndim=1] template_wave,template_flux,wave

    wave = data_spectrum[0]
    flux = []

    template_wave = template_spectrum[0]
    template_flux = template_spectrum[1]

    for i in range(len(wave)):

        ### Perform interpolation to transform template to data
        match_pos = 0
        j = 0
        while j < len(template_wave):
            if template_wave[j] > wave[i]:
                match_pos = j
                j = len(template_wave)
            elif j == (len(template_wave)-1):
                match_pos = j
            j = j+1
        
        if match_pos == 0:
            l1 = template_wave[0]
            l2 = template_wave[1]
            f1 = template_flux[0]
            f2 = template_flux[1]

        if match_pos == len(template_wave)-1:
            l1 = template_wave[len(template_wave)-2]
            l2 = template_wave[len(template_wave)-1]
            f1 = template_flux[len(template_wave)-2]
            f2 = template_flux[len(template_wave)-1]

        if match_pos > 0 and match_pos < (len(template_wave) - 1):
            l1 = template_wave[match_pos-1]
            l2 = template_wave[match_pos]
            f1 = template_flux[match_pos-1]
            f2 = template_flux[match_pos]

        flux_i = (f2 * l1 - f1 * l2 + f1 * wave[i] - f2 * wave[i]) / (l1 - l2)
        flux.append(flux_i)

    new_template = [wave,flux]
    new_template = numpy.array(new_template)
    return new_template

### Calculate Chisq
def chisq(numpy.ndarray[double,ndim=2] data_spectrum,numpy.ndarray[double,ndim=2] template_spectrum):
    
    cdef numpy.ndarray[double,ndim=1] data_flux,template_flux
    cdef int i
    cdef double numerator,denom,chisq

    data_flux = data_spectrum[1]
    template_flux = template_spectrum[1]

    #sigma_error = numpy.median(abs(data_flux - template_flux))

    sum_list = []
    for i in range(len(data_flux)):
        numerator = (data_flux[i] - template_flux[i])**2
        denom = template_flux[i]
        # denom = sigma_error
        if not numerator == 0:
            sum_list.append(numerator / denom)

    ### Calculate chisq / DOF
    chisq = sum(sum_list) / len(sum_list)
    return chisq

