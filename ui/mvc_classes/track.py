# -*- coding: utf-8 -*-

from collections import OrderedDict

import numpy as np
import wx
import matplotlib.pyplot as plt

from om.manager import ObjectManager
from ui.uimanager import UIManager
from ui.uimanager import UIControllerObject 
from ui.uimanager import UIModelObject 
from ui.uimanager import UIViewObject 
from ui.mvc_classes.mpl_base import TrackFigureCanvas
from ui.mvc_classes.mpl_base import VisDataLabel
from app.app_utils import LogPlotState, parse_string_to_uid  
from app.gripy_function_manager import FunctionManager
from app import log


class TrackController(UIControllerObject):
    tid = 'track_controller'
    
    def __init__(self):
        super(TrackController, self).__init__()   
        #print '\nTrackController.__init__'
        
    def PostInit(self):    
        self.subscribe(self.on_change_width, 'change.width')
        self.subscribe(self.on_change_overview, 'change.overview')

            
    def get_position(self, relative_position=True):  
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self.uid)
        parent_ctrl = UIM.get(parent_uid)
        return parent_ctrl.get_track_position(self.uid, relative_position)
            
    
    # Method for Drag and Drop....
    def append_object(self, obj_uid):
        UIM = UIManager()
        try:
#            print (111, obj_uid, type(obj_uid))
            toc = UIM.create('track_object_controller', self.uid)  
#            print (222)
            if isinstance(obj_uid, str):
                obj_uid = parse_string_to_uid(obj_uid)
            tid, oid = obj_uid
#            print (333)
            toc.model.obj_tid = tid
#            print (444)
            toc.model.obj_oid = oid
#            print (555)
            return toc
        except Exception as e:
            print ('ERRO TrackController.append_object', e)
            raise
            
    def reload_track_title(self):
        self.view.update_title(None, None)
        
    def set_ylim(self, ymin, ymax):
        self.view._set_ylim(ymin, ymax) 
                
    def get_cursor_state(self):
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self.uid)
        parent_ctrl = UIM.get(parent_uid)
        return parent_ctrl.model.cursor_state 
    
    def on_change_width(self, new_value, old_value):  
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self.uid)
        parent_ctrl = UIM.get(parent_uid)
        parent_ctrl.view._do_change_width(self.get_position(False), 
                                          self.model.width
        )
        if not self.model.selected:
            return
        parent_ctrl._propagate_change_width(self.uid)
  
    def on_change_overview(self, new_value, old_value):
        #UIM = UIManager()
        #parent_uid = UIM._getparentuid(self.uid)
        #parent_ctrl = UIM.get(parent_uid)
        #wx.CallAfter(parent_ctrl.set_overview_track, self.uid, new_value)
        raise Exception('TrackModel.overview cannot be changed after TrackCreation.')
  
    def reposition_depth_canvas(self):
        self.view.reposition_depth_canvas()
    
    def redraw(self):
        self.view.track.draw() 
           
    def _append_track_label(self):    
        return self.view.label.append_object()

    def _append_artist(self, artist_type, *args, **kwargs):
        return self.view._append_artist(artist_type, *args, **kwargs)
    
    # For TrackFigureCanvas lying MPL.Artists objects
    def _get_canvas(self):
        return self.view.track

    def _get_windows(self):    
        return self.view.label, self.view.track



class TrackModel(UIModelObject):
    tid = 'track_model'
    
    _ATTRIBUTES = {
        'pos': {'default_value': -1, 
                'type': int
        },        
        'label': {'default_value': wx.EmptyString, 
                  'type': str
        },          
        'plotgrid': {'default_value': True, 
                     'type': bool
        },             
        'x_scale': {'default_value': 0, 
                    'type': int
        },
        'overview':{'default_value': False, 
                    'type': bool
        },                                 
        'depth_lines': {'default_value': 0, 
                        'type': int
        },                
        'width': {'default_value': 160, 
                  'type': int
        },
        'minorgrid': {'default_value': True, 
                      'type': bool
        },              
        'leftscale': {'default_value': 0.2, 
                      'type': float
        },              
        'decades':  {'default_value': 4, 
                     'type': int
        },             
        'scale_lines': {'default_value': 5, 
                        'type': int
        },                
        'selected': {'default_value': False, 
                     'type': bool
        },
        'visible': {'default_value': True, 
                     'type': bool
        }#,
        
#        Moved to LogPlot
#        'y_major_grid_lines': {'default_value': 1000.0, 
#                      'type': float
#        },
#        'y_minor_grid_lines': {'default_value': 100.0, 
#                      'type': float
#        }
          
    }        
    
    def __init__(self, controller_uid, **base_state): 
        super(TrackModel, self).__init__(controller_uid, **base_state) 



ShowGridId = wx.NewId()
HideGridId = wx.NewId()
ScaleLinGridId = wx.NewId()
ScaleLogGridId = wx.NewId()
DepthLinesAllId = wx.NewId()
DepthLinesLeftId = wx.NewId()
DepthLinesRightId = wx.NewId()
DepthLinesCenterId = wx.NewId()
DepthLinesLeftRightId = wx.NewId()
DepthLinesNoneId = wx.NewId()
Decades1Id = wx.NewId()
Decades10Id = wx.NewId()
Decades100Id = wx.NewId()
Decades1000Id = wx.NewId()
Decades10000Id = wx.NewId()
Decades100000Id = wx.NewId()
Decades1000000Id = wx.NewId()

