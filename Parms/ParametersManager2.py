import json
from os import path

_jsonfilepath = '.\\Parms'
_jsonfilename = 'parameters2.json'

# global _parametersdict

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

def load():
    global _parametersdict
    with open(path.join(_jsonfilepath, _jsonfilename), 'r') as jsonfile:
        _parametersdict = json.load(jsonfile)

def dump():
    global _parametersdict
    with open(path.join(_jsonfilepath, _jsonfilename), 'w') as jsonfile:
         json.dump(_parametersdict, jsonfile, sort_keys=True, indent=4, separators=(',', ': '))

def getcurvetypefrommnem(mnem):
    global _parametersdict
    key = _removetrailingdigits(mnem).lower()
    
    if key not in _parametersdict['mnemtocurvetype']:
        return ''

    bestmatch = _getbestmatch(_parametersdict['mnemtocurvetype'][key])
    
    return bestmatch

def voteforcurvetype(mnem, curvetype):
    global _parametersdict
    key = _removetrailingdigits(mnem).lower()
    
    if key not in _parametersdict['mnemtocurvetype']:
        _parametersdict['mnemtocurvetype'][key] = {}
    
    if curvetype not in _parametersdict['mnemtocurvetype'][key]:
        _parametersdict['mnemtocurvetype'][key][curvetype] = 0
    
    _parametersdict['mnemtocurvetype'][key][curvetype] += 1

def getcurvetypes():
    global _parametersdict
    return _parametersdict['curvetypes']

def getdatatypefrommnem(mnem):
    global _parametersdict
    key = _removetrailingdigits(mnem).lower()
    
    if key not in _parametersdict['mnemtodatatype']:
        return ''

    bestmatch = _getbestmatch(_parametersdict['mnemtodatatype'][key])
    
    return bestmatch

def votefordatatype(mnem, datatype):
    global _parametersdict
    key = _removetrailingdigits(mnem).lower()
    
    if key not in _parametersdict['mnemtodatatype']:
        _parametersdict['mnemtodatatype'][key] = {}
    
    if datatype not in _parametersdict['mnemtodatatype'][key]:
        _parametersdict['mnemtodatatype'][key][datatype] = 0
    
    _parametersdict['mnemtodatatype'][key][datatype] += 1

def getdatatypes():
    # global _parametersdict
    # return _parametersdict['datatypes']
    return ['Index', 'Log', 'Partition']
