# -*- coding: utf-8 -*-
import wx
import os
import numpy as np
import DT
import FileIO
from collections import OrderedDict
from UI.uimanager import UIManager
from OM.Manager import ObjectManager
from Parms import ParametersManager
from  UI import HeaderEditor
from  UI import ImportSelector
from  UI import ExportSelector
from  UI import ODTEditor
from  UI import lisloader
from  UI import PartitionEditor
from App.gripy_debug_console import DebugConsoleFrame


import utils

from Algo.Spectral.Spectral import STFT, WaveletTransform, Morlet, Paul, DOG, Ricker
from UI.dialog_new import Dialog


from Algo import AVO 
import copy


"""
TODO: explicar uso de wx.App.Get().GetTopWindow() e de event.GetEventObject()

"""

WAVELET_TYPES = OrderedDict()
WAVELET_TYPES['Morlet complex'] = 'morlet'
WAVELET_TYPES['Ricker'] = 'ricker'
WAVELET_TYPES['DOG (order=3)'] = 'dog3'
WAVELET_TYPES['DOG (order=4)'] = 'dog4'
WAVELET_TYPES['DOG (order=5)'] = 'dog5'
WAVELET_TYPES['DOG (order=6)'] = 'dog6'
WAVELET_TYPES['Paul (order=2)'] = 'paul2'
WAVELET_TYPES['Paul (order=3)'] = 'paul3'
WAVELET_TYPES['Paul (order=4)'] = 'paul4'
WAVELET_TYPES['Paul (order=5)'] = 'paul5'
WAVELET_TYPES['Paul (order=6)'] = 'paul6'

WAVELET_MODES = OrderedDict()
WAVELET_MODES['Magnitude'] = 0
WAVELET_MODES['Power'] = 1
WAVELET_MODES['Phase (wrap)'] = 2
WAVELET_MODES['Phase (unwrap)'] = 3



def teste4(event):
    #
    filename = 'D:\\Sergio_Adriano\\NothViking\\Mobil_AVO_Viking_pstm_16_CIP_stk.sgy'
    name = 'Mobil_AVO_Viking_pstm_16_CIP_stk'
    utils.load_segy(event, filename, 
        new_obj_name=name, 
        comparators_list=[(21, 4, '==', 808), (21, 4, '==', 1572)], 
        iline_byte=9, xline_byte=21, offset_byte=37
    )
    #
    filename = 'D:\\Sergio_Adriano\\NothViking\\Mobil_AVO_Viking_pstm_16_CIP_prec_stk.sgy'
    name =  'Mobil_AVO_Viking_pstm_16_CIP_prec_stk'   
    utils.load_segy(event, filename, 
        new_obj_name=name, 
        comparators_list=[(21, 4, '==', 808), (21, 4, '==', 1572)], 
        iline_byte=9, xline_byte=21, offset_byte=37
    )    


