# -*- coding: utf-8 -*-

import wx
from formatframe import LogPlotFormatFrame
from OM.Manager import ObjectManager
from chronometer import Chronometer
from collections import OrderedDict

#from UI.logplotformat import LogPlotFormat
import UI
import DT


'''

   TODO: FICAR ATENTO AS DUAS LINHAS NO FINAL QUE REGISTRAM NO OBJECTMANAGER !!!

'''


class UIObject(object):
    
    def __init__(self):
        UIManagerSingleton.get()._register_ui_object(self)        
        self.uid = self.tid, self.oid
        
    def destroy(self):
        raise NotImplementedError("Please Implement this method")    



# Singleton based on yapsy.PluginManager
class UIManager(object):
    VALID_TIDS = ['logplot', 'crossplot', 'well_range']

    def __init__(self):
        self._current_tid_ids = {}
        self._well_objects = {}
        for tid in self.VALID_TIDS:
            self._current_tid_ids[tid] = 0
        self._OM = ObjectManager(self)
        self._main_window = None
        
   
    def _register_well(self, well_uid):
        _, well_oid = well_uid
        well_map = {}
        for tid in self.VALID_TIDS:
            well_map[tid] = OrderedDict()   
        self._well_objects[well_oid] = well_map    
        #print 'UIManager.register_well: ', self._well_objects    
    
    def _register_depth(self, depth_uid):
        well_uid = self._OM._getparentuid(depth_uid)
        _, well_oid = well_uid
        #print depth_uid 
        depth = self._OM.get(depth_uid)
        self.add_well_plot_range(well_oid, depth.data.min(), depth.data.max(), 'Whole Well')
                
        #self.add_well_plot_range(well_oid, 0.0, 6000.0, 'Default Range')        
            
    def create_main_window(self):
        if self._main_window is None:
            self._main_window = UI.MainWindow.Frame(None)
    
    def get_main_window(self):
        if self._main_window is None:
            self.create_main_window()
        return self._main_window


    def create_log_plot(self, well_oid, logplotformat=None, depth_lim=None, fit=False):
        if not self._main_window:
            raise Exception('Cannot create a Log Plot without a Main Window.')
        c = Chronometer() 
        logplot = UI.logplot.LogPlot(self._main_window, well_oid, logplotformat)
        well_map = self._well_objects.get(well_oid)
        well_map.get('logplot')[logplot.oid] = logplot
        c.end('UIManager.create_log_plot')

    def destroy_log_plot(self, well_oid, logplot_oid):
        self.destroy_ui_object(well_oid, 'logplot', logplot_oid)
     
     
    def destroy_ui_object(self, well_oid, obj_tid, obj_oid):
        if not obj_tid in self.VALID_TIDS:
            raise Exception('Cannot destroy a object with a invalid type.')
        if well_oid in self._well_objects.keys():
            well_tid_map = self._well_objects.get(well_oid).get(obj_tid)
            if obj_oid in well_tid_map.keys():
                obj = well_tid_map.get(obj_oid)
                obj.destroy()
            else:
                print 'UIManager.destroy_well_object: invalid object oid.'
        else:
            print 'UIManager.destroy_well_object: invalid well oid.'          
    
    
    def get_well_plot_ranges(self, well_oid):
        well_map = self._well_objects.get(well_oid)
        return well_map.get('well_range')
        
        
    def add_well_plot_range(self, well_oid, depth_min, depth_max, name):
        well_plot_ranges = self.get_well_plot_ranges(well_oid)
        well_plot_ranges[name] = (depth_min, depth_max)


    def create_logplot_track(self, logplot, pos, **kwargs):
        print
        
    def update_logplot_track(self, logplot, pos, **kwargs):
        print

    def remove_logplot_track(self, logplot, pos):
        print        
                  
    def set_logplot_parms(self, logplot_oid, parms_map): 
        print
        
    def get_logplot_parms(self, logplot_oid):
        print
        
        
    '''    
    def OnTrackTitleActivate(self, evt):
        track_title_activated = evt.GetEventObject()
        logplot_activated = track_title_activated.get_real_parent() 
        #def __init__(self, logplot, track_id=ID_ALL_TRACKS, logplotformat=None, ok_callback=None):
        track_title_position = logplot_activated.get_panel_position(track_title_activated)
        ff = LogPlotFormatFrame(logplot_activated, track_title_position, 
            logplot_activated.get_plot_format(), ok_callback=self.OnTrackTitleActivateCB)
        ff.Show()

    #self.callback(self.logplot, self.track_id, self.edited_logplotformat)
    def OnTrackTitleActivateCB(self, logplot, logplotformat):
        logplot.set_plot_fommat(logplotformat)
    '''    
    
    '''
        pos = logplot.get_panel_position(track)
        titlePanel, trackPanel = logplot.get_panels()[pos] 
        list_ = []
        depth_obj = self._OM.list('depth', logplot.get_well_uid())[0]
        y = depth_obj.data
        for loguid, attr in result.items():
            list_.append((attr.get('CurveName'), (attr.get('LeftScale'), attr.get('RightScale')), attr.get('Color')))
            x = self._OM.get(loguid).data
            trackPanel.insert_curve(x, y, color=attr.get('Color'), xlim=(attr.get('LeftScale'), attr.get('RightScale')))
        titlePanel.add_track_titles(list_)
    '''
        
   
    def _get_new_id(self, object_tid):
        """
        Return a new object identifier for the desired tid.
        
        Parameters
        ----------
        object_tid : str
            The type identifier whose a new object identifier is needed.
        
        Returns
        -------
        idx : int
            A new unique object identifier for a given tid.
        """     

        idx = self._current_tid_ids[object_tid]
        self._current_tid_ids[object_tid] += 1
        return idx


    def _register_ui_object(self, obj):
        if not obj.tid:
            raise Exception('Cannot register a UIWellChildObject without a tid.')
        elif obj.tid not in self.VALID_TIDS:
            raise Exception('Cannot register a invalid UIWellChildObject type.')
        if obj.well_oid is None:
            #print 'obj.well_oid: ', obj.well_oid
            raise Exception('Cannot register a UIWellChildObject without a well oid.')
        elif obj.well_oid not in self._well_objects.keys():
            #print 'self._well_objects.keys(): ', self._well_objects.keys()
            #print 'obj.well_oid: ', obj.well_oid
            raise Exception('Cannot register a UIWellChildObject a invalid well oid.')
        obj.oid = self._get_new_id(obj.tid)
        well_map = self._well_objects[obj.well_oid]
        well_map[obj.tid][obj.oid] = obj
        #print self._well_objects
        
        
    def _unregister_ui_object(self, obj):
        if not obj.tid:
            raise Exception('Cannot unregister a UIWellChildObject without a tid.')
        elif obj.tid not in self.VALID_TIDS:
            raise Exception('Cannot unregister a invalid UIWellChildObject type.')
        well_map = self._well_objects[obj.well_oid]
        well_tid_map = well_map.get(obj.tid)
        if obj.oid in well_tid_map:
            del well_tid_map[obj.oid]    



    

    """
    Para que todo poço ou depth criado seja registrado no UIManager
    """
    def _register_object(self, obj_uid): 
        tid, oid = obj_uid
        if tid == 'well':
            self._register_well(obj_uid)
        elif tid == 'depth':
            self._register_depth(obj_uid)    
       





