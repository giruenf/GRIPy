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
from collections import OrderedDict

try:
    import builtins
except ImportError:
    import __builtin__ as builtins


class ODTFile(object):
#    """
#    A ODT 2.0 file object.
#    
#    Parameters
#    ----------
#    filename : str
#        File name
#
#    Attributes
#    ----------
#    filename : str
#        File name.
#    header : OrderedDict
#        Header of the file. Each section of the ODT header is a value in the
#        dictionary. The key of each section is its capitalized first letter
#        (e.g. "V" for VERSION section). Each section is also an OrderedDict, in
#        which the keys are the mnems of the lines and the lines themselves are
#        the values. The lines are dicts with 4 keys: "MNEM", "UNIT", "DATA" and
#        "DESC".
#    headersectionnames : dict
#        Names of the header sections. The keys are the capitalized first
#        letters of each section and the values are the full section names.
#    headerlayout : dict
#        Layout of the header. Similar to `header`, but instead of the lines,
#        contains the layout of the line. The layout of a line is a list of 6
#        ints, representing the number of whitespaces in the line. The elements
#        of the list are, respectively, the number of whitespaces between the
#        beginning of the line and the beginning of the mnem, the end of mnem
#        and the first dot, the end of the unit and the beginning of the data,
#        the end of the data and the colon, the colon and the beginning of the
#        description and the end of the description and the end of the line.
#    headercomments : dict
#        Comments in the ODT header. The keys are the linenumber of the comment
#        and the values are the comments themselves.
#    data : numpy.ndarray
#        The data present in the ASCII section of the ODT file. The data shape
#        is nc x ns, where nc is the number of curves and ns is the
#        number of samples.
#    """
    
    def __init__(self, filename):
        self.filename = filename
        self.logheader = OrderedDict()
        self.fileheader = []
        self.headersectionnames = {}
        self.headerlayout = {}
        self.headercomments = {}
        self.data = np.empty(0)
        self.curvenames = ''
        self.curveunits = ''


class ODTReader(ODTFile):
    """
    A specialization of `ODTFile` for reading files.
    
    Attributes
    ----------
    wellname : str
        Name of the well.
    curvesnames : list
        Name of each curve.
    curvesunits : list
        Unit of each curve.
    
    Notes
    -----
    When creating a `ODTReader` object the file is not read immediately. The
    `read` method must be called after the creation. Once it is called, all
    of its attributes will be read from the file and the file will be closed.
    
    Examples
    --------
    >>> odtfile = ODTReader("filename.las")
    >>> odtfile.read()
    >>> odtfile.wellname
    'wellname'
    >>> odtfile.curvesnames
    ['curve01name', 'curve02name', ...]
    >>> odtfile.header["V"]["VERSION"]["DATA"]
    '2.0'
    >>> odtfile.data[0]
    array([1500.0, 1500.2, ...])
    """

    def __init__(self, filename):
        super(ODTReader, self).__init__(filename)
#    
#    @property
#    def wellname(self):
#        return self.header["W"]["WELL"]["DATA"]
#    
    @property
    def curvesnames(self):
        return [line['MNEM'] for line in self.header["C"].itervalues()]
#    
    @property
    def curvesunits(self):
        return [line['UNIT'] for line in self.header["C"].itervalues()]
