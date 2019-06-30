from collections import OrderedDict

from classes.om import ObjectManager
from classes.ui import UIManager
from ui.mvc_classes.representation import RepresentationController
from ui.mvc_classes.representation import RepresentationView
from app.app_utils import MPL_COLORMAPS
  
  
class DensityRepresentationController(RepresentationController):
    tid = 'density_representation_controller'

    _ATTRIBUTES = OrderedDict()
    
    _ATTRIBUTES['type'] = {
            'default_value': 'density', #'wiggle', #'density', 
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Plot type',
            'options_labels': ['Density', 'Wiggle', 'Both'],  
            'options_values': ['density', 'wiggle', 'both']
    }    
    _ATTRIBUTES['colormap'] = {
            'default_value': 'Spectral_r', #'gray',
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Colormap',
            'options_labels': MPL_COLORMAPS
    }      
    _ATTRIBUTES['interpolation'] = {
            'default_value': 'bicubic', #'none', #'bilinear',
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Colormap interpolation',
            'options_labels': ['none', 'nearest', 'bilinear', 'bicubic',
                      'spline16', 'spline36', 'hanning', 'hamming',
                      'hermite', 'kaiser', 'quadric', 'catrom',
                      'gaussian', 'bessel', 'mitchell', 'sinc',
                      'lanczos'
            ]  
    }       
    _ATTRIBUTES['min_density'] = {
            'default_value': None,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Colormap min value'     
    }
    _ATTRIBUTES['max_density'] = {
            'default_value': None,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Colormap max value' 
    }
    _ATTRIBUTES['density_alpha'] = {
            'default_value': 1.0,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Colormap alpha'
    }
    _ATTRIBUTES['linewidth'] = {
            'default_value': 1, 
            'type': int,
            'pg_property': 'EnumProperty',
            'label': 'Wiggle line width',
            'options_labels': ['0', '1', '2', '3'],
            'options_values': [0, 1, 2, 3]
    }   
    _ATTRIBUTES['linecolor'] = {
            'default_value': 'Black',
            'type': str,
            'pg_property': 'MPLColorsProperty',
            'label': 'Wiggle line color'
    }    
    _ATTRIBUTES['min_wiggle'] = {
            'default_value': None,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Wiggle min value'
    }
    _ATTRIBUTES['max_wiggle'] = {
            'default_value': None,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Wiggle max value'
    }  
    _ATTRIBUTES['wiggle_alpha'] = {
            'default_value': 1.0,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Wiggle alpha'
    }    
    _ATTRIBUTES['fill'] = {
            'default_value': None,
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Wiggle fill type',
            'options_labels': ['None', 'Left', 'Right', 'Both'],  
            'options_values': [None, 'left', 'right', 'both']
    }      
    _ATTRIBUTES['fill_color_left'] = {
            'default_value': 'Red', 
            'type': str,
            'pg_property': 'MPLColorsProperty',
            'label': 'Wiggle left fill color'
#            'options_labels': list(MPL_COLORS.keys())
    }       
    _ATTRIBUTES['fill_color_right'] = {
            'default_value': 'Blue', 
            'type': str,
            'pg_property': 'MPLColorsProperty',
            'label': 'Wiggle right fill color'
#            'options_labels': list(MPL_COLORS.keys())
    }  
    
    def __init__(self, **state):
        super().__init__(**state)
        
    def PostInit(self):    
        self.subscribe(self.on_change_colormap, 'change.colormap')   
        self.subscribe(self.on_change_density_alpha, 
                                                       'change.density_alpha'
        )
        self.subscribe(self.on_change_wiggle_alpha, 
                                                       'change.wiggle_alpha'
        )

    def on_change_density_alpha(self, new_value, old_value):    
        if new_value >= 0.0 and new_value <= 1.0:
            self.view.set_density_alpha(new_value)
        else:
            self.set_value_from_event('density_alpha', old_value)
            
    def on_change_wiggle_alpha(self, new_value, old_value):      
        if new_value >= 0.0 and new_value <= 1.0:
            self.view.set_wiggle_alpha(new_value)
        else:
            self.set_value_from_event('wiggle_alpha', old_value)   
    
    def on_change_colormap(self, new_value, old_value):
        if new_value not in MPL_COLORMAPS:
            msg = 'Invalid colormap. Valid values are: {}'.format(MPL_COLORMAPS)
            print (msg)
            self.set_value_from_event('colormap', old_value)
        else:    
            self.view.set_colormap(new_value)     
            

