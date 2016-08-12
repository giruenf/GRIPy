# -*- coding: utf-8 -*-

import wx

import wx.aui as aui

import os.path

import numpy as np
from OM.Manager import ObjectManager

import IO
import DT
import Vis

import HeaderEditor
import ODTEditor
import ImportSelector
import ExportSelector
import CrossPlotSelector
import LogSelectorForPlot
import WellSelector
import OMTree
import PartitionEditor
import logplotformat
import lisloader

from uimanager import UIManagerSingleton as UIManager

import Plugins

from Parms import ParametersManager
from Parms import ParametersManager2

# Uso do Dialog Constructor no _on_plot
from dialog import Dialog

#Menu Arquivo
ID_IMPORTLAS = wx.NewId()
ID_EXPORTLAS = wx.NewId()
ID_IMPORTODT = wx.NewId()
ID_IMPORTLIS = wx.NewId()
#Menu Editar
ID_PARTITIONEDIT = wx.NewId()

#Menu Ferramentas
ID_PLOT = wx.NewId()
ID_CROSSPLOT = wx.NewId()

#Menu Precondicionamento
#ID_DESPIKE = wx.NewId()
#ID_SMOOTH = wx.NewId()
#ID_MERGE = wx.NewId()
#ID_FILL = wx.NewId()
#ID_CALCULATE = wx.NewId()
#ID_CORRECT_INVASION = wx.NewId()

#Menu Inferencia
#ID_FACIES = wx.NewId()
#ID_PDFS = wx.NewId()
#ID_POROSITIES = wx.NewId()
#ID_SATURATION = wx.NewId()
#ID_VSH = wx.NewId()

# Adriano - 23/11/2015 - Id para SashLayoutWindow que receberá o OMTree
ID_WINDOW_LEFT = wx.NewId()
# Adriano - 17/04/2016
ID_WINDOW_MENU_CLOSE = wx.NewId()



class Frame(aui.AuiMDIParentFrame):

    def __init__(self, parent):
        aui.AuiMDIParentFrame.__init__(self, parent,-1,
                                          title="AuiMDIParentFrame",
                                          size=(640,480),
                                          style=wx.DEFAULT_FRAME_STYLE)

        self.dict_menus = {}
        self.create_menu_bar()
        self.status_bar = self.CreateStatusBar()

        #self.PLTs = IO.PLT.getPLTFiles(DEFAULT_PLOT_DIR)

        # Retirando AuiManager pois não funciona com AUIMDIParentFrame (verificar)
        #self._mgr = AuiManager()
        #self._mgr.SetManagedWindow(self)
        
        #self.create_notebook()
        # Para o Notebook (AuiMDIClientWindow) ser 'colocado' ao lado direito
        # do OMTree

                
        
        self.notebook = self.GetClientWindow()
        bkcolour = (126, 200, 252)
        
     #   self.notebook.SetBackgroundColour(bkcolour)
     #   self.notebook.SetForegroundColour(bkcolour)
        self.notebook.SetOwnBackgroundColour(bkcolour)
        
     #   self.SetArtProvider(wx.lib.agw.aui.ChromeTabArt())
     #   self.notebook._mgr.GetArtProvider().SetColour(
     #       wx.lib.agw.aui.AUI_DOCKART_BACKGROUND_COLOUR, bkcolour)
       
        # OMTree passou a ser inserido dentro de um SashLayoutWindow 
        self.create_om_tree()
        
        


        #self._mgr.Update()
        
        #self.Maximize()
        
        # Para posicionar corretamente o Notebook(AuiMDIClientWindow)
        wx.LayoutAlgorithm().LayoutWindow(self, self.notebook)


        self.dir_name = ''
        self.file_name = ''
        self.las_dir_name = ''
        self.odt_dir_name = ''
        
        self._OM = ObjectManager(self)
        
        self.dict_menus['plugins'] = wx.Menu()
        self.menu_bar.Append(self.dict_menus['plugins'],  u"Plugins")
        
        self.PM = Plugins.PluginManager.get()
        self.pluginnamemap = {}
        self.plugincategorymap = {}
        
        self.create_plugin_menu('simpledialog')
        self.create_plugin_menu('autogendata')
        self.create_plugin_menu2('default')
        
        self.defaultplugin_menu = wx.Menu()
        
        # Inserido OnSize para ajustar as janelas do OMTree e do Notebook
        self.Bind(wx.EVT_SIZE, self.OnSize)
        # Para lidar com o arrastar do Sash
        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnSashDrag)
        
        self.Bind(wx.EVT_CLOSE, self.OnDoClose)
        
        self.SetTitle("GRIPy 0.4.0 Dev")
        
       #
       # self.notebook.SetOwnBackgroundColour("light blue")
        
       # bkcolour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_APPWORKSPACE)
       # self.SetOwnBackgroundColour(bkcolour)
       # self._mgr.GetArtProvider().SetColour(AUI_DOCKART_BACKGROUND_COLOUR, bkcolour)
        
        
        
    def OnDoClose(self, evt):
        for m in self.GetChildren():
            if isinstance(m, wx.aui.AuiMDIClientWindow):
                print len(m.GetChildren())
                for k in m.GetChildren():
                    if isinstance(k, wx.aui.AuiMDIChildFrame):
                        k.Close()
                        k.Destroy()
        

        if evt.GetId() == ID_WINDOW_MENU_CLOSE:
            # Closing by menu action
            self.Destroy()
        else:    
            # Closing by window Exit
            evt.Skip()     
        
        
    def OnSize(self, event):
        self.leftWin.SetDefaultSize((self.leftWin.GetSize().GetWidth(),
                                 self.GetClientSize().GetHeight()))      
        wx.LayoutAlgorithm().LayoutWindow(self, self.notebook)        
        
        
    def OnSashDrag(self, event):
        if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
            return
        eobj = event.GetEventObject()
        if eobj is self.leftWin:
            self.leftWin.SetDefaultSize((event.GetDragRect().width, 
                             self.notebook.GetSize().GetHeight()))
        wx.LayoutAlgorithm().LayoutWindow(self, self.notebook)  
        
    def create_toolbar(self):
        self.toolbar = self.CreateToolBar()
        self.las_bar = self.toolbar.AddLabelTool(wx.ID_ANY, u"Importar arquivo LAS", wx.Bitmap('./Icon/document-open.png'), shortHelp='Importar LAS', longHelp='Importar LAS')
        self.save_bar = self.toolbar.AddLabelTool(wx.ID_ANY, u"Salvar projeto", wx.Bitmap('./Icon/document-save-as.png'), shortHelp='Salvar projeto', longHelp='Salvar projeto')
