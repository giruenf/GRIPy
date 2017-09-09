# -*- coding: utf-8 -*-


import sys
import os
import code
import wx
from OM.Manager import ObjectManager
import UI 
from app_utils import Chronometer
import FileIO
from collections import OrderedDict


class DebugConsole(code.InteractiveConsole):
    _OM = None
    
    def __init__(self, outputFunc, setPromptFunc, exitCmd, clearFunc, echoFunc=None):
        self._output = outputFunc
        self._echo = echoFunc
        self._setPrompt = setPromptFunc
        self._exitCmd = exitCmd
        self._clearFunc = clearFunc
        self._OM = ObjectManager(self)      
        self._UIManager = UI.uimanager.UIManager()
        
        self.namespace = {
            "self": self,
            "OM": self._OM,
            "FileIO": FileIO,
            "UI": self._UIManager,
            "clear": self._clearFunc,
            "self": self,
            "exit": self._exitCmd,
            "quit": self._exitCmd,
            "sys": sys,
            "os": os,
            "wx": wx,
            "OrderedDict": OrderedDict
        }
        
        # Can't use super here because stupid code.InteractiveConsole doesn't sub-class object. Grrr!
        code.InteractiveConsole.__init__(self, locals=self.namespace)
        self.prompt = ">>>"
        
        
    def _set_prompt(self, prompt):
        self._prompt = prompt
        self._setPrompt(prompt)

    def _get_prompt(self):
        return self._prompt

    def write(self, data):
        self._output(data)

    def push(self, data):
        lines = data.split('\n')
        if self._echo:
            for line in lines:
                self._echo("%s %s\n" % (self.prompt, line))
            c = Chronometer()
            
        #print 'execute', data    
        # Capture stdout/stderr output as well as code interaction.
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = self
        for line in lines:
            more = code.InteractiveConsole.push(self, line)
            self.prompt = "..." if more else ">>>"
            
        if self._echo:
            self._echo("%s \n\n" % (c.end()))
            
        sys.stdout, sys.stderr = stdout, stderr
        
        
 
