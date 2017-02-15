# -*- coding: utf-8 -*-
"""
PLT
===

This file defines the classes and functions necessary to read and write 
Senergy's Interactive Petrophysics (IP) PLT files.
Based on observations of ASCii PLT files placed in IP's Default Plot 
directory.
 

References
----------
.. [1] Interactive Petrophysics version 4.1:
    Interactive Petrophysics is a trademark of Senergy Software Limited
"""


from utils import AsciiFile    
import os, os.path

"""
    Class to representate a .plt file
"""
class PLTFile(object):
    def __init__(self):
        self.filename = None
        self._data = []
        
    @property
    def name(self):
        if not self.filename:
            return None
        head, tail = os.path.split(self.filename)        
        name, ext = os.path.splitext(tail)    
        return name    

    @property   
    def data(self):
        return self._data      
    
    @data.setter
    def data(self, value):
        self._data = value  


"""
    Method to read a .plt file
    Returns: An object pltfile
"""
def Reader(filename):
    pltfile = PLTFile()        
    pltfile.filename = filename.encode('string-escape')
    content = AsciiFile.read_file_as_list(pltfile.filename, '$')        
    if not content:
        return None
    for line in content:
        if line:
            key = line[0]
            values = line[1:]
            if key and values:    
                pltfile.data.append((key, values))
    return pltfile        
                
                
"""
    Method to read all .plt files in a specific directory
    Returns: A list of pltfile objects 
"""
def getPLTFiles(dirname):
    dirname = dirname.encode('string-escape')
    plts = []
    for filename in os.listdir(dirname):
        if filename.endswith(".plt") or filename.endswith(".PLT"):              
            fullname = os.path.join(dirname, filename)   
            plts.append(Reader(fullname))
    return plts                 
     
            