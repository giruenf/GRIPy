# -*- coding: utf-8 -*-

from collections import OrderedDict

import numpy as np
import wx

#from om.manager import ObjectManager
#from ui.uimanager import UIManager
from classes.om import ObjectManager
from classes.ui import UIManager
from algo.spectral.Spectral import STFT, WaveletTransform, MorletWavelet, PaulWavelet, DOGWavelet, RickerWavelet
from basic.uom.uom import uom


SPECGRAM_TYPES = OrderedDict()
SPECGRAM_TYPES['Power Spectral Density'] = 'PSD'
SPECGRAM_TYPES['Magnitude'] = 'MAGNITUDE'
SPECGRAM_TYPES['Phase (no unwrapping)'] = 'ANGLE'
SPECGRAM_TYPES['Phase (unwrapping)'] = 'PHASE' 

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




def do_STFT(*args, **kwargs):
    toc = kwargs.get('toc')
    if not toc:
        raise Exception('Trabalhando somente com o TrackObjectController.')
    #    
    OM = ObjectManager()
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Short Time Fourier Transform') 
    #
    try:
        ctn_spec_type = dlg.view.AddCreateContainer('StaticBox', 
                                                    label='Spectrogram type', 
                                                    orient=wx.VERTICAL, 
                                                    proportion=0, 
                                                    flag=wx.EXPAND|wx.TOP, 
                                                    border=5
        )
        dlg.view.AddChoice(ctn_spec_type, 
                           proportion=0, 
                           flag=wx.EXPAND|wx.TOP, 
                           border=5,  
                           widget_name='spectrogram_type', 
                           options=SPECGRAM_TYPES
        )     
        #
        ctn_win_size = dlg.view.AddCreateContainer('StaticBox', 
                                                   label='Window size (samples)', 
                                                   orient=wx.VERTICAL, 
                                                   proportion=0, 
                                                   flag=wx.EXPAND|wx.TOP, 
                                                   border=5
        )        
        dlg.view.AddSpinCtrl(ctn_win_size, 
                             proportion=0, 
                             flag=wx.EXPAND, 
                             widget_name='window_size', 
                             max=1024, 
                             initial=256
        )
        #
        ctn_overlap_size = dlg.view.AddCreateContainer('StaticBox', 
                                                       label='Overlap size (samples)', 
                                                       orient=wx.VERTICAL, 
                                                       proportion=0, 
                                                       flag=wx.EXPAND|wx.TOP, 
                                                       border=5
        )
        dlg.view.AddSpinCtrl(ctn_overlap_size, 
                             proportion=0, 
                             flag=wx.EXPAND, 
                             widget_name='noverlap', 
                             max=512, 
                             initial=128
        )
        #
        dlg.view.SetSize((230, 260))
        result = dlg.view.ShowModal()
        #
        if result == wx.ID_OK:
            results = dlg.get_results()   
            if results.get('spectrogram_type'):
                #
                print('\ndo_STFT:', toc.get_data_object_uid())
                #
                di_uid, di_data = toc.get_last_dimension_index()
                data_index = OM.get(di_uid)
                
                
                unit = uom.get_unit(data_index.unit)
                dim = uom.get_unit_dimension(unit.dimension)
    
                print(unit.dimension, dim, dim.name)
                if dim.name == 'time':
                    print('\nConvertendo {} de {} para {}.'.format(dim.name, data_index.unit, 's'))
                    di_data = uom.convert(di_data, data_index.unit, 's')
                    
                elif dim.name == 'length':
                    print('\nConvertendo {} de {} para {}.'.format(dim.name, data_index.unit, 'm'))
                    di_data = uom.convert(di_data, data_index.unit, 'm')
                
                else:
                    print('\nNao converteu')
                # new_data = uom.convert(obj.data, obj.unit, new_unit_name)
                   
                #
                start_value = di_data[0]
                step_value = di_data[1] - di_data[0]
                #
                print('start_value: {} - step_value: {}'.format(start_value, step_value))
                #         
                dm_data = toc.get_filtered_data()
                #
                #STFT(x, window_size, noverlap, time_start, Ts, mode='psd'):    
#                print('start_value, step_value:', start_value, step_value)
 
                spec_type = results.get('spectrogram_type')
                
                stft_data, freq_values, index_values = STFT(dm_data, 
                        results.get('window_size'), 
                        results.get('noverlap'),
                        start_value, step_value, 
                        mode=spec_type
                )
#                freq_values *= 1000
                
                #
