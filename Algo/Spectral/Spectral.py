# -*- coding: utf-8 -*-
import numpy as np
import scipy
import matplotlib.pyplot as plt

from SlidingWindow import SlidingWindow

import wavelets 
#import WaveletAnalysis, Morlet, Paul, DOG, Ricker

from scipy.signal import chirp


import timeit


WaveletTransform = wavelets.WaveletAnalysis
#
MorletWavelet = wavelets.Morlet
PaulWavelet = wavelets.Paul
DOGWavelet = wavelets.DOG
RickerWavelet =  wavelets.Ricker
#




"""

# Define a wavelet.
def ricker(f, length, dt):
    t = np.linspace(-length / 2, (length-dt) / 2, length / dt)
    y = (1. - 2.*(np.pi**2)*(f**2)*(t**2))*np.exp(-(np.pi**2)*(f**2)*(t**2))
    return t, y


# Time in milliseconds
def ricker(freq, peak=0.0, x_values=None, y_values=None):
    t = np.arange(-1000.0, 1001.0, 1)        
    factor = (np.pi * freq * t)**2
    y = (1 - 2. * factor) * np.exp(-factor)
    t = t + peak
    if x_values is None:        
        return t, y
    else:
        vec = in1d_with_tolerance(t, x_values)
        y = y[vec]
        if y_values is None:
            return x_values, y
        else:
            return x_values, y + y_values

"""

# Short Time Fourier Transform 1-D using SlidingWindow
def STFT(x, window_size, noverlap, time_start, Ts, mode='psd'):
    print 'Ts:', Ts
    f0 = 1.0/Ts
    print 'F Zero:', f0
    print 'Frquencia de Nyquist:', f0/2, 'Hz'
    print 'Resolução em frquencia:', f0/window_size, 'Hz'    
    print 'Resolução temporal:', Ts, 'seconds'   
    
    #
    window = scipy.hanning(window_size)
    stft_data = np.array([np.fft.fft(window*data) 
                for data in SlidingWindow(x, len(window), noverlap)]
    )
    #
    

    
    
    if len(window) % 2:
        numFreqs = stft_data.shape[1]/2+1
    else:
        numFreqs = stft_data.shape[1]/2
    freqs = np.fft.fftfreq(window_size, Ts)[:numFreqs]
    stft_data = stft_data[:, :numFreqs]
    time_values = np.arange(window_size/2, 
                         len(x)-window_size/2+1, 
                         window_size-noverlap) * Ts  + time_start
    #                        
    if mode == 'psd':
        # Also include scaling factors for one-sided densities and dividing by
        # the sampling frequency, if desired. Scale everything, except the DC
        # component and the NFFT/2 component:
        stft_data *= 2.
        # MATLAB divides by the sampling frequency so that density function
        # has units of dB/Hz and can be integrated by the plotted frequency
        # values. Perform the same scaling here.
        #if scale_by_freq:
        scale_by_freq = True    
        if scale_by_freq:    
            Fs = 1/Ts    
            stft_data /= Fs
            # Scale the spectrum by the norm of the window to compensate for
            # windowing loss; see Bendat & Piersol Sec 11.5.2.
            stft_data /= (np.abs(window)**2).sum()   
        else:
            # In this case, preserve power in the segment, not amplitude
            stft_data /= np.abs(window).sum()**2
        stft_data = stft_data * np.conjugate(stft_data) 
        stft_data = stft_data.real 
        
    elif mode == 'magnitude':
        stft_data = np.absolute(stft_data)   
        
    elif mode == 'angle' or mode == 'phase':
        stft_data = np.angle(stft_data)
        if mode == 'phase':
            stft_data = np.unwrap(stft_data, axis=0)
            
    return stft_data.T, freqs, time_values
  


"""
n_fft = 2 ** int(np.ceil(np.log2(2 * (len(h) - 1) / 0.01)))
"""







