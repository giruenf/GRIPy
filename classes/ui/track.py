
from collections import OrderedDict
import wx

from classes.om import ObjectManager
from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIViewObject 

from app.app_utils import WellPlotState, parse_string_to_uid  
from app.gripy_function_manager import FunctionManager
from app import log

from app.app_utils import DropTarget
from classes.ui import interface


class TrackController(UIControllerObject):
    tid = 'track_controller'

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
        
    def __init__(self, **state):
        super(TrackController, self).__init__(**state)   
        
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
            toc = UIM.create('track_object_controller', self.uid)  
            if isinstance(obj_uid, str):
                obj_uid = parse_string_to_uid(obj_uid)
            toc.data_obj_uid = obj_uid
            return toc
        except Exception as e:
            print ('ERRO TrackController.append_object', e)
            raise
            
            
    def reload_track_title(self):
        self.view.update_title(None, None)
        
                
    def get_cursor_state(self):
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self.uid)
        parent_ctrl = UIM.get(parent_uid)
        return parent_ctrl.cursor_state 
    
    def on_change_width(self, new_value, old_value):  
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self.uid)
        parent_ctrl = UIM.get(parent_uid)
        parent_ctrl.view._do_change_width(self.get_position(False), 
                                          self.width
        )
        if not self.selected:
            return
        parent_ctrl._change_width_for_selected_tracks(self.uid)
  
    def on_change_overview(self, new_value, old_value):
        raise Exception('TrackModel.overview cannot be changed after TrackCreation.')
  
    
    def redraw(self):
        self.view.track.draw() 
           
    def _append_track_label(self, *args, **kwargs): 
        tlc = self._get_label_controller()
        return tlc.append_object(*args, **kwargs)

    def append_artist(self, artist_type, *args, **kwargs):
        tcc = self._get_canvas_controller()
        return tcc.append_artist(artist_type, *args, **kwargs)
    
    






#
ShowGridId = wx.NewId()
HideGridId = wx.NewId()
#
ScaleLinGridId = wx.NewId()
ScaleLogGridId = wx.NewId()
#
DepthLinesAllId = wx.NewId()
DepthLinesLeftId = wx.NewId()
DepthLinesRightId = wx.NewId()
DepthLinesCenterId = wx.NewId()
DepthLinesLeftRightId = wx.NewId()
DepthLinesNoneId = wx.NewId()
#
LinScaleLines0Id = wx.NewId()
LinScaleLines1Id = wx.NewId()
LinScaleLines2Id = wx.NewId()
LinScaleLines3Id = wx.NewId()
LinScaleLines4Id = wx.NewId()
LinScaleLines5Id = wx.NewId()
LinScaleLines6Id = wx.NewId()
LinScaleLines7Id = wx.NewId()
#   
LogDecades1Id = wx.NewId()
LogDecades10Id = wx.NewId()
LogDecades100Id = wx.NewId()
LogDecades1000Id = wx.NewId()
LogDecades10000Id = wx.NewId()
LogDecades100000Id = wx.NewId()
LogDecades1000000Id = wx.NewId()
#
ShowMinorgridId = wx.NewId()
HideMinorgridId = wx.NewId()     
#





