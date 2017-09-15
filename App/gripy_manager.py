# -*- coding: utf-8 -*-
import wx
import weakref
import app_utils
from pubsub import PublisherMixin
from App import log

"""
Parent class for Managers
"""
class Manager(PublisherMixin):

    def __init__(self):
        caller_info = app_utils.get_caller_info()
        owner = caller_info[1][1]

        # TODO: Armengue feito para as funcoes dos menus.. tentar corrigir isso
        if not owner:
            owner = wx.GetApp()
        try:
            owner_name = owner.uid
        except AttributeError:
            owner_name = owner.__class__.__name__
        msg = 'A new instance of ' + self.__class__.__name__ + \
                                ' was solicited by {}'.format(owner_name)
        log.debug(msg)       
        self._ownerref = weakref.ref(owner)
        