#        self.las_bar2 = self.toolbar.AddLabelTool(wx.ID_ANY, u"Importar arquivo LAS", wx.Bitmap('./Icon/import-las32x32.png'))
        self.plot_bar = self.toolbar.AddLabelTool(wx.ID_ANY, u"Visualizar Plot", wx.Bitmap('./Icon/plot-log.png'), shortHelp='Plot', longHelp='Plot')
        self.crossplot_bar = self.toolbar.AddLabelTool(wx.ID_ANY, u"Visualizar Crossplot", wx.Bitmap('./Icon/crossplot-log.png'), shortHelp='Crossplot', longHelp='Crossplot')
        self.toolbar.Realize()
        self.Bind(wx.EVT_TOOL, self.on_import_las, self.las_bar)
        self.Bind(wx.EVT_TOOL, self.on_save, self.save_bar)
        self.Bind(wx.EVT_TOOL, self.on_plot, self.plot_bar)
        self.Bind(wx.EVT_TOOL, self.on_crossplot, self.crossplot_bar)
        self.SetTitle('Simple toolbar')
        self.Centre()
        self.Show(True)
        
    def create_menu_bar(self):
        self.menu_bar = wx.MenuBar()
        self.create_file_menu()
        self.create_edit_menu()
#        self.create_visualization_menu()
        self.create_preconditioning_menu()
        self.create_interpretation_menu()
        self.create_inference_menu()
        self.create_tools_menu()
        self.create_toolbar()
        self.SetMenuBar(self.menu_bar)

    def create_file_menu(self):
        self.dict_menus['file'] = wx.Menu()
        self.dict_menus['file'].Append(wx.ID_OPEN, u"&Abrir", u"Abrir arquivo")
        self.dict_menus['file'].Append(wx.ID_SAVE, u"&Salvar", u"Salvar arquivo")
        self.dict_menus['file'].Append(wx.ID_SAVEAS, u"Salvar &Como",
                              u"Salvar arquivo com nome diferente")
        self.dict_menus['file'].AppendSeparator()
        
        self.import_menu = wx.Menu()        
#        self.import_menu.Append(ID_IMPORTTAB, u"&TAB", u"Importar arquivo TAB")
        self.export_menu = wx.Menu()
        self.export_menu.Append(ID_EXPORTLAS, u"&LAS", u"Exportar arquivo LAS")
        self.dict_menus['file'].AppendMenu(wx.ID_ANY, u"&Importar", self.import_menu, u"Importar arquivo")
        self.dict_menus['file'].AppendMenu(wx.ID_ANY, u"&Exportar", self.export_menu, u"Exportar arquivo")
        self.dict_menus['file'].AppendSeparator()
        
        self.dict_menus['file'].Append(wx.ID_CLOSE, u"&Fechar", u"Fechar o programa")

        self.Bind(wx.EVT_MENU, self.on_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_save, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.on_save_as, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.on_import_las, id=ID_IMPORTLAS)
        self.Bind(wx.EVT_MENU, self.on_import_odt, id=ID_IMPORTODT)  
        self.Bind(wx.EVT_MENU, self.on_import_lis, id=ID_IMPORTLIS)
        self.Bind(wx.EVT_MENU, self.on_export_las, id=ID_EXPORTLAS)
        #self.Bind(wx.EVT_MENU, self.on_close, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnDoClose, id=wx.ID_CLOSE)
        
#        item = wx.MenuItem(self.import_menu, -1, u"&LAS", "Importar arquivo LAS") # exemplo de criacao de item com bmp
#        item.SetBitmap(wx.Bitmap('./Icon/import-las16x16.png'))
#        self.Bind(wx.EVT_MENU, self.on_import_las, item)
#        self.import_menu.AppendItem(item)
        self.import_menu.Append(ID_IMPORTLAS, u"&LAS", u"Importar arquivo LAS")        
        self.import_menu.Append(ID_IMPORTODT, u"&ODT", u"Importar arquivo ODT")
        self.import_menu.Append(ID_IMPORTLIS, u"&LIS", u"Importar arquivo LIS")
        self.menu_bar.Append(self.dict_menus['file'], u"&Arquivo")
    
    def create_edit_menu(self):
        self.dict_menus['edit'] = wx.Menu()
        
        self.dict_menus['edit'].Append(ID_PARTITIONEDIT, u"&Partições", u"Editar partições")
        
        self.Bind(wx.EVT_MENU, self.on_partitionedit, id=ID_PARTITIONEDIT)
        
        self.menu_bar.Append(self.dict_menus['edit'], u"&Editar")

