# -*- coding: utf-8 -*-
import wx
import wx.aui as aui
from trackstitlessplitter import TracksTitlesSplitter
from plotstatusbar import PlotStatusBar
from logplot_base import TrackFigureCanvas
from OM.Manager import ObjectManager    

import UI
import Parms    
        
        
class LogPlot(aui.AuiMDIChildFrame, UI.uimanager.UIObject):
    tid = 'logplot'
    
        
    def __init__(self, parent, well_oid, logplotformat=None, fit=False):         
        self._OM = ObjectManager(self)
        self.well_oid = well_oid
        UI.uimanager.UIObject.__init__(self)
        
        self.logplotformat = None
        well_obj = self._OM.get(('well', self.well_oid))        
        
        title = 'Log Plot: {} [id:{}]'.format(well_obj.name, self.oid)
        aui.AuiMDIChildFrame.__init__(self, parent, -1, title=title)
        
        self._plot_range = None        
        self.set_plot_range('Whole Well')
        
        self._create_toolbar()        
        self.choice_plot_ranges.SetSelection(0)        
        
        self.statusBar = PlotStatusBar(self)
        
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_CLOSE, self._OnDoClose)
        self.ttsplitter = TracksTitlesSplitter(self)     
        
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)        
        self.hbox.Add(self.ttsplitter, 1, flag=wx.EXPAND)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL) 
        self.vbox.Add(self.tb, 0, flag=wx.TOP|wx.EXPAND)
        self.vbox.Add(self.hbox, 1, flag=wx.EXPAND)
        self.vbox.Add(self.statusBar, 0, flag=wx.BOTTOM|wx.EXPAND)
        self.SetSizer(self.vbox)
        self._tracks = []        
        self.fit = fit
        self.Layout()
        # A unica vez que este metodo eh chamado diretamente
        # Deve ser utilizado set_plot_fommat
        self._process_plot_format(logplotformat)
        #c1 = Chronometer()        
        #self.update_depth_limits()
        #c1.end('LogPlot.update_depth_limits()')

    def destroy(self):
        self._destroy_toolbar()
        UI.UIManager.get()._unregister_ui_object(self)

    def add_plot_range(self, depth_min, depth_max, name=None):
        print '\nadd_plot_range', depth_min, depth_max
        if name is None:
            name = 'User Plot Range ' + str(len(UI.UIManager.get().get_well_plot_ranges(self.well_oid)))  
        UI.UIManager.get().add_well_plot_range(self.well_oid, depth_min, depth_max, name) 
        #pos = self.choice_plot_ranges.Append(name)
        #self.choice_plot_ranges.SetSelection(pos)
        self.set_plot_range(name)

    def set_plot_range(self, plot_range_name):
        if self._plot_range is None:
            lim_ = UI.UIManager.get().get_well_plot_ranges(self.well_oid).get(plot_range_name)
            self._plot_range = (plot_range_name, lim_)        
        else:
            self.change_plot_range(plot_range_name)
        
    def change_plot_range(self, plot_range_name):
        _depth_lim = UI.UIManager.get().get_well_plot_ranges(self.well_oid).get(plot_range_name)
        if not self._tracks:
            return    
        if not _depth_lim:
            return
        try:
            min_lim, max_lim = _depth_lim
        except Exception:
            return
        for (_, track_panel) in self._tracks:
            track_panel.set_ylim(_depth_lim)   
        self._plot_range = (plot_range_name, _depth_lim)       
     
    def get_plot_range(self):
        return self._plot_range        
        
    def get_well_uid(self):
        return ('well', self.well_oid)

    def get_panels(self, pos):
        return self._tracks[pos]

    def get_panel_position(self, panel):
        #print type(panel)
        #raise Exception()
        if isinstance(panel, UI.logplot_base.PlotLabelTrack) or \
                    isinstance(panel, UI.logplot_base.PlotLabelTitle):
            panel = panel.parent                
        if not self._tracks:
            return None 
        i = 0
        for (title_panel, track_panel) in self._tracks:
            if title_panel == panel or track_panel == panel:
                return i
            else:
                i += 1
        return None
    
    def get_plot_format(self):     
        return self.logplotformat
            
    def set_plot_fommat(self, logplotformat):
        self._process_plot_format(logplotformat)

    '''
    def create_overview_track(self, width_inches):
        self._overview_track = TrackFigureCanvas(self)
        self._overview_track.set_callback(self.statusBar.SetInfo)
        #width = self._overview_track._inches_to_pixels(width_inches)
        #self._overview_track.SetBackgroundColour('blue')
        #self._overview_track.set_dummy_spines_visibility(True)
        self._overview_track.SetMinSize([40, 100])
        return self._overview_track
    
    def get_overview_track(self):
        return self._overview_track
    '''    
 

