from collections import OrderedDict

import wx
from pubsub import pub

from classes.ui import UIManager
from .toplevel import  TopLevelController, TopLevel
from app.app_utils import GripyIcon


class DialogController(TopLevelController):
    tid = 'dialog_controller'
    
    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['flags'] = {
        'default_value': wx.OK|wx.CANCEL, 
        'type': int

    }    
    _ATTRIBUTES['style'] = {
        'default_value': wx.DEFAULT_DIALOG_STYLE, 
        'type': int        
    }
    
    def __init__(self, **state):
        super().__init__(**state)

    def PreDelete(self):
        pub.unsubAll(topicFilter=self._topic_filter)
        self.view._objects = {}
        try:
            self.view.Destroy()
        except:
            pass
    
    def _topic_filter(self, topic_name):
        return topic_name == '_widget_changed@' + self.view.get_topic()   
    
          
class Dialog(TopLevel, wx.Dialog):   
    tid = 'dialog'
    
    def __init__(self, controller_uid):
        TopLevel.__init__(self, controller_uid)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        wx.Dialog.__init__(self, None, wx.ID_ANY, controller.title,
            pos=controller.pos, size=controller.size, 
            style=controller.style              
        ) 
        self._objects = {}
        if controller.icon:   
            self.icon = GripyIcon(controller.icon, wx.BITMAP_TYPE_ICO)        
            self.SetIcon(self.icon)     
        if controller.maximized:
            self.Maximize()   
        self.Bind(wx.EVT_MAXIMIZE, self.on_maximize)       
        self.Bind(wx.EVT_SIZE, self.on_size)    
        self.Bind(wx.EVT_MOVE, self.on_move)
        #
        self._dialog_main_sizer = wx.BoxSizer(wx.VERTICAL) 
        self.SetSizer(self._dialog_main_sizer)
        # This is will use dialog_main_sizer as Sizer. 
        # See self.AddContainer function to get more details.
        self.mainpanel = self.AddCreateContainer('BoxSizer', 
                                        self, 
                                        proportion=1, 
                                        flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 
                                        border=10
        )
        if controller.flags is not None:
            button_sizer = self.CreateButtonSizer(controller.flags)
            self._dialog_main_sizer.Add(button_sizer, 
                           flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, 
                           border=10
            )    
        self._dialog_main_sizer.Layout()
  
    
    def GetSizer(self):
        """
        Users must get only mainpanel's Sizer. 
        During mainpanel creation, the Sizer given will be _dialog_main_sizer.
        """
        try:
            return self.mainpanel.GetSizer()
        except:
            return self._dialog_main_sizer           


    def get_topic(self):
        return 'dialog_' + str(self._controller_uid[1])

