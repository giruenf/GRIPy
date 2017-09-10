# -*- coding: utf-8 -*-

from DataTypes import GenericDataType
        
    
class Rock(GenericDataType):

    tid = 'rock'
    _TID_FRIENDLY_NAME = 'Rock'
    
    
    def __init__(self, **attributes):
        super(Rock, self).__init__(None, **attributes)




class RockInference(object):

    def __init__(self):
        self.rock = None
        self.measures = []

'''
class Rock(object):
 
    def __init__(self):
        self.frame = None    
'''    
    
class RockFramework(object):

    def __init__(self):
        self.mineralogy = None
        self.porosity = None
        self.texture = None
        
        
class RockMineralogy(object):

    def __init__(self):
        pass
    
    
class RockPorosity(object):

    def __init__(self):
        pass
    

class RockTexture(object):

    def __init__(self):
        pass    
    
    
class RockCell(object):
    
    def __init__(self):
        pass    
    
    
class CellLogMD(object):
    
    def __init__(self):
        pass        
    
    
class Measure(object):
    
    def __init__(self):
        self.name = None
        self.type = None
        self.value = None
        self.unit = None
        self.env = None
        self.date = None
        
        
class EnvironmentProperties(object):
    
    def __init__(self):
        self.pressure = None
        self.temperature = None
        
              
            
 
    