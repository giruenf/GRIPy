# -*- coding: utf-8 -*-

import wx

import app
from classes.ui import UIManager

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
    
    gripy_app = wx.GetApp()
    #gripy_app = app.gripy_app.GripyApp.Get()
    
    if not gripy_app:
        raise Exception('ERRO grave.')
    
    
    UIM = UIManager()
    
    if load_UI_file:
        """
        Load basic app from file.            
        """
        load_application_UI_data(gripy_app._gripy_app_state.get('app_UI_file'))
        load_user_UI_data(gripy_app._gripy_app_state.get('user_UI_file'))
        mwc = UIM.list('main_window_controller')[0]      
    else:
        """
        Construct the application itself.
        """    
        mwc = UIM.create('main_window_controller', 
                         title=gripy_app._gripy_app_state.get('app_display_name'),
                         
                         pos=(2000, 800), maximized=True
        )

       # """

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
                callback='app.menu_functions.on_new'
        )
        UIM.create('menu_item_controller', mc_project.uid, 
                       kind=wx.ITEM_SEPARATOR
        )
        UIM.create('menu_item_controller', mc_project.uid, 
                label=u'&Open', 
                help=u'Open GriPy Project (*.pgg)',
                id=wx.ID_OPEN,
                callback='app.menu_functions.on_open'
        )
        UIM.create('menu_item_controller', mc_project.uid, 
                label=u'&Save', 
                help=u'Save GriPy Project',
                id=wx.ID_SAVE,
                callback='app.menu_functions.on_save'
        )   
        UIM.create('menu_item_controller', mc_project.uid, 
                label=u'&Save as', 
                help=u'Save GriPy Project with a new name',
                id=wx.ID_SAVEAS, 
                callback='app.menu_functions.on_save_as'
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
                callback='app.menu_functions.on_import_las'
        )
        UIM.create('menu_item_controller', mc_import.uid, 
                label=u"ODT File", 
                help=u'Import a ODT file to current GriPy Project',
                callback='app.menu_functions.on_import_odt'
        )
        # TODO: Falta LIS !!!!
        '''
        UIM.create('menu_item_controller', mc_import.uid, 
                label=u"LIS File", 
                help=u'Import a LIS file to current GriPy Project',
                callback='app.menu_functions.on_import_lis'
        )    
        '''        
        # TODO: Falta DLIS !!!!
        '''
        mic_import_dlis = UIM.create('menu_item_controller', mc_import.uid, 
                label=u"DLIS File", 
                help=u'Import a DLIS file to current GriPy Project',
                callback='app.menu_functions.on_import_dlis'
        )  
        '''
        UIM.create('menu_item_controller', mc_import.uid, 
                label=u"SEG-Y Well Gather", 
                help=u'Import a SEG-Y Seismic file as Well Gather',
                callback='app.menu_functions.on_import_segy_well_gather'
        )  
        UIM.create('menu_item_controller', mc_import.uid, 
                label=u"SEG-Y Seismic", 
                help=u'Import a SEG-Y Seismic file to current GriPy Project',
                callback='app.menu_functions.on_import_segy_seis'
        )  
        UIM.create('menu_item_controller', mc_import.uid, 
                label=u"SEG-Y Velocity", 
                help=u'Import a SEG-Y Velocity file to current GriPy Project',
                callback='app.menu_functions.on_import_segy_vel'
        )  
        mc_export = UIM.create('menu_controller', mc_project.uid, 
                                      label=u"Export",
                                      help=u"Export file"
        )      
        UIM.create('menu_item_controller', mc_export.uid, 
                label=u"LAS File", 
                help=u'Export a LAS file from a well in current GriPy Project',
                callback='app.menu_functions.on_export_las'
        )
        
        
        
        
        UIM.create('menu_item_controller', mc_project.uid, 
                       kind=wx.ITEM_SEPARATOR
        )
        UIM.create('menu_item_controller', mc_project.uid, 
                label=u'Exit', 
                help=u'Exits GRIPy application.',
                id=wx.ID_EXIT,
                callback='app.menu_functions.on_exit'
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
                callback='app.menu_functions.on_new_rocktable'
        )
        UIM.create('menu_item_controller', mc_rocktable.uid, 
                label=u"Edit Rock Table", 
                help=u'Edit Rock Table',
                callback='app.menu_functions.on_edit_rocktable'
        )
        UIM.create('menu_item_controller', mc_partition.uid, 
                label=u"New Partition", 
                help=u'New Partition',
                callback='app.menu_functions.on_new_partition'
        )
        UIM.create('menu_item_controller', mc_partition.uid, 
                label=u"Edit Partition", 
                help=u'Edit Partitions',
                callback='app.menu_functions.on_edit_partition'
        )
        UIM.create('menu_item_controller', mc_edit.uid, 
                label=u'&Well Plot', 
                help=u'Well Plot',
                callback='app.menu_functions.on_new_wellplot'
        ) 
        UIM.create('menu_item_controller', mc_edit.uid, 
                label=u'&Crossplot', 
                help=u'Crossplot',
                callback='app.menu_functions.on_new_crossplot'
        )            
