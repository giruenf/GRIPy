# -*- coding: utf-8 -*-

from OM.Manager import ObjectManager
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 


import wx
import wx.propgrid as pg                                  
import App.pubsub as pub

from wx.adv import OwnerDrawnComboBox  


from collections import OrderedDict
import collections
import App.pubsub as pub


###############################################################################
###############################################################################


class IntProperty(pg.IntProperty):    

    def __init__(self, controller_uid, model_key, 
                                 label = pg.PG_LABEL, name = pg.PG_LABEL):
        
        self._controller_uid = controller_uid
        self._model_key = model_key
        super(IntProperty, self).__init__(label, name)

    def ValueToString(self, *args):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        value = controller.model[self._model_key]
        return str(value)

    def StringToValue(self, variant, text, flag):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller.model[self._model_key] = text
        return True    
 
    
        #pg.Append( wxpg.IntProperty("IntWithSpin",value=256) )
        #pg.SetPropertyEditor("IntWithSpin", "SpinCtrl")    
    
    
class FloatProperty(pg.FloatProperty):    

    def __init__(self, controller_uid, model_key, 
                 label = pg.PG_LABEL,
                 name = pg.PG_LABEL):

        self._controller_uid = controller_uid
        self._model_key = model_key
        super(FloatProperty, self).__init__(label, name)


    def ValueToString(self, *args):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        value = controller.model[self._model_key]
        return str(value)


    def StringToValue(self, variant, text, flag):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller.model[self._model_key] = text
        return True    


