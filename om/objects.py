# -*- coding: utf-8 -*-
"""
Objects
=======

This file defines the base classes for objects that can be managed by
`ObjectManager`.
"""

from app.pubsub import PublisherMixin


class GenericObject(PublisherMixin):
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

    def __str__(self):
        return str(self.uid)        

    ###
    #def _being_deleted(self):
    #    self.send_message('remove')
    ###

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
    
    # TODO: Rever docs
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