#        UIM.create('menu_item_controller', mc_edit.uid, 
#                label=u'&Rock', 
#                help=u'Initialize rock model',
#                callback='app.menu_functions.on_rock'
#        )
#        UIM.create('menu_item_controller', mc_edit.uid, 
#                label=u'&Fluid', 
#                help=u'Initialize fluid model',
#                callback='app.menu_functions.on_fluid'
#        )             
        
        
        # Well Menu
        UIM.create('menu_item_controller', mc_well.uid, 
                   label=u"New well",
                   help=u"Create new well",
                   callback='app.menu_functions.on_create_well'
        ) 

        UIM.create('menu_item_controller', mc_well.uid, 
                label=u"Create Synthetic Log",
                callback='app.menu_functions.on_create_synthetic'
        )
        
        
        ### Trabalho Roseane
        UIM.create('menu_item_controller', mc_well.uid, 
                       kind=wx.ITEM_SEPARATOR
        )
        
        UIM.create('menu_item_controller', mc_well.uid, 
                label=u'PoroPerm Cross-Plot',
                callback='app.menu_functions.create_poro_perm_xplot'
        )           
        
        UIM.create('menu_item_controller', mc_well.uid, 
                label=u'Winland Cross-Plot',
                callback='app.menu_functions.create_winland_xplot'
        )        
        UIM.create('menu_item_controller', mc_well.uid, 
                label=u'Stratigraphic Modified lorenz Plot (SMLP)',
                callback='app.menu_functions.create_SMLP_xplot'
        )        
        UIM.create('menu_item_controller', mc_well.uid, 
                label=u'Modified lorenz Plot (MLP)',
                callback='app.menu_functions.create_MLP_xplot'
        )          
        UIM.create('menu_item_controller', mc_well.uid, 
                label=u'Depth vs Acumulated KH',
                callback='app.menu_functions.create_Depth_vs_kHAcum_xplot'
        )      


    
        ### FIM - Trabalho Roseane
        
        
        
        # Inference Menu
        UIM.create('menu_item_controller', mc_infer.uid, 
                label=u"Avo PP", 
                callback='app.menu_functions.teste6'
        )  
        UIM.create('menu_item_controller', mc_infer.uid, 
                label=u"Avo PP-PS", 
                callback='app.menu_functions.teste7'
        )  
        
        
        # Interpretation Menu
        mc_specdecom = UIM.create('menu_controller', mc_interp.uid,  
                                      label=u"Spectral Decomposition",
                                      help=u"Spectral Decomposition",
        )
        UIM.create('menu_item_controller', mc_specdecom.uid, 
                label=u"Continuous Wavelet Transform", 
                callback='app.menu_functions.on_cwt'
        )          
        mc_attributes = UIM.create('menu_controller', mc_interp.uid,  
                                      label=u"Attributes",
                                      help=u"Attributes",
        )
        UIM.create('menu_item_controller', mc_attributes.uid, 
                label=u"Phase Rotation", 
                callback='app.menu_functions.on_phase_rotation'
        )

        UIM.create('menu_item_controller', mc_attributes.uid, 
                label=u"Hilbert Attributes", 
                callback='app.menu_functions.on_hilbert_attributes'
        )             
        
        # Modeling Menu  
        UIM.create('menu_item_controller', mc_model.uid, 
                label=u"Create 2/3 layers model", 
                callback='app.menu_functions.on_create_model'
        )   
        UIM.create('menu_item_controller', mc_model.uid,
                       kind=wx.ITEM_SEPARATOR
        )        
        UIM.create('menu_item_controller', mc_model.uid,
                label=u"Aki-Richards PP", 
                callback='app.menu_functions.on_akirichards_pp'
        )      
        UIM.create('menu_item_controller', mc_model.uid, 
				label=u"Reflectivity Method", 
				callback='app.menu_functions.ReflectivityModel'
        )
        #UIM.create('menu_item_controller', mc_model.uid,
        #               kind=wx.ITEM_SEPARATOR
        #) 
        #UIM.create('menu_item_controller', mc_model.uid,
        #        label=u"Poisson ratio", 
        #        callback='app.menu_functions.on_poisson_ratio'
        #)            



        # Debug Menu
        UIM.create('menu_item_controller', mc_debug.uid, 
                label=u"Debug Console", help=u"Gripy Debug Console", 
                callback='app.menu_functions.on_debugconsole'
        )  
        #
        UIM.create('menu_item_controller', mc_debug.uid, 
                       kind=wx.ITEM_SEPARATOR
        )
        UIM.create('menu_item_controller', mc_debug.uid, 
                label=u"Load Wilson Synthetics", 
                callback='app.menu_functions.on_load_wilson'
        )  
           
        UIM.create('menu_item_controller', mc_debug.uid, 
                label=u"Load Stack North Viking Data", 
                callback='app.menu_functions.teste10'
        )   
        UIM.create('menu_item_controller', mc_debug.uid, 
                label=u"Teste 11", 
                callback='app.menu_functions.teste11'
        ) 
     
        UIM.create('menu_item_controller', mc_debug.uid, 
                label=u'Calc Well Time from Depth curve', 
                callback='app.menu_functions.calc_well_time_from_depth'
        ) 
     
        # Fim Main Menu Bar

       

        # Object Manager TreeController                                                          
        UIM.create('tree_controller', mwc.uid)                            
            
        # Main ToolBar 
        tbc = UIM.create('toolbar_controller', mwc.uid)
        UIM.create('toolbartool_controller', tbc.uid,
                       label=u"New project", 
                       bitmap='new_file-30.png',
                       help='New project', 
                       long_help='Start a new Gripy project, closes existing',
                       callback='app.menu_functions.on_new'
        )            
        UIM.create('toolbartool_controller', tbc.uid,
                       label=u"Abrir projeto", 
                       bitmap='open_folder-30.png',
                       help='Abrir projeto', 
                       long_help='Abrir projeto GriPy',
                       callback='app.menu_functions.on_open'
        )
        UIM.create('toolbartool_controller', tbc.uid,
                       label=u"Salvar projeto", 
                       bitmap='save_close-30.png',
                       help='Salvar projeto', 
                       long_help='Salvar projeto GriPy',
                       callback='app.menu_functions.on_save'
        )
        UIM.create('toolbartool_controller', tbc.uid,
                       label=u"Well Plot", 
                       bitmap='oil_rig-30.png',
                       help='Well Plot', 
                       long_help='Well Plot',
                       callback='app.menu_functions.on_new_wellplot'
        )
        UIM.create('toolbartool_controller', tbc.uid,
                       label=u"Crossplot", 
                       bitmap='scatter_plot-30.png',
                       help='Crossplot', 
                       long_help='Crossplot',
                       callback='app.menu_functions.on_new_crossplot'
        )               


        # StatusBar
        UIM.create('statusbar_controller', mwc.uid, 
            label='Bem vindo ao ' + \
            app.gripy_app.GripyApp.Get()._gripy_app_state.get('app_display_name')
        )  
        
        
        

    _do_initial_tests()




