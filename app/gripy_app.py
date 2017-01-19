# -*- coding: utf-8 -*-

import logging
import wx
from collections import OrderedDict
from FileIO.utils import AsciiFile
from gripy_controller import GripyController
import utils
import gripy_classes
import Plugins


class GripyApp(wx.App):

    _DEFAULT_APP_INIT_FILE = '.gripy_app_ini.json'
    __version__ = '0.5 Development'
    _inited = False
      
    def __init__(self, optional_init_file=None):
        if optional_init_file is None:
            self._app_full_filename =  self._DEFAULT_APP_INIT_FILE
        else:
            self._app_full_filename = optional_init_file           
        self.load_app_state()
        self.set_logging()
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


    def load_app_structure(self, filename):
        print 'Loading GripyApp state from:', filename
        _state = AsciiFile.read_json_file(filename)
        _GC = GripyController(self)
        _GC._UIM._loadstate(_state)


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
        self._init_ended_message()
        logging.info('Starting to register Gripy internal classes...')
        gripy_classes.register_app_classes()
        logging.info('Registering Gripy internal classes ended.')   
        gc = GripyController(self)
                
        # From old MainWindow 
        self.PM = Plugins.PluginManager.get()
        self.pluginnamemap = {}
        self.plugincategorymap = {}        
        #
        
        #self.load_app_state = True        
        self.load_app_state = False

        if self.load_app_state:
            """
            Load basic app from file.            
            """
            self.load_app_structure(self._gripy_app_state.get('app_state_file'))
            mwc = gc._UIM.list('main_window_controller')[0]
        else:
            """
            Construct the application itself.
            """
            mwc = gc.create('main_window_controller', 
                title=self._gripy_app_state.get('app_display_name'),
                icon='./icons/logo-transp.ico'#, pos=wx.Point(399, 322)
                
            )
            

            menubar_ctrl = gc._UIM.create('menubar_controller', mwc.uid)
            
            
      
            mc_file = gc._UIM.create('menu_controller', menubar_ctrl.uid, label=u"&File")      
            

            mc_edit = gc._UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Editar")
            mc_precond = gc._UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Precondicionamento")
            mc_interp = gc._UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Interpretação")
            mc_infer = gc._UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Inferência")
            mc_tools = gc._UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Ferramentas")
            
            mc_plugins = gc._UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Plugins")

            """
            for plugin in sorted(self.PM.getPluginsOfCategory('simpledialog'), 
                                                 key=lambda x: x.name.lower()):
                gc._UIM.create('menu_item_controller', mc_plugins.uid, 
                        label=unicode(plugin.name, 'utf8'), 
                        help=unicode(plugin.description, 'utf8'),
                        callback=plugin.plugin_object.run
                )
           
           
            for plugin in sorted(self.PM.getPluginsOfCategory('autogendata'), 
                                                 key=lambda x: x.name.lower()):
                gc._UIM.create('menu_item_controller', mc_plugins.uid, 
                        label=unicode(plugin.name, 'utf8'), 
                        help=unicode(plugin.description, 'utf8'),
                        callback=plugin.plugin_object.run
                )

            for info in sorted(self.PM.getPluginsOfCategory('default'), 
                                                 key=lambda x: x.name.lower()):

                mic_plugin_item = gc._UIM.create('menu_item_controller', 
                        mc_plugins.uid, 
                        label=unicode(plugin.name, 'utf8'), 
                        help=unicode(plugin.description, 'utf8'),
                        callback=plugin.plugin_object.run
                )
            """    
       

            mc_debug = gc._UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Debug")            
            

            mic_open = gc._UIM.create('menu_item_controller', mc_file.uid, 
                    label=u"&Open", callback='app.functions.on_open'
            )
            
            mic_save = gc._UIM.create('menu_item_controller', mc_file.uid, 
                    label=u"&Salvar", help=u"Salvar arquivo", id=wx.ID_SAVE,
                    callback='app.functions.on_save'
            )   
            
            mic_saveas = gc._UIM.create('menu_item_controller', mc_file.uid, 
                    label=u"&Salvar Como", help=u"Salvar arquivo com nome diferente", 
                    id=wx.ID_SAVEAS, callback='app.functions.on_save_as'
            )    
            
            
            
            mc_import = gc._UIM.create('menu_controller', mc_file.uid, 
                                          label=u"&Importar",
                                          help=u"Importar arquivo"
            )
            mic_open1 = gc._UIM.create('menu_item_controller', mc_import.uid, 
                    label=u"&Open", callback='app.functions.on_open'
            )
            
            #label=u"&Salvar", help=u"Salvar arquivo", id=wx.ID_SAVE,
            #        callback='app.functions.on_save'
            
                        
            
            
            mic_debug = gc._UIM.create('menu_item_controller', mc_debug.uid, 
                    label=u"Debug Console", help=u"Gripy Debug Console", 
                    callback='app.functions.on_debugconsole'
            )    




            '''                            
            menubar_ctrl.create_menu_separator('file')
            menubar_ctrl.create_submenu('file', 'import_menu', text=u"Importar",
                                        help=u"Importar arquivo")
            menubar_ctrl.create_menu_item('file', parent_key='import_menu', key='import_las',                             
                                        text=u"&LAS", help=u"Importar arquivo LAS",
                                        callback=self.on_import_las)
            menubar_ctrl.create_menu_item('file', parent_key='import_menu', key='import_odt',                             
                                        text=u"&ODT", help=u"Importar arquivo ODT",
                                        callback=self.on_import_odt)
            menubar_ctrl.create_menu_item('file', parent_key='import_menu', key='import_lis',                             
                                        text=u"&LIS", help=u"Importar arquivo LIS",
                                        callback=self.on_import_lis)     
            menubar_ctrl.create_menu_item('file', parent_key='import_menu', key='import_seis_segy',                             
                            text=u"&SEG-Y Seismic", help=u"Importar arquivo SEG-Y",
                            callback=self.on_import_seis_segy)

            menubar_ctrl.create_menu_item('file', parent_key='import_menu', key='import_vel_segy',                             
                            text=u"&SEG-Y Velocity", help=u"Importar arquivo SEG-Y",
                            callback=self.on_import_vel_segy)                            
                            
            menubar_ctrl.create_menu_item('file', parent_key='import_menu', key='wilson',                             
                            text=u"&Load Wilson Synthetics", help=u"Load Wilson Synthetics",
                            callback=self.on_load_wilson)  
            menubar_ctrl.create_menu_item('file', parent_key='import_menu', key='avo_inv_wells',                             
                            text=u"&Load AVO Inv Wells", help=u"",
                            callback=self.on_load_avo_inv_wells)  
            menubar_ctrl.create_menu_item('file', parent_key='import_menu', key='test_partition',                             
                            text=u"&Load Partition for testing", help=u"",
                            callback=self.on_test_partition)                              
        
            menubar_ctrl.create_submenu('file', 'export_menu', text=u"Exportar",
                                        help=u"Exportar arquivo")        
            menubar_ctrl.create_menu_item('file', parent_key='export_menu', key='export_las',                             
                                        text=u"&LAS", help=u"Exportar arquivo LAS",
                                        callback=self.on_export_las)                                      
            menubar_ctrl.create_menu_separator('file')
            '''
            # TODO: VERIFICAR self.OnDoClose
            #menubar_ctrl.create_menu_item('file', key='close', text=u"&Fechar", 
            #                              help=u"Fechar o programa", id=wx.ID_CLOSE,
            #                              callback=self.OnDoClose)     
                      
            
            # TreeController                                                          
            gc._UIM.create('tree_controller', mwc.uid)                            
                
             
            # ToolBarController 
            tbc = gc._UIM.create('toolbar_controller', mwc.uid)
            
            gc._UIM.create('toolbartool_controller', tbc.uid,
                           label=u"New project", 
                           bitmap='./icons/aqua_new_file_24.png',
                           help='New project', long_help='Start a new Gripy project, closes existing',
                           callback='app.functions.on_open'
            )            
            
            gc._UIM.create('toolbartool_controller', tbc.uid,
                           label=u"Abrir projeto", 
                           bitmap='./icons/folder_opened_24.png',
                           help='Abrir projeto', long_help='Abrir projeto GriPy',
                           callback='app.functions.on_open'
            )
                        
            gc._UIM.create('toolbartool_controller', tbc.uid,
                           label=u"Salvar projeto", 
                           bitmap='./icons/aqua_new_file_24.png',
                           help='Salvar projeto', long_help='Salvar projeto GriPy',
                           callback='app.functions.on_save'
            )

            gc._UIM.create('toolbartool_controller', tbc.uid,
                           label=u"Visualizar LogPlot", 
                           bitmap='./icons/log_plot_24.png',
                           help='Log Plot', long_help='Log Plot',
                           callback='app.functions.on_new_logplot' #GripyController.on_plo
            )

            gc._UIM.create('toolbartool_controller', tbc.uid,
                           label=u"Visualizar Crossplot", 
                           bitmap='./icons/crossplot_24.png',
                           help='Crossplot', long_help='Crossplot',
                           callback='app.functions.on_open' # GripyController.on_crossplot
            )         

           
            # StatusBarController  
            gc._UIM.create('statusbar_controller', mwc.uid, 
                label='Bem vindo ao ' + self._gripy_app_state.get('app_display_name')
            )        
                
             
        mwc.view.Show()
        self.SetTopWindow(mwc.view)
        # Here, it is necessary to return True as requested by wx.App         
        return True


    def OnExit(self):
        logging.info('GriPy Application is going to terminate....')
        logging.info('GriPy Application has finished.')
        
        
    def set_logging(self):
        # TODO: implement gripy_logging.py (or no)
        """
        logging_level = self._state.get('logging_level', logging.ERROR)
        logging_config_file = self._state.get('logging_config_file', None)
        gripy_logging.setup_logging(logging_level, logging_config_file)

        """
        logging_level = self._logging_state.get('logging_level', None)
        logging_filename = self._logging_state.get('logging_filename', None)
        logging_filemode = self._logging_state.get('logging_filemode', 'a')
        if logging_level is not None:
            if logging_filename is None:
                logging.basicConfig(level=logging_level)
            else:    
                logging.basicConfig(filename=logging_filename, 
                    level=logging_level,
                    filemode=logging_filemode,
                    format='[%(asctime)s] [%(levelname)s] %(message)s ', #[line %(lineno)d in %(pathname)s]',
                    datefmt='%d/%m/%Y %H:%M:%S'
                )        
              
     
    def reload_state(self):
        self._gripy_app_state['app_name'] = self.GetAppName()
        self._gripy_app_state['app_display_name'] = self.GetAppDisplayName()
        self._gripy_app_state['app_version'] = self.__version__
        self._gripy_app_state['class_name'] = self.GetClassName()
        self._gripy_app_state['vendor_name'] = self.GetVendorName()
        self._gripy_app_state['vendor_display_name'] = self.GetVendorDisplayName()
        


    def load_app_state(self):
        try:
            file_dict = AsciiFile.read_json_file(self._app_full_filename)
            self._wx_app_state = OrderedDict(file_dict.get('wx.App'))
            class_full_name = utils.get_class_full_name(self)
            self._gripy_app_state = OrderedDict(file_dict.get(class_full_name))
            self._logging_state = OrderedDict(file_dict.get('logging'))
        except Exception:
            if self._app_full_filename != self._DEFAULT_APP_INIT_FILE:
                self._app_full_filename = self._DEFAULT_APP_INIT_FILE
                self.load_state()
            self._app_full_filename = None
            raise        
            
        
    def save_app_state(self):
        return self.save_state_as(self._app_full_filename)
        
        
    def save_app_state_as(self, fullfilename):
        try:
            _state = self._get_state_dict()
            AsciiFile.write_json_file(_state, fullfilename)
            self._app_full_filename = fullfilename
            msg = 'GripyApp state was saved to file {}'.format(self._app_full_filename)
            logging.info(msg)
            return True
        except Exception, e:
            msg = 'Error in saving GripyApp state to file {}'.format(fullfilename)
            logging.exception(msg)
            raise e       


    def get_app_full_name(self):
        if not self._inited:
            raise Exception('GripyApp has not initializated.')
        return self.GetAppName() + ' ' + self.__version__   


    def _init_ended_message(self):
        _app_name = self.get_app_full_name()    
        logging.info('Welcome to {}.'.format(_app_name))
        logging.info('{} was initializated. Settings loaded are:'.format(_app_name))
        _state = self._get_state_dict()
        for key, value in _state.items():
            msg = '    ' + str(key) + ' = ' + str(value)
            logging.info(msg)
        

    def _get_state_dict(self):
        class_full_name = utils.get_class_full_name(self)
        _state = OrderedDict()
        _state['wx.App'] = self._wx_app_state
        _state[class_full_name] = self._gripy_app_state
        _state['logging'] = self._logging_state
        return _state        