def exemplo_3():
    print 'Exemplo 3'
    print '========='
    print 'Transformada de Fourier usando classe SlidingWindow1D.\n'
    
    #print 'Parametros de entrada para a transformada.'     
    '''
    # Parametros de entrada (pode alterar)    
    Fs = 250.0 # Hz    
    Ts = 1/Fs  
    t0 = 3.0
    t1 = 9.0
    time = np.arange(t0, t1+Ts, Ts)
    f1 = 40
    #print 'Curva cosseno com frequencia:', f1, 'Hz'
    x = np.cos(time * 2 * np.pi * f1)
    '''
    # Parametros de entrada (pode alterar)    
    Fs = 250.0 # Hz    
    Ts = 1/Fs  
    t0 = 3.0
    t1 = 9.0
    time = np.arange(t0, t1+Ts, Ts)
    f1 = 30
    #print 'Curva cosseno com frequencia:', f1, 'Hz'
    x = 20 * np.cos(time * 2 * np.pi * f1)
    
    result, ret_freq, ret_time = STFT(x, 256, 128, t0, Ts=Ts, mode='psd') #mode='psd')

    #result = np.conjugate(result) * result
    #result = result.real
    
    #elif mode == 'magnitude':
    #result = np.absolute(result)
    
    
    #elif mode == 'angle' or mode == 'phase':
        # we unwrap the phase later to handle the onesided vs. twosided case
    #result = np.angle(result)    
    #result = np.unwrap(result, axis=0)
    #print '\nResultado no grafico Matplotlib.'
    
    # Para densidade espectral
    #transformed = transformed * np.conj(transformed)  
    
    '''
    k2 = 0.0
    for i in range(transformed.shape[0]):
        for j in range(transformed.shape[1]):
            k2+= transformed[i][j]
    print 'k2:', k2.real  
    '''
    
    #print ret_freq[-1]
    time_start = ret_time[0]-(ret_time[1]-ret_time[0])/2
    time_end = ret_time[-1]+(ret_time[1]-ret_time[0])/2
    ext = [ret_freq[0], ret_freq[-1], time_end, time_start]
    #ext = [0.0, 1.0, time_end, time_start] 
    print ext
    #ext = [t0, t[-1]+t[0], -f[-1], f[-1]]
    #plt.imshow(transformed.real.T, aspect='auto', cmap='rainbow', extent=ext)
    plt.imshow(result.T, aspect='auto', cmap='rainbow', extent=ext) #, interpolation='bilinear')#cubic')
        
        
    #y = 20*np.log10(np.abs(np.fft.fft(x)))# ** 2 
    y = np.abs(np.fft.fft(x)) # ** 2 
    freqs = np.fft.fftfreq(len(x), Ts)
    
    idx = np.argsort(freqs)
    
    print min(y), max(y), freqs
        
    plt.plot(freqs[idx], y[idx])    
        
    #plt.xlim((t0, t1))    
    plt.show()
    

# Based on:
# http://www.gaussianwaves.com/2015/11/interpreting-fft-results-obtaining-magnitude-and-phase-information/
def aaa(x, N, Ts):
    stft_data = np.fft.fft(x, n=N)/N #* 2 # x2 is the sum of positive and negative freqs
    magnitude = np.abs(stft_data) 
    freqs = np.fft.fftfreq(N, Ts)
    #
    #"""
    X2 = np.copy(stft_data)
    threshold = np.max(np.abs(stft_data))/10000
    X2[np.where(np.abs(X2) < threshold)] = 0
    #phase = np.arctan2(np.imag(X2), np.real(X2)) * 180/np.pi
    phase = np.angle(X2)* 180/np.pi
    #"""
    #phase = np.angle(stft_data) #[:numFreqs]
    #
    if N % 2:
        numFreqs = N/2+1
    else:
        numFreqs = N/2    
    #    
    magnitude = magnitude[:numFreqs]    
    phase = phase[:numFreqs]
    freqs = freqs[:numFreqs]
    #
    return magnitude, phase, freqs


