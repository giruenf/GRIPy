# -*- coding: utf-8 -*-

import wx
from collections import OrderedDict
from OM.Manager import ObjectManager
from Algo.Modeling.Reflectivity import Reflectivity

class ReflectivityModel():
    def __init__(self, event):
        self.OM = ObjectManager(event.GetEventObject()) 
        
        self.flagRB = 1        
        
        self.modtype = OrderedDict()    
        self.modtype['PP Seismogram'] = 0
        self.modtype['PS Seismogram'] = 1
        
        self.modresponse = OrderedDict()
        self.modresponse['Complete Response'] = 1   
        self.modresponse['Primaries and Internal Multiples'] = 2
        self.modresponse['Only Primaries Reflections'] = 3
        
        self.wellOptions = OrderedDict()
    
        for well in self.OM.list('well'):
            self.wellOptions[well.name] = well.uid   
           
        self.outtype = OrderedDict() 
        self.outtype['T-X Seismogram'] = 1
        self.outtype['T-X NMO-Corrected Seismogram'] = 2
        self.outtype['Tau-P Seismogram'] = 3
        self.outtype['Tau-P NMO-Corrected Seismogram'] = 4
        self.outtype['Angle Gather'] = 5
    
        self.dlg = wx.Dialog(None, title='Reflectivity Modeling')
        ico = wx.Icon(r'./icons/logo-transp.ico', wx.BITMAP_TYPE_ICO)
        self.dlg.SetIcon(ico)
        
        
        modStatLin = wx.StaticText(self.dlg, - 1, "Modeling Type:")
        modStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)) 
        self.modChoiceBox = wx.Choice(self.dlg, -1, choices=self.modtype.keys())
        
        respStatLin = wx.StaticText(self.dlg, - 1, "Response Type:")
        respStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.respChoiceBox = wx.Choice(self.dlg, -1, choices=self.modresponse.keys())
        
        logStatLin = wx.StaticText(self.dlg, -1, "Input Logs from Well:")    
        logStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
    
        self.logOptions = OrderedDict()
             
        self.wellChoiceBox = wx.Choice(self.dlg, -1, choices=self.wellOptions.keys())    
        self.wellChoiceBox.Bind(wx.EVT_CHOICE, self.on_well_choice) 
    
        outStatLin = wx.StaticText(self.dlg, -1, "Output Type")    
        outStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.outChoiceBox = wx.Choice(self.dlg, -1, choices=self.outtype.keys())
        
        objStatLin= wx.StaticText(self.dlg, -1, "Output Name")
        objStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.objTxtCtrl = wx.TextCtrl(self.dlg, -1, "NEW_NAME")        
        
        vpStatLin = wx.StaticText(self.dlg, -1, "P-Wave Velocity")
        self.vpChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
    
        vsStatLin = wx.StaticText(self.dlg, -1, "S-Wave Velocity")
        self.vsChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
    
        rhoStatLin = wx.StaticText(self.dlg, -1, "Density")
        self.rhoChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
        
        qvalueStatLin = wx.StaticText(self.dlg, -1, "Use Q values from logs?")       
        qvalueStatLin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.yesQvalueRB = wx.RadioButton(self.dlg, -1, 'Yes')        
        self.noQvalueRB = wx.RadioButton(self.dlg, -1, 'No')
        
        self.dlg.Bind(wx.EVT_RADIOBUTTON, self.on_yes_rb, id=self.yesQvalueRB.GetId())
        self.dlg.Bind(wx.EVT_RADIOBUTTON, self.on_no_rb, id=self.noQvalueRB.GetId())        
            
        parStatLin = wx.StaticText(self.dlg, -1, "Parameters List", )    
        parStatLin.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
    
        nsampStatLin = wx.StaticText(self.dlg, -1, "Number of Samples:")
        self.nsampTxtCtrl = wx.TextCtrl(self.dlg, -1, "256")
    
        dtStatLin = wx.StaticText(self.dlg, -1, "Sample Rate:")
        self.dtTxtCtrl = wx.TextCtrl(self.dlg, -1, "0.004")
    
        fwavStatLin = wx.StaticText(self.dlg, -1, "Wavelet Peak Frequency (Hz):")
        self.fwavTxtCtrl = wx.TextCtrl(self.dlg, -1, "30.0")
    
        ntrcsStatLin = wx.StaticText(self.dlg, -1, "Number of Traces:")
        self.ntrcsTxtCtrl = wx.TextCtrl(self.dlg, -1, "50")
    
        trc1StatLin = wx.StaticText(self.dlg, -1, "Trace 1 Cordinate:")
        self.trc1TxtCtrl = wx.TextCtrl(self.dlg, -1, "10.0")
    
        latdtStatLin = wx.StaticText(self.dlg, -1, "Lateral Cordenate Rate:")
        self.latdtTxtCtrl = wx.TextCtrl(self.dlg, -1, "12.5")
    
        cam1velStatLin = wx.StaticText(self.dlg, -1, "First Layer Velocity (m/s):")
        self.cam1velTxtCtrl = wx.TextCtrl(self.dlg, -1, "1500")
    
        cam1thickStatLin = wx.StaticText(self.dlg, -1, "First Layer Thickness (m):")
        self.cam1thickTxtCtrl = wx.TextCtrl(self.dlg, -1, "0.0")
    
        nsupStatLin = wx.StaticText(self.dlg, -1, "Number of Sup Layers:")
        self.nsupTxtCtrl = wx.TextCtrl(self.dlg, -1, "40")
    
        zsupStatLin = wx.StaticText(self.dlg, -1, "Thickness of Sup Layers:")
        self.zsupTxtCtrl = wx.TextCtrl(self.dlg, -1, "20.0")
    
        firstLayerStatLin = wx.StaticText(self.dlg, -1, "Depth of First Layer to be Modeled:")
        self.firstLayerTxtCtrl = wx.TextCtrl(self.dlg, -1, "100.00")

        lastLayerStatLin = wx.StaticText(self.dlg, -1, "Depth of Last Layer to be Modeled:")
        self.lastLayerTxtCtrl = wx.TextCtrl(self.dlg, -1, "270")

        pnumStatLin = wx.StaticText(self.dlg, -1, "Number of Ray Parameters:")
        self.pnumTxtCtrl = wx.TextCtrl(self.dlg, -1, "1000")

        angmaxStatLin = wx.StaticText(self.dlg, -1, "Maximum Angle of Incidence:")
        self.angmaxTxtCtrl = wx.TextCtrl(self.dlg, -1, "75.0")  
        
        vpSupStatLin = wx.StaticText(self.dlg, -1, "Sup Layers P velocity:")
        self.vpSupTxtCtrl = wx.TextCtrl(self.dlg, -1, "3100.00")
        
        vsSupStatLin = wx.StaticText(self.dlg, -1, "Sup Layers S velocity:")
        self.vsSupTxtCtrl = wx.TextCtrl(self.dlg, -1, "1640.00")
        
        wellSizer = wx.FlexGridSizer (cols=2, hgap=3, vgap=3)    
        wellSizer.Add(logStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        wellSizer.Add(self.wellChoiceBox, 0, wx.EXPAND|wx.ALL, 5 )
    
        logSizer = wx.FlexGridSizer(cols=2, hgap=3, vgap=3)
        logSizer.AddGrowableCol(1)
        logSizer.Add(vpStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        logSizer.Add(self.vpChoiceBox, 0, wx.EXPAND|wx.ALL, 5 )
        logSizer.Add(vsStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        logSizer.Add(self.vsChoiceBox, 0, wx.EXPAND|wx.ALL, 5 )
        logSizer.Add(rhoStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        logSizer.Add(self.rhoChoiceBox, 0, wx.EXPAND|wx.ALL, 5 )
        
        rbSizer = wx.FlexGridSizer(cols = 3, hgap=3, vgap=3)
        rbSizer.Add(qvalueStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        rbSizer.Add(self.yesQvalueRB, 0)
        rbSizer.Add(self.noQvalueRB,0)        
        
        parSizer = wx.FlexGridSizer(cols = 4, hgap=5, vgap=5)        
        parSizer.Add(nsampStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.nsampTxtCtrl, 0,)        
        parSizer.Add(cam1velStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.cam1velTxtCtrl, 0,)        
        parSizer.Add(dtStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.dtTxtCtrl, 0,)        
        parSizer.Add(cam1thickStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.cam1thickTxtCtrl, 0,)        
        parSizer.Add(ntrcsStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.ntrcsTxtCtrl, 0,)        
        parSizer.Add(vpSupStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.vpSupTxtCtrl, 0,)        
        parSizer.Add(trc1StatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.trc1TxtCtrl, 0,)        
        parSizer.Add(vsSupStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.vsSupTxtCtrl, 0,)        
        parSizer.Add(latdtStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.latdtTxtCtrl, 0,)        
        parSizer.Add(nsupStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.nsupTxtCtrl, 0,)        
        parSizer.Add(fwavStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.fwavTxtCtrl, 0,)        
        parSizer.Add(zsupStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.zsupTxtCtrl, 0,)        
        parSizer.Add(firstLayerStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.firstLayerTxtCtrl, 0,)        
        parSizer.Add(angmaxStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.angmaxTxtCtrl, 0,)        
        parSizer.Add(lastLayerStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.lastLayerTxtCtrl, 0,)            
        parSizer.Add(pnumStatLin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        parSizer.Add(self.pnumTxtCtrl, 0,)        
        
        outSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)    
        outSizer.AddGrowableCol(1)
        outSizer.Add(outStatLin,0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        outSizer.Add(self.outChoiceBox,0, wx.EXPAND|wx.ALL, 5 )
        outSizer.Add(objStatLin,0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)        
        outSizer.Add(self.objTxtCtrl,0, wx.EXPAND|wx.ALL, 5 )
        
        self.dlg.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)     
        btnSizer = self.dlg.CreateButtonSizer(wx.OK|wx.CANCEL)                              
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(modStatLin, 0, wx.ALL, 5)
        self.mainSizer.Add(self.modChoiceBox, 0, wx.EXPAND|wx.ALL, 5)
        self.mainSizer.Add(respStatLin, 0, wx.ALL, 5)
        self.mainSizer.Add(self.respChoiceBox, 0, wx.EXPAND|wx.ALL, 5)
        self.mainSizer.Add(wx.StaticLine(self.dlg), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        self.mainSizer.Add(wellSizer, 0, wx.ALL, 5) 
        self.mainSizer.Add(logSizer, 0, wx.EXPAND|wx.ALL, 10 )
        self.mainSizer.Add(rbSizer, 0, wx.ALL, 5 )
        self.mainSizer.Add(wx.StaticLine(self.dlg), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        self.mainSizer.Add(parStatLin, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5) 
        self.mainSizer.Add(parSizer, 0, wx.EXPAND|wx.ALL, 10)
        self.mainSizer.Add(wx.StaticLine(self.dlg), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        self.mainSizer.Add(outSizer, 0, wx.EXPAND|wx.ALL, 10)
        self.mainSizer.Add(btnSizer, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
               
        self.dlg.SetSizer(self.mainSizer) 
        self.dlg.SetSize((610, 780)) 
        self.dlg.ShowModal()
        
    def on_yes_rb(self, event):
        
        if self.flagRB == 1:        
            self.qpStatLin = wx.StaticText(self.dlg, -1, "Q value for P-Wave:")
            self.qpChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
            self.qsStatLin = wx.StaticText(self.dlg, -1, "Q value for S-Wave:")
            self.qsChoiceBox = wx.Choice(self.dlg, -1, choices=self.logOptions.keys())
            self.qSizer = wx.FlexGridSizer(cols=2, hgap=3, vgap=3)   
            self.qSizer.AddGrowableCol(1)
            self.qSizer.Add(self.qpStatLin, 0, wx.ALL, 5)
            self.qSizer.Add(self.qpChoiceBox, 0, wx.EXPAND|wx.ALL, 5)
            self.qSizer.Add(self.qsStatLin, 0, wx.ALL, 5)
            self.qSizer.Add(self.qsChoiceBox, 0, wx.EXPAND|wx.ALL, 5)
            self.mainSizer.Insert(8, self.qSizer, 0, wx.EXPAND|wx.ALL, 5)
            self.flagRB = 0
            
        self.dlg.SetSize((610, 860))
        
    def on_no_rb(self, event):
        
        if self.flagRB == 0:        
            self.mainSizer.Remove(self.qSizer)
            self.qpStatLin.Destroy()
            self.qpChoiceBox.Destroy()
            self.qsStatLin.Destroy()
            self.qsChoiceBox.Destroy()
            
            self.dlg.SetSize((610, 780))
            self.flagRB = 1
        
    def on_well_choice(self,event):
        wellname = self.wellChoiceBox.GetStringSelection()
        wellUid = self.wellOptions[wellname]
        self.vpChoiceBox.Clear()
        self.vsChoiceBox.Clear()
        self.rhoChoiceBox.Clear()
        self.logOptions.clear()
        for log in self.OM.list('log', wellUid):
            self.logOptions[log.name] = log.uid
        self.vpChoiceBox.AppendItems(self.logOptions.keys())
        self.vsChoiceBox.AppendItems(self.logOptions.keys())
        self.rhoChoiceBox.AppendItems(self.logOptions.keys())
        
    def on_ok(self, event):
                
        parDict = OrderedDict()
        parDict['Qvalue']=0    
        if self.modChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a type of Seismogram to be modeled!")
            raise Exception("Please choose a type of Seismogram to be modeled!")            
        parDict['modFlag'] = self.modtype[self.modChoiceBox.GetStringSelection()]
        if self.respChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a type of Response!")
            raise Exception("Please choose a type of Response!")            
        parDict['respFlag'] = self.modtype[self.modChoiceBox.GetStringSelection()]
        if self.wellChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a Well!")
            raise Exception("Please choose a Well!")
        parDict['wellID'] = self.wellOptions[self.wellChoiceBox.GetStringSelection()]    
        if self.vpChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a Vp log!")
            raise Exception("Please choose a Vp log!")           
        parDict['vpLogID'] = self.logOptions[self.vpChoiceBox.GetStringSelection()]
        if self.vsChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a Vs log!")
            raise Exception("Please choose a Vs log!")
        parDict['vsLogID'] = self.logOptions[self.vsChoiceBox.GetStringSelection()]
        if self.rhoChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a Density log!")
            raise Exception("Please choose a Density log!")
        parDict['rhoLogID'] = self.logOptions[self.rhoChoiceBox.GetStringSelection()]
        if not self.yesQvalueRB.GetValue() and not self.noQvalueRB.GetValue():
            wx.MessageBox("Please choose the Q-value option!")
            raise Exception("Please choose the Q-value option!")
            parDict['Qvalue'] = self.yesQvalueRB.GetValue()
        if self.flagRB == 0:
            parDict['Qvalue']=1
            if self.qpChoiceBox.GetStringSelection() == "":
                wx.MessageBox("Please choose a Q-value log for P-Wave!")
                raise Exception("Please choose a Q-value log for P-Wave!")
            parDict['Pwav_QvalueID'] = self.logOptions[self.qpChoiceBox.GetStringSelection()]
            if self.qsChoiceBox.GetStringSelection() == "":
                wx.MessageBox("Please choose a Q-value log for S-Wave!")
                raise Exception("Please choose a Q-value log for S-Wave!")
            parDict['Swav_QvalueID'] = self.logOptions[self.qsChoiceBox.GetStringSelection()]
        if self.nsampTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Number of Samples!")
            raise Exception("Please choose the Number of Samples!")
        parDict['numsamps'] = int(float(self.nsampTxtCtrl.GetValue()))
        if self.dtTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Sample Rate Interval!")
            raise Exception("Please choose the Sample Rate Interval!")
        parDict['dt'] = float(self.dtTxtCtrl.GetValue())
        if self.fwavTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose Peak Frequency of the Wavelet to be Used!")
            raise Exception("Please choose Peak Frequency of the Wavelet to be Used!")
        parDict['fWav'] = float(self.fwavTxtCtrl.GetValue())
        if self.ntrcsTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Number of Traces of the Output!")
            raise Exception("Please choose the Number of Traces of the Output!")
        parDict['ntraces'] = int(float(self.ntrcsTxtCtrl.GetValue()))
        if self.trc1TxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the 1st trace cordinate!")
            raise Exception("Please choose the 1st trace cordinate!")
        parDict['trc1'] = float(self.trc1TxtCtrl.GetValue())
        if self.latdtTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Lateral Sample Rate!")
            raise Exception("Please choose the Lateral Sample Rate!")
        parDict['dlat'] = float(self.latdtTxtCtrl.GetValue())
        if self.cam1velTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Velocity of the 1st Layer!")
            raise Exception("Please choose the Velocity of the 1st Layer!")
        parDict['vel1'] = float(self.cam1velTxtCtrl.GetValue())
        if self.cam1thickTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Thickness of 1st Layer!")
            raise Exception("Please choose the Thickness of 1st Layer!")
        parDict['z1'] = float(self.cam1thickTxtCtrl.GetValue())
        if self.nsupTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Number of Superior Layers!")
            raise Exception("Please choose the Number of Superior Layers!")
        parDict['nsup'] = int(float(self.nsupTxtCtrl.GetValue()))
        if self.zsupTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Thickness of Each Superior Layers!")
            raise Exception("Please choose the Thickness of Each Superior Layers!")
        parDict['zsup'] = float(self.zsupTxtCtrl.GetValue())
        if self.firstLayerTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Depth of the 1st Layer to be Modeled!")
            raise Exception("Please choose the Depth of the 1st Layer to be Modeled!")
        parDict['firstLayer'] = float(self.firstLayerTxtCtrl.GetValue())
        if self.lastLayerTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Depth of the Last Layer to be Modeled!")
            raise Exception("Please choose the Depth of the Last Layer to be Modeled!")
        parDict['lastLayer'] = float(self.lastLayerTxtCtrl.GetValue())
        if self.pnumTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Number Ray Parameters to Integration!")
            raise Exception("Please choose the Number Ray Parameters to Integration!")
        parDict['pNum'] = int(float(self.pnumTxtCtrl.GetValue()))
        if self.angmaxTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Maximum Angle of Incidence!")
            raise Exception("Please choose the Maximum Angle of Incidence!")
        parDict['angMax'] = float(self.angmaxTxtCtrl.GetValue())    
        if self.vpSupTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the P velocity of Superior Layers!")
            raise Exception("Please choose the P velocity of Superior Layers!")
        parDict['vpSup'] = float(self.vpSupTxtCtrl.GetValue())    
        if self.vsSupTxtCtrl.GetValue() == "":
            wx.MessageBox("Please choose the Maximum Angle of Incidence!")
            raise Exception("Please choose the Maximum Angle of Incidence!")
        parDict['vsSup'] = float(self.vsSupTxtCtrl.GetValue())
        if self.outChoiceBox.GetStringSelection() == "":
            wx.MessageBox("Please choose a type of Output!")
            raise Exception("Please choose a type of Output!")
        parDict['outFlag'] = self.outtype[self.outChoiceBox.GetStringSelection()]
        if self.objTxtCtrl.GetValue() == "":
            wx.MessageBox("Please Choose an Output Name!")
            raise Exception("Please Choose an Output Name!")
        parDict['outName'] = self.objTxtCtrl.GetValue()       
        
        return_flag = -1
        
        try:
            disableAll = wx.WindowDisabler()
            wait = wx.BusyInfo("Running the Modeling...")
            return_flag = Reflectivity(self.OM, parDict)
        except Exception as e:
            print 'ERROR:', e
            pass
        finally:
            del wait
            del disableAll
            self.dlg.Destroy()

        if return_flag == 1:
            wx.MessageBox('Vp and Vs logs have different sizes!')
        elif return_flag == 2:
            wx.MessageBox('Vp and Density logs have different sizes!')
        elif return_flag == 3:
            wx.MessageBox('Vp and Depth indexes have different sizes!')
        elif return_flag == 4:
            wx.MessageBox('Insuficient Number of Layer!')
        elif return_flag == 5:
            wx.MessageBox('The Q-values Logs have different sizes than Vp and VS!')      
        elif return_flag == 6:
            wx.MessageBox('Done!')
        else:
            wx.MessageBox('Other problems has occurred.')
            