def get_main_window_controller():    
    UIM = UIManager()
    mwc = UIM.list('main_window_controller')[0]   
    return mwc
   
    
    
"""
Funcao reservada para alguns testes 
"""
def _do_initial_tests():
   # pass
   
    mwc = get_main_window_controller()
    mwc.model.size = (1000, 700)
  
    
    depth = [
        2240.07,
        2240.22,
        2240.38,
        2240.53,
        2240.68,
        2240.83,
        2240.99,
        2241.14,
        2241.29,
        2241.44,
        2241.60,
        2241.75,
        2241.90,
        2242.05,
        2242.21,
        2242.36,
        2242.51,
        2242.66,
        2242.81,
        2242.97,
        2243.12,
        2243.27,
        2243.42,
        2243.58,
        2243.73,
        2243.88,
        2244.03,
        2244.19,
        2244.34,
        2244.49,
        2244.64,
        2244.80,
        2244.95,
        2245.10,
        2245.25,
        2245.41,
        2245.56,
        2245.71,
        2245.86,
        2246.02,
        2246.17,
        2246.32,
        2246.47,
        2246.62,
        2246.78,
        2246.93,
        2247.08,
        2247.23,
        2247.39,
        2247.54,
        2247.69,
        2247.84,
        2248.00,
        2248.15,
        2248.30,
        2248.45,
        2248.61,
        2248.76,
        2248.91,
        2249.06,
        2249.22,
        2249.37,
        2249.52,
        2249.67,
        2249.83,
        2249.98,
        2250.13,
        2250.28,
        2250.43,
        2250.59,
        2250.74,
        2250.89,
        2251.04,
        2251.20,
        2251.35,
        2251.50,
        2251.65,
        2251.81,
        2251.96,
        2252.11,
        2252.26,
        2252.42,
        2252.57,
        2252.72,
        2252.87,
        2253.03,
        2253.18,
        2253.33,
        2253.48,
        2253.64,
        2253.79,
        2253.94,
        2254.09,
        2254.24,
        2254.40,
        2254.55,
        2254.70,
        2254.85,
        2255.01,
        2255.16,
        2255.31,
        2255.46,
        2255.62,
        2255.77,
        2255.92,
        2256.07,
        2256.23,
        2256.38,
        2256.53,
        2256.68,
        2256.84,
        2256.99,
        2257.14,
        2257.29,
        2257.45,
        2257.60,
        2257.75,
        2257.90,
        2258.05,
        2258.21,
        2258.36,
        2258.51,
        2258.66,
        2258.82,
        2258.97,
        2259.12,
        2259.27,
        2259.43,
        2259.58,
        2259.73,
        2259.88,
        2260.04,
        2260.19,
        2260.34,
        2260.49,
        2260.65,
        2260.80,
        2260.95,
        2261.10,
        2261.26,
        2261.41,
        2261.56,
        2261.71,
        2261.86,
        2262.02,
        2262.17,
        2262.32,
        2262.47,
        2262.63,
        2262.78,
        2262.93,
        2263.08,
        2263.24,
        2263.39,
        2263.54,
        2263.69,
        2263.85,
        2264.00,
        2264.15,
        2264.30,
        2264.46,
        2264.61,
        2264.76,
        2264.91,
        2265.07,
        2265.22,
        2265.37,
        2265.52,
        2265.67,
        2265.83,
        2265.98,
        2266.13,
        2266.28,
        2266.44,
        2266.59,
        2266.74,
        2266.89,
        2267.05,
        2267.20,
        2267.35,
        2267.50,
        2267.66,
        2267.81,
        2267.96,
        2268.11,
        2268.27,
        2268.42,
        2268.57,
        2268.72,
        2268.88,
        2269.03,
        2269.18,
        2269.33,
        2269.48,
        2269.64,
        2269.79,
        2269.94,
        2270.09,
        2270.25,
        2270.40,
        2270.55,
        2270.70,
        2270.86,
        2271.01,
        2271.16,
        2271.31,
        2271.47,
        2271.62,
        2271.77,
        2271.92,
        2272.08,
        2272.23,
        2272.38,
        2272.53,
        2272.69,
        2272.84,
        2272.99,
        2273.14,
        2273.29,
        2273.45,
        2273.60,
        2273.75,
        2273.90,
        2274.06,
        2274.21,
        2274.36,
        2274.51,
        2274.67,
        2274.82,
        2274.97,
        2275.12,
        2275.28,
        2275.43,
        2275.58,
        2275.73,
        2275.89,
        2276.04,
        2276.19,
        2276.34,
        2276.50,
        2276.65,
        2276.80,
        2276.95,
        2277.10,
        2277.26,
        2277.41,
        2277.56,
        2277.71,
        2277.87,
        2278.02,
        2278.17,
        2278.32,
        2278.48,
        2278.63,
        2278.78,
        2278.93,
        2279.09,
        2279.24,
        2279.39,
        2279.54,
        2279.70,
        2279.85,
        2280.00,
        2280.15,
        2280.31,
        2280.46,
        2280.61,
        2280.76,
        2280.91,
        2281.07,
        2281.22,
        2281.37,
        2281.52,
        2281.68,
        2281.83,
        2281.98,
        2282.13,
        2282.29,
        2282.44,
        2282.59,
        2282.74,
        2282.90,
        2283.05,
        2283.20,
        2283.35,
        2283.51,
        2283.66,
        2283.81,
        2283.96,
        2284.12,
        2284.27,
        2284.42,
        2284.57,
        2284.72,
        2284.88,
        2285.03            
            
    ] 
   
    phi = [
        12.71,
        13.03,
        13.91,
        14.24,
        14.14,
        14.05,
        13.56,
        14.80,
        18.43,
        18.44,
        18.44,
        21.12,
        21.15,
        17.38,
        15.26,
        13.14,
        13.79,
        13.79,
        17.52,
        20.47,
        23.41,
        25.46,
        25.37,
        25.39,
        25.40,
        25.40,
        27.12,
        30.32,
        29.79,
        29.28,
        28.77,
        28.77,
        27.44,
        28.19,
        28.16,
        28.13,
        28.36,
        28.37,
        26.91,
        24.28,
        21.66,
        16.64,
        13.95,
        13.96,
        16.51,
        19.06,
        23.68,
        25.13,
        19.13,
        19.13,
        19.13,
        11.90,
        9.31,
        9.70,
        11.75,
        13.81,
        13.82,
        18.41,
        21.13,
        20.91,
        20.69,
        20.68,
        20.37,
        21.27,
        21.83,
        22.39,
        20.46,
        20.46,
        16.11,
        14.51,
        12.92,
        12.37,
        12.38,
        14.83,
        15.59,
        16.35,
        15.95,
        14.55,
        14.56,
        14.06,
        13.56,
        11.95,
        11.58,
        11.58,
        11.53,
        11.47,
        11.62,
        11.91,
        11.91,
        12.19,
        12.48,
        11.73,
        11.46,
        11.47,
        11.22,
        10.96,
        9.73,
        13.72,
        13.73,
        16.19,
        18.65,
        18.03,
        13.38,
        13.38,
        12.02,
        10.66,
        10.46,
        10.19,
        10.19,
        10.04,
        9.89,
        9.97,
        9.97,
        10.42,
        10.55,
        10.67,
        10.72,
        10.72,
        10.56,
        10.65,
        10.75,
        11.36,
        11.36,
        11.22,
        11.09,
        10.96,
        9.82,
        9.82,
        7.87,
        7.16,
        6.46,
        5.33,
        5.33,
        4.40,
        3.59,
        2.77,
        2.37,
        2.37,
        5.29,
        7.49,
        9.69,
        10.75,
        10.76,
        8.09,
        6.05,
        4.00,
        1.81,
        1.81,
        1.41,
        2.65,
        3.90,
        5.53,
        5.52,
        7.33,
        7.22,
        7.10,
        7.38,
        7.39,
        6.75,
        7.39,
        8.02,
        11.19,
        11.20,
        11.50,
        10.28,
        9.05,
        6.72,
        6.72,
        7.45,
        7.65,
        7.84,
        7.10,
        7.10,
        5.83,
        5.72,
        5.61,
        4.59,
        4.10,
        4.10,
        4.79,
        5.48,
        6.55,
        7.06,
        7.06,
        7.21,
        7.36,
        8.14,
        9.52,
        10.88,
        10.88,
        10.89,
        11.31,
        11.47,
        11.27,
        11.27,
        11.27,
        11.02,
        10.32,
        10.17,
        11.47,
        12.78,
        12.78,
        16.69,
        19.24,
        20.08,
        20.92,
        20.92,
        20.50,
        19.54,
        19.01,
        18.48,
        19.14,
        19.14,
        21.05,
        22.17,
        23.28,
        24.52,
        24.55,
        24.56,
        23.37,
        22.18,
        19.87,
        20.66,
        25.14,
        27.49,
        29.85,
        29.85,
        27.70,
        20.82,
        18.12,
        15.42,
        17.81,
        17.81,
        24.27,
        26.65,
        29.04,
        30.60,
        30.29,
        29.74,
        29.55,
        29.35,
        29.35,
        29.75,
        30.04,
        30.74,
        31.44,
        32.84,
        34.00,
        33.49,
        33.49,
        33.49,
        31.75,
        30.09,
        29.21,
        29.32,
        29.43,
        29.69,
        29.54,
        29.54,
        29.33,
        29.11,
        29.05,
        29.68,
        30.06,
        29.81,
        29.55,
        28.75,
        28.50,
        28.76,
        28.76,
        28.77,
        28.43,
        27.98,
        26.45,
        25.01,
        23.57,
        20.54,
        19.43,
        20.82,
        21.88,
        22.94,
        23.35,
        21.23,
        17.69,
        17.69,
        17.69,
        15.08,
        13.85,
        13.22,
        14.04,
        14.86,
        16.63,
        15.77,
        12.90,
        11.81,
        10.72     
    ]
    

    k = [
        3.17,
        3.73,
        5.40,
        6.05,
        6.04,
        6.03,
        4.90,
        6.40,
        21.92,
        21.94,
        21.96,
        39.61,
        35.40,
        9.82,
        5.63,
        1.45,
        4.24,
        4.24,
        22.42,
        58.34,
        94.26,
        151.13,
        143.73,
        117.33,
        117.42,
        117.51,
        125.67,
        215.58,
        158.82,
        155.51,
        152.19,
        152.12,
        120.77,
        180.07,
        207.44,
        234.81,
        256.96,
        257.26,
        128.33,
        85.05,
        41.76,
        15.27,
        7.26,
        7.27,
        20.29,
        33.32,
        88.98,
        155.43,
        36.55,
        36.55,
        36.54,
        1.99,
        0.00,
        0.00,
        1.49,
        2.97,
        2.98,
        17.56,
        40.01,
        37.44,
        34.87,
        34.84,
        28.78,
        42.96,
        61.04,
        79.13,
        49.58,
        49.58,
        12.45,
        7.08,
        1.70,
        0.47,
        0.47,
        3.35,
        5.34,
        7.33,
        7.46,
        3.98,
        3.99,
        2.77,
        1.56,
        0.82,
        0.63,
        0.63,
        0.66,
        0.69,
        1.16,
        0.49,
        0.49,
        0.47,
        0.44,
        0.09,
        0.07,
        0.07,
        0.48,
        0.88,
        0.60,
        11.45,
        11.47,
        20.36,
        29.25,
        19.84,
        3.37,
        3.36,
        1.73,
        0.10,
        0.08,
        0.11,
        0.11,
        0.12,
        0.14,
        0.15,
        0.15,
        0.15,
        0.15,
        0.15,
        0.17,
        0.17,
        0.18,
        0.28,
        0.37,
        0.56,
        0.56,
        0.64,
        0.87,
        1.10,
        1.73,
        1.73,
        1.76,
        1.23,
        0.69,
        0.17,
        0.17,
        0.13,
        0.08,
        0.04,
        0.01,
        0.01,
        0.52,
        3.90,
        7.28,
        16.15,
        16.16,
        6.50,
        3.48,
        0.47,
        0.03,
        0.03,
        0.02,
        0.32,
        0.62,
        1.04,
        1.04,
        1.82,
        1.30,
        0.79,
        0.84,
        0.84,
        0.51,
        1.58,
        2.66,
        13.37,
        13.39,
        13.48,
        8.85,
        4.22,
        0.38,
        0.38,
        0.61,
        0.59,
        0.56,
        0.25,
        0.25,
        0.04,
        0.03,
        0.03,
        0.01,
        0.02,
        0.02,
        0.02,
        0.02,
        0.02,
        0.01,
        0.01,
        0.03,
        0.06,
        0.48,
        1.42,
        2.44,
        2.44,
        2.44,
        2.06,
        2.13,
        2.31,
        2.31,
        2.31,
        1.68,
        1.08,
        1.06,
        2.60,
        4.15,
        4.15,
        12.25,
        27.08,
        38.61,
        50.14,
        50.13,
        55.07,
        44.74,
        40.26,
        35.79,
        46.19,
        46.22,
        80.29,
        105.75,
        131.21,
        185.27,
        171.19,
        171.31,
        129.09,
        86.87,
        41.32,
        41.43,
        119.83,
        325.13,
        530.42,
        530.63,
        453.72,
        85.49,
        52.88,
        20.27,
        33.22,
        33.23,
        149.22,
        329.19,
        509.16,
        900.93,
        590.33,
        343.81,
        296.22,
        248.63,
        248.46,
        259.63,
        328.47,
        421.46,
        514.44,
        628.84,
        692.98,
        445.79,
        445.70,
        445.61,
        335.99,
        301.97,
        295.60,
        302.84,
        310.09,
        311.65,
        323.01,
        323.06,
        299.90,
        276.74,
        234.65,
        231.59,
        257.46,
        267.27,
        277.08,
        244.13,
        246.43,
        245.78,
        245.91,
        246.05,
        197.69,
        187.18,
        95.09,
        63.74,
        32.39,
        13.97,
        15.42,
        30.43,
        35.40,
        40.37,
        35.11,
        19.13,
        8.35,
        8.35,
        8.35,
        2.52,
        0.69,
        0.85,
        3.02,
        5.20,
        13.43,
        8.33,
        1.22,
        0.62,
        0.01
    ]    
    
    from classes.om import ObjectManager
    import numpy as np
    
    OM = ObjectManager()
    #
    well = OM.new('well', name='Winland-Lorenz')
    OM.add(well)	
    #
   
    
  
    iset = OM.new('curve_set', name='Run 001')
    OM.add(iset, well.uid)
    #
    
    
    
    
    #"""
    
    index = OM.new('data_index', np.array(depth), name='Depth', dimension=0, datatype='MD', unit='m') 
    OM.add(index, iset.uid)
    
    #      
    log = OM.new('log', np.array(phi)/100, index_uid=index.uid, name='Phi', unit='dec', datatype='NMRperm')
    OM.add(log, iset.uid)  
    #"""
    
    
    
    
    
    
    """
    #
    log = OM.new('log', np.array(k), index_uid=index.uid, name='K', unit='mD', datatype='CorePerm')
    OM.add(log, iset.uid)  
    #
    #
    #
    """
    iset2 = OM.new('curve_set', name='Run 002')
    OM.add(iset2, well.uid)
    #
    
    
    index = OM.new('data_index', np.array(depth), name='Depth', dimension=0, datatype='MD', unit='m') 
    OM.add(index, iset2.uid)
    #      
    log = OM.new('log', np.array(phi)/100, index_uid=index.uid, name='Phi', unit='dec', datatype='NMRperm')
    OM.add(log, iset2.uid)  
    #
    log = OM.new('log', np.array(k), index_uid=index.uid, name='K', unit='mD', datatype='CorePerm')
    OM.add(log, iset2.uid)  
    #
    
    #"""
        
    
    
    
    