def exemplo_4():
    '''
    # Parametros de entrada (pode alterar)    
    Fs = 250.0 # Hz    
    Ts = 1/Fs  
    t0 = 3.0
    t1 = 9.0
    time = np.arange(t0, t1+Ts, Ts)
    '''
    
    Fc = 10.0 # Signal frequency
    Fs = 32 * Fc # Sampling frequency with oversampling factor=32
    Ts = 1/Fs # Time sample (or step)
    A = 0.5 # Signal amplitude
    phi = np.pi/6 # Signal amplitude
    #
    time = np.arange(0, 2-Ts, Ts)
    x = A * np.cos(2 * np.pi * time * Fc + phi)
    #
    print 'time sample:', Ts
    N=256
    #N=len(x)
    #N = 512
    
    Fr = Fs/N
    print 'Freq res:', Fr    
    
    #
    magnitude, phase, freqs = aaa(x, N, Ts)
    print len(magnitude), len(phase), len(freqs)
    #
    plt.figure(1)
    plt.subplot(211)
    plt.plot(freqs, magnitude) 
    #
    plt.subplot(212)
    plt.plot(freqs, phase) 
    plt.show()
    #


def exemplo_5():
    '''
    # Parametros de entrada (pode alterar)    
    Fs = 250.0 # Hz    
    Ts = 1/Fs  
    t0 = 3.0
    t1 = 9.0
    time = np.arange(t0, t1+Ts, Ts)
    '''
    #"""
    # Parametros de entrada (pode alterar)    
    Fs = 250.0 # Hz    
    Ts = 1/Fs  
    t0 = 0.0
    t1 = 6.0
    time = np.arange(t0, t1+Ts, Ts)
    f1 = 1/128.0
    #print 'Curva cosseno com frequencia:', f1, 'Hz'
    x = 20 * np.cos(time * 2 * np.pi * f1)
    #"""
    
    #x = chirp(time, f0=f1, f1=125.0, 
    #               t1=time[-1], 
    #               phi=0, method='hyperbolic'
    #)
    
    x = chirp(time, f0=0, f1=100, t1=time[-1], method='linear')
    
    #
    #def __init__(self, data=None, time=None, dt=1,
    #             dj=0.125, wavelet=Morlet(), unbias=False,
    #             mask_coi=False, frequency=False, axis=-1
    
    wa = WaveletTransform(x, dt=Ts)
    print wa.wavelet_transform
    #
    #pF = wa.wavelet.w0/wa.scales #wa.wavelet.w0 / (wa.scales*Ts)
    #
    #idx = 6
    #print wa.wavelet_power.shape
    print len(wa.scales), wa.scales, wa.scales[0], wa.scales[-1]
    #print
    #print len(wa.fourier_frequencies), wa.fourier_frequencies, wa.fourier_frequencies[idx]
    #print
    #print len(pF), pF, pF[idx]
    
    ext = [0, len(wa.wavelet_power)-1, wa.time[0], wa.time[-1]]    
    print ext
    
    #wa.plot_power()
    
    plt.imshow(wa.wavelet_transform.real, aspect='auto', cmap='rainbow')#, extent=ext)
    #plt.plot(wa.wavelet_power)
    
    
    plt.yscale('log')
    plt.grid(True)
    
    plt.show()