#    def create_visualization_menu(self):
#        self.visualization_menu = wx.Menu()
#
#        self.visualization_menu.Append(ID_PLOT, u"&Plot", u"Plot de perfis")
#        self.visualization_menu.Append(ID_CROSSPLOT, u"&Crossplot", u"Crossplot de perfis")
#
#        self.Bind(wx.EVT_MENU, self.on_plot, id=ID_PLOT)
#        self.Bind(wx.EVT_MENU, self.on_crossplot, id=ID_CROSSPLOT)
#
#        self.menu_bar.Append(self.visualization_menu, u"&Visualizar")

    def create_preconditioning_menu(self):
        self.dict_menus['precond'] = wx.Menu()

#        log_edit_menu = wx.Menu()
#        log_edit_menu.Append(ID_DESPIKE, u"&Remover spikes", u"???")
#        log_edit_menu.Append(ID_SMOOTH, u"&Suavizar", u"???")
#        log_edit_menu.Append(ID_MERGE, u"&Fundir", u"???")
#        log_edit_menu.Append(ID_FILL, u"&Preencher", u"???")

        self.dict_menus['precond'].Append(-1, u"Vazio", u"Faz nada!")
#        self.dict_menus['precond'].AppendMenu(wx.ID_ANY, u"&Edição de perfis",
#                                             log_edit_menu, u"???")
#        self.dict_menus['precond'].Append(ID_CALCULATE, u"&Calcular perfis",
#                                         u"???")
#        self.dict_menus['precond'].Append(ID_CORRECT_INVASION,
#                                         u"Correção de &invasão", u"???")

#        self.Bind(wx.EVT_MENU, self.on_despike, id=ID_DESPIKE)
#        self.Bind(wx.EVT_MENU, self.on_smooth, id=ID_SMOOTH)
#        self.Bind(wx.EVT_MENU, self.on_merge, id=ID_MERGE)
#        self.Bind(wx.EVT_MENU, self.on_fill, id=ID_FILL)
#        self.Bind(wx.EVT_MENU, self.on_calculate, id=ID_CALCULATE)
#        self.Bind(wx.EVT_MENU, self.on_correct_invasion,
#                  id=ID_CORRECT_INVASION)

        self.menu_bar.Append(self.dict_menus['precond'], u"&Precondicionamento")

    def create_interpretation_menu(self):
        self.dict_menus['interp'] = wx.Menu()

#        self.dict_menus['interp'].Append(-1, u"Vazio", u"Faz nada!")
#        self.dict_menus['interp'].Append(ID_PDFS, u"F&DPS", u"???")
#        self.dict_menus['interp'].Append(ID_POROSITIES, u"&Porosidades", u"???")
#        self.dict_menus['interp'].Append(ID_SATURATION, u"&Saturação", u"???")
#        self.dict_menus['interp'].Append(ID_VSH, u"&Volume de Argila", u"???")
#
#        self.Bind(wx.EVT_MENU, self.on_pdfs, id=ID_PDFS)
#        self.Bind(wx.EVT_MENU, self.on_porosities, id=ID_POROSITIES)
#        self.Bind(wx.EVT_MENU, self.on_saturation, id=ID_SATURATION)
#        self.Bind(wx.EVT_MENU, self.on_vsh, id=ID_VSH)

        self.menu_bar.Append(self.dict_menus['interp'], u"&Interpretação")
    
    def create_inference_menu(self):
        self.dict_menus['infer'] = wx.Menu()
        
        self.dict_menus['infer'].Append(-1, u"Vazio", u"Faz nada!")
