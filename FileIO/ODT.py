# -*- coding: utf-8 -*-
"""
ODT
===

This file defines the classes and functions necessary to read and write wll
(OpendTect well log files)
Version 4.0

References
----------
.. [1] OpendTect:
    http://www.opendtect.org
"""


import numpy as np
import os
from collections import OrderedDict

try:
    import builtins
except ImportError:
    import __builtin__ as builtins


class ODTManager():
    
    def __init__(self,dirct, filename):
        self.filename = filename[:-4]
        self.logheader = []
        self.fileheader = []
        self.headersectionnames = {}
        self.headerlayout = {}
        self.headercomments = {}
        self.data = np.empty(0)
        self.curvesnames = []
        self.curvesunits = []
        self.ndepth = np.empty(0)
        self.proj(self, dirct, filename)
        
    @staticmethod
    def proj(self, dirct, filename):
        list_files = os.listdir(dirct)
        log_files = []
        for i in list_files:
            if i[:len(filename)-5] == filename[:-5] and i[-4:] == '.wll':
                
                log_files.append(i)
        data = []
        depth = []
        for filename in log_files:
            odt_file = ODTReader(os.path.join(dirct,filename))
            odt_file.read()
            self.fileheader = odt_file.fileheader
            self.logheader.append(odt_file.logheader)
            self.curvesnames.append(odt_file.logheader['Name'][1:5])
            self.curvesunits.append(odt_file.logheader['Unit of Measure'][1:5])
#            self.data =  np.insert(self.data, len(self.data), odt_file.data)
#            self.data = np.insert(self.data,)
            depth.append(odt_file.depth)
            data.append(odt_file.data)
#            self.data = np.asarray(data)
        
#        print '\ndepth', depth
        maxdepts = []
        mindepts = []
        for d in depth:
            maxdepts.append(max(d))
            mindepts.append(min(d))
        maxdepth = max(maxdepts)
        mindepth = min(mindepts)
        step = depth[0][1] - depth[0][0]
        self.ndepth = np.arange(mindepth,maxdepth, step)
        for i in range(len(depth)):
            fixmin= np.arange(mindepth,depth[i].min(), step)
            fixmax= np.arange(depth[i].max()+step, maxdepth+step, step)
            
#            print '\ninicio\n',len(fixmin), len(fixmax), len(values[i]), len(total), len(depth[i]), total[12297]#, (mindepth-depth[i].min())/step,(maxdepth-depth[i].max())/step,total
            if len(fixmin) != 0:
#                print len(fixmin)
                for j in range(len(fixmin)-1):
#                    print j
                    depth[i] = np.insert(depth[i], 0, np.nan)
                    data[i] = np.insert(data[i], 0, np.nan)
            if len(fixmax) != 0:
#                print len(fixmax)
                for j in range (len(fixmax)-1):
#                    print j
                    data[i] = np.insert(data[i], len(data[i]), np.nan)
                    depth[i] = np.insert(depth[i], len(depth[i]), np.nan)
#            print '\n\n', depth
        
        data.insert(0,self.ndepth)
        self.data = np.asarray(data)
        self.curvesnames.insert(0, ' DEPT')
        self.curvesunits.insert(0,'')

class ODTFile(object):
   
    def __init__(self, filename):
        self.filename = filename
        self.logheader = OrderedDict()
        self.fileheader = []
        self.headersectionnames = {}
        self.headerlayout = {}
        self.headercomments = {}
        self.depth = np.empty(0)
        self.data = np.empty(0)
        self.curvenames = ''
        self.curveunits = ''


class ODTReader(ODTFile):

    def __init__(self, filename):
        super(ODTReader, self).__init__(filename)

    @property
    def curvesnames(self):
        return [line['MNEM'] for line in self.header["C"].itervalues()]
#    
    @property
    def curvesunits(self):
        return [line['UNIT'] for line in self.header["C"].itervalues()]

    @staticmethod    
    def _getheaderlines(fileobject):
        fileobject.seek(0)
        fileheader = []
        logheader = []
        line = fileobject.readline()
        while not line.startswith('!'):
            fileheader.append(line.strip())
            line = fileobject.readline()
        line = fileobject.readline()
        while not line.startswith('!'):
            logheader.append(line.strip())
            line = fileobject.readline()
        return fileheader, logheader
    
    @staticmethod
    def _getheader(headerlines):
        header = OrderedDict()
   
        for i in headerlines:
            label, info = i.strip().split(':')
            header [label] = info
        try:
            header['Unit of Measure']
        except:
            header['Unit of Measure'] = ''
        return header
        
    @staticmethod
    def _getdatalines(fileobject):
        dept = np.empty(0)
        value=np.empty(0)
#        fileobject.seek(0)
        datalines = fileobject.readlines()
        for i in datalines:
            dep,val = i.split('\t')
#            dept.append(float(dep))
#            value.append(float(val.strip()))
            if float(val.strip()) == 1e30:
                val = np.nan
            else:
                val = float(val.strip())
            dept = np.insert(dept, len(dept), round(float(dep),2))
            value = np.insert(value, len(value), val)

        return dept, value

    
    def read(self):
        fileobject = builtins.open(self.filename, 'r')
        self.fileheader, headerlines = ODTReader._getheaderlines(fileobject)
        self.depth, self.data = ODTReader._getdatalines(fileobject)
        
        self.logheader = ODTReader._getheader(headerlines)

def open(dirct, filename, mode='r'):

    if mode == 'r':
        odtfile = ODTManager(dirct, filename)
#    elif mode == 'w':
#        odtfile = ODTWriter(name)
    else:
        odtfile = None
    
    return odtfile
  
if __name__ == '__main__':
    dirct = "C:\\Users\\Tabelini\\Dropbox\\Python\\"
    filename = "1RJS-0074--RJ-^2.wll"
#    odt_file = ODTReader("C:\\Users\\Tabelini\\Dropbox\\Python\\1RJS-0074--RJ-^2.wll")
#    odt_file.read()
    odt_file = open(dirct, filename)
    print odt_file.fileheader, '\n\n',odt_file.logheader, '\n\n', odt_file.ndepth