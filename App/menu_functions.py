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

from DT.UOM import uom as UOM

import app_utils

from Algo.Spectral.Spectral import STFT, WaveletTransform, Morlet, Paul, DOG, Ricker
from UI.dialog_new import Dialog

from scipy.signal import chirp

from Algo import AVO 
#import copy


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



def teste11(event):
    print 'teste 11'


def teste10(event):
    #
    """
    filename = 'D:\\Sergio_Adriano\\NothViking\\Mobil_AVO_Viking_pstm_16_CIP_prec_stk.sgy'
    name = 'Mobil_AVO_Viking_pstm_16_CIP_prec_stk'
    app_utils.load_segy(event, filename, 
        new_obj_name=name, 
        comparators_list=None,
        iline_byte=9, xline_byte=21, offset_byte=37
    )
    """
    #"""
    filename = 'D:\\Sergio_Adriano\\NothViking\\Mobil_AVO_Viking_pstm_16_stk.sgy'
    name = 'Mobil_AVO_Viking_pstm_16_stk'
    app_utils.load_segy(event, filename, 
        new_obj_name=name, 
        comparators_list=None,
        iline_byte=9, xline_byte=21, offset_byte=37
    )
    #"""

def on_modelling_pp(event):
    #
    print '\non_modelling_pp'    
    #
    def avo_modeling_akirichards_pp(vp, vs, rho, angles): 
        ret_array = np.zeros((len(vp)-1, len(angles)))
        for i in range(len(vp)-1):
            delta_vp = vp[i+1] - vp[i]
            delta_vs = vs[i+1] - vs[i]
            delta_rho = rho[i+1] - rho[i]
            if (delta_vp == 0) and (delta_vs == 0) and (delta_rho == 0):
                continue
            media_vp = (vp[i+1] + vp[i]) / 2.0
            media_vs = (vs[i+1] + vs[i]) / 2.0
            media_rho = (rho[i+1] + rho[i]) / 2.0
            deltas = np.array([delta_vp/media_vp, delta_vs/media_vs, delta_rho/media_rho])
            coeficientes = avoMatrix_Aki_Rich(angles, media_vp, media_vs)
            ret_array[i] = np.dot(coeficientes, deltas)     
        return ret_array


    def avoMatrix_Aki_Rich(angles, media_vp, media_vs):     
        ret_array = np.zeros((len(angles), 3))
        gamma = media_vs/media_vp
        for i, angle in enumerate(angles):
            ret_array[i][0] = 1 / (2 * np.cos(angle) ** 2)
            ret_array[i][1] = -4 * (gamma * np.sin(angle)) ** 2
            ret_array[i][2] = 0.5 * (1 + ret_array[i][1])
            # Old wrong value above found in Fortran code
            #ret_array[i][2] = (-0.5 * ((np.tan(angle))**2)) + (2 * ((gamma * np.sin(angle))**2))
        return ret_array	
    
    
    OM = ObjectManager(event.GetEventObject())
    #
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='P-Wave Modeling')
    #
    try:
        wells = OrderedDict()
        for well in OM.list('well'):
            wells[well.name] = well.uid
        #
        ctn_well = dlg.view.AddCreateContainer('StaticBox', label='Well', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddChoice(ctn_well, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='welluid', options=wells)

        #            
        ctn_vp = dlg.view.AddCreateContainer('StaticBox', label='Compressional wave', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)     
        #
        #logs = OrderedDict()
        #for log in OM.list('log'):
        #    logs[log.get_friendly_name()] = log.uid
        dlg.view.AddChoice(ctn_vp, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='vp')    
        #
        ctn_vs = dlg.view.AddCreateContainer('StaticBox', label='Shear wave', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5) 
        dlg.view.AddChoice(ctn_vs, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='vs')
        #
        ctn_rho = dlg.view.AddCreateContainer('StaticBox', label='Density', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5) 
        dlg.view.AddChoice(ctn_rho, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='rho')
        #
        ctn_rho = dlg.view.AddCreateContainer('StaticBox', label='New object name', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5) 
        dlg.view.AddTextCtrl(ctn_rho, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='new_name', initial='') 
        #
        def on_change_well(name, old_value, new_value, **kwargs):
            print '\non_change_well:', name, old_value, new_value, kwargs
            vps = OrderedDict()
            vss = OrderedDict()
            rhos = OrderedDict()
            OM = ObjectManager(on_change_well)
            logs = OM.list('log', new_value)
            for log in logs:
                if log.datatype == 'Velocity':
                    vps[log.name] = log.uid
                elif log.datatype == 'ShearVel':
                    vss[log.name] = log.uid
                elif log.datatype == 'Density':
                    rhos[log.name] = log.uid    
            choice_vp = dlg.view.get_object('vp')
            choice_vs = dlg.view.get_object('vs')
            choice_rho = dlg.view.get_object('rho')
            choice_vp.set_options(vps)
            choice_vs.set_options(vss)
            choice_rho.set_options(rhos)
            choice_vp.set_value(0, True)
            choice_vs.set_value(0, True)
            choice_rho.set_value(0, True)
        #    
        choice_well = dlg.view.get_object('welluid')
        choice_well.set_trigger(on_change_well)         
        #
        dlg.view.SetSize((270, 430))
        result = dlg.view.ShowModal()
        #
        if result == wx.ID_OK:
            results = dlg.get_results()  
            print results
            
        disableAll = wx.WindowDisabler()
        wait = wx.BusyInfo("Wait...")        
        welluid = results['welluid']
        vp_data = OM.get(results.get('vp')).data
        vs_data = OM.get(results.get('vs')).data
        rho_data = OM.get(results.get('rho')).data
        new_name = results.get('new_name')
        
        angles_rad = np.deg2rad(np.array(range(46)))
        
        reflectivity = avo_modeling_akirichards_pp(vp_data, vs_data, rho_data, angles_rad)
        reflectivity = np.insert(reflectivity, 0, np.nan, axis=0)
        #
        well = OM.get(welluid)
        #
        model = OM.new('model1d', reflectivity, name=new_name)
        #
        
        #
        OM.add(model, welluid)
                
   
    except Exception as e:
        print '\n', e.message, e.args
        pass
    finally:
        del wait
        del disableAll 
        UIM.remove(dlg.uid) 



def teste7(event):
    raise Exception()
    '''
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
    dlg.view.SetSize((270, 500))
    result = dlg.view.ShowModal()
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
            """
            index = seis_mod_ppps_pp.get_index()
            print '\nMM:', index.max, index.min
            print mod_ppps_pp.shape
            """
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
    '''


def teste6(event):
    raise Exception()
    
    """
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
    
    dlg.view.SetSize((270, 460))
    
    result = dlg.view.ShowModal()
 
    
    
    
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
                               datatype=seis.get_index().attributes['curvetype'])
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
        
            '''
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
    
            '''

    dlg.Destroy() 

    """


def teste5(event):
    #
    OM = ObjectManager(event.GetEventObject()) 
    
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Continuous Wavelet Transform') 
    #
    try:
        ctn_input_data = dlg.view.AddCreateContainer('StaticBox', label='Input data', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        #
        accept_tids = ['seismic', 'gather']
        input_data = OrderedDict()
        for tid in accept_tids:
            for obj in OM.list(tid):
                input_data[obj._TID_FRIENDLY_NAME + ': ' + obj.name] = obj.uid
        
        '''
        seismics = OrderedDict()
        for seis in OM.list('seismic'):
            name =  'Seismic: ' + seis.name
            seismics[name] = seis.uid
        for seis in OM.list('gather'):
            name =  'Gather: ' + seis.name
            seismics[name] = seis.uid
        '''
        
        dlg.view.AddChoice(ctn_input_data, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='seismic', options=input_data)     
        #    
        ctn_wavelet = dlg.view.AddCreateContainer('StaticBox', label='Wavelet', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddChoice(ctn_wavelet, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='wavelet', options=WAVELET_TYPES)
        #
        ctn_scale_res = dlg.view.AddCreateContainer('StaticBox', label='Scale resolution', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_scale_res, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='dj', initial='0.125') 
        #
        ctn_mode = dlg.view.AddCreateContainer('StaticBox', label='Mode', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddChoice(ctn_mode, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='mode', options=WAVELET_MODES)
        #
        ctn_name = dlg.view.AddCreateContainer('StaticBox', label='New object name', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_name, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='cwt_name')       
        #
        dlg.view.SetSize((330, 430))
        result = dlg.view.ShowModal()
        if result == wx.ID_OK:
            results = dlg.get_results()  
            print '\nresults:', results, '\n'
            
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
            #    
            obj_uid = results.get('seismic')
            obj = OM.get(obj_uid) 
            mode = results.get('mode')    
            #
            input_indexes = obj.get_index()
            z_axis = input_indexes[0][0]
            #
            #print '\n', z_axis.name, z_axis.uid, z_axis.step, z_axis.datatype
            
            if z_axis.datatype != 'TIME':
                raise Exception('Only TIME datatype is accepted.')
                
            time = UOM.convert(z_axis.data, z_axis.unit, 's')      
            step = UOM.convert(z_axis.step, z_axis.unit, 's') 
            
            print 'Input obj.data.shape:', obj.data.shape
            
            if len(obj.data.shape) == 4:
                print 'Input data shape lenght: 4'
                iaxis, jaxis, kaxis, zaxis = obj.data.shape
                data_out = None
                for i in range(iaxis):
                    for j in range(jaxis):
                        for k in range(kaxis):
                             wt = WaveletTransform(obj.data[i][j][k], dj=dj,
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
                                 data_out[i][j][k] = np.abs(np.flip(wt.wavelet_transform, 0))      
                             elif mode == 1:            
                                 # np.abs(self.wavelet_transform) ** 2
                                 data_out[i][j][k] = np.flip(wt.wavelet_power, 0)         
                             elif mode == 2 or mode ==3:   
                                 data_out[i][j][k] = np.angle(np.flip(wt.wavelet_transform, 0))
                             if mode == 3:   
                                 data_out[i][j][k] = np.unwrap(np.angle(np.flip(wt.wavelet_transform, 0)), axis=0)    

            elif len(obj.data.shape) == 3:
                print 'Input data shape lenght: 3'
                iaxis, jaxis, zaxis = obj.data.shape
                data_out = None
                for i in range(iaxis):
                    for j in range(jaxis):
                         wt = WaveletTransform(obj.data[i][j], dj=dj,
                                               wavelet=func, 
                                               dt=step,
                                               time=time
                         )
                         
                         #print 'wt_shape:', wt.wavelet_transform.shape
                         #print (i, j, k), wt.wavelet_transform.shape, np.flip(wt.fourier_frequencies, 0)#, wt.scales
                         
                         if data_out is None:
                             wt_axis = wt.wavelet_transform.shape[0]
                             new_shape = (iaxis, jaxis, wt_axis, zaxis)
                             print 'New data CWT shape:', new_shape 
                             data_out = np.zeros(new_shape)    
                             freqs =  np.flip(wt.fourier_frequencies, 0)
                             scales = np.flip(wt.scales, 0)
                         if mode == 0:
                             data_out[i][j] = np.abs(np.flip(wt.wavelet_transform, 0))      
                         elif mode == 1:            
                             # np.abs(self.wavelet_transform) ** 2
                             data_out[i][j] = np.flip(wt.wavelet_power, 0)         
                         elif mode == 2 or mode ==3:   
                             data_out[i][j] = np.angle(np.flip(wt.wavelet_transform, 0))
                         if mode == 3:   
                             data_out[i][j] = np.unwrap(np.angle(np.flip(wt.wavelet_transform, 0)), axis=0)    

            else:
                raise Exception()
            #
            
            print '\ndata_out.shape:', data_out.shape
            print np.nanmin(data_out), np.nanmax(data_out)
            
            #
            name = results.get('cwt_name')
            scalogram = OM.new('scalogram', data_out, name=name)
            if not OM.add(scalogram):
                raise Exception('Object was not added. tid={\'scalogram\'}')
            # 
            
            
            state = z_axis._getstate()
            index = OM.create_object_from_state('data_index', **state)
            OM.add(index, scalogram.uid)
            #
            
            index = OM.new('data_index', 1, 'Frequency', 'FREQUENCY', 'Hz', 
                           data=freqs
            ) 
            OM.add(index, scalogram.uid)
            #
            # TODO: Inserir scales na dimensao 1
            # 
            # Inserindo as outras dimensões do dado
            for idx in range(1, len(input_indexes)):
                state = input_indexes[idx][0]._getstate()        
                state['dimension'] = idx+1
                index = OM.index = OM.create_object_from_state('data_index', **state)
                OM.add(index, scalogram.uid)

        del wait
        del disableAll
    except Exception:
        pass
    finally:
        UIM.remove(dlg.uid)   



def on_exit(*args, **kwargs):
    gripy_app = wx.App.Get() 
    event = args[0]
    event.Skip()
    gripy_app.PreExit()
    main_window = gripy_app.GetTopWindow()
    main_window.Destroy()

    

def on_new(*args, **kwargs):
    gripy_app = wx.App.Get() 
    gripy_app.reset_ObjectManager()



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
    cont_well = dlg.AddStaticBoxContainer(label='Well', 
                                          orient=wx.HORIZONTAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )
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
    wells = OrderedDict()
    for well in OM.list('well'):
        wells[well.name] = well.uid
            
    #reference
    dlg.AddStaticText(cont_sup, initial='Type of Support   ')
    dlg.AddChoice  (cont_sup, widget_name='suporte', initial=options)
    dlg.AddTextCtrl(cont_sup, widget_name='point', initial='1500')
    dlg.AddTextCtrl(cont_sup, widget_name='top', initial='1000')
    dlg.AddTextCtrl(cont_sup, widget_name='base', initial='2000')
    dlg.AddChoice(cont_sup, widget_name='fac', initial=partitions)
    dlg.AddChoice(cont_well, widget_name='welluid', initial=wells)
#    c1 = dlg.view.AddCreateContainer('StaticBox', label='Well', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
#    dlg.view.AddChoice(c1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5,  widget_name='welluid', options=wells)
#    #
#    ctn_name = dlg.view.AddCreateContainer('StaticBox', label='Rock name:', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.AddTextCtrl(cont_well, proportion=0, flag=wx.EXPAND|wx.TOP, 
                         border=5, widget_name='rock_name', initial='new_rock'#, 
    )
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
#    wells = OrderedDict()
#    for well in OM.list('well'):
#        wells[well.name] = well.uid
#
#    #    
#    cont_well = dlg.AddCreateContainer('StaticBox', label='Well', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
#    dlg.AddChoice(c1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5,  widget_name='welluid', options=wells)
#    dlg.AddChoice(cont_well, widget_name='fac', initial=partitions)
    result = dlg.ShowModal()
    print 'result0'
    try:
        if result == wx.ID_OK:
            results = dlg.get_results()     
            well_uid = results.get('welluid')   
            rock_name = results.get('rock_name')
            #                   
            rock = OM.new('rock', name=rock_name)
            OM.add(rock, well_uid)  
    except Exception as e:
        print 'ERROR:', e
    finally:
        dlg.Destroy()
#    if result == wx.ID_OK:
#        print 'result1'
#        results = dlg.get_results()  
#        print '\nresults2'
#        #
#        print '\nresult.get', results.get('suporte')
#    dlg.Destroy()
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

                    index = OM.new('data_index', 0, names[i], 
                                   sel_curvetypes[i].upper(), units[i].lower(), 
                                   data=data[i]
                    )
                    #print 'data_index', names[i]
                    OM.add(index, well.uid)
                
                elif sel_datatypes[i] == 'Log':
                    log = OM.new('log', data[i], name=names[i], 
                                unit=units[i], datatype=sel_curvetypes[i]
                                #index_uid=index.uid
                    )
                    OM.add(log, well.uid)

                elif sel_datatypes[i] == 'Partition':
                    try:
                        booldata, codes = DT.DataTypes.Partition.getfromlog(data[i])
                    except TypeError:
                        print 'data[{}]: {}'.format(i, data[i])
                        raise
                    partition = OM.new('partition', name=names[i], 
                                           datatype=sel_curvetypes[i]#,
                                           #index_uid=index.uid
                    )
                    OM.add(partition, well.uid)
                    for j in range(len(codes)):
                        part = OM.new('part', booldata[j], 
                            code=int(codes[j]), datatype=sel_curvetypes[i])
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
    app_utils.load_segy(event, os.path.join(dir_name, file_name), 
                    new_obj_name=name, comparators_list=None, 
              iline_byte=9, xline_byte=21, offset_byte=37
    )
    


def on_import_segy_well_gather(event):
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Import SEG-Y Well Gather') 
    #
    try:
        ctn_file = dlg.view.AddCreateContainer('StaticBox', label='File', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddFilePickerCtrl(ctn_file, proportion=0,
                flag=wx.EXPAND|wx.TOP, border=5, widget_name='filename', 
                wildcard="SEG-Y files (*.sgy)|*.sgy", path='',  
                message='Choose SEG-Y file'
        )
        #
        print 333
        ctn = dlg.view.AddCreateContainer('BoxSizer', orient=wx.HORIZONTAL)
        #
        print 222
        ctn_iline_byte = dlg.view.AddCreateContainer('StaticBox', ctn, label='ILine', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        print 999
        dlg.view.AddTextCtrl(ctn_iline_byte, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='iline_byte', initial='9')
        #
        print 444
        ctn_xline_byte = dlg.view.AddCreateContainer('StaticBox', ctn, label='XLine', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        print 999
        dlg.view.AddTextCtrl(ctn_xline_byte, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='xline_byte', initial='21')        
        #
        print 555
        ctn_offset_byte = dlg.view.AddCreateContainer('StaticBox', ctn, label='Offset', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_offset_byte, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='offset_byte', initial='37')            
        #
        print 111
        ctn_where = dlg.view.AddCreateContainer('StaticBox', label='Where', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        #
        ctn_where_iline = dlg.view.AddCreateContainer('StaticBox', ctn_where, label='ILine', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_where_iline, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='iline_number')
        #
        print 222
        ctn_where_xline = dlg.view.AddCreateContainer('StaticBox', ctn_where, label='XLine', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_where_xline, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='xline_number')
        #
        print 333
        ctn_wells = dlg.view.AddCreateContainer('StaticBox', label='Well', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        wells = OrderedDict()
        OM = ObjectManager(event.GetEventObject())
        for well in OM.list('well'):
            wells[well.name] = well.uid
        dlg.view.AddChoice(ctn_wells, proportion=0, flag=wx.EXPAND|wx.TOP, border=5,  widget_name='welluid', options=wells)     
        #
        print 444
        ctn_gather = dlg.view.AddCreateContainer('StaticBox', label='Well gather name', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        print 555
        dlg.view.AddTextCtrl(ctn_gather, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='wellgather_name')
        #
        print 666
        dlg.view.SetSize((460, 500))
        print 777
        result = dlg.view.ShowModal()
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
            app_utils.load_segy(event, filename, 
                new_obj_name=wellgather_name, 
                comparators_list=comparators, 
                iline_byte=iline_byte, xline_byte=xline_byte, 
                offset_byte=offset_byte, tid='gather', parentuid=welluid
            )
            
            """
            filename = 'D:\\Sergio_Adriano\\NothViking\\Mobil_AVO_Viking_pstm_16_CIP_stk.sgy'
            name = 'Mobil_AVO_Viking_pstm_16_CIP_stk'
            app_utils.load_segy(event, filename, 
                new_obj_name=name, 
                comparators_list=[(21, 4, '==', 808), (21, 4, '==', 1572)], 
                iline_byte=9, xline_byte=21, offset_byte=37
            )
            """
    except Exception as e:
        print e
    finally:
        UIM.remove(dlg.uid)  

 
   
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
    if esdlg.view.ShowModal() == wx.ID_OK:
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
    dlg.view.ShowModal()
    dlg.Destroy()
    
    _UIM = UIManager()
    tree_ctrl = _UIM.list('tree_controller')[0]
    tree_ctrl.refresh() 
 
    
def on_createrock(event):
    OM = ObjectManager(event.GetEventObject()) 
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Create Rock')
    wells = OrderedDict()
    for well in OM.list('well'):
        wells[well.name] = well.uid

    #    
    c1 = dlg.view.AddCreateContainer('StaticBox', label='Well', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddChoice(c1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5,  widget_name='welluid', options=wells)
    #
    ctn_name = dlg.view.AddCreateContainer('StaticBox', label='Rock name:', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_name, proportion=0, flag=wx.EXPAND|wx.TOP, 
                         border=5, widget_name='rock_name', initial='new_rock'#, 
    )

    #
    dlg.view.SetSize((350, 530))
    result = dlg.view.ShowModal()
    try:
        if result == wx.ID_OK:
            results = dlg.get_results()     
            well_uid = results.get('welluid')   
            rock_name = results.get('rock_name')
            #                   
            rock = OM.new('rock', name=rock_name)
            OM.add(rock, well_uid)  
    except Exception as e:
        print 'ERROR:', e
    finally:
        UIM.remove(dlg.uid)        
        
    
def on_createwell(event):
    OM = ObjectManager(event.GetEventObject()) 
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Create Well')
    ctn_name = dlg.view.AddCreateContainer('StaticBox', label='Name', 
            orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5
    )
    #
    def on_change_well_name(name, old_value, new_value, **kwargs):
        if new_value == '':
            dlg.view.enable_button(wx.ID_OK, False)
        else:
            dlg.view.enable_button(wx.ID_OK, True)
    #
    dlg.view.AddTextCtrl(ctn_name, proportion=0, flag=wx.EXPAND|wx.TOP, 
                         border=5, widget_name='well_name', initial=''
    )
    textctrl_well_name = dlg.view.get_object('well_name')
    textctrl_well_name.set_trigger(on_change_well_name)
    #
    #container = dlg.view.AddStaticBoxContainer(label='Synthetic type', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    #dlg.view.AddChoice(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='synth_type', initial=synth_type)  
    ctn_index = dlg.view.AddCreateContainer('StaticBox', label='Index', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    ctn_index_base = dlg.view.AddCreateContainer('BoxSizer', ctn_index, orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    #
    datatypes = OrderedDict()
    datatypes['Time'] = 'TIME'
    datatypes['MD'] = 'MD'
    #
    def on_change_datatype(name, old_value, new_value, **kwargs):
        textctrl_name = dlg.view.get_object('index_name')
        statictext_start = dlg.view.get_object('static_start')
        statictext_end = dlg.view.get_object('static_end')
        statictext_sampling = dlg.view.get_object('static_sampling')
        if new_value == "TIME":
            textctrl_name.set_value('Time')
            statictext_start.set_value('Start (ms):')
            statictext_end.set_value('End (ms):')
            statictext_sampling.set_value('Sampling (ms):')
        if new_value == "MD":
            textctrl_name.set_value('Depth')  
            statictext_start.set_value('Start (m):')
            statictext_end.set_value('End (m):')
            statictext_sampling.set_value('Sampling (m):')
        #
    #    
    c1 = dlg.view.AddCreateContainer('BoxSizer', ctn_index_base, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c1, label='Type:', proportion=1, flag=wx.ALIGN_RIGHT)
    dlg.view.AddChoice(c1, proportion=1, flag=wx.ALIGN_LEFT, widget_name='datatype', options=datatypes)
    choice_datatype = dlg.view.get_object('datatype')
    choice_datatype.set_trigger(on_change_datatype)
    #
    c2 = dlg.view.AddCreateContainer('BoxSizer', ctn_index_base, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c2, label='Name:', proportion=1, flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c2, proportion=1, flag=wx.ALIGN_LEFT, widget_name='index_name', initial='') 
    #
    c3 = dlg.view.AddCreateContainer('BoxSizer', ctn_index_base, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c3, label='', widget_name='static_start', proportion=1, flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c3, proportion=1, flag=wx.ALIGN_LEFT, widget_name='start', initial='0.0')     
    #
    c4 = dlg.view.AddCreateContainer('BoxSizer', ctn_index_base, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c4, label='', widget_name='static_end', proportion=1, flag=wx.ALIGN_RIGHT) 
    dlg.view.AddTextCtrl(c4, proportion=1, flag=wx.ALIGN_LEFT, widget_name='end', initial='5000.0')  
    #
    c5 = dlg.view.AddCreateContainer('BoxSizer', ctn_index_base, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c5, label='', widget_name='static_sampling', proportion=1, flag=wx.ALIGN_RIGHT)    
    dlg.view.AddTextCtrl(c5, proportion=1, flag=wx.ALIGN_LEFT, widget_name='ts', initial='4.0')  
    #
    #print ctn_index_base
    #dlg.view.DetachContainer(ctn_index)
    #dlg.view.AddContainer(ctn_index, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    #
    choice_datatype.set_value(0, True)
    dlg.view.enable_button(wx.ID_OK, False)
    #
    dlg.view.SetSize((280, 360))
    result = dlg.view.ShowModal()
    
    try:
        disableAll = wx.WindowDisabler()
        wait = wx.BusyInfo("Creating new well. Wait...")
        if result == wx.ID_OK:
            results = dlg.get_results() 
            well_name = results['well_name']
            datatype = results['datatype']
            if datatype == 'TIME':
                unit = 'ms'
            elif datatype == 'MD':    
                unit = 'm'
            index_name = results['index_name']
            start = float(results['start'])
            end = float(results['end'])
            ts = float(results['ts'])
            OM = ObjectManager(event.GetEventObject())
            well = OM.new('well', name=well_name) 
            OM.add(well)
            index = OM.new('data_index', 0, index_name, datatype, unit, 
                   start=start, samples=(end-start)/ts, step=ts
            )
            OM.add(index, well.uid)
    except:
        pass
    finally:
        del wait
        del disableAll
        UIM.remove(dlg.uid)   
    
    
def on_create_synthetic(event):
    OM = ObjectManager(event.GetEventObject()) 
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Create Synthetic Log')
    wells = OrderedDict()
    for well in OM.list('well'):
        wells[well.name] = well.uid
    #
    def on_change_well(name, old_value, new_value, **kwargs):
        choice = dlg.view.get_object('indexuid')
        opt = OrderedDict()
        for obj in OM.list('data_index', new_value):
            opt[obj.name] = obj.uid
        choice.set_options(opt)
        choice.set_value(0, True)
    #    
    c1 = dlg.view.AddCreateContainer('StaticBox', label='Well', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddChoice(c1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='welluid', options=wells)
    choice_well = dlg.view.get_object('welluid')
    choice_well.set_trigger(on_change_well) 
    #
    c2 = dlg.view.AddCreateContainer('StaticBox', label='Index', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddChoice(c2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='indexuid')  
    #
    choice_well.set_value(0, True)
    #
    synth_type = OrderedDict()
    synth_type['Sine wave'] = 0
    synth_type['Cosine wave'] = 1
    synth_type['Linear chirp'] = 2
    synth_type['Quadratic chirp'] = 3
    synth_type['Logaritmic chirp'] = 4
    synth_type['Hiperbolic chirp'] = 5
    #
    ctn_synth_type = dlg.view.AddCreateContainer('StaticBox', label='Synthetic type', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    #
    #choice = dlg.view.get_object('synth_type')
    #choice.set_value(0)
    #
    ctn_parms = dlg.view.AddCreateContainer('StaticBox', label='Parameters', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    flags = {'proportion': 0, 'flag': wx.EXPAND|wx.TOP, 'border': 5}
    #
    #
    ctn_sin_cos = dlg.view.CreateContainer('BoxSizer', ctn_parms, orient=wx.VERTICAL)
    #
    c4 = dlg.view.AddCreateContainer('BoxSizer', ctn_sin_cos, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c4, label='Frequency (Hz):', proportion=1, flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c4, proportion=1, flag=wx.ALIGN_LEFT, widget_name='sin_cos_freq', initial='1.0')  
    #
    c5 = dlg.view.AddCreateContainer('BoxSizer', ctn_sin_cos, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c5, label='Amplitude:', proportion=1, flag=wx.ALIGN_RIGHT)   
    dlg.view.AddTextCtrl(c5, proportion=1, flag=wx.ALIGN_LEFT, widget_name='sin_cos_amp', initial='1.0')   
    #
    ctn_chirp = dlg.view.CreateContainer('BoxSizer', ctn_parms, orient=wx.VERTICAL)
    #
    ctn_chirp_0 = dlg.view.AddCreateContainer('BoxSizer', ctn_chirp, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(ctn_chirp_0, label='Start:', proportion=1, flag=wx.ALIGN_RIGHT)  
    dlg.view.AddTextCtrl(ctn_chirp_0, proportion=1, flag=wx.ALIGN_LEFT, widget_name='chirp_start')   
    #
    ctn_chirp_1 = dlg.view.AddCreateContainer('BoxSizer', ctn_chirp, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(ctn_chirp_1, label='Initial Frequency (Hz):', proportion=1, flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(ctn_chirp_1, proportion=1, flag=wx.ALIGN_LEFT, widget_name='chirp_f0', initial='1.0')  
    #
    ctn_chirp_3 = dlg.view.AddCreateContainer('BoxSizer', ctn_chirp, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(ctn_chirp_3, label='End:', proportion=1, flag=wx.ALIGN_RIGHT)  
    dlg.view.AddTextCtrl(ctn_chirp_3, proportion=1, flag=wx.ALIGN_LEFT, widget_name='chirp_end')     
    #
    ctn_chirp_2 = dlg.view.AddCreateContainer('BoxSizer', ctn_chirp, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(ctn_chirp_2, label='End Frequency (Hz):', proportion=1, flag=wx.ALIGN_RIGHT)   
    dlg.view.AddTextCtrl(ctn_chirp_2, proportion=1, flag=wx.ALIGN_LEFT, widget_name='chirp_f1', initial='10.0')   
    #
    ctn_chirp.Show(False)    
    #
    def on_change_synth_type(name, old_value, new_value, **kwargs):
        #print '\nchanged_synth_type:', name, old_value, new_value, kwargs
        if old_value is None:
            if new_value in [0, 1]:
                dlg.view.AddContainer(ctn_sin_cos, ctn_parms, **flags)
            else:
                dlg.view.AddContainer(ctn_chirp, ctn_parms, **flags)  
        elif new_value in [0, 1] and old_value in [2, 3, 4, 5]:
            dlg.view.DetachContainer(ctn_chirp)
            dlg.view.AddContainer(ctn_sin_cos, ctn_parms, **flags)
        if new_value in [2, 3, 4, 5] and old_value in [0, 1]:
            dlg.view.DetachContainer(ctn_sin_cos)
            dlg.view.AddContainer(ctn_chirp, ctn_parms, **flags)    
        dlg.view.Layout()    
    #
    dlg.view.AddChoice(ctn_synth_type, proportion=0, flag=wx.EXPAND|wx.TOP, 
                       border=5, widget_name='synth_type', options=synth_type
    )
    
    choice_synth_type = dlg.view.get_object('synth_type')    
    choice_synth_type.set_trigger(on_change_synth_type)
    choice_synth_type.set_value(0, True)
    #print 'ctn_parms:', ctn_parms
    #print '\n\n'
    

    ctn_name = dlg.view.AddCreateContainer('StaticBox', label='Synthetic name:', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_name, proportion=0, flag=wx.EXPAND|wx.TOP, 
                         border=5, widget_name='synth_name', initial='new_synth'
    )
    
    #
    def on_change_synth_name(name, old_value, new_value, **kwargs):
        #print 'on_change_synth_name:', name, old_value, new_value, kwargs
        if new_value == '':
            dlg.view.enable_button(wx.ID_OK, False)
        else:
            dlg.view.enable_button(wx.ID_OK, True)
    #
    #
    choice_synth_name = dlg.view.get_object('synth_name')  
    choice_synth_name.set_trigger(on_change_synth_name)
    #
    
    #
    dlg.view.SetSize((350, 530))
    result = dlg.view.ShowModal()
    try:
        disableAll = wx.WindowDisabler()
        wait = wx.BusyInfo("Creating synthetic. Wait...")
        if result == wx.ID_OK:
            results = dlg.get_results()  
            print results
            synth_type = results['synth_type']
            welluid = results['welluid']
            indexuid = results['indexuid'] 
            synth_name = results['synth_name']
            index = OM.get(indexuid)
            #
            if synth_type in [0, 1]:
                sin_cos_freq = float(results['sin_cos_freq'])
                sin_cos_amp = float(results['sin_cos_amp'])
                if synth_type == 0:
                    data = sin_cos_amp * np.sin(index.data/1000 * 2 * np.pi * sin_cos_freq) 
                elif synth_type == 1:
                    data = sin_cos_amp * np.cos(index.data/1000 * 2 * np.pi * sin_cos_freq)  
            else:        
                chirp_f0 = float(results['chirp_f0'])
                chirp_f1 = float(results['chirp_f1'])
                chirp_start = float(results['chirp_start'])
                chirp_end = float(results['chirp_end'])
                if synth_type == 2:
                    #x = chirp(time, f0=0, f1=100, t1=time[-1], method='linear')
                    data = chirp(index.data, chirp_f0, chirp_end, chirp_f1, method='linear')#, phi=0, vertex_zero=True)
                elif synth_type == 3:
                    data = chirp(index.data, chirp_f0, chirp_end, chirp_f1, method='quadratic')#, phi=0, vertex_zero=True)    
                elif synth_type == 4:
                    data = chirp(index.data, chirp_f0, chirp_end, chirp_f1, method='logarithmic')#, phi=0, vertex_zero=True)
                elif synth_type == 5:
                    data = chirp(index.data, chirp_f0, chirp_end, chirp_f1, method='hyperbolic')#, phi=0, vertex_zero=True)                   
            #                   
            log = OM.new('log', data, indexes=[index.uid], name=synth_name, 
                         unit='amplitude', datatype=''
            )
            OM.add(log, welluid)  
    except Exception as e:
        print 'ERROR:', e
    finally:
        del wait
        del disableAll
        UIM.remove(dlg.uid)
    

    
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
    depth = self.OM.new('depth', data, name='depth', unit='m', datatype='Depth')
    self.OM.add(depth, well.uid)
    
    #data = np.array([12, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14])
    #booldata, codes = DT.DataTypes.Partition.getfromlog(data)
    partition = self.OM.new('partition', name='particao', datatype='partition')
    self.OM.add(partition, well.uid)
    
    b1 = np.array([True, True, True, True, False, False, False, False, False, False, False])
    p1 = self.OM.new('part', b1, code=12, color=(255, 0, 0), datatype='part')
    self.OM.add(p1, partition.uid)

    b2 = np.array([False, False, False, False, True, True, True, True, False, False, False])
    p2 = self.OM.new('part', b2, code=13, color=(0, 255, 0),datatype='part')
    self.OM.add(p2, partition.uid)

    b3 = np.array([True, True, False, False, False, False, False, False, True, True, True])
    p3 = self.OM.new('part', b3, code=14, color=(0, 0, 255), datatype='part')
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
        depth = self.OM.new('index_curve', d, name='DEPTH', unit='m', datatype='Depth')
        self.OM.add(depth, well.uid)        

        log_rho = self.OM.new('log', p_rho, name='Rho', index_uid=depth.uid,
                               unit='g/cm3', datatype='Density'
        )
        self.OM.add(log_rho, well.uid)
        
        log_vp = self.OM.new('log', p_vp, name='Vp', index_uid=depth.uid,
                              unit='ft/sec', datatype='Velocity'
        )
        self.OM.add(log_vp, well.uid)    
        
        log_vs = self.OM.new('log', p_vs, name='Vs', index_uid=depth.uid,
                              unit='ft/sec', datatype='Velocity'
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

        if dlg.view.ShowModal() == wx.ID_OK:
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
        dlg.view.ShowModal()
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
        if dlg.view.ShowModal() == wx.ID_OK:
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