# -*- coding: utf-8 -*-

"""
Created on Sat Aug 25 20:21:46 2018

@author: Adriano
"""

from classes.base import GripyObject


class OMBaseObject(GripyObject):
    """
    
    """
    tid = None
    _TID_FRIENDLY_NAME = None

    @classmethod
    def is_tid_node_needed(cls):
        """For TreeController"""
        return True

    def get_object_friendly_name(self):
        return self.name
    
    def get_tid_friendly_name(self):
        return self.name