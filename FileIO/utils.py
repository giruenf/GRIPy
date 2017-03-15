# -*- coding: utf-8 -*-    
    
def clean_path_str(path):
    path = path.replace('\\' ,'/')  
    path = path.encode('ascii', 'ignore') # in order to save unicode characters
    path = path.encode('string-escape')
    return path

def open_file(fullfilename, mode='r'):
    fullfilename = clean_path_str(fullfilename) 
    return open(fullfilename, mode)

"""
Reads a file, discards comments, and returns its content as list of strings.
Retuns: A List (lines) of list (rows) of strings.
"""
def read_file_as_list(fullfilename, comment_str=None, splitter_str=None):
    file_ = open_file(fullfilename)
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
def write_file_from_list(fullfilename, list_to_be_written):    
    fullfilename = clean_path_str(fullfilename)
    with open(fullfilename, 'w') as file_:
        for line in list_to_be_written:
            print line
            file_.write(' '.join(line) + '\n')
    file_.close()    


def create_empty_file(fullfilename):    
    fullfilename = clean_path_str(fullfilename)  
    return open(fullfilename, 'w')
    
    