class DebugConsoleFrame(wx.Frame):
    
    def __init__(self, parent):
        super(DebugConsoleFrame, self).__init__(parent, wx.ID_ANY, 'GRIPy Python Debug Console')
        self.Bind(wx.EVT_ACTIVATE, self.onActivate)            
        frame_panel = wx.Panel(self, -1)         
        frame_panel_sizer = wx.BoxSizer(wx.VERTICAL)        
        top_panel = wx.Panel(frame_panel, -1)
        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.outputCtrl = wx.TextCtrl(top_panel, wx.ID_ANY, 
                                      style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.outputCtrl.Bind(wx.EVT_KEY_DOWN, self.onOutputKeyDown)
        self.outputCtrl.Bind(wx.EVT_CHAR, self.onOutputChar)
        output_attr = wx.TextAttr(wx.Colour(255,0,0),font=font)
        self.outputCtrl.SetDefaultStyle(output_attr)        
        
        #self.promptLabel = wx.StaticText(self, wx.ID_ANY)
        #top_sizer.Add(self.promptLabel, flag=wx.EXPAND)
        self.inputCtrl = wx.TextCtrl(top_panel, wx.ID_ANY, 
                    style=wx.TE_RICH2 | wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.TE_PROCESS_TAB)        
        self.inputCtrl.Bind(wx.EVT_CHAR, self.onInputChar)
        self.inputCtrl.SetFont(font)
        #input_attr = wx.TextAttr('black', font=font)
        #self.inputCtrl.SetDefaultStyle(input_attr)    
        
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(self.inputCtrl, proportion=5, flag=wx.EXPAND)
        top_sizer.Add(self.outputCtrl, proportion=4, flag=wx.EXPAND)
        top_panel.SetSizer(top_sizer)     
        bottom_panel = wx.Panel(frame_panel, -1)
        ### Begin - buttons_panel             
        buttons_panel = wx.Panel(bottom_panel)      
        self.clear_input_button = wx.Button(buttons_panel, label='Clear input')
        self.clear_input_button.Bind(wx.EVT_BUTTON, self.onClearInput)
        self.clear_output_button = wx.Button(buttons_panel, label='Clear output')
        self.clear_output_button.Bind(wx.EVT_BUTTON, self.onClearOutput)
        self.clear_all_button = wx.Button(buttons_panel, label='Clear all')
        self.clear_all_button.Bind(wx.EVT_BUTTON, self.onClearAll)
        self.execute_button_selected = wx.Button(buttons_panel, label='Excecute selected')
        self.execute_button_selected.Bind(wx.EVT_BUTTON, self.onExecuteSelected)
        self.execute_button_all = wx.Button(buttons_panel, label='Excecute all')
        self.execute_button_all.Bind(wx.EVT_BUTTON, self.onExecuteAll)
        self.load_button = wx.Button(buttons_panel, label='Load')
        self.load_button.Bind(wx.EVT_BUTTON, self.onLoadFile)
        self.save_button = wx.Button(buttons_panel, label='Save')
        self.save_button.Bind(wx.EVT_BUTTON, self.onSaveFile)
        self.save_button_as = wx.Button(buttons_panel, label='Save as')
        self.save_button_as.Bind(wx.EVT_BUTTON, self.onSaveFileAs)
        buttons_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_panel_sizer.Add(self.clear_input_button, 0, wx.ALIGN_CENTER|wx.LEFT, 10)
        buttons_panel_sizer.Add(self.clear_output_button, 0, wx.ALIGN_CENTER|wx.LEFT, 10)
        buttons_panel_sizer.Add(self.clear_all_button, 0, wx.ALIGN_CENTER|wx.LEFT, 10)
        buttons_panel_sizer.Add(self.execute_button_selected, 0, wx.ALIGN_CENTER|wx.LEFT, 10)
        buttons_panel_sizer.Add(self.execute_button_all, 0, wx.ALIGN_CENTER|wx.LEFT, 10)
        buttons_panel_sizer.Add(self.load_button, 0, wx.ALIGN_CENTER|wx.LEFT, 10)
        buttons_panel_sizer.Add(self.save_button, 0, wx.ALIGN_CENTER|wx.LEFT, 10)
        buttons_panel_sizer.Add(self.save_button_as, 0, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 10)
        buttons_panel.SetSizer(buttons_panel_sizer)
        buttons_panel.Layout()
        ### End - buttons_panel
        bottom_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        bottom_panel_sizer.Add(buttons_panel, 1, wx.ALIGN_CENTER|wx.ALL, 2)        
        bottom_panel.SetSizer(bottom_panel_sizer)
        bottom_panel.Layout()
        frame_panel_sizer.Add(top_panel, 1, wx.EXPAND)
        bottom_panel.SetMinSize((40,40))
        frame_panel_sizer.Add(bottom_panel, 0, wx.EXPAND)
        frame_panel.SetSizer(frame_panel_sizer)
        self.console = DebugConsole(outputFunc=self.output, exitCmd=self.Close,
                            clearFunc=self.clearOutput,
                            echoFunc=self.echo, setPromptFunc=self.setPrompt)
        self.SetSize((1350,700))
        self.SetPosition((10,10))        
        
        self.Bind(wx.EVT_CLOSE, self.onClose) 
        
        gripy_app = wx.GetApp()
        _fullfilename = gripy_app._gripy_app_state.get('gripy_debug_file')
        _fullfilename = os.path.normpath(_fullfilename)
        self.file_name = os.path.basename(_fullfilename)
        self.dir_name = os.path.dirname(_fullfilename)
            
        if not os.path.isdir(self.dir_name):
            os.makedirs(self.dir_name)    
            msg = 'DebugConsoleFrame.__init__ has created directory: {}'.format(self.dir_name)
            #log.debug(msg)
            print msg
        if not os.path.isfile(_fullfilename):
            open(_fullfilename, 'a').close()
            msg = 'DebugConsoleFrame.__init__ has created empty file: {}'.format(_fullfilename)
            #log.debug(msg)
            print msg
        if self.file_name and self.dir_name:
            self._load_file()            
                    
            
    def onLoadFile(self, evt):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        wildcard = "Arquivo de console GRIPy (*.gripy_console)|*.gripy_console"
        fdlg = wx.FileDialog(self, 'Escolha o arquivo gripy_console', 
                             defaultDir=self.dir_name, 
                             wildcard=wildcard, 
                             style=style
        )
        if fdlg.ShowModal() == wx.ID_OK:
            self.file_name = fdlg.GetFilename()
            self.dir_name = fdlg.GetDirectory()
            self._load_file()
        fdlg.Destroy()
 
 
    def _load_file(self):
        self.inputCtrl.LoadFile(os.path.join(self.dir_name, self.file_name))  
                            
       
    def onSaveFileAs(self, evt):       
        style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        wildcard = "Arquivo de console GRIPy (*.gripy_console)|*.gripy_console"
        fdlg = wx.FileDialog(self, 'Escolha o arquivo gripy_console', 
                             defaultDir=self.dir_name, 
                             wildcard=wildcard, 
                             style=style
        )
        if fdlg.ShowModal() == wx.ID_OK:
            self.file_name = fdlg.GetFilename()
            self.dir_name = fdlg.GetDirectory()
            self._do_save()
        fdlg.Destroy()       
   
    def onSaveFile(self, evt):          
        self._do_save()
        
    def _do_save(self):
        self.inputCtrl.SaveFile(os.path.join(self.dir_name, self.file_name))
       
    def onExecuteAll(self, evt):
        data = self.inputCtrl.GetValue()
        data = data + '\n'
        self.console.push(data)
        
    def onExecuteSelected(self, evt):
        data = self.inputCtrl.GetStringSelection()
        data = data + '\n'
        self.console.push(data)        

    def onClearInput(self, evt):
        self.clearInput()
   
    def onClearOutput(self, evt):
        self.clearOutput()
     
    def onClearAll(self, evt):
        self.clearInput()
        self.clearOutput()
       
    def onActivate(self, evt):
        if evt.GetActive():
            self.inputCtrl.SetFocus()
        evt.Skip()

    def onClose(self, evt):
        self._do_save()
        evt.Skip()

    def output(self, data):
        self.outputCtrl.WriteText(data)

    def echo(self, data):
        self.outputCtrl.WriteText(data)

    def setPrompt(self, prompt):
        self.promptLabel.SetLabel(prompt)

    def onInputChar(self, evt):
        key = evt.GetKeyCode()
        if key == wx.WXK_TAB:
            data = self.inputCtrl.GetValue()
            ins_point = self.inputCtrl.GetInsertionPoint()
            last_point = self.inputCtrl.GetLastPosition()
            line_number = len(data[0:ins_point].split("\n"))
            if line_number > 1:
                ins_point -= line_number - 1
            data = data[0:ins_point] + '    ' + data[ins_point:last_point]
            self.inputCtrl.ChangeValue(data)
            self.inputCtrl.SetInsertionPoint(ins_point+3+line_number)
            return
        elif key == wx.WXK_F6:
            self.outputCtrl.SetFocus()
            return
        elif key == wx.WXK_ESCAPE:
            self.Close()
            return
        evt.Skip()
        
    def clearOutput(self):
        self.outputCtrl.ChangeValue("")

    def clearInput(self):
        self.inputCtrl.ChangeValue("")

    def onOutputKeyDown(self, evt):
        key = evt.GetKeyCode()
        # #3763: WX 3 no longer passes escape to evt_char for richEdit fields, therefore evt_key_down is used.
        if key == wx.WXK_ESCAPE:
            self.Close()
            return
        evt.Skip()

    def onOutputChar(self, evt):
        key = evt.GetKeyCode()
        if key == wx.WXK_F6:
            self.inputCtrl.SetFocus()
            return
        evt.Skip()
  
  
'''  
def initialize():
    """Initialize the NVDA Python console GUI.
    This creates a singleton instance of the console GUI. This is accessible as L{consoleUI}. This may be manipulated externally.
    """
    global consoleUI
    consoleUI = ConsoleUI(None)


def activate():
    """Activate the console GUI.
    This shows the GUI and brings it to the foreground if possible.
    @precondition: L{initialize} has been called.
    """
    global consoleUI
    consoleUI.Raise()
    # There is a MAXIMIZE style which can be used on the frame at construction, but it doesn't seem to work the first time it is shown,
    # probably because it was in the background.
    # Therefore, explicitly maximise it here.
    # This also ensures that it will be maximized whenever it is activated, even if the user restored/minimised it.
    #consoleUI.Maximize()
    consoleUI.Show()       
'''       
       

    
