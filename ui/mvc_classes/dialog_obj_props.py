
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
        state['flags'] = wx.OK
        state['title'] = 'Object properties'
        super().__init__(**state)    

        
    def PostInit(self):  
        self.subscribe(self.on_change_obj_uid, 'change.obj_uid')
        # The lines below are placed here because Controller.PostInit is called
        # after View.PostInit
        UIM = UIManager()
        pgc = UIM.create('property_grid_controller', self.uid)
        self.view.mainpanel.GetSizer().Add(pgc.view, 
                            proportion=1,
                            flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 
                            border=10
        )
        self.view.mainpanel.GetSizer().Layout()
        self.view.GetSizer().Layout()

             
    def on_change_obj_uid(self, new_value, old_value):
        UIM = UIManager()
        pgc = UIM.list('property_grid_controller', parent_uid=self.uid)[0]      
        pgc.obj_uid = new_value
        

        
    
class ObjectPropertiesDialog(Dialog):
    tid = 'object_properties_dialog'
    
    def __init__(self, controller_uid):
        super().__init__(controller_uid)        

    def _get_wx_parent(self, *args, **kwargs):
        return self.mainpanel        
        