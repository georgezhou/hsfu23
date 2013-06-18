import os
import sys
import functions
from numpy import *
from scipy import optimize
import matplotlib.pyplot as plt
import emcee
import random

def listify_array(input_array):
    xlist = []
    ylist = []
    zlist = []
    for i in range(len(input_array)):
        for j in range(len(input_array[i])):
            xlist.append(i)
            ylist.append(j)
            zlist.append(input_array[i,j])
    xlist,ylist,zlist = array(xlist),array(ylist),array(zlist)
    return xlist,ylist,zlist


def gaussian(parameters,sigma,offset,x,y):
    ### Parameters [[x1,y1,c1],[x2,y2,c2]..]
    ### sigma is universial to the image
    ### x and y are oned arrays
    f = 0
    for gauss in parameters:
        fn = gauss[2] * exp(-1 * (((y-gauss[0])**2 / (2*sigma**2))+((x-gauss[1])**2/(2*sigma**2))))
        f = f + fn
    f = f + offset
    return f

def minimising_function(guess,x,y,z):

    parameters = []
    i = 0
    while i < len(guess)-2:
        i_list = [guess[i],guess[i+1],guess[i+2]]
        parameters.append(i_list)
        i = i+3
        
    sigma,offset = guess[-2],guess[-1]

    f = gaussian(parameters,sigma,offset,x,y)
    diff = f - z
    rms = sqrt(sum(diff**2)/len(diff))
    return rms

def fit_2d_gauss(input_array,initial_pos):
    ### Initial pos in format [[x1,y1],[x2,y2]]
    nstars = len(initial_pos)
    
    x,y,z = listify_array(input_array)
    z = z / max(z)

    initial_guess = []

    for i in range(len(initial_pos)):
        initial_guess.append(initial_pos[i][0]-1)
        initial_guess.append(initial_pos[i][1]-1)
        initial_guess.append(1.0)

    ### Initial_guess = [initial_pos,sigma,offset]
    initial_guess.append(2.0)
    initial_guess.append(0.0)
    
    best_params =optimize.fmin(minimising_function,initial_guess,args=(x,y,z),maxiter=20000,maxfun=10000,disp=0)

    new_pos = []
    i = 0
    while i < len(best_params)-2:
        i_list = [best_params[i]+1,best_params[i+1]+1]
        new_pos.append(i_list)
        i = i+3
    #print new_pos

    return new_pos
    

def fit_2d_fwhm(input_array,initial_pos):
    ### Initial pos in format [[x1,y1],[x2,y2]]
    nstars = len(initial_pos)
    
    x,y,z = listify_array(input_array)
    z = z / max(z)

    initial_guess = []

    for i in range(len(initial_pos)):
        initial_guess.append(initial_pos[i][0]-1)
        initial_guess.append(initial_pos[i][1]-1)
        initial_guess.append(1.0)

    ### Initial_guess = [initial_pos,sigma,offset]
    initial_guess.append(2.0)
    initial_guess.append(0.0)
    
    best_params =optimize.fmin(minimising_function,initial_guess,args=(x,y,z),maxiter=20000,maxfun=10000,disp=0)

    fwhm = best_params[-2] * 2.35482

    return fwhm
    








    # ### Perform mcmc
    # nwalkers = 20
    # ndim = len(initial_guess)

    # p0 = []
    # for i in range(nwalkers):
    #     pi = []
    #     for n in range(len(initial_guess)):
    #         pi.append(random.gauss(initial_guess[n],0.1))
    #     pi = array(pi)
    #     p0.append(pi)

    # sampler = emcee.EnsembleSampler(nwalkers, ndim, minimising_function, args=[x,y,z])
    
    # pos, prob, state = sampler.run_mcmc(p0, 100)
    # sampler.reset()

    # master_pos = []
    # master_prob = []

    # for result in sampler.sample(pos, iterations=1000, storechain=False):
    #     position,probability = result[0],result[1]

    #     for i in range(len(position)):
    #         master_pos.append(list(position[i]))
    #         master_prob.append(probability[i])

    # for i in range(len(master_prob)):
    #     if master_prob[i] == max(master_prob):
    #         result = master_pos[i]
    #         break
    # print result