'''        
        titlePanel.Bind(wx.EVT_LEFT_DCLICK, self._OnTrackTitileActivate, source=titlePanel)
        

    

        
    def aaa(self):

        

        #overview = logplot.get_overview_track()
        #overview.update_dummy_axes(width=2.0, plotgrid=True, decades= 3, 
        #    depth_lines=0, leftscale=0.1, x_scale='lin', minorgrid=True)
        cls.__plots.append(logplot)
        
        titlePanel1, trackPanel1 = logplot.AddTrack()
        titlePanel1.create_title('1', cls._title_bg_color)
        trackPanel1.update_dummy_axes(width=0.5, plotgrid=True, decades= 3, 
            depth_lines=0, leftscale=0.1, x_scale='lin', minorgrid=True)
            
        titlePanel2, trackPanel2 = logplot.AddTrack()
        titlePanel2.create_title('2', cls._title_bg_color)
        trackPanel2.update_dummy_axes(width=0.5, plotgrid=True, decades= 3, 
            depth_lines=0, leftscale=0.1, x_scale='lin', minorgrid=True)
            
        titlePanel3, trackPanel3 = logplot.AddTrack()
        titlePanel3.create_title('3', cls._title_bg_color)
        trackPanel3.update_dummy_axes(width=0.5, plotgrid=True, decades= 3, 
            depth_lines=0, leftscale=0.1, x_scale='lin', minorgrid=True)
       
        

        # Ip's Triple Combo as testing...
        =================================
        
        
TRACK    0.50    No   No     2    0.200          No       No       5
CURVE   *Index  0.0000     1.0000   NONE       1     Black   LIN      Solid
$ gr caliper track
TRACK    2.00   Yes   No     2    0.200          No       No       5
CURVE  *GammaRay *         *         RBU        1     Green   LIN      Solid
CURVE  *Caliper  *         *         RBU        1     Blue    LIN      Solid
CURVE  *SP       *         *         RBU        1     Black   LIN      Solid
$ resistivity track
TRACK    3.50   Yes   Yes    4    0.200          Yes      No       5
CURVE  *DeepRes  0.2000    2000.0000 RBU        1     Red     LOG      Solid
CURVE  *MedRes   0.2000    2000.0000 RBU        1     Fuchsia LOG      Solid
CURVE  *MicroRes 0.2000    2000.0000 RBU        1     Purple  LOG      Solid
$ density neutron track
TRACK    3.50   Yes   No     4    0.200          Yes      No      10
CURVE  *Density  *         *         LBU        1     Red     LIN      Solid
CURVE  *Neutron  *         *         LBU        1     Green   LIN      Solid
CURVE  *Drho     *         *         NONE       1     Black   LIN      Solid
$ OverView Track
TRACK    0.50   No    No     2    0.200          No       Yes      5        

        titlePanel.add_track_titles([
            ("BAGACA 01", (0.0, 1.0), 'red'), 
            ("BAGACA 02", (1.0, 2.0), 'green'),
            ("BAGACA 03", (2.0, 3.0), 'blue'),
            ("BAGACA 04", (2.0, 3.0), 'yellow'),
            ("BAGACA 05", (2.0, 3.0), 'black'),
        ])
        
        trackPanel.update_dummy_axes(width=2.0, plotgrid=True, decades= 3, 
            depth_lines=0, leftscale=0.1, x_scale='lin', minorgrid=True)
            
        titlePanel2, trackPanel2 = logplot.AddTrack()
        titlePanel2.create_title('2', cls._title_bg_color)
        titlePanel2.add_track_titles([
            ("BAGACA 01", (0.0, 1.0), 'red'), 
            ("BAGACA 02", (1.0, 2.0), 'green'),
            ("BAGACA 03", (2.0, 3.0), 'blue')
        ])
        trackPanel2.update_dummy_axes(width=2.0, plotgrid=True, decades= 3, 
            depth_lines=0, leftscale=0.1, x_scale='lin', minorgrid=True)
            
        titlePanel3, trackPanel3 = logplot.AddTrack()
        titlePanel3.create_title('3', cls._title_bg_color)
        titlePanel3.add_track_titles([
            ("BAGACA 01", (0.0, 1.0), 'red'), 
            ("BAGACA 02", (1.0, 2.0), 'green'),
            ("BAGACA 03", (2.0, 3.0), 'blue')
        ])
        trackPanel3.update_dummy_axes(width=2.0, plotgrid=True, decades= 3, 
            depth_lines=0, leftscale=0.1, x_scale='lin', minorgrid=True)
      
#        titlePanel.Bind(wx.EVT_LEFT_DCLICK, self._OnLegendaDClick, source=titlePanel)

  
    def _OnLegendaDClick(cls, evt):
        ff = FormatFrame(self, self.well, 
                    self.ttsplitter.LegendaIndexOf(evt.GetEventObject()))        
        ff.Show()
        
        
  
    
    def file_read(cls):
        import os
        for file in os.listdir("/mydir"):
            if file.endswith(".txt"):
                print(file)
               
        f = open('SYN_RJS_710_R30HZ_UT5X..txt')
        xf, yf = [], []
        for l in f:
            row = l.split()
            xf.append(float(row[1]))
            yf.append(float(row[0]))
        
'''     
    
    
# Singleton based on yapsy.PluginManagerSingleton
class UIManagerSingleton(object):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = UIManager()
        return cls.__instance    
        
        
ObjectManager.addcallback("add",  UIManagerSingleton.get()._register_object)        
#ObjectManager.registertype(UI.logplotformat.LogPlotFormat, DT.DataTypes.Well)     

   
        
        
        
        
        
        