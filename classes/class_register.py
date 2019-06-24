# -*- coding: utf-8 -*-

from classes.om import ObjectManager
from classes.ui import UIManager
#
from classes.om import Well
from classes.om import DataIndex
from classes.om import DataIndexMap
from classes.om import Log
from classes.om import CurveSet
from classes.om import Seismic
from classes.om import Spectogram

"""
from classes.dt.datatypes import Core
from classes.dt.datatypes import Partition
from classes.dt.datatypes import RockTable
from classes.dt.datatypes import Inference
from classes.dt.datatypes import RockType
from classes.dt.datatypes import Part
from classes.dt.datatypes import Property

#from classes.dt.datatypes import Velocity


from classes.dt.datatypes import Scalogram
from classes.dt.datatypes import GatherScalogram
from classes.dt.datatypes import Spectogram
from classes.dt.datatypes import GatherSpectogram

#from classes.dt.datatypes import Angle
#from classes.dt.datatypes import Inversion
#from classes.dt.datatypes import InversionParameter
from classes.dt.datatypes import WellGather
#from classes.dt.datatypes import IndexSet


from classes.dt.datatypes import Model1D
from classes.dt.datatypes import Zone
from classes.dt.datatypes import ZoneSet
#
from classes.inference.dtrock import Rock
from classes.inference.dtrock import Fluid
#
"""
#

#
from classes.ui import DataMaskController, DataMask
from ui.mvc_classes.wxgripy import FrameController, Frame
from ui.mvc_classes.wxgripy import DialogController, Dialog
from ui.mvc_classes.main_window import MainWindowController,MainWindow
from ui.mvc_classes.menu_bar import MenuBarController, MenuBarView
from ui.mvc_classes.menu import MenuController, MenuView
from ui.mvc_classes.menu_item import MenuItemController, MenuItemView
from ui.mvc_classes.tree import TreeController, TreeView
from ui.mvc_classes.tool_bar import ToolBarController, ToolBar
from ui.mvc_classes.tool_bar_tool import ToolBarToolController
from ui.mvc_classes.status_bar import StatusBarController, StatusBar
from ui.mvc_classes.well_plot import WellPlotController, WellPlot
from ui.mvc_classes.track import TrackController, TrackView
from ui.mvc_classes.track_object import TrackObjectController
from ui.mvc_classes.frame_nav import NavigatorController, Navigator
from ui.mvc_classes.cross_plotter import CrossPlotController, CrossPlot
from ui.mvc_classes.workpage import WorkPageController, WorkPage

from ui.mvc_classes.track_object import \
    LineRepresentationController, LineRepresentationView, \
    IndexRepresentationController, IndexRepresentationView, \
    DensityRepresentationController, DensityRepresentationView, \
    PatchesRepresentationController, PatchesRepresentationView, \
    ContourfRepresentationController, ContourfRepresentationView                          
from ui.mvc_classes.lpf import WellPlotEditorController, WellPlotEditor  
from ui.mvc_classes.lpf import LPEWellPlotPanelController, LPEWellPlotPanel      
from ui.mvc_classes.lpf import LPETrackPanelController, LPETrackPanel
from ui.mvc_classes.lpf import LPEObjectsPanelController, LPEObjectsPanel
from ui.mvc_classes.propgrid import PropertyGridController, PropertyGridView
#                                            
from ui.mvc_classes.canvas_plotter import CanvasPlotterController, CanvasPlotter                
from ui.mvc_classes.canvas_track import TrackCanvasController, TrackCanvas   
from ui.mvc_classes.track_label import TrackLabelController, TrackLabel
                   
#
from ui.mvc_classes.dialog_obj_props import \
        ObjectPropertiesDialogController,ObjectPropertiesDialog
        
from ui.mvc_classes.coding_console import ConsoleController, Console



def register_app_classes():
    register_OM_classes()
    register_UIManager_classes()    
    
    
