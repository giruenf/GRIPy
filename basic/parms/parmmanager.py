# -*- coding: utf-8 -*-

import os
import json

import app

CURVETYPES_FILE = 'curvetypes.json'
PARAMETERS_FILE = 'parameters.json'


# GRIPY_DEFAULT_PLOT='Gripy Default.plt_'


def _removetrailingdigits(text):
    count = 0
    for character in reversed(text):
        if not character.isdigit():
            break
        count += 1
    if count == len(text) or count == 0:
        return text
    return text[:-count]


def _getbestmatch(dictionary):
    maxcount = -1
    bestmatch = ''
    for type_, count in dictionary.items():
        if count > maxcount:
            maxcount = count
            bestmatch = type_
    return bestmatch


# Based on yapsy.PluginManager
class ParametersManager(object):

    def __init__(self):
        """
        self.PLTs = OrderedDict()
        # For read first Gripy Default Plot
        dirname = os.path.dirname(os.path.abspath(__file__))
        dirname = dirname.encode('string-escape')
        fullname = os.path.join(dirname, GRIPY_DEFAULT_PLOT) 
        self.PLTs['GRIPy Default Plot'] = FileIO.PLT.Reader(fullname)
        # End - Gripy Default Plot
        self.PLTs['No Tracks Plot'] = None
        self.PLTs = FileIO.PLT.getPLTFiles(self.PLTs, os.path.dirname(os.path.abspath(__file__)))
        """

        # base_path == this floder
        base_path = os.path.dirname(os.path.abspath(__file__))
        #
        self._curvetypes = app.app_utils.read_json_file(
            os.path.join(base_path, CURVETYPES_FILE)
        )
        #     
        self._parametersdict = app.app_utils.read_json_file(
            os.path.join(base_path, PARAMETERS_FILE)
        )

        # def getPLTs(self):

    #    self.check_and_reload_PLTs()
    #    return self.PLTs

    # def getPLT(self, PLT_name):
    #    self.check_and_reload_PLTs()
    #    return self.PLTs.get(PLT_name)

    # def get_PLTs_names(self):
    #    return self.getPLTs().keys()

    # def check_and_reload_PLTs(self):
    #    self.PLTs = FileIO.PLT.getPLTFiles(self.PLTs, os.path.dirname(os.path.abspath(__file__)))

    def get_tids(self):
        """Return valid tids.
        """
        return self._parametersdict["TIDS"]

    def get_datatypes(self, tid):
        """Given a tid name (e.g. log) return its datatypes associated.
        """
        return self._parametersdict["DATATYPES"].get(tid)

    def get_all_datatypes(self):
        ret_list = []
        for tid, dts in self._parametersdict["DATATYPES"].items():
            ret_list += list(dts)
        return ret_list

    def get_datatypes_visual_props(self, datatype_name):
        """Given a datatype name (e.g. GammaRay) return its visual properties.
        """
        return self._curvetypes.get(datatype_name)

    def get_datatype_from_mnemonic(self, mnem):
        """Given a mnemonic (e.g. GR), return its datatype (e.g. GammaRay)
        """
        key = _removetrailingdigits(mnem).lower()
        datatype = self._parametersdict["MNEMONIC_TO_DATATYPE"].get(key)
        if not datatype:
            return None
        # Let's get most voted...
        datatype = _getbestmatch(datatype)
        return datatype

    def get_tid_from_mnemonic(self, mnem):
        """Given a mnemonic (e.g. GR), return its tid (e.g. log)
        """
        datatype = self.get_datatype_from_mnemonic(mnem)
        if datatype is None:
            msg = 'Unknown datatype for mnemonic: {}'.format(mnem)
            raise Exception(msg)
        #
        for tid, datatypes in self._parametersdict["DATATYPES"].items():
            if datatype in datatypes:
                return tid
        msg = 'Unknown tid for mnemonic: {}'.format(mnem)
        raise Exception(msg)

    def vote_for_datatype(self, mnem, datatype):
        """Register user selections.
        """
        key = _removetrailingdigits(mnem).lower()
        if self._parametersdict["MNEMONIC_TO_DATATYPE"].get(key) is None:
            msg = 'PM.vote_for_curvetype criou mnemonic key:' + key
            print(msg)
            self._parametersdict["MNEMONIC_TO_DATATYPE"][key] = {}
        #    
        if datatype not in self._parametersdict["MNEMONIC_TO_DATATYPE"][key]:
            self._parametersdict["MNEMONIC_TO_DATATYPE"][key][datatype] = 0
            msg = 'PM.vote_for_curvetype criou datatype:' + datatype \
                  + ' for key:' + key
            print(msg)
        self._parametersdict["MNEMONIC_TO_DATATYPE"][key][datatype] += 1

    """
    def votefordatatype(self, mnem, datatype):
        key = _removetrailingdigits(mnem).lower()
        if self._parametersdict['MNEMONIC_TO_DATATYPE'].get(key) is None:
            print ('votefordatatype criou key:', key)
            self._parametersdict['MNEMONIC_TO_DATATYPE'][key] = {}
        
        if self._parametersdict['MNEMONIC_TO_DATATYPE'][key].get(datatype) is None:
            self._parametersdict['MNEMONIC_TO_DATATYPE'][key][datatype] = 0 
            print ('votefordatatype criou datatype:', datatype)
        try:    
            self._parametersdict['MNEMONIC_TO_DATATYPE'][key][datatype] += 1
        except KeyError:
            print (mnem, datatype, key)
            raise
    """

    def register_votes(self):
        """Save to the JSON file.
        """
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               PARAMETERS_FILE), 'w') as jsonfile:
            json.dump(self._parametersdict,
                      jsonfile,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': ')
                      )


# Based on yapsy.PluginManagerSingleton
class ParametersManagerSingleton(object):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = ParametersManager()
        return cls.__instance
