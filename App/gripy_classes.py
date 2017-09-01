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
from DT.DataTypes import Angle

from DT.DataTypes import Inversion
#from DT.DataTypes import InvIndexCurve
from DT.DataTypes import InversionParameter
from DT.DataTypes import WellGather




from UI.uimanager import UIManager
from UI.mvc_classes.main_window import MainWindowController, MainWindowModel, MainWindow
from UI.mvc_classes.menu_bar import MenuBarController, MenuBarModel, MenuBarView
from UI.mvc_classes.menu import MenuController, MenuModel, MenuView
from UI.mvc_classes.menu_item import MenuItemController, MenuItemModel, MenuItemView
from UI.mvc_classes.tree import TreeController, TreeView
from UI.mvc_classes.tool_bar import ToolBarController, ToolBarModel, ToolBar
from UI.mvc_classes.tool_bar_tool import ToolBarToolController, ToolBarToolModel
from UI.mvc_classes.status_bar import StatusBarController, StatusBarModel, StatusBar
from UI.mvc_classes.log_plot import LogPlotController, LogPlotModel, LogPlot
from UI.mvc_classes.track import TrackController, TrackModel, TrackView
from UI.mvc_classes.track_object import TrackObjectController, \
    TrackObjectModel#, TrackObjectView
    
from UI.mvc_classes.cross_plotter import CrossPlotController, CrossPlotModel, CrossPlot

from UI.mvc_classes.workpage import WorkPageController, WorkPageModel, WorkPage


from UI.mvc_classes.track_object import \
    LineRepresentationController, LineRepresentationModel, LineRepresentationView, \
    IndexRepresentationController, IndexRepresentationModel, IndexRepresentationView, \
    DensityRepresentationController, DensityRepresentationModel, DensityRepresentationView, \
    PatchesRepresentationController, PatchesRepresentationModel, PatchesRepresentationView, \
    ContourfRepresentationController, ContourfRepresentationModel, ContourfRepresentationView
    

                        
from UI.mvc_classes.lpf import LogPlotEditorController, LogPlotEditor        

from UI.mvc_classes.lpf import LPETrackPanelController, LPETrackPanel
from UI.mvc_classes.lpf import LPEObjectsPanelController, LPEObjectsPanel

from UI.mvc_classes.propgrid import PropertyGridController, \
                                            PropertyGridView


def register_app_classes():
    register_OM_classes()
    register_UIManager_classes()    
    
    
def register_OM_classes():
    
    ObjectManager.register_class(Well)
    ObjectManager.register_class(IndexCurve, Well)
    ObjectManager.register_class(Core, Well)
    ObjectManager.register_class(Log, Well)
    ObjectManager.register_class(Partition, Well)
    
    ObjectManager.register_class(Part, Partition)
    ObjectManager.register_class(Property, Partition)
    
    ObjectManager.register_class(Seismic)
#    ObjectManager.register_class(Trace, Seismic)
    
    ObjectManager.register_class(Velocity)
    ObjectManager.register_class(Scalogram)
  
    ObjectManager.register_class(Angle)   
    
    ObjectManager.register_class(Inversion)
    ObjectManager.register_class(IndexCurve, Inversion)
    ObjectManager.register_class(InversionParameter, Inversion)
    #
    ObjectManager.register_class(WellGather, Well)
    #
    
    
def register_UIManager_classes():
    UIManager.register_class(MainWindowController, MainWindowModel, MainWindow)    
    UIManager.register_class(MenuBarController, MenuBarModel, MenuBarView, MainWindowController) 
    UIManager.register_class(MenuController, MenuModel, MenuView, MenuBarController)
    UIManager.register_class(MenuController, MenuModel, MenuView, MenuController)
    UIManager.register_class(MenuItemController, MenuItemModel, MenuItemView, MenuController)
    UIManager.register_class(ToolBarController, ToolBarModel, ToolBar, MainWindowController)     
    UIManager.register_class(ToolBarToolController, ToolBarToolModel, None, ToolBarController)  
    UIManager.register_class(TreeController, None, TreeView, MainWindowController)
    UIManager.register_class(StatusBarController, StatusBarModel, StatusBar, MainWindowController)
    UIManager.register_class(LogPlotController, LogPlotModel, LogPlot, MainWindowController)
    UIManager.register_class(CrossPlotController, CrossPlotModel, CrossPlot, MainWindowController)
    UIManager.register_class(TrackController, TrackModel, TrackView, LogPlotController)
    UIManager.register_class(TrackObjectController, TrackObjectModel, None,
                              TrackController
    )
    UIManager.register_class(LogPlotEditorController, None, LogPlotEditor, LogPlotController)
    UIManager.register_class(LineRepresentationController, LineRepresentationModel, 
                             LineRepresentationView, TrackObjectController
    )
    UIManager.register_class(IndexRepresentationController, IndexRepresentationModel, 
                             IndexRepresentationView, TrackObjectController
    )
    UIManager.register_class(DensityRepresentationController, DensityRepresentationModel, 
                             DensityRepresentationView, TrackObjectController
    )
    UIManager.register_class(PatchesRepresentationController, PatchesRepresentationModel, 
                              PatchesRepresentationView, TrackObjectController
    )
    UIManager.register_class(LPETrackPanelController, None, LPETrackPanel, 
                             LogPlotEditorController
    )
    UIManager.register_class(LPEObjectsPanelController, None, LPEObjectsPanel, 
                             LogPlotEditorController
    )
    UIManager.register_class(PropertyGridController, None,
                             PropertyGridView, LPEObjectsPanelController
    )
    UIManager.register_class(ContourfRepresentationController, ContourfRepresentationModel,     
                              ContourfRepresentationView, TrackObjectController
    )
    
    UIManager.register_class(WorkPageController, WorkPageModel, WorkPage, MainWindowController)