#                print ('\n\nRetornou')    
                data_out = np.zeros((len(di_data), len(freq_values)))
                stft_index_step = index_values[1] - index_values[0]
                stft_index_start = index_values[0] - (stft_index_step/2)
                stft_index_end = index_values[-1] + (stft_index_step/2)
                #
#                print('Orig shape:', dm_data.shape)
#                print('Freq Index Shape:', len(freq_values), len(index_values), stft_data.shape)           
#                print('Freqs:', np.nanmin(freq_values), np.nanmax(freq_values))
#                print('Indexes:', index_values)
                #
#                print ('\n\n', stft_index_start, stft_index_end)
                
                for idx, time in enumerate(di_data):
                    if time >= stft_index_start and time < stft_index_end: 
                        stft_index_idx = int((time - stft_index_start) // stft_index_step)
#                        print(idx, time, stft_index_start, stft_index_step, stft_index_idx)
                        
                        data_out[idx] = stft_data[stft_index_idx]
                
                #print '\n\n'
                
                data_out = data_out.T               
                
#                print()
#                print('data_out.shape:', data_out.shape)
#                print()
                
                #
                if spec_type == 'PHASE':
                    spec_type = 'PHASE_UNWRAPPED'
                elif spec_type == 'ANGLE':
                    spec_type = 'PHASE'
                #    

                spectogram = OM.new('spectogram', 
                                    data_out, 
                                    name=toc.get_data_name()+'_STFT',
                                    datatype=results.get('spectrogram_type')
                )
                if not OM.add(spectogram, toc.get_data_object_uid()):
                    msg = 'Object was not added. tid={\'spectogram\'}'
                    raise Exception(msg)   
                #
                freq_index = OM.new('data_index', 
                               freq_values, 
                               name='Frequency', 
                               unit='Hz', 
                               datatype='FREQUENCY'
                )
                if not OM.add(freq_index, spectogram.uid):
                    raise Exception('Frequency Index was not added.') 
                #
                spectogram._create_data_index_map(
                                        [freq_index.uid],
                                        [di_uid]
                )                          
    except Exception as e:
        print ('ERROR:', e)
        #pass
    finally:
        UIM.remove(dlg.uid)        
    


def do_CWT(*args, **kwargs):
    
    toc = kwargs.get('toc')
    if not toc:
        raise Exception('Trabalhando somente com o TrackObjectController.')
    #    
    
#    obj = args[0]
    UIM = UIManager()
    dlg = UIM.create('dialog_controller', title='Continuous Wavelet Transform') 
    #
    try:
        ctn_wavelet = dlg.view.AddCreateContainer('StaticBox', 
                                                  label='Wavelet', 
                                                  orient=wx.VERTICAL, 
                                                  proportion=0, 
                                                  flag=wx.EXPAND|wx.TOP, 
                                                  border=5
        )
        dlg.view.AddChoice(ctn_wavelet, 
                           proportion=0, 
                           flag=wx.EXPAND|wx.TOP, 
                           border=5,  
                           widget_name='wavelet', 
                           options=WAVELET_TYPES
        )     
        #
        ctn_scale_res = dlg.view.AddCreateContainer('StaticBox', 
                                                    label='Scale resolution', 
                                                    orient=wx.VERTICAL, 
                                                    proportion=0, 
                                                    flag=wx.EXPAND|wx.TOP, 
                                                    border=5
        )
        dlg.view.AddTextCtrl(ctn_scale_res, 
                             proportion=0, 
                             flag=wx.EXPAND|wx.TOP, 
                             border=5, 
                             widget_name='dj', 
                             initial='0.125'
        ) 
        #
        dlg.view.SetSize((230, 260))
        result = dlg.view.ShowModal()
        if result == wx.ID_OK:
            results = dlg.get_results()  
            print (results)
            dj = None
            try:
                dj = float(results.get('dj'))
            except:
                pass
            if dj is None:
                return
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
                
             
            # TODO: Rever tudo isso abaixo    
            valid_data = obj.data[np.isfinite(obj.data)]
            valid_index_data = obj.get_indexes().data[np.isfinite(obj.data)]
            
            #
            wt = WaveletTransform(valid_data, 
                                  dj=dj, 
                                  wavelet=func, 
                                  dt=obj.step,
                                  time=valid_index_data
            )
            #
            OM = ObjectManager() 
            seismic = OM.new('scalogram', 
                             wt.wavelet_power, 
                             name=obj.name+'_CWT', 
                             unit='m', 
                             domain='depth', 
                             sample_rate=wt.time[1] - wt.time[0],
                             datum=wt.time[0],
                             samples= len(wt.time),
                             frequencies=wt.fourier_frequencies,
                             periods=wt.fourier_periods,
                             scales=wt.scales
            )                       
            OM.add(seismic)  
            print (wt.wavelet_transform.shape)    
            #
    except Exception:
        pass
    finally:
        UIM.remove(dlg.uid)   
        
        
        
        
        

'''
def teste():
    od = OrderedDict()
    od['A'] = 1
    od['B'] = 2
    od['C'] = 3
    od['D'] = 4
    od['E'] = 5
    return od


def teste2(**kwargs):
    print kwargs
    value = kwargs.get('well_choice')
    value = value * value
    _dict = OrderedDict()
    for i in range(5):
        _dict[str(value+i)] = value+i
    enc_control = DialogPool.get_object('log_choice')
    enc_control.set_value(_dict)    
    
    
def teste3(**kwargs):
    enc_control = DialogPool.get_object('text_ctrl')
    if kwargs.get('well_choice') is None:
        enc_control.set_value(wx.EmptyString)
        return
    else:
        value = kwargs.get('well_choice')
    if kwargs.get('log_choice') is None:    
        enc_control.set_value(value)
    else:
        enc_control.set_value(str(value) + '_' + str(kwargs.get('log_choice')))
        
def teste4(**kwargs):
    enc_control = DialogPool.get_object('stext')
    if kwargs.get('well_choice') is None:
        enc_control.set_value(wx.EmptyString)
        return
    else:
        value = kwargs.get('well_choice')
    if kwargs.get('log_choice') is None:    
        enc_control.set_value(value)
    else:
        enc_control.set_value(str(value) + '_' + str(kwargs.get('log_choice')))



def teste21(**kwargs):
    print '\nteste21:', kwargs
    value = kwargs.get('well_choice')
    value = value * value
    _dict = OrderedDict()
    for i in range(5):
        _dict[str(value+i)] = str(value+i)
    enc_control = DialogPool.get_object('list_box')
    enc_control.set_value(_dict)    
    





if __name__ == '__main__':  
    app = wx.App(False) 
    
    dlg = Dialog(None, title='Teste Dialog', flags=wx.OK|wx.CANCEL)

    container = dlg.AddStaticBoxContainer(label='well_selector', 
                                          orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )   
    
    dlg.AddChoice(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  name='well_choice', initial_values=teste()
    ) 
   
    dlg.AddChoice(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  name='log_choice', listening=(['well_choice'], teste2)
    )      
    dlg.AddTextCtrl(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  name='text_ctrl',
                  initial_values='AAA_initial_values_value',
                  listening=(['well_choice', 'log_choice'], teste3)
    )    
    dlg.AddSpinCtrl(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                    name='spin_ctrl', initial_values=50
    )
    
    dlg.AddStaticText(container, label='AAAAAA', proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.AddStaticText(container, label='BBBBBB', proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    
    dlg.AddListBox(container, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  name='list_box', listening=(['well_choice', 'log_choice'], teste21)
    )  



    c2 = dlg.AddBoxSizerContainer(orient=wx.VERTICAL, proportion=0, 
                                          flag=wx.EXPAND|wx.TOP, border=5
    )        
   # c2.SetBackgroundColour('blue')
    dlg.AddStaticText(c2, label='CCCCCC', proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.AddStaticText(c2, label='DDDDDD', proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.AddChoice(c2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  name='log_choice2', listening=(['well_choice'], teste21)
    )      
    dlg.AddTextCtrl(c2, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, 
                  name='text_ctrl2',
                  initial_values='AAA_initial_values_value',
                  listening=(['well_choice', 'log_choice'], teste31)
    )
    """
    
    """
    c3 = dlg.AddFlexGridSizerContainer(rows=3, cols=2, vgap=0, hgap=0, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.AddChoice(c3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.AddSpinCtrl(c3, proportion=0, flag=wx.EXPAND)
    dlg.AddTextCtrl(c3, proportion=0, flag=wx.EXPAND)
    dlg.AddTextCtrl(c3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.AddStaticText(c3, label='AAAAAA', proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
    dlg.AddTextCtrl(c3, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
   # c3.SetBackgroundColour('red')
    """        
   
    dlg.SetSize((300, 600))
    
    result = dlg.ShowModal()
    if result == wx.ID_OK:
        print 'OK:', dlg.get_results()  
    elif result == wx.ID_CANCEL:          
        print 'CANCEL'
'''    