class PropertyMixin(object):
    
    def _get_value(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        return controller.model[self._model_key]

    def _set_value(self, value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)        
        controller.model[self._model_key] = value   


class BoolProperty(pg.BoolProperty, PropertyMixin):    

    def __init__(self, controller_uid, model_key, 
                                         label=pg.PG_LABEL, name=pg.PG_LABEL):
        self._controller_uid = controller_uid
        self._model_key = model_key
        super(BoolProperty, self).__init__(label, name)
        self.SetAttribute("UseCheckbox", 1)
        self.SetAttribute("UseDClickCycling", 1)
        value = self._get_value()
        self.SetValue(value)
    
    def ValueToString(self, *args):
        value = self._get_value()
        return str(value)
    
    def OnSetValue(self):
        self._set_value(self.GetValue())


            
    
class EnumProperty(pg.EnumProperty, PropertyMixin):    
 
    def __init__(self, controller_uid, model_key, 
                 label=pg.PG_LABEL, name=pg.PG_LABEL, labels=[], 
                 values=None, value=0):
        if labels is None:
            raise Exception('No labels values found in: {} - model key: {}'.\
                            format(controller_uid, model_key)
            )   
        super(EnumProperty, self).__init__(label, name, labels, value=value)
        #pg.EnumProperty(label, name, labels, values, value)
        # EnumProperty(label, name, choice, value=0)  choice as wxPGChoices
        #              
        # EnumProperty(label, name, labels=[], values=[], value=0)
        # labels - list of strings
        # values - list of integers
        
        #wxEnumProperty(const  ::wxString& label,const  ::wxString& name, 
        #                ::wxPGChoices& choices,int value)
        
        self._controller_uid = controller_uid
        self._model_key = model_key
        self._labels = labels
        if not values:
            self._values = labels
        else:    
            self._values = values

        val = self._get_value()
        idx = self._values.index(val)
        self.SetValue(idx)
        
    def IntToValue(self, variant, int_value, flag):
        val = self._values[int_value]
        self._set_value(val)
        return True
        
    def ValueToString(self, value, flag):
        val = self._get_value()
        # self._label.index can raise Exception (Attention)
        idx = self._values.index(val)
        return self._labels[idx]    
        
    def GetIndexForValue(self, value):
        val = self._get_value()
        idx = self._values.index(val)
        return idx



class DynamicEnumProperty(pg.EnumProperty):    
 
    def __init__(self, callback, 
                 label=pg.PG_LABEL, name=pg.PG_LABEL, labels=[], 
                 values=None, value=0):
        if labels is None:
            raise Exception('No labels values found.')
        super(DynamicEnumProperty, self).__init__(label, name, labels, value=value)
        self._callback = callback
        self._labels = labels
        if not values:
            self._values = labels
        else:    
            self._values = values
        wx.CallAfter(self.IntToValue, None, value, None)
        
    def IntToValue(self, variant, int_value, flag):
        self._value = int_value
        value = self._values[self._value]
        self._callback(value)
        return True
        
    def ValueToString(self, value, flag):
        return self._labels[self._value]    
        


def _get_pg_property(uid, model_key, model_key_props):
    if model_key_props.get('label') is None:
        raise Exception('No label found in: {} - model key: {}'.format(uid, \
                                                                    model_key))  
    #if model_key_props.get('pg_property') is None:
    #    return None
    if model_key_props.get('pg_property') == 'IntProperty':
        return IntProperty(uid, model_key, label=model_key_props.get('label'))
    if model_key_props.get('pg_property') == 'FloatProperty':
        return FloatProperty(uid, model_key, label=model_key_props.get('label'))
    if model_key_props.get('pg_property') == 'EnumProperty':
        return EnumProperty(uid, model_key, label=model_key_props.get('label'),
                            labels=model_key_props.get('labels'),
                            values=model_key_props.get('values')
        )    
    if model_key_props.get('pg_property') == 'BoolProperty':
        return BoolProperty(uid, model_key, label=model_key_props.get('label'))                
    raise Exception()



class PropertyGridController(UIControllerBase):
    tid = 'property_grid_controller'
    
    def __init__(self):
        super(PropertyGridController, self).__init__()
        self._properties = collections.OrderedDict()
        self._toc_obj_uid = None


    def clear(self):
        #print 'PropertyGridController.clear()'
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self.uid)
        parent_controller =  UIM.get(parent_controller_uid)
        if parent_controller.view.splitter.IsSplit():  
            parent_controller.view.splitter.Unsplit(self.view)               
        if self._properties:    
            old_obj = UIM.get(self._toc_obj_uid)
            old_repr_ctrl = old_obj.get_representation()
            if old_repr_ctrl.tid != 'patches_representation_controller':
                for key in self._properties.keys():
                    old_repr_ctrl.unsubscribe(self.refresh_property, \
                                              'change.' + key
                    )                     
        self._properties.clear()
        self.view.Clear()
        self._toc_obj_uid = None
 

      
    def get_object_uid(self):
        return self._toc_obj_uid

    def set_object_uid(self, toc_obj_uid): 
        if toc_obj_uid == self._toc_obj_uid:
            self.view.Refresh()
            return
        UIM = UIManager()    
        if toc_obj_uid[0] != 'track_object_controller':
            raise Exception('Cannot set an object with tid != "track_object_controller"')
        toc = UIM.get(toc_obj_uid)
        if not toc.is_valid():
            return  
    
        self.clear()
        title = toc.get_object().get_friendly_name()
        #title = toc.get_object()._TID_FRIENDLY_NAME + ': ' + \
        #                                            toc.get_object().name
        self.view.Append(
            pg.PropertyCategory(title, name='title')
        )
        
        repr_ctrl = toc.get_representation()
        if repr_ctrl.tid != 'patches_representation_controller':
            #print
            for key, key_props in repr_ctrl.model._ATTRIBUTES.items():
                property_ = _get_pg_property(repr_ctrl.uid, key, key_props)
                #print '\n', repr_ctrl.uid, key, key_props, property_
                self._properties[key] = property_
                self.view.Append(property_)
                repr_ctrl.subscribe(self.refresh_property, 'change.' + key)
        else:
            obj = toc.get_object()
            OM = ObjectManager(self)
            parts =  OM.list('part', obj.uid)
            parts_name = [part.name for part in parts]
            parts_uid = [part.uid for part in parts]
            property_ = DynamicEnumProperty(self.cb, label='Select part',
                        labels=parts_name,
                        values=parts_uid,
                        value=len(parts_uid)-1
            )  
            self._properties['part'] = property_
            self.view.Append(property_)
        self._toc_obj_uid = toc_obj_uid
        
        
    def cb(self, value):
        OM = ObjectManager(self)
        part = OM.get(value)
        color_prop = self._properties.get('color')
        if color_prop:
            self.view.DeleteProperty(color_prop.GetName())
        mpl_color = part.color #[float(c)/255.0 for c in part.color]
        print value, '-', mpl_color
        color_prop = pg.ColourProperty(label='Part color', value=mpl_color)
        self._properties['color'] = color_prop
        self.view.Append(color_prop)
        
        
    def refresh_property(self, topicObj=pub.AUTO_TOPIC, 
                                              new_value=None, old_value=None):
        #obj_uid = pub.pubuid_to_uid(topicObj.getName().split('.')[0])
        key = topicObj.getName().split('.')[-1]
        p = self._properties[key]
        self.view.RefreshProperty(p)



