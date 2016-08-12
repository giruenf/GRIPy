# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManagerSingleton as PluginManager

class DefaultPlugin(IPlugin):
    pass

class SimpleDialogPlugin(IPlugin):
    pass

class AutoGenDataPlugin(IPlugin):
    pass

PM = PluginManager.get()

try:
    with open('pluginplaces.txt', 'r') as f:
        pluginplaces = f.readlines()
    PM.setPluginPlaces(pluginplaces) # Ver se pode sair do except (se a verificação de diretórios for feita somente no momento de execução
except:
    pluginplaces = ["Plugins"]
    PM.setPluginPlaces(pluginplaces) # Ver se pode sair do except (se a verificação de diretórios for feita somente no momento de execução

categoriesfilter = dict(default=DefaultPlugin, simpledialog=SimpleDialogPlugin, autogendata=AutoGenDataPlugin)

PM.setCategoriesFilter(categoriesfilter)
PM.collectPlugins()