#
#    @staticmethod    
#    def _splitline(line):
#        """
#        Split a ODT line in MNEM, UNITS, DATA and DESCRIPTION.
#        
#        Parameters
#        ----------
#        line : str
#            A non-comment ODT line.
#        
#        Returns
#        -------
#        mnem : str
#            Mnemoic part of the line
#        unit : str
#            Unit part of the line
#        data : str
#            Data part of the line
#        desc : str
#            Description part of the line
#        
#        Notes
#        -----
#        This method doesn't remove whitespaces from the line parts.
#        
#        Examples
#        --------
#        >>> ODTReader._splitline('  DEPTH.M       : MEASURED DEPTH  ')
#        ('  DEPTH', 'M', '       ', ' MEASURED DEPTH  ')
#        """
#        mnem, rest = line.split(".", 1)
#        unit, rest = rest.split(" ", 1)
#        rest = " " + rest
#        data, desc = rest.rsplit(":", 1)
#        return mnem, unit, data, desc
#    
#    @staticmethod    
#    def _getlinelayout(splittedline):
#        """
#        Obtain the layout, i.e. the whitespace structure, of a splitted line.
#        
#        Parameters
#        ----------
#        splittedline : list
#            Contains the four parts of a ODT line with the whitespaces, i.e.
#            the return of the `_splitline` method
#        
#        Returns
#        -------
#        layout : list
#            A list of 6 ints, in which each element correspond to the lenght of 
#            a string of whitespaces in the line. The elements of the list are,
#            respectively, the number of whitespaces between the beginning of
#            the line and the beginning of the mnem, the end of mnem and the
#            first dot, the end of the unit and the beginning of the data, the
#            end of the data and the colon, the colon and the beginning of the
#            description and the end of the description and the end of the line.
#        
#        Examples
#        --------
#        >>> splittedline = ODTReader._splitline(
#                '  DEPTH.M       : MEASURED DEPTH  ')
#        >>> ODTReader._getlinelayout(splittedline)
#        [2, 0, 7, 0, 1, 2]
#        """
#        mnem, unit, data, desc = splittedline
#        layout = []
#        lmnem = mnem.lstrip()
#        ldata = data.lstrip()
#        ldesc = desc.lstrip()
#        layout.append(len(mnem) - len(lmnem))
#        layout.append(len(lmnem) - len(lmnem.rstrip()))
#        layout.append(len(data) - len(ldata))
#        layout.append(len(ldata) - len(ldata.rstrip()))
#        layout.append(len(desc) - len(ldesc))
#        layout.append(len(ldesc) - len(ldesc.rstrip()))
#        return layout
#
#    @staticmethod        
#    def _parseline(line, withlayout=False):
#        """
#        Parse a ODT line in its components and, if specified, its layout.
#        
#        Parameters
#        ----------
#        line : str
#            A non-comment ODT line.
#        withlayout : bool, optional
#            Whether the layout must be returned.
#        
#        Returns
#        -------
#        parsedline : dict
#            A dictionary consisting of the 4 elements of a ODT line, with keys
#            "MENM", "UNIT", "DATA" and "DESC".
#        layout : list
#            A list of 6 ints, in which each element correspond to the lenght of 
#            a string of whitespaces in the line.
#        
#        Examples
#        --------
#        >>> parsedline, layout = ODTReader._parseline(
#                '  DEPTH.M       : MEASURED DEPTH  ', True)
#        >>> parsedline
#        {'DATA': '', 'DESC': 'MEASURED DEPTH', 'MNEM': 'DEPTH', 'UNIT': 'M'}
#        >>> layout
#        [2, 0, 7, 0, 1, 2]
#        """
#        mnem, unit, data, desc = ODTReader._splitline(line)
#        parsedline = {}
#        parsedline["MNEM"] = mnem.strip()
#        parsedline["UNIT"] = unit.strip()
#        parsedline["DATA"] = data.strip()
#        parsedline["DESC"] = desc.strip()
#        if not withlayout:
#            return parsedline
#        else:
#            layout = ODTReader._getlinelayout((mnem, unit, data, desc))
#            return parsedline, layout

#    @staticmethod    
    def _getheaderlines(fileobject):
#        """
#        Obtain the ODT header lines from a file object.
#        
#        Parameters
#        ----------
#        fileobject : file-like object
#            The file object from which the header lines will be obtained.
#        
#        Returns
#        -------
#        headerlines : list
#            A list containing the lines that belong to a ODT file header.
#        """
        fileobject.seek(0)
        fileheader = []
        headerlines = []
#        line = ''
#        line = fileobject.readline()
#        while not line.startswith('!'):
#            headerlines.append(line.replace('\t', ' '))  # TODO: Suportar vários tipos de separadores
#            line = fileobject.readline()
#        headerlines.append(line)
#        while not line.startswith('!'):
#            line = fileobject.readline()
#        line = fileobject.readline()
#        while not line.startswith('!'):
#            headerlines.append(line)
#            line = fileobject.readline()
#        return headerlines
        
        line = odt_file.readline()
        while not line.startswith('!'):
            fileheader.append(line.strip())
            line = odt_file.readline()
        line = odt_file.readline()
        while not line.startswith('!'):
            headerlines.append(line.strip())
            line = odt_file.readline()
        return headerlines
    