class PropertyGridView(UIViewBase, pg.PropertyGrid):
    tid = 'property_grid_view'

    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)      
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        
        pg.PropertyGrid.__init__(self, parent_controller.view.splitter, 
                        style=pg.PG_SPLITTER_AUTO_CENTER|pg.PG_HIDE_MARGIN
        )
        self.SetCaptionBackgroundColour(wx.Colour(0,128,192))
        self.SetCaptionTextColour('white')       


    
"""    
# Index

    def get_propgrid(self, parent):
        propgrid = self._get_propgrid(parent)
        propgrid.Append( 
            FloatProperty(self._controller_uid, 'step', 
                            label='Step'
            )
        )
        propgrid.Append(              
            EnumProperty(self._controller_uid, 'pos_x',
                         label='Horizontal Alignment',
                         labels=['Left', 'Center', 'Right'],
                         values=[0.1, 0.5, 0.9]
            ) 
        ) 
        propgrid.Append(
            EnumProperty(self._controller_uid, 'fontsize', 
                         label='Font Size',
                         labels=['7', '8', '9', '10', '11', '12', '13'],
                         values=[7, 8, 9, 10, 11, 12, 13]
            )             
        )            
        propgrid.Append(
            EnumProperty(self._controller_uid, 'color', 
                         label='Color',
                         labels=ColorSelectorComboBox.get_colors()            
            )             
        )    
        propgrid.Append(  
            BoolProperty(self._controller_uid, 'bbox', 
                         label='Bbox'
            )    
        )  
        propgrid.Append(              
            EnumProperty(self._controller_uid, 'bbox_style',
                         label='Bbox Style',
                         labels=['Circle', 'DArrow', 'LArrow', 'RArrow', 
                                 'Round', 'Round4', 'Roundtooth', 'Sawtooth',
                                 'Square'],
                         values=['circle', 'darrow', 'larrow', 'rarrow',
                                 'round', 'round4', 'roundtooth', 'sawtooth',
                                 'square']
            ) 
        ) 
        propgrid.Append(
            EnumProperty(self._controller_uid, 'bbox_color', 
                         label='Bbox Color',
                         labels=ColorSelectorComboBox.get_colors()            
            )             
        )        
        propgrid.Append( 
            FloatProperty(self._controller_uid, 'bbox_alpha', 
                            label='Bbox Alpha'
            )
        )            
        propgrid.Append(              
            EnumProperty(self._controller_uid, 'ha',
                         label='Horizontal Alignment in the TextBox',
                         labels=['Left', 'Center', 'Right'],
                         values=['left', 'center', 'right']
            ) 
        )
        propgrid.Append(
            EnumProperty(self._controller_uid, 'va',
                         label='Vertical Alignment in the TextBox',
                         labels=['Top', 'Center', 'Bottom', 'Baseline'],
                         values=['top', 'center', 'bottom', 'baseline']
            ) 
        )            
        return propgrid  


#Density



    def get_propgrid(self, parent):
        propgrid = self._get_propgrid(parent)
        propgrid.Append(
            EnumProperty(self._controller_uid, 'type', 
                         label='Plot type',
                         labels=['Density', 'Wiggle', 'Both'],     
                         values=['density', 'wiggle', 'both']
            )             
        ) 
        propgrid.Append(
            EnumProperty(self._controller_uid, 'colormap', 
                         label='Colormap',
                         labels=MPL_COLORMAPS            
            )             
        )
        propgrid.Append(
            EnumProperty(self._controller_uid, 'interpolation', 
                         label='Colormap interpolation',
                         labels=['none', 'nearest', 'bilinear', 'bicubic',
                                  'spline16', 'spline36', 'hanning', 'hamming',
                                  'hermite', 'kaiser', 'quadric', 'catrom',
                                  'gaussian', 'bessel', 'mitchell', 'sinc',
                                  'lanczos'
                         ]         
            )             
        )            
            # Interpolation values accepted
            # ‘none’, ‘nearest’, ‘bilinear’, ‘bicubic’, ‘spline16’,
            # ‘spline36’, ‘hanning’, ‘hamming’, ‘hermite’, ‘kaiser’, ‘quadric’, ‘catrom’,
            # ‘gaussian’, ‘bessel’, ‘mitchell’, ‘sinc’, ‘lanczos’            
        propgrid.Append( 
            FloatProperty(self._controller_uid, 'min_density', 
                            label='Colormap min value'
            )
        )   
        propgrid.Append( 
            FloatProperty(self._controller_uid, 'max_density', 
                            label='Colormap max value'
            )
        )   

        propgrid.Append( 
            FloatProperty(self._controller_uid, 'density_alpha', 
                            label='Colormap alpha'
            )
        )  

        propgrid.Append(
            EnumProperty(self._controller_uid, 'linewidth', 
                         label='Wiggle line width',
                         labels=['0', '1', '2', '3'], #, '10', '11', '12', '13'],
                         values=[0, 1, 2, 3]#, 10, 11, 12, 13]
            )             
        )            
        propgrid.Append(
            EnumProperty(self._controller_uid, 'linecolor', 
                         label='Wiggle line color',
                         labels=ColorSelectorComboBox.get_colors()            
            )             
        )   
        propgrid.Append( 
            FloatProperty(self._controller_uid, 'min_wiggle', 
                            label='Wiggle min value'
            )
        )   
        propgrid.Append( 
            FloatProperty(self._controller_uid, 'max_wiggle', 
                            label='Wiggle max value'
            )
        )      
        propgrid.Append( 
            FloatProperty(self._controller_uid, 'wiggle_alpha', 
                            label='Wiggle alpha'
            )
        )  
        propgrid.Append(  
            EnumProperty(self._controller_uid, 'fill', 
                         label='Wiggle fill type',
                         labels=['None', 'Left', 'Right', 'Both'],     
                         values=[None, 'left', 'right', 'both']
            )          
        )  

        propgrid.Append(
            EnumProperty(self._controller_uid, 'fill_color_left', 
                         label='Wiggle left fill color',
                         labels=ColorSelectorComboBox.get_colors()            
            )             
        )   
        propgrid.Append(
            EnumProperty(self._controller_uid, 'fill_color_right', 
                         label='Wiggle right fill color',
                         labels=ColorSelectorComboBox.get_colors()            
            )             
        )            
        return propgrid  
    
    
# Partitions
       
    def get_propgrid(self, parent):
        propgrid = self._get_propgrid(parent)
         
        return propgrid           
    
    
    
"""


   



