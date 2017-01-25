# -*- coding: utf-8 -*-

import wx
import os

#from OM.Manager import ObjectManager
from UI.uimanager import UIManager
from gripy_controller import GripyController




def handler_teste(event):
    print
    print 'id: ', event.GetId()
    print 'type: ', event.GetEventType()
    print 'object: ', event.GetEventObject().uid
    print 'category: ', event.GetEventCategory()
    #print 'user_data: ', event.GetEventUserData()
    
      
       
       
       
def on_open(event):
    _controller, _root_controller = GripyController.get_event_controllers(event)
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    wildcard = "Arquivo de projeto do GRIPy (*.pgg)|*.pgg"
    try:
        fdlg = wx.FileDialog(_root_controller.view, 'Escolha o arquivo PGG', wildcard=wildcard, style=style)
        if fdlg.ShowModal() == wx.ID_OK:
            file_name = fdlg.GetFilename()
            dir_name = fdlg.GetDirectory()
            fdlg.Destroy()
        else:
            fdlg.Destroy()
            return
        _GC = GripyController(_controller)   
        _GC.load_project(dir_name, file_name)    
    except Exception:
        raise


def on_save(event):
    _controller = GripyController.get_event_controllers(event)[0]
    _GC = GripyController(_controller)   
    if _GC._OM_file:
        _GC._OM.save()
    else:
        on_save_as(event)
    

def on_save_as(event):
    _controller, _root_controller = GripyController.get_event_controllers(event)
    _GC = GripyController(_controller)    
    style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
    wildcard = "Arquivo de projeto do GRIPy (*.pgg)|*.pgg"
    fdlg = wx.FileDialog(_root_controller.view, 'Escolha o arquivo PGG', 
                        _GC.dir_name,_GC.file_name, wildcard=wildcard, style=style)
    if fdlg.ShowModal() == wx.ID_OK:
        _GC.file_name = fdlg.GetFilename()
        _GC.dir_name = fdlg.GetDirectory()
        _GC._OM.save(os.path.join(_GC.dir_name, _GC.file_name))
    fdlg.Destroy()    
    
    
 
def on_new_logplot(event):
    _UIM = UIManager()
    _controller = _UIM.get(event.GetEventObject()._controller_uid)
    _root_controller = _controller.get_root_controller()          
    _UIM.create('logplot_controller', _root_controller.uid)
    
  
            
def on_debugconsole(event):
    from app.gripy_debug_console import DebugConsoleFrame
    _controller, _root_controller = GripyController.get_event_controllers(event)
    consoleUI = DebugConsoleFrame(_root_controller.view)
    consoleUI.Show()    
    
    
    
    @staticmethod
    def on_import_las(event):
        gc = GripyController(event.GetEventObject())
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        wildcard="Arquivos LAS (*.las)|*.las"
        fdlg = wx.FileDialog(gc.get_main_window().view, 'Escolha o arquivo LAS', 
                             wildcard=wildcard, style=style)
        if fdlg.ShowModal() == wx.ID_OK:
            gc.file_name = fdlg.GetFilename()
            gc.dir_name  = fdlg.GetDirectory()
            fdlg.Destroy()
        else:
            fdlg.Destroy()
            return
        las_file = IO.LAS.open(os.path.join(gc.dir_name, gc.file_name), 'r')
        las_file.read()
        hedlg = HeaderEditor.Dialog(gc.get_main_window().view)
        hedlg.set_header(las_file.header)

        if hedlg.ShowModal() == wx.ID_OK:
            las_file.header = hedlg.get_header()