###############################################################################
### Processing LogPlotFormat change methods
###############################################################################  

    # TODO: Melhorar isso    
    def _process_plot_format(self, new_lpf):#, first_time=False):
        #print '\nLogPlot._process_plot_format'
        #print new_lpf
        #raise Exception()
        if new_lpf == self.logplotformat:
            return
        if new_lpf is None:
            self.logplotformat = None
            return
            
        #c1 = Chronometer()

        # First time implies in only track inserts, no track updates or removes
        if self.logplotformat is None:
            if new_lpf.get_tracks():
                self.logplotformat = UI.logplotformat.LogPlotFormat()
                for new_track in new_lpf.get_tracks():
                    self.append_track(new_track)
                #raise Exception()    
        else:      
            menor = min(len(self.logplotformat), len(new_lpf))    
            maior = max(len(self.logplotformat), len(new_lpf)) 
             
            for idx in range(menor):
                self.update_track(idx, new_lpf.get_track(idx))
            if menor == maior:
                return               
            if len(self.logplotformat) > len(new_lpf):
                self.remove_tracks(range(menor, maior))
            else:
                for i in range(menor, maior):
                    self.append_track(new_lpf.get_track(i))
                
                


###############################################################################
### Tracks and curves methods
###############################################################################  

    def _get_all_well_curves(self):
        curves = {}
        depth = self._OM.list('depth', self.get_well_uid())[0]
        curves[depth.name] = depth
        for log in self._OM.list('log', self.get_well_uid()):
            curves[log.name]  = log
        for part in self._OM.list('partition', self.get_well_uid()):
            curves[part.name] = part
        return curves   
    

    def append_track(self, track):
        print '\nLogPlot.append_track'
        if self.logplotformat is None:        
            track_pos = 0
        else:
            track_pos = len(self.logplotformat)
        self.insert_track(track_pos, track)


    def insert_track(self, track_pos, track):
        print '\nLogPlot.insert_track', track_pos
        print track
        # First, insert track in the logplotformat
        self.logplotformat.insert_track(track_pos, track)
        # Then, to the visual part        
        kwargs = dict(track.get_values())
        _, y_lim_ = self.get_plot_range() 
        if kwargs and not kwargs.get('ylim'):
            kwargs['ylim'] = y_lim_
        plot_label, track_panel = self.ttsplitter.insert_track(track_pos,
                status_bar_callback = self.statusBar.SetInfo, 
                zoom_callback = self.add_plot_range,
                **kwargs
        )
        # Double click event on Track Title                                    
        plot_label.Bind(wx.EVT_LEFT_DCLICK, self._OnTrackTitleActivate)
        # All the panel are placed in _tracks list as tuples 
        self._tracks.insert(track_pos, (plot_label, track_panel))
        # plot_curves takes care of Curves visual part
        self.plot_curves(track_pos)#, track.get_curves())
                                 


    def update_track(self, track_pos, new_track):   
        print '\nLogPlot.update_track', track_pos
        print new_track
        old_track = self.logplotformat.get_track(track_pos)
        if old_track == new_track:
            return
        
        self.logplotformat.get_tracks()[track_pos] = new_track
        
        if old_track.get_values() != new_track.get_values():
            
            kwargs = dict(new_track.get_values())    
            plot_label, track_panel = self.get_panels(track_pos)
            #print 'LogPlot.udpate_track values: ', track_pos
            if kwargs.get('track_name') is not None:
                plot_label.update_title(text=kwargs.get('track_name'))
            else:

                plot_label.update_title(text=str(track_pos+1))
            #title_panel.set_track_title_text(track_pos, kwargs.get('track_name'))  
            ###
            if kwargs.get('show_track') is not None:
                if kwargs.get('show_track') is True:
                    self.show_track(track_pos)
                else:    
                    self.hide_track(track_pos)
                del kwargs['show_track']
            # Tratar kwargs['overview']
            if kwargs.get('overview') is not None:
                del kwargs['overview']
            # Tratar kwargs['width']
            if kwargs.get('width') is not None:
                del kwargs['width']    
            ###        
            print '\ntrack_panel.update_properties({})'.format(kwargs)    
            track_panel.update_properties(**kwargs)
        else:
            print '\nOLD AND NEW ARE EQUALS\n'
            print old_track
        self.plot_curves(track_pos, old_track.get_curves())    
 


    def show_track(self, track_pos):
        title_panel, track_panel = self.get_panels(track_pos)
        if not title_panel.IsShown():
            title_panel.Show()
            title_panel.GetParent()._SizeComponent()
        if not track_panel.IsShown():
            track_panel.Show()            
            track_panel.GetParent()._SizeComponent()

    def hide_track(self, track_pos):
        title_panel, track_panel = self.get_panels(track_pos)
        if title_panel.IsShown():
            title_panel.Hide()
            title_panel.GetParent()._SizeComponent()
        if track_panel.IsShown():
            track_panel.Hide()  
            track_panel.GetParent()._SizeComponent()
       
    def remove_tracks(self, indexes_list):
        print '\nLogPlot.remove_tracks({})'.format(indexes_list)
        self.logplotformat.remove_tracks_indexes(indexes_list)
        self.ttsplitter.remove_tracks(indexes_list)


    # Just the visual part
    def plot_curves(self, track_pos, old_curves=None):
        print  '\nLogPlot.plot_curves'
        track = self.logplotformat.get_track(track_pos)
        if not track.get_curves():
            if not old_curves:
                return
        track = self.logplotformat.get_track(track_pos)
        track_valid_curves = []
        if track.get_curves():
            for curve in track.get_curves():
                curve = self._check_curve(curve)
                if curve is not None:
                    track_valid_curves.append(curve)        
        old_valid_curves = []
        if old_curves:        
            for curve in old_curves:
                curve = self._check_curve(curve)
                if curve is not None:
                    old_valid_curves.append(curve)
        if old_valid_curves == track_valid_curves:
            return
        if not old_valid_curves:
            old_len = 0
        else:
            old_len = len(old_valid_curves)
        menor = min(old_len, len(track_valid_curves))    
        maior = max(old_len, len(track_valid_curves))                
        
        for curve_pos in range(menor):
            print 'updating ', track_pos, curve_pos
            self.update_curve(track_pos, curve_pos)
        if menor == maior:
            return
        if old_len > len(track_valid_curves):    
            deleted_curves = (curve for curve in old_valid_curves if not curve in track_valid_curves) 
            deleted_idx = []
            for i, curve in enumerate(deleted_curves):
                if curve is not None:                    
                    idx = old_valid_curves.index(curve)
                    deleted_idx.append(idx)
            print 'deleting ', track_pos, deleted_idx       
            self.remove_track_curves(track_pos, deleted_idx)
        else:
            print 'appending ', track_pos, range(menor, maior) 
            self.append_curves(track_pos, track_valid_curves[menor:maior])
        return
            

    def update_curve(self, track_pos, curve_pos):
        print  '\nLogPlot.update_curve'
        curve = self.logplotformat.get_track(track_pos).get_curve(curve_pos)
        curve = self._check_curve(curve)
        if curve is None:
            return
        plot_label, track_panel = self.get_panels(track_pos)
        depth_obj = self._OM.list('depth', self.get_well_uid())[0]
        y_axis = depth_obj.data
        curve_name = curve.get_value('curve_name')

        if self._get_all_well_curves().get(curve_name) is not None:
            if self._get_all_well_curves().get(curve_name).tid == 'partition':
                partition = self._get_all_well_curves().get(curve_name)
                curve.set_value('point_plotting', 'Partition')
                part_map = {}
                for part in partition.list('part'): 
                    part_map[part.code] = (part.color, part.data)
                x_axis = part_map
                unit = None
            else:  
                x_axis = self._get_all_well_curves().get(curve_name).data
                unit = self._get_all_well_curves().get(curve_name).unit
            plot_label.update_track(curve_pos, name=curve.get_value('curve_name'), 
                                tracktype=curve.get_value('point_plotting'),
                                unit = unit,
                                xmin=curve.get_value('left_scale'),
                                xmax=curve.get_value('right_scale'),
                                linecolor=curve.get_value('color'),
                                linewidth=curve.get_value('thickness')
            )                            
            kwargs = dict(curve.get_values())
            print '\ntrack_panel.update_curve({}, {})'.format(curve_pos, kwargs)
            track_panel.update_curve(curve_pos, x_axis, y_axis, **kwargs) 

        
        
    def _check_curve(self, curve):
        if curve.get_value('curve_name').startswith('*'):
            curve_type = curve.get_value('curve_name').replace('*', '')
            for log_name in self._get_all_well_curves().keys():
                parms = Parms.ParametersManager.get().get_curve_parms(log_name)
                if parms:
                    if curve_type == str(parms.get('Type')):
                        curve.set_value('curve_name', log_name)
                        curve.set_value('left_scale', parms.get('LeftScale'))
                        curve.set_value('right_scale', parms.get('RightScale'))
                        curve.set_value('width', parms.get('thickness'))
                        curve.set_value('point_plotting', parms.get('LineStyle'))
                        break
                else:
                    continue
            if curve.get_value('curve_name').startswith('*'):
                return None      
        if self._get_all_well_curves().get(curve.get_value('curve_name')) is None:
            return None
        return curve
         
         
    def append_curves(self, track_pos, curves_list):
        print '\nLogPlot.append_curves'
        plot_label, track_panel = self.get_panels(track_pos)
        depth_obj = self._OM.list('depth', self.get_well_uid())[0]
        y_axis = depth_obj.data
        
        for curve in curves_list:
            curve_name = curve.get_value('curve_name')
            if self._get_all_well_curves().get(curve_name).tid == 'partition':
                partition = self._get_all_well_curves().get(curve_name)
                curve.set_value('point_plotting', 'Partition')
                part_map = {}
                for part in partition.list('part'): 
                    part_map[part.code] = (part.color, part.data)
                x_axis = part_map
                unit = None
            else:    
                x_axis = self._get_all_well_curves().get(curve_name).data  
                unit = self._get_all_well_curves().get(curve_name).unit
            print curve
            kwargs = dict(curve.get_values())
            track_panel.append_curve(x_axis, y_axis, **kwargs) 
            plot_label.append_track(name=curve.get_value('curve_name'), 
                                    tracktype=curve.get_value('point_plotting'),
                                    unit = unit,
                                    xmin=curve.get_value('left_scale'),
                                    xmax=curve.get_value('right_scale'),
                                    linecolor=curve.get_value('color'),
                                    linewidth=curve.get_value('thickness')
            )    

        
        
    def remove_track_curves(self, track_pos, curves_indexes_list):
        print  '\nLogPlot.remove_track_curves'
        plot_label, track_panel = self.get_panels(track_pos)
        curves_indexes_list.sort(reverse=True) 
        for curve_idx in curves_indexes_list:
            plot_label.remove_track(curve_idx)
            track_panel.remove_curve(curve_idx)

    
    """
    def _get_curve_parameters(self, curve):
        curve_name = curve.get_value('curve_name')
        if self._get_all_well_curves().get(curve_name).tid == 'partition':
            partition = self._get_all_well_curves().get(curve_name)
            curve.set_value('point_plotting', 'Partition')
            part_map = {}
            for part in partition.list('part'): 
                part_map[part.code] = (part.color, part.data)
            x_axis = part_map
            prop_map = {}
            prop_map['name'] = curve_name
            prop_map['tracktype'] = curve.get_value('point_plotting')
            return prop_map, x_axis
        elif :    
            x_axis = self._get_all_well_curves().get(curve_name).data  
            unit = self._get_all_well_curves().get(curve_name).unit
        print curve
        kwargs = dict(curve.get_values())
    """
    