def exemplo_6():
    
    
    #"""
    # Parametros de entrada (pode alterar)    
    Fs = 250.0 # Hz    
    Ts = 1/Fs  
    t0 = 0.0
    t1 = 100.0
    time = np.arange(t0, t1+Ts, Ts)
    f1 = 1/10.0 
    #print 'Curva cosseno com frequencia:', f1, 'Hz'
    x =  np.cos(time * 2 * np.pi * f1)
    #print len(x)
    
    t02 = 10
    t12 = 20
    time2 = np.arange(t02, t12, Ts)
    
    i, = np.where(time == t02)
    j,  = np.where(time == t12)
    
    #print i, j
    
    f2 = 1/20.0 #/128.0
    x2 = 2 * np.cos(time2 * 2 * np.pi * f2)
    
    
    
    #x[i[0]:j[0]] += x2
    
    
    #"""
    
    #x = chirp(time, f0=f1, f1=125.0, 
    #               t1=time[-1], 
    #               phi=0, method='hyperbolic'
    #)
    
    #x = chirp(time, f0=0, f1=100, t1=time[-1], method='linear')
    
    #
    #def __init__(self, data=None, time=None, dt=1,
    #             dj=0.125, wavelet=Morlet(), unbias=False,
    #             mask_coi=False, frequency=False, axis=-1
    factor = 2
    Dj = 0.500/factor
    wa = WaveletTransform(x, dt=Ts, dj=Dj)#dt=Ts)
    #print wa.wavelet_transform
    
    #wa.plot_power(coi=False)
    #plt.show()
    
   

   # """
    fig=plt.figure(1)
    

    # 2-d coefficient plot
    ax = plt.axes([0.4, 0.1, 0.55, 0.4])
    plt.xlabel('Time [s]')
    #'''
    #plotcwt = np.clip(np.fabs(cwt.real), 0., 1000.)
    #if plotpower2d: 
    #    plotcwt=pwr
    #ext = (x[0], x[-1], y[-1], y[0]) #y[-1], y[0]]    
    #print ext, plotcwt.shape
    
    
    Time, Scale = np.meshgrid(wa.time, wa.fourier_periods) #wa.scales)
    
    print 'Time:', Time.shape    
    print 'Scale:', Scale.shape  
    print 'wa.fourier_periods:', wa.fourier_periods.shape
    print wa.fourier_periods[0], wa.fourier_periods[-1]
    print wa.scales[0], wa.scales[-1]
    print
    #ax.contourf(Time, Scale, wa.wavelet_power, 100)
    
    
    
    
   # ext = (wa.time[0], wa.time[-1] , wa.fourier_periods[0], wa.fourier_periods[-1]) #y[-1], y[0]]    
   # print wa.wavelet_power.shape
   # print ext
   # print
    
    #im = plt.imshow(wa.wavelet_power, cmap=plt.cm.jet, extent=ext, aspect='auto')
    
    plt.contourf(Time, Scale, wa.wavelet_power, 100, cmap=plt.cm.jet)
 
    
    #Time, Scale = np.meshgrid(self.time, self.scales)
    #ax.contourf(Time, Scale, self.wavelet_power, 100)

    plt.yscale('log')
    print '\nscales:', wa.scales[0], wa.scales[-1]
    print 'periods:', wa.fourier_periods[0], wa.fourier_periods[-1]
    print 'ff:', wa.fourier_frequencies[0], wa.fourier_frequencies[-1]
    plt.ylim(wa.scales[0], wa.scales[-1])
    plt.grid(True)
    
    #colorbar()
    #if scaling=="log": 
    #    ax.set_yscale('log')
    
    #for ti in Time:
    #    print ti
    
    #plt.ylim(Time[0][0], Time[-1][-1])
    #ax.xaxis.set_ticks(np.arange(Nlo*1.0,(Nhi+1)*1.0,100.0))
    #ax.yaxis.set_ticklabels(["",""])
    #theposition=plt.gca().get_position()


    

    # data plot
    ax2=plt.axes([0.4, 0.54, 0.55, 0.3])
    plt.ylabel('Data')
    plt.plot(time, x)
    plt.xlim(t0, t1)
    

    '''
    pos=ax.get_position()
    plt.plot(x, A,'b-')
    plt.xlim(Nlo*1.0,Nhi*1.0)
    '''
    ax2.xaxis.set_ticklabels(["",""])
    plt.text(0.5,0.9,"Wavelet example with extra panes",
         fontsize=14,bbox=dict(facecolor='green',alpha=0.2),
         transform = fig.transFigure,horizontalalignment='center')
    
   
    
    scalespec = np.sum(wa.wavelet_power, axis=1) / wa.fourier_periods # calculate scale spectrum
    
    # projected power spectrum
    ax3 = plt.axes([0.08, 0.1, 0.29, 0.4])
    plt.xlabel('Power')
    plt.ylabel('Period [s]')
    vara=1.0
    '''
    if scaling=="log":
        plt.loglog(scalespec/vara+0.01, y,'b-')
    else:
        plt.semilogx(scalespec/vara+0.01, y,'b-')
        

    '''
    #print wa.scales
    #print wa.fourier_periods
    plt.plot(scalespec, wa.fourier_periods)
    plt.ylim(wa.fourier_periods[0], wa.fourier_periods[-1])

    #plt.xlim(scalespec[0], scalespec[-1])
    plt.show()


   # """

