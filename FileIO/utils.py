# -*- coding: utf-8 -*-
import json
import os

try:
    import builtins
except ImportError:
    import __builtin__ as builtins
    
  
class AsciiFile(object):
    @classmethod
    def clean_path_str(cls, path):
        path = path.replace('\\' ,'/')  
        path = path.encode('ascii', 'ignore') # in order to save unicode characters
        path = path.encode('string-escape')
        return path
    

    @classmethod
    def open_file(cls, fullfilename, mode='r'):
        fullfilename = cls.clean_path_str(fullfilename) 
        return builtins.open(fullfilename, mode)

    """
    Reads a file, discards comments, and returns its content as list of strings.
    Retuns: A List (lines) of list (rows) of strings.
    """
    @classmethod
    def read_file_as_list(cls, fullfilename, comment_str=None, splitter_str=None):
        file_ = cls.open_file(fullfilename)
        lines = []
        for line in file_:
            if comment_str:
                line = line.partition(comment_str)[0]
                line = line.rstrip()
            if '\n' in line:
                line = line.replace('\n', '')
            if splitter_str:
                data = line.split(splitter_str)
            else:
                data = line.split() 
            lines.append(data)
        file_.close()    
        return lines     


    """
    Write a file from a list (lines) of list (rows) of strings.
    Retuns: Number os written lines
    """  
    @classmethod
    def write_file_from_list(cls, fullfilename, list_to_be_written):    
        fullfilename = cls.clean_path_str(fullfilename)
        with builtins.open(fullfilename, 'w') as file_:
            for line in list_to_be_written:
                print line
                file_.write(' '.join(line) + '\n')
        file_.close()    


    @classmethod
    def get_empty_file(cls, fullfilename):    
        fullfilename = cls.clean_path_str(fullfilename)  
        return builtins.open(fullfilename, 'w')
        
        
    @classmethod
    def write_json_file(cls, py_object, fullfilename):
        fullfilename = cls.clean_path_str(fullfilename)
        f = cls.get_empty_file(fullfilename)
        f.write(json.dumps(py_object, indent=4))
        f.close()
    
    @classmethod
    def read_json_file(cls, fullfilename):
        fullfilename = cls.clean_path_str(fullfilename)
        f = cls.open_file(fullfilename)
        py_object = json.load(f)
        f.close()
        return py_object
        
        