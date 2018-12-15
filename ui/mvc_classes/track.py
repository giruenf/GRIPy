# -*- coding: utf-8 -*-

from collections import OrderedDict

import numpy as np
import wx
import matplotlib.pyplot as plt

from classes.om import ObjectManager
from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIModelObject 
from classes.ui import UIViewObject 
from ui.mvc_classes.mpl_base import TrackFigureCanvas
from ui.mvc_classes.mpl_base import VisDataLabel
from app.app_utils import WellPlotState, parse_string_to_uid  
from app.gripy_function_manager import FunctionManager
from app import log

from ui.mvc_classes.mpl_base import PlotLabel
from app.app_utils import DropTarget






class TrackController(UIControllerObject):
    tid = 'track_controller'
    
    def __init__(self):
        super(TrackController, self).__init__()   
        
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
        
#    def set_ylim(self, ymin, ymax):
#        self.view._set_ylim(ymin, ymax) 
                
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
        parent_ctrl._change_width_for_selected_tracks(self.uid)
  
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
    
    
    """
    # For TrackFigureCanvas lying MPL.Artists objects
    def _get_canvas(self):
        UIM = UIManager()
        ctc = UIM.list('track_canvas_controller', self.uid)[0]  
        return ctc.view
    """
    

    def _get_windows(self):    
        tlc, tcc = self.view._get_label_canvas_controllers()
        return tlc.view, tcc.view




class TrackModel(UIModelObject):
    tid = 'track_model'
    
    _ATTRIBUTES = {
        'pos': {'default_value': -1, 
                'type': int
        },        
        'label': {'default_value': wx.EmptyString, 
                  'type': str
        },          
        'overview':{'default_value': False, 
                    'type': bool
        },   
        'width': {'default_value': 160, 
                  'type': int
        },
        'selected': {'default_value': False, 
                     'type': bool
        },
        'visible': {'default_value': True, 
                     'type': bool
        }
        
    }        
    
    def __init__(self, controller_uid, **base_state): 
        super(TrackModel, self).__init__(controller_uid, **base_state) 





# TODO: verificar uso de enum no App.utils
SASH_DRAG_NONE = 0 
SASH_DRAG_DRAGGING = 1



class TrackView(UIViewObject):
    tid = 'track_view'

    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)

        
    def PostInit(self): 
        try:
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            wp_ctrl_uid = UIM._getparentuid(self._controller_uid)
            wp_ctrl =  UIM.get(wp_ctrl_uid)
            #
            tcc = UIM.create('track_canvas_controller', self._controller_uid)
            tcc.view.mpl_connect('motion_notify_event', self._on_track_move)
            #
            drop_target_track_canvas = DropTarget(controller.is_valid_object,
                                  controller.append_object
            )            
            tcc.view.SetDropTarget(drop_target_track_canvas)            
            #   

            if controller.model.overview:             
                wp_ctrl._place_as_overview(tcc.view)
            else:
                tlc = UIM.create('track_label_controller', self._controller_uid)
  
                label_canvas_dt = DropTarget(controller.is_valid_object,
                                      controller.append_object
                )

                tlc.view.SetDropTarget(label_canvas_dt)        
            #  

            if controller.model.pos == -1:
                # aqui controller.size jah inclui track
                controller.model.pos = len(wp_ctrl) - 1
            #
            #track.view.track.update_multicursor(controller.model.multicursor)
            #track_canvas_controller.view.update_multicursor(controller.model.multicursor)
            #        
  
            pos = controller.model.pos
            tracks_affected = UIM.do_query('track_controller', wp_ctrl.uid,
                                                            'pos>='+str(pos)
            )    
            wp_ctrl._adjust_up_pos(self._controller_uid, pos)
            #            
            if not controller.model.overview:
                # TODO: rever o erro abaixo (nao chamar objeto da View assim)
                wp_ctrl.view.tracks_panel.insert(pos, tlc.view, 
                                              tcc.view,
                                              controller.model.width
                )
                for track_affected in tracks_affected:
                    if track_affected.uid != self._controller_uid:
                        track_affected.reload_track_title() 
                #
                self.set_ylim(wp_ctrl.model.shown_ylim[0], wp_ctrl.model.shown_ylim[1])
            else:
                self.set_ylim(wp_ctrl.model.wellplot_ylim[0], wp_ctrl.model.wellplot_ylim[1])

            # TODO: Verificar se isso ficarah
            """
            if controller.model.overview:
                ctc = UIM.list('track_canvas_controller', self._controller_uid)[0]    
                ctc.view.Bind(wx.EVT_SIZE, self.on_track_size)
                self.create_depth_canvas()
                self.reposition_depth_canvas()
                ctc.view.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)  
            #
            ctc.view.mpl_connect('motion_notify_event', self.on_track_move)
            """
            controller.subscribe(self._invert_selection, 'change.selected')
            controller.subscribe(self.change_visibility, 'change.visible')
            controller.subscribe(self.update_title, 'change.label')
            #controller.subscribe(self.update_title, 'change.pos')
            controller.subscribe(self._change_position, 'change.pos')

            self.update_title(None, None)   
            
        except Exception as e:
            print ('\n\n\nERROR [TrackView.PostInit]:', e, '\n\n\n')
            #raise
