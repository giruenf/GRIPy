# -*- coding: utf-8 -*-
"""
LAS
===

This file defines the classes and functions necessary to read and write LAS
Version 2.0 [1]_ files.

References
----------
.. [1] LAS Version 2.0:
    http://www.cwls.org/wp-content/uploads/2014/09/LAS_20_Update_Jan2014.pdf
"""


import numpy as np
from collections import OrderedDict

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

_VERBOSE = False


class LASFile(object):
    """
    A LAS 2.0 file object.
    
    Parameters
    ----------
    filename : str
        File name

    Attributes
    ----------
    filename : str
        File name.
    header : OrderedDict
        Header of the file. Each section of the LAS header is a value in the
        dictionary. The key of each section is its capitalized first letter
        (e.g. "V" for VERSION section). Each section is also an OrderedDict, in
        which the keys are the mnems of the lines and the lines themselves are
        the values. The lines are dicts with 4 keys: "MNEM", "UNIT", "DATA" and
        "DESC".
    headersectionnames : dict
        Names of the header sections. The keys are the capitalized first
        letters of each section and the values are the full section names.
    headerlayout : dict
        Layout of the header. Similar to `header`, but instead of the lines,
        contains the layout of the line. The layout of a line is a list of 6
        ints, representing the number of whitespaces in the line. The elements
        of the list are, respectively, the number of whitespaces between the
        beginning of the line and the beginning of the mnem, the end of mnem
        and the first dot, the end of the unit and the beginning of the data,
        the end of the data and the colon, the colon and the beginning of the
        description and the end of the description and the end of the line.
    headercomments : dict
        Comments in the LAS header. The keys are the linenumber of the comment
        and the values are the comments themselves.
    data : numpy.ndarray
        The data present in the ASCII section of the LAS file. The data shape
        is nc x ns, where nc is the number of curves and ns is the
        number of samples.
    """
    
    def __init__(self, filename):
        self.filename = filename
        self.header = OrderedDict()
        self.headersectionnames = {}
        self.headerlayout = {}
        self.headercomments = {}
        self.data = np.empty(0)