class TrackView(UIViewObject):
    tid = 'track_view'

    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        
        
    def PostInit(self): 
        try:
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            well_plot_ctrl_uid = UIM._getparentuid(self._controller_uid)
            well_plot_ctrl =  UIM.get(well_plot_ctrl_uid)
            #
            tcc = UIM.create('track_canvas_controller', self._controller_uid)
            # TODO: Verificar se os mpl_connect devem ser desfeitos no PreDelete
            tcc.view.mpl_connect('motion_notify_event', self._on_track_move)
            tcc.view.mpl_connect('button_press_event', self._on_button_press)
            #
            drop_target_track_canvas = DropTarget(controller.is_valid_object,
                                  controller.append_object
            )            
            
            tcc.view.SetDropTarget(drop_target_track_canvas)            
            #   
            if controller.overview:             
                well_plot_ctrl._place_as_overview(tcc.view)
            
            else:
                tlc = UIM.create('track_label_controller', 
                                                         self._controller_uid)
                label_canvas_dt = DropTarget(controller.is_valid_object,
                                      controller.append_object
                )
                tlc.view.SetDropTarget(label_canvas_dt)        
            #  
            if controller.pos == -1:
                # aqui controller.size jah inclui track
                controller.pos = len(well_plot_ctrl) - 1


            # When a new Track is inserted, others with position >= must have
            # theirs position incremented by 1.
            well_plot_ctrl._increment_tracks_positions(
                                        pos=controller.pos,
                                        exclude_track_uid=self._controller_uid, 
            )
            #            
            if not controller.overview:
                # Pass windows to WellPlot to be inserted on track panel.
                well_plot_ctrl._insert_windows_on_track_panel(
                        pos=controller.pos, label_window=tlc.view, 
                        canvas_window=tcc.view, 
                        initial_width=controller.width
                )
                # Track with position greater than inserted must have their 
                # titles updated.
                well_plot_ctrl._reload_tracks_titles(pos=controller.pos,
                                        exclude_track_uid=self._controller_uid, 
                )              
                # 
                self.set_ylim(well_plot_ctrl.shown_ylim[0], 
                                                  well_plot_ctrl.shown_ylim[1]
                )
            else:
                self.set_ylim(well_plot_ctrl.wellplot_ylim[0], 
                                              well_plot_ctrl.wellplot_ylim[1]
                )

            # TODO: Verificar se isso ficarah

                tcc.create_depth_canvas()
                

            controller.subscribe(self._on_change_selected, 'change.selected')
            controller.subscribe(self.change_visibility, 'change.visible')
            
            controller.subscribe(self.update_title, 'change.label')
            controller.subscribe(self.update_title, 'change.pos')
            
            controller.subscribe(self._change_position, 'change.pos')

            self.update_title(None, None)   
            
        except Exception as e:
            print ('\n\n\nERROR [TrackView.PostInit]:', e, '\n\n\n')



    def PreDelete(self):

        try:
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            parent_controller_uid = UIM._getparentuid(self._controller_uid)
            parent_controller =  UIM.get(parent_controller_uid)
            

            
            # TODO: disconect ctc.view.mpl_connect('motion_notify_event', self.on_track_move) ????
            
            if not controller.overview:    
                pos = controller.pos
                parent_controller._adjust_positions_after_track_deletion(pos)
            
    
        except Exception as e:
            print('TRACK PreDelete:', e)
            raise 
            
            
        
    def _get_label_controller(self):     
        """
        """
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if controller.overview:
            return None
        return UIM.list('track_label_controller', self._controller_uid)[0]    
     
        
    def _get_canvas_controller(self):
        """
        """
        UIM = UIManager()
        return UIM.list('track_canvas_controller', self._controller_uid)[0]
        
        

    def _on_track_move(self, event):
        axes = event.inaxes
        if axes is None:
            return

        OM = ObjectManager()
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        info = parent_controller.index_type + ': {:0.2f}'.format(event.ydata)

        for toc in UIM.list('track_object_controller', self._controller_uid):
            
            
            data = toc.get_data_info(event)
            if data is None:
                continue
            if isinstance(data, float):
                str_x = '{:0.2f}'.format(data)
            else:
                str_x = str(data)

            obj = OM.get(toc.data_obj_uid)
            info += ', {}: {}'.format(obj.name, str_x)    
        
        