#        self.dict_menus['infer'].Append(ID_FACIES, u"&Fácies", u"???")
#        
#        self.Bind(wx.EVT_MENU, self.on_facies, id=ID_FACIES)
        
        self.menu_bar.Append(self.dict_menus['infer'], u"&Inferência")
    
    def create_plugin_menu2(self, category):
        for info in sorted(self.PM.getPluginsOfCategory(category), key=lambda x: x.name.lower()):
            menukey = getattr(info.plugin_object, 'menukey', 'plugins')
            menu = self.dict_menus[menukey]
            
            pluginname = info.name
            plugindescription = info.description
            
            plugininputid = wx.NewId()
            pluginrunid = wx.NewId()
            pluginoutputid = wx.NewId()
            pluginreloadid = wx.NewId()

            plugin_menu = wx.Menu()
            plugin_menu.Append(plugininputid, u"Fazer &Entrada", u"???")
            plugin_menu.Append(pluginrunid, u"&Rodar", u"???")
            plugin_menu.Append(pluginoutputid, u"Fazer &Saída", u"???")
            plugin_menu.AppendSeparator()
            plugin_menu.Append(pluginreloadid, u"Re&carregar", u"???")

            menu.AppendMenu(wx.ID_ANY, unicode(pluginname, 'utf8'), plugin_menu, unicode(plugindescription, 'utf8'))

            self.Bind(wx.EVT_MENU, self.on_pluginsinput, id=plugininputid)
            self.Bind(wx.EVT_MENU, self.on_pluginsrun, id=pluginrunid)
            self.Bind(wx.EVT_MENU, self.on_pluginsoutput, id=pluginoutputid)
            self.Bind(wx.EVT_MENU, self.on_pluginsreload, id=pluginreloadid)

            self.pluginnamemap[plugininputid] = pluginname
            self.pluginnamemap[pluginrunid] = pluginname
            self.pluginnamemap[pluginoutputid] = pluginname
            self.pluginnamemap[pluginreloadid] = pluginname
            
            self.plugincategorymap[plugininputid] = category
            self.plugincategorymap[pluginrunid] = category
            self.plugincategorymap[pluginoutputid] = category
            self.plugincategorymap[pluginreloadid] = category
            
    def create_plugin_menu(self, category):
        
        for info in sorted(self.PM.getPluginsOfCategory(category), key=lambda x: x.name.lower()):
            menukey = getattr(info.plugin_object, 'menukey', 'plugins')
            menu = self.dict_menus[menukey]
            
            pluginname = info.name
            plugindescription = info.description
            pluginid = wx.NewId()

            menu.Append(pluginid, unicode(pluginname, 'utf8'), unicode(plugindescription, 'utf8'))
            self.Bind(wx.EVT_MENU, self.on_pluginui, id=pluginid)

            self.pluginnamemap[pluginid] = pluginname
            self.plugincategorymap[pluginid] = category
    
    '''
    AuiMDIClientWindow atuará como Notebook        
    def create_notebook(self):
        _style = aui.AUI_NB_TOP | aui.AUI_NB_TAB_MOVE | \
            aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_CLOSE_ON_ALL_TABS | \
             aui.AUI_NB_TAB_SPLIT
       # _style = _style | aui.AUI_NB_TAB_SPLIT #| aui.AUI_NB_TAB_FLOAT

        self.notebook = aui.AuiNotebook(self, style= _style)#agwStyle=style)
        self._mgr.AddPane(self.notebook, aui.AuiPaneInfo().
                          Name("notebook_content").CenterPane())
    '''

    def create_tools_menu(self):
        self.ID_CHECKTAB = wx.NewId()
        self.tool_menu = wx.Menu()
        self.tool_menu.Append(self.ID_CHECKTAB, u"Abrir ViTables ...", u"Importar arquivo TAB")
        self.Bind(wx.EVT_MENU, self.check_tab, id=self.ID_CHECKTAB)          
        
        
        self.tool_menu.Append(ID_PLOT, u"&Plot", u"Plot de perfis")
        self.tool_menu.Append(ID_CROSSPLOT, u"&Crossplot", u"Crossplot de perfis")
        
#        cross = wx.MenuItem(self.tool_menu, -1, u"&Crossplot", "Crossplot de perfis") # exemplo de criacao de item com bmp
#        cross.SetBitmap(wx.Bitmap('./Icon/crossplot-log16x16.png'))
#        self.Bind(wx.EVT_MENU, self.on_crossplot, cross)
#        self.tool_menu.AppendItem(cross)

        self.Bind(wx.EVT_MENU, self.on_plot, id=ID_PLOT)
        self.Bind(wx.EVT_MENU, self.on_crossplot, id=ID_CROSSPLOT)
        self.menu_bar.Append(self.tool_menu,  u"Ferramentas")
#        self.menu_bar.Append(self.tool_menu, u"&Visualizar")
    def create_om_tree(self):
        #self.om_tree = OMTree.Tree(self, size=wx.Size(140, -1))
        self.leftWin = wx.SashLayoutWindow(self, ID_WINDOW_LEFT, style=wx.NO_BORDER|wx.SW_3D)
        self.om_tree = OMTree.Tree(self.leftWin, size=wx.Size(140, -1))      
        
        
        # TODO: A linha abaixo faz parte do armengue do OMTree
        #       Retirar esta bagaça o quanto antes
        self.om_tree.set_main_window(self)
        
        
        self.leftWin.SetDefaultSize((180, self.notebook.GetSize().GetHeight()))
        self.leftWin.SetOrientation(wx.LAYOUT_VERTICAL)
        self.leftWin.SetAlignment(wx.LAYOUT_LEFT)
        self.leftWin.SetSashVisible(wx.SASH_RIGHT, True)

        #self._mgr.AddPane(self.om_tree, pinfo)#, aui.AuiPaneInfo().Name("tree_content").
                          #Left().CloseButton(False).Floatable(False)
                          #.CaptionVisible(False))

    def on_open(self, event):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        wildcard = "Arquivo de projeto do GRIPy (*.pgg)|*.pgg"
        fdlg = wx.FileDialog(self, 'Escolha o arquivo PGG', self.dir_name, wildcard=wildcard, style=style)
        if fdlg.ShowModal() == wx.ID_OK:
            self.file_name = fdlg.GetFilename()
            self.dir_name = fdlg.GetDirectory()
            fdlg.Destroy()
        else:
            fdlg.Destroy()
            return

        self._OM.load(os.path.join(self.dir_name, self.file_name))
    
    def on_save(self, event):
        if self.file_name and self.dir_name:
            self._OM.save(os.path.join(self.dir_name, self.file_name))
        else:
            self.on_save_as(event)
    
    def on_save_as(self, event):
        style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        wildcard = "Arquivo de projeto do GRIPy (*.pgg)|*.pgg"
        fdlg = wx.FileDialog(self, 'Escolha o arquivo PGG', self.dir_name, wildcard=wildcard, style=style)
        if fdlg.ShowModal() == wx.ID_OK:
            self.file_name = fdlg.GetFilename()
            self.dir_name = fdlg.GetDirectory()
            self._OM.save(os.path.join(self.dir_name, self.file_name))
        fdlg.Destroy()
        
    def check_tab(self, event):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        wildcard="Arquivos hdf5 (*.h5)|*.h5"
        fdlg = wx.FileDialog(self, 'Escolha o projeto a carregar', self.odt_dir_name, wildcard=wildcard, style=style)
        if fdlg.ShowModal() == wx.ID_OK:
            file_proj = fdlg.GetFilename()
            self.odt_dir_name = fdlg.GetDirectory()
            fdlg.Destroy()
        else:
            fdlg.Destroy()
            return
        dfile = os.path.join(self.odt_dir_name, file_proj)
        os.system("vitables %s" %dfile)
            
    def on_import_lis(self, event):
        lis_import_frame = lisloader.LISImportFrame(self)
        lis_import_frame.Show()
 
           
            
    def on_import_odt(self, event):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        wildcard="Arquivos ODT (*.wlm)|*.wlm"
