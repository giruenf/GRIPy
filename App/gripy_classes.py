# -*- coding: utf-8 -*-

from OM.Manager import ObjectManager
from DT.DataTypes import Well
from DT.DataTypes import Core
from DT.DataTypes import Log
from DT.DataTypes import Partition
from DT.DataTypes import Part
from DT.DataTypes import Property
from DT.DataTypes import IndexCurve
from DT.DataTypes import Seismic
from DT.DataTypes import Velocity
from DT.DataTypes import Scalogram


from UI.uimanager import UIManager
from UI.mvc_classes.main_window import MainWindowController, MainWindowModel, MainWindow
from UI.mvc_classes.menu_bar import MenuBarController, MenuBarModel, MenuBarView
from UI.mvc_classes.menu import MenuController, MenuModel, MenuView
from UI.mvc_classes.menu_item import MenuItemController, MenuItemModel, MenuItemView
from UI.mvc_classes.tree import TreeController, TreeView
from UI.mvc_classes.tool_bar import ToolBarController, ToolBarModel, ToolBarView
from UI.mvc_classes.tool_bar_tool import ToolBarToolController, ToolBarToolModel
from UI.mvc_classes.status_bar import StatusBarController, StatusBarModel, StatusBar
from UI.mvc_classes.plotter_log import LogPlotController, LogPlotModel, LogPlot
from UI.mvc_classes.plotter_track import TrackController, TrackModel, TrackView
from UI.mvc_classes.plotter_object import TrackObjectController, \
    TrackObjectModel, TrackObjectView
from UI.mvc_classes.lpf import LogPlotEditorController, LogPlotEditor        



def register_app_classes():
    register_OM_classes()
    register_UIManager_classes()   
    
    
  
def register_OM_classes():
    ObjectManager.registertype(Core, Well)
    ObjectManager.registertype(Well)
    ObjectManager.registertype(Log, Well)
    ObjectManager.registertype(Partition, Well)
    ObjectManager.registertype(Part, Partition)
    ObjectManager.registertype(Property, Partition)
    ObjectManager.registertype(IndexCurve, Well)
    ObjectManager.registertype(Seismic)
    ObjectManager.registertype(Velocity)
    ObjectManager.registertype(Scalogram)
  
   

def register_UIManager_classes():
    UIManager.register_class(MainWindowController, MainWindowModel, MainWindow)    
    UIManager.register_class(MenuBarController, MenuBarModel, MenuBarView, MainWindowController) 
    
    UIManager.register_class(MenuController, MenuModel, MenuView, MenuBarController)
    UIManager.register_class(MenuController, MenuModel, MenuView, MenuController)
    
    UIManager.register_class(MenuItemController, MenuItemModel, MenuItemView, MenuController)
    UIManager.register_class(ToolBarController, ToolBarModel, ToolBarView, MainWindowController)     
    UIManager.register_class(ToolBarToolController, ToolBarToolModel, None, ToolBarController)  
    UIManager.register_class(TreeController, None, TreeView, MainWindowController)
    UIManager.register_class(StatusBarController, StatusBarModel, StatusBar, MainWindowController)
    UIManager.register_class(LogPlotController, LogPlotModel, LogPlot, MainWindowController)
    UIManager.register_class(TrackController, TrackModel, TrackView, LogPlotController)
    UIManager.register_class(TrackObjectController, TrackObjectModel, 
                             TrackObjectView, TrackController
    )
    UIManager.register_class(LogPlotEditorController, None, LogPlotEditor, LogPlotController)
    
    #UIManager.register_class(ToolBarController, ToolBarModel, ToolBarView, LogPlotController) 
    
    #UIManager.register_class(StatusBarController, StatusBarModel, StatusBar, LogPlotController)
    
    '''
    UIManager.register_class(CrossPlotController, CrossPlotModel, CrossPlot, MainWindowController)
    UIManager.register_class(ToolBarController, ToolBarModel, ToolBarView, CrossPlotController)
    UIManager.register_class(StatusBarController, None, StatusBar, CrossPlotController)
    UIManager.register_class(TrackController, TrackModel, TrackView, LogPlotController)
    '''