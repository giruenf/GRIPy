# -*- coding: utf-8 -*-
import types
import os
import imp
import wx
from yapsy.IPlugin import IPlugin
from yapsy.PluginInfo import PluginInfo
from UI.uimanager import UIManager
from App import log

"""
A reloadable PluginInfo. Must be setted as PluginInfo class in
PluginFileLocator.setPluginInfoClass(GripyPluginInfo) 
It was done in GripyPluginManagerSingleton.get() function.
"""
class GripyPluginInfo(PluginInfo):
    
    def __init__(self, plugin_name, plugin_path):
        super(GripyPluginInfo, self).__init__(plugin_name, plugin_path)
        self._menu_item_uid = None
        
    def reloadPlugin(self):
        if self.is_activated:
            self.deactivatePlugin()
        mod_name = self.plugin_object.__module__
        if os.path.isdir(self.path):
            module = imp.load_module(mod_name, None, 
                                     self.path, ("py","r",imp.PKG_DIRECTORY)
            )
        else:
            with open(self.path+".py","r") as plugin_file:
                module = imp.load_module(mod_name, plugin_file, 
                                     self.path+".py",("py","r",imp.PY_SOURCE)
        )        
        for element in (getattr(module, name) for name in dir(module)):
            for category_name in _CATEGORIES_FILTER.keys():
                try:
                    is_correct_subclass = issubclass(element, _CATEGORIES_FILTER[category_name])
                except Exception:
                    continue
                if is_correct_subclass and element is not _CATEGORIES_FILTER[category_name]:
                    self.plugin_object = element()
        self.activatePlugin()            
        log.debug('Reloaded plugin: {}'.format(self.name))            

    def activatePlugin(self):
        if self.is_activated:
            return
        if self.plugin_object._parent_menu:
            menu_name = self.plugin_object._parent_menu
        else:
            menu_name = GripyPlugin._DEFAULT_PARENT_MENU
        found = None    
        _UIM = UIManager()
        menus = _UIM.list('menu_controller')
        for menu in menus:
            testing_name = menu.model.label
            if testing_name.startswith('&'):
                testing_name = testing_name[1:]
            if testing_name == menu_name:
                found = menu
        if found:
            log.debug('Plugin {} will try insert itself to Menu {}'.format(self.name, found.model.label))

            menu_item = _UIM.create('menu_item_controller', found.uid, 
                            label=unicode(self.name, 'utf8'), 
                            help=unicode(self.description, 'utf8'),
                            callback=self.plugin_object.event_run
            )

            if menu_item:
                self._menu_item_uid = menu_item.uid
            log.debug('Plugin {} was inserted to Menu {}'.format(self.name, found.model.label))
        self.plugin_object.activate()
        log.debug('Activated plugin: {}'.format(self.name))
        
    def deactivatePlugin(self):
        if not self.is_activated:
            return
        if self._menu_item_uid:
            log.debug('Plugin {} will try to remove itself from Menu'.format(self.name))
            _UIM = UIManager()
            _UIM.remove(self._menu_item_uid)
            self._menu_item_uid = None
            log.debug('Plugin {} was removed from Menu'.format(self.name))
        self.plugin_object.deactivate()
        log.debug('Deactivated plugin: {}'.format(self.name))


class GripyPlugin(IPlugin):
    
    _DEFAULT_PARENT_MENU = 'Plugins'    
    
    def __init__(self):
        super(GripyPlugin, self).__init__()
        self._parent_menu = GripyPlugin._DEFAULT_PARENT_MENU
        self._modules = []

    def register_module(self, module):
        if not isinstance(module, types.ModuleType):
            raise TypeError('Cannot register a non-Module object.')
        try:
            self.reload_module(module)
            self._modules.append(module)    
        except Exception:
            raise

    def reload_module(self, module):
        # Reloads every function plugin module, not only doinput, dojob and dooutput
        reload(module)
        try:
            for candidate in (getattr(module,name) for name in dir(module)):
                if callable(candidate):
                    setattr(self, candidate.__name__, candidate)
        except Exception as e: 
            print e.args
            raise
       
    def reload_all_modules(self, *args):
        for module in self._modules:
            self.reload_module(module)       
    
    # To be called by an event (like wx.Menu or wx.Toolbar)
    def event_run(self, *args):
        if isinstance(self, DefaultPlugin):
            self.run()
        else:
            self.run(wx.App.Get().GetTopWindow())

    def run(*args, **kwargs):
        raise NotImplementedError("'run' must be reimplemented by %s" % args[0])
    

class SimpleDialogPlugin(GripyPlugin):
    pass

class AutoGenDataPlugin(GripyPlugin):
    pass

class DefaultPlugin(GripyPlugin):
    pass    


# Observation: Below "default" category is not the as 
# yapsy.PluginManager.PluginManager category "Default".
_CATEGORIES_FILTER = dict(default=DefaultPlugin, 
                        simpledialog=SimpleDialogPlugin, 
                        autogendata=AutoGenDataPlugin
)


