# -*- coding: utf-8 -*-
import wx
from uimanager import UIManager

#from Algo.Modeling.Reflectivity import Reflectivity2


"""
Load interface data.
"""
def load_application_UI_data(fullfilename):
    pass
    #UIM = UIManager()
    #UIM.load_application_state_from_file(fullfilename)


"""
Load interface data.
"""
def load_user_UI_data(fullfilename):
    pass
    #UIM = UIManager()
    #UIM.load_user_state_from_file(fullfilename)


"""
Save application structure UI data.
"""        
def save_UI_application_data(fullfilename):
    pass
    #UIM = UIManager()
    #UIM.save_application_state_to_file(fullfilename)
 
 
"""
Save user UI data.
"""        
def save_UI_user_data(fullfilename):
    pass
    #UIM = UIManager()
    #UIM.save_user_state_to_file(fullfilename)
    #UIM._save_state_to_file(self.UIM_file)     


"""
Loads Gripy Initial Interface (MainWindow and it's children).
"""
def load():
    #load_UI_file = True        
    load_UI_file = False
    app = wx.App.Get()
    UIM = UIManager()
    
    if load_UI_file:
        """
        Load basic app from file.            
        """
        load_application_UI_data(app._gripy_app_state.get('app_UI_file'))
        load_user_UI_data(app._gripy_app_state.get('user_UI_file'))
        mwc = UIM.list('main_window_controller')[0]      
    else:
        """
        Construct the application itself.
        """    
        UIM = UIManager()
        mwc = UIM.create('main_window_controller', 
                         title=app._gripy_app_state.get('app_display_name')
        )

        # Menubar
        menubar_ctrl = UIM.create('menubar_controller', mwc.uid)
        
        
        # First level Menus
        mc_project = UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Project")      
        mc_edit = UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Edit")
        mc_well = UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Well")
        mc_precond = UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Preconditioning")
        mc_model = UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Modeling")
        mc_interp = UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Interpretation")
        mc_infer = UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Inference")
        #mc_specdecom = UIM.create('menu_controller', menubar_ctrl.uid, label=u"&SpecDecom")
        mc_tools = UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Tools")
        mc_plugins = UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Plugins")
        mc_debug = UIM.create('menu_controller', menubar_ctrl.uid, label=u"&Debug")  
        
        # Project Menu
        UIM.create('menu_item_controller', mc_project.uid, 
                label=u'&New project', 
                help=u'Create a new empty GriPy Project.',
                id=wx.ID_NEW,
                callback='App.menu_functions.on_new'
        )
        UIM.create('menu_item_controller', mc_project.uid, 
                       kind=wx.ITEM_SEPARATOR
        )
        UIM.create('menu_item_controller', mc_project.uid, 
                label=u'&Open', 
                help=u'Open GriPy Project (*.pgg)',
                id=wx.ID_OPEN,
                callback='App.menu_functions.on_open'
        )
        UIM.create('menu_item_controller', mc_project.uid, 
                label=u'&Save', 
                help=u'Save GriPy Project',
                id=wx.ID_SAVE,
                callback='App.menu_functions.on_save'
        )   
        UIM.create('menu_item_controller', mc_project.uid, 
                label=u'&Save as', 
                help=u'Save GriPy Project with a new name',
                id=wx.ID_SAVEAS, 
                callback='App.menu_functions.on_save_as'
        ) 
        UIM.create('menu_item_controller', mc_project.uid, 
                       kind=wx.ITEM_SEPARATOR
        )
        mc_import = UIM.create('menu_controller', mc_project.uid, 
                                      label=u"&Import",
                                      help=u"Import file"
        )
        UIM.create('menu_item_controller', mc_import.uid, 
                label=u"LAS File", 
                help=u'Import a LAS file to current GriPy Project',
                callback='App.menu_functions.on_import_las'
        )
        UIM.create('menu_item_controller', mc_import.uid, 
                label=u"ODT File", 
                help=u'Import a ODT file to current GriPy Project',
                callback='App.menu_functions.on_import_odt'
        )
        # TODO: Falta LIS !!!!
        '''
        UIM.create('menu_item_controller', mc_import.uid, 
                label=u"LIS File", 
                help=u'Import a LIS file to current GriPy Project',
                callback='App.menu_functions.on_import_lis'
        )    
        '''        
        # TODO: Falta DLIS !!!!
        '''
        mic_import_dlis = UIM.create('menu_item_controller', mc_import.uid, 
                label=u"DLIS File", 
                help=u'Import a DLIS file to current GriPy Project',
                callback='App.menu_functions.on_import_dlis'
        )  
        '''
        UIM.create('menu_item_controller', mc_import.uid, 
                label=u"SEG-Y Well Gather", 
                help=u'Import a SEG-Y Seismic file as Well Gather',
                callback='App.menu_functions.on_import_segy_well_gather'
        )  
        UIM.create('menu_item_controller', mc_import.uid, 
                label=u"SEG-Y Seismic", 
                help=u'Import a SEG-Y Seismic file to current GriPy Project',
                callback='App.menu_functions.on_import_segy_seis'
        )  
        UIM.create('menu_item_controller', mc_import.uid, 
                label=u"SEG-Y Velocity", 
                help=u'Import a SEG-Y Velocity file to current GriPy Project',
                callback='App.menu_functions.on_import_segy_vel'
        )  
        mc_export = UIM.create('menu_controller', mc_project.uid, 
                                      label=u"Export",
                                      help=u"Export file"
        )      
        UIM.create('menu_item_controller', mc_export.uid, 
                label=u"LAS File", 
                help=u'Export a LAS file from a well in current GriPy Project',
                callback='App.menu_functions.on_export_las'
        )
        UIM.create('menu_item_controller', mc_project.uid, 
                       kind=wx.ITEM_SEPARATOR
        )
        UIM.create('menu_item_controller', mc_project.uid, 
                label=u'Exit', 
                help=u'Exits GRIPy application.',
                id=wx.ID_EXIT,
                callback='App.menu_functions.on_exit'
        )            
        
        # Edit Menu
        mc_partition = UIM.create('menu_controller', mc_edit.uid, 
                                      label=u"&Partition",
                                      help=u"Create / Edit Partition"
        )
        mc_rocktable = UIM.create('menu_controller', mc_edit.uid, 
                                      label=u"&Rock Table",
                                      help=u"Create / Edit RockTable"
        )
        UIM.create('menu_item_controller', mc_rocktable.uid, 
                label=u"New Rock Table", 
                help=u'New Rock Table',
                callback='App.menu_functions.on_new_rocktable'
        )
        UIM.create('menu_item_controller', mc_rocktable.uid, 
                label=u"Edit Rock Table", 
                help=u'Edit Rock Table',
                callback='App.menu_functions.on_edit_rocktable'
        )
        UIM.create('menu_item_controller', mc_partition.uid, 
                label=u"New Partition", 
                help=u'New Partition',
                callback='App.menu_functions.on_new_partition'
        )
        UIM.create('menu_item_controller', mc_partition.uid, 
                label=u"Edit Partition", 
                help=u'Edit Partitions',
                callback='App.menu_functions.on_edit_partition'
        )
        UIM.create('menu_item_controller', mc_edit.uid, 
                label=u'&Well Plot', 
                help=u'Well Plot',
                callback='App.menu_functions.on_new_wellplot'
        ) 
        UIM.create('menu_item_controller', mc_edit.uid, 
                label=u'&Crossplot', 
                help=u'Crossplot',
                callback='App.menu_functions.on_new_crossplot'
        )            
