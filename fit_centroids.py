### Load python modules
import pyfits
from numpy import *
import string
import sys
import os
import functions
import matplotlib.pyplot as plt
from scipy import optimize

def gaussian2d(x,coords):

    f = coords[0]*0.

    f = exp(-1*((x[1]-coords[1])**2/(2*x[3]**2) + (x[2]-coords[0])**2/(2*x[3]**2)))
    f *= x[0]
    f += x[4]
    #plt.imshow(f,interpolation="nearest")
    #plt.show()

    return f

def minfunc(x,spatial,coords):
    f = gaussian2d(x,coords)
    return std(f-spatial)

def fit_2dgauss(coo,spatial):
    coords = mgrid[0:len(spatial),0:len(spatial[0])]+0.5
    coord_fit = []
    for star in coo:
        x = [100.,star[0],star[1],1.,0.]
    
        x = optimize.fmin(minfunc,x,args=(spatial,coords))
        #gaussian2d(x,coords)   
        print x
        coord_fit.append(x)
        #f = gaussian2d(x,coords)
        #plt.imshow(spatial-f,interpolation="nearest")
        #plt.show()

    return coord_fit

def main(file_path,file_name):
    file_path_reduced = file_path+"reduced/"
    file_path_temp = file_path+"temp/"
    
    coo = functions.read_table(functions.read_ascii(file_path_temp+"master_coo"))
    spatial = loadtxt(file_path_reduced+"spatial_"+file_name+".dat")

    coord_fit = array(fit_2dgauss(coo,spatial))
    savetxt(file_path+"reduced/coords_"+file_name+".dat",coord_fit,fmt="%.10f")
    


if __name__ == "__main__":
    file_path = sys.argv[1]
    file_name = sys.argv[2]
    
    main(file_path,file_name)