#    @staticmethod
#    def _getheader(headerlines, withsectionnames=False, withlayout=False, withcomments=False):
#        """
#        Obtain the ODT header from a list of lines.
#        
#        Parameters
#        ----------
#        headerlines : list
#            A list containing the lines that belong to a ODT file header, i.e.
#            the return of `_getheaderlines` method.
#        withsectionnames : bool, optional
#            Whether to return the ODT section names.
#        withlayout : bool, optional
#            Whether to return the ODT header layout.
#        withcomments : bool, optional
#            Whether to return the ODT header comments.
#        
#        Returns
#        -------
#        header : OrderedDict
#            Header of a ODT file. Each section of the header is a value in the
#            dictionary. The key of each section is its capitalized first letter
#            (e.g. "V" for VERSION section). Each section is also an
#            OrderedDict, in which the keys are the mnems of the lines and the
#            lines themselves are the values. The lines are dicts with 4 keys:
#            "MNEM", "UNIT", "DATA" and "DESC".
#        sectionnames : dict
#            Names of the header sections. The keys are the capitalized first
#            letters of each section and the values are the full section names.
#        layout : dict
#            Layout of the header. Similar to `header`, but instead of the
#            lines, contains the layout of the line.
#        comments : dict
#            Comments in the ODT header. The keys are the linenumber of the
#            comment and the values are the comments themselves.
#        
#        See Also
#        --------
#        _getlinelayout : Obtain the line layout.
#        """
#        header = OrderedDict()
#        sectionnames = {}
#        comments = {}
#        layout = {}
#        currentsection = None
#        linecount = 0
#    
#        for line in headerlines:
#            if not line:
#                continue
#            elif line.lstrip().startswith('#'):
#                comments[linecount] = line.split('\n')[0]
#            elif line.lstrip().startswith('~'):
#                currentsection = []
#                sectionname = line.split('\n')[0]
#                sectionkey = sectionname.split('~')[1][0].upper()
#                header[sectionkey] = currentsection
#                sectionnames[sectionkey] = sectionname
#            else:
#                currentsection.append(line.split('\n')[0])
#            linecount += 1
#    
#        for sectionkey, lines in header.iteritems():
#            try:
#                section = OrderedDict()
#                sectionlayout = {}
#                for line in lines:
#                    parsedline, linelayout = ODTReader._parseline(line, True)
#                    
#                    # if parsedline['MNEM'] in section:
#                        # print "Curva repetida:", parsedline['MNEM']  # TODO: Fazer algo
#                    # section[parsedline['MNEM']] = parsedline
#                    # sectionlayout[parsedline['MNEM']] = linelayout
#                    
#                    # TODO: Melhorar e ver se funcionou
#                    old_mnem = parsedline['MNEM']
#                    new_mnem = old_mnem
#                    count = 0
#                    while new_mnem in section:
#                        print "Nome de curva repetido:", new_mnem
#                        count += 1
#                        new_mnem = old_mnem + '_{:0>4}'.format(count)
#                        print "Substituindo por:", new_mnem
#                    #
#
#                    section[new_mnem] = parsedline
#                    sectionlayout[new_mnem] = linelayout
#                    
#                if not section:
#                    header[sectionkey] = ''
#                else:
#                    header[sectionkey] = section
#                    layout[sectionkey] = sectionlayout
#            except:
#                header[sectionkey] = '\n'.join(lines)
#    
#        if (not withsectionnames) and (not withlayout) and (not withcomments):
#            return header
#        else:
#            returns = (header,)
#            if withsectionnames:
#                returns += (sectionnames,)
#            if withlayout:
#                returns += (layout,)
#            if withcomments:
#                returns += (comments,)
#            return returns
#    
#    @staticmethod
#    def _getdatalines(fileobject):
#        """
#        Obtain the ODT ASCII section lines from a file object.
#        
#        Parameters
#        ----------
#        fileobject : file-like object
#            The file object from which the data lines will be obtained.
#        
#        Returns
#        -------
#        datalines : list
#            A list containing the lines that belong to a ODT file ASCII
#            section.
#        """
#        fileobject.seek(0)
#        line = fileobject.readline()
#        while not line.lstrip().startswith('~A'):
#            line = fileobject.readline()
#        datalines = fileobject.readlines()
#        return datalines
#    
#    @staticmethod
#    def _getflatdata(datalines):
#        """
#        Obtain a flat `numpy.ndarray` from a list of data lines.
#        
#        Concatenate the lines; split the resulting string, convert each element
#        to float and convert to a `numpy.ndarray`.
#        
#        Parameters
#        ----------
#        datalines : list
#            A list containing the lines that belong to a ODT file ASCII
#            section.
#        
#        Returns
#        -------
#        flatdata : numpy.ndarray
#            A flat (i.e. one-dimensional) array containing data from
#            `datalines`.
#        """
#        flatdata = np.asarray([float(a) for a in ' '.join(datalines).split()])
#        return flatdata
#
#    @staticmethod
#    def _reshapeflatdata(flatdata, ncurves):
#        """
#        Reshape the flat data into a 2-dimensional data.
#        
#        The reshaped data will have the same number of elements as `flatdata`
#        and first dimension with length `ncurves`. This way, `data[0]` will
#        be the data from the first curve in the file.
#        
#        Parameters
#        ----------
#        flatdata : numpy.ndarray
#            A flat (i.e. one-dimensional) array containing data from a ODT
#            file.
#        ncurves : int
#            Number of existing curves in the same file
#
#        Returns
#        -------
#        data : numpy.ndarray
#            Reshaped data with first dimension lenght equal to `ncurves`
#        """
#        data = np.reshape(flatdata, (-1, ncurves)).T
#        return data
#    
#    @staticmethod
#    def _replacenullvalues(data, nullvalue, copy=False):
#        """
#        Replace null values in an array with `np.nan`.
#        
#        Parameters
#        ----------
#        data : np.ndarray
#            Array containing null values to be replaced.
#        nullvalue : float
#            The value that will be replaced by `np.nan`.
#        copy : bool, optional
#            Whether the operation will be performed in a copy of the data or
#            in the data itself.
#        
#        Returns
#        -------
#        newdata : np.ndarray
#            A array with `nullvalue` replaced with `np.nan`.
#        """
#        if copy:
#            newdata = np.copy(data)
#        else:
#            newdata = data
#        where = (newdata == nullvalue)
#        newdata[where] = np.nan
#        return newdata
#    
#    @staticmethod
#    def _reorderdata(data, copy=False):
#        """
#        Reorder the data so that the first line is in ascending order.
#        
#        This method suposes that the first line of `data` is already sorted
#        in descending order. It will invert the order of the rows in the array,
#        i.e. the last row will become the first, the second last will become
#        the second and so on.
#        
#        Parameters
#        ----------
#        data : np.ndarray
#            The array that will be reordered.
#        copy : bool, optional
#            Whether the operation will be performed in a copy of the data or
#            in the data itself.
#        
#        Returns
#        -------
#        newdata : np.ndarray
#            A array with the rows in reverse order.
#        """
#        if copy:
#            newdata = np.copy(data)
#        else:
#            newdata = data
#
#        return newdata[:, ::-1]
    
    def read(self):
