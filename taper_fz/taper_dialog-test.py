#!/usr/bin/env python

# Taper for pcbnew using filled zones
# easyw
#
# Based 
# on Teardrops for PCBNEW by Niluje 2019 thewireddoesntexist.org
# on kicad Toolbox vy aschaller 

import wx
import pcbnew
import os

from .taper_gui import taper_gui
from .taper import SetTaper, RmTapers, __version__

class TaperDialog(taper_gui):
    """Class that gathers all the Gui control"""

    def __init__(self, board):
        """Init the brand new instance"""
        super(TaperDialog, self).__init__(None)
        self.board = board
        self.SetTitle("Tapers (v{0})".format(__version__))
        self.rbx_action.Bind(wx.EVT_RADIOBOX, self.onAction)
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
        self.but_cancel.Bind(wx.EVT_BUTTON, self.onCloseWindow)
        self.but_ok.Bind(wx.EVT_BUTTON, self.onProcessAction)
        self.m_bitmap_help.SetBitmap(wx.Bitmap( os.path.join(os.path.dirname(os.path.realpath(__file__)), "rcs", "tapers-help.png") ) )
        self.SetMinSize(self.GetSize())

    def onAction(self, e):
        """Enables or disables the parameters/options elements"""
        els = [self.st_hpercent, self.sp_hpercent, self.st_vpercent,
               self.sp_vpercent, self.st_nbseg, self.sp_nbseg,
               self.cb_include_smd_pads]
        for i, el in enumerate(els):
            if self.rbx_action.GetSelection() == 0:
                el.Enable()
            else:
                el.Disable()

    def onProcessAction(self, event):
        """Executes the requested action"""
        if self.rbx_action.GetSelection() == 0:
            count = SetTaper(self.sp_hpercent.GetValue(),
                                 self.sp_vpercent.GetValue(),
                                 self.sp_nbseg.GetValue(),
                                 self.board,
                                 self.cb_include_smd_pads.IsChecked())
            wx.MessageBox("{0} Taper inserted".format(count))
        else:
            count = RmTapers(pcb=self.board)
            wx.MessageBox("{0} Tapers removed".format(count))
        pcbnew.Refresh() #Show up newly added vias
        self.Destroy()

    def onCloseWindow(self, event):
        self.Destroy()


def InitTapersDialog(board):
    """Launch the dialog"""
    tg = TapersDialog(board)
    tg.Show(True)
    return tg