def teste7(event):
    OM = ObjectManager(event.GetEventObject()) 
    # Init options to be used in wxChoices
    seismics = OrderedDict()
    for seis in OM.list('seismic'):
        seismics[seis.name] = seis.uid
    vels = OrderedDict()
    for vel in OM.list('velocity'):
        vels[vel.name] = vel.uid
    invmod = OrderedDict()
    invmod['Inversion'] = 0
    invmod['Modeling'] = 1    
    itype = OrderedDict()
    itype['Mahmoud'] = 1
    itype['Aki Richards'] = 2
    itype['Aki Rickards (Vel Func)'] = 5
    #itype['Caparica'] = 6
    #itype['Aki Richards (Modified)'] = 9
    #
    dlg = Dialog(None, title='AVO-PPPS', flags=wx.OK|wx.CANCEL)
    #
    cntr_pp = dlg.AddStaticBoxContainer(label='Pre-stack seismic PP', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(cntr_pp, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='seismic_pp', initial=seismics
    )     
    #
    cntr_ps = dlg.AddStaticBoxContainer(label='Pre-stack seismic PS', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(cntr_ps, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='seismic_ps', initial=seismics
    )     
    #    
    cntr_velp = dlg.AddStaticBoxContainer(label='P-Wave velocity', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(cntr_velp, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='vp', initial=vels
    )  
    #
    cntr_vels = dlg.AddStaticBoxContainer(label='S-Wave velocity', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(cntr_vels, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='vs', initial=vels
    )  
    #
    cntr_invmod = dlg.AddStaticBoxContainer(label='Inversion/Modeling', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(cntr_invmod, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='invmod', initial=invmod
    )      
    #        
    cntr_method = dlg.AddStaticBoxContainer(label='Method', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(cntr_method, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='itype', initial=itype
    )          
    
    #
    cntr_objname = dlg.AddStaticBoxContainer(label='New object name', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddTextCtrl(cntr_objname, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='invmod_name', initial='INVMOD'
    )    
    #
    dlg.SetSize((270, 500))
    result = dlg.ShowModal()
    #
    if result == wx.ID_OK:
        results = dlg.get_results()  
        print '\n', results
        #
        if not results.get('seismic_pp') or not results.get('seismic_ps') or \
                not results.get('vp') or not results.get('vs') or \
                results.get('itype') is None or results.get('invmod') is None:
            dlg.Destroy() 
            print 'RETURNED'
            return
        #
        seis_pp = OM.get(results.get('seismic_pp'))
        seis_ps = OM.get(results.get('seismic_ps'))
        vp = OM.get(results.get('vp'))
        vs = OM.get(results.get('vs'))

        # original
        # vp = Velocidade - "data/vp_cdp_966.sgy"
        # offsets = Vetor valores offset de cada traco
        npar_rt = 200 # numero de parametros p a serem usados no raytracing
        # dt = Amostragem # 4ms
        # t0 = 0 # tempo inicial
        # npts = numero de amostras de cada traco sismico
        # ntrace = Numero de tracos # 17

        dt_pp = seis_pp.step/1000.0
        t0 = seis_pp.get_index().data[0]
        ntrace_pp = seis_pp.data.shape[0]
        npts_pp = seis_pp.data.shape[1]
        #
        dt_ps = seis_ps.step/1000.0
        t0_ps = seis_ps.get_index().data[0]
        ntrace_ps = seis_ps.data.shape[0]
        npts_ps = seis_ps.data.shape[1]
        #
        vp_data = vp.data.reshape((vp.data.shape[0] * vp.data.shape[1])).tolist()
        vs_data = vs.data.reshape((vs.data.shape[0] * vs.data.shape[1])).tolist()
        
        #print
        #print len(vp_data)
        #print seis.attributes.get('offsets')
        #print npar_rt, dt, t0, npts, ntrace
        #print
        
        #
        #theta_p = angle_pp(vp, offsets, np, dt, t0, npts, ntrace)
        
        
        #angle_pp(vp, offsets, np, dt, t0, npts, ntrace)
        #angle_pppsv(vp, vs, offsets, offsets_ps, npts, np, ntrace, ntrace_ps, dt, t0)
 
        print '\nStarting theta P' 
        theta_p = AVO.angle_pp(vp_data, seis_pp.attributes.get('offsets'),
                               npar_rt, 
                               dt_pp, 
                               t0, 
                               npts_pp, 
                               ntrace_pp
        )
        angle_pp = OM.new('angle', theta_p.T, name=seis.name+'_Angle_PP', 
                               unit='m', domain='depth', 
                               sample_rate = dt_pp,
                               datum = t0,
                               samples = theta_p.shape[0]
        )                       
        OM.add(angle_pp) 
        print 'Ended theta P'
        print '\nStarting theta S' 
        #
        #theta_s, phi = angle_pppsv(vp, vs, offsets, offsets_ps, 
        #                            npts, np, ntrace, ntrace_ps, dt, t0)        
        theta_s, phi = AVO.angle_pppsv(vp_data, vs_data, 
                                       seis_pp.attributes.get('offsets'),
                                       seis_ps.attributes.get('offsets'),
                                       npts_pp,
                                       npar_rt,
                                       ntrace_pp,
                                       ntrace_ps,
                                       dt_pp, 
                                       t0
        )
        print 'Ended theta S'
        angle_ps = OM.new('angle', theta_s.T, name=seis.name+'_Angle_PS', 
                               unit='m', domain='depth', 
                               sample_rate = dt_pp,
                               datum = t0,
                               samples = theta_s.shape[0]
        )                       
        OM.add(angle_ps) 
        #
        angle_phi = OM.new('angle', phi.T, name=seis.name+'_Angle_PHI', 
                               unit='m', domain='depth', 
                               sample_rate = dt_pp,
                               datum = t0,
                               samples = phi.shape[0]
        )                       
        OM.add(angle_phi) 
        #
        print 'OK Theta' 
        #
 
        #ntrace = seis.data.shape[0]
        npts = seis.data.shape[1]
        ifirst = 0
        winsize = 1
        angmin = 0.0            # angulo minimo para PP
        angmax = 50.0           # angulo maximo para PP      
        angmin_ps = 0.0         # angulo minimo para PS
        angmax_ps = 40.0        # angulo maximo para PS

         
        # inversão
        #inv_out_ppps_pp, inv_out_ppps_ps = avopp_ps(itype, 0, ntrace, ntrace_ps,
        #                        npts_ps, ifirst, winsize, vp, vs, 
        #                        Rpp, Rps, 
        #                        angmin, angmax, angmin_ps, angmax_ps, 
        #                        theta_p, theta_s, phi, 
        #                        npts
        #)


        if results.get('invmod') == 1:    

            mod_ppps_pp, mod_ppps_ps = AVO.avopp_ps(results.get('itype'), 
                                 results.get('invmod'),
                                 ntrace_pp,
                                 ntrace_ps,
                                 npts_ps,
                                 ifirst, 
                                 winsize, 
                                 vp_data, vs_data, 
                                 seis_pp.data.T, seis_ps.data.T,
                                 angmin, angmax, angmin_ps, angmax_ps, 
                                 theta_p, theta_s, phi, 
                                 npts      
            )
            #
            seis_mod_ppps_pp = OM.new('seismic', mod_ppps_pp.T, 
                                   name=results.get('invmod_name')+'MOD_PP', 
                                   unit='ms', 
                                   domain='time', 
                                   sample_rate=seis_pp.step, 
                                   datum=0,
                                   samples=mod_ppps_pp.shape[0],
                                   stacked='False'
            )       
            OM.add(seis_mod_ppps_pp)     
            #
            '''
            index = seis_mod_ppps_pp.get_index()
            print '\nMM:', index.max, index.min
            print mod_ppps_pp.shape
            '''
            #
            seis_mod_ppps_ps = OM.new('seismic', mod_ppps_ps.T, 
                                   name=results.get('invmod_name')+'MOD_PS', 
                                   unit='ms', 
                                   domain='time', 
                                   sample_rate=seis_ps.step,
                                   datum=0,
                                   samples=mod_ppps_ps.shape[0],
                                   stacked='False'
            )       
            OM.add(seis_mod_ppps_ps)             

        else:
            inv_ppps_pp, inv_ppps_ps = AVO.avopp_ps(results.get('itype'), 
                                 results.get('invmod'),
                                 ntrace_pp,
                                 ntrace_ps,
                                 npts_ps,
                                 ifirst, 
                                 winsize, 
                                 vp_data, vs_data, 
                                 seis_pp.data.T, seis_ps.data.T,
                                 angmin, angmax, angmin_ps, angmax_ps, 
                                 theta_p, theta_s, phi, 
                                 npts      
            )
            print '\nFIM INVERSAO'
            #raise Exception()
            


        #Rp = out_ppps_pp[0]
        #Rs = out_ppps_pp[1]
        #Rd = out_ppps_pp[2]
        
        #Rp_ps, Rs_ps, Rd_ps = out_ppps_ps
        

        
        """
        print 
        #for d in enumerate(Rp):
        #    print d
        print 
        print Rs
        print 
        print Rd
        print 
        """

        """

        print seis.data.shape # (17L, 901L)
        
        ntrace = seis.data.shape[0]
        npts = seis.data.shape[1]
        ifirst = 0
        winsize = 3
        angmin = 0.0            # angulo minimo para PP
        angmax = 50.0           # angulo maximo para PP       
        
        
        print ntrace, npts, ifirst, winsize, len(vp_data), len(vs_data), seis.data.T.shape, \
                            angmin, angmax, theta_p.shape#, 
        
        
   
        avo_data = AVO.avopp(results.get('itype'), results.get('invmod'),
                            ntrace, 
                            #npts,
                            ifirst, 
                            winsize, 
                            vp_data, vs_data, seis.data.T, 
                            angmin, angmax, 
                            theta_p, 
                            npts      
        )
        if avo_data is None:
            raise Exception()
            
            
        print len(avo_data), len(avo_data[0]) 
        
        avo_data = np.asarray(avo_data)
        avo_data = avo_data.T
        
        
        
        
        print avo_data.shape
        
        #SUBROUTINE avopp(itype, irecon_flag, ntrace, npts, ifirst, winsize,  &
        #                 vp, vs, ampl, angmin, angmax, angle)
        
        #SUBROUTINE avopp_v2(itype, irecon_flag, ntrace, npts, ifirst, winsize,  &
        #                  vp, vs, ampl, angmin, angmax, angle)
        
        #qqcoisa = avopp(itype, 0, ntrace, ifirst, winsize, vp, vs, Rpp, angmin, angmax, theta_p, npts)
  


        seismic = OM.new('seismic', avo_data, 
                               name=results.get('invmod_name'), 
                               unit='ms', 
                               domain='time', 
                               sample_rate=seis.step, #segy_file.sample_rate*1000, 
                               datum=0,
                               samples=avo_data.shape[1],
                               stacked='False'#,
                               #trace_headers=trace_headers,
                               #offsets=offsets
        )       
        OM.add(seismic)  

        """

    dlg.Destroy() 



def teste6(event):
    
    OM = ObjectManager(event.GetEventObject()) 


    dlg = Dialog(None, title='AVO-PP', 
                 flags=wx.OK|wx.CANCEL
    )
    #
    container = dlg.AddStaticBoxContainer(label='Pre-stack seismic', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    seismics = OrderedDict()
    for seis in OM.list('seismic'):
        seismics[seis.name] = seis.uid
    
    dlg.AddChoice(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='seismic', initial=seismics
    )     
    #
    container2 = dlg.AddStaticBoxContainer(label='P-Wave velocity', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    vels = OrderedDict()
    for vel in OM.list('velocity'):
        vels[vel.name] = vel.uid
    dlg.AddChoice(container2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='vp', initial=vels
    )  
    
    #
    
    container3 = dlg.AddStaticBoxContainer(label='S-Wave velocity', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(container3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='vs', initial=vels
    )  
    
    #
    
    invmod = OrderedDict()
    invmod['Inversion'] = 0
    invmod['Modeling'] = 1
    container = dlg.AddStaticBoxContainer(label='Inversion/Modeling', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='invmod', initial=invmod
    )      
    #    
    itype = OrderedDict()
    itype['Shuey'] = 0
    itype['Mahmoud'] = 1
    itype['Aki Richards'] = 2
    itype['Fatti'] = 3
    itype['Hiltermann'] = 4
    itype['Aki Rickards (Vel Func)'] = 5
    itype['Caparica'] = 6
    
    container = dlg.AddStaticBoxContainer(label='Method', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='itype', initial=itype
    )          
    
    #
    
    container = dlg.AddStaticBoxContainer(label='New object name', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    
    dlg.AddTextCtrl(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='invmod_name', initial=''
    )    
    
    dlg.SetSize((270, 460))
    
    result = dlg.ShowModal()
 
    
    
    
    if result == wx.ID_OK:
        results = dlg.get_results()  
        print '\n', results
        #
        if not results.get('seismic') or not results.get('vp') or \
                results.get('itype') is None or results.get('invmod') is None:
            dlg.Destroy() 
            return
        #
        seis = OM.get(results.get('seismic'))
        vp = OM.get(results.get('vp'))
        vs = OM.get(results.get('vs'))

        print seis.uid
        print vp.uid
        print vs.uid
		
        
        # original
        # vp = Velocidade - "data/vp_cdp_966.sgy"
        # offsets = Vetor valores offset de cada traco
        npar_rt = 200 # numero de parametros p a serem usados no raytracing
        # dt = Amostragem # 4ms
        # t0 = 0 # tempo inicial
        # npts = numero de amostras de cada traco sismico
        # ntrace = Numero de tracos # 17

        dt = seis.step/1000.0
        t0 = seis.get_index().data[0]

        ntrace = seis.data.shape[0]
        npts = seis.data.shape[1]

        vp_data = vp.data.reshape((vp.data.shape[0] * vp.data.shape[1])).tolist()
        vs_data = vs.data.reshape((vs.data.shape[0] * vs.data.shape[1])).tolist()
        
        print
        print len(vp_data)
        print seis.attributes.get('offsets')
        print npar_rt, dt, t0, npts, ntrace
        print 
        
        
        #theta_p = angle_pp(vp, offsets, np, dt, t0, npts, ntrace)
        theta_p = AVO.angle_pp(vp_data, seis.attributes.get('offsets'),
                               npar_rt, 
                               dt, 
                               t0, 
                               npts, 
                               ntrace
        )

        print 'Theta P:', theta_p.shape
        #raise Exception()

        angle_pp = OM.new('angle', theta_p.T, name=seis.name+'_Angle', 
                               unit='m', domain='depth', 
                               sample_rate = dt,
                               datum = t0,
                               samples = theta_p.shape[0]
        )                       
        OM.add(angle_pp) 

        print 'OK Theta' 

        print seis.data.shape # (17L, 901L)
        
        ntrace = seis.data.shape[0]
        npts = seis.data.shape[1]
        ifirst = 0
        winsize = 1
        angmin = 0.0            # angulo minimo para PP
        angmax = 50.0           # angulo maximo para PP       
        
        #print ntrace, npts, ifirst, winsize, len(vp_data), len(vs_data), seis.data.T.shape, \
        #                    angmin, angmax, theta_p.shape#, 
        
        avo_data = AVO.avopp(results.get('itype'), 
                                 results.get('invmod'),
                                 ntrace, 
                                 ifirst, 
                                 winsize, 
                                 vp_data, vs_data, seis.data.T, 
                                 angmin, angmax, 
                                 theta_p, 
                                 npts      
        )


        if results.get('invmod') == 1:       
            seis_mod_pp_pp = OM.new('seismic', avo_data.T, 
                                   name=results.get('invmod_name')+'_MOD_PP', 
                                   unit='ms', 
                                   domain='time', 
                                   sample_rate=seis.step, 
                                   datum=0,
                                   samples=avo_data.shape[0],
                                   stacked='False'
            )       
            OM.add(seis_mod_pp_pp)     
            

        else:
            avo_data = avo_data.T
            inversion = OM.new('inversion', name=results.get('invmod_name'))
            OM.add(inversion)
    
            inv_index = OM.new('index_curve', seis.get_index().data,
                               name='DEPTH', 
                               unit=seis.get_index().name, 
                               curvetype=seis.get_index().attributes['curvetype'])
            OM.add(inv_index, inversion.uid)
    
            intercept = OM.new('inversion_parameter',
                         avo_data[0], 
                         name='Intercept', 
                         index_uid=inv_index.uid
            )
            OM.add(intercept, inversion.uid)
            
            
            
            gradient = OM.new('inversion_parameter',
                         avo_data[1], 
                         name='Gradient', 
                         index_uid=inv_index.uid
            )    
            OM.add(gradient, inversion.uid)
            
            #OM.new('s', 
            print type(avo_data)
            print len(avo_data)
            print avo_data.shape
        
            """
            avo_data = AVO.avopp(results.get('itype'), results.get('invmod'),
                                ntrace, 
                                #npts,
                                ifirst, 
                                winsize, 
                                vp_data, vs_data, seis.data.T, 
                                angmin, angmax, 
                                theta_p, 
                                npts      
            )
            if avo_data is None:
                raise Exception()
                
                
            print len(avo_data), len(avo_data[0]) 
            
            avo_data = np.asarray(avo_data)
            avo_data = avo_data.T
            
            
            
            
            print avo_data.shape
            
            #SUBROUTINE avopp(itype, irecon_flag, ntrace, npts, ifirst, winsize,  &
            #                 vp, vs, ampl, angmin, angmax, angle)
            
            #SUBROUTINE avopp_v2(itype, irecon_flag, ntrace, npts, ifirst, winsize,  &
            #                  vp, vs, ampl, angmin, angmax, angle)
            
            #qqcoisa = avopp(itype, 0, ntrace, ifirst, winsize, vp, vs, Rpp, angmin, angmax, theta_p, npts)
         
    
    
            seismic = OM.new('seismic', avo_data, 
                                   name=results.get('invmod_name'), 
                                   unit='ms', 
                                   domain='time', 
                                   sample_rate=seis.step, #segy_file.sample_rate*1000, 
                                   datum=0,
                                   samples=avo_data.shape[1],
                                   stacked='False'#,
                                   #trace_headers=trace_headers,
                                   #offsets=offsets
            )       
            OM.add(seismic)  
    
            """

    dlg.Destroy() 




def teste5(event):
    #
    OM = ObjectManager(event.GetEventObject()) 
    dlg = Dialog(None, title='Continuous Wavelet Transform', 
                 flags=wx.OK|wx.CANCEL
    )
    container = dlg.AddStaticBoxContainer(label='Seismic', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    #
    seismics = OrderedDict()
    for seis in OM.list('seismic'):
        seismics[seis.name] = seis.uid
    
    dlg.AddChoice(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='seismic', initial=seismics
    ) 


    container = dlg.AddStaticBoxContainer(label='Wavelet', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='wavelet', initial=WAVELET_TYPES
    ) 

    container = dlg.AddStaticBoxContainer(label='Scale resolution', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddTextCtrl(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='dj', initial='0.125'
    ) 


    ###
    container = dlg.AddStaticBoxContainer(label='Mode', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='mode', initial=WAVELET_MODES
    ) 
    ###

    container = dlg.AddStaticBoxContainer(label='New object name', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    
    dlg.AddTextCtrl(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='cwt_name', initial=''
    )    

    dlg.SetSize((270, 430))
    result = dlg.ShowModal()

    
    try:
    
        if result == wx.ID_OK:
            results = dlg.get_results()  
            print results
            
            disableAll = wx.WindowDisabler()
            wait = wx.BusyInfo("Applying CWT. Wait...")
            
    
            dj = float(results.get('dj'))

            
            wavelet = results.get('wavelet')        
            if wavelet == 'morlet':
                func = Morlet()
            elif wavelet == 'ricker':
                func = Ricker()
            elif wavelet == 'dog3':
                func = DOG(m=3) 
            elif wavelet == 'dog4':
                func = DOG(m=4)             
            elif wavelet == 'dog5':
                func = DOG(m=5) 
            elif wavelet == 'dog6':
                func = DOG(m=6) 
            elif wavelet == 'paul2':
                func = Paul(m=2) 
            elif wavelet == 'paul3':
                func = Paul(m=3) 
            elif wavelet == 'paul4':
                func = Paul(m=4) 
            elif wavelet == 'paul5':
                func = Paul(m=5)             
            elif wavelet == 'paul6':
                func = Paul(m=6) 
            else:
                raise Exception()   
    
            obj = OM.get(results.get('seismic')) 
            
            #'''
            print
            print obj.name
            print obj.data.shape
            print obj.get_index().data.shape
            print np.isfinite(obj.data).shape
            #'''
    
    
            mode = results.get('mode')        

    
            
    
            # TODO: fazer essa conversao pelo UOM
            time = obj.get_index().data / 1000    
            step = obj.step / 1000
            
            # seis.dimensions or seis.data.shape
            if len(seis.data.shape) == 4:
                iaxis, jaxis, kaxis, zaxis = seis.data.shape
                data_out = None
                for i in range(iaxis):
                    for j in range(jaxis):
                        for k in range(kaxis):
                             wt = WaveletTransform(seis.data[i][j][k], dj=dj,
                                                   wavelet=func, 
                                                   dt=step,
                                                   time=time
                             )
                             wt_axis = wt.wavelet_transform.shape[0]
                             #print (i, j, k), wt.wavelet_transform.shape, np.flip(wt.fourier_frequencies, 0)#, wt.scales
                             
                             if data_out is None:
                                 data_out = np.zeros((iaxis, jaxis, kaxis, wt_axis, zaxis))    
                                 freqs =  np.flip(wt.fourier_frequencies, 0)
                                 scales = np.flip(wt.scales, 0)
                             if mode == 0:
                                 data_out[i][j][k] = np.abs(np.flip(wt.wavelet_transform), 0)      
                             elif mode == 1:            
                                 # np.abs(self.wavelet_transform) ** 2
                                 data_out[i][j][k] = np.flip(wt.wavelet_power, 0)         
                             elif mode == 2 or mode ==3:   
                                 data_out[i][j][k] = np.angle(np.flip(wt.wavelet_transform), 0)
                             if mode == 3:   
                                 data_out[i][j][k] = np.unwrap(np.flip(wt.wavelet_transform, 0), axis=0)    

            
            
            #print
            #print obj.get_index().data
            #print obj.step
            #print "Fim CWT:", data_out.shape                 
                
            #for dim_name, dim_values in seis.dimensions:
            #    print '\n', dim_name, dim_values
    
    
            dims = copy.deepcopy(seis.dimensions)
            dims.append(('Frequencies', freqs))
    
           # a = np.flip(a, 2)
    
    
            name = results.get('cwt_name')

            
            
            #"""
            scalogram = OM.new('scalogram', data_out, dims, name=name, 
                                   unit=seis.attributes.get('unit'), 
                                   domain=seis.attributes.get('domain', 'time'), 
                                   sample_rate=seis.attributes.get('sample_rate'), 
                                   datum=seis.attributes.get('datum'),
                                   samples=seis.attributes.get('samples')
            )
            OM.add(scalogram)
            #"""
            
            #valid_data = obj.data[np.isfinite(obj.data)]
            #valid_index_data = obj.get_index().data[np.isfinite(obj.data)]
           
            
            #wt = WaveletTransform(valid_data, dj=dj, wavelet=func, dt=obj.step,
            #                      time=valid_index_data
            #)
            
            '''
            OM = ObjectManager(obj) 
            seismic = OM.new('scalogram', data, name=results.get('cwt_name')+'_CWT', 
                                   unit='m', domain='depth', 
                                   sample_rate=wt.time[1] - wt.time[0],
                                   datum=wt.time[0],
                                   samples= len(wt.time),
                                   frequencies=wt.fourier_frequencies,
                                   periods=wt.fourier_periods,
                                   scales=wt.scales
            )                       
            OM.add(seismic)  
            '''
        
        del wait
        del disableAll
    except Exception as e:
        print '\n', e.message, e.args
        pass
    finally:
        dlg.Destroy()     

        


def teste3(event):
    
    OM = ObjectManager(event.GetEventObject())

    fs = 250.0
    #fs = 1000.0
    ts = 1/fs
    start = 0.0 #seconds
    end = 6.0 #seconds
    depth = np.arange(start, end+ts, ts)
    
    freq = 1.0
    amp = 77
    #freq = freq/1000
    d1 = amp * np.cos(depth * 2 * np.pi * freq)

    #freq = freq/1000
    amp = 55
    d2 = amp * np.sin(depth * 2 * np.pi * freq)


    print d1.shape
    print d2.shape
    data = np.asarray([d1, d2])    
    print data.shape


    seismic = OM.new('seismic', data, name='Synthetic', 
                           unit='ms', domain='depth', 
                           sample_rate=ts*1000, datum=0,
                           samples=int(data.shape[1]),
                           stacked=True,
                           traces=int(data.shape[0]),
                           offsets=None
    )
             
    OM.add(seismic) 
    



def teste2(event):
    
    OM = ObjectManager(event.GetEventObject())
    well = OM.new('well', name='ACME_XPTO_002')
    OM.add(well)

    depth = np.array([1000.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0, 7000.0])
    index = OM.new('index_curve', depth, name='DEPTH', unit='m', curvetype='MD')
    well.index.append(index)
    OM.add(index, well.uid)

    data = np.array([0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0])
    log = OM.new('log', data, name='LOG_TESTE_CURVE', unit='amplitude', curvetype='', index_uid=index.uid)
    OM.add(log, well.uid)
    

def teste(event):
    
    OM = ObjectManager(event.GetEventObject())
    well = OM.new('well', name='ACME_XPTO_2')
    OM.add(well)
    
    fs = 250.0
    ts = 1/fs
    start = 2000.0
    end = 3000.0
    depth = np.arange(start, end+ts, ts)
    index = OM.new('index_curve', depth, name='DEPTH', unit='m', curvetype='MD')
    well.index.append(index)
    OM.add(index, well.uid)


    """
    Fs = 250.0 # Hz    
    Ts = 1/Fs  
    t0 = 0.0
    t1 = 5000.0
    time = np.arange(t0, t1+Ts, Ts)
    f1 = 30
    #print 'Curva cosseno com frequencia:', f1, 'Hz'
    x = 20 * np.cos(time * 2 * np.pi * f1)
    """

    freq = 20.0
    amp = 50
    #freq = freq/1000
    data = amp * np.sin(depth * 2 * np.pi * freq)
    log = OM.new('log', data, name='COS_20_A50', unit='amplitude', curvetype='', index_uid=index.uid)
    OM.add(log, well.uid)


    freq = 30.0
    amp = 20
    #freq = freq/1000
    data = amp * np.sin(depth * 2 * np.pi * freq)
    log = OM.new('log', data, name='SEN_30_A20', unit='amplitude', curvetype='', index_uid=index.uid)
    OM.add(log, well.uid)

    freq = 2.0
    amp = 100
    #freq = freq/1000
    data = amp * np.sin(depth * 2 * np.pi * freq)
    log = OM.new('log', data, name='SEN_2_A100', unit='amplitude', curvetype='', index_uid=index.uid)
    OM.add(log, well.uid)    


    freq = 2.0
    amp = 100
    #freq = freq/1000
    data = amp * np.cos(depth * 2 * np.pi * freq)
    log = OM.new('log', data, name='COS_2_A100', unit='amplitude', curvetype='', index_uid=index.uid)
    OM.add(log, well.uid)    

    freq = 2.0
    amp = 50
    #freq = freq/1000
    data = amp * np.cos(depth * 2 * np.pi * freq)
    log = OM.new('log', data, name='COS_2_A50', unit='amplitude', curvetype='', index_uid=index.uid)
    OM.add(log, well.uid)    


def on_open(*args, **kwargs):
    wildcard = "Arquivo de projeto do GRIPy (*.pgg)|*.pgg"
    try:
        fdlg = wx.FileDialog(wx.App.Get().GetTopWindow(), 
                             'Escolha o arquivo PGG', 
                             wildcard=wildcard, 
                             style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
        )
        if fdlg.ShowModal() == wx.ID_OK:
            file_name = fdlg.GetFilename()
            dir_name = fdlg.GetDirectory()
            fdlg.Destroy()
        else:
            fdlg.Destroy()
            return
        fullfilename = os.path.join(dir_name, file_name)    
        gripy_app = wx.App.Get()
        gripy_app.load_project_data(fullfilename)
    except Exception:
        raise


def on_save(*args, **kwargs):
    gripy_app = wx.App.Get() 
    gripy_app.on_save()


def on_save_as(*args, **kwargs):
    gripy_app = wx.App.Get()
    gripy_app.on_save_as()

       
 
def on_new_logplot(event):
    UIM = UIManager()
    root_controller = UIM.get_root_controller()        
    UIM.create('logplot_controller', root_controller.uid)
    
def on_rock(event):
    OM = ObjectManager(event.GetEventObject()) 
    dlg = Dialog(None, title='Rock selector', flags=wx.OK|wx.CANCEL)
    dlg.SetSize((800, 600))
    cont_sup = dlg.AddStaticBoxContainer(label='Support', 
                                          orient=wx.HORIZONTAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )
    cont_grain = dlg.AddStaticBoxContainer(label='Grain Parts', 
                                          orient=wx.HORIZONTAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )
    cont_matr = dlg.AddStaticBoxContainer(label='Matrix Parts', 
                                          orient=wx.HORIZONTAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )
    options = OrderedDict()
    partitions = OrderedDict()
    
    options['PT'] = 'PT'
    options['FACIES'] = 'FACIES'
    options['TOP&BASE'] = 'TOP&BASE'
    
    for well in OM.list('well'):
        for partition in OM.list('partition', well.uid):
            partitions[partition.get_friendly_name()] = partition.uid
            
    #reference
    dlg.AddStaticText(cont_sup, initial='Type of Support   ')
    dlg.AddChoice  (cont_sup, widget_name='suporte', initial=options)
    dlg.AddTextCtrl(cont_sup, widget_name='point', initial='1500')
    dlg.AddTextCtrl(cont_sup, widget_name='top', initial='1000')
    dlg.AddTextCtrl(cont_sup, widget_name='base', initial='2000')
    dlg.AddChoice(cont_sup, widget_name='fac', initial=partitions)
#    def text_return(self, event):
#        lst = ['3','4']
#        print '1\n'
#    vels = OrderedDict()
#    for vel in OM.list('velocity'):
#        vels[vel.name] = vel.uid
#    print '\n\nchoice\n', choice, type(choice), type(cont_matr)
    #matrix grain
    dlg.AddStaticText(cont_grain, proportion=0, initial='Fraction '
#                  widget_name='fraction1', initial='Fraction '
    )
    dlg.AddTextCtrl(cont_grain, proportion=0, 
                  widget_name='frac1', initial='0.20'
    )
    dlg.AddStaticText(cont_grain,
                  widget_name='K_Modulus', initial='K Modulus (GPa) '
    )
    dlg.AddTextCtrl(cont_grain, 
                  widget_name='kmod1', initial='36.5'
    )
    dlg.AddStaticText(cont_grain,  
                  widget_name='G_Modulus', initial='G Modulus (GPa) '
    )
    dlg.AddTextCtrl(cont_grain, 
                  widget_name='gmod1', initial='78.6'
    )
    dlg.AddStaticText(cont_grain,
                  widget_name='Density', initial='Density (g/cc) '
    )
    dlg.AddTextCtrl(cont_grain,
                  widget_name='dens1', initial='2.65'
    )
    # matrix content
    dlg.AddStaticText(cont_matr, proportion=0, 
                  widget_name='fraction2', initial='Fraction '
    )
    dlg.AddTextCtrl(cont_matr, proportion=0, 
                  widget_name='frac2', initial='0.20'
    )
    dlg.AddStaticText(cont_matr,
                  widget_name='K_Modulus2', initial='K Modulus (GPa) '
    )
    dlg.AddTextCtrl(cont_matr, 
                  widget_name='kmod2', initial='36.5'
    )
    dlg.AddStaticText(cont_matr,  
                  widget_name='G_Modulus2', initial='G Modulus (GPa) '
    )
    dlg.AddTextCtrl(cont_matr, 
                  widget_name='gmod2', initial='78.6'
    )
    dlg.AddStaticText(cont_matr,
                  widget_name='Density2', initial='Density (g/cc) '
    )
    dlg.AddTextCtrl(cont_matr,
                  widget_name='dens2', initial='2.65'
    )
#    dlg.AddStaticText(c1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
#                  widget_name='xaxis')#, initial=options)
#    dlg.AddStaticText(c2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
#                  widget_name='Yaxis')#, initial=options)
#    dlg.AddStaticText(c3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
#                  widget_name='Zaxis')#, initial=options)
#    results = dlg.get_results()  
#        print '\nresults:', results
        #
#    print '\n\nresults\n',results.get('suporte')
    result = dlg.ShowModal()
    print 'result0'
    if result == wx.ID_OK:
        print 'result1'
        results = dlg.get_results()  
        print '\nresults2'
        #
        print '\nresult.get', results.get('suporte')
    dlg.Destroy()
#    if result != wx.ID_OK:
#        dlg.destroy()
#    #
#    c1 = dlg.AddStaticBoxContainer(label='X-axis', 
#                                          orient=wx.VERTICAL, proportion=0, 
#                                          flag=wx.EXPAND|wx.TOP, border=5
#    )   
#    dlg.AddChoice(c1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
#                  widget_name='xaxis', initial=options
#    ) 
#    #
#    c2 = dlg.AddStaticBoxContainer(label='Y-axis', 
#                                          orient=wx.VERTICAL, proportion=0, 
#                                          flag=wx.EXPAND|wx.TOP, border=5
#    )   
#    dlg.AddChoice(c2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
#                  widget_name='yaxis', initial=options
#    )     
#    #
#    c3 = dlg.AddStaticBoxContainer(label='Colorbar', 
#                                          orient=wx.VERTICAL, proportion=0, 
#                                          flag=wx.EXPAND|wx.TOP, border=5
#    )   
#    options.update(partitions)
#    dlg.AddChoice(c3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
#                  widget_name='zaxis', initial=options
#    )       
#    dlg.SetSize((230, 300))
##    dlg.SetSize((230, 350))
#    result = dlg.ShowModal()
#    if result == wx.ID_OK:
#        results = dlg.get_results()  
##        print '\nresults:', results
#        #
#        if not results.get('xaxis') or not results.get('yaxis'):# or not results.get('zaxis'):
#            dlg.Destroy()
#            return
    
def on_new_crossplot(event):
    
    OM = ObjectManager(event.GetEventObject()) 
    #
    options = OrderedDict()
    partitions = OrderedDict()
    
    for inv in OM.list('inversion'):
        for index in OM.list('index_curve', inv.uid):
            options[index.get_friendly_name()] = index.uid
        for invpar in OM.list('inversion_parameter', inv.uid):
            options[invpar.get_friendly_name()] = invpar.uid            
    for well in OM.list('well'):
        for index in OM.list('index_curve', well.uid):
            options[index.get_friendly_name()] = index.uid
        for log in OM.list('log', well.uid):
            options[log.get_friendly_name()] = log.uid
        for partition in OM.list('partition', well.uid):
            partitions[partition.get_friendly_name()] = partition.uid
            
    #    
    dlg = Dialog(None, title='Crossplot selector', flags=wx.OK|wx.CANCEL)
    #
    c1 = dlg.AddStaticBoxContainer(label='X-axis', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(c1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='xaxis', initial=options
    ) 
    #
    c2 = dlg.AddStaticBoxContainer(label='Y-axis', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddChoice(c2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='yaxis', initial=options
    )     
    #
    c3 = dlg.AddStaticBoxContainer(label='Colorbar', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    options.update(partitions)
    dlg.AddChoice(c3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='zaxis', initial=options
    ) 
    #
#    c4 = dlg.AddStaticBoxContainer(label='Partition', 
#                                          orient=wx.VERTICAL, proportion=0, 
#                                          flag=wx.EXPAND|wx.TOP, border=5
#    )   
#    dlg.AddChoice(c4, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
#                  widget_name='waxis', initial=partitions
#    ) 
    #        
    dlg.SetSize((230, 300))
#    dlg.SetSize((230, 350))
    result = dlg.ShowModal()
    if result == wx.ID_OK:
        results = dlg.get_results()  
#        print '\nresults:', results
        #
        if not results.get('xaxis') or not results.get('yaxis'):# or not results.get('zaxis'):
            dlg.Destroy()
            return
        #
        UIM = UIManager()
        root_controller = UIM.get_root_controller()        
        cp_ctrl = UIM.create('crossplot_controller', root_controller.uid)  
        cpp = cp_ctrl.view
        xaxis_obj = OM.get(results.get('xaxis'))
        yaxis_obj = OM.get(results.get('yaxis'))
        cpp.crossplot_panel.set_xdata(xaxis_obj.data)
        cpp.crossplot_panel.set_xlabel(xaxis_obj.name)
        cpp.crossplot_panel.set_ydata(yaxis_obj.data)
        cpp.crossplot_panel.set_ylabel(yaxis_obj.name)
        #
        #'''
        print '\n\nzaxis', results.get('zaxis')
        if results.get('zaxis') is not None:
            zaxis_obj = OM.get(results.get('zaxis'))
            if zaxis_obj.tid == 'partition':
                cpp.crossplot_panel.set_zdata(zaxis_obj.getaslog())
                cpp.crossplot_panel.set_zlabel(zaxis_obj.name)
                classcolors = {}
                classnames = {}
                for part in OM.list('part', zaxis_obj.uid):
                    classcolors[part.code] = tuple(c/255.0 for c in part.color)
                    classnames[part.code] = part.name
                cpp.crossplot_panel.set_classcolors(classcolors)
                cpp.crossplot_panel.set_classnames(classnames)
                cpp.crossplot_panel.set_nullclass(-1)
                cpp.crossplot_panel.set_nullcolor((0.0, 0.0, 0.0))
                cpp.crossplot_panel.set_zmode('classes')
            else:
                cpp.crossplot_panel.set_zdata(zaxis_obj.data)
                cpp.crossplot_panel.set_zlabel(zaxis_obj.name)
                cpp.crossplot_panel.set_zmode('continuous')
        elif results.get('waxis') is not None:
            waxis_obj = OM.get(results.get('waxis'))
            cpp.crossplot_panel.set_parts(waxis_obj.getdata())  # TODO: ver o que é necessário fazer quando não se escolhe wcpp.crossplot_panel.set_zmode('solid')
#            raise Exception("Not Implemented yet!")
            #print "Not Implemented yet!"  # TODO: fazer alguma coisa quando não escolhe z (cor sólida)
        
        else:
            cpp.crossplot_panel.set_zmode('solid')
#            waxis_obj = OM.get(results.get('waxis'))
#            cpp.crossplot_panel.set_parts(waxis_obj.getdata())  # TODO: ver o que é necessário fazer quando não se escolhe w
        #'''
        cpp.crossplot_panel.plot()
      #  self.notebook.AddPage(cpp, "Crossplot - {}".format(self.OM.get(welluid).name), True)
        cpp.crossplot_panel.draw()        
        
        
    dlg.Destroy()


    '''
    UIM = UIManager()
    root_controller = UIM.get_root_controller()        
    UIM.create('crossplot_controller', root_controller.uid)   
    #UIM.create('workpage_controller', root_controller.uid)
    '''        
    
def on_debugconsole(event):
    consoleUI = DebugConsoleFrame(wx.App.Get().GetTopWindow())
    consoleUI.Show()    
    
    


def on_import_las(event):
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    wildcard="Arquivos LAS (*.las)|*.las"
    fdlg = wx.FileDialog(wx.App.Get().GetTopWindow(), 'Escolha o arquivo LAS', 
                         wildcard=wildcard, style=style)
    if fdlg.ShowModal() == wx.ID_OK:
        file_name = fdlg.GetFilename()
        dir_name  = fdlg.GetDirectory()
        fdlg.Destroy()
    else:
        fdlg.Destroy()
        return
    las_file = FileIO.LAS.open(os.path.join(dir_name, file_name), 'r')
    las_file.read()
    hedlg = HeaderEditor.Dialog(wx.App.Get().GetTopWindow())
    hedlg.set_header(las_file.header)

    if hedlg.ShowModal() == wx.ID_OK:
        las_file.header = hedlg.get_header()
        names = las_file.curvesnames
        units = las_file.curvesunits
        ncurves = len(names)

        # Tentativa de solução não lusitana
        
        PM = ParametersManager.get()
        
        curvetypes = PM.getcurvetypes()
        datatypes = PM.getdatatypes()
        
        sel_curvetypes = [PM.getcurvetypefrommnem(name) for name in names]
        
        sel_datatypes = []
        for name in names:
            datatype = PM.getdatatypefrommnem(name)
            if not datatype:
                sel_datatypes.append('Log')
            else:
                sel_datatypes.append(datatype)

        isdlg = ImportSelector.Dialog(wx.App.Get().GetTopWindow(),
                                      names, units, curvetypes, datatypes)
        
        isdlg.set_curvetypes(sel_curvetypes)
        isdlg.set_datatypes(sel_datatypes)
        
        if isdlg.ShowModal() == wx.ID_OK:
            sel_curvetypes = isdlg.get_curvetypes()
            sel_datatypes = isdlg.get_datatypes()
            data = las_file.data
            
            OM = ObjectManager(event.GetEventObject())
            well = OM.new('well', name=las_file.wellname, 
                              LASheader=las_file.header)
            OM.add(well)
            
            index = None
            
            for i in range(ncurves):
                if sel_curvetypes[i]:
                    PM.voteforcurvetype(names[i], sel_curvetypes[i])

                if sel_datatypes[i]:
                    PM.votefordatatype(names[i], sel_datatypes[i])
                
                if sel_datatypes[i] == 'Index':
                    index = OM.new('index_curve', data[i], name=names[i], 
                                       unit=units[i].lower(), curvetype=sel_curvetypes[i])
                    well.index.append(index)
                    OM.add(index, well.uid)
                
                elif sel_datatypes[i] == 'Log':
                    log = OM.new('log', data[i], name=names[i], 
                                unit=units[i].lower(), curvetype=sel_curvetypes[i],
                                index_uid=index.uid
                    )
                    OM.add(log, well.uid)

                elif sel_datatypes[i] == 'Partition':
                    try:
                        booldata, codes = DT.DataTypes.Partition.getfromlog(data[i])
                    except TypeError:
                        print 'data[{}]: {}'.format(i, data[i])
                        raise
                    partition = OM.new('partition', name=names[i], 
                                           curvetype=sel_curvetypes[i],
                                           index_uid=index.uid
                    )
                    OM.add(partition, well.uid)
                    for j in range(len(codes)):
                        part = OM.new('part', booldata[j], 
                            code=int(codes[j]), curvetype=sel_curvetypes[i])
                        OM.add(part, partition.uid)
                else:
                    print "Not importing {} as no datatype matches '{}'".format(names[i], sel_datatypes[i])
                 
        PM.register_votes()
        isdlg.Destroy()
    hedlg.Destroy()



def on_import_odt(event):
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    wildcard="Arquivos ODT (*.wll)|*.wll"
#        self.odt_dir_name = ''
    fdlg = wx.FileDialog(wx.App.Get().GetTopWindow(), 'Escolha o projeto a carregar', wildcard=wildcard, style=style)
    if fdlg.ShowModal() == wx.ID_OK:
        file_proj = fdlg.GetFilename()
        odt_dir_name = fdlg.GetDirectory()
        fdlg.Destroy()
    else:
        fdlg.Destroy()
        return
    odt_file = FileIO.ODT.open(odt_dir_name, file_proj, 'r')
    hedlg = ODTEditor.Dialog()
#    print odt_file.ndepth
    hedlg.set_header(odt_file.fileheader, odt_file.logheader, odt_file.ndepth)

    if hedlg.ShowModal() == wx.ID_OK:
        OM = ObjectManager(event.GetEventObject())
        odt_file.header = hedlg.get_header()
        print 'header 2\n', odt_file.header

        names = [line['MNEM'] for line in odt_file.header["C"].itervalues()]
        units = [line['UNIT'] for line in odt_file.header["C"].itervalues()]
        ncurves = len(names)
        
        """
        # TODO: acabar com essa verdadeira gambiarra e colocar em um arquivo json, além de implementar uma persistência
        
        curvetypes = ['Azimuth', 'BVW', 'BitSize', 'CBHP', 'CDP',
                      'Caliper', 'Coord.', 'CoreGD', 'CorePerm', 'CorePhi',
                      'DVcl', 'DeepRes', 'Density', 'Depth', 'Deviation',
                      'Drho', 'ECD', 'EPT', 'FlowRate', 'GAS', 'GammaRay',
                      'Hookload', 'LoadFactor', 'Matrix', 'MaxHorzStress',
                      'MedRes', 'MicroRes', 'MinHorzStress', 'Mineral',
                      'NMRbfi', 'NMRcbfi', 'NMRffi', 'NMRperm', 'NMRphi',
                      'NMRphiT', 'NMRswi', 'Neutron', 'OnBottom',
                      'OrigResPress', 'PEF', 'Perforations', 'Phi', 'PhiT',
                      'Pump', 'RB_Offset', 'ROP', 'RotarySpeed', 'SP',
                      'ShalRes', 'ShearSonic', 'ShearVel', 'Sigma',
                      'Sonic', 'Spectral', 'StickSlip', 'StressAzimuth',
                      'Sw', 'Temp', 'Tension', 'Tool_Azimuth',
                      'Tool_RelBearng', 'Torque', 'TwcPredicted', 'Vcl',
                      'Vcoal', 'Velocity', 'VertStress', 'Vibration',
                      'Vsalt', 'Vsilt', 'WeightonBit', 'Xaccelerometer',
                      'Xmagnetometer', 'Yaccelerometer', 'Ymagnetometer',
                      'Zaccelerometer', 'Zmagnetometer']
        
        datatypes = ['Depth', 'Log', 'Partition']
        
        sel_curvetypes = ['']*ncurves
        sel_datatypes = ['Depth'] + ['Log']*(ncurves - 1)
        
        """ 
        # Tentativa de solução não lusitana
        
        PM = ParametersManager.get()
        
        curvetypes = PM.getcurvetypes()
        datatypes = PM.getdatatypes()
        
        sel_curvetypes = [PM.getcurvetypefrommnem(name) for name in names]
        
        sel_datatypes = []
        for name in names:
            datatype = PM.getdatatypefrommnem(name)
            if not datatype:
                sel_datatypes.append('Log')
            else:
                sel_datatypes.append(datatype)
        
        # """

        isdlg = ImportSelector.Dialog(wx.App.Get().GetTopWindow(), names, units, curvetypes, datatypes)
        
        isdlg.set_curvetypes(sel_curvetypes)
        isdlg.set_datatypes(sel_datatypes)
        
        if isdlg.ShowModal() == wx.ID_OK:
            
            sel_curvetypes = isdlg.get_curvetypes()
            sel_datatypes = isdlg.get_datatypes()
            
            data = odt_file.data
            well = OM.new('well', name=odt_file.filename, LASheader=odt_file.header)
           
            OM.add(well)
            for i in range(ncurves):
                if sel_curvetypes[i]:
                    PM.voteforcurvetype(names[i], sel_curvetypes[i])
            
                if sel_datatypes[i]:
                    PM.votefordatatype(names[i], sel_datatypes[i])
            
                if sel_datatypes[i] == 'Depth':
                    # print "Importing {} as '{}' with curvetype '{}'".format(names[i], sel_datatypes[i], sel_curvetypes[i])
                    depth = OM.new('depth', data[i], name=names[i], unit=units[i], curvetype=sel_curvetypes[i])
                    OM.add(depth, well.uid)
                
                elif sel_datatypes[i] == 'Log':
                    # print "Importing {} as '{}' with curvetype '{}'".format(names[i], sel_datatypes[i], sel_curvetypes[i])
                    log = OM.new('log', data[i], name=names[i], unit=units[i], curvetype=sel_curvetypes[i])
                    OM.add(log, well.uid)

                elif sel_datatypes[i] == 'Partition':
                    # print "Importing {} as '{}' with curvetype '{}'".format(names[i], sel_datatypes[i], sel_curvetypes[i])
                    booldata, codes = DT.DataTypes.Partition.getfromlog(data[i])
                    
                    partition = OM.new('partition', name=names[i], curvetype=sel_curvetypes[i])
                    OM.add(partition, well.uid)
                    
            
                    for j in range(len(codes)):
                        part = OM.new('part', booldata[j], code=int(codes[j]), curvetype=sel_curvetypes[i])
                        OM.add(part, partition.uid)
                
                else:
                    print "Not importing {} as no datatype matches '{}'".format(names[i], sel_datatypes[i])
                
        
        PM.register_votes()
                
        isdlg.Destroy()

    hedlg.Destroy()




def on_import_lis(event):
    lis_import_frame = lisloader.LISImportFrame(wx.App.Get().GetTopWindow())
    lis_import_frame.Show()
 
    


def on_import_segy_seis(event):
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    wildcard="Arquivos SEG-Y (*.sgy)|*.sgy"
    
    file_dlg = wx.FileDialog(wx.App.Get().GetTopWindow(), 
                         'Escolha o arquivo SEG-Y', 
                         wildcard=wildcard, style=style
    )
    result = file_dlg.ShowModal()
    if result == wx.ID_OK:
        file_name = file_dlg.GetFilename()
        dir_name  = file_dlg.GetDirectory()
    file_dlg.Destroy()
    if result == wx.ID_CANCEL:
        return
    name = file_name.split('.')[0]
    utils.load_segy(event, os.path.join(dir_name, file_name), 
                    new_obj_name=name, comparators_list=None, 
              iline_byte=9, xline_byte=21, offset_byte=37
    )
    


def on_import_segy_well_gather(event):
    dlg = Dialog(None, title='Well Gather load', 
                 flags=wx.OK|wx.CANCEL
    )

    container = dlg.AddStaticBoxContainer(label='File', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.AddFilePickerCtrl(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='filename', wildcard="SEG-Y files (*.sgy)|*.sgy",
                  #style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST#,
                  message='Choose SEG-Y file'
    ) 


    container = dlg.AddBoxSizerContainer(orient=wx.HORIZONTAL)
    #                                  
    c1 = dlg.AddStaticBoxContainer(container, label='ILine',
                                          orient=wx.VERTICAL, proportion=1, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )  
    
    dlg.AddTextCtrl(c1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='iline_byte', initial='9'
    ) 
    #
    c2 = dlg.AddStaticBoxContainer(container, label='XLine',
                                          orient=wx.VERTICAL, proportion=1, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )  
    dlg.AddTextCtrl(c2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='xline_byte', initial='21'
    ) 
    #
    c3 = dlg.AddStaticBoxContainer(container, label='Offset',
                                          orient=wx.VERTICAL, proportion=1, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )  
    dlg.AddTextCtrl(c3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='offset_byte', initial='37'
    ) 
    #
    container = dlg.AddStaticBoxContainer(label='Where', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )  
    
    c1 = dlg.AddStaticBoxContainer(container, label='ILine',
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )  
    
    dlg.AddTextCtrl(c1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='iline_number'
    ) 
    #
    c2 = dlg.AddStaticBoxContainer(container, label='XLine',
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )  
    dlg.AddTextCtrl(c2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='xline_number'
    )    
    #
    container = dlg.AddStaticBoxContainer(label='Well', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    #
    wells = OrderedDict()
    OM = ObjectManager(event.GetEventObject())
    for well in OM.list('well'):
        wells[well.name] = well.uid
    #
    dlg.AddChoice(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='welluid', initial=wells
    )     
    #
    container = dlg.AddStaticBoxContainer(label='Well gather name', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )      
    dlg.AddTextCtrl(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='wellgather_name'
    )        
    #
    dlg.SetSize((460, 500))
    #
    try:
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            results = dlg.get_results()  
            print results
            #
            filename = results.get('filename')
            iline_byte = int(results.get('iline_byte'))
            xline_byte = int(results.get('xline_byte'))
            offset_byte = int(results.get('offset_byte'))
            welluid = results.get('welluid')
            wellgather_name = results.get('wellgather_name')
            
            if not welluid:
                raise Exception('')
            #
            if results.get('iline_number'):
                iline_number = int(results.get('iline_number'))
            else:
                iline_number = None
            if results.get('xline_number'):     
                xline_number = int(results.get('xline_number'))
            else:
                xline_number = None
            comparators = []
            if iline_number: 
                comparators.append((iline_byte, 4, '==', iline_number))
            if xline_number: 
                comparators.append((xline_byte, 4, '==', xline_number))                
            #
            utils.load_segy(event, filename, 
                new_obj_name=wellgather_name, 
                comparators_list=comparators, 
                iline_byte=iline_byte, xline_byte=xline_byte, 
                offset_byte=offset_byte, tid='gather', parentuid=welluid
            )
            
            """
            filename = 'D:\\Sergio_Adriano\\NothViking\\Mobil_AVO_Viking_pstm_16_CIP_stk.sgy'
            name = 'Mobil_AVO_Viking_pstm_16_CIP_stk'
            utils.load_segy(event, filename, 
                new_obj_name=name, 
                comparators_list=[(21, 4, '==', 808), (21, 4, '==', 1572)], 
                iline_byte=9, xline_byte=21, offset_byte=37
            )
            """
    #   
    except Exception as e:
        print e
        pass
    finally:
        dlg.Destroy()

 
   
def on_import_segy_vel(event):
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    wildcard="SEG-Y files (*.sgy)|*.sgy"
    fdlg = wx.FileDialog(wx.App.Get().GetTopWindow(), 'Choose SEG-Y file', 
                         wildcard=wildcard, style=style)
    if fdlg.ShowModal() == wx.ID_OK:
        file_name = fdlg.GetFilename()
        dir_name  = fdlg.GetDirectory()
        fdlg.Destroy()
    else:
        fdlg.Destroy()
        return
    
    segy_file = FileIO.SEGY.SEGYFile(os.path.join(dir_name, file_name))
    segy_file.read()
    name = segy_file.filename.rsplit('\\')[-1]
    name = name.split('.')[0]
    

    OM = ObjectManager(event.GetEventObject())     
    velocity = OM.new('velocity', segy_file.data, name=name, 
                           unit='ms', domain='time', 
                           sample_rate=segy_file.sample_rate*1000, datum=0,
                           samples=segy_file.number_of_samples,
                           #stacked=stacked,
                           traces=int(segy_file.data.shape[0])
    )
             
    OM.add(velocity)                   
   


def on_export_las(event):

    esdlg = ExportSelector.Dialog(wx.App.Get().GetTopWindow())
    if esdlg.ShowModal() == wx.ID_OK:
        OM = ObjectManager(event.GetEventObject())   
        ###
        # TODO: Colocar isso em outro lugar
        names = []
        units = []
        data = []
        for depthuid in esdlg.get_depth_selection():
            depth = OM.get(depthuid)
            names.append(depth.name)
            units.append(depth.unit)
            data.append(depth.data)
        for loguid in esdlg.get_log_selection():
            log = OM.get(loguid)
            names.append(log.name)
            units.append(log.unit)
            data.append(log.data)
        for partitionuid in esdlg.get_partition_selection():
            partition = OM.get(partitionuid)
            names.append(partition.name)
            units.append('')
            data.append(partition.getaslog())
        for partitionuid, propselection in esdlg.get_property_selection().iteritems():
            partition = OM.get(partitionuid)
            for propertyuid in propselection:
                prop = OM.get(propertyuid)
                names.append(prop.name)
                units.append(prop.unit)
                data.append(partition.getaslog(propertyuid))
        data = np.asanyarray(data)
        ###
        
        welluid = esdlg.get_welluid()
        well = OM.get(welluid)
        header = well.attributes.get("LASheader", None)
        if header is None:
            header = FileIO.LAS.LASWriter.getdefaultheader()
        
        header = FileIO.LAS.LASWriter.rebuildwellsection(header, data[0], units[0])
        header = FileIO.LAS.LASWriter.rebuildcurvesection(header, names, units)
        
        hedlg = HeaderEditor.Dialog(wx.App.Get().GetTopWindow())
        hedlg.set_header(header)
        
        if hedlg.ShowModal() == wx.ID_OK:
            style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            wildcard="Arquivos LAS (*.las)|*.las"
            fdlg = wx.FileDialog(wx.App.Get().GetTopWindow(), 
                                 'Escolha o arquivo LAS', 
                                 wildcard=wildcard, style=style
            )
            if fdlg.ShowModal() == wx.ID_OK:
                file_name = fdlg.GetFilename()
                las_dir_name = fdlg.GetDirectory()
                header = hedlg.get_header()
                las_file = FileIO.LAS.open(os.path.join(las_dir_name, file_name), 'w')
                las_file.header = header
                las_file.data = data
                las_file.headerlayout = FileIO.LAS.LASWriter.getprettyheaderlayout(header)
                las_file.write()
            fdlg.Destroy()
        hedlg.Destroy()
    esdlg.Destroy()



def on_partitionedit(event):
    OM = ObjectManager(event.GetEventObject())
    if not OM.list('partition'):
        return
    dlg = PartitionEditor.Dialog(wx.App.Get().GetTopWindow())
    dlg.ShowModal()
    dlg.Destroy()
    
    _UIM = UIManager()
    tree_ctrl = _UIM.list('tree_controller')[0]
    tree_ctrl.refresh() 
    
    #
 



def on_load_wilson(event):
    
    def in1d_with_tolerance(A, B, tol=1e-05):
        return (np.abs(A[:,None] - B) < tol).any(1)
    
    # Time in milliseconds
    def ricker(fp, peak=0.0, x_values=None, y_values=None):
        t = np.arange(-1000.0, 1001.0, 1)        
        factor = (np.pi * fp * t) ** 2
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
    
    def time_array(start, end, dt):
        return np.arange(start, end+dt, dt)
    
    r_values = [
        (40, 100),
        (10, 300),
        (40, 300),
        (30, 500),
        (30, 520),
        (20, 800),
        (30, 800),
        (20, 820),
        (30, 820)
    ]

    dt = 4
    t = time_array(0, 1000.0, dt)

    pos_stack_data = np.zeros(len(t)) 
    pre_stack_data = []
    
    for idx, (f, peak) in enumerate(r_values):   
        pre_stack = np.zeros(len(t))
        pre_stack = ricker(f, peak, t, pre_stack)[1]
        pos_stack_data += pre_stack
        pre_stack_data.append(pre_stack)
    pre_stack_data = np.array(pre_stack_data)    


    OM = ObjectManager(event.GetEventObject())
    
    offsets = []
    for i in range(1, len(pre_stack_data)+1):
        offsets.append(i)
    seismic = OM.new('seismic', pre_stack_data, name='wilson_synth_pre', 
                           unit='ms', domain='time', 
                           sample_rate=dt, datum=0,
                           samples=len(t),
                           stacked=False,
                           traces=int(pre_stack_data.shape[0]),
                           offsets=offsets
    )
    OM.add(seismic) 


    pos_stack_data = pos_stack_data[np.newaxis,:]
    
    seismic = OM.new('seismic', pos_stack_data, name='wilson_synth_pos', 
                           unit='ms', domain='time', 
                           sample_rate=dt, datum=0,
                           samples=len(t),
                           stacked=True,
                           traces=int(pos_stack_data.shape[0]))
    OM.add(seismic) 
        


   
'''

def on_test_partition(self, event):
    well = self.OM.new('well', name='teste_particao') 
    self.OM.add(well)
    data = np.arange(0, 550, 50)
    depth = self.OM.new('depth', data, name='depth', unit='m', curvetype='Depth')
    self.OM.add(depth, well.uid)
    
    #data = np.array([12, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14])
    #booldata, codes = DT.DataTypes.Partition.getfromlog(data)
    partition = self.OM.new('partition', name='particao', curvetype='partition')
    self.OM.add(partition, well.uid)
    
    b1 = np.array([True, True, True, True, False, False, False, False, False, False, False])
    p1 = self.OM.new('part', b1, code=12, color=(255, 0, 0), curvetype='part')
    self.OM.add(p1, partition.uid)

    b2 = np.array([False, False, False, False, True, True, True, True, False, False, False])
    p2 = self.OM.new('part', b2, code=13, color=(0, 255, 0),curvetype='part')
    self.OM.add(p2, partition.uid)

    b3 = np.array([True, True, False, False, False, False, False, False, True, True, True])
    p3 = self.OM.new('part', b3, code=14, color=(0, 0, 255), curvetype='part')
    self.OM.add(p3, partition.uid)
    
   

        
    def on_load_wilson(self, event):
        
        def in1d_with_tolerance(A,B,tol=1e-05):
            return (np.abs(A[:,None] - B) < tol).any(1)
        
        # Time in milliseconds
        def ricker(fp, peak=0.0, x_values=None, y_values=None):
            t = np.arange(-1000.0, 1001.0, 1)        
            factor = (np.pi * fp * t) ** 2
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
        
        def time_array(start, end, dt):
            return np.arange(start, end+dt, dt)
        
        r_values = [
            (40, 100),
            (10, 300),
            (40, 300),
            (30, 500),
            (30, 520),
            (20, 800),
            (30, 800),
            (20, 820),
            (30, 820)
        ]

        dt = 4
        t = time_array(0, 1000.0, dt)

        pos_stack_data = np.zeros(len(t)) 
        pre_stack_data = []
        
        for idx, (f, peak) in enumerate(r_values):   
            pre_stack = np.zeros(len(t))
            pre_stack = ricker(f, peak, t, pre_stack)[1]
            pos_stack_data += pre_stack
            pre_stack_data.append(pre_stack)
        pre_stack_data = np.array(pre_stack_data)    
    


        seismic = self.OM.new('seismic', pre_stack_data, name='wilson_synth_pre', 
                               unit='ms', domain='time', 
                               sample_rate=dt, datum=0,
                               samples=len(t),
                               stacked=False,
                               traces=int(pre_stack_data.shape[0]))
        self.OM.add(seismic) 


        pos_stack_data = pos_stack_data[np.newaxis,:]
        
        seismic = self.OM.new('seismic', pos_stack_data, name='wilson_synth_pos', 
                               unit='ms', domain='time', 
                               sample_rate=dt, datum=0,
                               samples=len(t),
                               stacked=True,
                               traces=int(pos_stack_data.shape[0]))
        self.OM.add(seismic) 
        



    
    def on_load_avo_inv_wells(self, event):    
        
        def lerAscii(filename):
            f = file(filename, 'r')
            d = np.array([float(x) for x in f.readlines()])
            f.close  
            return d
            
        poco_densidade  = str("C:\Users\Adriano\Documents\GitHub\AVO_INVTRACE_NEW\data\poco_0210_densidade.dat")
        poco_vp         = str("C:\Users\Adriano\Documents\GitHub\AVO_INVTRACE_NEW\data\poco_0210_vp.dat")
        poco_vs         = str("C:\Users\Adriano\Documents\GitHub\AVO_INVTRACE_NEW\data\poco_0210_vs.dat")
        
        # Carregando dados ascii (poços)
        p_rho = lerAscii(poco_densidade)
        p_vp  = lerAscii(poco_vp)
        p_vs  = lerAscii(poco_vs)    
            
        p_vp = p_vp * 3.28084    
        p_vs = p_vs * 3.28084
       #print p_rho
        
        well = self.OM.new('well', name='poco_0210')
        self.OM.add(well)
        d = np.arange(2514, 2946, 4)
        depth = self.OM.new('index_curve', d, name='DEPTH', unit='m', curvetype='Depth')
        self.OM.add(depth, well.uid)        

        log_rho = self.OM.new('log', p_rho, name='Rho', index_uid=depth.uid,
                               unit='g/cm3', curvetype='Density'
        )
        self.OM.add(log_rho, well.uid)
        
        log_vp = self.OM.new('log', p_vp, name='Vp', index_uid=depth.uid,
                              unit='ft/sec', curvetype='Velocity'
        )
        self.OM.add(log_vp, well.uid)    
        
        log_vs = self.OM.new('log', p_vs, name='Vs', index_uid=depth.uid,
                              unit='ft/sec', curvetype='Velocity'
        )
        self.OM.add(log_vs, well.uid)         



    def on_wavelet_analysis(self, event):                
        gc = GripyController(event.GetEventObject())
        mw_ctrl = gc.get_main_window()

        dlg = dialog.Dialog(mw_ctrl.view, 
            [
                (dialog.Dialog.seismic_selector, 'Seismic:', 'seismic_uid'),
                (dialog.Dialog.text_ctrl, 'Scalogram name:', 'new_obj_name')
            ], 'Wavelet Analysis - Select Source:'
        )

        if dlg.ShowModal() == wx.ID_OK:
            results = dlg.get_results()
        else:
            return
            
        seismic_uid = results.get('seismic_uid')
        scalogram_name = results.get('new_obj_name')
        
        seis = self.OM.get(seismic_uid)
 
        start = seis.attributes.get('datum')
        step = seis.attributes.get('sample_rate')
        samples = seis.attributes.get('samples')
        stop = start + step * samples
        time = np.arange(start, stop, step)
        data = []
        for j in range(seis.data.shape[0]):
            wa = wavelets.WaveletAnalysis(seis.data[j], time=time, dj=0.125)
            power = wa.wavelet_power   
            data.append(power)     
        data = np.array(data)

        scalogram = self.OM.new('scalogram', data, name=scalogram_name, 
                               unit='ms', domain=seis.attributes.get('domain', 'time'), 
                               sample_rate=step, datum=start,
                               samples=samples, traces=int(data.shape[0]), 
                               scales=int(data.shape[1]), type='Amp Power'
        )
        self.OM.add(scalogram)
        
        





    def on_partitionedit(self, event):
        if not self.OM.list('partition'):
            return
        gc = GripyController(event.GetEventObject())    
        dlg = PartitionEditor.Dialog(gc.get_main_window().view)
        dlg.ShowModal()
        dlg.Destroy()
        self.om_tree.refresh()


    def check_tab(self, event):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        wildcard="Arquivos hdf5 (*.h5)|*.h5"
        fdlg = wx.FileDialog(self.get_main_window_controller().view, 'Escolha o projeto a carregar', 
                             wildcard=wildcard, style=style)
        if fdlg.ShowModal() == wx.ID_OK:
            file_proj = fdlg.GetFilename()
            self.odt_dir_name = fdlg.GetDirectory()
            fdlg.Destroy()
        else:
            fdlg.Destroy()
            return
        dfile = os.path.join(self.odt_dir_name, file_proj)
        os.system("vitables %s" %dfile)
            

'''
        

"""
    @staticmethod
    def on_plot(event):
        gc = GripyController(event.GetEventObject())
        gc._UIM.create('logplot_controller', gc.get_main_window().uid)
        
        '''
        dlg = Dialog(self.get_main_window_controller().view, 
            [
                (Dialog.well_selector, 'Well:', 'well_uid'),
                (Dialog.logplotformat_selector, 'Format: ', 'plt_file_name')
            ], 
            'Plot Selector'
        )
        if dlg.ShowModal() == wx.ID_OK:
            results = dlg.get_results()
            plt = ParametersManager.get().getPLT(results['plt_file_name'])
            if plt is None:
                lpf = None
            else:    
                lpf = logplotformat.LogPlotFormat.create_from_PLTFile(plt)
            _, well_oid = results['well_uid']
            UIManager.get().create_log_plot(well_oid, lpf)
        '''        

        
    @staticmethod
    def on_crossplot(event):
        gc = GripyController(event.GetEventObject())
        gc._UIM.create('crossplot_controller', gc.get_main_window().uid)        
        
"""