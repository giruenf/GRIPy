# -*- coding: utf-8 -*-
"""
Created on Fri Sep 09 10:18:02 2016

@author: apfranco
"""

import numpy as np
import scipy
import matplotlib.pyplot as plt


def PlotGatherBin (fileName, numtrcs, numsamps, dt, dataOrientation=1, displayText='Display', normalize=True):
    """Plot a gather that is saved in bin format as a Matrix.
    
    Input:
         fileName - Name of the bin file with its corresponding path
         numtrcs - Number of traces of gather
         nsamples - Number of samples of gather
         dt - sample interval (seconds)
         dataOrientation - 1: If data is stored by columns
                           2: If data is stored by rows
         displayText - Title of the display
         normalize - Normalize all amplitudes (True) or don't (False)
                    
    Output:
        dataMat - Return the gather matrix
        Plot the Wigle Gather
    
    """    
    dataUnf = np.fromfile(fileName,dtype=np.float32)
    dataMat = np.array(np.zeros([numsamps, numtrcs]))

    if dataOrientation == 1:
        for j in np.arange(0,numtrcs):
            for i in np.arange(0,numsamps):
                dataMat[i,j]= dataUnf[i +j*numsamps]
    else:
        for i in np.arange(0,numsamps):
            for j in np.arange(0,numtrcs):
                dataMat[i,j]= dataUnf[j +i*numtrcs]
    

    PlotGather(dataMat, numtrcs, numsamps, int(dt*1000), normalize, displayText)
    
    return dataMat
    
def PlotGather(data, ntraces, nsample, dt, scale=1, displaytext='Display', normalize=True):
    
    if (ntraces > 100):
        ntraces = 100       #numero maximo de tracos por display  

    t = range(0, nsample*dt, dt)
    
    
    plt.figure()    
    plt.title(displaytext)
    plt.ylabel('t (ms)')
    t = np.asarray(t)
    
    if normalize==True:
        f = NormalizationFactor(data, ntraces, 2)
    else:
        f = 1
        
    for i in range(0, ntraces, 1):
        tr = data.T[i]
        #tr = (tr / f[i]) * scale
        tr = (tr / f) * scale
        
        #print shape(tr), shape(t)
        #reshape(t, (nsample,1))
        plt.plot(i+tr, t, 'k')
        plt.fill_betweenx(t, i, i+tr, tr>=0, color='k');

    plt.ylim(nsample*dt,0)
    plt.xlim(-1,ntraces)
    
    plt.show()

    
def NormalizationFactor(traces, ntraces, mode):
    """Normalize traces' amplitude values.
    
    Input:
        traces - array/matrix containing the traces' samples
        mode   - what kind of normalization will be performed
    Output:
        returns a vector containing the normalization factors to be used ijn the normalization process
    
    
    Modes are:
        0 - no normalization (returns vector filled with 1's)
        1 - single trace normalization
        2 - all traces normalization
    
    Normalizing a trace means all of it's amplitudes will stay within the [-1,+1] interval. 
    The normalization process is basically divide all samples by the maximum absolute sample value.
    If the chosen mode is 1 (all traces normalization), the maximum value is picked from all traces, and all traces are normalized using this single value.
    In this particular case, the returned vector will contain the same value in all positions.

    """
    
    factors = []
    
    #no normalization
    if (mode == 0):
        for i in range(0, ntraces, 1):
            factors.append(1)
    
    #single trace normalization
    if (mode == 1):
    
        for i in range(0, ntraces, 1):
            factors.append(max(np.absolute(np.asarray(traces.T[i]))))
    
    #all traces normalization
    if (mode == 2):
    
        tmpmax = []
        for i in range(0, ntraces, 1):
            tmpmax.append(max(np.absolute(np.asarray(traces.T[i]))))
        
        factors=max(tmpmax)
    
    return factors
    
def DepthToTime(v1, v2, dz, flag):
    """Retorna um vetor de tempo PP ou PS de acordo com a flag usada.
    
    
    Entrada:
        v1 - vetor com velocidade P (m/s).
        v2 - vetor com velocidade S (m/s).
        dz - vetor com a espessura de cada camada (m).
        flag:  0 - tempo PP
               1 - tempo PS
               
    """
    
    if (flag==0):
        
        if (np.size(v1)!=np.size(dz) ):
            print "O vetor v1 diferem em tamanho de dz!"
            return 0
        
        st = 0.
        tempo = np.array(np.zeros(np.shape(dz)))
        
        for i in range (0, np.size(dz),1):
            st = st + 2.0*dz[i]/v1[i]
            tempo[i] = st            
        
    
    elif (flag==1):
        
        if ( np.size(v1)!=np.size(dz) or np.size(v2)!=np.size(dz) ):
            print "Os vetores v1, v2 e dz diferem em tamanho!"
            return 0
    
        st = 0.
        tempo = np.array(np.zeros(np.shape(dz)))
        
        for i in range (0, np.size(dz),1):
            st = st + dz[i]/v1[i] + dz[i]/v2[i]
            tempo[i] = st 
    
    return tempo
    
    
def mediamovel (jan, dado):
    """Suavização por media movel.
    
    
    Entrada:
        n - metade do comprimento da janela de suavização.
        dado - vetor real com dado a ser suavizado.
    """
    sizeDado = len(dado)    
    
    if (jan == 0):
        return dado[:]
        
    dadoOut = np.array(dado[:])
    dadoTmp = np.array(dado[:])
    
    for i in range(sizeDado):
        
        if (i-jan) < 0:
            ini = 0
            M1 = ( abs(i - jan)*dado[0] ) #M1 compensa a borda anterior da janela
        else:
            ini = i - jan
            M1 = 0.0
        
        if (i + jan) > (sizeDado - 1):
            fin = sizeDado
            M2 = ( (i + jan - sizeDado +1)*dado[sizeDado-1] ) #M2 compensa a borda posterior da janela
        else:
            fin = i + jan + 1
            M2 = 0.0

        subserie = np.array(dadoTmp[ini:fin])

        dadoOut[i] = (np.sum(subserie) + M1 + M2)/(2*jan + 1)
        
    return dadoOut
    
    
def vint2vrms ( vint ):
    """obtem perfil de velocidade rms a partir de perfil de velocidade intervalar.

    Entrada:

    vint: vetor contendo as amostras do perfil de vel. intervalar 
  
    Saida:

    vrms: vetor contendo as amostras do perfil de velocidade rms
   """ 
    soma = 0.
    cont = 0.
    vrms = np.array(vint[:])
    
    for i in range (len (vint) ):
        soma = soma + vint[i]**2
        cont = cont + 1
        vrms[i] = np.sqrt(soma/cont)
    
    return vrms




















    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    