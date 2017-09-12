# -*- coding: utf-8 -*-
import os
import wx
from collections import OrderedDict
import app_utils
import gripy_classes
import gripy_functions
from OM.Manager import ObjectManager
from UI.uimanager import UIManager
from UI import Interface
from App import DEFS 
from App import log
from gripy_plugin_manager import GripyPluginManagerSingleton
wx.SystemOptions.SetOption("msw.remap", '0')


class GripyApp(wx.App):
    __version__ = None
    _inited = False
      
    def __init__(self):
        self.OM_file = None
        self._wx_app_state = OrderedDict(DEFS.get('wx.App'))
        class_full_name = app_utils.get_class_full_name(self)
        self._gripy_app_state = OrderedDict(DEFS.get(class_full_name))
        self._plugins_state = OrderedDict(DEFS.get('plugins', dict()))
        plugins_places = self._plugins_state.get('plugins_places')
        if plugins_places:
            plugins_places = [place.encode('utf-8') for place in plugins_places]
        else:
            plugins_places = ['Plugins']
        self._plugins_state['plugins_places'] = plugins_places   
        self._logging_state = OrderedDict(DEFS.get('logging', dict()))   
        #
        self._app_dir = os.getcwd()
        # wx.App args    
        _redirect = self._wx_app_state.get('redirect', False)
        _filename = self._wx_app_state.get('filename', None) 
        _useBestVisual = self._wx_app_state.get('useBestVisual', False) 
        _clearSigInt = self._wx_app_state.get('clearSigInt', True)
        # wx.App.__init__()        
        super(GripyApp, self).__init__(_redirect, _filename, 
                                       _useBestVisual, _clearSigInt
        )
        # Then, wx.App has inited and it calls OnInit

        
    # TODO: REVER ISSO E COLOCAR COMO wx.Config ou wx.StandardPaths
    #def set_app_dir():
    #    wx.App.Get()._app_dir = os.getcwd()
        """        
        print 'a1:', os.getcwd()
        sp = wx.StandardPaths.Get()
        sp.SetInstallPrefix(os.getcwd())
        print type(wx.App.Get())
        print wx.App.Get()
        
        print '\n\n\n'
        for f in ['GetConfigDir',
                  'GetUserConfigDir',
                  'GetDataDir',
                  'GetLocalDataDir',
                  'GetUserDataDir',
                  'GetUserLocalDataDir',
                  'GetDocumentsDir',
                  'GetPluginsDir',
                  'GetInstallPrefix',
                  'GetResourcesDir',
                  'GetTempDir',
                  'GetExecutablePath',
        ]:
            func = getattr(sp, f)
            print f, func()
        """    
        '''    
        print 'ExecutablePath:', sp.GetExecutablePath()
        print 'UserConfigDir:', sp.GetUserConfigDir()
        print 'DataDir:', sp.GetDataDir()
        print 'PluginsDir:', sp.GetPluginsDir()
        print 'InstallPrefix:', sp.GetInstallPrefix()
        '''
        #print os.getcwd()
        # print '\n\n\n'
        
        
    @staticmethod    
    def get_app_dir():
        return wx.App.Get()._app_dir
        

    def get_project_filename(self):
        return self.OM_file
        
        
    #def get_interface_filename(self):
    #    return self.UIM_file
 
    '''
    def _load_app_definitions(self):
        self.OM_file = None
        #self.UIM_file = None
        self._wx_app_state = OrderedDict(DEFS.get('wx.App'))
        class_full_name = app_utils.get_class_full_name(self)
        self._gripy_app_state = OrderedDict(DEFS.get(class_full_name))
        self._plugins_state = OrderedDict(DEFS.get('plugins', dict()))
        plugins_places = self._plugins_state.get('plugins_places')
        if plugins_places:
            plugins_places = [place.encode('utf-8') for place in plugins_places]
        else:
            plugins_places = ['Plugins']
        self._plugins_state['plugins_places'] = plugins_places   
        self._logging_state = OrderedDict(DEFS.get('logging', dict()))      
    '''
          
    '''          
    def save_app_state(self):
        return self.save_state_as(self._app_full_filename)
        
        
    def save_app_state_as(self, fullfilename):
        try:
            _state = self._get_state_dict()
            AsciiFile.write_json_file(_state, fullfilename)
            self._app_full_filename = fullfilename
            msg = 'GripyApp state was saved to file {}'.format(self._app_full_filename)
            self.loginfo(msg)
            return True
        except Exception, e:
            msg = 'Error in saving GripyApp state to file {}'.format(fullfilename)
            self.logexception(msg)
            raise e     
    '''        

    """
    Load ObjectManager data.
    """
    # Falta unload data
    def load_project_data(self, fullfilename):
        OM = ObjectManager(self)
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
            OM = ObjectManager(self)
            OM.save(self.OM_file)


    def OnInit(self):
        self._app_dir = os.getcwd()
        #self.set_app_dir()  # TODO: REVER ISSO CONFORME ACIMA NA FUNÇÃO
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
        gripy_classes.register_app_classes()
        log.info('Registering Gripy internal classes ended.')   
        #
        log.info('Starting to register Gripy internal functions...')
        gripy_functions.register_app_functions()
        log.info('Registering Gripy internal functions ended.')          
        #
        mwc = Interface.load()
        PM = GripyPluginManagerSingleton.get()
        plugins_places = self._plugins_state.get('plugins_places')
        PM.setPluginPlaces(plugins_places)
        #PM.setPluginPlaces(['Plugins'])
        PM.collectPlugins()   
        mwc.view.Show()
        self.SetTopWindow(mwc.view)
        # Here, it is necessary to return True as requested by wx.App         
        return True


    """
    When the MainWindow calls the function below, GripyApp will close UIManager 
    but not finish the wx.App.
    This job must be done by Wx. (don't try to change it!)
    """
    def PreExit(self):
        msg = 'GriPy Application is preparing to terminate....'
        log.info(msg)
        print '\n', msg
        OM = ObjectManager(self)
        if OM.get_changed_flag():
            dial = wx.MessageDialog(self.GetTopWindow(), 
                                    'Do you want to save your project?', 
                                    'GriPy', 
                                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
            )
            if dial.ShowModal() == wx.ID_YES:
                self.on_save()   
        #
        self.reset_ObjectManager()
        #
        app_UI_filename = self._gripy_app_state.get('app_UI_file')
        Interface.save_UI_application_data(app_UI_filename)

        user_UI_filename = self._gripy_app_state.get('user_UI_file')
        Interface.save_UI_user_data(user_UI_filename)
        
        # This time I choose not use the line below because there was a little
        # freeze on exiting (1-2 seconds). Then I opted delegate it do compiler.
        #UIM = UIManager()      
        #UIM.close()
        UIM = UIManager()  
        UIM.PreExit()
        
        # As indicated by https://forums.wxwidgets.org/viewtopic.php?t=32138        
        aui_manager = wx.aui.AuiManager.GetManager(self.GetTopWindow())
        aui_manager.UnInit()        
        
        
    def OnExit(self):
        msg = 'GriPy Application has finished.'
        log.info(msg)
        print msg, '\n'
        return super(GripyApp, self).OnExit()
        
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


    def reset_ObjectManager(self):
        OM = ObjectManager(self)
        OM._reset()
