#!/usr/bin/env python

# Taper for pcbnew using filled zones
# easyw
#
# Based 
# on Teardrops for PCBNEW by Niluje 2019 thewireddoesntexist.org
# on kicad Toolbox vy aschaller 

import wx
import os
from pcbnew import ActionPlugin, GetBoard

#from .taper_dialog import InitTaperDialog
# from .taper import dummy #Layout
#from .taper import Taper #Layout
#from .taper import Taper_Zone #Layout
from .taper import SetTaper_Zone
from .taper import __version__

class TaperPlugin(ActionPlugin):
    """Class that gathers the actionplugin stuff"""
    def defaults(self):
        self.name = "Tapers & smooth Joins vers "+__version__+"\n Select one Track and one Pad\n or Two connected or nearby Tracks\n or a single Track"
        self.category = "Modify PCB"
        self.description = "Manages Tapers as Zones on a PCB"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'taper.png')
        self.show_toolbar_button = True

    def Run(self):
        #InitTaperDialog(GetBoard())
        #Taper_Zone(GetBoard())
        SetTaper_Zone(GetBoard())
        #pass
        
