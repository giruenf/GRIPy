# -*- coding: utf-8 -*-
import sys
import imp
from App import log
from yapsy import NormalizePluginNameForModuleName
from yapsy.PluginInfo import PluginInfo
from yapsy.PluginManager import PluginManager
from Plugins import _CATEGORIES_FILTER
from Plugins import GripyPluginInfo


class GripyPluginManager(PluginManager):
        
        
    def __init__(self, categories_filter=None, directories_list=None,
                                 plugin_info_ext=None, plugin_locator=None):
        if not categories_filter: 
            categories_filter = _CATEGORIES_FILTER                            
        super(GripyPluginManager, self).__init__(categories_filter, 
                        directories_list, plugin_info_ext, plugin_locator
        )


    def getPluginByName(self, name):
        # TODO: Comments        
        """
        Get the plugin correspoding to a given category and name
        """
        for info in super(GripyPluginManager, self).getAllPlugins():
            if info.name == name:
                return info
        return None
        

    def activatePluginByName(self, name):
        # TODO: Comments     
        """
        Activate a plugin corresponding to a given category + name.
        """
        pta_item = self.getPluginByName(name)
        if pta_item is not None:
            pta_item.activatePlugin()
            return pta_item
        return None


    def deactivatePluginByName(self, name):
        # TODO: Comments     
        """
        Desactivate a plugin corresponding to a given name.
        """
        plugin_to_deactivate = self.getPluginByName(name)
        if plugin_to_deactivate is not None:
            log.debug("Deactivating plugin: %s"% (name))
            plugin_to_deactivate.deactivate()
            return plugin_to_deactivate
        return None



    def getAllDataLoaded(self):
        # TODO: Comments   
        data_loaded = {}
        for category in super(GripyPluginManager, self).getCategories():
            files_infos = self._category_file_mapping.get(category)[:]
            plugins_infos = self.category_mapping.get(category)[:]
            category_list = zip(plugins_infos, files_infos)
            data_loaded[category] = category_list
        return data_loaded
        

    def searchForPluginLoaded(self, **kwargs):
        # TODO: Comments  
        if not kwargs: 
            return None
        plugin_name = kwargs.get('name', None)    
        infofile = kwargs.get('infofile', None)    
        filepath =  kwargs.get('filepath', None)  
        if not plugin_name and not infofile and not filepath:
            return None
        data_loaded = []
        for list_ in self.getAllDataLoaded().values():
            data_loaded.extend(list_) 
        if plugin_name:
            for plugin_info, info_file in data_loaded:
                if plugin_info.name == plugin_name:
                    return plugin_info, info_file, 'name'
        if filepath:
            if filepath.endswith('.py'):
                filepath = filepath[:-3]
            for plugin_info, info_file in data_loaded:
                if plugin_info == filepath:
                    return plugin_info, info_file, 'filepath'
        if infofile:
            for plugin_info, info_file in data_loaded:
                if info_file == infofile:
                    return plugin_info, info_file, 'infofile'            
        return None                
                 

    def collectPlugins(self):
        """
        Override PluginManager.collectPlugins, but returning 2 lists 
        containing (or not) PluginInfo objects:
        First list contains objects that have been loaded successfully.
        The second one contains objects that were not loaded.      
        
        This function guarantees that a PluginInfo object will belong to only 
        one category (this is done by PluginManager.collectPlugins)
        """
        super(GripyPluginManager, self).locatePlugins()
        exists_previously = []
        still_candidate = []
        for candidate_infofile, candidate_filepath, plugin_info in self._candidates:
            loaded = self.searchForPluginLoaded(name=plugin_info.name, 
                                           filepath=candidate_filepath,
                                           infofile=candidate_infofile
            )
            if loaded:
                exists_previously.append(plugin_info)
            else:
                still_candidate.append((candidate_infofile, candidate_filepath, plugin_info))
        self._candidates = still_candidate        
        processed_plugins = super(GripyPluginManager, self).loadPlugins()
        ok = []
        error =  []        
        for info in processed_plugins:
            if info.error or not info.plugin_object or not info.categories:
                error.append(info)
            else:
                ok.append(info)
        for plugin_info in ok:
            plugin_info.activatePlugin()
        return ok, exists_previously, error    



    def loadPluginDirectly(self, name, fullfilename):
        """
        TODO
        """
        loaded = self.searchForPluginLoaded(name=name, 
                                           filepath=fullfilename
        )
        if loaded:
            raise Exception('GripyPluginManager.loadPluginDirectly: Plugin {} already exist.'.format(loaded[2]))
            
        # If there is candidates before, they are not loaded this time...
        try:
            candidates = self.getPluginCandidates()
        except RuntimeError:
            candidates = None
        # locatePlugins is run just do set self.PM attribute _candidates  
        # maybe setting self._candidates directly instead calling 
        # locatePlugins will be a best option because it does not try 
        # to load unsuccessful candidates again   
        self._candidates = []  # It's a kind of hack to avoid using locatePlugins 
        #self.locatePlugins()    
        if fullfilename.endswith('.py'):
            candidate_filepath = fullfilename[:-3]
        else:
            raise Exception('Only .py files are accept as Plugins.')
        plugin_info = PluginInfo(name, candidate_filepath)
        candidate_tuple = fullfilename, candidate_filepath, plugin_info
        self.appendPluginCandidate(candidate_tuple)  
        infos = self.loadPlugins()
        # Putting candidates back, if any
        if candidates:
            for candidate in candidates:
                self.appendPluginCandidate(candidate)
        if len(infos) > 1:
            raise Exception('Unknown error. Call software devolper.')                
        info = infos[0]        
        if info.error:
            raise info.error[1]
        if not info.plugin_object:
            msg = 'Either this file was already loaded or the plugin class ' + \
                    'does not derive from a plugin base class.'
            raise Exception(msg)
        info.activatePlugin()    
        return info      
 

    def reloadPlugin(self, name):
        loaded = self.searchForPluginLoaded(name=name)
        if not loaded:
            msg = 'Cannot reload a plugin that was not loaded before.'
            raise Exception(msg) 
        plugin_info, _, _ = loaded
        plugin_info.reloadPlugin()
        



class GripyPluginManagerSingleton(object):
    
    __instance = None
    __decoration_chain = None
    
    
    # Verificar uso de decorators atraves de PluginManagerSingleton.setBehaviour
    def get(self):
        """
        Actually create an instance. 
        Obtained from yapsy.PluginManager.PluginManagerSingleton
        """

        if self.__instance is None:
            if self.__decoration_chain is not None:
                # Get the object to be decorated
#                print self.__decoration_chain
                pm = self.__decoration_chain[0]()
                for cls_item in self.__decoration_chain[1:]:
#                    print cls_item
                    pm = cls_item(decorated_manager=pm)
                # Decorate the whole object
                self.__instance = pm
            else:
                # initialise the 'inner' PluginManagerDecorator
                self.__instance = GripyPluginManager()
            log.debug("GripyPluginManagerSingleton initialised.")
        # In order to use only GripyPluginInfo as PluginInfo    
        self.__instance.getPluginLocator().setPluginInfoClass(GripyPluginInfo)    
        return self.__instance
    get = classmethod(get)       
    
    
    