#        self.odt_dir_name = ''
        fdlg = wx.FileDialog(self, 'Escolha o projeto a carregar', self.odt_dir_name, wildcard=wildcard, style=style)
        if fdlg.ShowModal() == wx.ID_OK:
            file_proj = fdlg.GetFilename()
            self.odt_dir_name = fdlg.GetDirectory()
            fdlg.Destroy()
        else:
            fdlg.Destroy()
            return
        odt_file = IO.ODT.open(self.odt_dir_name, file_proj, 'r')
        hedlg = ODTEditor.Dialog(self)
        print odt_file.ndepth
        hedlg.set_header(odt_file.fileheader, odt_file.logheader, odt_file.ndepth)

        if hedlg.ShowModal() == wx.ID_OK:
            odt_file.header = hedlg.get_header()
            print 'header 2\n', odt_file.header

            names = [line['MNEM'] for line in odt_file.header["C"].itervalues()]
            units = [line['UNIT'] for line in odt_file.header["C"].itervalues()]
            ncurves = len(names)
            
            """
            # TODO: acabar com essa verdadeira gambiarra e colocar em um arquivo json, além de implementar uma persistência
            
            curvetypes = ['Azimuth', 'BVW', 'BitSize', 'CBHP', 'CDP',
                          'Caliper', 'Coord.', 'CoreGD', 'CorePerm', 'CorePhi',
                          'DVcl', 'DeepRes', 'Density', 'Depth', 'Deviation',
                          'Drho', 'ECD', 'EPT', 'FlowRate', 'GAS', 'GammaRay',
                          'Hookload', 'LoadFactor', 'Matrix', 'MaxHorzStress',
                          'MedRes', 'MicroRes', 'MinHorzStress', 'Mineral',
                          'NMRbfi', 'NMRcbfi', 'NMRffi', 'NMRperm', 'NMRphi',
                          'NMRphiT', 'NMRswi', 'Neutron', 'OnBottom',
                          'OrigResPress', 'PEF', 'Perforations', 'Phi', 'PhiT',
                          'Pump', 'RB_Offset', 'ROP', 'RotarySpeed', 'SP',
                          'ShalRes', 'ShearSonic', 'ShearVel', 'Sigma',
                          'Sonic', 'Spectral', 'StickSlip', 'StressAzimuth',
                          'Sw', 'Temp', 'Tension', 'Tool_Azimuth',
                          'Tool_RelBearng', 'Torque', 'TwcPredicted', 'Vcl',
                          'Vcoal', 'Velocity', 'VertStress', 'Vibration',
                          'Vsalt', 'Vsilt', 'WeightonBit', 'Xaccelerometer',
                          'Xmagnetometer', 'Yaccelerometer', 'Ymagnetometer',
                          'Zaccelerometer', 'Zmagnetometer']
            
            datatypes = ['Depth', 'Log', 'Partition']
            
            sel_curvetypes = ['']*ncurves
            sel_datatypes = ['Depth'] + ['Log']*(ncurves - 1)
            
            """ 
            # Tentativa de solução não lusitana
            
            ParametersManager2.load()
            
            curvetypes = ParametersManager2.getcurvetypes()
            datatypes = ParametersManager2.getdatatypes()
            
            sel_curvetypes = [ParametersManager2.getcurvetypefrommnem(name) for name in names]
            
            sel_datatypes = []
            for name in names:
                datatype = ParametersManager2.getdatatypefrommnem(name)
                if not datatype:
                    sel_datatypes.append('Log')
                else:
                    sel_datatypes.append(datatype)
            
            # """

            isdlg = ImportSelector.Dialog(self, names, units, curvetypes, datatypes)
            
            isdlg.set_curvetypes(sel_curvetypes)
            isdlg.set_datatypes(sel_datatypes)
            
            if isdlg.ShowModal() == wx.ID_OK:
                
                sel_curvetypes = isdlg.get_curvetypes()
                sel_datatypes = isdlg.get_datatypes()
                
                data = odt_file.data
                well = self._OM.new('well', name=odt_file.filename, LASheader=odt_file.header)
               
                self._OM.add(well)
                for i in range(ncurves):
                    if sel_curvetypes[i]:
                        ParametersManager2.voteforcurvetype(names[i], sel_curvetypes[i])
                
                    if sel_datatypes[i]:
                        ParametersManager2.votefordatatype(names[i], sel_datatypes[i])
                
                    if sel_datatypes[i] == 'Depth':
                        # print "Importing {} as '{}' with curvetype '{}'".format(names[i], sel_datatypes[i], sel_curvetypes[i])
                        depth = self._OM.new('depth', data[i], name=names[i], unit=units[i], curvetype=sel_curvetypes[i])
                        self._OM.add(depth, well.uid)
                    
                    elif sel_datatypes[i] == 'Log':
                        # print "Importing {} as '{}' with curvetype '{}'".format(names[i], sel_datatypes[i], sel_curvetypes[i])
                        log = self._OM.new('log', data[i], name=names[i], unit=units[i], curvetype=sel_curvetypes[i])
                        self._OM.add(log, well.uid)

                    elif sel_datatypes[i] == 'Partition':
                        # print "Importing {} as '{}' with curvetype '{}'".format(names[i], sel_datatypes[i], sel_curvetypes[i])
                        booldata, codes = DT.DataTypes.Partition.getfromlog(data[i])
                        
                        partition = self._OM.new('partition', name=names[i], curvetype=sel_curvetypes[i])
                        self._OM.add(partition, well.uid)
                        
                
                        for j in range(len(codes)):
                            part = self._OM.new('part', booldata[j], code=int(codes[j]), curvetype=sel_curvetypes[i])
                            self._OM.add(part, partition.uid)
                    
                    else:
                        print "Not importing {} as no datatype matches '{}'".format(names[i], sel_datatypes[i])
                    
            
            ParametersManager2.dump()
                    
            isdlg.Destroy()

        hedlg.Destroy()


    def on_import_las(self, event):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        wildcard="Arquivos LAS (*.las)|*.las"
        print self.las_dir_name
        fdlg = wx.FileDialog(self, 'Escolha o arquivo LAS', self.las_dir_name, wildcard=wildcard, style=style)
        if fdlg.ShowModal() == wx.ID_OK:
            file_name = fdlg.GetFilename()
            self.las_dir_name = fdlg.GetDirectory()
            fdlg.Destroy()
        else:
            fdlg.Destroy()
            return
        las_file = IO.LAS.open(os.path.join(self.las_dir_name, file_name), 'r')
        las_file.read()
        hedlg = HeaderEditor.Dialog(self)
        hedlg.set_header(las_file.header)

        if hedlg.ShowModal() == wx.ID_OK:
            las_file.header = hedlg.get_header()