def exemplo_7():

    Fs = 250.0 # Hz    
    Ts = 1/Fs  
    t0 = 0.0
    t1 = 10.0
    time = np.arange(t0, t1+Ts, Ts)
    f1 = 8.0
    #print 'Curva cosseno com frequencia:', f1, 'Hz'
    x =  np.sin(time * 2 * np.pi * f1)
    

    

    t02 = 2.0
    t12 = 4.0
    time2 = np.arange(t02, t12, Ts)
    
    i, = np.where(time == t02)
    j,  = np.where(time == t12)
    
    #print i, j
    
    f2 = 30.0 #/128.0
    x2 = np.cos(time2 * 2 * np.pi * f2)
    
    
    x[i[0]:j[0]] += x2
    
    
    
    factor = 2
    Dj = 0.500/factor
    wa = WaveletTransform(x, dt=Ts, dj=Dj)#dt=Ts)    
        
        
    #"""
    # Phase 
    wt = np.copy(wa.wavelet_transform)
    threshold = np.max(np.abs(wt))/10
    wt[np.where(np.abs(wt) < threshold)] = 0
    to_plot = np.unwrap(np.angle(wt))   
    #to_plot = np.angle(wt)
    #"""
    
    
    """
    # Magnitude
    to_plot = np.abs(wa.wavelet_transform)
    """
    
    """
    # Power
    to_plot = wa.wavelet_power    
    """
    
    #wa.anomaly_data
    
    #to_plot = np.angle(wa.wavelet_transform)
    #to_plot = np.arctan(wa.wavelet_transform.imag/wa.wavelet_transform.real)
    
    #print wa.anomaly_data.shape
    #print to_plot.shape    

    x_axis = wa.fourier_frequencies
    y_axis = wa.time
    mesh_y, mesh_x = np.meshgrid(y_axis, x_axis)
    
    #Time, Scale = np.meshgrid(wa.time, wa.scales)
    #Time, Scale = np.meshgrid(wa.time, wa.fourier_periods)
    
    #print 'Time:', Time.shape    
    #print 'Scale:', Scale.shape  
    
    
    #plt.contourf( Scale, Time, phase, 100, cmap=plt.cm.jet)    
    plt.contourf(mesh_x, mesh_y, to_plot, 100, cmap=plt.cm.jet)   
    
    #im = plt.imshow(power, cmap=plt.cm.jet, aspect='auto')


    plt.xscale('log')
    #print '\nscales:', wa.scales[0], wa.scales[-1]
    #print 'periods:', wa.fourier_periods[0], wa.fourier_periods[-1]
    #print 'ff:', wa.fourier_frequencies[0], wa.fourier_frequencies[-1]
    
    
    #plt.xlim(wa.scales[-1], wa.scales[0])
    #plt.ylim(wa.time[-1], wa.time[0])
    #
    plt.xlim(x_axis[-1], x_axis[0])
    plt.ylim(y_axis[-1], y_axis[0])
    
    plt.grid(True)
  
    plt.show()    
    
    
class Chronometer(object):
    
    def __init__(self):
        self.start_time = timeit.default_timer()
    
    def end(self):
        self.total = timeit.default_timer() - self.start_time
        return 'Execution in {:0.3f}s'.format(self.total)        
    
 


