import code
import os
import sys

import wx

from app.app_utils import Chronometer
from app.app_utils import GripyBitmap 
from classes.ui import UIManager
from ui.mvc_classes.workpage import WorkPageController
from ui.mvc_classes.workpage import WorkPage


# TODO: rever isso... replicado em WellPlot
WP_FLOAT_PANEL = wx.NewId() 


class ConsoleController(WorkPageController):
    tid = 'console_controller'
    _ATTRIBUTES = {
    }
    
    def __init__(self, **state):
        super().__init__(**state)


class InteractiveConsole(code.InteractiveConsole):
    
    def __init__(self, outputFunc, flushFunc, setPromptFunc, exitCmd, clearFunc, echoFunc=None):
        self._output = outputFunc
        self._flush = flushFunc
        self._echo = echoFunc
        self._setPrompt = setPromptFunc
        self._exitCmd = exitCmd
        self._clearFunc = clearFunc 
        
        
        # Can't use super here because stupid code.
        # InteractiveConsole doesn't sub-class object. Grrr!
        #code.InteractiveConsole.__init__(self) # , locals=self.namespace)
        super().__init__(locals=None) #, filename=self._output) # locals=None, filename="<console>"
        self.prompt = ">>>"
        
    def _set_prompt(self, prompt):
        self._prompt = prompt
        self._setPrompt(prompt)

    def _get_prompt(self):
        return self._prompt

    def write(self, data):
        self._output(data)

    def _show_error_info(self, exectype, value, tb):
        msg = '\nError found! \nError type: ' + exectype.__name__ \
                                    + '\nDescription: ' + str(value) + '\n'
        #print('Traceback:', tb)
        self.write(msg)
                
    def push(self, data):
        lines = data.split('\n')
        if self._echo:
            for line in lines:
                self._echo("%s %s\n" % (self.prompt, line))
            c = Chronometer()               
        # Capture stdout/stderr output as well as code interaction.
        stdout, stderr = sys.stdout, sys.stderr
        temp_excepthook = sys.excepthook
        sys.excepthook = self._show_error_info
        #
        sys.stdout = sys.stderr = self
        for line in lines:
            #more = code.InteractiveConsole.push(self, line)
            more = super().push(line)
            self.prompt = "..." if more else ">>>"
        #    
        if self._echo:
            self._echo("%s \n\n" % (c.end()))  
        #    
        sys.excepthook = temp_excepthook
        sys.stdout, sys.stderr = stdout, stderr
       
    def flush(self):
        self._flush()
        


class Console(WorkPage):
    tid = 'console'
    _TID_FRIENDLY_NAME = 'Coding Console'
    
    def __init__(self, controller_uid):   
        super().__init__(controller_uid) 
        # Top
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self._tool_bar =  wx.aui.AuiToolBar(self)
        self.sizer.Add(self._tool_bar, 0, flag=wx.TOP|wx.EXPAND)
        # Center    
        self._main_panel = wx.Panel(self)
        self.sizer.Add(self._main_panel, 1, flag=wx.EXPAND)
        #
        self.SetSizer(self.sizer)
        # Then, let's construct our ToolBar
        self._build_tool_bar()
               
#        super(DebugConsoleFrame, self).__init__(parent, 
#                                                wx.ID_ANY, 
#                                                'GRIPy Python Debug Console'
#        )
#        self.Bind(wx.EVT_ACTIVATE, self.onActivate)         
        
