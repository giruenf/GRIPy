# -*- coding: utf-8 -*-

from classes.base import GripyObject


class OMBaseObject(GripyObject):
    """
    OMBaseObject is the base class for all objects dealt by ObjectManager.
    """
    tid = None
    _TID_FRIENDLY_NAME = None

    @classmethod
    def _is_tid_node_needed(cls):
        """Used by TreeController to create or not a tid node as a objects
        from a given class grouper. If tid node is created, the method 
        get_tid_friendly_name will provide it's node label.
        """
        return True

    @classmethod
    def _get_tid_friendly_name(self):
        """In general, classes tids are not adequated to be shown as a
        tid node label. If class _TID_FRIENDLY_NAME is provided, it will be
        used by TreeController as tid node label.
        """
        try:
            return self._TID_FRIENDLY_NAME
        except:
            return self.tid

    def _get_object_friendly_name(self):
        """Returns a name to be used by TreeController as object node label."""
        return self.name
    