#            print 'header\n', las_file.header
            names = las_file.curvesnames
            units = las_file.curvesunits
            
            ncurves = len(names)
            
            """
            # TODO: acabar com essa verdadeira gambiarra e colocar em um arquivo json, além de implementar uma persistência
            
            curvetypes = ['Azimuth', 'BVW', 'BitSize', 'CBHP', 'CDP',
                          'Caliper', 'Coord.', 'CoreGD', 'CorePerm', 'CorePhi',
                          'DVcl', 'DeepRes', 'Density', 'Depth', 'Deviation',
                          'Drho', 'ECD', 'EPT', 'FlowRate', 'GAS', 'GammaRay',
                          'Hookload', 'LoadFactor', 'Matrix', 'MaxHorzStress',
                          'MedRes', 'MicroRes', 'MinHorzStress', 'Mineral',
                          'NMRbfi', 'NMRcbfi', 'NMRffi', 'NMRperm', 'NMRphi',
                          'NMRphiT', 'NMRswi', 'Neutron', 'OnBottom',
                          'OrigResPress', 'PEF', 'Perforations', 'Phi', 'PhiT',
                          'Pump', 'RB_Offset', 'ROP', 'RotarySpeed', 'SP',
                          'ShalRes', 'ShearSonic', 'ShearVel', 'Sigma',
                          'Sonic', 'Spectral', 'StickSlip', 'StressAzimuth',
                          'Sw', 'Temp', 'Tension', 'Tool_Azimuth',
                          'Tool_RelBearng', 'Torque', 'TwcPredicted', 'Vcl',
                          'Vcoal', 'Velocity', 'VertStress', 'Vibration',
                          'Vsalt', 'Vsilt', 'WeightonBit', 'Xaccelerometer',
                          'Xmagnetometer', 'Yaccelerometer', 'Ymagnetometer',
                          'Zaccelerometer', 'Zmagnetometer']
            
            datatypes = ['Depth', 'Log', 'Partition']
            
            sel_curvetypes = ['']*ncurves
            sel_datatypes = ['Depth'] + ['Log']*(ncurves - 1)
            
            """ 
            # Tentativa de solução não lusitana
            
            ParametersManager2.load()
            
            curvetypes = ParametersManager2.getcurvetypes()
            datatypes = ParametersManager2.getdatatypes()
            
            sel_curvetypes = [ParametersManager2.getcurvetypefrommnem(name) for name in names]
            
            sel_datatypes = []
            for name in names:
                datatype = ParametersManager2.getdatatypefrommnem(name)
                if not datatype:
                    sel_datatypes.append('Log')
                else:
                    sel_datatypes.append(datatype)
            
            # """

            isdlg = ImportSelector.Dialog(self, names, units, curvetypes, datatypes)
            
            isdlg.set_curvetypes(sel_curvetypes)
            isdlg.set_datatypes(sel_datatypes)
            
            if isdlg.ShowModal() == wx.ID_OK:
                
                sel_curvetypes = isdlg.get_curvetypes()
                sel_datatypes = isdlg.get_datatypes()
                
                data = las_file.data
                print '\n\ndata:\n',data

                well = self._OM.new('well', name=las_file.wellname, LASheader=las_file.header)
                print 'well\n', well, '\n\n',las_file.header
                self._OM.add(well)
                #_, well_oid = well.uid
                #PlotController.get().register_well(well_oid)
                for i in range(ncurves):
                    if sel_curvetypes[i]:
                        ParametersManager2.voteforcurvetype(names[i], sel_curvetypes[i])
                
                    if sel_datatypes[i]:
                        ParametersManager2.votefordatatype(names[i], sel_datatypes[i])
                
                    if sel_datatypes[i] == 'Depth':
                        # print "Importing {} as '{}' with curvetype '{}'".format(names[i], sel_datatypes[i], sel_curvetypes[i])
                        depth = self._OM.new('depth', data[i], name=names[i], unit=units[i], curvetype=sel_curvetypes[i])
                        self._OM.add(depth, well.uid)
                    
                    elif sel_datatypes[i] == 'Log':
                        # print "Importing {} as '{}' with curvetype '{}'".format(names[i], sel_datatypes[i], sel_curvetypes[i])
                        log = self._OM.new('log', data[i], name=names[i], unit=units[i], curvetype=sel_curvetypes[i])
                        self._OM.add(log, well.uid)

                    elif sel_datatypes[i] == 'Partition':
                        # print "Importing {} as '{}' with curvetype '{}'".format(names[i], sel_datatypes[i], sel_curvetypes[i])
                        booldata, codes = DT.DataTypes.Partition.getfromlog(data[i])
                        
                        partition = self._OM.new('partition', name=names[i], curvetype=sel_curvetypes[i])
                        self._OM.add(partition, well.uid)
                        
                
                        for j in range(len(codes)):
                            part = self._OM.new('part', booldata[j], code=int(codes[j]), curvetype=sel_curvetypes[i])
                            self._OM.add(part, partition.uid)
                    
                    else:
                        print "Not importing {} as no datatype matches '{}'".format(names[i], sel_datatypes[i])
                    
            
            ParametersManager2.dump()
                    
            isdlg.Destroy()

        hedlg.Destroy()
        

    def on_export_las(self, event):

        esdlg = ExportSelector.Dialog(self)
        if esdlg.ShowModal() == wx.ID_OK:
            ###
            # TODO: Colocar isso em outro lugar
            names = []
            units = []
            data = []
            for depthuid in esdlg.get_depth_selection():
                depth = self._OM.get(depthuid)
                names.append(depth.name)
                units.append(depth.unit)
                data.append(depth.data)
            for loguid in esdlg.get_log_selection():
                log = self._OM.get(loguid)
                names.append(log.name)
                units.append(log.unit)
                data.append(log.data)
            for partitionuid in esdlg.get_partition_selection():
                partition = self._OM.get(partitionuid)
                names.append(partition.name)
                units.append('')
                data.append(partition.getaslog())
            for partitionuid, propselection in esdlg.get_property_selection().iteritems():
                partition = self._OM.get(partitionuid)
                for propertyuid in propselection:
                    prop = self._OM.get(propertyuid)
                    names.append(prop.name)
                    units.append(prop.unit)
                    data.append(partition.getaslog(propertyuid))
            data = np.asanyarray(data)
            ###
            
            welluid = esdlg.get_welluid()
            well = self._OM.get(welluid)
            header = well.attributes.get("LASheader", None)
            if header is None:
                header = IO.LAS.LASWriter.getdefaultheader()
            
            header = IO.LAS.LASWriter.rebuildwellsection(header, data[0], units[0])
            header = IO.LAS.LASWriter.rebuildcurvesection(header, names, units)
            
            hedlg = HeaderEditor.Dialog(self)
            hedlg.set_header(header)
            
            if hedlg.ShowModal() == wx.ID_OK:
                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
                wildcard="Arquivos LAS (*.las)|*.las"
                fdlg = wx.FileDialog(self, 'Escolha o arquivo LAS', self.las_dir_name, wildcard=wildcard, style=style)
                
                if fdlg.ShowModal() == wx.ID_OK:
                    file_name = fdlg.GetFilename()
                    self.las_dir_name = fdlg.GetDirectory()
                    header = hedlg.get_header()
                    las_file = IO.LAS.open(os.path.join(self.las_dir_name, file_name), 'w')
                    las_file.header = header
                    las_file.data = data
                    las_file.headerlayout = IO.LAS.LASWriter.getprettyheaderlayout(header)
                    las_file.write()
                fdlg.Destroy()
            hedlg.Destroy()
        esdlg.Destroy()
        
    '''    
    def on_close(self, event):
        self.Close()
    '''
    
    def on_partitionedit(self, event):
        if not self._OM.list('partition'):
            return
        dlg = PartitionEditor.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.om_tree.refresh()
        
    def load_core (self, event):
