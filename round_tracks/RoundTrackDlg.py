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
## Class RoundTrackDlg
###########################################################################

class RoundTrackDlg ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Round Track parameters", pos = wx.DefaultPosition, size = wx.Size( 390,520 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer3 = wx.BoxSizer( wx.VERTICAL )

		self.m_comment = wx.StaticText( self, wx.ID_ANY, u"Select Two angled Tracks\n", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_comment.Wrap( -1 )

		bSizer3.Add( self.m_comment, 0, wx.ALL|wx.EXPAND, 5 )

		bSizer31 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Distance from Intersection (mm)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )

		bSizer31.Add( self.m_staticText3, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_distanceMM = wx.TextCtrl( self, wx.ID_ANY, u"5", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_distanceMM.SetMinSize( wx.Size( 1000,-1 ) )

		bSizer31.Add( self.m_distanceMM, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer3.Add( bSizer31, 0, 0, 5 )

		bSizer311 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText31 = wx.StaticText( self, wx.ID_ANY, u"Number of segments    ..   (1-32)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText31.Wrap( -1 )

		bSizer311.Add( self.m_staticText31, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_segments = wx.TextCtrl( self, wx.ID_ANY, u"16", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_segments.SetMinSize( wx.Size( 1000,-1 ) )

		bSizer311.Add( self.m_segments, 1, wx.ALL, 5 )


		bSizer3.Add( bSizer311, 1, wx.EXPAND, 5 )

		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer3.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer12 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1013 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1013.Wrap( -1 )

		bSizer12.Add( self.m_staticText1013, 1, wx.ALL, 5 )

		self.m_bitmap1 = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 180,100 ), 0 )
		bSizer12.Add( self.m_bitmap1, 1, wx.EXPAND, 5 )


		bSizer3.Add( bSizer12, 1, wx.EXPAND, 5 )

		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText101 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText101.Wrap( -1 )

		bSizer1.Add( self.m_staticText101, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_buttonRound = wx.Button( self, wx.ID_OK, u"Round", wx.DefaultPosition, wx.DefaultSize, 0 )

		self.m_buttonRound.SetDefault()
		bSizer1.Add( self.m_buttonRound, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_buttonCancel = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1.Add( self.m_buttonCancel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer3.Add( bSizer1, 0, wx.ALIGN_RIGHT|wx.EXPAND, 5 )

		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Reconnecting" ), wx.VERTICAL )

		bSizer611 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText81 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Select a Track to delete round segments", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText81.Wrap( -1 )

		bSizer611.Add( self.m_staticText81, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )

		self.m_buttonDelete = wx.Button( sbSizer1.GetStaticBox(), wx.ID_OK, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611.Add( self.m_buttonDelete, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sbSizer1.Add( bSizer611, 1, wx.EXPAND, 5 )

		bSizer111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText10111 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Select tracks including one round corner to be straighten", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10111.Wrap( -1 )

		bSizer111.Add( self.m_staticText10111, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_buttonReconnect = wx.Button( sbSizer1.GetStaticBox(), wx.ID_OK, u"Connect", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer111.Add( self.m_buttonReconnect, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sbSizer1.Add( bSizer111, 1, wx.EXPAND, 5 )


		bSizer3.Add( sbSizer1, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer3 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


