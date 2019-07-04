from collections import OrderedDict   
from collections import Sequence

from classes.om import ObjectManager
from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIViewObject 
                         

class RepresentationController(UIControllerObject):
    tid = 'representation_controller'
    
    def __init__(self, **state):
        super().__init__(**state)

    def get_parent_controller(self):
        UIM = UIManager()
        toc_uid = UIM._getparentuid(self.uid)
        return UIM.get(toc_uid)

    def get_track_controller(self):
        UIM = UIManager()
        toc_uid = UIM._getparentuid(self.uid)
        tc_uid = UIM._getparentuid(toc_uid)
        return UIM.get(tc_uid)
        
    def get_data_object_uid(self):
        toc = self.get_parent_controller()
        return toc.data_obj_uid

    def get_data_object(self):
        do_uid = self.get_data_object_uid()
        OM = ObjectManager()
        data_object = OM.get(do_uid)        
        return data_object              
         
    def get_friendly_name(self):
        data_object = self.get_data_object()
        return data_object.get_friendly_name()

 
class RepresentationView(UIViewObject):
    tid = 'representation_view'

    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid) 
        self._mplot_objects = OrderedDict()     
            
    def PreDelete(self):
        self.clear()

    def get_parent_controller(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)            
        return controller.get_parent_controller()

    def get_track_controller(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)            
        return controller.get_track_controller()
        
    def get_data_info(self, event):
        raise NotImplemented('{}.get_data_info must be implemented.'.format(self.__class__))
     
    def get_canvas(self):
        try:
            first_mpl_object = list(self._mplot_objects.values())[0]
            canvas = first_mpl_object.figure.canvas        
            return canvas
        except:
            # TODO: Rever linhas abaixo
            # Getting from TrackController    
            try:
                UIM = UIManager()
                toc_uid = UIM._getparentuid(self._controller_uid)
                track_controller_uid = UIM._getparentuid(toc_uid)
                track_controller =  UIM.get(track_controller_uid)
                tcc = track_controller._get_canvas_controller()
                return tcc.view
            except:
                raise
             
    def draw_canvas(self):     
        canvas = self.get_canvas()   
        if canvas:
            canvas.draw()
            return True
        return False

    def draw_after(self, func, *args, **kwargs):
        if callable(func):
            func(*args, **kwargs)
            return self.draw_canvas()
        return False
    
    def clear(self):  
        self.draw_after(self._remove_all_artists)

    def _remove_all_artists(self):
        for value in self._mplot_objects.values():
            # String is a sequence too, but it will not be here
            if isinstance(value, Sequence):
                for obj in value:
                    if obj:
                        obj.remove()  
            else:
                if value:
                    value.remove()
        self._mplot_objects = OrderedDict()     
        
    def _set_picking(self, mplot_obj, pickradius=3):
        # When we set picker to True (to enable line picking) function
        # Line2D.set_picker sets pickradius to True, 
        # then we need to set it again.
        mplot_obj.set_picker(True)
        mplot_obj.set_pickradius(pickradius)
              