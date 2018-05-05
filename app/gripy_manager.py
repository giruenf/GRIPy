# -*- coding: utf-8 -*-
import wx
import weakref
from app import app_utils
from app.pubsub import PublisherMixin
from app import log

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
        