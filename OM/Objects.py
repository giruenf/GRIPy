# -*- coding: utf-8 -*-
"""
Objects
=======

This file defines the base classes for objects that can be managed by
`ObjectManager`.
"""

from collections import OrderedDict


class GenericObject(object):
    """
    The simplest object that can be managed by `ObjectManager`.
    
    Attributes
    ----------
    tid : string
        A identificator for the type. Subclasses of `GenericObject` must have
        their own unique `tid`.
    oid : int
        A identificator for the object. Objects of the same type cannot have
        the same `oid` (on the other hand, objects from different types might
        share the same `oid`).
    uid : tuple
        A unique identificator for the object. A combination (a tuple) of the
        type identificator (`tid`) and the object identificator (`oid`). No
        object can share the same `uid` with another.
    """
    tid = None

    def __init__(self):
        self._oid = None

    @property
    def oid(self):
        return self._oid

    @oid.setter
    def oid(self, _oid):
        if self._oid is None:
            self._oid = _oid
        else:
            msg = "Cannot change object id."
            raise TypeError(msg)

    @oid.deleter
    def oid(self):
        msg = "Cannot delete object id."
        raise TypeError(msg)

    @property
    def uid(self):
        return self.tid, self.oid
    
    def _getstate(self):
        """
        Return the state of the object.
        
        This method is used by `ObjectManager` method `save`. It must return a
        dictionary containing all necessary data to reconstruct the object with
        a simple call to its constructor. For example::
        
            obj1 = SubClassOfGenericObject(someparameters)
            # do some changes to 'obj1'
            state = obj1._getstate()
            obj2 = SubClassOfGenericObject(**state)
            # now 'obj2' must behave the same as 'obj1'
        
        Returns
        -------
        dict
            The state necessary to reconstruct the object with a call to its
            constructor.
        
        Notes
        -----
        Not all of the data needs to be returned in this method. But the object
        recovered from the state must behave the same way as the original
        object.
        """
        return {}


class ParentObject(GenericObject):
    """
    An object that can have children.
    
    The 'children' of an object are the objects that belong to it in an
    hierarchy. For example, a Log object can be thought of as a child of a
    Well object, since a Well object can 'have' Log objects.
    
    The possible children of an object are determined by the type registration
    whithin `ObjectManager`. For example, ``ObjectManager.registertype(TypeA,
    TypeB)`` determines that instances of TypeB can have children with type
    TypeA.
    
    Children are not added directly to an object. To do it the ObjectManager
    must be used::
    
        om = ObjectManager(owner)
        parentobj = om.new('parenttid')
        om.add(parentobj)
        childobj = om.new('childtid')
        om.add(childobj, parentobj.uid)
        # Now 'parentobj' has 'childobj' as a child
    
    Attributes
    ----------
    _children : OrderedDict
        Object's children. Keys are children `uid`s and values are the children
        themselves.
    """
    tid = None

    def get(self, uid):
        """
        Return the child that has the given `uid`.
        
        Parameters
        ----------
        uid : uid
            The unique identificator of the required child.
        
        Returns
        -------
        GenericObject
            The child which unique identificator matches `uid`.
            
        See Also
        --------
        Manager.ObjectManager.get
        """
        return self._children[uid]

    def list(self, tidfilter=None):
        """
        Return a list of children.
        
        Parameters
        ----------
        tidfilter : str, optional
            Filter the children so that only those with `tid` equal to
            `tidfilter` will be returned.
        
        Returns
        -------
        children : list
            A list of all the object's children or a list of object's children
            of a specific type, depending on the value of `tidfilter`.
        
        See Also
        --------
        Manager.ObjectManager.list
        """
        children = self._children.values()
        if tidfilter:
            return [child for child in children if child.tid == tidfilter]
        else:
            return children

    def __init__(self):
        super(ParentObject, self).__init__()
        self._children = OrderedDict()
