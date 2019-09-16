
import os
from collections import OrderedDict

import wx

from app import app_utils
from app import gripy_functions

from classes import class_register
from classes.om import OMBaseObject
from classes.om import ObjectManager
from classes.ui import UIBaseObject
from classes.ui import UIManager
from classes.ui import interface

from app import DEFS 
from app import log
from app.gripy_plugin_manager import GripyPluginManagerSingleton


class GripyApp(wx.App):
    __version__ = None
    _inited = False
      
    def __init__(self):
        self._wx_app_state = OrderedDict(DEFS.get('wx.App'))
        _redirect = self._wx_app_state.get('redirect', False)
        _filename = self._wx_app_state.get('filename', None) 
        _useBestVisual = self._wx_app_state.get('useBestVisual', False) 
        _clearSigInt = self._wx_app_state.get('clearSigInt', True)
        #
        class_full_name = app_utils.get_class_full_name(self)
        self._gripy_app_state = OrderedDict(DEFS.get(class_full_name))
        self._plugins_state = OrderedDict(DEFS.get('plugins', dict()))
        plugins_places = self._plugins_state.get('plugins_places')
        if plugins_places:
            plugins_places = [str(place) for place in plugins_places]
        else:
            plugins_places = ['Plugins']
        self._plugins_state['plugins_places'] = plugins_places   
        self._logging_state = OrderedDict(DEFS.get('logging', dict()))   
        #   
        super().__init__(_redirect, _filename, 
                                       _useBestVisual, _clearSigInt
        ) 



    def OnInit(self):
        if self._gripy_app_state.get('app_name') is not None:
            self.SetAppName(self._gripy_app_state.get('app_name')) 
        if self._gripy_app_state.get('app_display_name') is not None:
            self.SetAppDisplayName(self._gripy_app_state.get('app_display_name'))       
        if self._gripy_app_state.get('app_version') is not None:    
            self.__version__ = self._gripy_app_state.get('app_version')   
        if self._gripy_app_state.get('vendor_name') is not None:
            self.SetVendorName(self._gripy_app_state.get('vendor_name'))                       
        if self._gripy_app_state.get('vendor_display_name') is not None:
            self.SetVendorDisplayName(self._gripy_app_state.get('vendor_display_name'))           
        class_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)  
        if self._gripy_app_state.get('class_name'):
            class_name = self._gripy_app_state.get('class_name') 
        self.SetClassName(class_name)
        self._gripy_debug_file = self._gripy_app_state.get('gripy_debug_file')
        self._inited = True
        self._init_has_ended_message()
        #
        log.info('Starting to register Gripy internal classes...')
        class_register.register_app_classes()
        log.info('Registering Gripy internal classes ended.')   
        #
        log.info('Starting to register Gripy internal functions...')
        gripy_functions.register_app_functions()
        log.info('Registering Gripy internal functions ended.') 
        #
        log.info('Starting Gripy plugin system...')
        self._init_plugin_system()
        log.info('Plugin system was initializated.') 
        #
        
        self.load_app_interface()
         
        return True



    def load_app_interface(self):
        if not wx.App.Get():
            raise Exception('ERROR: wx.App not found.')
            
        interface.load()
        mwc = interface.get_main_window_controller()
        mwc.Show()
        self.SetTopWindow(mwc.view)       


    """
    Init plugin system
    """
    def _init_plugin_system(self):
        PM = GripyPluginManagerSingleton.get()
        plugins_places = self._plugins_state.get('plugins_places')
        PM.setPluginPlaces(plugins_places)
        PM.setPluginPlaces(['Plugins'])
        ok, exists_previously, error = PM.collectPlugins()   
        

    def get_project_filename(self):
        return wx.EmptyString
        

    """
    Load ObjectManager data.
    """
    # Falta unload data
    def load_project_data(self, fullfilename):
        OM = ObjectManager()
        UIM = UIManager()
        self.OM_file = fullfilename
        ret = OM.load(self.OM_file)
        if not ret:
            msg = 'GRIPy project cannot be opened.'
            wx.MessageBox(msg, 'Error', wx.OK | wx.ICON_ERROR)
            return
        mwc = UIM.list('main_window_controller')[0]
        tree_ctrl = UIM.list('tree_controller', mwc.uid)[0]
        if tree_ctrl:        
            tree_ctrl.set_project_name(self.OM_file)
                  
            
    """
    Save ObjectManager data.
    """                  
    def save_project_data(self, fullfilename=None):
        if fullfilename:
            self.OM_file = fullfilename
        if self.OM_file:
            OM = ObjectManager()
            OM.save(self.OM_file)


    """
    When the MainWindow calls the function below, GripyApp will close UIManager 
    but not finish the wx.App.
    This job must be done by Wx. (don't try to change it!)
    """
    def PreExit(self):
        msg = 'GriPy Application is preparing to terminate....'
        log.info(msg)
        
        OM = ObjectManager()
        UIM = UIManager()
        UIM.PreExit()
        OM._reset()
        

    def OnExit(self):
        msg = 'GriPy Application has finished.'
        log.info(msg)
        return super().OnExit()
        
    
    # Convenience function    
    def getLogger(self):    
        return log
        
    # Convenience function    
    def getPluginManager(self):
        return GripyPluginManagerSingleton.get()
        
    
    def reload_state(self):
        self._gripy_app_state['app_name'] = self.GetAppName()
        self._gripy_app_state['app_display_name'] = self.GetAppDisplayName()
        self._gripy_app_state['app_version'] = self.__version__
        self._gripy_app_state['class_name'] = self.GetClassName()
        self._gripy_app_state['vendor_name'] = self.GetVendorName()
        self._gripy_app_state['vendor_display_name'] = self.GetVendorDisplayName()
          
          
    def get_app_full_name(self):
        if not self._inited:
            raise Exception('GripyApp has not initializated.')
        return self.GetAppName() + ' ' + self.__version__   


    def _init_has_ended_message(self):
        _app_name = self.get_app_full_name()    
        log.info('Welcome to {}.'.format(_app_name))
        log.info('{} was initializated. Settings loaded are:'.format(_app_name))
        _state = self._get_state_dict()
        for key, value in _state.items():
            msg = '    ' + str(key) + ' = ' + str(value)
            log.info(msg)
        

    def _get_state_dict(self):
        class_full_name = app_utils.get_class_full_name(self)
        _state = OrderedDict()
        _state['wx.App'] = self._wx_app_state
        _state[class_full_name] = self._gripy_app_state
        _state['logging'] = self._logging_state
        return _state        


    def on_save(self):
        if self.get_project_filename():
            disableAll = wx.WindowDisabler()
            wait = wx.BusyInfo("Saving GriPy project. Wait...")
            self.save_project_data()
            del wait
            del disableAll
        else:
            self.on_save_as()
        
    
    def on_save_as(self):
        if self.get_project_filename():
            dir_name, file_name = os.path.split(self.get_project_filename())
        style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        wildcard = "Arquivo de projeto do GRIPy (*.pgg)|*.pgg"
        
        fdlg = wx.FileDialog(self.GetTopWindow(), 
                             'Escolha o arquivo PGG', 
                            #dir_name, file_name, 
                            wildcard=wildcard, style=style
        )
        
        if fdlg.ShowModal() == wx.ID_OK:
            
            file_name = fdlg.GetFilename()
            dir_name = fdlg.GetDirectory()
            if not file_name.endswith('.pgg'):
                file_name += '.pgg'
            disableAll = wx.WindowDisabler()
            wait = wx.BusyInfo("Saving GriPy project. Wait...")    
            self.save_project_data(os.path.join(dir_name, file_name))
            del wait
            del disableAll
            
        fdlg.Destroy()   


    def get_manager_class(self, obj_tid):
        if obj_tid in ObjectManager._types:
            return ObjectManager
        elif obj_tid in UIManager._types:
            return UIManager    
        raise Exception('App.gripy_app.get_manager_class: Class {} has a '+\
                        'unknown manager.'.format(obj_tid)
        )
    
    