def register_OM_classes():
    ObjectManager.register_class(Well)
    ObjectManager.register_class(CurveSet, Well)
    ObjectManager.register_class(DataIndex, CurveSet)
    ObjectManager.register_class(Log, CurveSet)
    #
    ObjectManager.register_class(Seismic)
    ObjectManager.register_class(DataIndex, Seismic)
    ObjectManager.register_class(DataIndexMap, Seismic)
    #
    ObjectManager.register_class(DataIndexMap, Log)
    #
    ObjectManager.register_class(Spectogram, Log)
    ObjectManager.register_class(DataIndexMap, Spectogram)
    ObjectManager.register_class(DataIndex, Spectogram)
    #
    """
#    ObjectManager.register_class(IndexSet, Well)
    ObjectManager.register_class(Core, Well)
    #
    
    #
    ObjectManager.register_class(Partition, Well)
    ObjectManager.register_class(Part, Partition)
    ObjectManager.register_class(Property, Partition)
    ObjectManager.register_class(Property, Part)
    ObjectManager.register_class(Partition) #remover apos alterar pra rocktbale
    ObjectManager.register_class(RockTable)
    ObjectManager.register_class(RockType, RockTable)
    ObjectManager.register_class(Inference, Well)
    ObjectManager.register_class(Part, Inference)
    ObjectManager.register_class(Rock)   #remover apos alterar pra rocktbale
    ObjectManager.register_class(Rock, Partition)   #remover apos alterar pra rocktbale
    ObjectManager.register_class(Rock, Well)   #remover apos alterar pra rocktbale
    ObjectManager.register_class(Fluid)																			   
    #
    ObjectManager.register_class(Seismic)
    
#    ObjectManager.register_class(IndexSet, Seismic)
    #
    ObjectManager.register_class(Scalogram, Seismic)
    ObjectManager.register_class(DataIndex, Scalogram)
#    ObjectManager.register_class(IndexSet, Scalogram)
    #
    ObjectManager.register_class(WellGather, Well)
    ObjectManager.register_class(DataIndex, WellGather)  
#    ObjectManager.register_class(IndexSet, WellGather)

    ObjectManager.register_class(GatherSpectogram, Well)
    ObjectManager.register_class(DataIndex, GatherSpectogram)
#    ObjectManager.register_class(IndexSet, GatherSpectogram)
    #
    ObjectManager.register_class(GatherScalogram, Well)
    ObjectManager.register_class(DataIndex, GatherScalogram)
#    ObjectManager.register_class(IndexSet, GatherScalogram)
    #
    ObjectManager.register_class(Rock, Well)
    ObjectManager.register_class(Fluid, Well)
    #
#    ObjectManager.register_class(DataIndex, IndexSet)
    
    ObjectManager.register_class(Model1D, Well)
    ObjectManager.register_class(DataIndex, Model1D)
    #
#    ObjectManager.register_class(IndexSet, Model1D)
    #
    ObjectManager.register_class(ZoneSet, Well)
    ObjectManager.register_class(Zone, ZoneSet)
    ObjectManager.register_class(Property, Zone)
    #
    """
    
def register_UIManager_classes():
    UIManager.register_class(FrameController, Frame)
    UIManager.register_class(DialogController, Dialog)
    UIManager.register_class(MainWindowController, MainWindow)    
    UIManager.register_class(MenuBarController, MenuBarView, MainWindowController) 
    UIManager.register_class(MenuController, MenuView, MenuBarController)
    UIManager.register_class(MenuController, MenuView, MenuController)
    UIManager.register_class(MenuItemController, MenuItemView, MenuController)
    UIManager.register_class(ToolBarController, ToolBar, MainWindowController)     
    UIManager.register_class(ToolBarToolController, None, ToolBarController)  
    UIManager.register_class(TreeController, TreeView, MainWindowController)
    UIManager.register_class(StatusBarController, StatusBar, MainWindowController)
    # 
    UIManager.register_class(WorkPageController, WorkPage, MainWindowController)
    UIManager.register_class(WorkPageController, WorkPage, FrameController)
    #
    UIManager.register_class(WellPlotController, WellPlot, MainWindowController)
    UIManager.register_class(WellPlotController, WellPlot, FrameController)
    #
    UIManager.register_class(CrossPlotController, CrossPlot, MainWindowController)
    UIManager.register_class(CrossPlotController, CrossPlot, FrameController)
    # 
    UIManager.register_class(ConsoleController, Console, MainWindowController)
    UIManager.register_class(ConsoleController, Console, FrameController)
    #    
    UIManager.register_class(TrackController, TrackView, WellPlotController)
    UIManager.register_class(TrackObjectController, None,
                              TrackController
    )
    UIManager.register_class(WellPlotEditorController, WellPlotEditor, WellPlotController)
    UIManager.register_class(NavigatorController, Navigator)
    UIManager.register_class(LineRepresentationController, 
                             LineRepresentationView, TrackObjectController
    )
    UIManager.register_class(IndexRepresentationController, 
                             IndexRepresentationView, TrackObjectController
    )
    UIManager.register_class(DensityRepresentationController, 
                             DensityRepresentationView, TrackObjectController
    )
    UIManager.register_class(PatchesRepresentationController,
                              PatchesRepresentationView, TrackObjectController
    )
    UIManager.register_class(LPEWellPlotPanelController, LPEWellPlotPanel, 
                             WellPlotEditorController
    )    
    UIManager.register_class(LPETrackPanelController, LPETrackPanel, 
                             WellPlotEditorController
    )
    UIManager.register_class(LPEObjectsPanelController, LPEObjectsPanel, 
                             WellPlotEditorController
    )
    UIManager.register_class(PropertyGridController,
                             PropertyGridView, LPEObjectsPanelController
    )
    UIManager.register_class(ContourfRepresentationController,  
                              ContourfRepresentationView, TrackObjectController
    )
    #

    UIManager.register_class(CanvasPlotterController, CanvasPlotter, CrossPlotController) 
    
    #
    UIManager.register_class(FrameController, Frame, MainWindowController)
    #
    UIManager.register_class(TrackCanvasController, TrackCanvas, TrackController)
    UIManager.register_class(TrackLabelController, TrackLabel, TrackController)
    #
    UIManager.register_class(ObjectPropertiesDialogController, 
                                                 ObjectPropertiesDialog)
    UIManager.register_class(PropertyGridController,
                             PropertyGridView, ObjectPropertiesDialogController
    )    
    UIManager.register_class(PropertyGridController,
                             PropertyGridView, LPEWellPlotPanelController
    ) 
    #
    UIManager.register_class(DataMaskController, DataMask, TrackObjectController)      