class LASReader(LASFile):
    """
    A specialization of `LASFile` for reading files.
    
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
    When creating a `LASReader` object the file is not read immediately. The
    `read` method must be called after the creation. Once it is called, all
    of its attributes will be read from the file and the file will be closed.
    
    Examples
    --------
    >>> lasfile = LASReader("filename.las")
    >>> lasfile.read()
    >>> lasfile.wellname
    'wellname'
    >>> lasfile.curvesnames
    ['curve01name', 'curve02name', ...]
    >>> lasfile.header["V"]["VERSION"]["DATA"]
    '2.0'
    >>> lasfile.data[0]
    array([1500.0, 1500.2, ...])
    """

    def __init__(self, filename):
        super(LASReader, self).__init__(filename)
    
    @property
    def wellname(self):
        return self.header["W"]["WELL"]["DATA"]
    
    @property
    def curvesnames(self):
        return [line['MNEM'] for line in self.header["C"].itervalues()]
    
    @property
    def curvesunits(self):
        return [line['UNIT'] for line in self.header["C"].itervalues()]

    @staticmethod    
    def _splitline(line):
        """
        Split a LAS line in MNEM, UNITS, DATA and DESCRIPTION.
        
        Parameters
        ----------
        line : str
            A non-comment LAS line.
        
        Returns
        -------
        mnem : str
            Mnemoic part of the line
        unit : str
            Unit part of the line
        data : str
            Data part of the line
        desc : str
            Description part of the line
        
        Notes
        -----
        This method doesn't remove whitespaces from the line parts.
        
        Examples
        --------
        >>> LASReader._splitline('  DEPTH.M       : MEASURED DEPTH  ')
        ('  DEPTH', 'M', '       ', ' MEASURED DEPTH  ')
        """
        # if ":" not in line:
            # desc = ''
        # else:
            # line, desc = line.rsplit(":", 1)
            # desc = desc.strip()
        # line = line.strip()
        # if " " not in line:
            # data = ''
        # else:
            # line, data = line.rsplit(" ", 1)
            # data = data.strip()
        # line = line.strip()    
        # if "." not in line:
            # unit = ''
            # mnem = line
        # else:
            # mnem, unit = line.split(".", 1)
        # return mnem, unit, data, desc
        rest, desc = line.rsplit(":", 1)
        mnem, rest = rest.split(".", 1)
        unit, data = rest.split(" ", 1)
        
        return mnem, unit, data, desc
        
    
    @staticmethod    
    def _getlinelayout(splittedline):
        """
        Obtain the layout, i.e. the whitespace structure, of a splitted line.
        
        Parameters
        ----------
        splittedline : list
            Contains the four parts of a LAS line with the whitespaces, i.e.
            the return of the `_splitline` method
        
        Returns
        -------
        layout : list
            A list of 6 ints, in which each element correspond to the lenght of 
            a string of whitespaces in the line. The elements of the list are,
            respectively, the number of whitespaces between the beginning of
            the line and the beginning of the mnem, the end of mnem and the
            first dot, the end of the unit and the beginning of the data, the
            end of the data and the colon, the colon and the beginning of the
            description and the end of the description and the end of the line.
        
        Examples
        --------
        >>> splittedline = LASReader._splitline(
                '  DEPTH.M       : MEASURED DEPTH  ')
        >>> LASReader._getlinelayout(splittedline)
        [2, 0, 7, 0, 1, 2]
        """
        mnem, unit, data, desc = splittedline
        layout = []
        lmnem = mnem.lstrip()
        ldata = data.lstrip()
        ldesc = desc.lstrip()
        layout.append(len(mnem) - len(lmnem))
        layout.append(len(lmnem) - len(lmnem.rstrip()))
        layout.append(len(data) - len(ldata))
        layout.append(len(ldata) - len(ldata.rstrip()))
        layout.append(len(desc) - len(ldesc))
        layout.append(len(ldesc) - len(ldesc.rstrip()))
        return layout

    @staticmethod        
    def _parseline(line, withlayout=False):
        """
        Parse a LAS line in its components and, if specified, its layout.
        
        Parameters
        ----------
        line : str
            A non-comment LAS line.
        withlayout : bool, optional
            Whether the layout must be returned.
        
        Returns
        -------
        parsedline : dict
            A dictionary consisting of the 4 elements of a LAS line, with keys
            "MENM", "UNIT", "DATA" and "DESC".
        layout : list
            A list of 6 ints, in which each element correspond to the lenght of 
            a string of whitespaces in the line.
        
        Examples
        --------
        >>> parsedline, layout = LASReader._parseline(
                '  DEPTH.M       : MEASURED DEPTH  ', True)
        >>> parsedline
        {'DATA': '', 'DESC': 'MEASURED DEPTH', 'MNEM': 'DEPTH', 'UNIT': 'M'}
        >>> layout
        [2, 0, 7, 0, 1, 2]
        """
        mnem, unit, data, desc = LASReader._splitline(line)
        parsedline = {}
        parsedline["MNEM"] = mnem.strip()
        parsedline["UNIT"] = unit.strip()
        parsedline["DATA"] = data.strip()
        parsedline["DESC"] = desc.strip()
        if not withlayout:
            return parsedline
        else:
            layout = LASReader._getlinelayout((mnem, unit, data, desc))
            return parsedline, layout

    @staticmethod    
    def _getheaderlines(fileobject):
        """
        Obtain the LAS header lines from a file object.
        
        Parameters
        ----------
        fileobject : file-like object
            The file object from which the header lines will be obtained.
        
        Returns
        -------
        headerlines : list
            A list containing the lines that belong to a LAS file header.
        """
        fileobject.seek(0)
        headerlines = []
        line = fileobject.readline()
        while not line.lstrip().startswith('~A'):
            headerlines.append(line.replace('\t', ' '))  # TODO: Suportar vários tipos de separadores
            line = fileobject.readline()
        headerlines.append(line) 
        return headerlines
    
    @staticmethod
    def _getheader(headerlines, withsectionnames=False, withlayout=False, withcomments=False):
        """
        Obtain the LAS header from a list of lines.
        
        Parameters
        ----------
        headerlines : list
            A list containing the lines that belong to a LAS file header, i.e.
            the return of `_getheaderlines` method.
        withsectionnames : bool, optional
            Whether to return the LAS section names.
        withlayout : bool, optional
            Whether to return the LAS header layout.
        withcomments : bool, optional
            Whether to return the LAS header comments.
        
        Returns
        -------
        header : OrderedDict
            Header of a LAS file. Each section of the header is a value in the
            dictionary. The key of each section is its capitalized first letter
            (e.g. "V" for VERSION section). Each section is also an
            OrderedDict, in which the keys are the mnems of the lines and the
            lines themselves are the values. The lines are dicts with 4 keys:
            "MNEM", "UNIT", "DATA" and "DESC".
        sectionnames : dict
            Names of the header sections. The keys are the capitalized first
            letters of each section and the values are the full section names.
        layout : dict
            Layout of the header. Similar to `header`, but instead of the
            lines, contains the layout of the line.
        comments : dict
            Comments in the LAS header. The keys are the linenumber of the
            comment and the values are the comments themselves.
        
        See Also
        --------
        _getlinelayout : Obtain the line layout.
        """
        global _VERBOSE
        header = OrderedDict()
        sectionnames = {}
        comments = {}
        layout = {}
        currentsection = None
        linecount = 0
    
        for line in headerlines:
            if not line:
                continue
            elif line.lstrip().startswith('#'):
                comments[linecount] = line.split('\n')[0]
            elif line.lstrip().startswith('~'):
                currentsection = []
                sectionname = line.split('\n')[0]
                sectionkey = sectionname.split('~')[1][0].upper()
                header[sectionkey] = currentsection
                sectionnames[sectionkey] = sectionname
            else:
                currentsection.append(line.split('\n')[0])
            linecount += 1
        
        for sectionkey, lines in header.iteritems():
            try:
                section = OrderedDict()
                sectionlayout = {}
                for line in lines:
                    parsedline, linelayout = LASReader._parseline(line, True)
                    # if parsedline['MNEM'] in section:
                        # print "Curva repetida:", parsedline['MNEM']  # TODO: Fazer algo
                    # section[parsedline['MNEM']] = parsedline
                    # sectionlayout[parsedline['MNEM']] = linelayout
                    
                    # TODO: Melhorar e ver se funcionou
                    old_mnem = parsedline['MNEM']
                    new_mnem = old_mnem
                    count = 0
                    while new_mnem in section:
                        if _VERBOSE: print "Nome de curva repetido:", new_mnem
                        count += 1
                        new_mnem = old_mnem + '_{:0>4}'.format(count)
                        if _VERBOSE: print "Substituindo por:", new_mnem

                    section[new_mnem] = parsedline
                    sectionlayout[new_mnem] = linelayout
                    
                if not section:
                    header[sectionkey] = ''
                else:
                    header[sectionkey] = section
                    layout[sectionkey] = sectionlayout
            except:
                header[sectionkey] = '\n'.join(lines)
    
        if (not withsectionnames) and (not withlayout) and (not withcomments):
            return header
        else:
            returns = (header,)
            if withsectionnames:
                returns += (sectionnames,)
            if withlayout:
                returns += (layout,)
            if withcomments:
                returns += (comments,)
            return returns
    
    @staticmethod
    def _getdatalines(fileobject):
        """
        Obtain the LAS ASCII section lines from a file object.
        
        Parameters
        ----------
        fileobject : file-like object
            The file object from which the data lines will be obtained.
        
        Returns
        -------
        datalines : list
            A list containing the lines that belong to a LAS file ASCII
            section.
        """
        fileobject.seek(0)
        line = fileobject.readline()
        while not line.lstrip().startswith('~A'):
            line = fileobject.readline()
        datalines = fileobject.readlines()
        return datalines
    
    @staticmethod
    def _getflatdata(datalines):
        """
        Obtain a flat `numpy.ndarray` from a list of data lines.
        
        Concatenate the lines; split the resulting string, convert each element
        to float and convert to a `numpy.ndarray`.
        
        Parameters
        ----------
        datalines : list
            A list containing the lines that belong to a LAS file ASCII
            section.
        
        Returns
        -------
        flatdata : numpy.ndarray
            A flat (i.e. one-dimensional) array containing data from
            `datalines`.
        """
        flatdata = np.asarray([float(a) for a in ' '.join(datalines).split()])
        return flatdata

    @staticmethod
    def _reshapeflatdata(flatdata, ncurves):
        """
        Reshape the flat data into a 2-dimensional data.
        
        The reshaped data will have the same number of elements as `flatdata`
        and first dimension with length `ncurves`. This way, `data[0]` will
        be the data from the first curve in the file.
        
        Parameters
        ----------
        flatdata : numpy.ndarray
            A flat (i.e. one-dimensional) array containing data from a LAS
            file.
        ncurves : int
            Number of existing curves in the same file

        Returns
        -------
        data : numpy.ndarray
            Reshaped data with first dimension lenght equal to `ncurves`
            
        """
        data = np.reshape(flatdata, (-1, ncurves)).T
        return data
    
    @staticmethod
    def _replacenullvalues(data, nullvalue, copy=False):
        """
        Replace null values in an array with `np.nan`.
        
        Parameters
        ----------
        data : np.ndarray
            Array containing null values to be replaced.
        nullvalue : float
            The value that will be replaced by `np.nan`.
        copy : bool, optional
            Whether the operation will be performed in a copy of the data or
            in the data itself.
        
        Returns
        -------
        newdata : np.ndarray
            A array with `nullvalue` replaced with `np.nan`.
        """
        if copy:
            newdata = np.copy(data)
        else:
            newdata = data
        where = (newdata == nullvalue)
        newdata[where] = np.nan
        return newdata
    
    @staticmethod
    def _reorderdata(data, copy=False):
        """
        Reorder the data so that the first line is in ascending order.
        
        This method suposes that the first line of `data` is already sorted
        in descending order. It will invert the order of the rows in the array,
        i.e. the last row will become the first, the second last will become
        the second and so on.
        
        Parameters
        ----------
        data : np.ndarray
            The array that will be reordered.
        copy : bool, optional
            Whether the operation will be performed in a copy of the data or
            in the data itself.
        
        Returns
        -------
        newdata : np.ndarray
            A array with the rows in reverse order.
        """
        if copy:
            newdata = np.copy(data)
        else:
            newdata = data

        return newdata[:, ::-1]
    
    def read(self):
        """
        Read the file.
        
        Notes
        -----
        When creating a `LASReader` object the file is not read immediately.
        This method must be called after the creation. Once it is called, all
        of the instance's attributes will be read from the file and the file
        will be closed.
        """
        fileobject = builtins.open(self.filename, 'r')
        headerlines = LASReader._getheaderlines(fileobject)
        datalines = LASReader._getdatalines(fileobject)
        fileobject.close()
        
        self.header, self.headersectionnames, self.headerlayout, self.headercomments = LASReader._getheader(headerlines, True, True, True)
        ncurves = len(self.header["C"])
        nullvalue = float(self.header["W"]["NULL"]["DATA"])
        stepvalue = float(self.header["W"]["STEP"]["DATA"])
        
        flattendata = LASReader._getflatdata(datalines)
        nandata = LASReader._replacenullvalues(flattendata, nullvalue)
        self.data = LASReader._reshapeflatdata(nandata, ncurves)
        
        if (stepvalue == nullvalue) or (stepvalue == 0.0):
            stepvalue = self.data[0][1] - self.data[0][0]
        
        if stepvalue < 0:
            self.data = LASReader._reorderdata(self.data)
        
        