#        print 'reader'
        odt_file = builtins.open(self.filename, 'r')
        
        odt_file.seek(0)
        headerlines = []
        dept = np.empty(0)
        value=np.empty(0)
#        line = ''
        headerlines = ODTReader._getheaderlines(fileobject)
#        print 'reader2'
        #for line in lines:
        #    headerlines.append(line)
        #print lines.find('!')
        #dados = lines.split('!')
        line = odt_file.readline()
        while not line.startswith('!'):
            self.fileheader.append(line.strip())
            line = odt_file.readline()
        line = odt_file.readline()
        while not line.startswith('!'):
            headerlines.append(line.strip())
            line = odt_file.readline()
#        print 'reader3'    
        data = odt_file.readlines()
        for i in data:
            dep,val = i.split('\t')
#            dept.append(float(dep))
#            value.append(float(val.strip()))
            if float(val.strip()) == 1e30:
                val = np.nan
            else:
                val = float(val.strip())
            dept = np.insert(dept, len(dept), round(float(dep),2))
            value = np.insert(value, len(value), val)
            
    #    print value
#        print 'reader4'    
#        dept = [float(x) for x in dept]
#        value = [float(x) for x in value]
#        value = np.asarray(value)
        return headerlines, dept, value

    def LogHeader (self, headerlist):
        
        for i in headerlist:
            label, info = i.strip().split(':')
            self.logheader [label] = info
        try:
            self.logheader['Unit of Measure']
        except:
            self.logheader['Unit of Measure'] = ''
#        for i in headerlist:
        self.curvenames = (self.logheader['Name'])
        self.curveunits = (self.logheader['Unit of Measure'])
#        print self.curvenames, self.curveunits
    

def open(name, mode='r'):
    """
    Create a new ODTFile instance.
    
    Parameters
    ----------
    name : str
        The file name.
    mode : {'r', 'w'}, optional
        The mode in which the file will be opened. If 'r' a ODTReader object
        is created; if 'w' a ODTWriter is created instead.
    
    Returns
    -------
    odtfile : ODTFilee 
        A ODTFile object. The actual return type depends on `mode`
    
    Note
    ----
    This function does not work the same way as the builtin `open` function
    since the ODTFile is not a file-like object, despite its name.
    """
    if mode == 'r':
        odtfile = ODTReader(name)
#    elif mode == 'w':
#        odtfile = ODTWriter(name)
    else:
        odtfile = None
    
    return odtfile
  
if __name__ == '__main__':
#    print os.getcwd()
#    headerlines = ODTReader("1RJS-0074--RJ-^1.wll")
    odt_file = ODTReader("C:\\Users\\Tabelini\\Dropbox\\Python\\opendetect_export.wll")
#print 'odt', odt_file    
    headerlines, dept, value = odt_file.read()
    odt_file.LogHeader (headerlines)
    print odt_file.curvenames
    