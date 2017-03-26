# -*- coding: utf-8 -*-

class RockInference(object):

    def __init__(self):
        self.rock = None
        self.measures = []


class Rock(object):
 
    def __init__(self):
        self.frame = None    
    
    
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
        
        
class Unit(object):
    
    def __init__(self):    
        self.name = None
        self.type = None
        
        
class UnitType(object):
    
    def __init__(self):    
        self.name = None
        self.type = None        
            
 
    