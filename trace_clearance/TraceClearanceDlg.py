# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class TraceClearanceDlg
###########################################################################

class TraceClearanceDlg ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 373,480 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 373,580 ), wx.DefaultSize )

		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Add copper pour keepout\nto selected traces.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )

		bSizer2.Add( self.m_staticText4, 0, wx.ALL, 5 )

		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_bitmap = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_bitmap, 0, wx.ALL, 5 )


		bSizer2.Add( bSizer5, 1, wx.EXPAND, 5 )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Zone clearance (mm)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )

		bSizer3.Add( self.m_staticText5, 0, wx.ALL, 5 )

		self.m_clearance = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_clearance, 0, wx.ALL, 5 )


		bSizer2.Add( bSizer3, 1, wx.EXPAND, 5 )

		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_button_ok = wx.Button( self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_button_ok, 0, wx.ALL, 5 )

		self.m_button_cancel = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_button_cancel, 0, wx.ALL, 5 )


		bSizer2.Add( bSizer4, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer2 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