class LASWriter(LASFile):
    """
    A specialization of `LASFile` for writing files.
    
    Notes
    -----
    When creating a `LASReader` object the file is not written immediately. The
    `header` and `data` attributes must be defined before calling the `write`
    method. The other attributes (`headersectionnames`, `headerlayout` and
    `headercomments`) are optional.
    
    No verification is done to guarantee that the header and data are
    compatible (i.e. have the same number of curves and the same depth range).
    There are two methods that can be used for this: `correctwellsection` and
    `correctcurvesection`.
    
    In order to get a better layout for the header, the method
    `getprettyheaderlayout` may be used.
    
    Examples
    --------
    >>> lasfile = LASWriter("filename.las")
    >>> lasfile.header = existing_header
    >>> lasfile.data = existing_data
    >>> lasfile.write()
    """
    
    DEFAULTMNEMSTYLE = {'leftmargin': 1, 'rightmargin': 0, 'allign': 'left'}
    DEFAULTDATASTYLE = {'leftmargin': 1, 'rightmargin': 1, 'allign': 'left'}
    DEFAULTDESCSTYLE = {'leftmargin': 1, 'righmargin': 0, 'allign': 'left'}
    DEFAULTUNIFORMSECTIONS = True
    
    MINIMALLINELAYOUT = [0,0,1,0,0,0]
    LASLINEPATTERN = "{0[0]}{MNEM}{0[1]}.{UNIT}{0[2]}{DATA}{0[3]}:{0[4]}{DESC}{0[5]}"
    
    def __init__(self, filename):
        super(LASWriter, self).__init__(filename)
    
    @staticmethod
    def _composeline(parsedline, linelayout=None):
        """
        Turn a LAS parsed line into a one-string-line.
        
        Parameters
        ----------
        parsedline : dict
            A LAS parsed line, i.e. a dict with keys "MNEM", "UNIT", "DATA"
            and "DESC" which values are the respective LAS line parts.
        linelayout : list, optional
            A list containing 6 ints, each representing the number of
            whitespaces in a portion of the LAS line. If not provided a minimal
            layout will be used.
        
        Returns
        -------
        line : str
            A line composed using the `parsedline` parts and `linelayout`
            whitespaces.
        
        Examples
        --------
        >>> parsedline = {'DATA': '', 'DESC': 'MEASURED DEPTH',
                          'MNEM': 'DEPTH','UNIT': 'M'}
        >>> layout = [2, 0, 7, 0, 1, 2]
        >>> LASWriter._composeline(parsedline, linelayout)
        '  DEPTH.M       : MEASURED DEPTH  '
        """
        if not linelayout:
            linelayout = LASWriter.MINIMALLINELAYOUT

        line = LASWriter.LASLINEPATTERN.format([" "*n for n in linelayout], **parsedline)
        return line
    
    @staticmethod
    def _getspaces(style, spaces):
        """
        Return the number of left and right whitespaces in a LAS line element.
        
        Here LAS line element refers to either the MNEM, DATA or DESCRIPTION
        part of a LAS line (the UNIT part cannot have whitespaces). The
        distribution of whitespaces will be done according to `style`.
        
        Parameters
        ----------
            style : dict
                A dictionary contaning the style parameters of a LAS line
                element. The possible style parameters are 'allign',
                'leftmargin' and 'rightmargin'. All of them are optional. If
                'allign' is not provided, the other parameters are not used.
                'allign' can be 'left', 'center' or 'right' and describes the
                allignment of the LAS line element. 'leftmargin' and
                'rightmargin' are the number of extra whitespaces to the left
                or to the right of the line element, respectively.
            spaces : int
                Number of whitespaces to be distributed between `right` and
                `left`.
        
        Returns
        -------
            left : int
                Number of whitespaces to the left of the LAS line element.
            right : int
                Number of whitespaces to the right of the LAS line element.
        """
        if style.get('allign') == 'left':
            left = style.get('leftmargin', 0)
            right = style.get('rightmargin', 0) + spaces
        elif style.get('allign') == 'center':
            left = style.get('leftmargin', 0) + spaces//2
            right = style.get('rightmargin', 0) + (spaces + 1)//2
        elif style.get('allign') == 'right':
            left = style.get('leftmargin', 0) + spaces
            right = style.get('rightmargin', 0)
        else:
            left = style.get('leftmargin', 0)
            right = style.get('rightmargin', 0)
        return left, right
    
    @staticmethod
    def getprettyheaderlayout(header, mnemstyle=None, datastyle=None, descstyle=None, uniformsections=None):
        """
        Obtain a 'pretty' header layout from a header and style parameters.
        
        The layout will be constructed using the lenghts of the line elements
        of each line in each section of the header.
        
        Parameters
        ----------
        header : OrderedDict
            The LAS header for which the layout will be created.
        mnemstyle : dict, optional
            A dictionary containing the style parameters for the MNEM part of
            the LAS line. The possible style parameters are 'allign',
            'leftmargin' and 'rightmargin'. If not given, a default style will
            be used.
        datastyle : dict, optional
            Same as `mnemstyle`, but for the DATA part instead.
        descstyle : dict, optional
            Same as `mnemstyle`, but for the DESCRIPTION part instead.
        uniformsections : bool, optional
            If True, the line elements will have the same lenght across all
            sections of the header.
        
        Returns
        -------
        headerlayout : dict
            The pretty header layout that will fit the provided header.
        """
        if mnemstyle is None:
            mnemstyle = LASWriter.DEFAULTMNEMSTYLE
        if datastyle is None:
            datastyle = LASWriter.DEFAULTDATASTYLE
        if descstyle is None:
            descstyle = LASWriter.DEFAULTDESCSTYLE
        if uniformsections is None:
            uniformsections = LASWriter.DEFAULTUNIFORMSECTIONS
        
        style = {}
        style["MNEM"] = mnemstyle
        style["DATA"] = datastyle
        style["DESC"] = descstyle
        
        allignmnem = bool(style["MNEM"].get('allign'))
        alligndata = bool(style["DATA"].get('allign'))
        alligndesc = bool(style["DESC"].get('allign'))
        
        sizearrays = {}
        for sectionkey, section in header.iteritems():
            if isinstance(section, basestring) or not section:
                continue
            sizearray = {}
            for key in ("MNEM", "UNIT", "DATA", "DESC"):
                sizearray[key] = np.array([len(line[key]) for line in section.itervalues()])
            sizearrays[sectionkey] = sizearray
        
        usizearray = {}
        for key in ("MNEM", "UNIT", "DATA", "DESC"):
            usizearray[key] = np.hstack(sizearray[key] for sizearray in sizearrays.itervalues())
        
        leftpositions = {}
        for sectionkey, section in header.iteritems():
            if isinstance(section, basestring) or not section:
                continue
            leftposition = {}
            
            sizearray = sizearrays[sectionkey]
            
            if uniformsections:
                msizearray = usizearray
            else:
                msizearray = sizearray
            
            mnemleft = np.zeros(len(section))
            
            if not alligndata:
                dataleft = np.zeros(len(section))
            else:
                if allignmnem:
                    size = sizearray['UNIT']
                    maxsize = np.max(msizearray['UNIT'])
                else:
                    size = sizearray['MNEM'] + sizearray['UNIT']
                    maxsize = np.max(msizearray['MNEM'] + msizearray['UNIT'])
                dataleft = maxsize - size
            
            if not alligndesc or alligndata:
                descleft = np.zeros(len(section))
            else:
                if allignmnem:
                    size = sizearray['UNIT'] + sizearray['DATA']
                    maxsize = np.max(msizearray['UNIT'] + msizearray['DATA'])
                else:
                    size = sizearray['MNEM'] + sizearray['UNIT'] + sizearray['DATA']
                    maxsize = np.max(msizearray['MNEM'] + msizearray['UNIT'] + msizearray['DATA'])
                descleft = maxsize - size
                
            leftposition["MNEM"] = mnemleft
            leftposition["DATA"] = dataleft
            leftposition["DESC"] = descleft
            
            leftpositions[sectionkey] = leftposition
        
        headerlayout = {}
        for sectionkey, section in header.iteritems():
            if isinstance(section, basestring) or not section:
                continue
            
            sectionlayout = {}
            if uniformsections:
                msizearray = usizearray
            else:
                msizearray = sizearrays[sectionkey]
            for i, line in enumerate(section.itervalues()):
                linelayout = []
                for key in ("MNEM", "DATA", "DESC"):
                    spaces = np.max(msizearray[key]) - len(line[key])
                    left, right = LASWriter._getspaces(style[key], spaces)
                    left += leftpositions[sectionkey][key][i]
                    linelayout.append(left)
                    linelayout.append(right)
                sectionlayout[line["MNEM"]] = linelayout
            headerlayout[sectionkey] = sectionlayout
        
        return headerlayout
    
    @staticmethod
    def getemptyheader():
        """
        Return an empty LAS header.
        
        Returns
        -------
        emptyheader : OrderedDict
            An empty LAS header.
        """
        pass  # TODO: implementar
    
    @staticmethod
    def correctwellsection(header, depthdata, depthunit, copy=False):
        """
        Correct the Well Info section of the header based on the depth data.
        
        The correction consists basically in obtaining the correct STRT, STOP
        and STEP parameters from the provided depth data.
        
        Parameters
        ----------
        header : OrderedDict
            The LAS header which Well Info section will be corrected.
        depthdata : numpy.ndarray
            The data of the depth "curve".
        depthunit : str
            The unit in which `depthdata` was measured.
        copy : bool, optional
            Whether the correction will be done in a copy of `header` or in
            `header` itself.
        
        Returns
        -------
        hdr : OrderedDict
            A LAS header with corrected Well Info section.
        """
        if copy:
            hdr = header.copy()
        else:
            hdr = header

        start = depthdata[0]
        stop = depthdata[-1]
        steps = depthdata[1:] - depthdata[:-1]
        if np.equal(steps, steps[0]).all():
            step = steps[0]
        else:
            step = 0
        hdr["W"]["STRT"]["UNIT"] = depthunit
        hdr["W"]["STRT"]["DATA"] = "{:g}".format(start)
        hdr["W"]["STOP"]["UNIT"] = depthunit
        hdr["W"]["STOP"]["DATA"] = "{:g}".format(stop)
        hdr["W"]["STEP"]["UNIT"] = depthunit
        hdr["W"]["STEP"]["DATA"] = "{:g}".format(step)
        
        return hdr
    
    @staticmethod
    def correctcurvesection(header, mnems, units, keep=False, copy=False):
        """
        Correct the Curve Info section of the header.
        
        After the creation and deletion of curves the information existing in
        the header will unlikely be suitable to the data. This method will
        correct the Curve Info section, so that the header will use the
        provided mnems and units.
        
        Parameters
        ----------
        header : OrderedDict
            The LAS header which Curve Info section will be corrected.
        mnems : list
            The mnems of the curves that will exist in the header Curve Info
            section.
        units : list
            The units of the curves that will exist in the header Curve Info
            section.
        keep : bool, optional
            Whether only the necessary parts of the header will be corrected
            or it will be built from the ground up.
        copy : bool, optional
            Whether the correction will be done in a copy of `header` or in
            `header` itself.
        
        Returns
        -------
        hdr : OrderedDict
            A LAS header with corrected Curve Info section.
        """
        if copy:
            hdr = header.copy()
        else:
            hdr = header
        if keep:
            toremove = [key for key in hdr if key not in mnems]
            for key in toremove:
                del hdr[key]
            for name, unit in zip(mnems, units):
                if name in hdr["C"]:
                    hdr["C"][name]["UNIT"] = unit
                    hdr["C"][name] = hdr["C"].pop(name)  # Para manter a mesma ordem de names
                else:
                    hdr["C"][name] = {"MNEM": name, "UNIT": unit, "DATA": "", "DESC": ""}
        else:
            hdr["C"].clear()
            for name, unit in zip(mnems, units):
                hdr["C"][name] = {"MNEM": name, "UNIT": unit, "DATA": "", "DESC": ""}
        return hdr
    
    @staticmethod
    def _headertostring(header, sectionnames=None, layout=None, comments=None):
        """
        Convert the given LAS header to a string ready for writing into a file.
        
        Parameters
        ----------
        header : OrderedDict
            The header to convert into a string.
        sectionnames : dict, optional
            A dictionary with section names capitalized first letter as keys
            and full section names as values. For example, ``sectionnames["V"]
            = "VERSION INFORMATION SECTION"``. If not provided the capitalized
            first letter will be used as the full section name.
        layout : dict, optional
            Similar to header, but instead of the lines themselves it contains
            the layout of each line. If not given a minimal layout will be
            used.
        comments : dict, optional
            A dictinary which keys are the line numbers of the comment lines
            and values are the comment lines themselves. If not given no
            comment will be placed in the header string.
        
        Returns
        -------
        string : str
            A string containing all the header lines separated by '\\n'.
        """
        lines = []
        
        if not sectionnames:
            sectionnames = {}
            for key in header.iterkeys():
                sectionnames[key] = '~' + key
        
        if not layout:
            layout = {}
            for key in header.iterkeys():
                layout[key] = {}.fromkeys(header[key])
        
        if not comments:
            comments = {}
        
        for sectionkey, section in header.iteritems():
            while len(lines) in comments:
                lines.append(comments[len(lines)])
            if not section:
                continue
            lines.append(sectionnames[sectionkey])
            if isinstance(section, basestring):
                for line in section.split('\n'):
                    while len(lines) in comments:
                        lines.append(comments[len(lines)])
                    lines.append(line)
            else:
                for key, line in section.iteritems():
                    while len(lines) in comments:
                        lines.append(comments[len(lines)])
                    linelayout = layout[sectionkey][key]
                    lines.append(LASWriter._composeline(line, linelayout))
        while len(lines) in comments:
            lines.append(comments[len(lines)])
        lines.append(sectionnames["A"])

        string = '\n'.join(lines)
        return string
    
    @staticmethod
    def _datatostring(data, nullvalue=-999.25, revertorder=False, wrap=False, allign='right', collumnwidth=10, maxprecision=8, copy=False):  # TODO: rever (alinhar pontos e etc)
        """
        Convert the given LAS data to a string ready for writing into a file.
        
        The data is formatted in collumns, such that the first line of `data`
        will be placed in the first column, the second line in the second
        column and so on.
        
        Parameters
        ----------
        data : np.ndarray
            The data to convert into a string.
        nullvalue : float, optional
            A value that will replace the np.nan in the returned string.
        wrap : bool, optional
            Whether the output should be wrapped. If True, the each entry of
            the first line of `data` will be alone in its line and subsequent
            lines will be limitted to 80 characters.
        allign : {'right', 'left'}, optional
            The allignment of numbers inside the columns.
        collumnwidht : int, optional
            The width of the columns in which `data` will be formatted.
        maxprecision : int, optional
            The maximum number of signicant figures in which `data` will be
            formatted.
        copy : bool, optional
            Whether the data that will be used should be a copy of `data`.

        Returns
        -------
        string : str
            A string containing `data` formatted appropriately according to the
            given parameters.
        """
        if copy:
            newdata = np.copy(data)
        else:
            newdata = data
        
        if revertorder:
            newdata = newdata[:, ::-1]
            
        isnan = np.isnan(newdata)
        newdata[isnan] = nullvalue
        
        if allign == 'left':
            allignsymbol = '<'
        else:
            allignsymbol = '>'
        
        pattern = '{{:{}{}.{}g}}'.format(allignsymbol, collumnwidth, maxprecision)
        
        lines = []
        if wrap:
            ncolumns = 80//collumnwidth
            nrows = (newdata.shape[0] - 1)//ncolumns
            nrest = (newdata.shape[0] - 1) % ncolumns
            linepattern = pattern*ncolumns
            restpattern = pattern*nrest
            for line in newdata.T:
                lines.append(pattern.format(line[0]))
                for i in range(nrows):
                    lines.append(linepattern.format(*line[1+i*ncolumns:1+(i+1)*ncolumns]))
                lines.append(restpattern.format(*line[1+nrows*ncolumns:]))
        else:
            linepattern = pattern*newdata.shape[0]
            for line in newdata.T:
                lines.append(linepattern.format(*line))
        
        string = '\n'.join(lines)
        return string
    
    def write(self):
        """
        Write the file.
        
        Notes
        -----        
        When creating a `LASReader` object the file is not written immediately.
        The `header` and `data` attributes must be defined before calling the
        `write` method. The other attributes (`headersectionnames`,
        `headerlayout` and `headercomments`) are optional.
        
        No verification is done to guarantee that the header and data are
        compatible (i.e. have the same number of curves and the same depth
        range). There are two methods that can be used for this:
        `correctwellsection` and `correctcurvesection`.
        
        Calling this method may modify `header` and `data` attributes.
        """
        headerstring = LASWriter._headertostring(self.header, self.headersectionnames, self.headerlayout, self.headercomments)
        
        nullvalue = float(self.header["W"]["NULL"]["DATA"])
        stepvalue = float(self.header["W"]["STEP"]["DATA"])
        revertorder = (stepvalue != nullvalue) and (stepvalue < 0)
        wrap = self.header["V"]["WRAP"]["DATA"].upper().startswith("Y")
        
        datastring = LASWriter._datatostring(self.data, nullvalue, revertorder, wrap)
        
        fileobject = builtins.open(self.filename, 'w')
        fileobject.write(headerstring)
        fileobject.write('\n')
        fileobject.write(datastring)
        fileobject.close()
                

def open(name, mode='r'):
    """
    Create a new LASFile instance.
    
    Parameters
    ----------
    name : str
        The file name.
    mode : {'r', 'w'}, optional
        The mode in which the file will be opened. If 'r' a LASReader object
        is created; if 'w' a LASWriter is created instead.
    
    Returns
    -------
    lasfile : LASFile
        A LASFile object. The actual return type depends on `mode`
    
    Note
    ----
    This function does not work the same way as the builtin `open` function
    since the LASFile is not a file-like object, despite its name.
    """
    if mode == 'r':
        lasfile = LASReader(name)
    elif mode == 'w':
        lasfile = LASWriter(name)
    else:
        lasfile = None
    
    return lasfile

def verbose(v=True):
    global _VERBOSE
    _VERBOSE = v