#    mwc.model.pos = (-1300,600)

   # mwc.model.maximized = True
    
    
    """  
    from om.manager import ObjectManager
    OM = ObjectManager()
    well = OM.new('well', name='ZZZ')
    OM.add(well)
    """
    
    """
    mwc = get_main_window_controller()
    
    mwc.size = wx.Size(900, 200)
    mwc.size = wx.Size(900, 460)
    
    print (mwc.name)
    print (mwc['name'])
    
    del mwc.name
    
#    del mwc['name']
    
    """
    
    '''
    mwc = get_main_window_controller()
    mwc.model.pos = (-1092, 606)
    mwc.model.size = (900, 600)
    mwc.model.maximized = False
    '''

    '''

    print ('\n\n\n\n\n\n\n\n\n\n')

    from om.manager import ObjectManager
    OM = ObjectManager()
    
    
    OM.print_info()
    
    well = OM.new('well', name='ZZZ')
    OM.add(well)
    
    '''
    
    
    """
    
    OM.print_info()




    OM.remove(well.uid)


    OM.print_info()

    well1 = OM.new('well', name='xxx')
    OM.add(well1)
    
    OM.print_info()
    
    well2 = OM.new('well', name='yyy')
    OM.add(well2)

    OM.print_info()

    OM.remove(well1.uid)
    
    OM.print_info()
    
    OM.remove(well2.uid)

    OM.print_info()

    """

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
    
    