#        self.sizer = wx.BoxSizer(wx.VERTICAL)
#        self._main_panel = wx.Panel(self)
#        self.sizer.Add(self._main_panel, 1, flag=wx.EXPAND)        
                
        main_panel_sizer = wx.BoxSizer(wx.VERTICAL)        
        top_panel = wx.Panel(self._main_panel, -1)
        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.outputCtrl = wx.TextCtrl(top_panel, wx.ID_ANY, 
                            style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2
        )
        self.outputCtrl.Bind(wx.EVT_KEY_DOWN, self.onOutputKeyDown)
        self.outputCtrl.Bind(wx.EVT_CHAR, self.onOutputChar)
        output_attr = wx.TextAttr(wx.Colour(255,0,0), font=font)
        self.outputCtrl.SetDefaultStyle(output_attr)        
        #
        self.inputCtrl = wx.TextCtrl(top_panel, wx.ID_ANY, 
            style=wx.TE_RICH2|wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.TE_PROCESS_TAB
        )        
        self.inputCtrl.Bind(wx.EVT_CHAR, self.onInputChar)
        self.inputCtrl.SetFont(font)
        #
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(self.inputCtrl, proportion=4, flag=wx.EXPAND)
        top_sizer.Add(self.outputCtrl, proportion=4, flag=wx.EXPAND)
        top_panel.SetSizer(top_sizer)     
        bottom_panel = wx.Panel(self._main_panel, -1)
        
        
        ### Begin - buttons_panel             
        buttons_panel = wx.Panel(bottom_panel)      
        self.clear_input_button = wx.Button(buttons_panel, 
                                            label='Clear input'
        )
        self.clear_input_button.Bind(wx.EVT_BUTTON, self.onClearInput)
        self.clear_output_button = wx.Button(buttons_panel, 
                                             label='Clear output'
        )
        self.clear_output_button.Bind(wx.EVT_BUTTON, self.onClearOutput)
        self.clear_all_button = wx.Button(buttons_panel, 
                                          label='Clear all'
        )
        self.clear_all_button.Bind(wx.EVT_BUTTON, self.onClearAll)
        self.execute_button_selected = wx.Button(buttons_panel, 
                                                 label='Excecute selected'
        )
        self.execute_button_selected.Bind(wx.EVT_BUTTON, 
                                          self.onExecuteSelected
        )
        self.execute_button_all = wx.Button(buttons_panel, 
                                            label='Excecute all'
        )
        self.execute_button_all.Bind(wx.EVT_BUTTON, 
                                     self.onExecuteAll
        )
        self.load_button = wx.Button(buttons_panel, 
                                     label='Load'
        )
        self.load_button.Bind(wx.EVT_BUTTON, 
                              self.onLoadFile
        )
        self.save_button = wx.Button(buttons_panel, 
                                     label='Save'
        )
        self.save_button.Bind(wx.EVT_BUTTON, 
                              self.onSaveFile
        )
        self.save_button_as = wx.Button(buttons_panel, 
                                        label='Save as'
        )
        self.save_button_as.Bind(wx.EVT_BUTTON, 
                                 self.onSaveFileAs
        )
        buttons_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_panel_sizer.Add(self.clear_input_button, 
                                0, 
                                wx.ALIGN_CENTER|wx.LEFT, 
                                10
        )
        buttons_panel_sizer.Add(self.clear_output_button, 
                                0, 
                                wx.ALIGN_CENTER|wx.LEFT, 
                                10
        )
        buttons_panel_sizer.Add(self.clear_all_button, 
                                0, 
                                wx.ALIGN_CENTER|wx.LEFT, 
                                10
        )
        buttons_panel_sizer.Add(self.execute_button_selected, 
                                0, 
                                wx.ALIGN_CENTER|wx.LEFT, 
                                10
        )
        buttons_panel_sizer.Add(self.execute_button_all, 
                                0, 
                                wx.ALIGN_CENTER|wx.LEFT, 
                                10
        )
        buttons_panel_sizer.Add(self.load_button, 
                                0,
                                wx.ALIGN_CENTER|wx.LEFT, 
                                10
        )
        buttons_panel_sizer.Add(self.save_button, 
                                0, 
                                wx.ALIGN_CENTER|wx.LEFT, 
                                10
        )
        buttons_panel_sizer.Add(self.save_button_as, 
                                0, 
                                wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 
                                10
        )
        buttons_panel.SetSizer(buttons_panel_sizer)
        buttons_panel.Layout()
        ### End - buttons_panel
        bottom_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        bottom_panel_sizer.Add(buttons_panel, 1, wx.ALIGN_CENTER|wx.ALL, 2)        
        bottom_panel.SetSizer(bottom_panel_sizer)
        bottom_panel.Layout()
        main_panel_sizer.Add(top_panel, 1, wx.EXPAND)
        bottom_panel.SetMinSize((40,40))
        main_panel_sizer.Add(bottom_panel, 0, wx.EXPAND)
        #
        self._main_panel.SetSizer(main_panel_sizer)
        self.console = InteractiveConsole(outputFunc=self.output, 
                                    flushFunc=self.flush,
                                    exitCmd=self.Close,
                                    clearFunc=self.clearOutput,
                                    echoFunc=self.echo, 
                                    setPromptFunc=self.setPrompt
        )
#        main_panel_sizer.Layout()
        self.Layout()
#        self.SetSize((1350,700))
#        self.SetPosition((10,10))        
        #
        self.Bind(wx.EVT_CLOSE, self.onClose) 
        #
        gripy_app = wx.GetApp()
        _fullfilename = gripy_app._gripy_app_state.get('gripy_debug_file')
        _fullfilename = os.path.normpath(_fullfilename)
        self.file_name = os.path.basename(_fullfilename)
        self.dir_name = os.path.dirname(_fullfilename)
        #    
        if not os.path.isdir(self.dir_name):
            os.makedirs(self.dir_name)    
            msg = 'DebugConsoleFrame.__init__ has created directory: {}'.format(self.dir_name)
            #log.debug(msg)
            #print(msg)
        if not os.path.isfile(_fullfilename):
            open(_fullfilename, 'a').close()
            msg = 'DebugConsoleFrame.__init__ has created empty file: {}'.format(_fullfilename)
            #log.debug(msg)
            #print (msg)
        if self.file_name and self.dir_name:
            self._load_file()            


    def get_friendly_name(self):
        idx = self._get_sequence_number()     
        name = self._get_tid_friendly_name() \
                               + ': ' + '['+ str(idx) + ']' 
        return name

    def _build_tool_bar(self):
        self.fp_item = self._tool_bar.AddTool(WP_FLOAT_PANEL, 
                      wx.EmptyString,
                      GripyBitmap('restore_window-25.png'), 
                      wx.NullBitmap,
                      wx.ITEM_CHECK,
                      'Float Panel', 
                      'Float Panel',
                      None
        )
        self._tool_bar.ToggleTool(WP_FLOAT_PANEL, False)
        self._tool_bar.Bind(wx.EVT_TOOL, self._on_change_float_panel, None,
                  WP_FLOAT_PANEL
        )                
        self._tool_bar.AddSeparator()
        self._tool_bar.Realize()  
        #     

    def _on_change_float_panel(self, event):
        # TODO: Integrar binds de toggle buttons...
        if event.GetId() == WP_FLOAT_PANEL:
            UIM = UIManager()   
            controller = UIM.get(self._controller_uid)
            controller.float_mode = event.IsChecked()  
                             
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
        print('\n\nonClose')
        
    def output(self, data):
        self.outputCtrl.WriteText(data)

    def flush(self):
        self.outputCtrl.flush()

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
  
 