###############################################################################
### Event Methods
###############################################################################    

    def _OnSize(self, evt):  
        wx.CallAfter(self._refresh_scroll_bar)
        evt.Skip()                    
         
    def _OnDoClose(self, evt):
        #from NEW_UI import PlotController 
        #print
        #print evt
        #print 'closing LogPlot...'  
        self.destroy()
        evt.Skip()
        
    def _OnEditFormat(self, evt):
        self.run_format_frame()
 
    def _OnTrackTitleActivate(self, evt):        
        track_title_position = self.get_panel_position(evt.GetEventObject())
        self.run_format_frame(track_title_position)
        
    def _OnChoicePlotRange(self, evt):
        name, lim = self._plot_range
        if evt.GetString() != name:
            self.set_plot_range(evt.GetString())
                   
    def _OnEditRange(self, evt): 
        dlg = UI.dialog.Dialog(self, 
            [
                (UI.dialog.Dialog.text_ctrl, 'Range Name:', 'name'),
                (UI.dialog.Dialog.text_ctrl, 'Top Depth:', 'top'),
                (UI.dialog.Dialog.text_ctrl, 'Bottom Depth: ', 'bottom')
            ], 
            'Plot Range Editor'
        )
        if dlg.ShowModal() == wx.ID_OK:
            map_ = dlg.get_results()
            try:
                top = float(map_.get('top'))
                bottom = float(map_.get('bottom'))
            except Exception:
                print '\n_OnEditRange: Error converting top or depth values to float. Skiping...'
            self.add_plot_range(top, bottom, map_.get('name'))    
        dlg.Destroy()

    def _OnFit(self, evt):
        self._set_check_box_fit(self.cbFit.IsChecked())
        evt.Skip() 
        
