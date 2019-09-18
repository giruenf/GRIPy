import os
from collections import OrderedDict

import numpy as np
from scipy.signal import chirp
import wx

from app import app_utils
from fileio import las
from fileio import odt
from fileio import segy

from algo.spectral.Spectral import WaveletTransform, MorletWavelet, \
    PaulWavelet, DOGWavelet, RickerWavelet
from algo.spectral.Hilbert import HilbertTransform												  

from algo.modeling.reflectivity import Reflectivity
from classes.om import ObjectManager
from basic.parms import ParametersManager

from fileio.lis import LISFile
from fileio.dlis import DLISFile



from classes.ui import UIManager
from classes.ui import interface

from classes.ui import ImportSelector
from classes.ui import ExportSelector
from classes.ui import ODTEditor
from classes.ui import RockTableEditor

from app.app_utils import GripyIcon


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




def on_create_well(*args):
    OM = ObjectManager() 
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
    ctn_index = dlg.view.AddCreateContainer('StaticBox', label='Index', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    ctn_index_base = dlg.view.AddCreateContainer('BoxSizer', ctn_index, orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    #
    datatypes_ = OrderedDict()
    datatypes_['MD'] = 'MD'
    datatypes_['Time'] = 'TIME'
    
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
        elif new_value == "MD":
            textctrl_name.set_value('Depth')  
            statictext_start.set_value('Start (m):')
            statictext_end.set_value('End (m):')
            statictext_sampling.set_value('Sampling (m):')
        #
    #    
    c1 = dlg.view.AddCreateContainer('BoxSizer', ctn_index_base, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c1, label='Type:', proportion=1, flag=wx.ALIGN_RIGHT)
    dlg.view.AddChoice(c1, proportion=1, flag=wx.ALIGN_LEFT, widget_name='datatype', options=datatypes_)
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
    choice_datatype.set_value(0, True)
    dlg.view.enable_button(wx.ID_OK, False)
    #
    dlg.view.SetSize((280, 360))
    result = dlg.view.ShowModal()
    #
    disableAll = wx.WindowDisabler()
    wait = wx.BusyInfo("Creating new well. Wait...")
    #
    try:
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
            samples = ((end-start)/ts)+1
            #
            try:
                well = OM.new('well', name=well_name) 
                if not OM.add(well):
                    raise Exception('Well was not created.')
            except:
                try:
                    OM.remove(well.uid)
                except:
                    pass
                well = None
                raise
            #
            curve_set = well.create_new_curve_set()
            #
            try:
                index = OM.new('data_index', name=index_name, datatype=datatype, 
                               unit=unit, start=start, samples=samples, step=ts
                )            
                if not OM.add(index, curve_set.uid):
                    raise Exception('DataIndex was not created.')  
            except:
                try:
                    OM.remove(well.uid)
                except:
                    pass
                well = None
                raise
            #
    except:
        pass
    finally:                
        del wait
        del disableAll
    UIM.remove(dlg.uid)   
    return well



def no_well_found_dialog(*args, **kwargs):
    msg = 'This project has not a well. Create one?'
    ret_val = wx.MessageBox(msg, 'Warning', wx.ICON_EXCLAMATION | wx.YES_NO)    
    if ret_val == wx.YES:
        try:
            well = on_create_well()
            return well
        except:
            pass
    return None


def get_wells_dict(*args, **kwargs):
    """Used to select a well to be displayed in ComboBox widget like.
    If no well is found, user will be asked to create one.
    
    Returns a OrderedDict ``wells_od[well.name] = well.uid```or None if the 
    user did not create a well.
    """
    wells_od = OrderedDict()
    OM = ObjectManager() 
    wells = OM.list('well')
    if not wells: 
        well = no_well_found_dialog()
        if well:
            wells = [well]
        else:
            msg = 'There is no Well in this project.'
            wx.MessageBox(msg, 'ERROR', wx.ICON_ERROR|wx.OK_DEFAULT)  
            return None
    for well in wells:
        wells_od[well.name] = well.uid
    return wells_od    



def calc_well_time_from_depth(event):
    wells = get_wells_dict()
    if wells is None:
        return
    #    
    UIM = UIManager()    
    try:
        dlg = UIM.create('dialog_controller', title='Calc Well Time from Depth curve')
        ctn_well = dlg.view.AddCreateContainer('StaticBox', label='Well', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddChoice(ctn_well, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='welluid', options=wells)
        #
        dlg.view.SetSize((270, 250))
        result = dlg.view.ShowModal()
        #
        if result == wx.ID_OK:
            results = dlg.get_results()  
            #print results
            welluid = results['welluid']
            app_utils.calc_well_time_from_depth(event, welluid)
        #
    except Exception as e:
        print ('\n', str(e))
        pass
    finally:
        UIM.remove(dlg.uid) 

    
    



def on_new_wellplot(*args):
    wells = get_wells_dict()
    if wells is None:
        return
    #         
    UIM = UIManager()
    try:
        dlg = UIM.create('dialog_controller', title='New well plot')
        ctn_well = dlg.view.AddCreateContainer('StaticBox', label='Well', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddChoice(ctn_well, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='welluid', options=wells)
        ctn_zaxis = dlg.view.AddCreateContainer('StaticBox', label='Z-axis', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddChoice(ctn_zaxis, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='zaxis_type')
        #choice_well = dlg.view.get_object('welluid')
        #choice_well.set_trigger(on_change_well) 
        #
        def on_change_well(name, old_value, new_value, **kwargs):				
            OM = ObjectManager()
            well = OM.get(new_value)
            #
            z_axis = well.get_z_axis_datatypes(inverted=True)
            #
            choice_zaxis_type = dlg.view.get_object('zaxis_type')       
            choice_zaxis_type.set_options(z_axis)
            choice_zaxis_type.set_value(0, True)
        #
        choice_well = dlg.view.get_object('welluid')
        choice_well.set_trigger(on_change_well)
        choice_well.set_value(0, True)
        #
        dlg.view.SetSize((270, 250))
        result = dlg.view.ShowModal()
        #
        if result == wx.ID_OK:
            results = dlg.get_results()  
            #
            welluid = results['welluid']
            zaxis_type = results['zaxis_type']
            #
            mwc = interface.get_main_window_controller()
            UIM.create('wellplot_controller', mwc.uid, 
                       obj_uid=welluid, index_type=zaxis_type
            )
            #
        #
    except Exception as e:
        print ('\nERROR on_new_wellplot:', str(e))
        raise
    finally:
        UIM.remove(dlg.uid) 



class ReflectivityModel():
    def __init__(self, event):
        self.OM = ObjectManager() 
        
        self.flagRB = 1        
        
        self.modtype = OrderedDict()    
        self.modtype['PP Seismogram'] = 0
        self.modtype['PS Seismogram'] = 1
        
        self.modresponse = OrderedDict()
        self.modresponse['Complete Response'] = 1   
        self.modresponse['Primaries and Internal Multiples'] = 2
        self.modresponse['Only Primaries Reflections'] = 3
        
        self.wellOptions = OrderedDict()
    
        for well in self.OM.list('well'):
            self.wellOptions[well.name] = well.uid   
           
        self.outtype = OrderedDict() 
        self.outtype['T-X Seismogram'] = 1
        self.outtype['T-X NMO-Corrected Seismogram'] = 2
        self.outtype['Tau-P Seismogram'] = 3
        self.outtype['Tau-P NMO-Corrected Seismogram'] = 4
        self.outtype['Angle Gather'] = 5
    
        self.dlg = wx.Dialog(None, title='Reflectivity Modeling')
        ico = GripyIcon('logo-transp.ico', wx.BITMAP_TYPE_ICO)
        self.dlg.SetIcon(ico)
        
        
        modStatLin = wx.StaticText(self.dlg, - 1, "Modeling Type:")
        modStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)) 
        self.modChoiceBox = wx.Choice(self.dlg, -1, choices=self.modtype.keys())
        
        respStatLin = wx.StaticText(self.dlg, - 1, "Response Type:")
        respStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.respChoiceBox = wx.Choice(self.dlg, -1, choices=self.modresponse.keys())
        
        logStatLin = wx.StaticText(self.dlg, -1, "Input Logs from Well:")    
        logStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
    
        self.logOptions = OrderedDict()
             
        self.wellChoiceBox = wx.Choice(self.dlg, -1, choices=self.wellOptions.keys())    
        self.wellChoiceBox.Bind(wx.EVT_CHOICE, self.on_well_choice) 
    
        outStatLin = wx.StaticText(self.dlg, -1, "Output Type")    
        outStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.outChoiceBox = wx.Choice(self.dlg, -1, choices=self.outtype.keys())
        
        objStatLin= wx.StaticText(self.dlg, -1, "Output Name")
        objStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.objTxtCtrl = wx.TextCtrl(self.dlg, -1, "NEW_NAME")        
        
        vpStatLin = wx.StaticText(self.dlg, -1, "P-Wave Velocity")
        self.vpChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
    
        vsStatLin = wx.StaticText(self.dlg, -1, "S-Wave Velocity")
        self.vsChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
    
        rhoStatLin = wx.StaticText(self.dlg, -1, "Density")
        self.rhoChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
        
        qvalueStatLin = wx.StaticText(self.dlg, -1, "Use Q values from logs?")       
        qvalueStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.yesQvalueRB = wx.RadioButton(self.dlg, -1, 'Yes')        
        self.noQvalueRB = wx.RadioButton(self.dlg, -1, 'No')
        
        self.dlg.Bind(wx.EVT_RADIOBUTTON, self.on_yes_rb, id=self.yesQvalueRB.GetId())
        self.dlg.Bind(wx.EVT_RADIOBUTTON, self.on_no_rb, id=self.noQvalueRB.GetId())        
            
        parStatLin = wx.StaticText(self.dlg, -1, "Parameters List", )    
        parStatLin.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
    
        nsampStatLin = wx.StaticText(self.dlg, -1, "Number of Samples:")
        self.nsampTxtCtrl = wx.TextCtrl(self.dlg, -1, "256")
    
        dtStatLin = wx.StaticText(self.dlg, -1, "Sample Rate:")
        self.dtTxtCtrl = wx.TextCtrl(self.dlg, -1, "0.004")
    
        fwavStatLin = wx.StaticText(self.dlg, -1, "Wavelet Peak Frequency (Hz):")
        self.fwavTxtCtrl = wx.TextCtrl(self.dlg, -1, "30.0")
    
        ntrcsStatLin = wx.StaticText(self.dlg, -1, "Number of Traces:")
        self.ntrcsTxtCtrl = wx.TextCtrl(self.dlg, -1, "50")
    
        trc1StatLin = wx.StaticText(self.dlg, -1, "Trace 1 Cordinate:")
        self.trc1TxtCtrl = wx.TextCtrl(self.dlg, -1, "10.0")
    
        latdtStatLin = wx.StaticText(self.dlg, -1, "Lateral Cordenate Rate:")
        self.latdtTxtCtrl = wx.TextCtrl(self.dlg, -1, "12.5")
    
        cam1velStatLin = wx.StaticText(self.dlg, -1, "First Layer Velocity (m/s):")
        self.cam1velTxtCtrl = wx.TextCtrl(self.dlg, -1, "1500")
    
        cam1thickStatLin = wx.StaticText(self.dlg, -1, "First Layer Thickness (m):")
        self.cam1thickTxtCtrl = wx.TextCtrl(self.dlg, -1, "0.0")
    
        nsupStatLin = wx.StaticText(self.dlg, -1, "Number of Sup Layers:")
        self.nsupTxtCtrl = wx.TextCtrl(self.dlg, -1, "40")
    
        zsupStatLin = wx.StaticText(self.dlg, -1, "Thickness of Sup Layers:")
        self.zsupTxtCtrl = wx.TextCtrl(self.dlg, -1, "20.0")
    
        firstLayerStatLin = wx.StaticText(self.dlg, -1, "Depth of First Layer to be Modeled:")
        self.firstLayerTxtCtrl = wx.TextCtrl(self.dlg, -1, "100.00")

        lastLayerStatLin = wx.StaticText(self.dlg, -1, "Depth of Last Layer to be Modeled:")
        self.lastLayerTxtCtrl = wx.TextCtrl(self.dlg, -1, "270")

        pnumStatLin = wx.StaticText(self.dlg, -1, "Number of Ray Parameters:")
        self.pnumTxtCtrl = wx.TextCtrl(self.dlg, -1, "1000")

        angmaxStatLin = wx.StaticText(self.dlg, -1, "Maximum Angle of Incidence:")
        self.angmaxTxtCtrl = wx.TextCtrl(self.dlg, -1, "75.0")  
        
        vpSupStatLin = wx.StaticText(self.dlg, -1, "Sup Layers P velocity:")
        self.vpSupTxtCtrl = wx.TextCtrl(self.dlg, -1, "3100.00")
        
        vsSupStatLin = wx.StaticText(self.dlg, -1, "Sup Layers S velocity:")
        self.vsSupTxtCtrl = wx.TextCtrl(self.dlg, -1, "1640.00")
        
        wellSizer = wx.FlexGridSizer (cols=2, hgap=3, vgap=3)    
        wellSizer.Add(logStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        wellSizer.Add(self.wellChoiceBox, 0, wx.EXPAND|wx.ALL, 5 )
    
        logSizer = wx.FlexGridSizer(cols=2, hgap=3, vgap=3)
        logSizer.AddGrowableCol(1)
        logSizer.Add(vpStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        logSizer.Add(self.vpChoiceBox, 0, wx.EXPAND|wx.ALL, 5 )
        logSizer.Add(vsStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        logSizer.Add(self.vsChoiceBox, 0, wx.EXPAND|wx.ALL, 5 )
        logSizer.Add(rhoStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        logSizer.Add(self.rhoChoiceBox, 0, wx.EXPAND|wx.ALL, 5 )
        
        rbSizer = wx.FlexGridSizer(cols = 3, hgap=3, vgap=3)
        rbSizer.Add(qvalueStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        rbSizer.Add(self.yesQvalueRB, 0)
        rbSizer.Add(self.noQvalueRB,0)        
        
        parSizer = wx.FlexGridSizer(cols = 4, hgap=5, vgap=5)        
        parSizer.Add(nsampStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.nsampTxtCtrl, 0,)        
        parSizer.Add(cam1velStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.cam1velTxtCtrl, 0,)        
        parSizer.Add(dtStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.dtTxtCtrl, 0,)        
        parSizer.Add(cam1thickStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.cam1thickTxtCtrl, 0,)        
        parSizer.Add(ntrcsStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.ntrcsTxtCtrl, 0,)        
        parSizer.Add(vpSupStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.vpSupTxtCtrl, 0,)        
        parSizer.Add(trc1StatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.trc1TxtCtrl, 0,)        
        parSizer.Add(vsSupStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.vsSupTxtCtrl, 0,)        
        parSizer.Add(latdtStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.latdtTxtCtrl, 0,)        
        parSizer.Add(nsupStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.nsupTxtCtrl, 0,)        
        parSizer.Add(fwavStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.fwavTxtCtrl, 0,)        
        parSizer.Add(zsupStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.zsupTxtCtrl, 0,)        
        parSizer.Add(firstLayerStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.firstLayerTxtCtrl, 0,)        
        parSizer.Add(angmaxStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.angmaxTxtCtrl, 0,)        
        parSizer.Add(lastLayerStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.lastLayerTxtCtrl, 0,)            
        parSizer.Add(pnumStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.pnumTxtCtrl, 0,)        
        
        outSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)    
        outSizer.AddGrowableCol(1)
        outSizer.Add(outStatLin,0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        outSizer.Add(self.outChoiceBox,0, wx.EXPAND|wx.ALL, 5 )
        outSizer.Add(objStatLin,0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)        
        outSizer.Add(self.objTxtCtrl,0, wx.EXPAND|wx.ALL, 5 )
        
        self.dlg.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)     
        btnSizer = self.dlg.CreateButtonSizer(wx.OK|wx.CANCEL)                              
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(modStatLin, 0, wx.ALL, 5)
        self.mainSizer.Add(self.modChoiceBox, 0, wx.EXPAND|wx.ALL, 5)
        self.mainSizer.Add(respStatLin, 0, wx.ALL, 5)
        self.mainSizer.Add(self.respChoiceBox, 0, wx.EXPAND|wx.ALL, 5)
        self.mainSizer.Add(wx.StaticLine(self.dlg), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        self.mainSizer.Add(wellSizer, 0, wx.ALL, 5) 
        self.mainSizer.Add(logSizer, 0, wx.EXPAND|wx.ALL, 10 )
        self.mainSizer.Add(rbSizer, 0, wx.ALL, 5 )
        self.mainSizer.Add(wx.StaticLine(self.dlg), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        self.mainSizer.Add(parStatLin, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5) 
        self.mainSizer.Add(parSizer, 0, wx.EXPAND|wx.ALL, 10)
        self.mainSizer.Add(wx.StaticLine(self.dlg), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        self.mainSizer.Add(outSizer, 0, wx.EXPAND|wx.ALL, 10)
        self.mainSizer.Add(btnSizer, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
               
        self.dlg.SetSizer(self.mainSizer) 
        self.dlg.SetSize((610, 780)) 
        self.dlg.ShowModal()
        
    def on_yes_rb(self, event):
        
        if self.flagRB == 1:        
            self.qpStatLin = wx.StaticText(self.dlg, -1, "Q value for P-Wave:")
            self.qpChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
            self.qsStatLin = wx.StaticText(self.dlg, -1, "Q value for S-Wave:")
            self.qsChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
            self.qSizer = wx.FlexGridSizer(cols=2, hgap=3, vgap=3)   
            self.qSizer.AddGrowableCol(1)
            self.qSizer.Add(self.qpStatLin, 0, wx.ALL, 5)
            self.qSizer.Add(self.qpChoiceBox, 0, wx.EXPAND|wx.ALL, 5)
            self.qSizer.Add(self.qsStatLin, 0, wx.ALL, 5)
            self.qSizer.Add(self.qsChoiceBox, 0, wx.EXPAND|wx.ALL, 5)
            self.mainSizer.Insert(8, self.qSizer, 0, wx.EXPAND|wx.ALL, 5)
            self.flagRB = 0
            
        self.dlg.SetSize((610, 860))
        
    def on_no_rb(self, event):
        
        if self.flagRB == 0:        
            self.mainSizer.Remove(self.qSizer)
            self.qpStatLin.Destroy()
            self.qpChoiceBox.Destroy()
            self.qsStatLin.Destroy()
            self.qsChoiceBox.Destroy()
            
            self.dlg.SetSize((610, 780))
            self.flagRB = 1
        
    def on_well_choice(self,event):
        wellname = self.wellChoiceBox.GetStringSelection()
        wellUid = self.wellOptions[wellname]
        self.vpChoiceBox.Clear()
        self.vsChoiceBox.Clear()
        self.rhoChoiceBox.Clear()
        self.logOptions.clear()
        for log in self.OM.list('log', wellUid):
            self.logOptions[log.name] = log.uid
        self.vpChoiceBox.AppendItems(self.logOptions.keys())
        self.vsChoiceBox.AppendItems(self.logOptions.keys())
        self.rhoChoiceBox.AppendItems(self.logOptions.keys())
        
    def on_ok(self, event):
                
        parDict = OrderedDict()
        parDict['Qvalue']=0    
        if self.modChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a type of Seismogram to be modeled!")
            raise Exception("Please choose a type of Seismogram to be modeled!")            
        parDict['modFlag'] = self.modtype[self.modChoiceBox.GetStringSelection()]
        if self.respChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a type of Response!")
            raise Exception("Please choose a type of Response!")            
        parDict['respFlag'] = self.modtype[self.modChoiceBox.GetStringSelection()]
        if self.wellChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a Well!")
            raise Exception("Please choose a Well!")
        parDict['wellID'] = self.wellOptions[self.wellChoiceBox.GetStringSelection()]    
        if self.vpChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a Vp log!")
            raise Exception("Please choose a Vp log!")           
        parDict['vpLogID'] = self.logOptions[self.vpChoiceBox.GetStringSelection()]
        if self.vsChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a Vs log!")
            raise Exception("Please choose a Vs log!")
        parDict['vsLogID'] = self.logOptions[self.vsChoiceBox.GetStringSelection()]
        if self.rhoChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a Density log!")
            raise Exception("Please choose a Density log!")
        parDict['rhoLogID'] = self.logOptions[self.rhoChoiceBox.GetStringSelection()]
        if not self.yesQvalueRB.GetValue() and not self.noQvalueRB.GetValue():
            wx.MessageBox("Please choose the Q-value option!")
            raise Exception("Please choose the Q-value option!")
            parDict['Qvalue'] = self.yesQvalueRB.GetValue()
        if self.flagRB == 0:
            parDict['Qvalue']=1
            if self.qpChoiceBox.GetStringSelection() == "":
                wx.MessageBox("Please choose a Q-value log for P-Wave!")
                raise Exception("Please choose a Q-value log for P-Wave!")
            parDict['Pwav_QvalueID'] = self.logOptions[self.qpChoiceBox.GetStringSelection()]
            if self.qsChoiceBox.GetStringSelection() == "":
                wx.MessageBox("Please choose a Q-value log for S-Wave!")
                raise Exception("Please choose a Q-value log for S-Wave!")
            parDict['Swav_QvalueID'] = self.logOptions[self.qsChoiceBox.GetStringSelection()]
        if self.nsampTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Number of Samples!")
            raise Exception("Please choose the Number of Samples!")
        parDict['numsamps'] = int(float(self.nsampTxtCtrl.GetValue()))
        if self.dtTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Sample Rate Interval!")
            raise Exception("Please choose the Sample Rate Interval!")
        parDict['dt'] = float(self.dtTxtCtrl.GetValue())
        if self.fwavTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose Peak Frequency of the Wavelet to be Used!")
            raise Exception("Please choose Peak Frequency of the Wavelet to be Used!")
        parDict['fWav'] = float(self.fwavTxtCtrl.GetValue())
        if self.ntrcsTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Number of Traces of the Output!")
            raise Exception("Please choose the Number of Traces of the Output!")
        parDict['ntraces'] = int(float(self.ntrcsTxtCtrl.GetValue()))
        if self.trc1TxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the 1st trace cordinate!")
            raise Exception("Please choose the 1st trace cordinate!")
        parDict['trc1'] = float(self.trc1TxtCtrl.GetValue())
        if self.latdtTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Lateral Sample Rate!")
            raise Exception("Please choose the Lateral Sample Rate!")
        parDict['dlat'] = float(self.latdtTxtCtrl.GetValue())
        if self.cam1velTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Velocity of the 1st Layer!")
            raise Exception("Please choose the Velocity of the 1st Layer!")
        parDict['vel1'] = float(self.cam1velTxtCtrl.GetValue())
        if self.cam1thickTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Thickness of 1st Layer!")
            raise Exception("Please choose the Thickness of 1st Layer!")
        parDict['z1'] = float(self.cam1thickTxtCtrl.GetValue())
        if self.nsupTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Number of Superior Layers!")
            raise Exception("Please choose the Number of Superior Layers!")
        parDict['nsup'] = int(float(self.nsupTxtCtrl.GetValue()))
        if self.zsupTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Thickness of Each Superior Layers!")
            raise Exception("Please choose the Thickness of Each Superior Layers!")
        parDict['zsup'] = float(self.zsupTxtCtrl.GetValue())
        if self.firstLayerTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Depth of the 1st Layer to be Modeled!")
            raise Exception("Please choose the Depth of the 1st Layer to be Modeled!")
        parDict['firstLayer'] = float(self.firstLayerTxtCtrl.GetValue())
        if self.lastLayerTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Depth of the Last Layer to be Modeled!")
            raise Exception("Please choose the Depth of the Last Layer to be Modeled!")
        parDict['lastLayer'] = float(self.lastLayerTxtCtrl.GetValue())
        if self.pnumTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Number Ray Parameters to Integration!")
            raise Exception("Please choose the Number Ray Parameters to Integration!")
        parDict['pNum'] = int(float(self.pnumTxtCtrl.GetValue()))
        if self.angmaxTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Maximum Angle of Incidence!")
            raise Exception("Please choose the Maximum Angle of Incidence!")
        parDict['angMax'] = float(self.angmaxTxtCtrl.GetValue())    
        if self.vpSupTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the P velocity of Superior Layers!")
            raise Exception("Please choose the P velocity of Superior Layers!")
        parDict['vpSup'] = float(self.vpSupTxtCtrl.GetValue())    
        if self.vsSupTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Maximum Angle of Incidence!")
            raise Exception("Please choose the Maximum Angle of Incidence!")
        parDict['vsSup'] = float(self.vsSupTxtCtrl.GetValue())
        if self.outChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a type of Output!")
            raise Exception("Please choose a type of Output!")
        parDict['outFlag'] = self.outtype[self.outChoiceBox.GetStringSelection()]
        if self.objTxtCtrl.GetValue() == "":
            wx.MessageBox("Please Choose an Output Name!")
            raise Exception("Please Choose an Output Name!")
        parDict['outName'] = self.objTxtCtrl.GetValue()       
        
        return_flag = -1
        
        try:
            disableAll = wx.WindowDisabler()
            wait = wx.BusyInfo("Running the Modeling...")
            return_flag = Reflectivity(self.OM, parDict)
        except Exception as e:
            print ('ERROR:', str(e))
            raise e
        finally:
            del wait
            del disableAll
            self.dlg.Destroy()

        if return_flag == 1:
            wx.MessageBox('Vp and Vs logs have different sizes!')
        elif return_flag == 2:
            wx.MessageBox('Vp and Density logs have different sizes!')
        elif return_flag == 3:
            wx.MessageBox('Vp and Depth indexes have different sizes!')
        elif return_flag == 4:
            wx.MessageBox('Insuficient Number of Layer!')
        elif return_flag == 5:
            wx.MessageBox('The Q-values Logs have different sizes than Vp and VS!')      
        elif return_flag == 6:
            wx.MessageBox('Done!')
        else:
            wx.MessageBox('Other problems has occurred.')
            

def teste11(event):
    print ('teste 11')


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




"""
def on_poisson_ratio(event):
    
    def calc_poisson(vp, vs):
        aux = vp/vs
        aux = np.power(aux, 2)
        poisson = (aux - 2) / ((aux - 1) * 2)
        return poisson

    
    OM = ObjectManager()
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Poisson ratio')
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
        dlg.view.AddChoice(ctn_vp, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='vp')    
        #
        ctn_vs = dlg.view.AddCreateContainer('StaticBox', label='Shear wave', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5) 
        dlg.view.AddChoice(ctn_vs, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='vs')
        #
        ctn_rho = dlg.view.AddCreateContainer('StaticBox', label='Poisson curve name', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5) 
        dlg.view.AddTextCtrl(ctn_rho, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='new_name', initial='') 
        #
        def on_change_well(name, old_value, new_value, **kwargs):
            print '\non_change_well:', name, old_value, new_value, kwargs
            vps = OrderedDict()
            vss = OrderedDict()
            OM = ObjectManager()
            logs = OM.list('log', new_value)
            for log in logs:
                if log.datatype == 'Velocity':
                    vps[log.name] = log.uid
                elif log.datatype == 'ShearVel':
                    vss[log.name] = log.uid
            choice_vp = dlg.view.get_object('vp')
            choice_vs = dlg.view.get_object('vs')
            choice_vp.set_options(vps)
            choice_vs.set_options(vss)
            choice_vp.set_value(0, True)
            choice_vs.set_value(0, True)
        #    
        choice_well = dlg.view.get_object('welluid')
        choice_well.set_trigger(on_change_well)         
        #
        dlg.view.SetSize((270, 330))
        result = dlg.view.ShowModal()
        #
        if result == wx.ID_OK:
            results = dlg.get_results()  
            print results
            
            disableAll = wx.WindowDisabler()
            wait = wx.BusyInfo("Wait...")     
   
            welluid = results['welluid']
            vp_obj = OM.get(results.get('vp'))
            vp_data = vp_obj.data
            vs_data = OM.get(results.get('vs')).data

            new_name = results.get('new_name')
            
            poisson = calc_poisson(vp_data, vs_data)

            

   
    except Exception as e:
        print '\n', e.message, e.args
        pass
    finally:
        try:
            del wait
            del disableAll 
            UIM.remove(dlg.uid) 
        except:
            pass
"""

def on_akirichards_pp(event):
    #
    print ('\non_akirichards_pp')    
    #
    
    
    wells = get_wells_dict()
    if wells is None:
        return
    #   
        
        
    def calc_poisson(vp, vs):
        aux = vp/vs
        aux = np.power(aux, 2)
        poisson = (aux - 2) / ((aux - 1) * 2)
        return poisson
    
    
    def p_impedance(vp, rho):
        return rho * vp
    
    
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
            ret_array[i][1] = -4.0 * (gamma * np.sin(angle)) ** 2.0
            ret_array[i][2] = 0.5 * (1 + ret_array[i][1])
            # Old wrong value above found in Fortran code
            #ret_array[i][2] = (-0.5 * ((np.tan(angle))**2)) + (2 * ((gamma * np.sin(angle))**2))
        return ret_array	

    # TODO: Colocar isso em Algo.Spectral.Spectral
    # Function below from: https://github.com/seg/tutorials-2014/blob/master/1406_Make_a_synthetic/how_to_make_synthetic.ipynb
    # Define a wavelet.
    def ricker(f, length, dt):
        t = np.linspace(-length / 2, (length-dt) / 2, length / dt)
        y = (1. - 2.*(np.pi**2)*(f**2)*(t**2))*np.exp(-(np.pi**2)*(f**2)*(t**2))
        return t, y    
    #
    OM = ObjectManager()
    #
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='P-Wave Modeling')
    #
    try:
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
            print ('\non_change_well:', name, old_value, new_value, kwargs)
            vps = OrderedDict()
            vss = OrderedDict()
            rhos = OrderedDict()
            OM = ObjectManager()
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
            print (results)
            
            disableAll = wx.WindowDisabler()
            wait = wx.BusyInfo("Wait...")     
   
            welluid = results['welluid']
            vp_obj = OM.get(results.get('vp'))
            vp_data = vp_obj.data
            vs_data = OM.get(results.get('vs')).data
            rho_data = OM.get(results.get('rho')).data
            new_name = results.get('new_name')
            #
            angle_degree = np.array(range(46))
            angles_rad = np.deg2rad(angle_degree)
            
            reflectivity = avo_modeling_akirichards_pp(vp_data, vs_data, rho_data, angles_rad)
            reflectivity = np.insert(reflectivity, 0, np.nan, axis=0)
            reflectivity = reflectivity.T
            reflectivity = np.nan_to_num(reflectivity)
            
            print ('\n\nreflectivity:', np.nanmin(reflectivity), np.nanmax(reflectivity))
            #
            #print 'reflectivity.shape:', reflectivity.shape
            well = OM.get(welluid)
            
            #
            poisson = calc_poisson(vp_data, vs_data)
            ip = p_impedance(vp_data, rho_data)

            poisson_log = OM.new('log', poisson, index_set_uid=vp_obj.index_set_uid,
                         name='Poisson ratio', unit=None, datatype='PoissonRatio'
            )
            OM.add(poisson_log, welluid)              

            ip_log = OM.new('log', ip, index_set_uid=vp_obj.index_set_uid,
                         name='P Impedance', unit='(m/s)*(g/cm3)', datatype='Impedance'
            )
            OM.add(ip_log, welluid)    
            
            #            
            model = OM.new('model1d', reflectivity, 
                           datatype='Rpp Aki-Richards', name=new_name
            )
            OM.add(model, welluid)
            #
            index_set_uid = OM.get(results.get('vp')).index_set_uid
            new_index_set = OM.new('index_set', vinculated=index_set_uid)
            OM.add(new_index_set, model.uid)
            #
            index = OM.new('data_index', 1, 'Angle', 'ANGLE', 'deg', 
                           data=angle_degree
            ) 
            OM.add(index, new_index_set.uid)
            #'''
            
            """
            #
            # Do the convolution
            synthetic_data = np.zeros(reflectivity.shape) 
            tw, w = ricker(f=25, length = 0.512, dt = 0.004)
            for i in range(synthetic_data.shape[0]):
                synthetic_data[i] =  np.convolve(w, reflectivity[i], mode='same')
            #           
            print 'synthetic_data:', np.nanmin(synthetic_data), np.nanmax(synthetic_data)
            #
            #
            index_set_uid = OM.get(results.get('vp')).index_set_uid
            #vp_index_set_name = OM.get(index_set_uid).name
            #
            
            #
            synth = OM.new('gather', synthetic_data, datatype='SYNTH', name=new_name)
            OM.add(synth, welluid)
            #
            new_index_set = OM.new('index_set', vinculated=index_set_uid)
            OM.add(new_index_set, synth.uid)
            # 
            #for dim_idx, dis in vp_obj.get_data_indexes().items():
            #    for di in dis:
            #        index = OM.new('data_index', dim_idx, di.name, di.datatype, di.unit, data=di.data)
            #        OM.add(index, index_set_uid)     
            #        
            index = OM.new('data_index', 1, 'Angle', 'ANGLE', 'deg', data=angle_degree)
            OM.add(index, new_index_set.uid)
            #  
            """
        #
		 
	
   
    except Exception as e:
        print ('\n', str(e))
        pass
    finally:
        try:
            del wait
            del disableAll 
            UIM.remove(dlg.uid) 
        except:
            pass



def teste7(event):
    raise Exception()
    '''
    OM = ObjectManager() 
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
        t0 = seis_pp.get_indexes().data[0]
        ntrace_pp = seis_pp.data.shape[0]
        npts_pp = seis_pp.data.shape[1]
        #
        dt_ps = seis_ps.step/1000.0
        t0_ps = seis_ps.get_indexes().data[0]
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
            index = seis_mod_ppps_pp.get_indexes()
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
    OM = ObjectManager() 


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
        t0 = seis.get_indexes().data[0]

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
    
            inv_index = OM.new('index_curve', seis.get_indexes().data,
                               name='DEPTH', 
                               unit=seis.get_indexes().name, 
                               datatype=seis.get_indexes().attributes['curvetype'])
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


def on_cwt(event):
    #
    OM = ObjectManager() 
    
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Continuous Wavelet Transform') 
    #
    try:
        ctn_input_data = dlg.view.AddCreateContainer('StaticBox', 
                            label='Input data', orient=wx.VERTICAL, 
                            proportion=0, flag=wx.EXPAND|wx.TOP, border=5
        )
        #
        accept_tids = ['seismic', 'gather', 'log', 'model1d']
        input_data = OrderedDict()
        for tid in accept_tids:
            for obj in OM.list(tid):
                parent_uid = OM._getparentuid(obj.uid)
                if parent_uid:
                    parent = OM.get(parent_uid)
                    input_data[obj._get_tid_friendly_name() + ': ' + obj.name + '@' + parent.name ] = obj.uid
                else:
                    input_data[obj._get_tid_friendly_name() + ': ' + obj.name] = obj.uid

        dlg.view.AddChoice(ctn_input_data, proportion=0, flag=wx.EXPAND|wx.TOP,
                           border=5, widget_name='obj_uid', options=input_data
        )     
        #    
        ctn_real_complex = dlg.view.AddCreateContainer('StaticBox', 
                    label='Input signal', orient=wx.HORIZONTAL, proportion=0, 
                    flag=wx.EXPAND|wx.TOP, border=5
        )
        dlg.view.AddRadioButton(ctn_real_complex, 
                    proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                    widget_name='real', label='Real'
        )
        dlg.view.AddRadioButton(ctn_real_complex, 
                    proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                    widget_name='analytic', label='Analytic'
        )
        #        
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
            print ('\nresults:', results, '\n')
            
            disableAll = wx.WindowDisabler()
            wait = wx.BusyInfo("Applying CWT. Wait...")
            
            dj = float(results.get('dj'))

            wavelet = results.get('wavelet')        
            if wavelet == 'morlet':
                func = MorletWavelet()
            elif wavelet == 'ricker':
                func = RickerWavelet()
            elif wavelet == 'dog3':
                func = DOGWavelet(m=3) 
            elif wavelet == 'dog4':
                func = DOGWavelet(m=4)             
            elif wavelet == 'dog5':
                func = DOGWavelet(m=5) 
            elif wavelet == 'dog6':
                func = DOGWavelet(m=6) 
            elif wavelet == 'paul2':
                func = PaulWavelet(m=2) 
            elif wavelet == 'paul3':
                func = PaulWavelet(m=3) 
            elif wavelet == 'paul4':
                func = PaulWavelet(m=4) 
            elif wavelet == 'paul5':
                func = PaulWavelet(m=5)             
            elif wavelet == 'paul6':
                func = PaulWavelet(m=6) 
            else:
                raise Exception()   
            #    
            obj_uid = results.get('obj_uid')
            obj = OM.get(obj_uid) 
            mode = results.get('mode')   
            analytic = results.get('analytic')
            
            #
            
            input_indexes = obj.get_data_indexes()
            
            z_axis = input_indexes[0][0]
			
            ###
            # TODO: rever TIME/DEPTH
            time = z_axis.data
            step = z_axis.step
            if not step:
                print ('Data has not a step. Trying to calculating it from data.')
                try:
                    step = z_axis.data[1] - z_axis.data[0]
                except:
                    print ('ERROR: STEP!')
                    raise
            ###
            
            time = time/1000
            step  = step/1000            
            
            if obj_uid[0] == 'log':

                if analytic:
                    ht = HilbertTransform(obj.data, step)
                    input_data = ht.analytic_signal
                else:
                    input_data = obj.data
                wt = WaveletTransform(input_data, dj=dj, wavelet=func,  
                                      dt=step, time=time
                )
                #wt_axis = wt.wavelet_transform.shape[0]
                #new_shape = (wt_axis, len(obj.data))
                #print 'New data CWT shape:', new_shape 
                #data_out = np.zeros(new_shape)    
                freqs =  np.flip(wt.fourier_frequencies, 0)
                scales = np.flip(wt.scales, 0)
                if mode == 0:
                    data_out = np.abs(np.flip(wt.wavelet_transform, 0))      
                elif mode == 1:            
                    # np.abs(self.wavelet_transform) ** 2
                    data_out = np.flip(wt.wavelet_power, 0)         
                elif mode == 2:   
                    data_out = np.angle(np.flip(wt.wavelet_transform, 0))
                elif mode == 3:   
                    data_out = np.unwrap(np.angle(np.flip(wt.wavelet_transform, 0)), axis=0)    

 
                name = results.get('cwt_name')	 

                scalogram = OM.new('gather_scalogram', data_out, name=name)
                parent_uid = OM._getparentuid(obj_uid)
                if not OM.add(scalogram, parent_uid):
                    raise Exception('Object was not added. tid={\'gather_scalogram\'}')

                new_index_set = OM.new('index_set', vinculated=obj.index_set_uid)	 
                OM.add(new_index_set, scalogram.uid)
                #
                index = OM.new('data_index', 1, 'Frequency', 'FREQUENCY', 'Hz', 
                               data=freqs
                ) 
                OM.add(index, new_index_set.uid)
                #
                index = OM.new('data_index', 1, 'Scale', 'SCALE', 
                               data=scales
                ) 
                OM.add(index, new_index_set.uid)     
				
            else:
            
            
                print ('Input obj.data.shape:', obj.data.shape)
                
                if len(obj.data.shape) == 4:
                    print ('Input data shape lenght: 4')
                    iaxis, jaxis, kaxis, zaxis = obj.data.shape
                    data_out = None
                    for i in range(iaxis):
                        for j in range(jaxis):
                            for k in range(kaxis):
                                if analytic:
                                    ht = HilbertTransform(obj.data[i][j][k], step)
                                    input_data = ht.analytic_signal
                                else:
                                    input_data = obj.data[i][j][k]
    							  
    																	
    																														 
                                 
                                wt = WaveletTransform(input_data, dj=dj, wavelet=func,  
                                                      dt=step, time=time
                                )   
                                #print 'wt_shape:', wt.wavelet_transform.shape
                                #print (i, j, k), wt.wavelet_transform.shape, np.flip(wt.fourier_frequencies, 0)#, wt.scales
                                if data_out is None:
                                    wt_axis = wt.wavelet_transform.shape[0]
                                    new_shape = (iaxis, jaxis, kaxis, wt_axis, zaxis)
                                    print ('New data CWT shape:', new_shape) 
                                    data_out = np.zeros(new_shape)    
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
                    print ('Input data shape lenght: 3')
                    iaxis, jaxis, zaxis = obj.data.shape
                    data_out = None
                    
                    for i in range(iaxis):
                        for j in range(jaxis):
                            if analytic:
                                ht = HilbertTransform(obj.data[i][j], step)
                                input_data = ht.analytic_signal
                            else:
                                input_data = obj.data[i][j]
                            wt = WaveletTransform(input_data, dj=dj, wavelet=func,  
                                                  dt=step, time=time
    														
                            )                    
    						 
                            #print 'wt_shape:', wt.wavelet_transform.shape
                            #print (i, j, k), wt.wavelet_transform.shape, np.flip(wt.fourier_frequencies, 0)#, wt.scales
    						 
                            if data_out is None:
                                wt_axis = wt.wavelet_transform.shape[0]
                                new_shape = (iaxis, jaxis, wt_axis, zaxis)
                                print ('New data CWT shape:', new_shape) 
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
    
                elif len(obj.data.shape) == 2:
                    print ('Input data shape lenght: 2')
                    jaxis, zaxis = obj.data.shape
                    data_out = None
    
                    for j in range(jaxis):
                        if analytic:
                            ht = HilbertTransform(obj.data[j], step)
                            input_data = ht.analytic_signal
                        else:
                            input_data = obj.data[j]
                        wt = WaveletTransform(input_data, dj=dj, wavelet=func,  
                                              dt=step, time=time
                        )
                        if data_out is None:
                            wt_axis = wt.wavelet_transform.shape[0]
                            new_shape = (jaxis, wt_axis, zaxis)
                            print ('New data CWT shape:', new_shape) 
                            data_out = np.zeros(new_shape)    
                            freqs =  np.flip(wt.fourier_frequencies, 0)
                            scales = np.flip(wt.scales, 0)
                        if mode == 0:
                            data_out[j] = np.abs(np.flip(wt.wavelet_transform, 0))      
                        elif mode == 1:            
                            # np.abs(self.wavelet_transform) ** 2
                            data_out[j] = np.flip(wt.wavelet_power, 0)         
                        elif mode == 2:   
                            data_out[j] = np.angle(np.flip(wt.wavelet_transform, 0))
                        elif mode == 3:   
                            data_out[j] = np.unwrap(np.angle(np.flip(wt.wavelet_transform, 0)), axis=0)    
                else:
                    raise Exception()
                #
                
                print ('\ndata_out.shape:', data_out.shape)
                print (np.nanmin(data_out), np.nanmax(data_out))
                
                #
                name = results.get('cwt_name')
                
                if obj_uid[0] == 'gather' or obj_uid[0] == 'model1d':
                    scalogram = OM.new('gather_scalogram', data_out, name=name)
                    parent_uid = OM._getparentuid(obj_uid)
                    if not OM.add(scalogram, parent_uid):
                        raise Exception('Object was not added. tid={\'gather_scalogram\'}')  
                    #  
                    #obj_index_set = OM.list('index_set', obj.uid)[0]
                    #scalogram_index_set = OM.new('index_set', vinculated=obj_index_set.uid)
                    #OM.add(scalogram_index_set, scalogram.uid)
                    #
                elif obj_uid[0] == 'seismic':
                    scalogram = OM.new('scalogram', data_out, name=name)
                    result = OM.add(scalogram, obj_uid)
                    print ('result:', result)
                    #
                    #obj_index_set = OM.list('index_set', obj.uid)[0]
                    #scalogram_index_set = OM.new('index_set', vinculated=obj_index_set.uid)
                    #OM.add(scalogram_index_set, scalogram.uid)
                    #
                else:
                    raise Exception('Not a CWT valid class type.')
                #
                obj_index_set = OM.list('index_set', obj.uid)[0]
                scalogram_index_set = OM.new('index_set', name=obj_index_set.name)
                OM.add(scalogram_index_set, scalogram.uid)
                #
                state = z_axis.get_state()
                index = OM.create_object_from_state('data_index', **state)
                OM.add(index, scalogram_index_set.uid)
                #
                index = OM.new('data_index', 1, 'Frequency', 'FREQUENCY', 'Hz', 
                               data=freqs
                ) 
                OM.add(index, scalogram_index_set.uid)
                #
                index = OM.new('data_index', 1, 'Scale', 'SCALE', 
                               data=scales
                ) 
                OM.add(index, scalogram_index_set.uid)
                
                # Inserindo as outras dimensões do dado
                for idx in range(1, len(input_indexes)):
                    print ('idx:', idx)
                    state = input_indexes[idx][0].get_state()        
                    state['dimension'] = idx+1
                    index = OM.index = OM.create_object_from_state('data_index', **state)
                    OM.add(index, scalogram_index_set.uid)
                #
    except Exception as e:
        print ('ERROR [on_cwt]:', str(e))
        pass	
    finally:
        try:
            del wait
            del disableAll
        except:
            pass
        UIM.remove(dlg.uid)



def on_phase_rotation(event):
    #
    OM = ObjectManager() 
    
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Phase Rotation') 
    #
    try:
        ctn_input_data = dlg.view.AddCreateContainer('StaticBox', 
                            label='Input data', orient=wx.VERTICAL, 
                            proportion=0, flag=wx.EXPAND|wx.TOP, border=5
        )
        #
        #accept_tids = ['seismic', 'gather', 'log']
        accept_tids = ['log']
        input_data = OrderedDict()
        for tid in accept_tids:
            for obj in OM.list(tid):
                input_data[obj._get_tid_friendly_name() + ': ' + obj.name] = obj.uid

        dlg.view.AddChoice(ctn_input_data, proportion=0, flag=wx.EXPAND|wx.TOP,
                           border=5, widget_name='obj_uid', options=input_data
        )     
        #   
        ctn_degrees = dlg.view.AddCreateContainer('StaticBox', label='Degrees', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_degrees, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='degrees', initial='0') 
        #
        ctn_name = dlg.view.AddCreateContainer('StaticBox', label='New object name', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_name, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='name')       
        #
        dlg.view.SetSize((330, 430))
        result = dlg.view.ShowModal()
        
        
        
        if result == wx.ID_OK:
            results = dlg.get_results()  
            print ('\nresults:', results, '\n')
            #
            disableAll = wx.WindowDisabler()
            wait = wx.BusyInfo("Applying Phase Rotation. Wait...")            
            #    
            obj_uid = results.get('obj_uid')
            obj = OM.get(obj_uid) 
            parentuid = OM._getparentuid(obj_uid)
            degrees = float(results.get('degrees'))   
            new_name = str(results.get('name'))              
            
            
            index = obj.get_data_indexes()[0][0]
            
            rot_data_index, rot_data = frequency_phase_rotation(obj.data, degrees, True)   
            rot_data = rot_data.real
            
            rot_interp_data = np.interp(np.array(range(len(index.data))), rot_data_index, rot_data)
            
            #new_data = new_data.real
            
            #print '\n\nrot_interp_data.shape:', rot_interp_data.shape, obj.data.shape
            #print rot_data_index[0], rot_data_index[-1]
            #print len(index.data), len(rot_data_index)
            #print 
            #for i in rot_data_index:
            #    print 'rdi:', i
            #print
            #print obj.data - new_data

            log = OM.new('log', rot_interp_data, index_set_uid=obj.index_set_uid,
                         name=new_name, unit=obj.unit, datatype=obj.datatype
            )
            #print 'kkk 2'
            OM.add(log, parentuid)  
            #print 'kkk 3'

    except Exception as e:
        print ('ERROR:', str(e))
			
    finally:
        del wait
        del disableAll
        UIM.remove(dlg.uid)  
        



def on_hilbert_attributes(event):
    #
    OM = ObjectManager() 
    
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Hiltert Attibutes') 
    #
    try:
        ctn_input_data = dlg.view.AddCreateContainer('StaticBox', 
                            label='Input data', orient=wx.VERTICAL, 
                            proportion=0, flag=wx.EXPAND|wx.TOP, border=5
        )
        #
        #accept_tids = ['seismic', 'gather', 'log']
        accept_tids = ['log']
        input_data = OrderedDict()
        for tid in accept_tids:
            for obj in OM.list(tid):
                input_data[obj._get_tid_friendly_name() + ': ' + obj.name] = obj.uid

        dlg.view.AddChoice(ctn_input_data, proportion=0, flag=wx.EXPAND|wx.TOP,
                           border=5, widget_name='obj_uid', options=input_data
        )     
        dlg.view.SetSize((330, 430))
        result = dlg.view.ShowModal()
		
        if result == wx.ID_OK:
            results = dlg.get_results()  
            print ('\nresults:', results, '\n')
            #
            disableAll = wx.WindowDisabler()
            wait = wx.BusyInfo("Applying Hilbert Attributes. Wait...")            
            #    
            obj_uid = results.get('obj_uid')
            obj = OM.get(obj_uid) 
            parentuid = OM._getparentuid(obj_uid)    
            
            index = obj.get_data_indexes()[0][0]
            step = index.data[1] - index.data[0]
            ht = HilbertTransform(obj.data, step)

            ht.amplitude_envelope

            log = OM.new('log', ht.amplitude_envelope, index_set_uid=obj.index_set_uid,
                         name=obj.name+'_AMP_ENV', 
                         unit=obj.unit, datatype=obj.datatype
            )
            OM.add(log, parentuid)  
            
            log = OM.new('log', ht.instantaneous_frequency, index_set_uid=obj.index_set_uid,
                         name=obj.name+'_INST_FREQ', 
                         unit=obj.unit, datatype=obj.datatype
            )
            OM.add(log, parentuid)  

            log = OM.new('log', ht.instantaneous_phase, index_set_uid=obj.index_set_uid,
                         name=obj.name+'_INST_PHASE', 
                         unit=obj.unit, datatype=obj.datatype
            )
            OM.add(log, parentuid)



    except Exception as e:
        print ('ERROR:', str(e))
			
    finally:
        del wait
        del disableAll
        UIM.remove(dlg.uid)  




def on_exit(*args, **kwargs):
    mwc = interface.get_main_window_controller()
    mwc.close()

    

def on_new(*args, **kwargs):
    OM = ObjectManager()
    OM._reset()




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
    except Exception as e:
        print ('ERROR [on_open]:', str(e))
        raise


def on_save(*args, **kwargs):
    gripy_app = wx.App.Get() 
    gripy_app.on_save()


def on_save_as(*args, **kwargs):
    gripy_app = wx.App.Get()
    gripy_app.on_save_as()
    
	
def on_rock(event):
    OM = ObjectManager() 
    
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Rock creator') 
    
    cont_well = dlg.view.AddCreateContainer('StaticBox', label='Well', 
                                          orient=wx.HORIZONTAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )
    cont_sup = dlg.view.AddCreateContainer('StaticBox', label='Type of Support', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )
    cont_grain = dlg.view.AddCreateContainer('StaticBox', label='Grain Parts', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )
    cont_matr = dlg.view.AddCreateContainer('StaticBox', label='Matrix Parts', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )
    cont_rock = dlg.view.AddCreateContainer('StaticBox', label='Rock Name', 
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
    wells['GLOBAL'] = 'GLOBAL'
    for well in OM.list('well'):
        wells[well.name] = well.uid
            
    c00 = dlg.view.AddCreateContainer('BoxSizer', cont_sup, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddChoice(c00, widget_name='suporte', options=options)
    
    def on_change_support(name, old_value, new_value, **kwargs):
        textctrl_name = dlg.view.get_object('topo')
        statictext_suport = dlg.view.get_object('static_text_suport')
        textctrl_range = dlg.view.get_object('base')
        statictext_range = dlg.view.get_object('static_text_range')
        choice = dlg.view.get_object('chid')
#        print type(textctrl_range), type(c1hoice),   '\n'
#        print old_value, new_value
        
        if old_value == "FACIES":
#            print 'no old'
            choice = dlg.view.get_object('chid')
#            print choice
            print ('\nlist\n', OM.list('partition')[0].uid, '222', OM.list('partition')[0].get_friendly_name())
            choice.hide()
        
        if old_value == None:
#            print 'no old'
            choice = dlg.view.get_object('chid')
#            print choice
            choice.hide()
            
        if new_value == "PT":
#            print choice.show(),'-p'
#            if choice.show() == False: 
#                choice.hide()
#                print 'hide p'
            textctrl_name.show()
            statictext_suport.show()
            textctrl_name.set_value('ponto')
            statictext_suport.set_value('PONTO:')
            textctrl_range.hide()
            statictext_range.hide()
            
        if new_value == "FACIES":
#            a = dlg.view.AddChoice(c2, widget_name='partuid', options=partitions)
#            textctrl_name.set_value('facies')  
            
#            textctrl_name.hide()
#            statictext_suport.set_value('FACIES:')
#            dlg.view.AddChoice(c2, widget_name='chid', options=wells)            
            choice.show()
            
#            dlg.view.AddChoice(c2,widget_name='partuid', options=partitions)
#            statictext_suport.set_value('FACIES:')
            statictext_suport.hide()
            textctrl_name.hide()
            textctrl_range.hide()
            statictext_range.hide()
#            choice.show()
        
            
        if new_value == "TOP&BASE":
#            print choice.show(),'-z',choice.show()
#            if choice.show() == False: 
#                choice.hide()
#                print 'hide z'
            textctrl_name.show()
            statictext_suport.show()
            textctrl_name.set_value('Topo')  
            statictext_suport.set_value('TOPO:')
            textctrl_range.set_value ('BASE')
            textctrl_range.show()
            statictext_range.show()
            
    choice_datatype = dlg.view.get_object('suporte')
    choice_datatype.set_trigger(on_change_support)
    
    c2 = dlg.view.AddCreateContainer('BoxSizer', cont_sup, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c2, label='TOPO:', proportion=1, widget_name='static_text_suport', flag=wx.ALIGN_RIGHT)
    dlg.view.AddChoice(c00, widget_name='chid', options=partitions,  proportion=1, flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c2, proportion=1, flag=wx.ALIGN_LEFT, widget_name='topo', initial='')
    
#    choices = dlg.view.get_object('chid')
#    choices.hide()
    c3 = dlg.view.AddCreateContainer('BoxSizer', cont_sup, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c3, label='BASE:', proportion=1, widget_name='static_text_range',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c3, proportion=1, flag=wx.ALIGN_LEFT, widget_name='base', initial='')
    
    
    dlg.view.AddChoice(cont_well, widget_name='welluid', options=wells)
    dlg.view.AddTextCtrl(cont_rock, proportion=0, flag=wx.EXPAND|wx.TOP, 
                         border=5, widget_name='rock_name', initial='new_rock'#, 
    )
    minerals = OrderedDict()
    minerals['OTHER'] = 'OTHER'
    minerals['CALCITE'] = 'CALCITE'    
    minerals['DOLOMITE'] = 'DOLOMITE'
    minerals['QUARTZ'] = 'QUARTZ'
    minerals['FELDSPAR'] = 'FELDSPAR'
    
    def on_change_mineral(name, old_value, new_value, **kwargs):
        if name == 'mineralgrain':
            textctrl_k = dlg.view.get_object('kmod1')
            textctrl_g = dlg.view.get_object('gmod1')
            textctrl_rho = dlg.view.get_object('dens1')
        elif name == 'mineralmatr':
            textctrl_k = dlg.view.get_object('kmod2')
            textctrl_g = dlg.view.get_object('gmod2')
            textctrl_rho = dlg.view.get_object('dens2')
            
        if new_value == "CALCITE":
            textctrl_k.disable()
            textctrl_g.disable()
            textctrl_rho.set_value('2.65')
            textctrl_rho.disable()
        
        if new_value == "DOLOMITE":
            textctrl_k.disable()
            textctrl_g.disable()
            textctrl_rho.set_value('2.71')
            textctrl_rho.disable()
        
        if new_value == "QUARTZ":
            textctrl_k.disable()
            textctrl_g.disable()
            textctrl_rho.set_value('2.65')
            textctrl_rho.disable()
            
        if new_value == "FELDSPAR":
            textctrl_k.disable()
            textctrl_g.disable()
            textctrl_rho.set_value('2.60')
            textctrl_rho.disable()
            
        if new_value == "OTHER":
            textctrl_k.enable()
            textctrl_g.enable()
            textctrl_rho.enable()
        
    dlg.view.AddChoice(cont_grain, widget_name='mineralgrain', options=minerals)
    choice_grain = dlg.view.get_object('mineralgrain')
    choice_grain.set_trigger(on_change_mineral)
    
    dlg.view.AddChoice(cont_matr, widget_name='mineralmatr', options=minerals)
    choice_matr = dlg.view.get_object('mineralmatr')
    choice_matr.set_trigger(on_change_mineral)
    
    c3_gr = dlg.view.AddCreateContainer('BoxSizer', cont_grain, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c3_gr, proportion=1,initial='Fraction ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c3_gr, proportion=1, widget_name='frac1', initial='0.50',flag=wx.ALIGN_RIGHT)
    
    c3_poro = dlg.view.AddCreateContainer('BoxSizer', cont_grain, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c3_poro, proportion=1,initial='Porosity ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c3_poro, proportion=1, widget_name='poro1', initial='0.20',flag=wx.ALIGN_RIGHT)
    
    c4 = dlg.view.AddCreateContainer('BoxSizer', cont_grain, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c4, proportion=1,widget_name='K_Modulus', initial='K Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c4, proportion=1, widget_name='kmod1', initial='36.5', flag=wx.ALIGN_RIGHT)
    
    c5 = dlg.view.AddCreateContainer('BoxSizer', cont_grain, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c5, proportion=1,widget_name='G_Modulus', initial='G Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c5, proportion=1,widget_name='gmod1', initial='78.6', flag=wx.ALIGN_RIGHT)
    
    c6 = dlg.view.AddCreateContainer('BoxSizer', cont_grain, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c6, proportion=1,widget_name='Density', initial='Density (g/cc) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c6, proportion=1,widget_name='dens1', initial='2.65', flag=wx.ALIGN_RIGHT)
    # matrix content
    c7_gr = dlg.view.AddCreateContainer('BoxSizer', cont_matr, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c7_gr, proportion=1,widget_name='fraction2', initial='Fraction ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c7_gr, proportion=1,widget_name='frac2', initial='0.20', flag=wx.ALIGN_LEFT)
    
    c7_poro = dlg.view.AddCreateContainer('BoxSizer', cont_matr, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c7_poro, proportion=1,initial='Porosity ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c7_poro, proportion=1, widget_name='poro2', initial='0.10',flag=wx.ALIGN_RIGHT)
    
    c8 = dlg.view.AddCreateContainer('BoxSizer', cont_matr, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c8, proportion=1,widget_name='K_Modulus2', initial='K Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c8, proportion=1,widget_name='kmod2', initial='36.5', flag=wx.ALIGN_LEFT)
    
    c9 = dlg.view.AddCreateContainer('BoxSizer', cont_matr, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c9,proportion=1, widget_name='G_Modulus2', initial='G Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c9,proportion=1, widget_name='gmod2', initial='78.6', flag=wx.ALIGN_LEFT)
    
    c10 = dlg.view.AddCreateContainer('BoxSizer', cont_matr, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c10,proportion=1, widget_name='Density2', initial='Density (g/cc) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c10, proportion=1,widget_name='dens2', initial='2.65', flag=wx.ALIGN_LEFT)

    #
    dlg.view.SetSize((300, 700))
    result = dlg.view.ShowModal()
    print ('result0')
    try:
        if result == wx.ID_OK:
            results = dlg.get_results()     
            
            rock_name = results.get('rock_name')
            support = results.get('suporte')          
            gr_name = results.get('mineralgrain')
            gr_f = results.get('frac1')
            gr_k = results.get('kmod1')
            gr_mi = results.get('gmod1')
            gr_rho = results.get('dens1')
            mt_f = results.get('frac2')
            mt_k = results.get('kmod2')
            mt_mi = results.get('gmod2')
            mt_rho = results.get('dens2')
            print ('\nrounds', gr_f, gr_k, gr_mi, gr_rho, rock_name)
            # 
            if support == 'PT':
                ponto = results.get('topo')
                print ('escolheu ponto', ponto)
            elif support == 'FACIES':
                facie = results.get('chid')
                print ('escolheu facies', facie)
            elif support == 'TOP&BASE':
                topo = results.get('topo')
                base = results.get('base')
                print ('escolheu top&base', topo, base, '\n')
#            rock = OM.new('rock', name=rock_name, output)
            rock = OM.new('rock', suporte = support, name=rock_name, grain = gr_f+'% '+gr_name, vp = gr_f, mu = gr_mi)
            well_uid = results.get('welluid')
            print (well_uid, 'wellid')
            if well_uid == 'GLOBAL':
                OM.add(rock)
            else:
                OM.add(rock, well_uid)  
#            else: 
#            OM.add(rock)  
    except Exception as e:
        print ('ERROR:', e)
    finally:
        UIM.remove(dlg.uid)
        
def on_fluid(event):
    OM = ObjectManager() 
    
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Fluid creator') 
    
    cont_fluid1 = dlg.view.AddCreateContainer('StaticBox', label='Fluid 1', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )
    cont_fluid2 = dlg.view.AddCreateContainer('StaticBox', label='Fluid 2', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )
    cont_fluid = dlg.view.AddCreateContainer('StaticBox', label='Fluid Name', 
                                          orient=wx.HORIZONTAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )
    
    dlg.view.AddTextCtrl(cont_fluid, proportion=0, flag=wx.EXPAND|wx.TOP, 
                         border=5, widget_name='fluid_name', initial='new_fluid'#, 
    )
    fluids = OrderedDict()
    fluids['OTHER'] = 'OTHER'
    fluids['WATER'] = 'WATER'    
    fluids['OIL'] = 'OIL'
    fluids['GAS'] = 'GAS'
    
    def on_change_fluid(name, old_value, new_value, **kwargs):
        if name == 'fluid1':
            textctrl_k = dlg.view.get_object('kmod1')
            textctrl_g = dlg.view.get_object('gmod1')
            textctrl_rho = dlg.view.get_object('dens1')
        elif name == 'fluid2':
            textctrl_k = dlg.view.get_object('kmod2')
            textctrl_g = dlg.view.get_object('gmod2')
            textctrl_rho = dlg.view.get_object('dens2')
            
        if new_value == "WATER":
            textctrl_k.disable()
            textctrl_g.disable()
            textctrl_rho.set_value('1.01')
            textctrl_rho.disable()
            
        if new_value == "OIL":
            textctrl_k.disable()
            textctrl_g.disable()
            textctrl_rho.set_value('O.88')
            textctrl_rho.disable()
            
        if new_value == "GAS":
            textctrl_k.disable()
            textctrl_g.disable()
            textctrl_rho.set_value('O.001')
            textctrl_rho.disable()
            
        if new_value == "OTHER":
            textctrl_k.enable()
            textctrl_g.enable()
            textctrl_rho.enable()
        
    dlg.view.AddChoice(cont_fluid1, widget_name='fluid1', options=fluids)
    choice_fluid1 = dlg.view.get_object('fluid1')
    choice_fluid1.set_trigger(on_change_fluid)
    
    dlg.view.AddChoice(cont_fluid2, widget_name='fluid2', options=fluids)
    choice_fluid2 = dlg.view.get_object('fluid2')
    choice_fluid2.set_trigger(on_change_fluid)
    
    c3 = dlg.view.AddCreateContainer('BoxSizer', cont_fluid1, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c3, proportion=1,initial='Fraction ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c3, proportion=1, widget_name='frac1', initial='0.20',flag=wx.ALIGN_RIGHT)
    
    c4 = dlg.view.AddCreateContainer('BoxSizer', cont_fluid1, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c4, proportion=1,widget_name='K_Modulus', initial='K Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c4, proportion=1, widget_name='kmod1', initial='36.5', flag=wx.ALIGN_RIGHT)
    
    c5 = dlg.view.AddCreateContainer('BoxSizer', cont_fluid1, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c5, proportion=1,widget_name='G_Modulus', initial='G Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c5, proportion=1,widget_name='gmod1', initial='78.6', flag=wx.ALIGN_RIGHT)
    
    c6 = dlg.view.AddCreateContainer('BoxSizer', cont_fluid1, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c6, proportion=1,widget_name='Density', initial='Density (g/cc) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c6, proportion=1,widget_name='dens1', initial='1.00', flag=wx.ALIGN_RIGHT)
    # matrix content
    c7 = dlg.view.AddCreateContainer('BoxSizer', cont_fluid2, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c7, proportion=1,widget_name='fraction2', initial='Fraction ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c7, proportion=1,widget_name='frac2', initial='0.20', flag=wx.ALIGN_LEFT)
    
    c8 = dlg.view.AddCreateContainer('BoxSizer', cont_fluid2, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c8, proportion=1,widget_name='K_Modulus2', initial='K Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c8, proportion=1,widget_name='kmod2', initial='36.5', flag=wx.ALIGN_LEFT)
    
    c9 = dlg.view.AddCreateContainer('BoxSizer', cont_fluid2, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c9,proportion=1, widget_name='G_Modulus2', initial='G Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c9,proportion=1, widget_name='gmod2', initial='78.6', flag=wx.ALIGN_LEFT)
    
    c10 = dlg.view.AddCreateContainer('BoxSizer', cont_fluid2, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(c10,proportion=1, widget_name='Density2', initial='Density (g/cc) ',flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(c10, proportion=1,widget_name='dens2', initial='1.00', flag=wx.ALIGN_LEFT)

    #
    dlg.view.SetSize((300, 550))
    result = dlg.view.ShowModal()
    print ('result0')
    try:
        if result == wx.ID_OK:
            results = dlg.get_results()     
            fluid_name = results.get('fluid_name')     
            gr_name = results.get('fluid1')
            gr_f = results.get('frac1')
            gr_k = results.get('kmod1')
            gr_mi = results.get('gmod1')
            gr_rho = results.get('dens1')
            mt_f = results.get('frac2')
            mt_k = results.get('kmod2')
            mt_mi = results.get('gmod2')
            mt_rho = results.get('dens2')
            print ('\nrounds', gr_f, gr_k, gr_mi, gr_rho, fluid_name)
            fluid = OM.new('fluid', name=fluid_name, fluid1 = gr_f+'% '+gr_name, vp = gr_f, vs = gr_mi, rho = gr_rho)
            OM.add(fluid)  
    except Exception as e:
        print ('ERROR:', str(e))
    finally:
        UIM.remove(dlg.uid)
        
        
        
def on_pt(event):
        
        if self.flagRB == 1:        
            dlg.view.AddTextCtrl(cont_sup, widget_name='pointi', initial='5500')
#            self.qpStatLin = wx.StaticText(self.dlg, -1, "Q value for P-Wave:")
#            self.qpChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
#            self.qsStatLin = wx.StaticText(self.dlg, -1, "Q value for S-Wave:")
#            self.qsChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
#            self.qSizer = wx.FlexGridSizer(cols=2, hgap=3, vgap=3)   
#            self.qSizer.AddGrowableCol(1)
#            self.qSizer.Add(self.qpStatLin, 0, wx.ALL, 5)
#            self.qSizer.Add(self.qpChoiceBox, 0, wx.EXPAND|wx.ALL, 5)
#            self.qSizer.Add(self.qsStatLin, 0, wx.ALL, 5)
#            self.qSizer.Add(self.qsChoiceBox, 0, wx.EXPAND|wx.ALL, 5)
#            self.mainSizer.Insert(8, self.qSizer, 0, wx.EXPAND|wx.ALL, 5)
#            self.flagRB = 0
            
#        self.dlg.SetSize((610, 860))
    
    


def on_teste_container(event):
    print ('b4 on_teste_container')
    print (wx.SysErrorCode())
    UIM = UIManager()      
    mwc = interface.get_main_window_controller()
    UIM.create('workpage_controller', mwc.uid)
    print ('a5 on_teste_container')
    
    
def on_new_crossplot(event):
    UIM = UIManager()      
    mwc = interface.get_main_window_controller()

    """
    # Log-Log
    xlim = (0.01, 100.0)
    ylim = (0.01, 100.0)  
    x_scale = 1
    y_scale = 1

    cpc = UIM.create('crossplot_controller', mwc.uid, 
                     xlim=xlim, ylim=ylim, x_scale=x_scale, 
                     y_scale=y_scale
    )

    """

    """
    # Lin-Lin
    xlim = (0.0, 1000.0)
    ylim = (0.0, 1000.0)      
    x_scale = 0
    y_scale = 0
    y_major_grid_lines = 250.0
    y_minor_grid_lines = 50.0
   
    cpc = UIM.create('crossplot_controller', mwc.uid, 
                     xlim=xlim, ylim=ylim, x_scale=x_scale, 
                     scale_lines=10,
                     y_scale=y_scale,
                     y_major_grid_lines=y_major_grid_lines,
                     y_minor_grid_lines=y_minor_grid_lines,
                     y_scale_lines=10
    )
    """
    
    
    """
    # Log-Lin
    xlim = (0.01, 100.0)
    ylim = (0.0, 1000.0)  
    x_scale = 1
    y_scale = 0
    y_major_grid_lines = 250.0
    y_minor_grid_lines = 50.0
    
    cpc = UIM.create('crossplot_controller', mwc.uid, 
                     xlim=xlim, ylim=ylim, x_scale=x_scale, 
                     y_scale=y_scale,
                     y_major_grid_lines=y_major_grid_lines,
                     y_minor_grid_lines=y_minor_grid_lines,
                     y_scale_lines=10
    )

    """
    
#    """
    # Lin-Log
#    xlim = (0.0, 1000.0) 
#    ylim = (0.01, 100.0)
#    x_scale = 0
#    y_scale = 1

    UIM.create('crossplot_controller', mwc.uid)
#                     xlim=xlim, ylim=ylim, x_scale=x_scale, scale_lines=10, 
#                     y_scale=y_scale,
#                     x_label= 'X axis', y_label= 'Y axis', title='Title' 
#    )

#    """    
    
    
#    canvas = cpc.view.crossplot_panel.canvas
    
#    base_axes = canvas.base_axes
    
#    print ('base_axes.get_xticklabels:', 
#           base_axes.xaxis.get_ticklabels(minor=False, which=None)
#    )
    
    
    
#    base_axes.set_ylim(ylim)
#    base_axes.set_yscale('log')

#    plot_axes = canvas.plot_axes
#    plot_axes.set_ylim(ylim)
#    plot_axes.set_yscale('log')
#    plot_axes.set_xlim(xlim)

    #def scatter(self, x, y, s=None, c=None, marker=None, cmap=None, norm=None,
    #    vmin=None, vmax=None, alpha=None, linewidths=None,
    #    verts=None, edgecolors=None,
    #    **kwargs):

#    canvas.draw()



    
    """
    OM = ObjectManager() 
    options = OrderedDict()
    partitions = OrderedDict()
    '''
    for inv in OM.list('inversion'):
        for index in OM.list('index_curve', inv.uid):
            options[index.get_friendly_name()] = index.uid
        for invpar in OM.list('inversion_parameter', inv.uid):
            options[invpar.get_friendly_name()] = invpar.uid 
    '''        
    for well in OM.list('well'):
        #for index in OM.list('index_curve', well.uid):
        #    options[index.get_friendly_name()] = index.uid
        for log in OM.list('log', well.uid):
            options[log.get_friendly_name()] = log.uid
        for partition in OM.list('partition', well.uid):
            partitions[partition.get_friendly_name()] = partition.uid
            
    #
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Rock selector')     
    #
    c1 = dlg.view.AddCreateContainer('StaticBox', label='X-axis', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.view.AddChoice(c1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='xaxis', options=options
    ) 
    #
    c2 = dlg.view.AddCreateContainer('StaticBox', label='Y-axis', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    dlg.view.AddChoice(c2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='yaxis', options=options
    )     
    #
    c3 = dlg.view.AddCreateContainer('StaticBox', label='Colorbar', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    options.update(partitions)
    dlg.view.AddChoice(c3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  widget_name='zaxis', options=options
    ) 
    #
    
    dlg.view.SetSize((230, 300))
    result = dlg.view.ShowModal()

    try :
        
        if result == wx.ID_OK:
            results = dlg.get_results()  
    
            if not results.get('xaxis') or not results.get('yaxis'):
                raise Exception('No xaxis or no yaxis.')
            #
            UIM = UIManager()
            root_controller = UIM.get_root_controller()        
            #print 111
            cp_ctrl = UIM.create('crossplot_controller', root_controller.uid)  
            #print 2222
            cpp = cp_ctrl.view
            #print 222
            xaxis_obj = OM.get(results.get('xaxis'))
            yaxis_obj = OM.get(results.get('yaxis'))
            cpp.crossplot_panel.set_xdata(xaxis_obj.data)
            cpp.crossplot_panel.set_xlabel(xaxis_obj.name)
            cpp.crossplot_panel.set_ydata(yaxis_obj.data)
            cpp.crossplot_panel.set_ylabel(yaxis_obj.name)
            #
            #'''
            #print '\n\nzaxis', results.get('zaxis')
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
            else:
                #cpp.crossplot_panel.set_zmode('solid')
                cpp.crossplot_panel.set_zmode('continuous')
            cpp.crossplot_panel.plot()
            cpp.crossplot_panel.draw()        
        
    except Exception as e:
        print 'ERROR:', e
    finally:
        UIM.remove(dlg.uid)

    """
    
    

def on_coding_console(event):
    UIM = UIManager()      
    mwc = interface.get_main_window_controller()
    UIM.create('console_controller', mwc.uid)




def on_import_las(*args):
    wildcard="LAS Files (*.las)|*.las"
    file_dialog = wx.FileDialog(wx.App.Get().GetTopWindow(), 
                                'Choose LAS file to import:', 
                                wildcard=wildcard, 
                                style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
    )
    if file_dialog.ShowModal() != wx.ID_OK:
        file_dialog.Destroy()
        return
    #
    paths = file_dialog.GetPaths()
    try:
        full_filename = paths[0]
    except:
        raise
    finally:
        file_dialog.Destroy()
    #
    las_file = las.open(full_filename, 'r')
    las_file.read()
    #
    UIM = UIManager()
    mwc = interface.get_main_window_controller()
    well_import_ctrl = UIM.create('well_import_frame_controller', mwc.uid)
    well_import_ctrl.Show()
    #
    well_import_ctrl.set_status_bar_text(full_filename)
    well_import_ctrl.set_las_file(las_file)
    #
    


def on_import_odt(event):
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    wildcard="Arquivos ODT (*.wll)|*.wll"
#        self.odt_dir_name = ''
    fdlg = wx.FileDialog(wx.App.Get().GetTopWindow(), 
                         'Escolha o projeto a carregar', 
                         wildcard=wildcard, 
                         style=style
    )
    if fdlg.ShowModal() == wx.ID_OK:
        file_proj = fdlg.GetFilename()
        odt_dir_name = fdlg.GetDirectory()
        fdlg.Destroy()
    else:
        fdlg.Destroy()
        return
    odt_file = odt.open(odt_dir_name, file_proj, 'r')
    hedlg = ODTEditor.Dialog()
#    print odt_file.ndepth
    hedlg.set_header(odt_file.fileheader, odt_file.logheader, odt_file.ndepth)

    if hedlg.ShowModal() == wx.ID_OK:
        OM = ObjectManager()
        odt_file.header = hedlg.get_header()
        print ('header 2\n', odt_file.header)

        names = [line['MNEM'] for line in iter(odt_file.header["C"].values())]
        units = [line['UNIT'] for line in iter(odt_file.header["C"].values())]
        ncurves = len(names)

        # Tentativa de solução não lusitana
        
        PM = ParametersManager.get()
        
        curvetypes = PM.get_all_curvetypes()
        datatypes_ = PM.get_datatypes()
        
        sel_curvetypes = [PM.get_curvetype_from_mnemonic(name) for name in names]
        
        sel_datatypes = []
        for name in names:
            datatype = PM.get_datatype_from_mnemonic(name)
            if not datatype:
                sel_datatypes.append('Log')
            else:
                sel_datatypes.append(datatype)
        
        # """

        isdlg = ImportSelector.Dialog(wx.App.Get().GetTopWindow(), names, units, curvetypes, datatypes_)
        
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
                    PM.vote_for_curvetype(names[i], sel_curvetypes[i])
            
                #if sel_datatypes[i]:
                #    PM.votefordatatype(names[i], sel_datatypes[i])
            
                if sel_datatypes[i] == 'Depth':
                    # print "Importing {} as '{}' with curvetype '{}'".format(names[i], sel_datatypes[i], sel_curvetypes[i])
                    depth = OM.new('depth', data[i], name=names[i], unit=units[i], curvetype=sel_curvetypes[i])
                    OM.add(depth, well.uid)
                
                elif sel_datatypes[i] == 'Log':
                    # print "Importing {} as '{}' with curvetype '{}'".format(names[i], sel_datatypes[i], sel_curvetypes[i])
                    log = OM.new('log', data[i], name=names[i], unit=units[i], curvetype=sel_curvetypes[i])
                    OM.add(log, well.uid)

                
                else:
                    print ("Not importing {} as no datatype matches '{}'".format(names[i], sel_datatypes[i]))
                 
        PM.register_votes()
               
        isdlg.Destroy()

    hedlg.Destroy()




def on_import_lis(*args):
    wildcard="LIS Files (*.lis,*.tif)|*.lis;*.tif"
    file_dialog = wx.FileDialog(wx.App.Get().GetTopWindow(), 
                                'Choose LIS file to import:', 
                                wildcard=wildcard, 
                                style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
    )
    if file_dialog.ShowModal() != wx.ID_OK:
        file_dialog.Destroy()
        return
    #
    paths = file_dialog.GetPaths()
    try:
        full_filename = paths[0]
    except:
        raise
    finally:
        file_dialog.Destroy()
    #
    lis_file = LISFile()
    lis_file.read_file(full_filename)
    print ('FIM READ FILE')
    lis_file.read_physical_records()
    print ('FIM READ PHYSICAL')
    lis_file.read_logical_records()
    print ('FIM READ LOGICAL')   
    #
    UIM = UIManager()
    mwc = interface.get_main_window_controller()
    well_import_ctrl = UIM.create('well_import_frame_controller', mwc.uid)
    well_import_ctrl.Show()
    #
    well_import_ctrl.set_status_bar_text(full_filename)
    well_import_ctrl.set_lis_file(lis_file)
    #


def on_import_dlis(*args):
    wildcard="DLIS Files (*.dlis)|*.dlis"
    file_dialog = wx.FileDialog(wx.App.Get().GetTopWindow(), 
                                'Choose DLIS file to import:', 
                                wildcard=wildcard, 
                                style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
    )
    if file_dialog.ShowModal() != wx.ID_OK:
        file_dialog.Destroy()
        return
    #
    paths = file_dialog.GetPaths()
    try:
        full_filename = paths[0]
    except:
        raise
    finally:
        file_dialog.Destroy()
    #
    dlis_file = DLISFile()
    dlis_file.read(full_filename)
    #
    # dlis.read 
    # From AAA_Dlis main.py
    # t_stop = threading.Event()
    # dlg = MyProgressDialog(filename)
    # t = threading.Thread(target=dlis.read, args=(filename, dlg.update, t_stop))
    
    """
    print ('FIM READ FILE')
    dlis_file.read_physical_records()
    print ('FIM READ PHYSICAL')
    dlis_file.read_logical_records()
    print ('FIM READ LOGICAL')
    """
    
    #
    UIM = UIManager()
    mwc = interface.get_main_window_controller()
    well_import_ctrl = UIM.create('well_import_frame_controller', mwc.uid)
    well_import_ctrl.Show()
    #
    well_import_ctrl.set_status_bar_text(full_filename)
    well_import_ctrl.set_dlis_file(dlis_file)
    #
    
    

def on_import_segy_seis(event):

    raise Exception('Reescrever igual on_import_segy_well_gather')
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
    wells = get_wells_dict()
    if wells is None:
        return
    #   
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
        ctn = dlg.view.AddCreateContainer('BoxSizer', orient=wx.HORIZONTAL)
        #
        ctn_iline_byte = dlg.view.AddCreateContainer('StaticBox', ctn, label='ILine', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_iline_byte, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='iline_byte', initial='9')
        #
        ctn_xline_byte = dlg.view.AddCreateContainer('StaticBox', ctn, label='XLine', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_xline_byte, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='xline_byte', initial='21')        
        #
        ctn_offset_byte = dlg.view.AddCreateContainer('StaticBox', ctn, label='Offset', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_offset_byte, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='offset_byte', initial='37')            
        #
        ctn_where = dlg.view.AddCreateContainer('StaticBox', label='Where', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        #
        ctn_where_iline = dlg.view.AddCreateContainer('StaticBox', ctn_where, label='ILine', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_where_iline, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='iline_number')
        #
        ctn_where_xline = dlg.view.AddCreateContainer('StaticBox', ctn_where, label='XLine', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_where_xline, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='xline_number')
        #
        ctn_wells = dlg.view.AddCreateContainer('StaticBox', label='Well', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddChoice(ctn_wells, proportion=0, flag=wx.EXPAND|wx.TOP, border=5,  widget_name='welluid', options=wells)     
        #
        ctn_gather = dlg.view.AddCreateContainer('StaticBox', label='Well gather name', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        dlg.view.AddTextCtrl(ctn_gather, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='wellgather_name')
        #
        dlg.view.SetSize((460, 500))
        result = dlg.view.ShowModal()
        if result == wx.ID_OK:
            results = dlg.get_results()  
            print (results)
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
            #TODO: Falta datatype abaixo.
            #
            app_utils.load_segy(event, filename, 
                new_obj_name=wellgather_name, 
                comparators_list=comparators, 
                iline_byte=iline_byte, xline_byte=xline_byte, 
                offset_byte=offset_byte, tid='gather', 
                datatype='amplitude', parentuid=welluid
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
        print (e)
        raise
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
    
    segy_file = segy.SEGYFile(os.path.join(dir_name, file_name))
    segy_file.read()
    name = segy_file.filename.rsplit('\\')[-1]
    name = name.split('.')[0]
    

    OM = ObjectManager()     
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
        OM = ObjectManager()   
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
        for partitionuid, propselection in iter(esdlg.get_property_selection().items()):
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
        header = None #well.attributes.get("LASheader", None)
        if header is None:
            header = las.LASWriter.getdefaultheader()
        
        header = las.LASWriter.rebuildwellsection(header, data[0], units[0])
        header = las.LASWriter.rebuildcurvesection(header, names, units)
        
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
                las_file = las.open(os.path.join(las_dir_name, file_name), 'w')
                las_file.header = header
                las_file.data = data
                las_file.headerlayout = las.LASWriter.getprettyheaderlayout(header)
                las_file.write()
            fdlg.Destroy()
        hedlg.Destroy()
    esdlg.Destroy()



def on_new_rocktable(event):
    OM = ObjectManager()
    rocktable_dlg = RockTableEditor.NewRockTableDialog(wx.App.Get().GetTopWindow())
    try:
        if rocktable_dlg.ShowModal() == wx.ID_OK:
#            wx.MessageBox('It was created a partition.')
            name = rocktable_dlg.get_value()
            print ('name', name, type(str(name)), str(name).strip(''), str(name).strip())
            if name == '': name = 'Table'
            rock = OM.new('rocktable', name = name)
#            partition_dlg.Destroy()        
            OM.add(rock)
    except Exception as e:
        print ('ERROR:', str(e))
    finally:
        rocktable_dlg.Destroy()

def on_edit_rocktable(event):
    OM = ObjectManager()
    if not OM.list('rocktable'):
        try:
            wx.MessageBox('Please create a new Rock Table first!')
        except Exception as e:
            print ('ERROR:', str(e))
        finally:
            return
            
    dlg = RockTableEditor.Dialog(wx.App.Get().GetTopWindow())
    dlg.ShowModal()
    dlg.Destroy()
    
    _UIM = UIManager()
    tree_ctrl = _UIM.list('tree_controller')[0]
    tree_ctrl.refresh()


def on_createrock(event): 
    wells = get_wells_dict()
    if wells is None:
        return
    #       
    OM = ObjectManager() 
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Create Rock')
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
        print ('ERROR:', str(e))
    finally:
        UIM.remove(dlg.uid)        
        
    

    

def on_create_synthetic(event):
    wells = get_wells_dict()
    if wells is None:
        return
    #   
    OM = ObjectManager()
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Create Synthetic Log')
    #
    def on_change_well(name, old_value, new_value, **kwargs):
        choice = dlg.view.get_object('indexuid')
        opt = OrderedDict()
        new_well = OM.get(new_value)
        
        for name, obj_uid in new_well.get_friendly_indexes_dict().items():
            opt[name] = obj_uid
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
    synth_type['Ricker'] = 6
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
    ctn_ricker = dlg.view.CreateContainer('BoxSizer', ctn_parms, orient=wx.VERTICAL)
    #
    ctn_ricker_0 = dlg.view.AddCreateContainer('BoxSizer', ctn_ricker, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(ctn_ricker_0, label='Frequency (Hz):', proportion=1, flag=wx.ALIGN_RIGHT)
    dlg.view.AddTextCtrl(ctn_ricker_0, proportion=1, flag=wx.ALIGN_LEFT, widget_name='ricker_freq', initial='1.0')  
    #
    ctn_ricker_1 = dlg.view.AddCreateContainer('BoxSizer', ctn_ricker, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
    dlg.view.AddStaticText(ctn_ricker_1, label='Peak at:', proportion=1, flag=wx.ALIGN_RIGHT)   
    dlg.view.AddTextCtrl(ctn_ricker_1, proportion=1, flag=wx.ALIGN_LEFT, widget_name='ricker_peak')   
    #    
    ctn_ricker.Show(False)
    
    
    def on_change_synth_type(name, old_value, new_value, **kwargs):
        #print '\nchanged_synth_type:', name, old_value, new_value, kwargs
        if old_value in [2, 3, 4, 5]:
            dlg.view.DetachContainer(ctn_chirp)
        elif old_value in [0, 1]:
            dlg.view.DetachContainer(ctn_sin_cos)
        elif old_value == 6:
            dlg.view.DetachContainer(ctn_ricker)    
        #     
        if new_value in [0, 1]:
            dlg.view.AddContainer(ctn_sin_cos, ctn_parms, **flags)
        elif new_value in [2, 3, 4, 5]:    
            dlg.view.AddContainer(ctn_chirp, ctn_parms, **flags)    
        elif new_value == 6:
            dlg.view.AddContainer(ctn_ricker, ctn_parms, **flags)
        #    
        dlg.view.Layout()    
    #
    dlg.view.AddChoice(ctn_synth_type, proportion=0, flag=wx.EXPAND|wx.TOP, 
                       border=5, widget_name='synth_type', options=synth_type
    )
    
    choice_synth_type = dlg.view.get_object('synth_type')    
    choice_synth_type.set_trigger(on_change_synth_type)
    choice_synth_type.set_value(0, True)

    ctn_name = dlg.view.AddCreateContainer('StaticBox', label='Synthetic name:', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_name, proportion=0, flag=wx.EXPAND|wx.TOP, 
                         border=5, widget_name='synth_name', initial='new_synth'
    )
    
    #
    def on_change_synth_name(name, old_value, new_value, **kwargs):
        if new_value == '':
            dlg.view.enable_button(wx.ID_OK, False)
        else:
            dlg.view.enable_button(wx.ID_OK, True)
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
            
#            print (results)
            
            synth_type = results['synth_type']
            welluid = results['welluid']
            indexuid = results['indexuid'] 
            synth_name = results['synth_name']
            index = OM.get(indexuid)
            #
            index_data = index.data#/1000
            
            #
            if synth_type in [0, 1]:
                sin_cos_freq = float(results['sin_cos_freq'])
                sin_cos_amp = float(results['sin_cos_amp'])
                if synth_type == 0:
                    data = sin_cos_amp * np.sin(index_data * 2 * np.pi * sin_cos_freq) 
                elif synth_type == 1:
                    data = sin_cos_amp * np.cos(index_data * 2 * np.pi * sin_cos_freq)  
                    
            elif synth_type in [2, 3, 4, 5]:     
                chirp_f0 = float(results['chirp_f0'])
                chirp_f1 = float(results['chirp_f1'])
                # TODO: make chirp_start not to be necessarily index_data[0]
                chirp_start = float(results['chirp_start'])
                chirp_start_index = (np.abs(index_data-chirp_start)).argmin()
                #
                chirp_end = float(results['chirp_end'])
                chirp_end_index = (np.abs(index_data-chirp_end)).argmin()
                #
                if synth_type == 2:
                    method = 'linear'     
                elif synth_type == 3:
                    method = 'quadratic'
                elif synth_type == 4:
                    method = 'logarithmic'
                elif synth_type == 5:
                    method = 'hyperbolic'
                #    
                data = chirp(index_data[chirp_start_index:], 
                             f0=chirp_f0, 
                             f1=chirp_f1, 
                             t1=index_data[chirp_end_index], 
                             method=method
                ) #, phi=0, vertex_zero=True)
                #
                print('\nCreated Chirp:')
                print('method = {}'.format(method))
                print('f0 = {}'.format(chirp_f0))
                print('f1 = {}'.format(chirp_f1))
                print('t0 = {}'.format(index_data[chirp_start_index]))
                print('t1 = {}'.format(index_data[chirp_end_index]))
                print('data len: {}'.format(len(data)))
                print('original index_data len: {}'.format(len(index_data)))
                print()
                #
            elif synth_type == 6:
                ricker_freq = float(results['ricker_freq'])
                ricker_peak = float(results['ricker_peak'])
                ricker_peak = ricker_peak/1000.0
                data = get_synthetic_ricker(ricker_freq, ricker_peak, index_data)[1]
                print (data.shape)
                print ('\n\nDATA RICKER:', type(data), data.dtype)
                
                print (data.shape)
                print (data)
            #
            print('\n\nfinalizando a criacao...')
            print(indexuid)
            curve_set_uid = OM._getparentuid(indexuid)       
            print(curve_set_uid)
            log = OM.new('log',
                         data, 
                         name=synth_name, 
                         unit='amplitude', 
                         datatype='SYNTHETIC'
            )
            
            ret = OM.add(log, curve_set_uid)
            print(ret)
            
            log._create_data_index_map([indexuid])
            
            
    except Exception as e:
        print ('ERROR:', str(e))
    finally:
        del wait
        del disableAll
        UIM.remove(dlg.uid)
    


def on_create_model(event):
    wells = get_wells_dict()
    if wells is None:
        return
    #        
    OM = ObjectManager() 
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Create 2/3 layers model')
    #
    def on_change_well(name, old_value, new_value, **kwargs):
        choice = dlg.view.get_object('indexuid')
        opt = OrderedDict()
        new_well = OM.get(new_value)
        for name, obj_uid in new_well.get_friendly_indexes_dict().items():
            opt[name] = obj_uid
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
    ctn_layer_1 = dlg.view.AddCreateContainer('StaticBox', label='Layer 1', orient=wx.HORIZONTAL)
    #
    ctn_start1 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_1, label='Start', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_start1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='start1')
    #
    ctn_vp1 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_1, label='Vp(m/s)', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_vp1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='vp1', initial=2645.0)
    #
    ctn_vs1 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_1, label='Vs(m/s)', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_vs1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='vs1', initial=1170.0)      
    #
    ctn_rho1 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_1, label='Rho(g/cm3)', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_rho1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='rho1', initial=2.29)
    #    
    ctn_q1 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_1, label='Q', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_q1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='q1', initial=2000.0)            
    #   
    #
    ctn_layer_2 = dlg.view.AddCreateContainer('StaticBox', label='Layer 2', orient=wx.HORIZONTAL)
    #
    ctn_start2 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_2, label='Start', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_start2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='start2', initial=100.0)  
    #
    ctn_vp2 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_2, label='Vp(m/s)', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_vp2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='vp2', initial=2780.0)
    #
    ctn_vs2 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_2, label='Vs(m/s)', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_vs2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='vs2', initial=1665.0)      
    #
    ctn_rho2 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_2, label='Rho(g/cm3)', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_rho2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='rho2', initial=2.08)           
    #    
    ctn_q2 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_2, label='Q', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_q2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='q2', initial=100.0)  
    #
    ctn_layer_3 = dlg.view.AddCreateContainer('StaticBox', label='Layer 3', orient=wx.HORIZONTAL)
    #
    ctn_start3 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_3, label='Start', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_start3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='start3', initial=200.0)       
    #
    ctn_vp3 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_3, label='Vp(m/s)', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_vp3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='vp3', initial=2645.0)
    #
    ctn_vs3 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_3, label='Vs(m/s)', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_vs3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='vs3', initial=1170.0)        
    #
    ctn_rho3 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_3, label='Rho(g/cm3)', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_rho3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='rho3', initial=2.29)          
    #    
    ctn_q3 = dlg.view.AddCreateContainer('StaticBox', ctn_layer_3, label='Q', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddTextCtrl(ctn_q3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='q3', initial=2000.0)   
    #    
    dlg.view.SetSize((650, 500))
    result = dlg.view.ShowModal()
    try:
        disableAll = wx.WindowDisabler()
        wait = wx.BusyInfo("Creating model. Wait...")
        if result == wx.ID_OK:
            results = dlg.get_results()  
            #print results 
            
            indexuid = results.get('indexuid')
            welluid = results.get('welluid')
            
            start1 = results.get('start1')
            vp1 = results.get('vp1')
            vs1 = results.get('vs1')
            rho1 = results.get('rho1')
            q1 = results.get('q1')
            
            start2 = results.get('start2')
            vp2 = results.get('vp2')
            vs2 = results.get('vs2')
            rho2 = results.get('rho2')            
            q2 = results.get('q2')
            
            start3 = results.get('start3')
            vp3 = results.get('vp3')
            vs3 = results.get('vs3')
            rho3 = results.get('rho3')
            q3 = results.get('q3')
            
            index = OM.get(indexuid)

            if not start1:
                idx1 = 0
            else:
                start1 = float(start1)
                idx1 = (np.abs(index.data - start1)).argmin()
            
            if not start2:
                wx.MessageBox('Layer 2 start cannot be None.')
                raise Exception('Layer 2 start cannot be None.')
            else:
                start2 = float(start2)
                idx2 = (np.abs(index.data - start2)).argmin()
            
            if not start3:
                idx3 = None
            else:
                start3 = float(start3)
                idx3 = (np.abs(index.data - start3)).argmin()
                
                
            layer1 = (idx1, idx2)    
            if idx3 is not None:
                layer2 = (idx2, idx3) 
                layer3 = (idx3, len(index.data))
            else:
                layer2 = (idx2, len(index.data))
                layer3 = None
                
                
            try:    
                vp1 = float(vp1)
            except:
                vp1 = np.nan
            try:    
                vs1 = float(vs1)
            except:
                vs1 = np.nan
            try:    
                rho1 = float(rho1)
            except:
                rho1 = np.nan          
            try:    
                q1 = float(q1)
            except:
                q1 = np.nan   
            #
            try:    
                vp2 = float(vp2)
            except:
                vp2 = np.nan
            try:    
                vs2 = float(vs2)
            except:
                vs2 = np.nan
            try:    
                rho2 = float(rho2)
            except:
                rho2 = np.nan          
            try:    
                q2 = float(q2)
            except:
                q2 = np.nan   
            #  
            try:    
                vp3 = float(vp3)
            except:
                vp3 = np.nan
            try:    
                vs3 = float(vs3)
            except:
                vs3 = np.nan
            try:    
                rho3 = float(rho3)
            except:
                rho3 = np.nan          
            try:    
                q3 = float(q3)
            except:
                q3 = np.nan   
            #  

            if layer3:
                try:    
                    vp3 = float(vp3)
                except:
                    vp3 = np.nan
                try:    
                    vs3 = float(vs3)
                except:
                    vs3 = np.nan
                try:    
                    rho3 = float(rho3)
                except:
                    rho3 = np.nan          
                try:    
                    q3 = float(q3)
                except:
                    q3 = np.nan   
             
            vp = []
            vs = []
            rho = []
            q = []
            
            if index.data[layer1[0]] == 0.0:
                calc_owt = True    
                owt = [0.0]
            else:
                calc_owt = False
            
            
            for idx in range(len(index.data)):
                if idx >= layer1[0] and idx < layer1[1]:
                    #print '\nidx:', idx, 'layer 1'
                    vp.append(vp1)
                    vs.append(vs1)
                    rho.append(rho1)
                    q.append(q1)
                elif idx >= layer2[0] and idx < layer2[1]:
                    #print '\nidx:', idx, 'layer 2'
                    vp.append(vp2)
                    vs.append(vs2)
                    rho.append(rho2)
                    q.append(q2)
                elif layer3 and idx >= layer3[0] and idx < layer3[1]:
                    #print 'idx:', idx, 'layer 3'
                    vp.append(vp3)
                    vs.append(vs3)
                    rho.append(rho3)
                    q.append(q3)
                else:
                    #print 'idx:', idx, 'layer NONE'
                    vp.append(np.nan)
                    vs.append(np.nan)
                    rho.append(np.nan)
                    q.append(np.nan)

                if calc_owt and idx != 0 and vp[idx-1] != np.nan:
                    diff_prof = index.data[idx] - index.data[idx-1]
                    value = (float(diff_prof) / vp[idx-1]) * 1000.0
                    value = owt[idx-1] + value
                    owt.append(value)


            curve_set = index.get_curve_set()
            logs = []
            
            if vp:
                vp = np.array(vp)
                if np.count_nonzero(~np.isnan(vp)):
                    log = OM.new('log', vp, name='Vp_model', unit='m/s', datatype='Velocity')
                    OM.add(log, curve_set.uid)     
                    logs.append(log)
            if vs:
                vs = np.array(vs)
                if np.count_nonzero(~np.isnan(vs)):
                    log = OM.new('log', vs, name='Vs_model', unit='m/s', datatype='ShearVel')
                    OM.add(log, curve_set.uid)  
                    logs.append(log)
            if rho:
                rho = np.array(rho)
                if np.count_nonzero(~np.isnan(rho)):
                    log = OM.new('log', rho, name='Rho_model', unit='g/cm3', datatype='Density')
                    OM.add(log, curve_set.uid)    
                    logs.append(log)
            if q:
                q = np.array(q)
                if np.count_nonzero(~np.isnan(q)):
                    log = OM.new('log', q, name='Q_model', unit=None, datatype='QFactor')
                    OM.add(log, curve_set.uid)  
                    logs.append(log)
            
            if calc_owt:        
                owt = np.array(owt)       
                twt = owt * 2.0
            #    
            owt_index = OM.new('data_index', owt, name='One Way Time', unit='ms', datatype='TIME')
            OM.add(owt_index, curve_set.uid)  
            #
            twt_index = OM.new('data_index', twt, name='Two Way Time', unit='ms', datatype='TWT')
            OM.add(twt_index, curve_set.uid)  
            #     
            for log in logs:
                log._create_data_index_map([index.uid, owt_index.uid, twt_index.uid])
            
            #      
    except Exception as e:
        print ('ERROR [on_create_model]:', str(e))
        raise
    finally:
        del wait
        del disableAll
        UIM.remove(dlg.uid)



def on_time_depth(event):
    wells = get_wells_dict()
    if wells is None:
        return
    #   
    OM = ObjectManager() 
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Time Depth')
    #
    def on_change_well(name, old_value, new_value, **kwargs):
        choice = dlg.view.get_object('vpuid')
        opt = OrderedDict()
        logs = OM.list('log', new_value)
        for log in logs:
            if log.datatype == 'Velocity':
                opt[log.name] = log.uid             
        choice.set_options(opt)
        choice.set_value(0, True)
    #    
    c1 = dlg.view.AddCreateContainer('StaticBox', label='Well', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddChoice(c1, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='welluid', options=wells)
    choice_well = dlg.view.get_object('welluid')
    choice_well.set_trigger(on_change_well) 
    #
    c2 = dlg.view.AddCreateContainer('StaticBox', label='Vp', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.view.AddChoice(c2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='vpuid')  
    #
    choice_well.set_value(0, True)
    #       
    dlg.view.SetSize((250, 350))
    result = dlg.view.ShowModal()
    try:
        disableAll = wx.WindowDisabler()
        wait = wx.BusyInfo("Creating model. Wait...")
        if result == wx.ID_OK:
            results = dlg.get_results()  
            #print results   
            well_uid = results['welluid']
            vp_uid = results['vpuid']
            well = OM.get(well_uid)
            vp = OM.get(vp_uid)
            vp_index_set = OM.get(vp.index_set_uid)
            md = vp_index_set.get_z_axis_indexes_by_type('MD')[0]
            #
            print (len(vp.data), len(md.data))
            #
            
    #
    except Exception as e:
        print ('ERROR [on_time_depth]:', str(e))
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


    OM = ObjectManager()
    
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
        


##############################################################################################
##############################################################################################
##############################################################################################
#    
# Trabalho da Roseane - Abaixo 
# 07/07/2018    
#

def _get_phi_K_objects(well_uid):
    OM = ObjectManager()    
    #well_uid = ('well', 0) 

    phi_log_objects = OM.exec_query('log', well_uid, 'name=Phi')       
    phi_log_obj = phi_log_objects[0]

    K_log_objects = OM.exec_query('log', well_uid, 'name=K')       
    K_log_obj = K_log_objects[0]
                 
    #phi_data = uom.convert(phi_log_obj.data, phi_log_obj.unit, new_unit_name)
    return (phi_log_obj, K_log_obj)




def create_winland_xplot(event):
    UIM = UIManager()      
    mwc = interface.get_main_window_controller()

    well_uid = ('well', 0)

    # Lin-Log
    xlim = (0, 40.0)
    ylim = (0.0001, 10000.0)
    x_scale = 0
    y_scale = 1

    cpc = UIM.create('crossplot_controller', mwc.uid, 
                     xlim=xlim, ylim=ylim, x_scale=x_scale, scale_lines=8, 
                     y_scale=y_scale,
                     x_label= 'Porosity (Phie %)', 
                     y_label= 'Permeability (md)', 
                     title='Winland Crossplot' 
    )
  
    canvas = cpc.view.crossplot_panel.canvas
    
    
    logK = {}
    
    r = [(0.1, 'olive'),
         (0.5, 'blue'),
         (1.0, 'black'),
         (2.0, 'green'),
         (5.0, 'yellow'),
         (10.0, 'red')
    ]
    max_val = 40
    
    x_data = [idx+1 for idx in range(max_val)]
 
    for raio, _ in r:
        values = []
        for idx in range(max_val):
            val = 2.433 * np.log10(raio) - 0.664 + 0.869 * np.log10(idx+1)  
            values.append(val)
        logK[raio] = np.array(values)
        
    for raio, color in r:
        canvas.append_artist('Line2D', x_data, np.power(10, logK[raio]), 
                         linewidth=2, color=color
        )
    
    phi_log_obj, K_log_obj = _get_phi_K_objects(well_uid)

    canvas.append_artist('scatter', phi_log_obj.data*100, K_log_obj.data,
                         marker='^')   
    
    canvas.base_axes.set_xlim(xlim)
    canvas.base_axes.set_ylim(ylim)
    
    canvas.draw()    



def create_poro_perm_xplot(event):
    UIM = UIManager()      
    mwc = interface.get_main_window_controller()

    well_uid = ('well', 0)

    # Lin-Log
    xlim = (0, 40.0)
    ylim = (0.0001, 10000.0)
    x_scale = 0
    y_scale = 1

    cpc = UIM.create('crossplot_controller', mwc.uid, 
                     xlim=xlim, ylim=ylim, x_scale=x_scale, scale_lines=8, 
                     y_scale=y_scale,
                     x_label= 'Porosity (%)', 
                     y_label= 'Permeability (md)', title='Porosity-Permeability Crossplot' 
    )
  
    canvas = cpc.view.crossplot_panel.canvas
    
    phi_log_obj, K_log_obj = _get_phi_K_objects(well_uid)


    x = phi_log_obj.data*100
    y = K_log_obj.data

 


    def exponenial_func(x, a, b, c):
        return a*np.exp(-b*x)+c

    from scipy.optimize import curve_fit
    popt, pcov = curve_fit(exponenial_func, x, y, p0=(1, 1e-6, 1))
    
    xfit = np.linspace(xlim[0], xlim[1], 100)
    yfit = exponenial_func(xfit, *popt)
    
    canvas.append_artist('scatter', x, y)         

    canvas.append_artist('Line2D', xfit, yfit, 
                         linewidth=2, color='red'
    )   

    canvas.base_axes.set_xlim(xlim)
    canvas.base_axes.set_ylim(ylim)
    canvas.draw() 


    """
    from sklearn.linear_model import LinearRegression

    model = LinearRegression(fit_intercept=True)
    model.fit(x[:, np.newaxis], y)

    xfit = np.linspace(xlim[0], xlim[1])
    yfit = model.predict(xfit[:, np.newaxis])
    
    canvas.append_artist('Line2D', xfit, yfit, 
                         linewidth=2, color='red'
    )                     
    """
    

def create_SMLP_xplot(event):
    
    UIM = UIManager()      
    mwc = interface.get_main_window_controller()   
    
    well_uid = ('well', 0)
    
    # Lin-Lin
    xlim = (0.0, 1.0)
    ylim = (0.0, 1.0)      
    x_scale = 0
    y_scale = 0
   
    cpc = UIM.create('crossplot_controller', mwc.uid, 
                     xlim=xlim, ylim=ylim, x_scale=x_scale, 
                     scale_lines=10,
                     y_scale=y_scale,
                     y_scale_lines=10,
                     title='Stratigraphic Modified Lorenz Plot (SMLP)',
                     x_label='Percent Storage Capacity (%PHIH)',
                     y_label='Percent Flow Capacity (%KH)'
    )
    
    canvas = cpc.view.crossplot_panel.canvas
    phi_log_obj, K_log_obj = _get_phi_K_objects(well_uid)
    
    phiH = phi_log_obj.data * 10
    phiH_perc = phiH / 3.4
    
    kH = K_log_obj.data * 0.1
    kH_perc = kH / 90.09
    
    canvas.append_artist('scatter', phiH_perc, kH_perc) 
 
    canvas.base_axes.set_xlim(xlim)
    canvas.base_axes.set_ylim(ylim)
    canvas.draw()    


def create_MLP_xplot(event):
    
    UIM = UIManager()      
    mwc = interface.get_main_window_controller()   
    
    well_uid = ('well', 0)
    
    # Lin-Lin
    xlim = (0.0, 1.0)
    ylim = (0.0, 1.0)      
    x_scale = 0
    y_scale = 0
   
    cpc = UIM.create('crossplot_controller', mwc.uid, 
                     xlim=xlim, ylim=ylim, x_scale=x_scale, 
                     scale_lines=10,
                     y_scale=y_scale,
                     y_scale_lines=10,
                     title='Modified Lorenz Plot (MLP)',
                     x_label='Phi PAD',
                     y_label='K PAD'
    )
    
    canvas = cpc.view.crossplot_panel.canvas
    phi_log_obj, K_log_obj = _get_phi_K_objects(well_uid)
    
    phiH = phi_log_obj.data * 10
    
    phiH_acum = [phiH[0]]
    for idx in range(1, len(phiH)):
        phiH_acum.append(phiH[idx]+phiH_acum[idx-1])
        print ('phiH_acum[{}] = {}'.format(str(idx), str(phiH[idx]+phiH_acum[idx-1])))
        
    kH = K_log_obj.data * 0.1
    kH_acum = [kH[0]]
    for idx in range(1, len(kH)):
        kH_acum.append(kH[idx]+kH_acum[idx-1])
        print ('phiH_acum[{}] = {}'.format(str(idx), str(kH[idx]+kH_acum[idx-1])))
        
    print ('\n')
    print ('', type(phiH_acum))    
        
    phiH_acum = np.asarray(phiH_acum)    
    kH_acum = np.asarray(kH_acum)
    
    phiH_PAD = phiH_acum/493.02
    kH_PAD = kH_acum/2274.41
    
    canvas.append_artist('scatter', phiH_PAD, kH_PAD) 
 
    canvas.base_axes.set_xlim(xlim)
    canvas.base_axes.set_ylim(ylim)
    canvas.draw()    
  

def create_Depth_vs_kHAcum_xplot(event):
    OM = ObjectManager()
    UIM = UIManager()      
    mwc = interface.get_main_window_controller()   
    
    well_uid = ('well', 0)

    data_index = OM.list('data_index', well_uid)[0]
    
    # Lin-Lin
    xlim = (0.0, 2500.0)
    ylim = (2290.0, 2235.0)      
    x_scale = 0
    y_scale = 0
   
    cpc = UIM.create('crossplot_controller', mwc.uid, 
                     xlim=xlim, ylim=ylim, x_scale=x_scale, 
                     scale_lines=5,
                     y_scale=y_scale,
                     y_scale_lines=11,
                     title='Flow capacity (KH) accumulated X Depth',
                     x_label= 'KH Accumulated', y_label= 'Depth', 
    )
    
    canvas = cpc.view.crossplot_panel.canvas
    phi_log_obj, K_log_obj = _get_phi_K_objects(well_uid)
      
    kH = K_log_obj.data * 0.1
    kH_acum = [kH[0]]
    for idx in range(1, len(kH)):
        kH_acum.append(kH[idx]+kH_acum[idx-1])

    kH_acum = np.asarray(kH_acum)

    canvas.append_artist('scatter', kH_acum, data_index.data) 

  
    canvas.base_axes.set_xlim(xlim)
    canvas.base_axes.set_ylim(ylim)
    canvas.draw()    




def calc_logs(event):
    
    well_uid = ('well', 0)
    
    phi_log_obj, K_log_obj = _get_phi_K_objects(well_uid)
    phiH = phi_log_obj.data * 10
    
    phiH_acum = [phiH[0]]
    for idx in range(1, len(phiH)):
        phiH_acum.append(phiH[idx]+phiH_acum[idx-1])
    phiH_acum = np.asarray(phiH_acum)  
        
    kH = K_log_obj.data * 0.1
    kH_acum = [kH[0]]
    for idx in range(1, len(kH)):
        kH_acum.append(kH[idx]+kH_acum[idx-1]) 
    kH_acum = np.asarray(kH_acum)
    
    
    phiH_PAD = phiH_acum/493.02
    kH_PAD = kH_acum/2274.41
    


def on_load_teste_2019(event):
    
    try:
        OM = ObjectManager()
        
        #data = np.arange(100000000).reshape(100, 100, 100, 100)
        data = np.arange(100000).reshape(10, 10, 10, 10, 10)
    
        seismic = OM.new('seismic', 
                     data, 
                     name='Sismica', 
                     unit='amplitude', 
                     datatype='seismic'
        )
        OM.add(seismic)
        
    
    #    """    
        
        #
        i_line_index = OM.new('data_index', 
                       #np.arange(100), 
                       np.arange(10), 
                       name='I_line', 
                       unit=None, 
                       datatype='I_LINE'
        )
        b = OM.add(i_line_index, seismic.uid)
        print('i_line_index:', b)
        #
        x_line_index = OM.new('data_index', 
                       #np.arange(100), 
                       np.arange(10), 
                       name='X_line', 
                       unit=None, 
                       datatype='X_LINE'
        )
        b = OM.add(x_line_index, seismic.uid)
        print('x_line_index:', b)
        #
        offset_index = OM.new('data_index', 
                       #np.arange(100), 
                       np.arange(10), 
                       name='Offset', 
                       unit='m', 
                       datatype='OFFSET'
        )
        b = OM.add(offset_index, seismic.uid)
        print('offset_index:', b)
        #
        freq_index = OM.new('data_index', 
                       #np.arange(100), 
                       np.arange(10), 
                       name='Frequency', 
                       unit='Hz', 
                       datatype='FREQUENCY'
        )
        b = OM.add(freq_index, seismic.uid)
        print('freq_index:', b)
        #
        time_index = OM.new('data_index', 
                       #np.arange(100), 
                       np.arange(10), 
                       name='Time', 
                       unit='time', 
                       datatype='TWT'
        )
        b = OM.add(time_index, seismic.uid)
        print('time_index:', b)
        #    
        prof_index = OM.new('data_index', 
                       #np.arange(100), 
                       np.arange(0, -10, -1), 
                       name='Depth', 
                       unit='m', 
                       datatype='TVD'
        )
        b = OM.add(prof_index, seismic.uid)
        #
        print('prof_index:', b)
        #    
        seismic._create_data_index_map(
                                        [i_line_index.uid],
                                        [x_line_index.uid],
                                        [offset_index.uid],
                                        [freq_index.uid],
                                        [time_index.uid, prof_index.uid]
        )
        
    #    """
    except Exception as e:
        print('\nERROU!!!', e)
        raise

'''

def on_test_partition(self, event):
    well = self.OM.new('well', name='teste_particao') 
    self.OM.add(well)
    data = np.arange(0, 550, 50)
    depth = self.OM.new('depth', data, name='depth', unit='m', datatype='Depth')
    self.OM.add(depth, well.uid)
    
    #data = np.array([12, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14])
    #booldata, codes = datatypes.DataTypes.Partition.getfromlog(data)
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
            
        poco_densidade  = str("C:\\Users\\Adriano\\Documents\\GitHub\\AVO_INVTRACE_NEW\\data\\poco_0210_densidade.dat")
        poco_vp         = str("C:\\Users\\Adriano\\Documents\\GitHub\\AVO_INVTRACE_NEW\\data\\poco_0210_vp.dat")
        poco_vs         = str("C:\\Users\\Adriano\\Documents\\GitHub\\AVO_INVTRACE_NEW\\data\\poco_0210_vs.dat")
        
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
        