#        print ('on_track_move:', event.xdata, event.ydata)
        
        parent_controller.show_status_message(info)



    def _on_change_selected(self, new_value, old_value):
        tlc = self._get_label_controller()
        if tlc:
            try:
                tlc.change_selection(new_value)
            except Exception as e:
                print ('ERROR @ Track._on_change_selected: [LABEL]', e, new_value, old_value)
                pass
        #
        tcc = self._get_canvas_controller()
        try:
            tcc.change_selection(new_value)
        except Exception as e:
            print ('ERROR @ Track._on_change_selected: [CANVAS]', e, new_value, old_value)
            pass
            


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
                if controller.overview:
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



    def _on_track_size(self, event):
        event.Skip()
        wx.CallAfter(self.reposition_depth_canvas)



###############################################################################
###############################################################################
###############################################################################
        



    def on_canvas_mouse(self, event):

        if event.GetEventType() in [wx.wxEVT_MOTION, wx.wxEVT_LEFT_DOWN, 
                        wx.wxEVT_LEFT_UP, wx.wxEVT_MOTION|wx.wxEVT_LEFT_DOWN]:
            
            UIM = UIManager()
            tcc = UIM.list('track_canvas_controller', self._controller_uid)[0]
            
            new_event = wx.MouseEvent(event.GetEventType())
            pos = tcc.view.ScreenToClient(wx.GetMousePosition())
            new_event.SetPosition(pos)
            new_event.Skip()
            tcc.view.GetEventHandler().ProcessEvent(new_event)  



    def create_depth_canvas(self):
        self._in_canvas = -1
        self._drag_mode = SASH_DRAG_NONE
        self.canvas_color = 'blue'
        self.canvas_alt_color = 'red'
        self.canvas_width = 3
        #
        display_coords = self._get_depth_canvas_display_coords()
        #
        UIM = UIManager()
        tcc = UIM.list('track_canvas_controller', self._controller_uid)[0]
        #
        self.d1_canvas = wx.Panel(tcc.view, name='D1') 
        self.d1_canvas.SetSize((display_coords['width'], self.canvas_width))
        self.d1_canvas.SetBackgroundColour(self.canvas_color)    
        self.d1_canvas.SetPosition((display_coords['xmin'], 
                                                    display_coords['ymin']))
        #
        self.d2_canvas = wx.Panel(tcc.view, name='D2') 
        self.d2_canvas.SetSize((display_coords['width'], self.canvas_width))
        self.d2_canvas.SetBackgroundColour(self.canvas_color)  
        self.d2_canvas.SetPosition((display_coords['xmin'], 
                                    display_coords['ymax']-self.canvas_width))
        #
        self.d1_canvas.Bind(wx.EVT_MOUSE_EVENTS, self.on_canvas_mouse)
        self.d2_canvas.Bind(wx.EVT_MOUSE_EVENTS, self.on_canvas_mouse)        
        #
        




    
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



    def reposition_depth_canvas(self):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        if not controller.overview:
            return
        tcc = UIM.list('track_canvas_controller', self._controller_uid)[0]
        tcc.reposition_depth_canvas()
        
             


    
    
    def depth_to_wx_position(self, depth):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        if depth <= parent_controller.wellplot_ylim[0]:
            return 0
        elif depth >= parent_controller.wellplot_ylim[1]:
            return self.track.GetClientSize().height 
        return self.track.get_ypixel_from_depth(depth) 



    def start_dragging(self, canvas, start_y):
        if self._drag_mode != SASH_DRAG_NONE:
            return
        try:
            canvas.SetBackgroundColour(self.canvas_alt_color)
            canvas.Refresh()
            self._drag_mode = SASH_DRAG_DRAGGING
            self._old_y = start_y
        except:   
            self._drag_mode = SASH_DRAG_NONE
            raise

            

    def drag_it(self, canvas, new_y):
        if self._drag_mode != SASH_DRAG_DRAGGING:
            return   
        if new_y != self._old_y:
            inc = new_y - self._old_y
            x, y = canvas.GetPosition()  
            new_pos = y + inc
            if new_pos < 0:
                new_pos = 0
            if new_pos > (self.track.GetClientSize()[1] - self.canvas_width):
                new_pos = self.track.GetClientSize()[1] - self.canvas_width
            canvas.SetPosition((x, new_pos))
            canvas.Refresh()            
            self._old_y = new_y



    def end_dragging(self, canvas):

        if self._drag_mode != SASH_DRAG_DRAGGING:
            return    

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
        #parent_controller.wellplot_ylim = (d1, d2)
        #
        parent_controller.set_value_from_event('shown_ylim', (d1, d2))
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
   


    
        