ScaleLines3Id = wx.NewId()
ScaleLines4Id = wx.NewId()
ScaleLines5Id = wx.NewId()
ScaleLines6Id = wx.NewId()
ScaleLines7Id = wx.NewId()

# TODO: verificar uso de enum no App.utils
SASH_DRAG_NONE = 0 
SASH_DRAG_DRAGGING = 1



class TrackView(UIViewObject):
    tid = 'track_view'

    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)

        
        
    def PostInit(self):  
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
#        print ('000')
        parent_controller._create_windows(self._controller_uid)
        #
#        print ('111')
        
        if controller.model.overview:
#            print ('222')
            self.create_depth_canvas()
#            print ('333')
            self.reposition_depth_canvas()
            self.track.Bind(wx.EVT_SIZE, self.on_track_size)
            self.track.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)            
        #
        self.track.mpl_connect('motion_notify_event', self.on_track_move)
        controller.subscribe(self._invert_selection, 'change.selected')
        controller.subscribe(self.change_visibility, 'change.visible')
        controller.subscribe(self.update_title, 'change.label')
        #controller.subscribe(self.update_title, 'change.pos')
        controller.subscribe(self._change_position, 'change.pos')
        controller.subscribe(self.update_plotgrid, 'change.plotgrid')
        controller.subscribe(self.update_x_scale, 'change.x_scale')
        controller.subscribe(self.update_y_major_grid_lines, 'change.y_major_grid_lines')
        controller.subscribe(self.update_y_minor_grid_lines, 'change.y_minor_grid_lines')
        controller.subscribe(self.update_depth_lines, 'change.depth_lines')
        controller.subscribe(self.update_minorgrid, 'change.minorgrid')
        controller.subscribe(self.update_leftscale, 'change.leftscale')
        controller.subscribe(self.update_decades, 'change.decades')
        controller.subscribe(self.update_scale_lines, 'change.scale_lines')
        self.update_title(None, None)   


    def PreDelete(self):
        self.track.disconnect_multicursor()
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        if not controller.model.overview:    
            pos = controller.model.pos
            parent_controller.view._detach_windows(self.label, self.track)  
            self.label.Destroy()
            self.track.Destroy()
            parent_controller._propagate_deletion(pos, self._controller_uid)
        else:
            # TODO: cade o remove DropTarget?? verificar....
            if controller.model.overview:    
                parent_controller._pre_delete_overview_track()
            self.track.Destroy() 


    def on_track_size(self, event):
        event.Skip()
        wx.CallAfter(self.reposition_depth_canvas)


    def on_mouse(self, event):
        #print 'on_mouse'
        x, y = event.GetPosition()
        if self._drag_mode == SASH_DRAG_NONE:    
            self._set_in_canvas(self._canvas_hit_test(x, y))              
            if event.LeftDown():
                self.start_dragging(y)
        elif self._drag_mode == SASH_DRAG_DRAGGING:
            if event.LeftIsDown():
                self.drag_it(y)       
            elif event.LeftUp():
                self.end_dragging()
        event.Skip()
        

    def on_canvas_mouse(self, event):
        #print 'on_canvas_mouse'
        if event.GetEventType() in [wx.wxEVT_MOTION, wx.wxEVT_LEFT_DOWN, 
                        wx.wxEVT_LEFT_UP, wx.wxEVT_MOTION|wx.wxEVT_LEFT_DOWN]:
            evt = wx.MouseEvent(event.GetEventType())
            pos = self.track.ScreenToClient(wx.GetMousePosition())
            evt.SetPosition(pos)
            evt.Skip()
            self.track.GetEventHandler().ProcessEvent(evt)# or evt.IsAllowed()
                

    def create_depth_canvas(self):
        self._in_canvas = -1
        self._drag_mode = SASH_DRAG_NONE
        self.canvas_color = 'blue'
        self.canvas_alt_color = 'red'
        self.canvas_width = 2
        
        self.d1_canvas = wx.Panel(self.track) 
        self.d1_canvas.SetSize((self.track.GetClientSize().width, 
                                self.canvas_width)
        )
        self.d1_canvas.SetBackgroundColour(self.canvas_color)    
  
        self.d2_canvas = wx.Panel(self.track) 
        self.d2_canvas.SetSize((self.track.GetClientSize().width, 
                                self.canvas_width)
        )
        self.d2_canvas.SetBackgroundColour(self.canvas_color)    
        self.d1_canvas.Bind(wx.EVT_MOUSE_EVENTS, self.on_canvas_mouse)
        self.d2_canvas.Bind(wx.EVT_MOUSE_EVENTS, self.on_canvas_mouse)


    def reposition_depth_canvas(self):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)        
        ##print '\nMIN-MAX:', min_depth, max_depth, min_pos, max_pos, self.d1, self.d2     
        y1 = self.depth_to_wx_position(parent_controller.model.y_min_shown)
        self.d1_canvas.SetPosition((0, y1)) 
           
        #self.d1_canvas.Refresh()
        y2 = self.depth_to_wx_position(parent_controller.model.y_max_shown)          
        self.d2_canvas.SetPosition((0, y2 - self.canvas_width))    
        #self.d2_canvas.Refresh()


    def depth_to_wx_position(self, depth):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        if depth <= parent_controller.model.logplot_y_min:
            return 0
        elif depth >= parent_controller.model.logplot_y_max:
            return self.track.GetClientSize().height 
        return self.track.get_ypixel_from_depth(depth) 


    def start_dragging(self, start_y):
        #print 'Pressed button on canvas ', self._in_canvas
        if self._in_canvas == -1:
            return 
        if self._drag_mode != SASH_DRAG_NONE:
            return
        if self._in_canvas == 1:
            canvas = self.d1_canvas
        else:
            canvas = self.d2_canvas
        self._drag_mode = SASH_DRAG_DRAGGING
        #self.track.CaptureMouse()
        #print 'mouse capturado'
        self._old_y = start_y
        canvas.SetBackgroundColour(self.canvas_alt_color)
        canvas.Refresh()            


    def drag_it(self, new_y):
        #print 'Dragging canvas:', self._in_canvas
        if self._in_canvas == -1:
            return 
        if self._drag_mode != SASH_DRAG_DRAGGING:
            return       
        ##print new_y, self._old_y 
        if new_y != self._old_y:
            self._adjust_canvas_position(new_y - self._old_y)
            self._old_y = new_y


    def end_dragging(self):
        #print 'Release button of canvas', self._in_canvas
        print ('\nSTART of end_dragging')
        if self._in_canvas == -1:
            return 
        if self._drag_mode != SASH_DRAG_DRAGGING:
            return    
        if self._in_canvas == 1:
            canvas = self.d1_canvas
        else:
            canvas = self.d2_canvas
        self._drag_mode = SASH_DRAG_NONE
        self._old_y = None
        if self.track.HasCapture():
            self.track.ReleaseMouse()
         #   print 'mouse solto'
          
        y1 = self.d1_canvas.GetPosition()[1]
        y2 = self.d2_canvas.GetPosition()[1]

        #print 'y12:', y1, y2 

        if y1 <= y2:
            d1 = self.track.get_depth_from_ypixel(y1)
            d2 = self.track.get_depth_from_ypixel(y2 + self.canvas_width)
        #    print 'considerando y12:', y1, y2 + self.canvas_width
        else:    
            d1 = self.track.get_depth_from_ypixel(y2)
            d2 = self.track.get_depth_from_ypixel(y1 + self.canvas_width)
        #    print 'considerando y12:', y2, y1 + self.canvas_width
            
        #print 'd12:', d1, d2    
        #    
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        #
        #parent_controller.model.logplot_y_min = d1
        #parent_controller.model.logplot_y_max = d2
        #
        parent_controller.model.set_value_from_event('y_min_shown', d1)
        parent_controller.model.set_value_from_event('y_max_shown', d2)
        parent_controller._reload_ylim()
        #
        #
        #self._reload_depths_from_canvas_positions()    
        #if self._callback:
        #    self._callback(self.get_depth())
        #print 'Send ' + str(self.get_depth()) + ' to callback...'    
        canvas.SetBackgroundColour(self.canvas_color)
        canvas.Refresh()  
        #           
        #d1, d2 = self.get_depth()           
        self.track.SetToolTip(wx.ToolTip('{0:.2f} - {1:.2f}'.format(d1, d2)))
        print ('END of end_dragging')
   


    def _adjust_canvas_position(self, inc):
        if self._in_canvas == 1:
            canvas = self.d1_canvas
        elif self._in_canvas == 2:
            canvas = self.d2_canvas
        x, y = canvas.GetPosition()  
        new_pos = y + inc
        if new_pos < 0:
            new_pos = 0
        if new_pos > (self.track.GetClientSize()[1] - self.canvas_width):
            new_pos = self.track.GetClientSize()[1] - self.canvas_width
        canvas.SetPosition((x, new_pos))
        canvas.Refresh()

            
    def _canvas_hit_test(self, x, y, tolerance=5):
        r1 = self.d1_canvas.GetRect()   
        r2 = self.d2_canvas.GetRect() 
        if y >= r1.y - tolerance and y <= r1.y + r1.height + tolerance:
            return 1
        if y >= r2.y - tolerance and y <= r2.y + r2.height + tolerance:
            return 2        
        return -1    
        
   
    def _set_in_canvas(self, canvas_number):
        if canvas_number != self._in_canvas:
            ##print '_set_in_canvas({})'.format(canvas_number)
            if canvas_number != -1:
                ##print 'Entrou -', canvas_number
                self._in_canvas = canvas_number
                self.track.SetCursor(wx.Cursor(wx.CURSOR_SIZENS))

            else:
                ##print 'Saiu -', self._in_canvas
                self._in_canvas = -1
                self.track.SetCursor(wx.STANDARD_CURSOR)
    
        
    '''
    From wx display coords to mpl display position or vice-versa.
    ''' 
    #def transform_display_position(self, pos):
    #    y = self.track.GetClientSize().height
    #    pos = y - pos
    #    return int(pos)

    



    def change_visibility(self, new_value, old_value):
        #print 'change_visibility:', new_value
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        parent_controller.show_track(self._controller_uid, new_value)


    def update_plotgrid(self, new_value, old_value):
        self.track.update('plotgrid', new_value)

    def update_x_scale(self, new_value, old_value):
        self.track.update('x_scale', new_value)

    def update_y_major_grid_lines(self, new_value, old_value):
        self.track.update('y_major_grid_lines', new_value)

    def update_y_minor_grid_lines(self, new_value, old_value):
        self.track.update('y_minor_grid_lines', new_value)

    def update_depth_lines(self, new_value, old_value):
        self.track.update('depth_lines', new_value)

    def update_minorgrid(self, new_value, old_value):
        self.track.update('minorgrid', new_value)        

    def update_leftscale(self, new_value, old_value):
        self.track.update('leftscale', new_value)

    def update_decades(self, new_value, old_value):
        self.track.update('decades', new_value)
        
    def update_scale_lines(self, new_value, old_value):
        self.track.update('scale_lines', new_value)

    def _append_artist(self, artist_type, *args, **kwargs):
        return self.track.append_artist(artist_type, *args, **kwargs)


    def on_track_move(self, event):
        """
        def data_to_axes_coordinates(self, data_coordinates)
        def axes_to_data_coordinates(self, axes_coordinates)
        def data_to_display_coordinates(self, data_coordinates)
        def display_to_data_coordinates(self, display_coordinates)
        def display_to_figure_coordinates(self, display_coordinates)
        def figure_to_display_coordinates(self, figure_coordinates)
        """
        axes = event.inaxes
        if axes is None:
            return
        #data_coords = (event.xdata, event.ydata)
        #disp_coords = (event.x, event.y)
        #data_coords = (event.xdata, event.ydata)
        #axes_coords = axes.data_to_axes_coordinates(data_coords)
        #fig_coords = axes.display_to_figure_coordinates(disp_coords)
        
            
        OM = ObjectManager()
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        info = parent_controller.model.index_type + ': {:0.2f}'.format(event.ydata)

        for toc in UIM.list('track_object_controller', self._controller_uid):
            data = toc.get_data_info(event)
            if data is None:
                continue
            if isinstance(data, float):
                str_x = '{:0.2f}'.format(data)
            else:
                str_x = str(data)
            uid = (toc.model.obj_tid, toc.model.obj_oid)
            obj = OM.get(uid)
            info += ', {}: {}'.format(obj.name, str_x)    
               
        parent_controller.show_status_message(info)
        
        #print self._controller_uid, event.xdata, event.ydata
        #print parent_controller, self._controller_uid
        
        parent_controller.show_cursor(self._controller_uid, event.xdata, event.ydata)
    
        
        
    
    
    def update_title(self, new_value=None, old_value=None):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if controller.model.overview:
            return
        if not controller.model.label:
            splitter_pos = controller.get_position(relative_position=True)
          # print 'update_title:', self._controller_uid, str(splitter_pos+1)
            self.label.update_title(text=str(splitter_pos+1))
        else:  
            self.label.update_title(text=controller.model.label)       
                
            
    def _invert_selection(self, new_value, old_value):
        self.track.process_change_selection()
        if self.label:
            self.label.process_change_selection()
        
        
    def _set_ylim(self, ymin, ymax):
        #print '\nTrackView._set_ylim:', (ymax, ymin)
        self.track.set_ylim((ymax, ymin))
        UIM = UIManager()
        for toc in UIM.list('track_object_controller', self._controller_uid):
            #print 'redrawing', toc.uid
            toc.redraw()
            #print 'end redraw'
        #print 'END _set_ylim\n'

    def _change_position(self, new_value, old_value):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        print ('\nTrackView._change_position:', self._controller_uid, old_value, new_value)
        parent_controller.change_track_position(self._controller_uid,
                                                old_value, new_value
        )
            
        self.update_title()    


    def process_event(self, event):
        ### From: http://stackoverflow.com/questions/14617722/matplotlib-and-wxpython-popupmenu-cooperation     
        #print
        #if event.guiEvent.GetEventObject().HasCapture():            
        #    event.guiEvent.GetEventObject().ReleaseMouse()        
        ###
        #print '\nTrackView.process_event:', event     
        #
        OM = ObjectManager()
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)        
        if isinstance(event, wx.MouseEvent):        
            gui_evt = event
        else:
            gui_evt = event.guiEvent
        #
        if gui_evt.GetEventObject() and gui_evt.GetEventObject().HasCapture():            
            gui_evt.GetEventObject().ReleaseMouse()  
        #    
        if gui_evt.GetButton() == 1:
            if controller.get_cursor_state() == LogPlotState.SELECTION_TOOL:
                controller.model.selected = not controller.model.selected
        #   
        elif gui_evt.GetButton() == 2: 
            print ('entrou 2')
            self.track.mark_vertical(event.xdata)
        #    
        elif gui_evt.GetButton() == 3: 
            menu = None
            UIM = UIManager()
            if isinstance(gui_evt.GetEventObject(), VisDataLabel):    
                visdl = gui_evt.GetEventObject()
                menu = wx.Menu()
                if visdl._obj_uid[0] == 'density_representation_controller':
                    id_ = wx.NewId() 
                    menu.Append(id_, 'Show navigator')
                    event.canvas.Bind(wx.EVT_MENU, lambda event: self._show_navigator(visdl._obj_uid), id=id_)
                    menu.AppendSeparator()       
                id_ = wx.NewId() 
                menu.Append(id_, 'Remove from track')
                event.canvas.Bind(wx.EVT_MENU, lambda event: self._remove_object_helper((visdl._obj_uid)), id=id_)    
                event.canvas.PopupMenu(menu, event.guiEvent.GetPosition())  
                menu.Destroy() # destroy to avoid mem leak
            #
            elif isinstance(gui_evt.GetEventObject(), TrackFigureCanvas):
                menu = None
                if gui_evt.GetEventObject().plot_axes.images:
                    dens_uid = gui_evt.GetEventObject().plot_axes.images[0].get_label()
                    ydata = event.ydata    
                    str_ydata = "{0:.2f}".format(round(ydata, 2))
                    menu = wx.Menu()
                    #
                    id_ = wx.NewId() 
                    menu.Append(id_, 'AVAF [' + str_ydata + ']')
                    event.canvas.Bind(wx.EVT_MENU, lambda event: \
                                self._avaf(dens_uid, ydata), id=id_)
                    #
                    id_ = wx.NewId() 
                    menu.Append(id_, 'CrossPlot [' + str_ydata + ']')
                    event.canvas.Bind(wx.EVT_MENU, lambda event: \
                                self._crossplot(dens_uid, ydata), id=id_)
                    menu.AppendSeparator() 
                    
                    """
                    
                    dens_repr_ctrl = UIM.get(dens_uid)
                    toc_uid = UIM._getparentuid(dens_repr_ctrl.uid)
                    toc = UIM.get(toc_uid)

                    if dens_repr_ctrl._data is not None:
                        filter_ = toc.get_filter()
                        #
                        z_data = filter_.data[0]
                        di_uid, display, is_range, z_first, z_last = z_data
                        z_data_index = OM.get(di_uid)
                        z_data = z_data_index.data[z_first:z_last]
                        #
                        x_data = filter_.data[1]
                        di_uid, display, is_range, x_first, x_last = x_data
                        x_data_index = OM.get(di_uid)
                        x_data = x_data_index.data[z_first:z_last]
                        #
                        z_index = dens_repr_ctrl._get_z_index(event.ydata)
                        if z_index is not None:
                            #print z_index
                            #print dens_repr_ctrl._data.shape
                            #print 
                            values = dens_repr_ctrl._data[:, z_index]
                            x_data_index.name
                            x_data

                            ####
                            root_controller = UIM.get_root_controller()        
                            cp_ctrl = UIM.create('crossplot_controller', root_controller.uid)  
                            cpp = cp_ctrl.view
                            #                    
                            cpp.crossplot_panel.set_xdata(x_data)
                            cpp.crossplot_panel.set_xlabel(x_data_index.name)
                            #
                            cpp.crossplot_panel.set_ydata(values)
                            cpp.crossplot_panel.set_ylabel('Amplitude')
                            #
                            #'''
                            #cpp.crossplot_panel.set_zdata(np.array(range(len(obj.dimensions[2][1]))))
                            #cpp.crossplot_panel.set_zlabel('No Name')
                            #cpp.crossplot_panel.set_zmode('continuous')
                            #
                            cpp.crossplot_panel.set_zmode('solid')
                            cpp.crossplot_panel.plot()
                            cpp.crossplot_panel.draw()  
                            ###
                        
                
                    """
                    
                #
                if menu is None:
                    menu = wx.Menu()
                self._create_selected_obj_menus(menu)
                #
                grid_submenu = wx.Menu()
                grid_submenu.AppendRadioItem(ShowGridId, 'Show')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ShowGridId)
                grid_submenu.AppendRadioItem(HideGridId, 'Hide')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=HideGridId)
                if controller.model.plotgrid:
                    grid_submenu.Check(ShowGridId, True)
                else:
                    grid_submenu.Check(HideGridId, True)
                menu.AppendSubMenu(grid_submenu, 'Grid')
                
                #
                scale_submenu = wx.Menu()
                scale_submenu.AppendRadioItem(ScaleLinGridId, 'Linear')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ScaleLinGridId)
                scale_submenu.AppendRadioItem(ScaleLogGridId, 'Logarithmic')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ScaleLogGridId)
                if not controller.model.x_scale:
                    scale_submenu.Check(ScaleLinGridId, True)
                else:
                    scale_submenu.Check(ScaleLogGridId, True)
                menu.AppendSubMenu(scale_submenu, 'Scale')
                #           
                 
                depth_lines_submenu = wx.Menu()
                
                depth_lines_submenu.AppendRadioItem(DepthLinesAllId, 'All')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesAllId)
                
                depth_lines_submenu.AppendRadioItem(DepthLinesLeftId, 'Left')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesLeftId)
    
                depth_lines_submenu.AppendRadioItem(DepthLinesRightId, 'Right')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesRightId)
                
                depth_lines_submenu.AppendRadioItem(DepthLinesCenterId, 'Center')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesCenterId)
                
                depth_lines_submenu.AppendRadioItem(DepthLinesLeftRightId, 'Left and Right')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesLeftRightId)  
     
                depth_lines_submenu.AppendRadioItem(DepthLinesNoneId, 'None')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesNoneId)  
               
                if controller.model.depth_lines == 0:
                    depth_lines_submenu.Check(DepthLinesAllId, True)
                    
                elif controller.model.depth_lines == 1:
                    depth_lines_submenu.Check(DepthLinesLeftId, True)
                    
                elif controller.model.depth_lines == 2:
                    depth_lines_submenu.Check(DepthLinesRightId, True)
                    
                elif controller.model.depth_lines == 3:
                    depth_lines_submenu.Check(DepthLinesCenterId, True)  
    
                elif controller.model.depth_lines == 4:
                    depth_lines_submenu.Check(DepthLinesLeftRightId, True)  
                    
                elif controller.model.depth_lines == 5:
                    depth_lines_submenu.Check(DepthLinesNoneId, True)                  
                    
                menu.AppendSubMenu(depth_lines_submenu, 'Depth Lines')
                #                   
             
                menu.AppendSeparator() 
                if controller.model.x_scale == 0:
                    scale_lines_submenu = wx.Menu()
                
                    scale_lines_submenu.AppendRadioItem(ScaleLines3Id, '3')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ScaleLines3Id)
                    scale_lines_submenu.AppendRadioItem(ScaleLines4Id, '4')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ScaleLines4Id)
                    scale_lines_submenu.AppendRadioItem(ScaleLines5Id, '5')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ScaleLines5Id)
                    scale_lines_submenu.AppendRadioItem(ScaleLines6Id, '6')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ScaleLines6Id)
                    scale_lines_submenu.AppendRadioItem(ScaleLines7Id, '7')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ScaleLines7Id)
    
                    if controller.model.scale_lines == 3:
                        scale_lines_submenu.Check(ScaleLines3Id, True)  
                    elif controller.model.scale_lines == 4:
                        scale_lines_submenu.Check(ScaleLines4Id, True)  
                    elif controller.model.scale_lines == 5:
                        scale_lines_submenu.Check(ScaleLines5Id, True)                   
                    elif controller.model.scale_lines == 6:
                        scale_lines_submenu.Check(ScaleLines6Id, True)
                    elif controller.model.scale_lines == 7:
                        scale_lines_submenu.Check(ScaleLines7Id, True)    
                    menu.AppendSubMenu(scale_lines_submenu, 'Scale Lines')
                    
                else:    
                    decades_submenu = wx.Menu()
                
                    decades_submenu.AppendRadioItem(Decades1Id, '1')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=Decades1Id)
                    decades_submenu.AppendRadioItem(Decades10Id, '10')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=Decades10Id)
                    decades_submenu.AppendRadioItem(Decades100Id, '100')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=Decades100Id)
                    decades_submenu.AppendRadioItem(Decades1000Id, '1.000')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=Decades1000Id)        
                    decades_submenu.AppendRadioItem(Decades10000Id, '10.000')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=Decades10000Id)
                    decades_submenu.AppendRadioItem(Decades100000Id, '100.000')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=Decades100000Id)
                    decades_submenu.AppendRadioItem(Decades1000000Id, '1.000.000')
                    event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=Decades1000000Id)
                    if controller.model.decades == 1:
                        decades_submenu.Check(Decades1Id, True)  
                    elif controller.model.decades == 2:
                        decades_submenu.Check(Decades10Id, True)  
                    elif controller.model.decades == 3:
                        decades_submenu.Check(Decades100Id, True)  
                    elif controller.model.decades == 4:
                        decades_submenu.Check(Decades1000Id, True)  
                    elif controller.model.decades == 5:
                        decades_submenu.Check(Decades10000Id, True)                   
                    elif controller.model.decades == 6:
                        decades_submenu.Check(Decades100000Id, True)
                    elif controller.model.decades == 7:
                        decades_submenu.Check(Decades1000000Id, True)    
                    menu.AppendSubMenu(decades_submenu, 'Log Max')
                #   
                    
                event.canvas.PopupMenu(menu, event.guiEvent.GetPosition())  
                menu.Destroy() # destroy to avoid mem leak
        # If Menu was displayed, return True to TrackFigureCanvas.on_press    
            return True
        # Otherwise, unpick artists and return False to TrackFigureCanvas.on_press
        tocs = UIM.list('track_object_controller', self._controller_uid)
        for toc in tocs:
            toc.model.selected = False        
        return False


    def _create_selected_obj_menus(self, menu):
        self._ids_functions = {}
        selected_obj_menus = OrderedDict()
        UIM = UIManager()
        tocs = UIM.list('track_object_controller', self._controller_uid)
        for toc in tocs:
            if toc.model.selected:
                obj = toc.get_object()
                if obj:
                    obj_submenu = wx.Menu()
                    #
                    funcs = FunctionManager.functions_available_for_class(obj.__class__)
                    for f in funcs:
                        #print 
                        #print f['name']
                        #print f['friendly_name']
                        #print f['function']
                        #print f['args']
                        #print f['kwargs'] 
                        
                        id_ = wx.NewId() 
                        obj_submenu.Append(id_, f['friendly_name'])
                        self.track.Bind(wx.EVT_MENU, self._object_menu_selection, id=id_) 
                        self._ids_functions[id_] = (f['function'], (obj))
                    #
                    obj_submenu.AppendSeparator() 
                    id_ = wx.NewId() 
                    obj_submenu.Append(id_, 'Remove from track')
                    self.track.Bind(wx.EVT_MENU, self._object_menu_selection, id=id_)    
                    self._ids_functions[id_] = (self._remove_object_helper, 
                                                   (toc.uid)
                    )
                    #
                    obj_submenu.AppendSeparator() 
                    id_ = wx.NewId() 
                    obj_submenu.Append(id_, 'Delete object')
                    self.track.Bind(wx.EVT_MENU, self._object_menu_selection, id=id_)    
                    self._ids_functions[id_] = (self._delete_object_helper, 
                                                   (toc.get_object().uid)
                    )
                    #
                    selected_obj_menus[obj] = obj_submenu 
        if selected_obj_menus:
            for obj, obj_submenu in selected_obj_menus.items():
                menu.AppendSubMenu(obj_submenu, obj.get_friendly_name())
            menu.AppendSeparator()    
   
    
    def _object_menu_selection(self, event):
        func, args = self._ids_functions.get(event.GetId())
        if isinstance(func, staticmethod):
            func = func.__func__ 
        #print '_object_menu_selection', func, args
        if callable(func):
            #print 'callable'
            func(args)
        #else:
        #    print 'not callable'
            #print func.__dict__
            #print 
        #    print func.__func__ 
        #    print 
            
            
    def _remove_object_helper(self, *args):
        UIM = UIManager()
        UIM.remove(args[0])
  
    def _delete_object_helper(self, *args):
        print ('_delete_object_helper:', args[0])
        OM = ObjectManager()
        OM.remove(args[0])    

         
    def _menu_selection(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        if event.GetId() == ShowGridId:
            controller.model.plotgrid = True    
        elif event.GetId() == HideGridId:
            controller.model.plotgrid = False
        elif event.GetId() == ScaleLinGridId:
            controller.model.x_scale = 0    
        elif event.GetId() == ScaleLogGridId:
            controller.model.x_scale = 1        
        elif event.GetId() == DepthLinesAllId:
            controller.model.depth_lines = 0
        elif event.GetId() == DepthLinesLeftId:
            controller.model.depth_lines = 1  
        elif event.GetId() == DepthLinesRightId:
            controller.model.depth_lines = 2
        elif event.GetId() == DepthLinesCenterId:
            controller.model.depth_lines = 3   
        elif event.GetId() == DepthLinesLeftRightId:
            controller.model.depth_lines = 4           
        elif event.GetId() == DepthLinesNoneId:
            controller.model.depth_lines = 5       
        elif event.GetId() == Decades1Id:
            controller.model.decades = 1
        elif event.GetId() == Decades10Id:
            controller.model.decades = 2
        elif event.GetId() == Decades100Id:
            controller.model.decades = 3
        elif event.GetId() == Decades1000Id:
            controller.model.decades = 4
        elif event.GetId() == Decades10000Id:
            controller.model.decades = 5
        elif event.GetId() == Decades100000Id:
            controller.model.decades = 6
        elif event.GetId() == Decades1000000Id:
            controller.model.decades = 7
        elif event.GetId() == ScaleLines3Id:
            controller.model.scale_lines = 3
        elif event.GetId() == ScaleLines4Id:
            controller.model.scale_lines = 4
        elif event.GetId() == ScaleLines5Id:
            controller.model.scale_lines = 5
        elif event.GetId() == ScaleLines6Id:
            controller.model.scale_lines = 6
        elif event.GetId() == ScaleLines7Id:
            controller.model.scale_lines = 7



    def _show_navigator(self, obj_uid):
        UIM = UIManager()
        toc_ctrl_uid = UIM._getparentuid(obj_uid)
        toc_ctrl = UIM.get(toc_ctrl_uid)
        nav_ctrl = UIM.create('navigator_controller', 
                              data_filter_oid=toc_ctrl.model.data_filter_oid,
                              title='Data navigator', size=(350, 600)
        )
        nav_ctrl.view.Show()





    def _avaf(self, repr_ctrl_uid, ydata):
        str_ydata = "{0:.2f}".format(round(ydata, 2))
        print ('\nAVAF:', str_ydata)
        OM = ObjectManager()
        UIM = UIManager()
        repr_ctrl = UIM.get(repr_ctrl_uid)
        toc_uid = UIM._getparentuid(repr_ctrl.uid)
        toc = UIM.get(toc_uid)
        if repr_ctrl._data is not None:
            filter_ = toc.get_filter()
            z_data = filter_.data[0]
            di_uid, display, is_range, z_first, z_last = z_data
            z_data_index = OM.get(di_uid)
            z_data = z_data_index.data[z_first:z_last]
            data_indexes = filter_.data
            
            slicer = []
            z_index = repr_ctrl._get_z_index(ydata)
            slicer.append(z_index)
            
            '''
            for (di_uid, display, is_range, first, last) in data_indexes[1:]:
                obj = OM.get(di_uid)    
                print 'name:', obj.name, obj.data
                """
                if display and is_range:
                    x_data = obj.data[slice(first, last)]
                    x_name = obj.name
                    break
                """
            '''    

            
            (y_di_uid, y_display, y_is_range, y_first, y_last) = data_indexes[1]
            (x_di_uid, x_display, x_is_range, x_first, x_last) = data_indexes[2]
            

            y_obj = OM.get(y_di_uid)
            y_data = y_obj.data[slice(0, len(y_obj.data))]
            y_name = y_obj.name            
            slicer.append(slice(0, len(y_obj.data)))
            
            x_obj = OM.get(x_di_uid)
            x_data = x_obj.data[slice(0, len(x_obj.data))]
            x_name = x_obj.name
            slicer.append(slice(0, len(x_obj.data)))
            
            slicer.append(0)
            slicer.append(0)
            
            slicer = tuple(slicer[::-1])
            
            print ('\n\n')
            print (slicer)
            print (repr_ctrl.get_object().data.shape)
            data = repr_ctrl.get_object().data[slicer]
            print (data.shape)
            
            print ('\n\n')
            print ('X:', x_name, x_data, len(x_data))
            print ('Y:', y_name, y_data, len(y_data))
            
            print ('z_index:', z_index)
            
            
            #print data.shape[::-1]
            
            #values = repr_ctrl.get_object().data[:, z_index]
            #print values.shape
            
            
            X, Y = np.meshgrid(x_data, y_data)

            CS = plt.contourf(X, Y, data.T, 100, cmap='spectral_r', vmin=0.0, vmax=3000.0)
                
            #plt.yscale('lin')
            
            plt.title('Poco A - TWT: ' + str_ydata + ' ms', fontsize=14) 

            fs=13
            plt.xlabel('Angulo', fontsize=fs) 
            plt.ylabel('Frequencia', fontsize=fs) 
            #plt.clabel('Densidade espectral', fontsize=12) 
            plt.xlim(x_data[0], x_data[-1])
            plt.ylim(0.0, y_data[-1])
            plt.grid(True)


            cbar = plt.colorbar(CS)
            #cbar.ax.set_ylabel('Densidade espectral')
            cbar.set_label('Densidade espectral', fontsize=fs) 
            
            print ('\n\n', cbar)
            #cbar.vmin = 0
            #cbar.vmax = 6000.0
            
            print (cbar.get_clim())
            print (cbar.get_cmap())
            print (cbar.ax.get_xlim())
            print (cbar.ax.get_ylim())
            #
            print (cbar.boundaries, type(cbar.boundaries))
            print (cbar.values)
            print (cbar.extendrect)
            # Add the contour line levels to the colorbar
            
            plt.show()




    def _crossplot(self, repr_ctrl_uid, ydata):
        OM = ObjectManager()
        UIM = UIManager()
        repr_ctrl = UIM.get(repr_ctrl_uid)
        toc_uid = UIM._getparentuid(repr_ctrl.uid)
        toc = UIM.get(toc_uid)
        if repr_ctrl._data is not None:
            filter_ = toc.get_filter()
            z_data = filter_.data[0]
            di_uid, display, is_range, z_first, z_last = z_data
            z_data_index = OM.get(di_uid)
            z_data = z_data_index.data[z_first:z_last]
            data_indexes = filter_.data

            for (di_uid, display, is_range, first, last) in data_indexes[1:]:
                obj = OM.get(di_uid)      
                if display and is_range:
                    x_data = obj.data[slice(first, last)]
                    x_name = obj.name
                    break

            z_index = repr_ctrl._get_z_index(ydata)
            if z_index is not None:
                values = repr_ctrl._data[:, z_index]
                cp_ctrl = UIM.list('crossplot_controller')[0]
                cpp = cp_ctrl.view
                #                    
                cpp.crossplot_panel.set_xdata(x_data)
                cpp.crossplot_panel.set_xlabel(x_name)
                if not cpp.crossplot_panel.xlim:
                    cpp.crossplot_panel.set_xlim([x_data[0], x_data[-1]])
                #
                cpp.crossplot_panel.set_ydata(values)
                cpp.crossplot_panel.set_ylabel('Y Values')
                #
                if cpp.crossplot_panel.ylim:
                    ylim = cpp.crossplot_panel.ylim
                    
                    if np.nanmin(values) < ylim[0]:
                        ymin = np.nanmin(values) 
                    else:
                        ymin = ylim[0]
                    if np.nanmax(values) > ylim[1]:
                        ymax = np.nanmax(values)
                    else:
                        ymax = ylim[1]   
                    
                    if ymin < ymax:
                        cpp.crossplot_panel.set_ylim([ymin, ymax]) 
                    else:
                        cpp.crossplot_panel.set_ylim([ymax, ymin])    
                else:
                    cpp.crossplot_panel.set_ylim([np.nanmin(values), np.nanmax(values)])
                #
                cpp.crossplot_panel.set_zmode('continuous')
                cpp.crossplot_panel.plot()
                cpp.crossplot_panel.draw()  
                