def _pcolorargs(funcname, *args, **kw):
    # This takes one kwarg, allmatch.
    # If allmatch is True, then the incoming X, Y, C must
    # have matching dimensions, taking into account that
    # X and Y can be 1-D rather than 2-D.  This perfect
    # match is required for Gouroud shading.  For flat
    # shading, X and Y specify boundaries, so we need
    # one more boundary than color in each direction.
    # For convenience, and consistent with Matlab, we
    # discard the last row and/or column of C if necessary
    # to meet this condition.  This is done if allmatch
    # is False.

    allmatch = kw.pop("allmatch", False)

    if len(args) == 1:
        C = np.asanyarray(args[0])
        numRows, numCols = C.shape
        if allmatch:
            X, Y = np.meshgrid(np.arange(numCols), np.arange(numRows))
        else:
            X, Y = np.meshgrid(np.arange(numCols + 1),
                               np.arange(numRows + 1))
        return X, Y, C

    if len(args) == 3:
        X, Y, C = [np.asanyarray(a) for a in args]
        numRows, numCols = C.shape
    else:
        raise TypeError(
            'Illegal arguments to %s; see help(%s)' % (funcname, funcname))

    Nx = X.shape[-1]
    Ny = Y.shape[0]
    if len(X.shape) != 2 or X.shape[0] == 1:
        x = X.reshape(1, Nx)
        X = x.repeat(Ny, axis=0)
    if len(Y.shape) != 2 or Y.shape[1] == 1:
        y = Y.reshape(Ny, 1)
        Y = y.repeat(Nx, axis=1)
    if X.shape != Y.shape:
        raise TypeError(
            'Incompatible X, Y inputs to %s; see help(%s)' % (
            funcname, funcname))
    if allmatch:
        if not (Nx == numCols and Ny == numRows):
            raise TypeError('Dimensions of C %s are incompatible with'
                            ' X (%d) and/or Y (%d); see help(%s)' % (
                                C.shape, Nx, Ny, funcname))
    else:
        if not (numCols in (Nx, Nx - 1) and numRows in (Ny, Ny - 1)):
            raise TypeError('Dimensions of C %s are incompatible with'
                            ' X (%d) and/or Y (%d); see help(%s)' % (
                                C.shape, Nx, Ny, funcname))
        C = C[:Ny - 1, :Nx - 1]
    return X, Y, C



    
    