class DensityRepresentationView(RepresentationView):
    tid = 'density_representation_view'

    def __init__(self, controller_uid):
        super().__init__(controller_uid)   

            
    def PostInit(self):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        #
        # TODO: Ver um melhor lugar para redefinir a colormap
        tid, _ = controller.get_data_object_uid()
        if tid == 'gather' or tid == 'seismic':
            controller.colormap = 'gray_r'
        #          
        controller.subscribe(self._draw, 'change.type')    
        controller.subscribe(self.set_interpolation, 'change.interpolation')
        controller.subscribe(self._draw, 'change.min_density')   
        controller.subscribe(self._draw, 'change.max_density')  
        controller.subscribe(self.set_line_width, 'change.linewidth')   
        controller.subscribe(self.set_line_color, 'change.linecolor')   
        controller.subscribe(self.fill_between, 'change.fill') 
        controller.subscribe(self.fill_color_left, 'change.fill_color_left')
        controller.subscribe(self.fill_color_right, 'change.fill_color_right')
        controller.subscribe(self._draw, 'change.min_wiggle')   
        controller.subscribe(self._draw, 'change.max_wiggle')
        #
        #self.draw()
        
            
    def _draw(self, new_value, old_value):
        # Bypass function
        self.draw()  


    def set_colormap(self, colormap):
        if self._mplot_objects['density']:
            self._mplot_objects['density'].set_cmap(colormap)
            self.label.set_colormap(colormap)
        self.draw_canvas()       

    def set_interpolation(self, new_value, old_value):
        if self._mplot_objects['density']:
            self._mplot_objects['density'].set_interpolation(new_value)
        self.draw_canvas()                

    def set_density_alpha(self, alpha):
        if self._mplot_objects['density']:
            self._mplot_objects['density'].set_alpha(alpha)
        self.draw_canvas()

    def set_wiggle_alpha(self, alpha):
        if len(self._mplot_objects['wiggle']) == 0:
            return
        for idx in range(0, len(self._mplot_objects['wiggle'])):    
            mpl_obj = self._mplot_objects['wiggle'][idx]
            if mpl_obj is not None:
                mpl_obj.set_alpha(alpha)
        self.draw_canvas()

    def set_line_color(self, new_value, old_value):
        for idx_line in range(0, len(self._mplot_objects['wiggle']), 3):
            line = self._mplot_objects['wiggle'][idx_line]
            line.set_color(new_value)
        self.draw_canvas()   

    def set_line_width(self, new_value, old_value):
        for idx_line in range(0, len(self._mplot_objects['wiggle']), 3):
            line = self._mplot_objects['wiggle'][idx_line]
            line.set_linewidth(new_value)
        self.draw_canvas()    

    def fill_color_left(self, new_value, old_value):
        for idx_fill_obj in range(1, len(self._mplot_objects['wiggle']), 3):
            fill_mpl_obj = self._mplot_objects['wiggle'][idx_fill_obj]
            if fill_mpl_obj:
                fill_mpl_obj.set_color(new_value)
        self.draw_canvas()        

    def fill_color_right(self, new_value, old_value):
        for idx_fill_obj in range(2, len(self._mplot_objects['wiggle']), 3):
            fill_mpl_obj = self._mplot_objects['wiggle'][idx_fill_obj]
            if fill_mpl_obj:
                fill_mpl_obj.set_color(new_value)
        self.draw_canvas()   


    def get_data_info(self, event):
        """
        Retorna a string com informações do dado exibido em tela, 
        de acordo com a posicao do mouse no momento.
        """
        image = self._mplot_objects.get('density')
        if image:
            value = image.get_cursor_data(event)
            #
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            dm = controller.get_data_mask()
            x_di_uid, x_index_data = dm.get_index_for_dimension(-2)
            y_di_uid, y_index_data = dm.get_index_for_dimension(-1)
            canvas = self.get_canvas()
            xvalue = canvas.inverse_transform(event.xdata, 
                                              x_index_data[0], 
                                              x_index_data[-1]
            )  
            #
            OM = ObjectManager()
            x_data_index = OM.get(x_di_uid)
            y_data_index = OM.get(y_di_uid)
            #
            if event.ydata < y_index_data[0] or event.ydata > y_index_data[-1]:
                return None
            #
            msg = x_data_index.name + ': {:0.2f}'.format(xvalue) + ', ' \
                        +  y_data_index.name + ': {:0.2f}'.format(event.ydata)
            msg += ', Value: {:0.2f}'.format(value)  
            return '[' + msg +  ']'
        else:
            msg = ''
            return '[' + msg +  ']'