#        UIM.create('menu_item_controller', mc_edit.uid, 
#                label=u'&Rock', 
#                help=u'Initialize rock model',
#                callback='App.menu_functions.on_rock'
#        )
#        UIM.create('menu_item_controller', mc_edit.uid, 
#                label=u'&Fluid', 
#                help=u'Initialize fluid model',
#                callback='App.menu_functions.on_fluid'
#        )             
        
        # Well Menu
        UIM.create('menu_item_controller', mc_well.uid, 
                   label=u"New well",
                   help=u"Create new well",
                   callback='App.menu_functions.on_create_well'
        ) 

        UIM.create('menu_item_controller', mc_well.uid, 
                label=u"Create Synthetic Log",
                callback='App.menu_functions.on_create_synthetic'
        )
        
        # Inference Menu
        UIM.create('menu_item_controller', mc_infer.uid, 
                label=u"Avo PP", 
                callback='App.menu_functions.teste6'
        )  
        UIM.create('menu_item_controller', mc_infer.uid, 
                label=u"Avo PP-PS", 
                callback='App.menu_functions.teste7'
        )  
        
        # Interpretation Menu
        mc_specdecom = UIM.create('menu_controller', mc_interp.uid,  
                                      label=u"Spectral Decomposition",
                                      help=u"Spectral Decomposition",
        )
        UIM.create('menu_item_controller', mc_specdecom.uid, 
                label=u"Continuous Wavelet Transform", 
                callback='App.menu_functions.on_cwt'
        )          
        mc_attributes = UIM.create('menu_controller', mc_interp.uid,  
                                      label=u"Attributes",
                                      help=u"Attributes",
        )
        UIM.create('menu_item_controller', mc_attributes.uid, 
                label=u"Phase Rotation", 
                callback='App.menu_functions.on_phase_rotation'
        )

        UIM.create('menu_item_controller', mc_attributes.uid, 
                label=u"Hilbert Attributes", 
                callback='App.menu_functions.on_hilbert_attributes'
        )             
        
        # Modeling Menu  
        UIM.create('menu_item_controller', mc_model.uid, 
                label=u"Create 2/3 layers model", 
                callback='App.menu_functions.on_create_model'
        )   
        UIM.create('menu_item_controller', mc_model.uid,
                       kind=wx.ITEM_SEPARATOR
        )        
        UIM.create('menu_item_controller', mc_model.uid,
                label=u"Aki-Richards PP", 
                callback='App.menu_functions.on_akirichards_pp'
        )      
        UIM.create('menu_item_controller', mc_model.uid, 
				label=u"Reflectivity Method", 
				callback='App.menu_functions.ReflectivityModel'
        )
        #UIM.create('menu_item_controller', mc_model.uid,
        #               kind=wx.ITEM_SEPARATOR
        #) 
        #UIM.create('menu_item_controller', mc_model.uid,
        #        label=u"Poisson ratio", 
        #        callback='App.menu_functions.on_poisson_ratio'
        #)            
        

        # Debug Menu
        UIM.create('menu_item_controller', mc_debug.uid, 
                label=u"Debug Console", help=u"Gripy Debug Console", 
                callback='App.menu_functions.on_debugconsole'
        )  
        #
        UIM.create('menu_item_controller', mc_debug.uid, 
                       kind=wx.ITEM_SEPARATOR
        )
        UIM.create('menu_item_controller', mc_debug.uid, 
                label=u"Load Wilson Synthetics", 
                callback='App.menu_functions.on_load_wilson'
        )  
           
        UIM.create('menu_item_controller', mc_debug.uid, 
                label=u"Load Stack North Viking Data", 
                callback='App.menu_functions.teste10'
        )   
        UIM.create('menu_item_controller', mc_debug.uid, 
                label=u"Teste 11", 
                callback='App.menu_functions.teste11'
        ) 
     
        UIM.create('menu_item_controller', mc_debug.uid, 
                label=u'Calc Well Time from Depth curve', 
                callback='App.menu_functions.calc_well_time_from_depth'
        ) 
     
        # Fim Main Menu Bar

        # Object Manager TreeController                                                          
        UIM.create('tree_controller', mwc.uid)                            
            
        # Main ToolBar 
        tbc = UIM.create('toolbar_controller', mwc.uid)
        UIM.create('toolbartool_controller', tbc.uid,
                       label=u"New project", 
                       bitmap='./icons/aqua_new_file_24.png',
                       help='New project', 
                       long_help='Start a new Gripy project, closes existing',
                       callback='App.menu_functions.on_open'
        )            
        UIM.create('toolbartool_controller', tbc.uid,
                       label=u"Abrir projeto", 
                       bitmap='./icons/folder_opened_24.png',
                       help='Abrir projeto', 
                       long_help='Abrir projeto GriPy',
                       callback='App.menu_functions.on_open'
        )
        UIM.create('toolbartool_controller', tbc.uid,
                       label=u"Salvar projeto", 
                       bitmap='./icons/floppy_24.png',
                       help='Salvar projeto', 
                       long_help='Salvar projeto GriPy',
                       callback='App.menu_functions.on_save'
        )
        UIM.create('toolbartool_controller', tbc.uid,
                       label=u"Well Plot", 
                       bitmap='./icons/log_plot_24.png',
                       help='Well Plot', 
                       long_help='Well Plot',
                       callback='App.menu_functions.on_new_wellplot'
        )
        UIM.create('toolbartool_controller', tbc.uid,
                       label=u"Crossplot", 
                       bitmap='./icons/crossplot_24.png',
                       help='Crossplot', 
                       long_help='Crossplot',
                       callback='App.menu_functions.on_new_crossplot'
        )         

        # StatusBar
        UIM.create('statusbar_controller', mwc.uid, 
            label='Bem vindo ao ' + app._gripy_app_state.get('app_display_name')
        )   
        
        #"""


        # """
        # Area reservada para alguns testes 
        # """
        
        #fullfilename = 'C:\\Users\\Adriano\\Desktop\\aaa_teste_5.pgg'
        
        #fullfilename = 'C:\\Users\\Adriano\\Desktop\\aaa_teste_8.pgg'
        
        #fullfilename = 'C:\\Users\\Adriano\\Desktop\\2709_pocos_classes.pgg'
        #app.load_project_data(fullfilename)    

        #
        #lpc = UIM.create('logplot_controller', mwc.uid)
        #tc1 = UIM.create('track_controller', lpc.uid)
        #tc1.model.width = 900
        
        #UIM.create('track_controller', lpc.uid)
        #UIM.create('track_controller', lpc.uid)
        #UIM.create('track_controller', lpc.uid, overview=True, plotgrid=False)

        # CASA
        #mwc.model.pos = (-8, 0)
        #mwc.model.size = (1240, 1046)
        #mwc.model.maximized = False

        # BR
        #mwc.model.pos = (-1925, -921) 
        #mwc.model.size = (1116, 1131) 

        # """    
        # Fim - Testes
        # """


        return mwc
    
    
    
    
