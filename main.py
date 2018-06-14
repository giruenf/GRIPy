# -*- coding: utf-8 -*-

from app.gripy_app import GripyApp 
from app.app_utils import Chronometer


c = Chronometer()

app = GripyApp()


print (c.end())

app.MainLoop()

