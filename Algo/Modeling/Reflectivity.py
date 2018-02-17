import numpy as np
import wx
from OM.Manager import ObjectManager
#import rfltvPP
#import rfltvPS
import funcs as fn
import scipy

from DT.UOM import uom as UOM


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
     well_uid = parDictionary['wellID']
     
     well = OM.get(well_uid)
     
     #
     print
     for k, v in parDictionary.items():
         print k, '-', v
     print
     #
     #log_index = OM.list('log', well_uid)[0]
     
     #print 'B fore!'
     #index = well.get_z_axis_indexes_by_type('MD')[0]
     
     #print index
     vp_obj = OM.get(parDictionary['vpLogID'])
     vs_obj = OM.get(parDictionary['vsLogID'])
     rho_obj = OM.get(parDictionary['rhoLogID'])
     
     if vp_obj.index_set_uid != vs_obj.index_set_uid or \
                         vp_obj.index_set_uid != rho_obj.index_set_uid or \
                         vs_obj.index_set_uid != rho_obj.index_set_uid:
         raise Exception('Vp, Vs and Rho must be on same index_set_uid')                        
     
     #vp = vp_obj.data
     #vs = vs_obj.data
     #rho = rho_obj.data
     
     # Garantindo que as unidades de entrada estao corretas
     if vp_obj.unit != 'm/s':
         print 'Convertendo Vp para m/s...',
         vp = UOM.convert(vp_obj.data, vp_obj.unit, 'm/s')
         print 'OK!'
     else:
         vp = vp_obj.data    
     if vs_obj.unit != 'm/s':
         print 'Convertendo Vs para m/s...',
         vs = UOM.convert(vs_obj.data, vs_obj.unit, 'm/s')
         print 'OK!'
     else:
         vs = vs_obj.data            
     if rho_obj.unit != 'kg/m3':
         print 'Convertendo densidade para kg/m3...',
         rho = UOM.convert(rho_obj.data, rho_obj.unit, 'kg/m3')
         print 'OK!'
     else:
         rho = rho_obj.data         
     #
     
     vp_nan = np.argwhere(np.isnan(vp))
     vs_nan = np.argwhere(np.isnan(vs))
     rho_nan = np.argwhere(np.isnan(rho))
     vp = np.delete(vp, vp_nan)
     vs = np.delete(vs, vs_nan)
     rho = np.delete(rho, rho_nan)
     
     index_set = OM.get(vp_obj.index_set_uid)
     index = index_set.get_z_axis_indexes_by_type('MD')[0]
     
     print 'index.data:', index.data
     
     z1 = index.data
     z1 = np.delete(z1, rho_nan)
     z2 = z1[1:]
     last_z = z1[-1] + z1[-1] -z1[-2]
     z2 = np.append(z2, last_z) 
     dz = z2 - z1

     
     if np.size(vp) != np.size(vs):
         print 'vp:', len(vp), np.size(vp)
         print 'vs:', len(vs), np.size(vs)
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
     
     #
     # Para resolver o erro: 
     #     rfltvPP.error: failed in converting 12nd argument `qp' of rfltvPP.rfltvsubv4.modrfltv to C/Fortran array
     # Os arrays de vp, vs, rho, dz, fqp e fqs devem ser cortados de acordo com firstLayer e lastLayer
     #
     print '\n\nb4 lens:', len(vp), len(vs), len(rho), len(dz), len(fqp), len(fqs)
     #
     vp = vp[firstLayer-1:lastLayer]
     vs = vs[firstLayer-1:lastLayer]
     rho = rho[firstLayer-1:lastLayer]
     dz = dz[firstLayer-1:lastLayer]
     fqp = fqp[firstLayer-1:lastLayer]
     fqs = fqs[firstLayer-1:lastLayer]
     # FIM - rfltvPP.error
     #
     
     if parDictionary['modFlag']==0:
        
        #print '\n\n'
        print 'lens:', len(vp), len(vs), len(rho), len(dz), len(fqp), len(fqs)
        print '\n\n' 
        print 'dt:', dt
        print 'nSamp:', nSamp, '\n'
        print 'x:', x, '\n'
        print 'vel1:', vel1
        print 'zcam1:', zcam1
        print 'vpSup:', vpSup
        print 'zSup:', zSup, '\n'
        print 'vp:', vp, '\n'
        print 'vs:', vs, '\n'
        print 'rho:', rho, '\n'
        print 'dz:', dz, '\n'
        print 'fqp:', fqp, '\n'
        print 'fqs:', fqs, '\n'
        print 'firstLayer:', firstLayer
        print 'lastLayer:', lastLayer
        print 'angMax:', angMax
        print 'wavelet:', wavelet
        print 'fWav:', fWav
        print 'wavFlag:', wavFlag
        print 'eventRes:', eventRes
        print 'seisOut:', seisOut
        print 'pNum:', pNum
        print 'nLayers:', nLayers
        print 'numTrcsOut:', numTrcsOut
        print 'nSup:', nSup
        print '\n\n' 
        
        seisMod = rfltvPP.rfltvsubv4.modrfltv(dt, nSamp, x, vel1, zcam1, vpSup, 
                                               zSup, vp, vs, rho, dz, fqp, fqs,
                                               firstLayer, lastLayer, angMax, 
                                               wavelet, fWav, wavFlag, 
                                               eventRes, seisOut, pNum,
                                               nLayers,numTrcsOut,nSup
        )
     
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
             seisMod = rfltvPS.rfltvsubv4.modrfltv(dt, nSamp, numTrcsOut, x, vel1, zcam1, vpSup, vsSup, zSup, nSup, vp, vs, rho, dz, fqp, fqs, nLayers, firstLayer, lastLayer, angMax, wavelet, fWav, wavFlag, eventRes, seisOut, pNum)
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
             seisMod = rfltvPS.rfltvsubv4.modrfltv(dt, nSamp, numTrcsOut, x, vel1, zcam1, vpSup, vsSup, zSup, nSup, vp, vs, rho, dz, fqp, fqs, nLayers, firstLayer, lastLayer, angMax, wavelet, fWav, wavFlag, eventRes, seisOut, pNum)     
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
             seisMod = rfltvPS.rfltvsubv4.modrfltv(dt, nSamp, numTrcsOut, x, vel1, zcam1, vpSup, vsSup, zSup, nSup, vp, vs, rho, dz, fqp, fqs, nLayers, firstLayer, lastLayer, angMax, wavelet, fWav, wavFlag, eventRes, seisOut, pNum)
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
             seisMod = rfltvPS.rfltvsubv4.modrfltv(dt, nSamp, numTrcsOut, x, vel1, zcam1, vpSup, vsSup, zSup, nSup, vp, vs, rho, dz, fqp, fqs, nLayers, firstLayer, lastLayer, angMax, wavelet, fWav, wavFlag, eventRes, seisOut, pNum)
 
    
     print '\n\n'
     print seisMod.T.shape
     print np.nanmin(seisMod), np.nanmax(seisMod)
     print
    
     new_obj_name = parDictionary['outName']
        
     print 111
     
     try:
         index_set_name = new_obj_name + ' indexes'
         index_set = OM.new('index_set', name=index_set_name)
         OM.add(index_set, well.uid)
     except Exception as e:
         print 'ABCFHGHTHTHJ'
         print well.uid
         raise e
         
     print 222        
     
     synth = OM.new('gather', seisMod.T, datatype='Synth', name=new_obj_name)
     OM.add(synth, well.uid)
     #
     print 333
     #
     timeVector = timeVector * 1000.0
     time_index = OM.new('data_index', 0, 'Time', 'TWT', 'ms', data=timeVector)
     OM.add(time_index, index_set.uid)
     #
     print 444
     gather_index_set = OM.new('index_set', vinculated=index_set.uid)
     OM.add(gather_index_set, synth.uid)
     print 555
     if seisOut == 1 or seisOut == 2:
         index = OM.new('data_index', 1, 'Offset', 'OFFSET', 'm', data=x)
     elif seisOut == 3 or seisOut == 4:    
         index = OM.new('data_index', 1, 'Ray Parameter', 'P', 's/m', data=x)
     elif seisOut == 5:     
         index = OM.new('data_index', 1, 'Angle', 'ANGLE', 'deg', data=x)
     print 666    
     OM.add(index, gather_index_set.uid)
     #
     print 777
     return 6    
																  