'''
class ColorSelectorComboBox(OwnerDrawnComboBox):
    colors = OrderedDict()
    colors['Black'] = None
    colors['Maroon'] = None
    colors['Green'] = wx.Colour(0, 100, 0) # Dark Green
    colors['Olive'] = wx.Colour(128, 128, 0)
    colors['Navy'] = None
    colors['Purple'] = None
    colors['Teal'] = wx.Colour(0, 128, 128)
    colors['Gray'] = None
    colors['Silver'] = wx.Colour(192, 192, 192)
    colors['Red'] = None
    colors['Lime'] = wx.Colour(0, 255, 0) # Green
    colors['Yellow'] = None
    colors['Blue'] = None
    colors['Fuchsia'] = wx.Colour(255, 0, 255)
    colors['Aqua'] = wx.Colour(0, 255, 255)
    colors['White'] = None
    colors['SkyBlue'] = wx.Colour(135, 206, 235)
    colors['LightGray'] = wx.Colour(211, 211, 211)
    colors['DarkGray'] = wx.Colour(169, 169, 169)
    colors['SlateGray'] = wx.Colour(112, 128, 144)
    colors['DimGray'] = wx.Colour(105, 105, 105)
    colors['BlueViolet'] = wx.Colour(138, 43, 226)
    colors['DarkViolet'] = wx.Colour(148, 0, 211)
    colors['Magenta'] = None
    colors['DeepPink'] = wx.Colour(148, 0, 211)
    colors['Brown'] = None
    colors['Crimson'] = wx.Colour(220, 20, 60)
    colors['Firebrick'] = None
    colors['DarkRed'] = wx.Colour(139, 0, 0)
    colors['DarkSlateGray'] = wx.Colour(47, 79, 79)
    colors['DarkSlateBlue'] = wx.Colour(72, 61, 139)
    colors['Wheat'] = None
    colors['BurlyWood'] = wx.Colour(222, 184, 135)
    colors['Tan'] = None
    colors['Gold'] = None
    colors['Orange'] = None
    colors['DarkOrange'] = wx.Colour(255, 140, 0)
    colors['Coral'] = None
    colors['DarkKhaki'] = wx.Colour(189, 183, 107)
    colors['GoldenRod'] = None
    colors['DarkGoldenrod'] = wx.Colour(184, 134, 11)
    colors['Chocolate'] = wx.Colour(210, 105, 30)
    colors['Sienna'] = None
    colors['SaddleBrown'] = wx.Colour(139, 69, 19)
    colors['GreenYellow'] = wx.Colour(173, 255, 47)
    colors['Chartreuse'] = wx.Colour(127, 255, 0)
    colors['SpringGreen'] = wx.Colour(0, 255, 127)
    colors['MediumSpringGreen'] = wx.Colour(0, 250, 154)
    colors['MediumAquamarine'] = wx.Colour(102, 205, 170)
    colors['LimeGreen'] = wx.Colour(50, 205, 50)
    colors['LightSeaGreen'] = wx.Colour(32, 178, 170)
    colors['MediumSeaGreen'] = wx.Colour(60, 179, 113)
    colors['DarkSeaGreen'] = wx.Colour(143, 188, 143)
    colors['SeaGreen'] = wx.Colour(46, 139, 87)
    colors['ForestGreen'] = wx.Colour(34, 139, 34)
    colors['DarkOliveGreen'] = wx.Colour(85, 107, 47)
    colors['DarkGreen'] = wx.Colour(1, 50, 32)
    colors['LightCyan'] = wx.Colour(224, 255, 255)
    colors['Thistle'] = None
    colors['PowderBlue'] = wx.Colour(176, 224, 230)
    colors['LightSteelBlue'] = wx.Colour(176, 196, 222)
    colors['LightSkyBlue'] = wx.Colour(135, 206, 250)
    colors['MediumTurquoise'] = wx.Colour(72, 209, 204)
    colors['Turquoise'] = None
    colors['DarkTurquoise'] = wx.Colour(0, 206, 209)
    colors['DeepSkyBlue'] = wx.Colour(0, 191, 255)
    colors['DodgerBlue'] = wx.Colour(30, 144, 255)
    colors['CornflowerBlue'] = wx.Colour(100, 149, 237)
    colors['CadetBlue'] = wx.Colour(95, 158, 160)
    colors['DarkCyan'] = wx.Colour(0, 139, 139)
    colors['SteelBlue'] = wx.Colour(70, 130, 180)
    colors['RoyalBlue'] = wx.Colour(65, 105, 225)
    colors['SlateBlue'] = wx.Colour(106, 90, 205)
    colors['DarkBlue'] = wx.Colour(0, 0, 139)
    colors['MediumBlue'] = wx.Colour(0, 0, 205)
    colors['SandyBrown'] = wx.Colour(244, 164, 96)
    colors['DarkSalmon'] = wx.Colour(233, 150, 122)
    colors['Salmon'] = None
    colors['Tomato'] = wx.Colour(255, 99, 71) 
    colors['Violet'] = wx.Colour(238, 130, 238)
    colors['HotPink'] = wx.Colour(255, 105, 180)
    colors['RosyBrown'] = wx.Colour(188, 143, 143)
    colors['MediumVioletRed'] = wx.Colour(199, 21, 133)
    colors['DarkMagenta'] = wx.Colour(139, 0, 139)
    colors['DarkOrchid'] = wx.Colour(153, 50, 204)
    colors['Indigo'] = wx.Colour(75, 0, 130)
    colors['MidnightBlue'] = wx.Colour(25, 25, 112)
    colors['MediumSlateBlue'] = wx.Colour(123, 104, 238)
    colors['MediumPurple'] = wx.Colour(147, 112, 219)
    colors['MediumOrchid'] = wx.Colour(186, 85, 211)        
  
    
    def __init__(self, *args, **kwargs): 
        print 'ColorSelectorComboBox.__init__'
        kwargs['choices'] = self.colors.keys()
        OwnerDrawnComboBox.__init__(self, *args, **kwargs)
        print 'ColorSelectorComboBox.__init__ ENDED'
        #super(ColorSelectorComboBox, self).SetSelection().#SetSelection()
        
    """    
    def OnDrawItem(self, dc, rect, item, flags):
        print 'OnDrawItem:' , item, flags
        if wx.adv.ODCB_PAINTING_CONTROL == flags:
            print 'wx.adv.ODCB_PAINTING_CONTROL'
        elif wx.adv.ODCB_PAINTING_SELECTED == flags:
            print 'ODCB_PAINTING_SELECTED'
        if item == wx.NOT_FOUND:
            # painting the control, but there is no valid item selected yet
            return 
        font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Segoe UI')             
        dc.SetFont(font)
        
        if flags == 3:
            margin = 3    
        else:
            margin = 1
        r = wx.Rect(*rect)  # make a copy
        r.Deflate(margin, margin)
        tam = self.OnMeasureItem(item)-2
        dc.SetPen(wx.Pen("grey", style=wx.TRANSPARENT))
        color_name = self.GetString(item)     
        color = self.colors.get(color_name)
        if not color:
            color = wx.Colour(color_name)
        dc.SetBrush(wx.Brush(color))
        dc.DrawRectangle(r.x, r.y, tam, tam)
        dc.DrawText(self.GetString(item), r.x + tam + 2, r.y)            
    """   
        
    def OnMeasureItem(self, item):
        #print 'OnMeasureItem'
        return 15


    @staticmethod
    def get_colors():
        return ColorSelectorComboBox.colors.keys()

'''    