#            print 'header\n', las_file.header
            names = las_file.curvesnames
            units = las_file.curvesunits
            
            ncurves = len(names)

            # Tentativa de solução não lusitana
            
            ParametersManager2.load()
            
            curvetypes = ParametersManager2.getcurvetypes()
            datatypes = ParametersManager2.getdatatypes()
            
            sel_curvetypes = [ParametersManager2.getcurvetypefrommnem(name) for name in names]
            
            sel_datatypes = []
            for name in names:
                datatype = ParametersManager2.getdatatypefrommnem(name)
                print 'DT:', name, '-', datatype
                if not datatype:
                    sel_datatypes.append('Log')
                else:
                    sel_datatypes.append(datatype)

            isdlg = ImportSelector.Dialog(gc.get_main_window().view,
                                          names, units, curvetypes, datatypes)
            
            isdlg.set_curvetypes(sel_curvetypes)
            isdlg.set_datatypes(sel_datatypes)
            
            if isdlg.ShowModal() == wx.ID_OK:
                sel_curvetypes = isdlg.get_curvetypes()
                sel_datatypes = isdlg.get_datatypes()
                data = las_file.data
                well = gc._OM.new('well', name=las_file.wellname, 
                                  LASheader=las_file.header)
                gc._OM.add(well)
                
                depth = None
                
                for i in range(ncurves):
                    #print 'CT:', names[i], '-', sel_curvetypes[i]
                    if sel_curvetypes[i]:
                        ParametersManager2.voteforcurvetype(names[i], sel_curvetypes[i])

                    if sel_datatypes[i]:
                        ParametersManager2.votefordatatype(names[i], sel_datatypes[i])
                    
                    if sel_datatypes[i] == 'Depth':
                        depth = gc._OM.new('index_curve', data[i], name=names[i], 
                                           unit=units[i].lower(), curvetype=sel_curvetypes[i])
                        well.index.append(depth)
                        gc._OM.add(depth, well.uid)
                    
                    elif sel_datatypes[i] == 'Log':
                        log = gc._OM.new('log', data[i], name=names[i], 
                                    unit=units[i].lower(), curvetype=sel_curvetypes[i],
                                    index_uid=depth.uid
                        )
                        gc._OM.add(log, well.uid)

                    elif sel_datatypes[i] == 'Partition':
                        booldata, codes = DT.DataTypes.Partition.getfromlog(data[i])
                        partition = gc._OM.new('partition', name=names[i], 
                                               curvetype=sel_curvetypes[i],
                                               index_uid=depth.uid
                        )
                        gc._OM.add(partition, well.uid)
                        for j in range(len(codes)):
                            part = gc._OM.new('part', booldata[j], 
                                code=int(codes[j]), curvetype=sel_curvetypes[i])
                            gc._OM.add(part, partition.uid)
                    else:
                        print "Not importing {} as no datatype matches '{}'".format(names[i], sel_datatypes[i])
                     
            ParametersManager2.dump()
            isdlg.Destroy()
        hedlg.Destroy()



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


    def on_import_lis(self, event):
        lis_import_frame = lisloader.LISImportFrame(self)
        lis_import_frame.Show()
 

    def on_import_vel_segy(self, event):
        gc = GripyController(event.GetEventObject())
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        wildcard="Arquivos SEG-Y (*.sgy)|*.sgy"
        fdlg = wx.FileDialog(gc.get_main_window().view, 'Escolha o arquivo SEG-Y', 
                             wildcard=wildcard, style=style)
        if fdlg.ShowModal() == wx.ID_OK:
            file_name = fdlg.GetFilename()
            dir_name  = fdlg.GetDirectory()
            fdlg.Destroy()
        else:
            fdlg.Destroy()
            return
        
        segy_file = IO.SEGY.SEGYFile(os.path.join(dir_name, file_name))
        segy_file.read()
        name = segy_file.filename.rsplit('\\')[-1]
        name = name.split('.')[0]
        


            
        velocity = self._OM.new('velocity', segy_file.data, name=name, 
                               unit='ms', domain='time', 
                               sample_rate=segy_file.sample_rate*1000, datum=0,
                               samples=segy_file.number_of_samples,
                               #stacked=stacked,
                               traces=int(segy_file.data.shape[0])
        )
                 
        self._OM.add(velocity)                   
       


    def on_import_seis_segy(self, event):
        gc = GripyController(event.GetEventObject())
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        wildcard="Arquivos SEG-Y (*.sgy)|*.sgy"
        fdlg = wx.FileDialog(gc.get_main_window().view, 'Escolha o arquivo SEG-Y', 
                             wildcard=wildcard, style=style)
        if fdlg.ShowModal() == wx.ID_OK:
            file_name = fdlg.GetFilename()
            dir_name  = fdlg.GetDirectory()
            fdlg.Destroy()
        else:
            fdlg.Destroy()
            return
        
        segy_file = IO.SEGY.SEGYFile(os.path.join(dir_name, file_name))
        segy_file.read()
        name = segy_file.filename.rsplit('\\')[-1]
        name = name.split('.')[0]
        

            
        stacked = False
    
        if len(segy_file.data) > 1:    
            if (IO.SEGY.get_value(segy_file.header[0], 37, 4)  == 
                                IO.SEGY.get_value(segy_file.header[1], 37, 4)):   
                stacked = True
        else:
            stacked = True
              
 
            
        seismic = self._OM.new('seismic', segy_file.data, name=name, 
                               unit='ms', domain='time', 
                               sample_rate=segy_file.sample_rate*1000, datum=0,
                               samples=segy_file.number_of_samples,
                               stacked=stacked,
                               traces=int(segy_file.data.shape[0])
        )
                 
        self._OM.add(seismic)    
        


    def on_test_partition(self, event):
        well = self._OM.new('well', name='teste_particao') 
        self._OM.add(well)
        data = np.arange(0, 550, 50)
        depth = self._OM.new('depth', data, name='depth', unit='m', curvetype='Depth')
        self._OM.add(depth, well.uid)
        
        #data = np.array([12, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14])
        #booldata, codes = DT.DataTypes.Partition.getfromlog(data)
        partition = self._OM.new('partition', name='particao', curvetype='partition')
        self._OM.add(partition, well.uid)
        
        b1 = np.array([True, True, True, True, False, False, False, False, False, False, False])
        p1 = self._OM.new('part', b1, code=12, color=(255, 0, 0), curvetype='part')
        self._OM.add(p1, partition.uid)

        b2 = np.array([False, False, False, False, True, True, True, True, False, False, False])
        p2 = self._OM.new('part', b2, code=13, color=(0, 255, 0),curvetype='part')
        self._OM.add(p2, partition.uid)

        b3 = np.array([True, True, False, False, False, False, False, False, True, True, True])
        p3 = self._OM.new('part', b3, code=14, color=(0, 0, 255), curvetype='part')
        self._OM.add(p3, partition.uid)
        
   

        
    def on_load_wilson(self, event):
        
        def in1d_with_tolerance(A,B,tol=1e-05):
            return (np.abs(A[:,None] - B) < tol).any(1)
        
        # Time in milliseconds
        def ricker(fp, peak=0.0, x_values=None, y_values=None):
            t = np.arange(-1000.0, 1001.0, 1)        
            factor = (np.pi * fp * t) ** 2
            y = (1 - 2. * factor) * np.exp(-factor)
            t = t + peak
            if x_values is None:        
                return t, y
            else:
                vec = in1d_with_tolerance(t, x_values)
                y = y[vec]
                if y_values is None:
                    return x_values, y
                else:
                    return x_values, y + y_values
        
        def time_array(start, end, dt):
            return np.arange(start, end+dt, dt)
        
        r_values = [
            (40, 100),
            (10, 300),
            (40, 300),
            (30, 500),
            (30, 520),
            (20, 800),
            (30, 800),
            (20, 820),
            (30, 820)
        ]

        dt = 4
        t = time_array(0, 1000.0, dt)

        pos_stack_data = np.zeros(len(t)) 
        pre_stack_data = []
        
        for idx, (f, peak) in enumerate(r_values):   
            pre_stack = np.zeros(len(t))
            pre_stack = ricker(f, peak, t, pre_stack)[1]
            pos_stack_data += pre_stack
            pre_stack_data.append(pre_stack)
        pre_stack_data = np.array(pre_stack_data)    
    


        seismic = self._OM.new('seismic', pre_stack_data, name='wilson_synth_pre', 
                               unit='ms', domain='time', 
                               sample_rate=dt, datum=0,
                               samples=len(t),
                               stacked=False,
                               traces=int(pre_stack_data.shape[0]))
        self._OM.add(seismic) 


        pos_stack_data = pos_stack_data[np.newaxis,:]
        
        seismic = self._OM.new('seismic', pos_stack_data, name='wilson_synth_pos', 
                               unit='ms', domain='time', 
                               sample_rate=dt, datum=0,
                               samples=len(t),
                               stacked=True,
                               traces=int(pos_stack_data.shape[0]))
        self._OM.add(seismic) 
        



    
    def on_load_avo_inv_wells(self, event):    
        
        def lerAscii(filename):
            f = file(filename, 'r')
            d = np.array([float(x) for x in f.readlines()])
            f.close  
            return d
            
        poco_densidade  = str("C:\Users\Adriano\Documents\GitHub\AVO_INVTRACE_NEW\data\poco_0210_densidade.dat")
        poco_vp         = str("C:\Users\Adriano\Documents\GitHub\AVO_INVTRACE_NEW\data\poco_0210_vp.dat")
        poco_vs         = str("C:\Users\Adriano\Documents\GitHub\AVO_INVTRACE_NEW\data\poco_0210_vs.dat")
        
        # Carregando dados ascii (poços)
        p_rho = lerAscii(poco_densidade)
        p_vp  = lerAscii(poco_vp)
        p_vs  = lerAscii(poco_vs)    
            
        p_vp = p_vp * 3.28084    
        p_vs = p_vs * 3.28084
       #print p_rho
        
        well = self._OM.new('well', name='poco_0210')
        self._OM.add(well)
        d = np.arange(2514, 2946, 4)
        depth = self._OM.new('index_curve', d, name='DEPTH', unit='m', curvetype='Depth')
        self._OM.add(depth, well.uid)        

        log_rho = self._OM.new('log', p_rho, name='Rho', index_uid=depth.uid,
                               unit='g/cm3', curvetype='Density'
        )
        self._OM.add(log_rho, well.uid)
        
        log_vp = self._OM.new('log', p_vp, name='Vp', index_uid=depth.uid,
                              unit='ft/sec', curvetype='Velocity'
        )
        self._OM.add(log_vp, well.uid)    
        
        log_vs = self._OM.new('log', p_vs, name='Vs', index_uid=depth.uid,
                              unit='ft/sec', curvetype='Velocity'
        )
        self._OM.add(log_vs, well.uid)         



    def on_wavelet_analysis(self, event):                
        gc = GripyController(event.GetEventObject())
        mw_ctrl = gc.get_main_window()

        dlg = dialog.Dialog(mw_ctrl.view, 
            [
                (dialog.Dialog.seismic_selector, 'Seismic:', 'seismic_uid'),
                (dialog.Dialog.text_ctrl, 'Scalogram name:', 'new_obj_name')
            ], 'Wavelet Analysis - Select Source:'
        )

        if dlg.ShowModal() == wx.ID_OK:
            results = dlg.get_results()
        else:
            return
            
        seismic_uid = results.get('seismic_uid')
        scalogram_name = results.get('new_obj_name')
        
        seis = self._OM.get(seismic_uid)
 
        start = seis.attributes.get('datum')
        step = seis.attributes.get('sample_rate')
        samples = seis.attributes.get('samples')
        stop = start + step * samples
        time = np.arange(start, stop, step)
        data = []
        for j in range(seis.data.shape[0]):
            wa = wavelets.WaveletAnalysis(seis.data[j], time=time, dj=0.125)
            power = wa.wavelet_power   
            data.append(power)     
        data = np.array(data)

        scalogram = self._OM.new('scalogram', data, name=scalogram_name, 
                               unit='ms', domain=seis.attributes.get('domain', 'time'), 
                               sample_rate=step, datum=start,
                               samples=samples, traces=int(data.shape[0]), 
                               scales=int(data.shape[1]), type='Amp Power'
        )
        self._OM.add(scalogram)
        
        



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


    def on_partitionedit(self, event):
        if not self._OM.list('partition'):
            return
        gc = GripyController(event.GetEventObject())    
        dlg = PartitionEditor.Dialog(gc.get_main_window().view)
        dlg.ShowModal()
        dlg.Destroy()
        self.om_tree.refresh()


    def check_tab(self, event):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        wildcard="Arquivos hdf5 (*.h5)|*.h5"
        fdlg = wx.FileDialog(self.get_main_window_controller().view, 'Escolha o projeto a carregar', 
                             wildcard=wildcard, style=style)
        if fdlg.ShowModal() == wx.ID_OK:
            file_proj = fdlg.GetFilename()
            self.odt_dir_name = fdlg.GetDirectory()
            fdlg.Destroy()
        else:
            fdlg.Destroy()
            return
        dfile = os.path.join(self.odt_dir_name, file_proj)
        os.system("vitables %s" %dfile)
            


        


    @staticmethod
    def on_plot(event):
        gc = GripyController(event.GetEventObject())
        gc._UIM.create('logplot_controller', gc.get_main_window().uid)
        
        '''
        dlg = Dialog(self.get_main_window_controller().view, 
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
        '''        

        
    @staticmethod
    def on_crossplot(event):
        gc = GripyController(event.GetEventObject())
        gc._UIM.create('crossplot_controller', gc.get_main_window().uid)        
        