#            raise Exception('Tratar get_data_info para Wiggle.')

    
    def draw(self):
        #
        print('\n\nEntrou Density.draw():')
        #
        self.clear()    
        self._mplot_objects['density'] = None
        self._mplot_objects['wiggle'] = []
        #
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        dm = controller.get_data_mask()
        #
        print(controller.type)
        #
        data = dm.get_data(dimensions_desired=2)
        x_di_uid, x_index_data = dm.get_index_for_dimension(-2)
        y_di_uid, y_index_data = dm.get_index_for_dimension(-1)
        #
        OM = ObjectManager()
        xdata_index = OM.get(x_di_uid)
        ydata_index = OM.get(y_di_uid)
        #   
        canvas = self.get_canvas()
        toc_uid = UIM._getparentuid(self._controller_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)
        #
        xlim_min, xlim_max = canvas.get_xlim('plot_axes')
        #
        if controller.type == 'density' or controller.type == 'both':
            # (left, right, bottom, top)
            extent = (xlim_min, xlim_max, 
                      np.nanmax(y_index_data), np.nanmin(y_index_data)
            )   
            try:
                image = track_controller.append_artist('AxesImage',
                                        cmap=controller.colormap,
                                        interpolation=controller.interpolation,
                                        extent=extent
                )
                image.set_data(data.T)
                image.set_label(self._controller_uid)            
                if image.get_clip_path() is None:
                    # image does not already have clipping set, 
                    # clip to axes patch
                    image.set_clip_path(image.axes.patch)       
                if controller.min_density is None:
                    controller.set_value_from_event('min_density', 
                                                    np.nanmin(data)
                    )
                if controller.max_density is None:    
                    controller.set_value_from_event('max_density', 
                                                    np.nanmax(data)
                    )        
                #        
                image.set_clim(controller.min_density, controller.max_density)
                image.set_alpha(controller.density_alpha)
                self._mplot_objects['density'] = image
            except Exception as e:
                print('ERRO density.draw:', e)
                raise           
        else:
            self._mplot_objects['density'] = None
        #
        if controller.type == 'wiggle' or controller.type == 'both':    
            try:

                self._lines_center = []
                vec = np.arange(0.5, len(x_index_data)) 
                x_lines_position = canvas.transform(vec, 0.0, len(x_index_data))           
                if len(x_lines_position) > 1:
                    increment = (x_lines_position[0] + x_lines_position[1])/2.0 
                elif len(x_lines_position) == 1:
                    increment = 0.5
                else:
                    msg = 'Error. x_lines_position cannot have lenght 0. Shape: {}'.format(data.shape)
                    raise Exception(msg)
                
                
                if controller.min_wiggle == None:
                    controller.set_value_from_event('min_wiggle', 
                                    (np.amax(np.absolute(data))) * -1
                    )  
                if controller.max_wiggle == None:
                    controller.set_value_from_event('max_wiggle', 
                                            np.amax(np.absolute(data))
                    )     
                data_ = np.where(data<0, data/np.absolute(controller.min_wiggle), data)
                data_ = np.where(data_>0, data_/controller.max_wiggle, data_)
                #print('\n\ndata_:', data_)
                
                
                for idx, pos_x in enumerate(x_lines_position):
                    
                    self._lines_center.append(pos_x) 
                    xdata = data_[idx]
                    
                    #print()
                    print(idx, pos_x)
                    
                    #  def _transform_xdata_to_wiggledata(self, values, axes_left, axes_right):
                    
                    xdata = self._transform_xdata_to_wiggledata(xdata, 
                                                                pos_x, 
                                                                increment
                    )
                    line = track_controller.append_artist('Line2D', 
                                                xdata, y_index_data,
                                                linewidth=controller.linewidth,
                                                color=controller.linecolor   
                    )
                    self._mplot_objects['wiggle'].append(line)   
                    self._mplot_objects['wiggle'].append(None) # left fill
                    self._mplot_objects['wiggle'].append(None) # right fill
                             
            except Exception as e:
                print('ERRO wiggle.draw:', e)
                raise
                         
        
        # Deals with WellPlot label
        if self.label:
            try:
                self.label.set_plot_type(controller.type)
                self.label.set_title(dm.get_data_name())
                self.label.set_subtitle(dm.get_data_type())
                #
                if controller.type == 'density' or controller.type == 'both':
                    self.label.set_colormap(controller.colormap)
                    self.label.set_colormap_lim((controller.min_density, 
                                                 controller.max_density)
                    )
                    #
                    self.label.set_ruler(x_index_data[0], x_index_data[-1])
                    self.label.set_ruler_title(xdata_index.name)
                    self.label.set_ruler_subtitle(xdata_index.unit)                        
                    #    
                if controller.type == 'wiggle' or controller.type == 'both': 
                    self.label.set_offset(x_index_data, 
                                         x_lines_position, 
                                         xlim=(xlim_min, xlim_max)
                                         
                    )
                    self.label.set_offset_title(xdata_index.name)
                    self.label.set_offset_subtitle(xdata_index.unit)
                #    
            except Exception as e:
                msg = 'Deu RUIM: ' + str(e)
                print(msg)
                raise
        #
        
        
        print('self.draw_canvas()')    
        self.draw_canvas()
        if controller.type == 'wiggle' or controller.type == 'both':
            self.fill_between(controller.fill, None)
        print('FIM draw()\n\n')
        
        
    
    # Find a better name
    def _transform_xdata_to_wiggledata(self, values, center_pos, inc):
        return inc * values + center_pos    


    def _remove_fillings(self, type_='both'):
        for idx in range(0, len(self._mplot_objects['wiggle']), 3):
            left_fill = self._mplot_objects['wiggle'][idx+1]
            right_fill = self._mplot_objects['wiggle'][idx+2]         
            if left_fill is not None and type_ in ['left', 'both']:
                left_fill.remove()
                self._mplot_objects['wiggle'][idx+1] = None         
            if right_fill is not None and type_ in ['right', 'both']:
                right_fill.remove()
                self._mplot_objects['wiggle'][idx+2] = None
        self.draw_canvas()
    
    
    def fill_between(self, new_value, old_value):
        fill_type = new_value
        self._remove_fillings()
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        #
        for idx_line in range(0, len(self._mplot_objects['wiggle']), 3):
            line = self._mplot_objects['wiggle'][idx_line]
            left_fill = self._mplot_objects['wiggle'][idx_line+1]
            right_fill = self._mplot_objects['wiggle'][idx_line+2]
            axis_center = self._lines_center[idx_line/3]
            left_fill = None
            if fill_type == 'left' or fill_type == 'both':
                left_fill = self._my_fill(line.axes,
                                                line.get_ydata(),                                     
                                                line.get_xdata(), 
                                                axis_center,
                                                where=line.get_xdata() <= axis_center,
                                                facecolor=controller.fill_color_left,
                                                interpolate=True
                )
                
            right_fill = None    
            if fill_type == 'right' or fill_type == 'both':
                right_fill = self._my_fill(line.axes,
                                                line.get_ydata(),                                      
                                                line.get_xdata(), 
                                                axis_center,
                                                where=line.get_xdata() >= axis_center,
                                                facecolor=controller.fill_color_right,
                                                interpolate=True
                )
            self._mplot_objects['wiggle'][idx_line+1] = left_fill
            self._mplot_objects['wiggle'][idx_line+2] = right_fill
        self.draw_canvas()    
    
    
    def _my_fill(self, axes, y, x1, x2=0, where=None, interpolate=False, step=None, **kwargs):
        
        if not matplotlib.rcParams['_internal.classic_mode']:
            color_aliases = mcoll._color_aliases
            kwargs = cbook.normalize_kwargs(kwargs, color_aliases)

            if not any(c in kwargs for c in ('color', 'facecolors')):
                fc = axes._get_patches_for_fill.get_next_color()
                kwargs['facecolors'] = fc
        
        # Handle united data, such as dates
        axes._process_unit_info(ydata=y, xdata=x1, kwargs=kwargs)
        axes._process_unit_info(xdata=x2)

        # Convert the arrays so we can work with them
        y = ma.masked_invalid(axes.convert_yunits(y))
        x1 = ma.masked_invalid(axes.convert_xunits(x1))
        x2 = ma.masked_invalid(axes.convert_xunits(x2))

        if x1.ndim == 0:
            x1 = np.ones_like(y) * x1
        if x2.ndim == 0:
            x2 = np.ones_like(y) * x2

        if where is None:
            where = np.ones(len(y), np.bool)
        else:
            where = np.asarray(where, np.bool)

        if not (y.shape == x1.shape == x2.shape == where.shape):
            raise ValueError("Argument dimensions are incompatible")

        mask = reduce(ma.mask_or, [ma.getmask(a) for a in (y, x1, x2)])
        if mask is not ma.nomask:
            where &= ~mask

        polys = []
        
        for ind0, ind1 in mlab.contiguous_regions(where):
            yslice = y[ind0:ind1]
            x1slice = x1[ind0:ind1]
            x2slice = x2[ind0:ind1]
            if step is not None:
                step_func = cbook.STEP_LOOKUP_MAP[step]
                yslice, x1slice, x2slice = step_func(yslice, x1slice, x2slice)

            if not len(yslice):
                continue

            N = len(yslice)
            Y = np.zeros((2 * N + 2, 2), np.float)
           
            if interpolate:
                def get_interp_point(ind):
                    im1 = max(ind - 1, 0)
                    y_values = y[im1:ind + 1]
                    diff_values = x1[im1:ind + 1] - x2[im1:ind + 1]
                    x1_values = x1[im1:ind + 1]

                    if len(diff_values) == 2:
                        if np.ma.is_masked(diff_values[1]):
                            return y[im1], x1[im1]
                        elif np.ma.is_masked(diff_values[0]):
                            return y[ind], x1[ind]

                    diff_order = diff_values.argsort()
                    diff_root_y = np.interp(0, diff_values[diff_order], y_values[diff_order])
                    diff_root_x = np.interp(diff_root_y, y_values, x1_values)
                    return diff_root_x, diff_root_y

                start = get_interp_point(ind0)
                end = get_interp_point(ind1)
            else:
                # the purpose of the next two lines is for when x2 is a
                # scalar like 0 and we want the fill to go all the way
                # down to 0 even if none of the x1 sample points do
                start = x2slice[0], yslice[0] #Y[0] = x2slice[0], yslice[0]
                end = x2slice[-1], yslice[-1] #Y[N + 1] = x2slice[-1], yslice[-1]

            Y[0] = start
            Y[N + 1] = end

            Y[1:N + 1, 0] = x1slice
            Y[1:N + 1, 1] = yslice
            Y[N + 2:, 0] = x2slice[::-1]
            Y[N + 2:, 1] = yslice[::-1]

            polys.append(Y)

        collection = mcoll.PolyCollection(polys, **kwargs)

        # now update the datalim and autoscale
        X1Y = np.array([x1[where], y[where]]).T
        X2Y = np.array([x2[where], y[where]]).T
        axes.dataLim.update_from_data_xy(X1Y, axes.ignore_existing_data_limits,
                                         updatex=True, updatey=True)
        axes.ignore_existing_data_limits = False
        axes.dataLim.update_from_data_xy(X2Y, axes.ignore_existing_data_limits,
                                         updatex=True, updatey=False)
        axes.add_collection(collection, autolim=False)
        axes.autoscale_view()
        return collection 