#        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
#        wildcard="Arquivos hdf5 (*.h5)|*.h5"
#        fdlg = wx.FileDialog(self, 'Escolha o projeto a carregar', self.odt_dir_name, wildcard=wildcard, style=style)
#        if fdlg.ShowModal() == wx.ID_OK:
#            core = fdlg.GetFilename()
##            core_dir_name = fdlg.GetDirectory()
#            fdlg.Destroy()
#        else:
#            fdlg.Destroy()
#            return
#        print (core[:-2])
#        core = self._OM.new('core', name=(core[:-3]))
#        self._OM.add(core)
#        return True
        coredlg = DatabaseSelector.Dialog(self)
        dlg = Dialog(self, 
            [
                (Dialog.Database_selector, 'Well:', 'well_uid'),
#                (Dialog.logplotformat_selector, 'Format: ', 'plt_file_name')
            ], 
            'DB Selector'
        )
        if dlg.ShowModal() == wx.ID_OK:
            map_ = dlg.get_results()
            print 'map\n\n', map_
            plt = ParametersManager.get().getPLT(map_['plt_file_name'])
            if plt is None:
                lpf = None
            else:    
                lpf = logplotformat.LogPlotFormat.create_from_PLTFile(plt)
            _, well_oid = map_['well_uid']
            UIManager.get().create_log_plot(well_oid, lpf)


    def on_plot(self, event):
        dlg = Dialog(self, 
            [
                (Dialog.well_selector, 'Well:', 'well_uid'),
                (Dialog.logplotformat_selector, 'Format: ', 'plt_file_name')
            ], 
            'Plot Selector'
        )
        if dlg.ShowModal() == wx.ID_OK:
            results = dlg.get_results()
            plt = ParametersManager.get().getPLT(results['plt_file_name'])
            if plt is None:
                lpf = None
            else:    
                lpf = logplotformat.LogPlotFormat.create_from_PLTFile(plt)
            _, well_oid = results['well_uid']
            UIManager.get().create_log_plot(well_oid, lpf)
                

        

    def on_crossplot(self, event):
        csdlg = CrossPlotSelector.Dialog(self)
        if csdlg.ShowModal() == wx.ID_OK:
            welluid = csdlg.get_welluid()
            xuid = csdlg.get_xuid()
            yuid = csdlg.get_yuid()
            zuid = csdlg.get_zuid()
            wuid = csdlg.get_wuid()
            
            # print('\n\n')
            # print(welluid)
            # tid, oid = welluid
            # well = self._OM.list('well')[oid]
            # print(self)
            
            # cpp = Vis.CrossPlot.CrossPlotPanel(self, well.name)
            
            mdichildframe = aui.AuiMDIChildFrame(self, -1, title=self._OM.get(welluid).name)
            cpp = Vis.CrossPlot.CrossPlotPanel(mdichildframe)
            
            cpp.set_xdata(self._OM.get(xuid).data)
            cpp.set_xlabel(self._OM.get(xuid).name)
            cpp.set_ydata(self._OM.get(yuid).data)
            cpp.set_ylabel(self._OM.get(yuid).name)
            
            if zuid is not None:
                if zuid[0] == 'partition':
                    cpp.set_zdata(self._OM.get(zuid).getaslog())
                    cpp.set_zlabel(self._OM.get(zuid).name)
                    classcolors = {}
                    classnames = {}
                    for part in self._OM.list('part', zuid):
                        classcolors[part.code] = tuple(c/255.0 for c in part.color)
                        classnames[part.code] = part.name
                    cpp.set_classcolors(classcolors)
                    cpp.set_classnames(classnames)
                    cpp.set_nullclass(-1)
                    cpp.set_nullcolor((0.0, 0.0, 0.0))
                    cpp.set_zmode('classes')
                else:
                    cpp.set_zdata(self._OM.get(zuid).data)
                    cpp.set_zlabel(self._OM.get(zuid).name)
                    cpp.set_zmode('continuous')
            else:
                print "Not Implemented yet!"  # TODO: fazer alguma coisa quando não escolhe z (cor sólida)
            
            if wuid is not None:
                cpp.set_parts(self._OM.get(wuid).getdata())  # TODO: ver o que é necessário fazer quando não se escolhe w
            
            cpp.plot()
          #  self.notebook.AddPage(cpp, "Crossplot - {}".format(self._OM.get(welluid).name), True)
            cpp.draw()
            
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            hbox.Add(cpp, 1, flag=wx.EXPAND)
            mdichildframe.SetSizerAndFit(hbox)
            
        csdlg.Destroy()

