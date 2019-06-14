
from collections import OrderedDict

import wx

from classes.ui import UIManager
from ui.mvc_classes.wxgripy import DialogController
from ui.mvc_classes.wxgripy import Dialog


class ObjectPropertiesDialogController(DialogController):
    tid = 'object_properties_dialog_controller'

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['obj_uid'] = {
        'default_value': None,
        'type': 'uid'
    }
    
    def __init__(self, **state):
        state['flags'] = None
        state['title'] = 'Object properties'
        super().__init__(**state)    

    def PostInit(self):
        UIM = UIManager()
        pgc = UIM.create('property_grid_controller', self.uid)
        self.subscribe(self.on_change_obj_uid, 'change.obj_uid') 
        self.view.mainpanel.GetSizer().Add(pgc.view, proportion=1, 
                            flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, border=10
        )
        self.view.mainpanel.GetSizer().Layout() 
        
    def on_change_obj_uid(self, new_value, old_value):
        UIM = UIManager()
        pgc = UIM.list('property_grid_controller', parent_uid=self.uid)[0]      
        pgc.obj_uid = new_value
        
    def _get_wx_parent(self, *args, **kwargs):
        return self.view.mainpanel
        
    
class ObjectPropertiesDialog(Dialog):
    tid = 'object_properties_dialog'
    
    def __init__(self, controller_uid):
        super().__init__(controller_uid)        