'''
class ColorPropertyEditor(pg.PGEditor):

    def __init__(self):
        print 'ColorPropertyEditor.__init__'
        pg.PGEditor.__init__(self)
        print 'ColorPropertyEditor.__init__ ENDED'
        
        
    def CreateControls(self, propgrid, property, pos, size):
        print '\nCreateControls'
        csc = ColorSelectorComboBox(propgrid.GetPanel(), pos=pos, size=size)
        idx = ColorSelectorComboBox.get_colors().index(property.get_value())
        csc.SetSelection(idx)
        window_list = pg.PGWindowList(csc)
        return window_list


    def GetName(self):
        return 'ColorPropertyEditor'
    
    
    def UpdateControl(self, property, ctrl):
        idx = ColorSelectorComboBox.get_colors().index(property.get_value())
        print 'UpdateControl:', idx
        ctrl.SetSelection(idx)


    def DrawValue(self, dc, rect, property, text):        
        print 'DrawValue:', text
        #dc.SetPen( wxPen(propertyGrid->GetCellTextColour(), 1, wxSOLID) )
        #pen = dc.GetPen()
        #print pen.GetColour(), pen.GetStyle(), wx.PENSTYLE_SOLID
        #dc.SetPen(wx.Pen(wx.Colour(0, 0, 255, 255), 1, wx.SOLID))
        cell_renderer = property.GetCellRenderer(1)
        cell_renderer.DrawText(dc, rect, 0, text) # property.get_value())#rect.x+15, rect.y)
        #dc.DrawText(property.get_value(), rect.x+15, rect.y)
    #    if not property.IsValueUnspecified():
    #        dc.DrawText(property.get_value(), rect.x+5, rect.y)


    def OnEvent(self, propgrid, property, ctrl, event):
        if isinstance(event, wx.CommandEvent):
            if event.GetEventType() == wx.EVT_COMBOBOX:
                print 'COMBAO DA MASSA\n\n\n'
            if event.GetString():
                print 'VALUE:', event.GetString(), '\n'
                return True
        return False


    def GetValueFromControl(self, variant, property, ctrl):
        """ Return tuple (wasSuccess, newValue), where wasSuccess is True if
            different value was acquired succesfully.
        """
        print '\nGetValueFromControl:', ctrl.GetValue()
        if property.UsesAutoUnspecified() and not ctrl.GetValue():
            return True
        ret_val = property.StringToValue(ctrl.GetValue(), pg.PG_EDITABLE_VALUE)
        return ret_val


    def SetValueToUnspecified(self, property, ctrl):
        print '\nSetValueToUnspecified'
        ctrl.SetSelection(0) #Remove(0, len(ctrl.GetValue()))


    """
    def SetControlIntValue(self, property, ctrl, value):
        print 'SetControlIntValue:', value

    def SetControlStringValue(self, property, ctrl, text):
        print 'SetControlStringValue'
        ctrl.SetValue(text)
    """     

    """
    def SetControlAppearance(self, pg, property, ctrl, cell, old_cell, unspecified):
        print 'SetControlAppearance' 
        """
        cb = ctrl
        tc = ctrl.GetTextCtrl()
        
        changeText = False
        
        if cell.HasText() and not pg.IsEditorFosuced():
            print '   ENTROU A'
            tcText = cell.GetText()
            changeText = True
        elif old_cell.HasText():
            print '   ENTROU B'
            tcText = property.get_value()
            changeText = True
        else:
            print '   NEM A NEM B'
        if changeText:
            if tc:
                print '   ENTROU C'
                pg.SetupTextCtrlValue(tcText)
                tc.SetValue(tcText)
            else:
                print '   ENTROU D'
                cb.SetText(tcText)
        else:
            print '   NEM C NEM D'
        """    
        """    
        # Do not make the mistake of calling GetClassDefaultAttributes()
        # here. It is static, while GetDefaultAttributes() is virtual
        # and the correct one to use.
        vattrs = ctrl.GetDefaultAttributes()
    
        #Foreground colour
        fgCol = cell.GetFgCol()
        if fgCol.IsOk():
            ctrl.SetForegroundColour(fgCol)
            print 'fgCol:', fgCol
        
        elif old_cell.GetFgCol().IsOk():
            ctrl.SetForegroundColour(vattrs.colFg)
            print 'vattrs.colFg:', vattrs.colFg
    
        # Background colour
        bgCol = cell.GetBgCol()
        if bgCol.IsOk():
            ctrl.SetBackgroundColour(bgCol)
        elif old_cell.GetBgCol().IsOk():
            ctrl.SetBackgroundColour(vattrs.colBg)
    
        # Font
        font = cell.GetFont()
        if font.IsOk():
            ctrl.SetFont(font)
        elif old_cell.GetFont().IsOk():
            ctrl.SetFont(vattrs.font)
        """  
        # Also call the old SetValueToUnspecified()
        #if unspecified
        #    SetValueToUnspecified(property, ctrl);

                
        #print 'cell.GetText():', cell.GetText()
        #print 'old_cell.GetText():', old_cell.GetText()
        
        #print tc#, tc.GetText()
        super(ColorPropertyEditor, self).SetControlAppearance(pg, property, ctrl, cell, old_cell, unspecified)
    """    

    def InsertItem(self, ctrl, label, index):
        print 'InsertItem:', label, index
        
        
    def CanContainCustomImage(self):
        print 'CanContainCustomImage'
        return True
    
    def OnFocus(self, property, ctrl):
        #print 'OnFocus:' #, property, ctrl
        #ctrl.SetSelection(-1)#,-1)
        ctrl.SetFocus()



class ColorProperty(pg.PGProperty):
    # All arguments of this ctor should have a default value -
    # use wx.propgrid.PG_LABEL for label and name
    def __init__(self, controller_uid, model_key, 
             label = pg.PG_LABEL,
             name = pg.PG_LABEL):
        print 'ColorProperty.__init__'
        self._controller_uid = controller_uid
        self._model_key = model_key
        super(pg.PGProperty, self).__init__(label, name)
        self.SetValue(self.get_value())
        print 'ColorProperty.__init__ ENDED'
        
        
    #def OnSetValue(self):
    #    print 'ColorProperty.OnSetValue'
        
    def DoGetEditorClass(self):
        #print 'ColorProperty.DoGetEditorClass'
        return pg.PropertyGridInterface.GetEditorByName('ColorPropertyEditor')
        #_CPEditor #ColorPropertyEditor #wx.PGEditor_TextCtrl

    def ValueToString(self, value, flags):
        print '\nColorProperty.ValueToString'
        value = self.get_value()
        return value

    def StringToValue(self, text, flags):
        print 'ColorProperty.StringToValue:', text
        value = self.set_value(text) 
        self.SetValue(value)
        return value      
    
    def get_value(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        print 'ColorProperty.get_value:', controller.model[self._model_key]
        return controller.model[self._model_key]


    def set_value(self, new_value):
        print 'ColorProperty.set_value', new_value
        try:
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            controller.model[self._model_key] = new_value  
            return True
        except:
            return False


    def GetDisplayedString(self):
        print 'GetDisplayedString'
        return self.get_value()

    def GetChoiceSelection(self):
        idx = ColorSelectorComboBox.get_colors().index(self.get_value())
        print 'GetChoiceSelection:', idx
        return idx

    def IsTextEditable(self):
        ret = super(pg.PGProperty, self).IsTextEditable()
        print 'IsTextEditable'
        return ret

    def IsValueUnspecified(self):
        print '\n\nColorProperty.IsValueUnspecified\n\n'
        return False
  
    def SetLabel(self, label):
        print 'SetLabel:', label
        super(pg.PGProperty, self).SetLabel(label)
    
 
'''



  
        

                       
    
    
    