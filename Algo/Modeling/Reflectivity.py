import numpy as np
import wx
from OM.Manager import ObjectManager
import rfltvPP
import rfltvPS
import funcs as fn
import scipy

def Reflectivity(OM,parDictionary):
    
       
     wavFlag = 0        #Gerando a wavelet durante a modelagem (Por Enquanto)
     wavelet = np.array([0.0 for x in np.arange(1,129)], dtype=np.float64)
     
     nSamp = parDictionary['numsamps']
     dt = parDictionary['dt']
     fWav = parDictionary['fWav']
     numTrcsOut = parDictionary['ntraces']
     trc1Cor = parDictionary['trc1']
     dLat = parDictionary['dlat']
     vel1 = parDictionary['vel1']
     zcam1 = parDictionary['z1']
     nSup = parDictionary['nsup']
     vpSup1 = parDictionary['vpSup']
     vsSup1 = parDictionary['vsSup']
     zSup = parDictionary['zsup']
     pNum = parDictionary['pNum']
     angMax = parDictionary['angMax']
     seisOut = parDictionary['outFlag']
     eventRes = parDictionary['respFlag']                           
     
     log_index = OM.list('log', parDictionary['wellID'])[0]
     indexes = log_index.get_index()[0]
      
     vp = OM.get(parDictionary['vpLogID']).data
     vs = OM.get(parDictionary['vsLogID']).data
     rho = OM.get(parDictionary['rhoLogID']).data
     vp_nan = np.argwhere(np.isnan(vp))
     vs_nan = np.argwhere(np.isnan(vs))
     rho_nan = np.argwhere(np.isnan(rho))
     vp = np.delete(vp, vp_nan)
     vs = np.delete(vs, vs_nan)
     rho = np.delete(rho, rho_nan)
     
     
     z1 = indexes[0].data
     z1 = np.delete(z1, rho_nan)
     z2 = z1[1:]
     last_z = z1[-1] + z1[-1] -z1[-2]
     z2 = np.append(z2, last_z) 
     dz = z2 - z1

     
     if np.size(vp) != np.size(vs):
         return 1
     if np.size(vp) != np.size(rho):
         return 2
     if np.size(vp) != np.size(z1):  
         return 3
     
     for i in range(0, np.size(z1)):
         if parDictionary['firstLayer'] <= z1[i]:
             firstLayer = i + 1
             break
     
     lastLayer = np.size(z1) 
     for i in range(0, np.size(z1)):
         if parDictionary['lastLayer'] <= z1[i]:
             lastLayer = i + 1
             break
     
     nLayers = lastLayer - firstLayer + 1
     
     if (nLayers) <= 1:
         return 4
     
     if parDictionary['Qvalue'] == True:
         
         fqp = OM.get(parDictionary['Pwav_QvalueID']).data   
         fqs = OM.get(parDictionary['Swav_QvalueID']).data
         fqp = np.delete(fqp, vp_nan)
         fqs = np.delete(fqs, vp_nan)
         if np.size(vp) != np.size(fqp) or np.size(vs) != np.size(fqs):
            return 5
     else:
         fqp = np.array([2000.0 for i in np.arange(0,np.size(vp))], dtype=np.float64)   
         fqs = np.array([2000.0 for i in np.arange(0,np.size(vp))], dtype=np.float64)  
     
     x = np.arange(trc1Cor, (numTrcsOut)*dLat + trc1Cor, dLat, dtype=np.float64)
     
     vpSup = np.array([vpSup1 for i in np.arange(0,nSup)], dtype=np.float64)   
     vsSup = np.array([vsSup1 for i in np.arange(0,nSup)], dtype=np.float64) 
     
     timeVector = np.arange(0, nSamp*dt, dt)
     
     if parDictionary['modFlag']==0:
        
         seisMod = rfltvPP.rfltvsubv4.modrfltv(dt, nSamp, x, vel1, zcam1, vpSup, zSup, vp, vs, rho, dz, fqp, fqs, firstLayer, lastLayer, angMax, wavelet, fWav, wavFlag, eventRes, seisOut, pNum,nLayers,numTrcsOut,nSup)
     
     elif parDictionary['modFlag']==1:
         
         if (seisOut == 2 or seisOut == 4 or seisOut == 5):
                
             #Generating vp and vs rms in PS time
             vp1 = np.append (vpSup, vp)
             vs1 = np.append (vsSup, vs)
             dz1 = np.append( np.ones(nSup)*zSup, dz)  
  
             tempo = fn.DepthToTime(vp1, vs1, dz1, 1)
             t0off = np.arange(0., (nSamp)*dt, dt)

             vp_t0 = scipy.interp(t0off, tempo, vp1)
             vs_t0 = scipy.interp(t0off, tempo, vs1)            
    
             janSuav = int(2.0/(fWav*dt))

             vp_inter = fn.mediamovel(janSuav, vp_t0)
             vs_inter = fn.mediamovel(janSuav, vs_t0)

             vp_rms = fn.vint2vrms(vp_inter)
             vs_rms = fn.vint2vrms(vs_inter)
                 
         #Correcao NMO
         if (seisOut ==2):
             
             #Fortran Subroutine
             seisMod = rfltvPS.rfltvsubv4.modrfltv(dt, nSamp, x, vel1, z1, vpSup, vsSup, zSup, vp, vs, rho, dz, fqp, fqs, firstLayer, lastLayer, angMax, wavelet, fWav, wavFlag, eventRes, seisOut, pNum)
             tNMO = np.array(np.ones((nSamp, numTrcsOut)))
             seisModNMO = np.array (seisMod)
             vRMS = np.sqrt( (vp_rms*vs_rms) )
             
             for i in range (numTrcsOut):
        
                 tNMO[:,i] = t0off/2 + np.sqrt( (t0off**2)/4 + x[i]**2/(2*vRMS**2))
                 f = scipy.interpolate.interp1d(t0off, seisMod[:,i], kind='quadratic', bounds_error=False, fill_value=0.)
                 seisModNMO[:,i] = f(tNMO[:,i])
             seisMod = seisModNMO
         
         elif (seisOut ==4):
    
             #Fortran Subroutine   
             seisMod = rfltvPS.rfltvsubv4.modrfltv(dt, nSamp, x, vel1, z1, vpSup, vsSup, zSup, vp, vs, rho, dz, fqp, fqs, firstLayer, lastLayer, angMax, wavelet, fWav, wavFlag, eventRes, seisOut, pNum)      
             tNMO = np.array(np.ones((nSamp, numTrcsOut)))
             seisModNMO = np.array (seisMod)
    
             for i in range (numTrcsOut):
                 sinThetaP = (x[i]/1000.)*vp_rms
                 sinThetaS = (x[i]/1000.)*vs_rms    
                 tNMO[:,i] = (t0off/(vp_rms + vs_rms))*(vs_rms*np.sqrt(np.abs(1-sinThetaP**2)) + vp_rms*np.sqrt(np.abs(1-sinThetaS**2)))
                 f = scipy.interpolate.interp1d(t0off, seisMod[:,i], kind='quadratic', bounds_error=False, fill_value=0.)
                 seisModNMO[:,i] = f(tNMO[:,i])
             seisMod = seisModNMO
         elif (seisOut == 5):
     
             np2 = 90
             vel2 = vel1/1000
             pmax = 1./vel2
             pvec = np.arange(0., pmax, pmax/np2)    
             #Fortran Subroutine   
             seisMod = rfltvPS.rfltvsubv4.modrfltv(dt, nSamp, pvec, vel1, z1, vpSup, vsSup, zSup, vp, vs, rho, dz, fqp, fqs, firstLayer, lastLayer, angMax, wavelet, fWav, wavFlag, eventRes, seisOut, pNum) 
             tNMO = np.array(np.ones((nSamp, np2)))
             seisModNMO = np.array (seisMod)
   
             for i in range (np2):
                 sinThetaP = (pvec[i]/1000.)*vp_rms
                 sinThetaS = (pvec[i]/1000.)*vs_rms
                 tNMO[:,i] = (t0off/(vp_rms + vs_rms))*(vs_rms*np.sqrt(np.abs(1-sinThetaP**2)) + vp_rms*np.sqrt(np.abs(1-sinThetaS**2)))
                 f = scipy.interpolate.interp1d(t0off, seisMod[:,i], kind='quadratic', bounds_error=False, fill_value=0.)
                 seisModNMO[:,i] = f(tNMO[:,i])       
             #Calculando o Angle Gather
    
             xrad = np.deg2rad(x)
             seisMod = np.array(np.ones((nSamp, numTrcsOut)))
             for i in range (nSamp):
                 pval = seisModNMO[i,:]
                 rayp2 = np.sin(xrad)/vp_inter[i]*1000
                 seisMod[i,:] = scipy.interp(rayp2, pvec, pval)    
             
         else:
             seisMod = rfltvPS.rfltvsubv4.modrfltv(dt, nSamp, x, vel1, z1, vpSup, vsSup, zSup, vp, vs, rho, dz, fqp, fqs, firstLayer, lastLayer, angMax, wavelet, fWav, wavFlag, eventRes, seisOut, pNum)
 
     seisModNorm = seisMod
     factor = fn.NormalizationFactor(seisMod, numTrcsOut, 2)
     for i in range(0, numTrcsOut, 1):
        tr = seisMod.T[i]
        tr = (tr / factor) 
        seisModNorm.T[i] = tr
     
     fn.PlotGather(seisMod, numTrcsOut, nSamp, int(dt*1000), normalize=True, displaytext="Sismograma PP" )
     
     new_name = parDictionary['outName']
     synth = OM.new('gather', seisModNorm, datatype='Synth', name=new_name)
     OM.add(synth, parDictionary['wellID'])
     
     new_index = OM.new('data_index', 0, 'Time', 'TIME', 's', data=timeVector)
     OM.add(new_index, synth.uid)
     new_index = OM.new('data_index', 1, 'Offset', 'OFFSET', 'm', data=x)
     OM.add(new_index, synth.uid)
     
     
     return 6
     