#        print ('FIM TrackView PostInit\n')


    def PreDelete(self):
#        print ('\nTrackView PreDelete:')
        
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        
        #ctc = UIM.list('track_canvas_controller', self._controller_uid)[0]
        
        #ctc.view.disconnect_multicursor()
        #self.track.disconnect_multicursor()
        
        # TODO: disconect ctc.view.mpl_connect('motion_notify_event', self.on_track_move) ????
        
        if not controller.model.overview:    
            pos = controller.model.pos
            #parent_controller.view._detach_windows(self.label, ctc.view)  
            #parent_controller.view._detach_top_window(self.label)
            #self.label.Destroy()
            #UIM.remove(ctc.uid)
            #self.track.Destroy()
            parent_controller._adjust_positions_after_track_deletion(pos)
        
        #else:
            # TODO: cade o remove DropTarget?? verificar....
        #    if controller.model.overview:    
        #        parent_controller._pre_delete_overview_track()



    def _on_track_move(self, event):
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
        
        
#        print ('on_track_move:', event.xdata, event.ydata)
        
        parent_controller.show_status_message(info)



    def _get_wx_parent(self, *args):
        flag = args[0]
#        print ('\nTrackView._get_wx_parent', flag)
        """
        """        
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)      
        try:
            if flag.startswith('track_canvas'):
                # For tids track_canvas_controller, 
                # canvas_track_model and canvas_track.
                if controller.model.overview:
                    return parent_controller._get_wx_parent('overview')
                else:
                    return parent_controller._get_wx_parent('track')       
            elif flag.startswith('track_label'): 
                # For tids canvas_label_controller, 
                # canvas_label_model and canvas_label.
                return parent_controller._get_wx_parent('label') 
            return parent_controller._get_wx_parent(flag)
        except:
            raise



    @staticmethod
    def get_acceptable_tids():
        return ['log', 'index_curve', 'partition', 'seismic', 'scalogram', 
                'velocity', 'angle', 'gather', 'model1d']


    def is_valid_object(self, obj_uid):
        return True        



    def on_track_size(self, event):
        event.Skip()
        wx.CallAfter(self.reposition_depth_canvas)



    """    

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
        y1 = self.depth_to_wx_position(parent_controller.model.shown_ylim[0])
        self.d1_canvas.SetPosition((0, y1)) 
           
        #self.d1_canvas.Refresh()
        y2 = self.depth_to_wx_position(parent_controller.model.shown_ylim[1])          
        self.d2_canvas.SetPosition((0, y2 - self.canvas_width))    
        #self.d2_canvas.Refresh()


    def depth_to_wx_position(self, depth):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        if depth <= parent_controller.model.wellplot_ylim[0]:
            return 0
        elif depth >= parent_controller.model.wellplot_ylim[1]:
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
#        print ('\nSTART of end_dragging')
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
        #parent_controller.model.wellplot_ylim = (d1, d2)
        #
        parent_controller.model.set_value_from_event('shown_ylim', (d1, d2))
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
#        print ('END of end_dragging')
   


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
    
        

    """
    

    def change_visibility(self, new_value, old_value):
        #print 'change_visibility:', new_value
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        parent_controller.show_track(self._controller_uid, new_value)


    def _append_artist(self, artist_type, *args, **kwargs):
        return self.track.append_artist(artist_type, *args, **kwargs)



        

    def update_title(self, new_value=None, old_value=None):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        try:
            if controller.model.overview:
                return
            
            tlc, _ = self._get_label_canvas_controllers()
            if not controller.model.label:
#                print (333)
                splitter_pos = controller.get_position(relative_position=True)
#                print (444)
              # print 'update_title:', self._controller_uid, str(splitter_pos+1)
                tlc.update_title(text=str(splitter_pos+1))
            else:  
                tlc.update_title(text=controller.model.label)       
        except Exception as e:
            print (e)
            raise
            
            
    def _invert_selection(self, new_value, old_value):
        self.track.process_change_selection()

        if self.label:
            self.label.process_change_selection()

    def set_ylim(self, ymin, ymax):
#        print ('\nTrackView.set_ylim:', ymax, ymin)
        
        _, tcc = self._get_label_canvas_controllers()
        tcc.model.ylim = (ymax, ymin)

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

 
    def _get_label_canvas_controllers(self):
        """
        """
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        tcc = UIM.list('track_canvas_controller', self._controller_uid)[0]
        if controller.model.overview:
            tlc = None
        else:
            tlc = UIM.list('track_label_controller', self._controller_uid)[0]    
        return tlc, tcc
        
        
        
        
        
        
        
        
        
        
        
        
        
        