###############################################################################
    
    def run_format_frame(self, 
             target_track_pos=UI.formatframe.LogPlotFormatFrame.ID_ALL_TRACKS):        
        ff = UI.formatframe.LogPlotFormatFrame(self, target_track_pos,
                    self.get_plot_format(), ok_callback=self.set_plot_fommat)
        ff.Show()

###############################################################################
### Interface Methods
###############################################################################    
   
    def _refresh_scroll_bar(self):
        ps = self.ttsplitter._titles.GetScrollPageSize(wx.HORIZONTAL)
        sl = self.ttsplitter._titles.GetScrollLines(wx.HORIZONTAL)
        if sl > 0:
            self.statusBar.ShowScrollBar()
            self.statusBar.SetScrollbar(0, ps, sl, 1)
        else:
            self.statusBar.HideScrollBar()        

    def _DoScroll(self, pos):
        vpos = self.ttsplitter._titles.GetScrollPos(wx.VERTICAL)
        self.ttsplitter._titles.Scroll(pos, vpos)
        vpos = self.ttsplitter._tracks.GetScrollPos(wx.VERTICAL)
        self.ttsplitter._tracks.Scroll(pos, vpos)
    
    def _create_toolbar(self): 
        self.tb = aui.AuiToolBar(self)
        self.tb.SetToolBitmapSize(wx.Size(48, 48))   
        self.button_edit_format = wx.Button(self.tb, label='Edit Format')
        self.button_edit_format.Bind(wx.EVT_BUTTON , self._OnEditFormat)
        self.tb.AddControl(self.button_edit_format, '')
        plot_ranges = UI.UIManager.get().get_well_plot_ranges(self.well_oid)
        self.choice_plot_ranges = wx.Choice(self.tb, choices=plot_ranges.keys())
        self.choice_plot_ranges.Bind(wx.EVT_CHOICE , self._OnChoicePlotRange)
        self.tb.AddControl(self.choice_plot_ranges, '')        
        #self.button_edit_range = wx.Button(self.tb, label='Edit Range')
        #self.button_edit_range.Bind(wx.EVT_BUTTON , self._OnEditRange)
        #self.tb.AddControl(self.button_edit_range, '')
        self.cbFit = wx.CheckBox(self.tb, -1, 'Fit')        
        self.cbFit.Bind(wx.EVT_CHECKBOX , self._OnFit) 
        self.tb.AddControl(self.cbFit, '')
        self.tb.Realize()
        
    def _destroy_toolbar(self):
        if self.tb:
             # As recommended in <http://trac.wxwidgets.org/ticket/12590>
             del(self.tb)             

    def _set_check_box_fit(self, boolean):
        self.fit = boolean
        self.ttsplitter._SetFit(boolean)
        
    def _get_check_box_fit(self):
        return self.fit
        
###############################################################################        