#    def on_despike(self, event):
#        pass
#
#    def on_smooth(self, event):
#        pass
#
#    def on_merge(self, event):
#        pass
#
#    def on_fill(self, event):
#        pass
#
#    def on_calculate(self, event):
#        pass
#
#    def on_correct_invasion(self, event):
#        pass
#
#    def on_facies(self, event):
#        pass
#
#    def on_pdfs(self, event):
#        pass
#
#    def on_porosities(self, event):
#        pass
#
#    def on_saturation(self, event):
#        pass
#
#    def on_vsh(self, event):
#        pass
        
    def on_pluginui(self, event):
        name = self.pluginnamemap[event.GetId()]
        category = self.plugincategorymap[event.GetId()]
        pinfo = self.PM.getPluginByName(name, category)
        print '\n on pluginui', name, category, pinfo
        pinfo.plugin_object.run(self)

    def on_pluginsinput(self, event):
        name = self.pluginnamemap[event.GetId()]
        category = self.plugincategorymap[event.GetId()]
        pinfo = self.PM.getPluginByName(name, category)
        pinfo.plugin_object.doinput()
    
    def on_pluginsrun(self, event):
        name = self.pluginnamemap[event.GetId()]
        category = self.plugincategorymap[event.GetId()]
        pinfo = self.PM.getPluginByName(name, category)
        pinfo.plugin_object.run()
    
    def on_pluginsoutput(self, event):
        name = self.pluginnamemap[event.GetId()]
        category = self.plugincategorymap[event.GetId()]
        pinfo = self.PM.getPluginByName(name, category)
        pinfo.plugin_object.dooutput()

    def on_pluginsreload(self, event):
        name = self.pluginnamemap[event.GetId()]
        category = self.plugincategorymap[event.GetId()]
        pinfo = self.PM.getPluginByName(name, category)
        pinfo.plugin_object.reloadcore()

    def default_file_dialog_options(self):
        return {'message': 'Choose a file', 'defaultDir': self.dir_name,
                'wildcard': '*.*'}

    def ask_user_for_filename(self, **dialogOptions):
        dialog = wx.FileDialog(self, **dialogOptions)
        if dialog.ShowModal() == wx.ID_OK:
            userProvidedFilename = True
            self.file_name = dialog.GetFilename()
            self.dir_name = dialog.GetDirectory()
        else:
            userProvidedFilename = False
        dialog.Destroy()
        return userProvidedFilename