###############################################################################
###############################################################################
###############################################################################
        
    

    def change_visibility(self, new_value, old_value):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        parent_controller.show_track(self._controller_uid, new_value)

     

    def update_title(self, new_value, old_value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        try:
            if controller.overview:
                return
            if not controller.label:
                splitter_pos = controller.get_position(relative_position=True)
                text=str(splitter_pos+1)
            else:   
                text=controller.label   
            tlc = self._get_label_controller()    
            tlc.title = text    
        except Exception as e:
            print ('ERROR @ Track.update_title:', e)
            raise
            
            

    def set_ylim(self, ymin, ymax):
        tcc = self._get_canvas_controller()
        tcc.ylim = (ymax, ymin)
        UIM = UIManager()
        for toc in UIM.list('track_object_controller', 
                            self._controller_uid):

            toc.redraw()
 
        
    def _change_position(self, new_value, old_value):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        print ('\nTrackView._change_position:', self._controller_uid, old_value, new_value)
        parent_controller.change_track_position(self._controller_uid,
                                                old_value, new_value
        )          
        self.update_title()    
        

    def _on_button_press(self, event):
        UIM = UIManager()
        if isinstance(event, wx.MouseEvent):        
            # wx.MouseEvent events
            gui_evt = event
            canvas = event.GetEventObject()
        else:
            # Matplotlib events: redirect to inner wx.MouseEvent
            gui_evt = event.guiEvent
            canvas = event.canvas
        #
        if gui_evt.GetEventObject() and gui_evt.GetEventObject().HasCapture():            
            gui_evt.GetEventObject().ReleaseMouse()  
        #          

        if gui_evt.GetButton() == 1:
            controller = UIM.get(self._controller_uid)
            if controller.get_cursor_state() == WellPlotState.SELECTION_TOOL:
                controller.selected = not controller.selected

        elif gui_evt.GetButton() == 2: 
            return
        
        elif gui_evt.GetButton() == 3:
            #controller = UIM.get(self._controller_uid) 
            
            menu = wx.Menu()
            #
            self._create_selected_obj_menus(menu)
            #
            tcc = self._get_canvas_controller()
            grid_submenu = wx.Menu()
            grid_submenu.AppendRadioItem(ShowGridId, 'Show')
            canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ShowGridId)
            grid_submenu.AppendRadioItem(HideGridId, 'Hide')
            canvas.Bind(wx.EVT_MENU, self._menu_selection, id=HideGridId)
            if tcc.plotgrid:
                grid_submenu.Check(ShowGridId, True)
            else:
                grid_submenu.Check(HideGridId, True)
            menu.AppendSubMenu(grid_submenu, 'Grid')
            #
            scale_submenu = wx.Menu()
            scale_submenu.AppendRadioItem(ScaleLinGridId, 'Linear')
            canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ScaleLinGridId)
            scale_submenu.AppendRadioItem(ScaleLogGridId, 'Logarithmic')
            canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ScaleLogGridId)
            
            if tcc.xscale == 'linear':
                scale_submenu.Check(ScaleLinGridId, True)
            elif tcc.xscale == 'log':
                scale_submenu.Check(ScaleLogGridId, True)
            
            menu.AppendSubMenu(scale_submenu, 'Scale')
            #           
            depth_lines_submenu = wx.Menu()
            
            depth_lines_submenu.AppendRadioItem(DepthLinesAllId, 'All')
            canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesAllId)
            
            depth_lines_submenu.AppendRadioItem(DepthLinesLeftId, 'Left')
            canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesLeftId)

            depth_lines_submenu.AppendRadioItem(DepthLinesRightId, 'Right')
            canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesRightId)
            
            depth_lines_submenu.AppendRadioItem(DepthLinesCenterId, 'Center')
            canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesCenterId)
            
            depth_lines_submenu.AppendRadioItem(DepthLinesLeftRightId, 'Left and Right')
            canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesLeftRightId)  
 
            depth_lines_submenu.AppendRadioItem(DepthLinesNoneId, 'None')
            canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesNoneId)  
           
            if tcc.depth_lines == 0:
                depth_lines_submenu.Check(DepthLinesAllId, True)
                
            elif tcc.depth_lines == 1:
                depth_lines_submenu.Check(DepthLinesLeftId, True)
                
            elif tcc.depth_lines == 2:
                depth_lines_submenu.Check(DepthLinesRightId, True)
                
            elif tcc.depth_lines == 3:
                depth_lines_submenu.Check(DepthLinesCenterId, True)  

            elif tcc.depth_lines == 4:
                depth_lines_submenu.Check(DepthLinesLeftRightId, True)  
                
            elif tcc.depth_lines == 5:
                depth_lines_submenu.Check(DepthLinesNoneId, True)                  
                
            menu.AppendSubMenu(depth_lines_submenu, 'Depth Lines')
            #                   
         
            menu.AppendSeparator() 
            if tcc.xscale == 'linear':
                scale_lines_submenu = wx.Menu()

                scale_lines_submenu.AppendRadioItem(LinScaleLines0Id, 'None')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines0Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines1Id, '1')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines1Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines2Id, '2')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines2Id)            
                scale_lines_submenu.AppendRadioItem(LinScaleLines3Id, '3')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines3Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines4Id, '4')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines4Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines5Id, '5')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines5Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines6Id, '6')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines6Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines7Id, '7')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines7Id)

                if tcc.scale_lines == 0:
                    scale_lines_submenu.Check(LinScaleLines0Id, True)  
                elif tcc.scale_lines == 1:
                    scale_lines_submenu.Check(LinScaleLines1Id, True)  
                elif tcc.scale_lines == 2:
                    scale_lines_submenu.Check(LinScaleLines2Id, True)  
                elif tcc.scale_lines == 3:
                    scale_lines_submenu.Check(LinScaleLines3Id, True)  
                elif tcc.scale_lines == 4:
                    scale_lines_submenu.Check(LinScaleLines4Id, True)  
                elif tcc.scale_lines == 5:
                    scale_lines_submenu.Check(LinScaleLines5Id, True)                   
                elif tcc.scale_lines == 6:
                    scale_lines_submenu.Check(LinScaleLines6Id, True)
                elif tcc.scale_lines == 7:
                    scale_lines_submenu.Check(LinScaleLines7Id, True)    
                menu.AppendSubMenu(scale_lines_submenu, 'Scale Lines')
                
            elif tcc.xscale == 'log':
                decades_submenu = wx.Menu()
            
                decades_submenu.AppendRadioItem(LogDecades1Id, '1')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades1Id)
                decades_submenu.AppendRadioItem(LogDecades10Id, '10')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades10Id)
                decades_submenu.AppendRadioItem(LogDecades100Id, '100')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades100Id)
                decades_submenu.AppendRadioItem(LogDecades1000Id, '1.000')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades1000Id)        
                decades_submenu.AppendRadioItem(LogDecades10000Id, '10.000')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades10000Id)
                decades_submenu.AppendRadioItem(LogDecades100000Id, '100.000')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades100000Id)
                decades_submenu.AppendRadioItem(LogDecades1000000Id, '1.000.000')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades1000000Id)
                if tcc.decades == 1:
                    decades_submenu.Check(LogDecades1Id, True)  
                elif tcc.decades == 2:
                    decades_submenu.Check(LogDecades10Id, True)  
                elif tcc.decades == 3:
                    decades_submenu.Check(LogDecades100Id, True)  
                elif tcc.decades == 4:
                    decades_submenu.Check(LogDecades1000Id, True)  
                elif tcc.decades == 5:
                    decades_submenu.Check(LogDecades10000Id, True)                   
                elif tcc.decades == 6:
                    decades_submenu.Check(LogDecades100000Id, True)
                elif tcc.decades == 7:
                    decades_submenu.Check(LogDecades1000000Id, True)    
                menu.AppendSubMenu(decades_submenu, 'Log Max')
                #
                # Minorgrid submenu
                minorgrid_submenu = wx.Menu()
                minorgrid_submenu.AppendRadioItem(ShowMinorgridId, 'Show')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ShowMinorgridId)
                minorgrid_submenu.AppendRadioItem(HideMinorgridId, 'Hide')
                canvas.Bind(wx.EVT_MENU, self._menu_selection, id=HideMinorgridId)                
                if tcc.minorgrid:
                    minorgrid_submenu.Check(ShowMinorgridId, True)
                else:
                    minorgrid_submenu.Check(HideMinorgridId, True)
                menu.AppendSubMenu(minorgrid_submenu, 'Minor Grid')
            #   
                
            canvas.PopupMenu(menu, gui_evt.GetPosition())  
            menu.Destroy() # destroy to avoid mem leak
            # If Menu was displayed, return True to TrackFigureCanvas.on_press    
            #return True
 


    def _create_selected_obj_menus(self, menu):
        self._ids_functions = {}
        selected_obj_menus = OrderedDict()
        UIM = UIManager()
        tcc = self._get_canvas_controller()
        tocs = UIM.list('track_object_controller', self._controller_uid)
        for toc in tocs:
            print(toc.uid)
            repr_ctrl = toc.get_representation()
            print(repr_ctrl)
            if repr_ctrl and \
                        repr_ctrl.tid == 'density_representation_controller':
                obj_submenu = wx.Menu()
                id_ = wx.NewId() 
                obj_submenu.Append(id_, 'Show navigator')
                tcc.Bind(wx.EVT_MENU, self._object_menu_selection, id=id_)    
                self._ids_functions[id_] = (self._data_navigator_helper, 
                                               (toc.uid), {}
                )   
                selected_obj_menus[toc.get_data_object()] = obj_submenu
            elif toc.selected:
                obj = toc.get_data_object()
                if obj:
                    obj_submenu = wx.Menu()
                    #
                    funcs = FunctionManager.functions_available_for_class(obj.__class__)
                    for func in funcs:

                        id_ = wx.NewId() 
                        obj_submenu.Append(id_, func['friendly_name'])
                        tcc.Bind(wx.EVT_MENU, 
                                         self._object_menu_selection, id=id_
                        ) 
                        self._ids_functions[id_] = (func['function'], (obj), 
                                    {'toc': toc}
                        )
                    #
                    obj_submenu.AppendSeparator() 
                    id_ = wx.NewId() 
                    obj_submenu.Append(id_, 'Remove from track')
                    tcc.Bind(wx.EVT_MENU, self._object_menu_selection, id=id_)    
                    self._ids_functions[id_] = (self._remove_object_helper, 
                                                   (toc.uid), {}
                    )
                    #
                    obj_submenu.AppendSeparator() 
                    id_ = wx.NewId() 
                    obj_submenu.Append(id_, 'Properties')
                    tcc.Bind(wx.EVT_MENU, self._object_menu_selection, id=id_)    
                    self._ids_functions[id_] = (self._properties_object_helper, 
                                                   (toc.uid), {}
                    )
                    #
                    obj_submenu.AppendSeparator() 
                    id_ = wx.NewId() 
                    obj_submenu.Append(id_, 'Delete object')
                    tcc.Bind(wx.EVT_MENU, self._object_menu_selection, id=id_)    
                    self._ids_functions[id_] = (self._delete_object_helper, 
                                                   (obj.uid), {}
                    )
                    #
                    selected_obj_menus[obj] = obj_submenu 
                    
        if selected_obj_menus:
            for obj, obj_submenu in selected_obj_menus.items():
                menu.AppendSubMenu(obj_submenu, obj.get_friendly_name())
            menu.AppendSeparator()    
   
    
    def _object_menu_selection(self, event):
        func, args, kwargs = self._ids_functions.get(event.GetId())
        if isinstance(func, staticmethod):
            func = func.__func__ 
        #print '_object_menu_selection', func, args
        
        if callable(func):         
            try:
                func(args, **kwargs)
                
            except Exception as e:
                print('ERROR _object_menu_selection:', e)
                raise


    def _remove_object_helper(self, *args, **kwargs):
        UIM = UIManager()
        UIM.remove(args[0])
 
    
    def _properties_object_helper(self, *args, **kwargs):
        UIM = UIManager()
        toc = UIM.get(args[0])    
        repr_ctrl = toc.get_representation()
        Interface.create_properties_dialog(repr_ctrl.uid)
        
        
    def _delete_object_helper(self, *args, **kwargs):
        print ('_delete_object_helper:', args[0])
        OM = ObjectManager()
        OM.remove(args[0])    


    def _data_navigator_helper(self, *args, **kwargs):
        UIM = UIManager()
        nav_ctrl = UIM.create('navigator_controller', parent_uid=args[0])
        nav_ctrl.view.Show()        
        
              
    def _menu_selection(self, event):
        UIM = UIManager()
        tcc = UIM.list('track_canvas_controller', self._controller_uid)[0]
        
        if event.GetId() == ShowGridId:
            tcc.plotgrid = True    
        elif event.GetId() == HideGridId:
            tcc.plotgrid = False
        elif event.GetId() == ScaleLinGridId:
            tcc.xscale = 'linear'  
        elif event.GetId() == ScaleLogGridId:
            tcc.xscale = 'log'       
        elif event.GetId() == DepthLinesAllId:
            tcc.depth_lines = 0
        elif event.GetId() == DepthLinesLeftId:
            tcc.depth_lines = 1  
        elif event.GetId() == DepthLinesRightId:
            tcc.depth_lines = 2
        elif event.GetId() == DepthLinesCenterId:
            tcc.depth_lines = 3   
        elif event.GetId() == DepthLinesLeftRightId:
            tcc.depth_lines = 4           
        elif event.GetId() == DepthLinesNoneId:
            tcc.depth_lines = 5       
        elif event.GetId() == LogDecades1Id:
            tcc.decades = 1
        elif event.GetId() == LogDecades10Id:
            tcc.decades = 2
        elif event.GetId() == LogDecades100Id:
            tcc.decades = 3
        elif event.GetId() == LogDecades1000Id:
            tcc.decades = 4
        elif event.GetId() == LogDecades10000Id:
            tcc.decades = 5
        elif event.GetId() == LogDecades100000Id:
            tcc.decades = 6
        elif event.GetId() == LogDecades1000000Id:
            tcc.decades = 7          
        elif event.GetId() == LinScaleLines0Id:
            tcc.scale_lines = 0            
        elif event.GetId() == LinScaleLines1Id:
            tcc.scale_lines = 1             
        elif event.GetId() == LinScaleLines2Id:
            tcc.scale_lines = 2             
        elif event.GetId() == LinScaleLines3Id:
            tcc.scale_lines = 3
        elif event.GetId() == LinScaleLines4Id:
            tcc.scale_lines = 4
        elif event.GetId() == LinScaleLines5Id:
            tcc.scale_lines = 5
        elif event.GetId() == LinScaleLines6Id:
            tcc.scale_lines = 6
        elif event.GetId() == LinScaleLines7Id:
            tcc.scale_lines = 7
        elif event.GetId() == ShowMinorgridId:
            tcc.minorgrid = True    
        elif event.GetId() == HideMinorgridId:
            tcc.minorgrid = False        



        
        
            