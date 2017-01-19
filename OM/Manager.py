# -*- coding: utf-8 -*-
"""
Manager
=======

This file defines `ObjectManager`.
"""


import weakref
from collections import OrderedDict
import numpy as np
import zipfile
import os

try:
    import zlib
    compress_type = zipfile.ZIP_DEFLATED
except ImportError:
    compress_type = zipfile.ZIP_STORED

try:
    import cPickle as pickle
except ImportError:
    import pickle


# TODO: Possibilidade e a utilidade de se usar Proxys (restrição de acesso e etc)
# TODO: Receber o "dono" (utilizador) do ObjectManager no construtor, de modo a saber quem está invocando os métodos e poder restringir o acesso
# TODO: Acesso simultâneo (multiprocessing)


class ObjectManager(object):
    """
    The Object Manager.
    
    The ObjectManager is responsible for managing objects throughout the
    program execution. For instance, it is responsible for creating new objects
    and deleting them when they are no longer needed.
    
    The ObjectManager is a "Borg", i.e. all the instances of the class share
    (almost) the same state. This way, when access to a managed object is
    needed an "instance" of ObjectManager must be created in order to access
    the data.
    
    Parameters
    ----------
    owner
        The object that is instantiating a new ObjectManager.
    """
    _data = OrderedDict()
    _types = OrderedDict()
    _currentobjectids = {}
    _parentuidmap = {}
    _childrenuidmap = {}
    _parenttidmap = {}
    _CBTYPES = ["add", "pre-remove", "post-remove"]
    _callbacks = {cbtype: [] for cbtype in _CBTYPES}
    _log = []  # TODO: implementar logging (talvez usando decorators)
    _NPZIDENTIFIER = "__NPZ;;"

    def __init__(self, owner):
        self._ownerref = weakref.ref(owner)
        self._data = ObjectManager._data
        self._types = ObjectManager._types
        self._currentobjectids = ObjectManager._currentobjectids
        self._parentuidmap = ObjectManager._parentuidmap
        self._childrenuidmap = ObjectManager._childrenuidmap
        self._parenttidmap = ObjectManager._parenttidmap
        self._callbacks = ObjectManager._callbacks
        self._log = ObjectManager._log

    def _getnewobjectid(self, typeid):
        """
        Return a new object identifier for the desired type.
        
        Parameters
        ----------
        typeid : str
            The identifier for the type that a new object identifier is
            needed.
        
        Returns
        -------
        objectid : int
            A new unique object identifier for given type.
        """
        objectid = self._currentobjectids[typeid]
        self._currentobjectids[typeid] += 1
        return objectid

    def new(self, typeid, *args, **kwargs):
        """
        Create a new instance of the desired type.
        
        In this method `*args` and `**kwargs` will be passed on as arguments to
        the constructor of the new object.
        
        Parameters
        ----------
        typeid : str
            The type identificator of the new object.
        
        Returns
        -------
        obj : GenericObject
            The new object.
        
        Notes
        -----
        The new object is not automatically added to ObjectManager. The ``add``
        method must be called so that the new object can be managed.
        
        Examples
        --------
        >>> om = ObjectManager(owner)
        >>> newobj = om.new('typeid', name='nameofthenewobject')
        >>> # name will be passed to the constructor
        """
        obj = self._types[typeid](*args, **kwargs)
        objectid = self._getnewobjectid(typeid)
        obj.oid = objectid
        return obj

    def add(self, obj, parentuid=None):
        """
        Add a new instance that from now on will be managed by ObjectManager.
        
        Parameters
        ----------
        obj : GenericObject
            The object to be managed by ObjectManager.
        parentuid : uid, optional
            The unique identificator of the added object's parent. If the
            object has no parent this argument must be ommited.
        
        Returns
        -------
        bool
            Whether the operation was successful.
        
        Examples
        --------
        >>> om = ObjectManager(owner)
        >>> parentobj = om.new('parenttypeid')
        >>> om.add(parentobj)
        True
        >>> childobj = om.new('childtypeid')
        >>> om.add(childobj)
        False
        >>> om.add(childobj, parentobj.uid)
        True
        """
        if not self._isvalidparent(obj.uid, parentuid):
            return False
        self._parentuidmap[obj.uid] = parentuid
        self._childrenuidmap[obj.uid] = []
        self._data[obj.uid] = obj
        if parentuid:
            self._data[parentuid]._children[obj.uid] = obj
            self._childrenuidmap[parentuid].append(obj.uid)
        for cb in self._callbacks["add"]:
            cb(obj.uid)
        return True

    def get(self, uid):  # TODO: colocar "Raises" na docstring
        """
        Return the object which `uid` was provided.
        
        This method is the main access point for the objects that are being
        managed by ObjectManager.
        
        Parameters
        ----------
        uid : uid
            The unique identificator of the desired object.
        
        Returns
        -------
        GenericObject
            The desired object.
        
        Examples
        --------
        >>> om = ObjectManager(owner)
        >>> obj = om.new('typeid')
        >>> om.add(obj)
        True
        >>> obj2 = om.get(obj.uid)
        >>> obj2 == obj
        True
        """
        return self._data[uid]

    def remove(self, uid):
        """
        Remove the object which `uid` was provided.
        
        Parameters
        ----------
        uid : uid
            The unique identificator of the object to remove.
        
        Returns
        -------
        bool
            Whether the remove operation was successful.
        
        Examples
        --------
        >>> om = ObjectManager(owner)
        >>> obj = om.new('typeid')
        >>> om.add(obj)
        True
        >>> om.remove(obj.uid)
        True
        >>> om.get(obj.uid)
        KeyError: obj.uid
        """
        for cb in self._callbacks["pre-remove"]:
            cb(uid)
        
        for childuid in self._childrenuidmap[uid][::-1]:
            self.remove(childuid)
        
        parentuid = self._parentuidmap[uid]
        if parentuid:
            del self._data[parentuid]._children[uid]
            del self._parentuidmap[uid]
            self._childrenuidmap[parentuid].remove(uid)

        del self._childrenuidmap[uid]
        obj = self._data.pop(uid)
        del obj

        for cb in self._callbacks["post-remove"]:
            cb(uid)

        return True

    def list(self, tidfilter=None, parentuidfilter=None):
        """
        Return a list of objects being managed by `ObjectManager`.
        
        Parameters
        ----------
        tidfilter : str, optional
            Only objects which type identificator is equal to `tidfilter` will
            be returned.
        parentuidfilter : uid, optional
            Only objects which parent has unique identificator equal to
            `parentuidfilter` will be returned.
        
        Returns
        -------
        list
            A list of objects that satisfy the given filters.
        
        Examples
        --------
        >>> om = ObjectManager(owner)
        >>> parentobj = om.new('parenttypeid')
        >>> om.add(parentobj)
        True
        >>> childobj = om.new('childtypeid')
        >>> om.add(childobj, parentobj.uid)
        True
        >>> om.list()
        [parentobj, childobj]
        >>> om.list(parentuidfilter=parentobj.uid)
        [childobj]
        >>> om.list(tidfilter='parenttypeid')
        [parentobj]
        >>> om.list(parentuidfilter=parentobj.uid, tidfilter='parenttypeid')
        []
        """
        if parentuidfilter is None:
            objs = self._data.values()
            if tidfilter:
                return [obj for obj in objs if obj.tid == tidfilter]
            else:
                return objs
        else:
            return self.get(parentuidfilter).list(tidfilter)

    @classmethod
    def registertype(cls, type_, parenttype=None):
        """
        Register a type which instances are now able to be managed.
        
        Parameters
        ----------
        type_ : type
            The new type that will be registered within `ObjectManager`.
        parenttype : type, optional
            The parent type of `type_`
        
        Returns
        -------
        bool
            Whether the remove operation was successful.
        
        Examples
        --------
        >>> om = ObjectManager(owner)
        >>> obj = om.new('unregisteredtypeid', name='nameofobj')
        KeyError: 'unregisteredtypeid'
        >>> ObjectManager.registertype(UnregeristeredType)
        True
        >>> obj = om.new('unregisteredtypeid', name='nameofobj')
        >>> om.add(obj)
        True
        """
        typeid = type_.tid
        if typeid in cls._data.keys():
            msg = "Type {} is already registered".format(typeid)
            raise TypeError(msg)

        if parenttype:
            cls._parenttidmap[typeid] = parenttype.tid
        else:
            cls._parenttidmap[typeid] = None

        cls._currentobjectids[typeid] = 0
        cls._types[typeid] = type_
        
        return True

    @classmethod
    def addcallback(cls, cbtype, cb):
        """
        Add a function to the callback system.
        
        Parameters
        ----------
        cbtype : {"add", "pre-remove", "post-remove"}
            The type of the callback, i.e. the kind of action that will make
            `cb` get called.
        cb : callable
            The function that will be called when the callback is thrigerred.
            A pertinent object unique identificator will be passed to `cb`.
        
        Examples
        --------
        >>> def somefunctions(uid):
        >>>     print "Function was called!"
        >>> ObjectManager.addcallback("add", somefunction)
        >>> om = ObjectManager(owner)
        >>> obj = om.new('typeid')
        >>> om.add(obj)
        "Function was called!"
        """
        cls._callbacks[cbtype].append(cb)

    @classmethod
    def removecallback(cls, cbtype, cb):
        """
        Remove a callback from the callback system.
        
        Parameters
        ----------
        cbtype : {"add", "pre-remove", "post-remove"}
            The type of the callback, i.e. the kind of action that made `cb`
            get called.
        cb : callable
            The callback function, i.e. the function that was called when the
            callback was thrigerred.
        
        Examples
        --------
        >>> def somefunctions(uid):
        >>>     print "Function was called!"
        >>> ObjectManager.addcallback("add", somefunction)
        >>> om = ObjectManager(owner)
        >>> obj = om.new('typeid')
        >>> om.add(obj)
        "Function was called!"
        >>> ObjectManager.removecallback("add", somefunction)
        >>> obj2 = om.new('typeid')
        >>> # No function was called this time.
        
        """
        cls._callbacks[cbtype].remove(cb)
    
    def _isvalidparent(self, objuid, parentuid):
        """
        Verify if a given parent is suited for an object using their `uid`s.
        
        The verification is done by checking if the object type has the parent
        object type as its parent type.
        
        Parameters
        ----------
        objuid : uid
            The unique identificator of the object to check if the given parent
            is valid.
        parentuid : uid
            The unique identificator of the parent object to check if it is a
            valid parent for the given object.
        
        Returns
        -------
        bool
            Whether the parent is valid for the object.
        """
        objtid = objuid[0]
        if parentuid is None:
            parenttid = None
        else:
            parenttid = parentuid[0]
        return self._parenttidmap[objtid] == parenttid

    def _getparentuid(self, uid):
        """
        Return the parent unique identificator.
        
        Parameters
        ----------
        uid : uid
            The unique identificator for the object whose parent unique
            identificator is needed.
        
        Returns
        -------
        uid
            The unique identificator of the object's parent.
        """
        return self._parentuidmap[uid]

    def _gettype(self, tid):
        """
        Return the type (i.e. the class) that has the given `tid`.
        
        Parameters
        ----------
        tid : str
            The type identificator for the desired type.
        
        Returns
        -------
        type
            The type that has `tid` as its identificator.
        """
        return self._types[tid]
    
    def save(self, archivepath):
        """
        Save the current `ObjectManager` state to a file.
        
        Parameters
        ----------
        archivepath : str
            The path (i.e. the filename) of the file in which the state will
            be saved.
        
        Returns
        -------
        bool
            Whether the operation was successful.
        
        Notes
        -----
            Callbacks are not saved.
        """
        dirname, filename = os.path.split(archivepath)
        pickledata = OrderedDict()
        npzdata = {}
        for uid, obj in self._data.iteritems():
            objdict = OrderedDict()
            for key, value in obj._getstate().iteritems():
                if isinstance(value, np.ndarray):
                    npzname = "{}_{}_{}".format(uid[0], uid[1], key)
                    npzdata[npzname] = value
                    objdict[key] = self._NPZIDENTIFIER + npzname
                else:
                    objdict[key] = value
            pickledata[uid] = objdict
        
        picklefilename = filename.rsplit('.', 1)[0] + ".pkl"
        npzfilename = filename.rsplit('.', 1)[0] + ".npz"
        
        picklefile = open(os.path.join(dirname, picklefilename), 'wb')
        pickle.dump(dict(data=pickledata, parentmap=self._parentuidmap), picklefile, protocol=2)
        picklefile.close()
        
        npzfile = open(os.path.join(dirname, npzfilename), 'wb')
        np.savez_compressed(npzfile, **npzdata)
        npzfile.close()
        
        archivefile = zipfile.ZipFile(archivepath, mode='w', compression=compress_type)
        archivefile.write(os.path.join(dirname, picklefilename), arcname=picklefilename)
        archivefile.write(os.path.join(dirname, npzfilename), arcname=npzfilename)
        archivefile.close()
        
        os.remove(os.path.join(dirname, picklefilename))
        os.remove(os.path.join(dirname, npzfilename))
        
        return True

    def load(self, archivepath):
        """
        Load the state of `ObjectManager` from a previously saved file.
        
        Parameters
        ----------
        archivepath : str
            The path (i.e. the filename) of the file to load the state from.
        
        Returns
        -------
        bool
            Whether the operation was successful.
        """
        dirname, filename = os.path.split(archivepath)
        picklefilename = filename.rsplit('.', 1)[0] + ".pkl"
        npzfilename = filename.rsplit('.', 1)[0] + ".npz"
        
        archivefile = zipfile.ZipFile(archivepath, mode='r')
        archivefile.extract(picklefilename, path=dirname)
        archivefile.extract(npzfilename, path=dirname)
        archivefile.close()
        
        picklefile = open(os.path.join(dirname, picklefilename), 'rb')
        pickledict = pickle.load(picklefile)
        picklefile.close()
        
        npzfile = open(os.path.join(dirname, npzfilename), 'rb')
        npzdata = np.load(npzfile)
        
        pickledata = pickledict['data']
        parentuidmap = pickledict['parentmap']
        
        newuidsmap = {}
        for olduid, objdict in pickledata.iteritems():
            tid = olduid[0]
            for key, value in objdict.iteritems():
                if isinstance(value, basestring) and value.startswith(self._NPZIDENTIFIER):
                    objdict[key] = npzdata[value.lstrip(self._NPZIDENTIFIER)]
            obj = self.new(tid, **objdict)
            newuidsmap[olduid] = obj.uid
            self.add(obj, newuidsmap.get(parentuidmap[olduid]))
        
        npzfile.close()
        
        os.remove(os.path.join(dirname, picklefilename))
        os.remove(os.path.join(dirname, npzfilename))
        
        return True