def exemplo_8(): 
    Fs = 250.0
    Ts = 1/Fs
    start = 2000.0
    end = 3000.0
    depth = np.arange(start, end+Ts, Ts)

    freq = 60.0
    amp = 20
    data2 = amp * np.sin(depth * 2 * np.pi * freq)
    
    print depth, len(depth)

    t02 = 2200.0
    t12 = 2400.0
    time2 = np.arange(t02, t12, Ts)
    i, = np.where(depth == t02)
    j,  = np.where(depth == t12)
    
    print i, j
    
    f2 = 100.0 #/128.0
    x2 = np.sin(time2 * 2 * np.pi * f2)
    
    print len(x2)
    
  #  data2[50000:100000] = 1#+= x2




    print '\nWaveletTransform'
    c = Chronometer()
    factor = 1
    Dj = 0.500/factor
    wa = WaveletTransform(data2, dt=Ts, dj=Dj, time=depth) #dt=Ts)    
    print c.end()
    
    """
    # Phase 
    wt = np.copy(wa.wavelet_transform)
    threshold = np.max(np.abs(wt))/10
    wt[np.where(np.abs(wt) < threshold)] = 0
    to_plot = np.unwrap(np.angle(wt))   
    #to_plot = np.angle(wt)
    """
    
    """
    # Magnitude
    to_plot = np.abs(wa.wavelet_transform)
    """
    
    #"""
    # Power
    to_plot = wa.wavelet_power    
    #"""
    
    print '\nmeshgrid'
    c = Chronometer()
    x_axis = wa.fourier_frequencies
    y_axis = wa.time
    
    mesh_x, mesh_y = np.meshgrid(x_axis, y_axis)
    print c.end()
    
    '''
    for x in mesh_x:
        print 
        print x, len(x)
 
    print '\n\n\n'
    
    for y in mesh_y:
        print 
        print y, len(y)
    
    '''
    print '\ncontourf'
    c = Chronometer()
    
    fig, ax = plt.subplots(ncols=1, figsize=(8, 4))
    
    
    #####
    
    import matplotlib.collections as mcoll
    import matplotlib.colors as mcolors
    import matplotlib.transforms as mtransforms
    
    kwargs = {}
    alpha = None
    norm = None
    cmap = plt.cm.jet
    vmin = None
    vmax = None
    shading = 'flat'
    antialiased = False
    kwargs.setdefault('edgecolors', 'None')

    allmatch = False

    X, Y, C = _pcolorargs('pcolormesh', mesh_x, mesh_y, to_plot.T, 
                          allmatch=allmatch
    )
    Ny, Nx = X.shape

    # convert to one dimensional arrays
    C = C.ravel()
    X = X.ravel()
    Y = Y.ravel()

    #print X
    #print Y
    #raise Exception()

    # unit conversion allows e.g. datetime objects as axis values
    ax._process_unit_info(xdata=X, ydata=Y, kwargs=kwargs)
    X = ax.convert_xunits(X)
    Y = ax.convert_yunits(Y)

    '''
    print '\n'
    for x in X:
        print x
    print '\n'
    '''
    
    print '\n'
    print X[0], X[-1], len(X)
    print '\n'
    
    coords = np.zeros(((Nx * Ny), 2), dtype=float)
    coords[:, 0] = X
    coords[:, 1] = Y

    collection = mcoll.QuadMesh(Nx - 1, Ny - 1, coords,
                                antialiased=antialiased, shading=shading,
                                **kwargs
    )
    collection.set_alpha(alpha)
    collection.set_array(C)
    if norm is not None and not isinstance(norm, mcolors.Normalize):
        msg = "'norm' must be an instance of 'mcolors.Normalize'"
        raise ValueError(msg)
    collection.set_cmap(cmap)
    collection.set_norm(norm)
    collection.set_clim(vmin, vmax)
    collection.autoscale_None()

    ax.grid(False)

    """
    # Transform from native to data coordinates?
    t = collection._transform
    print '\nt:', t
    if (not isinstance(t, mtransforms.Transform) and hasattr(t, '_as_mpl_transform')):
        print 'E1'
        t = t._as_mpl_transform(ax.axes)

    if t and any(t.contains_branch_seperately(ax.transData)):
        trans_to_data = t - ax.transData
        pts = np.vstack([X, Y]).T.astype(np.float)
        transformed_pts = trans_to_data.transform(pts)
        X = transformed_pts[..., 0]
        Y = transformed_pts[..., 1]
    """
    
    ax.add_collection(collection, autolim=False)

    minx = np.amin(X)
    maxx = np.amax(X)
    miny = np.amin(Y)
    maxy = np.amax(Y)
    collection.sticky_edges.x[:] = [minx, maxx]
    collection.sticky_edges.y[:] = [miny, maxy]
    corners = (minx, miny), (maxx, maxy)
    
    print corners
    
    ax.update_datalim(corners)
    ax.autoscale_view()
    ret = collection    
    
    
    #####
    

    
    
    #ax2.pcolormesh(x, y, np.flipud(data))
    #ret = ax.pcolormesh(mesh_x, mesh_y, to_plot.T, cmap=plt.cm.jet)   
    
    #ret = plt.contourf(mesh_x, mesh_y, to_plot.T, 20, cmap=plt.cm.jet)#, 100, cmap=plt.cm.jet)   
    print c.end()
    
    print ret
    
    #plt.xscale('log')

    #plt.xlim(x_axis[-1], x_axis[0])
    plt.ylim(y_axis[-1], y_axis[0])
    
    #plt.grid(True)
  
    plt.show()    


#exemplo_8()






'''
mode : [ 'default' | 'psd' | 'magnitude' | 'angle' | 'phase' ]
    What sort of spectrum to use.  Default is 'psd', which takes
    the power spectral density.  'complex' returns the complex-valued
    frequency spectrum.  'magnitude' returns the magnitude spectrum.
    'angle' returns the phase spectrum without unwrapping.  'phase'
    returns the phase spectrum with unwrapping.
'''


'''
# Parametros de entrada (pode alterar)    
Fs = 250.0 # Hz    
Ts = 1/Fs  
t0 = 0.0
t1 = 6.0
time = np.arange(t0, t1+Ts, Ts)

print time.shape

f1 = 40
print 'Curva cosseno com frequencia:', f1, 'Hz'
x = np.cos(time * 2 * np.pi * f1)

print '\n'
#plt.specgram(x, NFFT=128, noverlap=64, Fs=250, cmap='rainbow', mode='angle')# mode='phase')
plt.angle_spectrum(x, Fs=250) #, Fc=None, window=None, pad_to=None, sides=None,
                   #hold=None, data=None, **kwargs):
plt.show()
'''
