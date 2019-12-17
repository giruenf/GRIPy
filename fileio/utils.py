from collections import OrderedDict

import numpy as np

from basic.parms import ParametersManager


def clean_path_str(path):
    path = path.replace('\\', '/')
    path = path.encode('ascii', 'ignore')  # in order to save unicode characters
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
            print(line)
            file_.write(' '.join(line) + '\n')
    file_.close()


def create_empty_file(fullfilename):
    fullfilename = clean_path_str(fullfilename)
    return open(fullfilename, 'w')


class Base(object):

    def __init__(self):
        self._data = []

    def __len__(self):
        return len(self._data)

    def _test_inner_instance(self, obj):
        raise NotImplementedError('Must be implemented by subclass.')

    @property
    def data(self):
        return self._data

    def append(self, obj):
        self._test_inner_instance(obj)
        self._data.append(obj)

    def add(self, index, obj):
        self._test_inner_instance(obj)
        self._data.insert(index, obj)

    def get(self, pos):
        return self._data[pos]


class IOWells(Base):

    def __init__(self):
        super().__init__()

    def _test_inner_instance(self, obj):
        if not isinstance(obj, IOWell):
            raise Exception('Object [{}] is not instance of IOWell.'.format(type(obj)))


class IOWell(Base):

    def __init__(self):
        super().__init__()
        self.name = None
        self.infos = None
        self._import = False

    def _test_inner_instance(self, obj):
        if not isinstance(obj, IOWellRun):
            raise Exception('Object [{}] is not instance of IOWellRun.'.format(type(obj)))

    def _get_run_name(self):
        return "Run {:03d}".format(len(self.data) + 1)


class IOWellRun(Base):

    def __init__(self, name):
        super().__init__()
        self.name = name
        self._import = False

    def _test_inner_instance(self, obj):
        if not isinstance(obj, IOWellLog):
            msg = 'Object [{}] is not instance of IOWellLog.'.format(type(obj))
            raise Exception(msg)

    def get_depth(self):
        try:
            return self._data[0]
        except:
            return None
        raise NotImplementedError('Must be implemented by subclass.')

    def get_depth_unit(self):
        raise NotImplementedError('Must be implemented by subclass.')

    def get_depth_start(self):
        raise NotImplementedError('Must be implemented by subclass.')

    def get_depth_end(self):
        raise NotImplementedError('Must be implemented by subclass.')

    def get_indexes(self):
        return [datum for datum in self.data \
                if datum.tid == "data_index" and datum._import]

    def get_logs(self):
        return [datum for datum in self.data \
                if datum.tid == "log" and datum._import]


class IOWellLog(object):

    def __init__(self, mnem, unit, data):
        self.mnem = mnem
        self.unit = unit
        self.data = data
        self._import = True
        self._progress = 0
        PM = ParametersManager.get()
        try:
            self.tid = PM.get_tid_from_mnemonic(self.mnem)
        except:
            self.tid = ""
        try:
            self.datatype = PM.get_datatype_from_mnemonic(self.mnem)
        except:
            self.datatype = ""

    def get_first_occurence_pos(self):
        for idx, boolean in enumerate(np.isnan(self.data)):
            if not boolean:
                return idx

    def get_last_occurence_pos(self):
        y = np.isnan(self.data)
        for idx in range(len(y) - 1, -1, -1):
            if not y[idx]:
                return idx

            # Just a wrapper to LISModel


class IOWellInfo(object):
    def __init__(self, type_=None):
        self.type = type_
        self.data = OrderedDict()

#    def __str__(self):
#        return "LISWellInfo.type: " + str(self.type) + "\nLISWellInfo.data: " + str(self.data)
