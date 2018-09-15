# -*- coding: utf-8 -*-
"""
GRIPy - Geofisica de Reservatorio Interativa em Python
======================================================

GRIPy is developed by GIR...

Details about licensing are located in files LICENSE and OSLICENSE.

Check README.md file for GRIPy dependencies.

"""

from app.gripy_app import GripyApp 
from app.app_utils import Chronometer

# Checking startup duration with Chronometer. It will be removed ASAP ;-) 
c = Chronometer()
app = GripyApp()
print (c.end())
app.MainLoop()
