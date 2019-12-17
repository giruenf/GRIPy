from collections import OrderedDict

from app.app_utils import DropTarget
from classes.ui import UIManager
from classes.ui import CanvasBaseController
from classes.ui import CanvasBaseView
from app import log


class CanvasPlotterController(CanvasBaseController):
    tid = 'canvas_plotter_controller'

    def __init__(self, **state):
        super().__init__(**state)

    def PostInit(self):
        super().PostInit()

    def get_friendly_name(self):
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self.uid)
        parent = UIM.get(parent_uid)
        return parent.get_friendly_name()

    ######    

    def _get_pg_categories(self):
        cats = OrderedDict([
            ('category_general', OrderedDict([
                ('label', 'General')
            ])),

            ('category_labelstext', OrderedDict([
                ('label', 'Labels Texts')
            ])),

            ('category_figure', OrderedDict([
                ('label', 'Figure')
            ])),

            ('category_axes', OrderedDict([
                ('label', 'Axes'),
                ('children', OrderedDict([
                    ('category_axes_label', OrderedDict([
                        ('label', 'Label')
                    ])),
                    ('category_axes_titletext', OrderedDict([
                        ('label', 'Title text')
                    ])),
                    ('category_axes_title', OrderedDict([
                        ('label', 'Title')
                    ])),
                ])),
            ])),

            ('category_grid', OrderedDict([
                ('label', 'Grid'),
                ('children', OrderedDict([
                    ('category_grid_xmajor', OrderedDict([
                        ('label', 'Major on X axis')
                    ])),
                    ('category_grid_xminor', OrderedDict([
                        ('label', 'Minor on X axis')
                    ])),
                    ('category_grid_ymajor', OrderedDict([
                        ('label', 'Major on Y axis')
                    ])),
                    ('category_grid_yminor', OrderedDict([
                        ('label', 'Minor on Y axis')
                    ])),
                ])),
            ])),

            ('category_spines', OrderedDict([
                ('label', 'Spines'),
                ('children', OrderedDict([
                    ('category_spines_position', OrderedDict([
                        ('label', 'Position')
                    ]))
                ])),
            ])),

            ('category_axis', OrderedDict([
                ('label', 'Axis')
            ])),

            ('category_tick', OrderedDict([
                ('label', 'Tick')
            ]))

        ])
        return cats

    def _get_pg_properties(self):
        """
        """
        props = OrderedDict()

        ### category_general
        props['rect'] = {
            'pg_property': 'StringProperty',
            'label': 'Rect',
            'category': 'category_general'
        }

        props['xscale'] = {
            'label': 'X axis scale',
            'pg_property': 'MPLScaleProperty',
            'category': 'category_general'
        }

        props['yscale'] = {
            'label': 'Y axis scale',
            'pg_property': 'MPLScaleProperty',
            'category': 'category_general'
        }

        props['xlim'] = {
            'pg_property': 'StringProperty',
            'label': 'X limits',
            'category': 'category_general'
        }

        props['ylim'] = {
            'pg_property': 'StringProperty',
            'label': 'Y limits',
            'category': 'category_general'
        }

        ### category_labelstexts
        props['xaxis_labeltext'] = {
            'pg_property': 'StringProperty',
            'label': 'X axis',
            'category': 'category_labelstext'
        }

        props['yaxis_labeltext'] = {
            'pg_property': 'StringProperty',
            'label': 'Y axis',
            'category': 'category_labelstext'
        }

        ### category_figure
        props['figure_facecolor'] = {
            #            'pg_property': 'MPLColorsProperty',
            #            'pg_property': 'SystemColourProperty',
            'pg_property': 'ColourProperty',
            'label': 'Face color',
            'category': 'category_figure'
        }
        props['figure_titletext'] = {
            'pg_property': 'StringProperty',
            'label': 'Title text',
            'category': 'category_figure'
        }
        props['figure_titlex'] = {
            'pg_property': 'FloatProperty',
            'label': 'Title X',
            'category': 'category_figure'
        }
        props['figure_titley'] = {
            'pg_property': 'FloatProperty',
            'label': 'Title Y',
            'category': 'category_figure'
        }
        props['figure_titlesize'] = {
            'pg_property': 'FloatProperty',
            'label': 'Title size',
            'category': 'category_figure'
        }
        props['figure_titleweight'] = {
            'pg_property': 'StringProperty',
            'label': 'Title weight',
            'category': 'category_figure'
        }
        props['figure_titleha'] = {
            'pg_property': 'MPLHAProperty',
            'label': 'Title horizontal alignment',
            'category': 'category_figure'
        }
        props['figure_titleva'] = {
            'pg_property': 'MPLVAProperty',
            'label': 'Title vertical alignment',
            'category': 'category_figure'
        }

        ### category_axes
        props['axes_facecolor'] = {
            #           'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'label': 'Facecolor',
            'category': 'category_axes'
        }
        props['axes_edgecolor'] = {
            #            'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'label': 'Edgecolor',
            'category': 'category_axes'
        }
        props['axes_axisbelow'] = {
            'pg_property': 'EnumProperty',
            'label': 'Axis below',
            'options_labels': ['True', 'Line', 'False'],
            'options_values': [True, 'line', False],
            'category': 'category_axes'
        }

        props['axes_linewidth'] = {
            'pg_property': 'FloatProperty',
            'label': 'Line width',
            'category': 'category_axes'
        }

        props['axes_labelcolor'] = {
            #            'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'label': 'Color',
            'category': 'category_axes_label'
        }
        props['axes_labelpad'] = {
            'pg_property': 'FloatProperty',
            'label': 'Pad',
            'category': 'category_axes_label'
        }
        props['axes_labelsize'] = {
            'pg_property': 'StringProperty',
            'label': 'Size',
            'category': 'category_axes_label'
        }
        props['axes_labelweight'] = {
            'pg_property': 'StringProperty',
            'label': 'Weight',
            'category': 'category_axes_label'
        }
        #
        props['axes_titletextcenter'] = {
            'pg_property': 'StringProperty',
            'label': 'Center',
            'category': 'category_axes_titletext'
        }
        props['axes_titletextleft'] = {
            'pg_property': 'StringProperty',
            'label': 'Left',
            'category': 'category_axes_titletext'
        }
        props['axes_titletextright'] = {
            'pg_property': 'StringProperty',
            'label': 'Right',
            'category': 'category_axes_titletext'
        }
        props['axes_titlecolor'] = {
            #            'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'label': 'Color',
            'category': 'category_axes_title'
        }
        props['axes_titlepad'] = {
            'pg_property': 'FloatProperty',
            'label': 'Pad',
            'category': 'category_axes_title'
        }
        props['axes_titlesize'] = {
            'pg_property': 'StringProperty',
            'label': 'Size',
            'category': 'category_axes_title'
        }
        props['axes_titleweight'] = {
            'pg_property': 'StringProperty',
            'label': 'Weight',
            'category': 'category_axes_title'
        }

        ### category_grid
        props['xgrid_major'] = {
            'pg_property': 'BoolProperty',
            'label': 'Major on X axis',
            'category': 'category_grid'
        }
        props['xgrid_minor'] = {
            'pg_property': 'BoolProperty',
            'label': 'Minor on X axis',
            'category': 'category_grid'
        }
        props['ygrid_major'] = {
            'pg_property': 'BoolProperty',
            'label': 'Major on Y axis',
            'category': 'category_grid'
        }
        props['ygrid_minor'] = {
            'pg_property': 'BoolProperty',
            'label': 'Minor on Y axis',
            'category': 'category_grid'
        }
        props['xgrid_major_color'] = {
            #            'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'label': 'Color',
            'category': 'category_grid_xmajor'
        }
        props['xgrid_major_alpha'] = {
            'pg_property': 'FloatProperty',
            'label': 'Alpha',
            'category': 'category_grid_xmajor'
        }
        props['xgrid_major_linestyle'] = {
            'pg_property': 'StringProperty',
            'label': 'Linestyle',
            'category': 'category_grid_xmajor'
        }
        props['xgrid_major_linewidth'] = {
            'pg_property': 'FloatProperty',
            'label': 'Linewidth',
            'category': 'category_grid_xmajor'
        }
        props['xgrid_major_locator'] = {
            'pg_property': 'IntProperty',
            'label': 'Locator',
            'category': 'category_grid_xmajor'
        }
        props['xgrid_minor_color'] = {
            #            'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'label': 'Color',
            'category': 'category_grid_xminor'
        }
        props['xgrid_minor_alpha'] = {
            'pg_property': 'FloatProperty',
            'label': 'Alpha',
            'category': 'category_grid_xminor'
        }
        props['xgrid_minor_linestyle'] = {
            'pg_property': 'StringProperty',
            'label': 'Linestyle',
            'category': 'category_grid_xminor'
        }
        props['xgrid_minor_linewidth'] = {
            'pg_property': 'FloatProperty',
            'label': 'Linewidth',
            'category': 'category_grid_xminor'
        }
        props['xgrid_minor_locator'] = {
            'pg_property': 'IntProperty',
            'label': 'Locator',
            'category': 'category_grid_xminor'
        }
        props['ygrid_major_color'] = {
            #            'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'label': 'Color',
            'category': 'category_grid_ymajor'
        }
        props['ygrid_major_alpha'] = {
            'pg_property': 'FloatProperty',
            'label': 'Alpha',
            'category': 'category_grid_ymajor'
        }
        props['ygrid_major_linestyle'] = {
            'pg_property': 'StringProperty',
            'label': 'Linestyle',
            'category': 'category_grid_ymajor'
        }
        props['ygrid_major_linewidth'] = {
            'pg_property': 'FloatProperty',
            'label': 'Linewidth',
            'category': 'category_grid_ymajor'
        }
        props['ygrid_major_locator'] = {
            'pg_property': 'IntProperty',
            'label': 'Locator',
            'category': 'category_grid_ymajor'
        }
        props['ygrid_minor_color'] = {
            #            'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'label': 'Color',
            'category': 'category_grid_yminor'
        }
        props['ygrid_minor_alpha'] = {
            'pg_property': 'FloatProperty',
            'label': 'Alpha',
            'category': 'category_grid_yminor'
        }
        props['ygrid_minor_linestyle'] = {
            'pg_property': 'StringProperty',
            'label': 'Linestyle',
            'category': 'category_grid_yminor'
        }
        props['ygrid_minor_linewidth'] = {
            'pg_property': 'FloatProperty',
            'label': 'Linewidth',
            'category': 'category_grid_yminor'
        }
        props['ygrid_minor_locator'] = {
            'pg_property': 'IntProperty',
            'label': 'Locator',
            'category': 'category_grid_yminor'
        }

        ### category_grid
        props['axes_spines_right'] = {
            'pg_property': 'BoolProperty',
            'label': 'Right',
            'category': 'category_spines'
        }
        props['axes_spines_left'] = {
            'pg_property': 'BoolProperty',
            'label': 'Left',
            'category': 'category_spines'
        }
        props['axes_spines_bottom'] = {
            'pg_property': 'BoolProperty',
            'label': 'Bottom',
            'category': 'category_spines'
        }
        props['axes_spines_top'] = {
            'pg_property': 'BoolProperty',
            'label': 'Top',
            'category': 'category_spines'
        }

        props['axes_spines_left_position'] = {
            'pg_property': 'StringProperty',
            'label': 'Left',
            'category': 'category_spines_position'
        }
        props['axes_spines_right_position'] = {
            'pg_property': 'StringProperty',
            'label': 'Right',
            'category': 'category_spines_position'
        }
        props['axes_spines_bottom_position'] = {
            'pg_property': 'StringProperty',
            'label': 'Bottom',
            'category': 'category_spines_position'
        }
        props['axes_spines_top_position'] = {
            'pg_property': 'StringProperty',
            'label': 'Top',
            'category': 'category_spines_position'
        }

        ### category_axis
        props['xaxis_visibility'] = {
            'pg_property': 'BoolProperty',
            'label': 'X axis',
            'category': 'category_axis'
        }
        props['yaxis_visibility'] = {
            'pg_property': 'BoolProperty',
            'label': 'Y axis',
            'category': 'category_axis'
        }

        ### category_tick
        props['xtick_labelbottom'] = {
            'pg_property': 'BoolProperty',
            'label': 'Label bottom',
            'category': 'category_tick'
        }
        props['xtick_labeltop'] = {
            'pg_property': 'BoolProperty',
            'label': 'Label top',
            'category': 'category_tick'
        }
        props['ytick_labelleft'] = {
            'pg_property': 'BoolProperty',
            'label': 'Label left',
            'category': 'category_tick'
        }
        props['ytick_labelright'] = {
            'pg_property': 'BoolProperty',
            'label': 'Label right',
            'category': 'category_tick'
        }

        # Tick visibility (detailed)         
        props['xtick_major_bottom'] = {
            'pg_property': 'BoolProperty',
            'label': 'X major bottom',
            'category': 'category_tick'
        }
        props['xtick_major_top'] = {
            'pg_property': 'BoolProperty',
            'label': 'X major top',
            'category': 'category_tick'
        }
        props['xtick_minor_bottom'] = {
            'pg_property': 'BoolProperty',
            'label': 'X minor bottom',
            'category': 'category_tick'
        }
        props['xtick_minor_top'] = {
            'pg_property': 'BoolProperty',
            'label': 'X minor top',
            'category': 'category_tick'
        }

        props['ytick_major_left'] = {
            'pg_property': 'BoolProperty',
            'label': 'Y major left',
            'category': 'category_tick'
        }
        props['ytick_major_right'] = {
            'pg_property': 'BoolProperty',
            'label': 'Y major right',
            'category': 'category_tick'
        }
        props['ytick_minor_left'] = {
            'pg_property': 'BoolProperty',
            'label': 'Y minor left',
            'category': 'category_tick'
        }
        props['ytick_minor_right'] = {
            'pg_property': 'BoolProperty',
            'label': 'Y minor right',
            'category': 'category_tick'
        }

        # Tick visibility   
        props['xtick_minor_visible'] = {
            'pg_property': 'BoolProperty',
            'label': 'X minor visible',
            'category': 'category_tick'
        }
        props['ytick_minor_visible'] = {
            'pg_property': 'BoolProperty',
            'label': 'Y minor visible',
            'category': 'category_tick'
        }

        # Tick visibility         
        props['xtick_bottom'] = {
            'pg_property': 'BoolProperty',
            'label': 'X bottom visible',
            'category': 'category_tick'
        }
        props['xtick_top'] = {
            'pg_property': 'BoolProperty',
            'label': 'X top visible',
            'category': 'category_tick'
        }
        props['ytick_left'] = {
            'pg_property': 'BoolProperty',
            'label': 'Y left visible',
            'category': 'category_tick'
        }
        props['ytick_right'] = {
            'pg_property': 'BoolProperty',
            'label': 'Y right visible',
            'category': 'category_tick'
        }

        # Tick direction    
        props['xtick_direction'] = {
            'pg_property': 'EnumProperty',
            'label': 'X direction',
            'options_labels': ['In', 'Out', 'In/Out'],
            'options_values': ['in', 'out', 'inout'],
            'category': 'category_tick'
        }
        props['ytick_direction'] = {
            'pg_property': 'EnumProperty',
            'label': 'Y direction',
            'options_labels': ['In', 'Out', 'In/Out'],
            'options_values': ['in', 'out', 'inout'],
            'category': 'category_tick'
        }

        # Tick length (size)
        props['xtick_major_size'] = {
            'label': 'X major tick size',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }

        props['xtick_minor_size'] = {
            'label': 'X minor tick size',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }
        props['ytick_major_size'] = {
            'label': 'Y major tick size',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }
        props['ytick_minor_size'] = {
            'label': 'Y minor tick size',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }

        # Tick width 
        props['xtick_major_width'] = {
            'label': 'X major tick width',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }

        props['xtick_minor_width'] = {
            'label': 'X minor tick width',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }
        props['ytick_major_width'] = {
            'label': 'Y major tick width',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }
        props['ytick_minor_width'] = {
            'label': 'Y minor tick width',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }

        # Tick pad   
        props['xtick_major_pad'] = {
            'label': 'X major tick pad',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }

        props['xtick_minor_pad'] = {
            'label': 'X minor tick pad',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }
        props['ytick_major_pad'] = {
            'label': 'Y major tick pad',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }
        props['ytick_minor_pad'] = {
            'label': 'Y minor tick pad',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }

        # Tick label size     
        props['xtick_labelsize'] = {
            'label': 'X tick label size',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }

        props['ytick_labelsize'] = {
            'label': 'Y tick label size',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }

        # Tick color        
        props['xtick_color'] = {
            'label': 'X tick color',
            #            'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'category': 'category_tick'
        }
        props['ytick_color'] = {
            'label': 'Y tick color',
            #            'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'category': 'category_tick'
        }

        # Tick label color  
        props['xtick_labelcolor'] = {
            'label': 'X tick label color',
            #            'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'category': 'category_tick'
        }

        props['ytick_labelcolor'] = {
            'label': 'Y tick label color',
            #            'pg_property': 'MPLColorsProperty',
            'pg_property': 'ColourProperty',
            'category': 'category_tick'
        }

        # Tick label rotation 
        props['ytick_labelrotation'] = {
            'label': 'X tick label rotation',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }

        props['ytick_labelsize'] = {
            'label': 'Y tick label rotation',
            'pg_property': 'FloatProperty',
            'category': 'category_tick'
        }

        return props


######    


class CanvasPlotter(CanvasBaseView):
    tid = 'canvas_plotter'

    def __init__(self, controller_uid):
        super().__init__(controller_uid)

    def PostInit(self):
        super().PostInit()
        #
        drop_target = DropTarget(self.is_valid_object,
                                 self.append_object
                                 )
        self.SetDropTarget(drop_target)
        #

    def is_valid_object(self, obj_uid):
        return True

        # Method for Drag and Drop....

    def append_object(self, obj_uid):
        print('\nCanvasPlotter.append_object:', obj_uid)
