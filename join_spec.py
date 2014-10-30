import os,sys
from numpy import *
import matplotlib.pyplot as plt
from scipy import interpolate

def normalise_spec(data,w1,w2):

    mask = data[:,0] > w1
    mask *= data[:,0] < w2
    data[:,1] /= median(data[:,1][mask])

    return data

def smooth(data,window_len=3,window='flat'):
    x = data[:,1]

    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=ones(window_len,'d')
    else:
        w=eval(window+'(window_len)')

    y=convolve(w/w.sum(),s,mode='valid')

    y = y[window_len/2:-1*window_len/2+1]

    data[:,1] = y
    return data

#def join(blue,red):
    
    


#
if __name__ == "__main__":
    data_blue = normalise_spec(smooth(loadtxt(sys.argv[1])),5710,5925)
    data_red = normalise_spec(loadtxt(sys.argv[2]),5710,5925)
    oname = sys.argv[3]

    master_wave = arange(3500,9000,0.5)
    blue = interpolate.splrep(data_blue[:,0],data_blue[:,1],k=1)
    blue = interpolate.splev(master_wave,blue)
    red = interpolate.splrep(data_red[:,0],data_red[:,1],k=1)
    red = interpolate.splev(master_wave,red)

    blue_mask = master_wave <= 5710
    red_mask = master_wave > 5925
    inter_mask = master_wave > 5710
    inter_mask *= master_wave <= 5925
    inter_flux = (blue[inter_mask]+red[inter_mask])/2

    master_flux = zeros(len(master_wave))
    master_flux[blue_mask]=blue[blue_mask]
    master_flux[inter_mask]=inter_flux
    master_flux[red_mask] = red[red_mask]

    odata = transpose(array([master_wave,master_flux]))
    savetxt(oname,odata,fmt="%.10f")
    
    plt.plot(data_blue[:,0],data_blue[:,1],"b-",lw=3)
    plt.plot(data_red[:,0],data_red[:,1],"r-",lw=3)
    plt.plot(master_wave,master_flux,"k-",lw=1)

    plt.show()
    
