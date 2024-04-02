#!/usr/bin/env python

#  Copyright 2019 Maurice https://github.com/easyw/

# some source tips @
# https://github.com/bpkempke/kicad-scripts
# https://github.com/MitjaNemec/Kicad_action_plugins
# https://github.com/jsreynaud/kicad-action-scripts

# GNU GENERAL PUBLIC LICENSE
#                        Version 3, 29 June 2007
# 
#  Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
#  Everyone is permitted to copy and distribute verbatim copies
#  of this license document, but changing it is not allowed.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

# import round_trk; reload(round_trk)

## todo:
# 1) insert check drc for rounding & fencing
# 2) add radius as text to rounded curve
# 3) add selected track lenght

import sys
import os
from pcbnew import *
try:
    from builtins import abs
except:
    pass
import wx
import pcbnew
import math
import cmath
# from wx import FileConfig
import configparser
        

#from .RoundTrackDlg import RoundTrackDlg
from . import RoundTrackDlg


ToUnits=pcbnew.ToMM #ToMils
FromUnits=pcbnew.FromMM #Mils

debug = False #True
debug2 = False
show_points = False
show_points2 = False

global delete_before_connect
delete_before_connect = False

# N_SEGMENTS = 32 #4#32
# distI = FromMM(10)

# import pcbnew; print (pcbnew.PLUGIN_DIRECTORIES_SEARCH)

# Python plugin stuff
def distance (p1,p2):
    return math.hypot(p1.y-p2.y,p1.x-p2.x)
#
#gets the angle of a track
def getTrackAngle(t1,center):
    #use atan2 so the correct quadrant is returned
    if t1.GetStart().x == center.x and t1.GetStart().y == center.y:
        wxLogDebug("Start = Center",debug)
        return math.atan2((t1.GetEnd().y - t1.GetStart().y), (t1.GetEnd().x - t1.GetStart().x))
    else:
        wxLogDebug("End = Center",debug)
        return math.atan2((t1.GetStart().y - t1.GetEnd().y), (t1.GetStart().x - t1.GetEnd().x));
#
def getPointsAngle(p1,center):
    #use atan2 so the correct quadrant is returned
        wxLogDebug("End = Center",debug)
        return math.atan2((p1.y - center.y), (p1.x - center.x));
#
#track length
def GetTrackLength(t1):
    return t1.GetLength()
#

def wxLogDebug(msg,show):
    """printing messages only if show is omitted or True"""
    if show:
        wx.LogMessage(msg)
# 
def CalcLinLenght(self): # , dist,len_field):
    import pcbnew
    import math
    import cmath
    global debug
    
    local_config_file = os.path.join(os.path.dirname(__file__), 'rt_config.ini')
    config = configparser.ConfigParser()
    config.read(local_config_file)
    orig_segments=config.get('params','segments')
    pcb = pcbnew.GetBoard()
    distI = FromUnits(float(self.m_distanceMM.Value))
    tracks = []
    #print ("TRACKS WHICH MATCH CRITERIA:")
    if  hasattr(pcbnew,'TRACK'):
        track_item = pcbnew.TRACK
    else:
        track_item = pcbnew.PCB_TRACK
    for item in pcb.GetTracks():
        if type(item) is track_item and item.IsSelected(): #item.GetNetname() == net_name:
            tracks.append(item)    
    if len (tracks) == 2:            
        #add all the possible intersections to a unique set, for iterating over later
        intersections = set();  
        for t1 in range(len(tracks)):
            for t2 in range(t1+1, len(tracks)):
                #check if these two tracks share an endpoint
                # reduce it to a 2-part tuple so there are not multiple objects of the same point in the set
                if(tracks[t1].IsPointOnEnds(tracks[t2].GetStart())): 
                    intersections.add((tracks[t2].GetStart().x, tracks[t2].GetStart().y))
                if(tracks[t1].IsPointOnEnds(tracks[t2].GetEnd())):
                    intersections.add((tracks[t2].GetEnd().x, tracks[t2].GetEnd().y))
        if len(intersections)==1:
            dbg=debug
            for ip in intersections:
                (x,y) = ip
                if  hasattr(pcbnew,'wxPoint()'):
                    intersection = wxPoint(x,y)
                else:
                    intersection = VECTOR2I(int(x),int(y))
                t1 = tracks [0]
                t2 = tracks [1]
                s1 = t1.GetStart()
                s2 = t2.GetStart()
                e1 = t1.GetEnd()
                e2 = t2.GetEnd()
                ini_len=t1.GetLength()+t2.GetLength()
                t1_ulen = t1.GetLength()
                t2_ulen = t2.GetLength()
                max_len = min(t1_ulen, t2_ulen)
                if max_len < distI:
                    self.m_staticText31.SetLabel("Max. Dist. "+str('%.3f'%(float(ToUnits(max_len)))))
                    self.m_segments.SetValue('------')
                    return 0
                else:
                    wxLogDebug("t1: "+str(ToUnits(s1.x))+":"+str(ToUnits(s1.y))+";"+str(ToUnits(e1.x))+":"+str(ToUnits(e1.y)),dbg)
                    wxLogDebug("t2: "+str(ToUnits(s2.x))+":"+str(ToUnits(s2.y))+";"+str(ToUnits(e2.x))+":"+str(ToUnits(e2.y)),dbg)
                    wxLogDebug("t1 length: "+str(ToUnits(t1.GetLength())),dbg)
                    wxLogDebug("t2 length: "+str(ToUnits(t2.GetLength())),dbg)
                    wxLogDebug("intersection: "+str(ToUnits(x))+":"+str(ToUnits(y)),dbg)
                    wxLogDebug("lenght: "+str(ToUnits(ini_len)),dbg)
                    wxLogDebug("distance: "+str(self.m_distanceMM.Value),dbg)
                    angle1 = math.degrees((getTrackAngle(tracks[0],intersection)))
                    angle2 = math.degrees((getTrackAngle(tracks[1],intersection)))
                    end_coord1 = (distI) * cmath.exp(math.radians(angle1)*1j) #cmath.rect(r, phi) : Return the complex number x with polar coordinates r and phi.
                    end_coord2 = (distI) * cmath.exp(math.radians(angle2)*1j)
                    if  hasattr(pcbnew,'wxPoint()'):
                        startP = wxPoint(end_coord1.real+x,end_coord1.imag+y)
                        endP = wxPoint(end_coord2.real+x,end_coord2.imag+y)
                    else:
                        startP = VECTOR2I(int(end_coord1.real+x),int(end_coord1.imag+y))
                        endP = VECTOR2I(int(end_coord2.real+x),int(end_coord2.imag+y))
                    center,radius = getCircleCenterRadius( startP,endP,intersection )
                    angle = angle2-angle1
                    if angle > math.degrees(math.pi):
                        angle -= math.degrees(2*math.pi)
                    elif angle < -math.degrees(math.pi):
                        angle += 2*math.degrees(math.pi)
                    wxLogDebug("tracks angle: "+str(angle),dbg)
                    angleArc1 = math.degrees((getPointsAngle(startP,center)))
                    wxLogDebug("start angle: "+str(angleArc1),dbg)
                    angleArc2 = math.degrees((getPointsAngle(endP,center)))
                    wxLogDebug("end angle: "+str(angleArc2),dbg)
                    wxLogDebug("delta angle: "+str(angleArc1-angleArc2),dbg)
                    wxLogDebug("radius: "+str(ToUnits(radius)),dbg)
                    arc_len = abs((math.pi*2*ToUnits(radius)) * ((angleArc1-angleArc2)/360))
                    wxLogDebug("arc lenght: "+str(arc_len),dbg)
                    final_len=ToUnits(ini_len)-2*(float(self.m_distanceMM.Value))+arc_len
                    wxLogDebug("final lenght: "+str(final_len),dbg)
                    pcb_v = pcbnew.GetBuildVersion()
                    if not hasattr(pcbnew, 'EDA_RECT') or pcb_v.startswith('(6.') or pcb_v.startswith('6.'): # kv7 or kv6
                        self.m_segments.SetValue(str('%.3f'%(final_len)))
                        self.m_staticText31.SetLabel("Calculated Lenght ...")
                    else:
                        self.m_staticText31.SetLabel("Calc. Lenght "+str('%.3f'%(float(final_len)))+' Segm Num')
                        if self.m_segments.Value == '------':
                            self.m_segments.SetValue(orig_segments)
                    return final_len
        else:
            return 0
    else:
        return 0
#
                
class RoundTrack_Dlg(RoundTrackDlg.RoundTrackDlg):
    # from https://github.com/MitjaNemec/Kicad_action_plugins
    # hack for new wxFormBuilder generating code incompatible with old wxPython
    # noinspection PyMethodOverriding
    def SetSizeHints(self, sz1, sz2):
        if wx.__version__ < '4.0':
            self.SetSizeHintsSz(sz1, sz2)
        else:
            super(RoundTrack_Dlg, self).SetSizeHints(sz1, sz2)

    def onDeleteClick(self, event):
        return self.EndModal(wx.ID_DELETE)

    def onConnectClick(self, event):
        return self.EndModal(wx.ID_REVERT)

    # def GetConfig(self):
    #     return [self.m_distanceMM.Value, self.GetSize()]

    def __init__(self,  parent):
        import wx
        global delete_before_connect
        import math
        import cmath
        import pcbnew
        import os
        
        
        RoundTrackDlg.RoundTrackDlg.__init__(self, parent)
        self.m_distanceMM.SetValue("5")
        #self.m_segments.SetValue(CalcLinLenght(self.m_distanceMM.Value,self.m_segments))
        local_config_file = os.path.join(os.path.dirname(__file__), 'rt_config.ini')
        config = configparser.ConfigParser()
        config.read(local_config_file)
        width = int(config.get('win_size','width'))
        height = int(config.get('win_size','height'))
        self.m_distanceMM.SetValue(config.get('params','distance'))
        self.m_segments.SetValue(config.get('params','segments'))
        #wx.LogMessage(str(width)+';'+str(height))
        self.SetSize((width,height))
        #self.m_distanceMM.SetValue("5")
        self.Bind(wx.EVT_TEXT, self.OnDistChange,
                  self.m_distanceMM)
        # self.Bind(wx.EVT_TEXT, self.OnLenghtChange,
        #           self.m_segments)
        # self.Bind(wx.EVT_SET_FOCUS, self.Navigate())
        #           self.m_segments)
        #self.GetSizer().Fit(self)
        # self.SetSize(self.GetSize())
        self.m_buttonDelete.Bind(wx.EVT_BUTTON, self.onDeleteClick)
        self.m_buttonReconnect.Bind(wx.EVT_BUTTON, self.onConnectClick)
        if wx.__version__ < '4.0':
            self.m_buttonReconnect.SetToolTipString( u"Select two converging Tracks to re-connect them\nor Select tracks including one round corner to be straighten" )
            self.m_buttonRound.SetToolTipString( u"Select two connected Tracks to round the corner\nThen choose distance from intersection and the number of segments" )
        else:
            self.m_buttonReconnect.SetToolTip( u"Select two converging Tracks to re-connect them\nor Select tracks including one round corner to be straighten" )
            self.m_buttonRound.SetToolTip( u"Select two connected Tracks to round the corner\nThen choose distance from intersection and the number of segments" )
        # self.m_distanceMM.SetValue("5")
        pcb_v = pcbnew.GetBuildVersion()
        if not hasattr(pcbnew, 'EDA_RECT') or pcb_v.startswith('(6.') or pcb_v.startswith('6.'): # kv7 or kv6
            self.m_staticText31.SetLabel("Calculated Lenght ...")
            self.m_segments.SetValue('')
            self.m_buttonRound.SetToolTip( u"Select two connected Tracks to round the corner\nThen choose distance from intersection" )
            #self.m_segments.Enable(False)
            # self.m_segments.SetFont(wx.Font(wx.BOLD))
            # self.m_segments.Hide()
        if self.m_checkBoxDelete.IsChecked():
            # self.m_staticText31.SetLabel("Calculated Lenght ...")
            delete_before_connect = True
        
    # def OnLenghtChange(self, event: wx.CommandEvent): #second text ctrl
    #     wx.MessageBox(self.m_segments.Value, 'info1',
    #                 wx.OK | wx.ICON_WARNING)
    def OnDistChange(self, event): #def OnDistChange(self, event: wx.CommandEvent): #first text ctrl
        CalcLinLenght(self) #, self.m_distanceMM.Value,self.m_segments) #parameters in internal units
        # wx.MessageBox(self.m_distanceMM.Value, 'info2',
        #             wx.OK | wx.ICON_WARNING)
 
#
class Tracks_Rounder(pcbnew.ActionPlugin):

    def defaults(self):
        self.name = "Rounder for Tracks\n version 3.2"
        self.category = "Modify PCB"
        self.description = "Rounder for selected Traces on the PCB"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./round_track.png")
        self.show_toolbar_button = True

    def Warn(self, message, caption='Warning!'):
        dlg = wx.MessageDialog(
            None, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

    def CheckDistanceInput(self, value, data):
        val = None
        try:
            val = float(value.replace(',','.'))
            if val <= 0:
                raise Exception("Invalid")
        except:
            self.Warn(
                "Invalid parameter for %s: Must be a positive number" % data)
            val = 0
        return val

    def CheckSegmentsInput(self, value, data):
        val = None
        pcb_v = pcbnew.GetBuildVersion()
        if not hasattr(pcbnew, 'EDA_RECT') or pcb_v.startswith('(6.') or pcb_v.startswith('6.'): # kv7 or kv6
            pass
        else: #kv5
            try:
                val = int(value)
                if (val < 2) or (val >32):
                    raise Exception("Invalid")
            except:
                self.Warn(
                    "Invalid parameter for %s: Must be bigger than 2" % data)
                val = None
        return val

    
    def Run(self):
        global delete_before_connect
        #self.pcb = GetBoard()
        # net_name = "GND"
        pcb = pcbnew.GetBoard()
        
        #from https://github.com/MitjaNemec/Kicad_action_plugins
        #hack wxFormBuilder py2/py3
        # _pcbnew_frame = [x for x in wx.GetTopLevelWindows() if x.GetTitle().lower().startswith('pcbnew')][0]
        _pcbnew_frame = [x for x in wx.GetTopLevelWindows() if x.GetName() == 'PcbFrame'][0]
        #aParameters = RoundTrackDlg(None)
        aParameters = RoundTrack_Dlg(_pcbnew_frame)
        if hasattr (pcb, 'm_Uuid'):
            aParameters.m_buttonDelete.Disable()
            aParameters.m_checkBoxDelete.Disable()
        #aParameters = RoundTrack_DlgEx(_pcbnew_frame)
        # local_config_file = os.path.join(os.path.dirname(__file__), 'rt_config.ini')
        # config = configparser.ConfigParser()
        # config.read(local_config_file)
        # width = int(config.get('win_size','width'))
        # height = int(config.get('win_size','height'))
        # aParameters.m_distanceMM.SetValue(config.get('params','distance'))
        #wx.LogMessage(str(width)+';'+str(height))
        #aParameters.SetSize((width,height))
        #aParameters.width=width
        #aParameters.height=height
        #aParameters.SetSize(width,height)

        
        aParameters.Show()
        calc_len = float(CalcLinLenght(aParameters)) #,aParameters.m_distanceMM.Value,aParameters.m_segments)

        #end hack
        #aParameters.m_distanceMM.SetValue("5")
        #aParameters.m_segments.SetValue("16")
        aParameters.m_bitmap1.SetBitmap(wx.Bitmap( os.path.join(os.path.dirname(os.path.realpath(__file__)), "round_track_help.png") ) )
        modal_result = aParameters.ShowModal()
        #def OnKeyDown(self, e):
        #    key = e.GetKeyCode()
        #    wx.MessageBox(aParameters.m_segments.GetValue(), 'info',
        #            wx.OK | wx.ICON_WARNING)

        #calc_len=None
        pcb_v = pcbnew.GetBuildVersion()
        if not hasattr(pcbnew, 'EDA_RECT') or pcb_v.startswith('(6.') or pcb_v.startswith('6.'): # kv7 or kv6
            segments = 1
            if len(aParameters.m_segments.GetValue()) > 0:
                try:
                    calc_len = float(aParameters.m_segments.GetValue())
                except:
                    calc_len = 0
            else:
                calc_len = 0
            pass
        else: #kv5
            segments = self.CheckSegmentsInput(
                aParameters.m_segments.GetValue(), "number of segments")
            calc_len = float(CalcLinLenght(aParameters)) #,aParameters.m_distanceMM.Value,aParameters.m_segments)
            #aParameters.m_staticText31.SetLabel("Calculated Lenght "+str('%.3f'%(float(CalcLinLenght(aParameters.m_distanceMM.Value,aParameters.m_segments)))))
        dist = self.CheckDistanceInput(aParameters.m_distanceMM.GetValue(), "distance from intersection")
        if aParameters.m_checkBoxDelete.IsChecked():
            delete_before_connect = True
        else:
            delete_before_connect = False
        if segments is not None and dist != 0:
            distI = FromMM(dist)
            if modal_result == wx.ID_OK:
                Round_Selection(pcb, distI, segments, calc_len)
                pcbnew.Refresh()
            elif modal_result == wx.ID_DELETE:
                Delete_Segments(pcb)
                #wx.LogMessage('Round Segments on Track Net Deleted')
            elif modal_result == wx.ID_REVERT:
                wxLogDebug('Connecting Tracks',debug)
                Connect_Segments(pcb)
            else:
                None  # Cancel
            #pcbnew.Refresh()
        else:
            None  # Invalid input
        # wx.LogMessage(aParameters.GetConfig()[0])
        # wx.LogMessage(str(aParameters.GetConfig()[1][0]))
        # wx.LogMessage(str(aParameters.GetConfig()[1][1]))
        # wx.LogMessage(str(aParameters.local_config_file))
        local_config_file = os.path.join(os.path.dirname(__file__), 'rt_config.ini')
        config = configparser.ConfigParser()
        config.read(local_config_file)
        config['win_size']['width'] = str(aParameters.GetSize()[0])
        config['win_size']['height'] = str(aParameters.GetSize()[1])
        config['params']['distance'] = aParameters.m_distanceMM.Value
        with open(local_config_file, 'w') as configfile:
            config.write(configfile)
        # aParameters.width = int(config.get('win_size','width'))
        # aParameters.height = int(config.get('win_size','height'))
        # aParameters.SetSize(self.width,self.height)
        aParameters.Destroy()
        
        #Round_Selection(pcb)
#


def create_Track(pcb,p1,p2,lyr=None,w=None,Nn=None,Ts=None):
    #draw segment to test
    #new_line = pcbnew.DRAWSEGMENT(pcb)
    if  hasattr(pcbnew,'TRACK'):
        new_line = pcbnew.TRACK(pcb)
    else:
        new_shape = PCB_SHAPE() 
        new_line = PCB_TRACK(new_shape)
    if hasattr(pcbnew, 'EDA_RECT')or not hasattr(pcbnew,'wxPoint()'): # kv5,kv6,kv8
        new_line.SetStart(p1)
        new_line.SetEnd(p2)
    else: #kv7
        new_line.SetStart(VECTOR2I(p1))
        new_line.SetEnd(VECTOR2I(p2))     
    if w is None:
        new_line.SetWidth(FromUnits(1.5)) #FromUnits(int(mask_width)))
    else:
        new_line.SetWidth(FromUnits(w))
    if lyr is None:
        lyr = F_SilkS
    if Nn is not None:
        new_line.SetNet(Nn)
        #new_line.SetNetname(Nn)
    new_line.SetLayer(lyr) #pcbnew.F_SilkS) #pcb.GetLayerID(mask_layer))
    if Ts is not None:
        tsc = 0
        Nname = new_line.GetNetname()
        for c in Nname:
            tsc = tsc + ord(c)
        if hasattr(new_line, 'SetTimeStamp'):
            new_line.SetTimeStamp(tsc)  # adding a unique number (this netname) as timestamp to mark this segment as generated by this script on this netname
    pcb.Add(new_line)
    return new_line
#
def create_Arc(pcb,p1,p2,mp,lyr=None,w=None,Nn=None,Ts=None):
    #import pcbnew
    #from pcbnew import *
    #b = pcbnew.GetBoard()
    #new_shape = PCB_SHAPE()
    #new_arc = PCB_ARC(new_shape)
    #p1= wxPoint(203200000, 127000000)
    #md= wxPoint(221160512, 134439488)
    #p2= wxPoint(228600000, 152400000)
    #new_arc.SetStart(p1)
    #new_arc.SetMid(md)
    #new_arc.SetEnd(p2)
    #new_arc.SetWidth(250000)
    #new_arc.SetLayer(pcbnew.B_Cu)
    #b.Add(new_arc)
    #pcbnew.Refresh()

    #draw segment to test
    #new_line = pcbnew.DRAWSEGMENT(pcb)
    if  hasattr(pcbnew,'TRACK'):
        new_arc = pcbnew.TRACK(pcb)
    else:
        #new_shape = PCB_SHAPE() 
        #new_arc = PCB_ARC(new_shape)
        new_trk = PCB_TRACK(pcb) 
        new_arc = PCB_ARC(new_trk)
    if hasattr(pcbnew, 'EDA_RECT'): # kv5,kv6
        new_arc.SetStart(p1)
        new_arc.SetEnd(p2)
        new_arc.SetMid(mp)
    elif hasattr(pcbnew, 'wxPoint()'): # kv7
        new_arc.SetStart(VECTOR2I(p1))
        new_arc.SetEnd(VECTOR2I(p2))
        new_arc.SetMid(VECTOR2I(mp))        
    else:#kv8
        new_arc.SetStart(p1)
        new_arc.SetEnd(p2)
        new_arc.SetMid(mp)
    if w is None:
        new_arc.SetWidth(FromUnits(1.5)) #FromUnits(int(mask_width)))
    else:
        new_arc.SetWidth(FromUnits(w))
    if lyr is None:
        lyr = F_SilkS
    if Nn is not None:
        new_arc.SetNet(Nn)
        #new_arc.SetNetname(Nn)
    new_arc.SetLayer(lyr) #pcbnew.F_SilkS) #pcb.GetLayerID(mask_layer))
    if Ts is not None:
        tsc = 0
        Nname = new_arc.GetNetname()
        for c in Nname:
            tsc = tsc + ord(c)
        if hasattr(new_arc, 'SetTimeStamp'):
            new_arc.SetTimeStamp(tsc)  # adding a unique number (this netname) as timestamp to mark this segment as generated by this script on this netname
    pcb.Add(new_arc)
    return new_arc
#

def create_Draw(pcb,p1,p2,lyr=None,w=None):
    #draw segment to test
    if hasattr(pcbnew,'DRAWSEGMENT'):
        new_line = pcbnew.DRAWSEGMENT(pcb)
    else:
        new_line = PCB_SHAPE()
    #new_line = pcbnew.TRACK(pcb)
    if hasattr(pcbnew, 'EDA_RECT'): # kv5,kv6
        new_line.SetStart(p1)
        new_line.SetEnd(p2)
    else: # kv7
        new_line.SetStart(VECTOR2I(p1))
        new_line.SetEnd(VECTOR2I(p2))    
    if w is None:
        new_line.SetWidth(FromUnits(1.5)) #FromUnits(int(mask_width)))
    else:
        new_line.SetWidth(FromUnits(w))
    if lyr is None:
        lyr = F_SilkS
    new_line.SetLayer(lyr) #pcbnew.F_SilkS) #pcb.GetLayerID(mask_layer))
    pcb.Add(new_line)
    return new_line
#
def create_Text(pcb, txt, p, w, lyr):
    if hasattr(pcbnew,'TEXTE_PCB'):
        mytxt = pcbnew.TEXTE_PCB(pcb)
    else:
        mytxt = pcbnew.PCB_TEXT(EDA_TEXT) #Cast_to_PCB_TEXT(EDA_TEXT)
    mytxt.SetText(txt)
    mytxt.SetLayer(lyr)
    mytxt.SetPosition(p)
    mytxt.SetHorizJustify(pcbnew.GR_TEXT_HJUSTIFY_CENTER)
    mytxt.SetTextSize(pcbnew.wxSize(w,w))
    if hasattr(mytext, 'SetThickness'):
        mytxt.SetThickness(int(w/4))
    else:
        mytxt.SetTextThickness(int(w/4))
    pcb.Add(mytxt)
#

def getAngleRadians(p1,p2):
    #return math.degrees(math.atan2((p1.y-p2.y),(p1.x-p2.x)))
    return (math.atan2((p1.y-p2.y),(p1.x-p2.x)))
#

def rotatePoint(r,sa,da,c):
    # sa, da in radians
    x = c.x - math.cos(sa+da) * r
    y = c.y - math.sin(sa+da) * r
    if hasattr(pcbnew, 'wxPoint()'):
        wp=wxPoint(x,y)
    else:
        wp=VECTOR2I(int(x),int(y))
    return wp

def create_round_segments(pcb,sp,a1,ep,a2,cntr,rad,layer,width,Nn,N_SEGMENTS):
    start_point = sp
    end_point = ep
    pos = sp
    next_pos = ep
    a1 = getAngleRadians(cntr,sp)
    a2 = getAngleRadians(cntr,ep)
    wxLogDebug('a1:'+str(math.degrees(a1))+' a2:'+str(math.degrees(a2))+' a2-a1:'+str(math.degrees(a2-a1)),debug)
    if (a2-a1) > 0 and abs(a2-a1) > math.radians(180):
        deltaA = -(math.radians(360)-(a2-a1))/N_SEGMENTS
        wxLogDebug('deltaA reviewed:'+str(math.degrees(deltaA)),debug)
    elif (a2-a1) < 0 and abs(a2-a1) > math.radians(180):
        deltaA = (math.radians(360)-abs(a2-a1))/N_SEGMENTS
        wxLogDebug('deltaA reviewed2:'+str(math.degrees(deltaA)),debug)
    else:
        deltaA = (a2-a1)/N_SEGMENTS
    delta=deltaA
    wxLogDebug('delta:'+str(math.degrees(deltaA))+' radius:'+str(ToMM(rad)),debug)
    points = []
    #import round_trk; import importlib; importlib.reload(round_trk)
    for ii in range (N_SEGMENTS+1): #+1):
        points.append(pos)
        #t = create_Track(pos,pos)
        prv_pos = pos
        #pos = pos + fraction_delta
        #posPolar = cmath.polar(pos)
        #(rad) * cmath.exp(math.radians(deltaA)*1j) #cmath.rect(r, phi) : Return the complex number x with polar coordinates r and phi.
        #pos = wxPoint(posPolar.real+sp.x,posPolar.imag+sp.y)
        pos = rotatePoint(rad,a1,delta,cntr)
        delta=delta+deltaA
        wxLogDebug("pos:"+str(ToUnits(prv_pos.x))+":"+str(ToUnits(prv_pos.y))+";"+str(ToUnits(pos.x))+":"+str(ToUnits(pos.y)),debug)
    if  hasattr(pcbnew,'TRACK'):
        for i, p in enumerate(points):
            #if i < len (points)-1:
            if i < len (points)-2:
                t = create_Track(pcb,p,points[i+1],layer,width,Nn,True) #adding ts code to segments
        t = create_Track(pcb,points[-2],ep,layer,width,Nn,True) #avoiding rounding on last segment
    else:
        # for i, p in enumerate(points):
        #     #if i < len (points)-1:
        #     if i < len (points)-2:
        #         t = create_Arc(pcb,p,points[i+1],layer,width,Nn,True) #adding ts code to segments
        #t = create_Track(pcb,points[-2],ep,layer,width,Nn,True) #avoiding rounding on last segment
        p1 = points[0]
        p2 = points[-1]
        angle = a2-a1
        if angle > math.pi:
            angle -= 2*math.pi
        elif angle < -math.pi:
            angle += 2*math.pi
        #mp = mid_point(points[0],points[-1],(a2-a1))
        mp = mid_point(points[0],points[-1],(angle))
        
        # #t = create_Arc(pcb,points[0],points[-1],mp,layer,width,Nn,True)
        #p1= wxPoint(203200000, 127000000)
        #mp= wxPoint(221160512, 134439488)
        #p2= wxPoint(228600000, 152400000)
        #mp = mid_point(p1,p2,math.pi/2)
        #wx.LogMessage(str(mp))
        t = create_Arc(pcb,p1,p2,mp,layer,width,Nn,True)
        #t = create_Arc(pcb,points[-2],ep,layer,width,Nn,True) 
    return points[-1]
#
def mid_point(p1,p2,angle): #wxpoints,angle in radians
    """mid_point(prev_vertex,vertex,angle)-> mid_vertex
       returns mid point on arc of angle between prev_vertex and vertex"""
    #angle=math.radians(angle/2)
    angle=(angle/2)
    basic_angle=math.atan2(p2.y-p1.y,p2.x-p1.x)-math.pi/2
    shift=(1-math.cos(angle))*math.hypot(p2.y-p1.y,p2.x-p1.x)/2/math.sin(angle)
    if  hasattr(pcbnew,'wxPoint()'):
        midpoint=wxPoint((p2.x+p1.x)/2+shift*math.cos(basic_angle),(p2.y+p1.y)/2+shift*math.sin(basic_angle))
    else:
        midpoint=VECTOR2I(int((p2.x+p1.x)/2+shift*math.cos(basic_angle)),int((p2.y+p1.y)/2+shift*math.sin(basic_angle)))
    return midpoint
###
def create_round_points(pcb,sp,a1,ep,a2,cntr,rad,N_SEGMENTS):
    #TODO: Put some error checking in here...
    #Re-order the two converging tracks if we're selecting the startpoint
    start_point = sp
    end_point = ep
    pos = sp
    next_pos = ep
    wxLogDebug('sp:'+str(ToMM(sp))+';ep:'+str(ToMM(ep))+';cntr:'+str(ToMM(cntr)),debug)
    a1 = getAngleRadians(cntr,sp)
    a2 = getAngleRadians(cntr,ep)
    wxLogDebug('sp:'+str(ToMM(sp))+';ep:'+str(ToMM(ep))+';cntr:'+str(ToMM(cntr)),debug)
    wxLogDebug('a1:'+str(math.degrees(a1))+' a2:'+str(math.degrees(a2))+' a2-a1:'+str(math.degrees(a2-a1)),debug)
    #if a1 < 0:
    #    a1 = math.radians(180) -a1
    #if a2 < 0:
    #    a2 = math.radians(180) -a2
    if (a2-a1) > 0 and abs(a2-a1) > math.radians(180):
        deltaA = -(math.radians(360)-(a2-a1))/N_SEGMENTS
        wxLogDebug('deltaA reviewed:'+str(math.degrees(deltaA)),debug)
    elif (a2-a1) < 0 and abs(a2-a1) > math.radians(180):
        deltaA = (math.radians(360)-abs(a2-a1))/N_SEGMENTS
        wxLogDebug('deltaA reviewed2:'+str(math.degrees(deltaA)),debug)
    else:
        deltaA = (a2-a1)/N_SEGMENTS
    delta=deltaA
    wxLogDebug('delta:'+str(math.degrees(deltaA))+' radius:'+str(ToMM(rad)),debug)
    points = []
    #import round_trk; import importlib; importlib.reload(round_trk)
    for ii in range (N_SEGMENTS+1):
        points.append(pos)
        #t = create_Track(pos,pos)
        prv_pos = pos
        #pos = pos + fraction_delta
        #posPolar = cmath.polar(pos)
        #(rad) * cmath.exp(math.radians(deltaA)*1j) #cmath.rect(r, phi) : Return the complex number x with polar coordinates r and phi.
        #pos = wxPoint(posPolar.real+sp.x,posPolar.imag+sp.y)
        pos = rotatePoint(rad,a1,delta,cntr)
        delta=delta+deltaA
        wxLogDebug("pos:"+str(ToUnits(prv_pos.x))+":"+str(ToUnits(prv_pos.y))+";"+str(ToUnits(pos.x))+":"+str(ToUnits(pos.y)),debug)
    for i, p in enumerate(points):
        if i < len (points):
            t = create_Draw(pcb,p,p,B_CrtYd,0.5+i*0.05)
#
def not_eq(a,b):
    if abs(a-b) >= 1: #1nm
        return True
    else:
        return False
#

def getCircleCenterRadius(sp,ep,ip):
    #center
    # NB add always set float even if values are pcb internal Units!!!
    x1 = float(sp.x); y1 = float(sp.y)
    x2 = float(ep.x); y2 = float(ep.y)
    xi = float(ip.x); yi = float(ip.y)
    # mg formula
    cxN = (y2-y1)*(yi-y1)*(yi-y2)-(xi-x1)*x1*(yi-y2)+(xi-x2)*x2*(yi-y1)
    cxD = -x2*yi-xi*y1+x2*y1+xi*y2+x1*yi-x1*y2
    if cxD != 0:
        Cx = cxN/cxD
    else:
        #stop
        Cx= FromMM(100)
    wxLogDebug(str(ToMM(y1))+':'+str(ToMM(yi))+':'+str(ToMM(y2)),debug)
    wxLogDebug(str(ToMM(x1))+':'+str(ToMM(xi))+':'+str(ToMM(x2)),debug)
    if not_eq(yi,y1):
        Cy = y1 - (xi-x1)/(yi-y1)*(Cx-x1)
    elif yi==y1 and (yi!=y2):
        Cx = x1
        Cy = y2 - (xi-x2)/(yi-y2)*(Cx-x2)
    elif yi==y2 and (yi!=y1):
        Cx = x2
        Cy = y1 - (xi-x1)/(yi-y1)*(Cx-x1)
    else:
        Cy = FromMM(100)
    # import round_trk; reload(round_trk)
    # import round_trk; import importlib; importlib.reload(round_trk)
    
    radius = math.hypot(Cx-sp.x,Cy-sp.y)
    if  hasattr(pcbnew,'wxPoint()'):
        wp=wxPoint(Cx,Cy)
    else:
        wp=VECTOR2I(int(Cx),int(Cy))
    return wp, radius
#
def deleteSelectedTracks(pcb):
    tracks = pcb.GetTracks()
    tracks_cp = list(tracks)
    l = len (tracks_cp)
    if  hasattr(pcbnew,'TRACK'):
        track_item = pcbnew.TRACK
    else:
        track_item = pcbnew.PCB_TRACK
    for i in range(l):
        if type(tracks_cp[i]) is track_item and tracks_cp[i].IsSelected(): #item.GetNetname() == net_name:
            pcb.RemoveNative(tracks_cp[i])
    #for item in pcb.GetTracks():
    #    if type(item) is TRACK and item.IsSelected(): #item.GetNetname() == net_name:
    #        pcb.RemoveNative(item)
    #        #pcb.Delete(item)
#
def deleteListTracks(pcb,tracks):
    tracksToDel_cp = list(tracks)
    l = len (tracksToDel_cp)
    if  hasattr(pcbnew,'TRACK'):
        track_item = pcbnew.TRACK
    else:
        track_item = pcbnew.PCB_TRACK
    for i in range(l):
        if type(tracksToDel_cp[i]) is track_item: #item.GetNetname() == net_name:
            pcb.RemoveNative(tracksToDel_cp[i])
    #for item in tracks:
    #    if type(item) is TRACK: #item.GetNetname() == net_name:
    #        pcb.RemoveNative(item)
    #        #pcb.Delete(item)
#
def selectListTracks(pcb,tracks):
    if  hasattr(pcbnew,'TRACK'):
        track_item = pcbnew.TRACK
    else:
        track_item = pcbnew.PCB_TRACK
    for item in tracks:
        if type(item) is track_item:
            item.SetSelected()
#

def getSelTracksLength(pcb):
    ln = 0.
    if  hasattr(pcbnew,'TRACK'):
        track_item = pcbnew.TRACK
    else:
        track_item = pcbnew.PCB_TRACK
    for item in pcb.GetTracks():
        if type(item) is track_item and item.IsSelected():
            ln+=(item.GetLength())
    return(ln)
    #print(pcbnew.ToMM(ln))
#
##    def HitTest(self, *args): for Tracks and Vias

##-----------------------------------------------------------------------------------------------------
def Round_Selection(pcb,distI,segments,calc_len=None):
    global delete_before_connect
    tracks = []
    #print ("TRACKS WHICH MATCH CRITERIA:")
    if  hasattr(pcbnew,'TRACK'):
        track_item = pcbnew.TRACK
    else:
        track_item = pcbnew.PCB_TRACK
    for item in pcb.GetTracks():
        if type(item) is track_item and item.IsSelected(): #item.GetNetname() == net_name:
            tracks.append(item)
    wxLogDebug(str(len(tracks)),debug)
    
    # if len (tracks) == 0:
    #     if  hasattr(pcbnew,'TRACK'):
    #         track_item = pcbnew.DRAWSEGMENT
    #     else:
    #         track_item = pcbnew.PCB_TRACK
    #     for item in pcb.GetTracks():
    #         if type(item) is track_item and item.IsSelected(): #item.GetNetname() == net_name:
    #             tracks.append(item)
    #     wxLogDebug(str(len(tracks)),debug)        
    
    if len (tracks) == 2:            
        #add all the possible intersections to a unique set, for iterating over later
        intersections = set();  
        for t1 in range(len(tracks)):
            for t2 in range(t1+1, len(tracks)):
                #check if these two tracks share an endpoint
                # reduce it to a 2-part tuple so there are not multiple objects of the same point in the set
                if(tracks[t1].IsPointOnEnds(tracks[t2].GetStart())): 
                    intersections.add((tracks[t2].GetStart().x, tracks[t2].GetStart().y))
                if(tracks[t1].IsPointOnEnds(tracks[t2].GetEnd())):
                    intersections.add((tracks[t2].GetEnd().x, tracks[t2].GetEnd().y))
        if len(intersections)==1:
            for ip in intersections:
                (x,y) = ip
                wxLogDebug("intersections: "+str(ToUnits(x))+":"+str(ToUnits(y)),debug)
                #wx.LogMessage(str(tracks[0].GetStart()))
                if  hasattr(pcbnew,'wxPoint()'):
                    intersection = wxPoint(x,y)
                else:
                    intersection = VECTOR2I(int(x),int(y))
                if tracks[0].GetStart() == intersection:
                    first_trk_extNode = tracks[0].GetEnd()
                    #wx.LogMessage("tracks[0] external node="+str(ToUnits(tracks[0].GetEnd().x))+";"+str(ToUnits(tracks[0].GetEnd().y)))
                else:
                    first_trk_extNode = tracks[0].GetStart()
                    #wx.LogMessage("tracks[0] external node="+str(ToUnits(tracks[0].GetStart().x))+";"+str(ToUnits(tracks[0].GetStart().y)))
                if tracks[1].GetStart() == intersection:
                    last_trk_extNode = tracks[1].GetEnd()
                    #wx.LogMessage("tracks[1] external node="+str(ToUnits(tracks[1].GetEnd().x))+";"+str(ToUnits(tracks[1].GetEnd().y)))
                else:
                    last_trk_extNode = tracks[1].GetStart()
                    #wx.LogMessage("tracks[1] external node="+str(ToUnits(tracks[1].GetStart().x))+";"+str(ToUnits(tracks[1].GetStart().y)))
                angle1 = math.degrees((getTrackAngle(tracks[0],intersection)))
                angle2 = math.degrees((getTrackAngle(tracks[1],intersection)))
                end_coord1 = (distI) * cmath.exp(math.radians(angle1)*1j) #cmath.rect(r, phi) : Return the complex number x with polar coordinates r and phi.
                end_coord2 = (distI) * cmath.exp(math.radians(angle2)*1j)
                if  hasattr(pcbnew,'wxPoint()'):
                    startP = wxPoint(end_coord1.real+x,end_coord1.imag+y)
                    endP = wxPoint(end_coord2.real+x,end_coord2.imag+y)
                else:
                    startP = VECTOR2I(int(end_coord1.real+x),int(end_coord1.imag+y))
                    endP = VECTOR2I(int(end_coord2.real+x),int(end_coord2.imag+y))
                layer = tracks[0].GetLayer()
                width = ToMM(tracks[0].GetWidth())
                # if track_item != pcbnew.DRAWSEGMENT:
                Nname = tracks[0].GetNet() #.GetNetname()
                wxLogDebug("offset1 = "+str(ToUnits(startP)),debug) #+":"+str(ToUnits(endP)),debug)
                wxLogDebug("offset2 = "+str(ToUnits(endP)),debug) #end_coord2.real+x))+":"+str(ToUnits(end_coord2.imag+y)))
                center,radius = getCircleCenterRadius( startP,endP,intersection )
                #rad = math.hypot(center.x-startP.x,center.y-startP.y)
                wxLogDebug('radius'+str(ToMM(radius)),debug)
                wxLogDebug('center'+str(ToMM(center)),debug)
                # import round_trk; import importlib; importlib.reload(round_trk)
                lenT1 = GetTrackLength(tracks[0])
                dist1 = math.hypot(startP.y-intersection.y,startP.x-intersection.x)
                lenT2 = GetTrackLength(tracks[1])
                dist2 = math.hypot(endP.y-intersection.y,endP.x-intersection.x)
                wxLogDebug('Len T1 {0:.3f} mm, dist1 {1:.3f} mm, LenT2 {2:.3f} mm, dist2 {3:.3f} mm'.format(ToMM(lenT1),ToMM(dist1),ToMM(lenT2),ToMM(dist2)),debug)
                if show_points:
                    create_Draw(pcb,startP,startP,F_Mask,0.2)
                    create_Draw(pcb,intersection,intersection,Eco1_User,1.5)
                    create_Draw(pcb,endP,endP,B_Mask,0.2)
                    create_Draw(pcb,center,center,F_SilkS,2.)
                    create_round_points(pcb,startP,angle1,endP,angle2,center,radius,segments)
                    pcbnew.Refresh()
                    selectListTracks(pcb,tracks)
                if (lenT1 < dist1) or (lenT2 < dist2):
                    wxLogDebug('Segments too short compared to selected distance {0:.3f} mm'.format(ToMM(distI)),True)
                #elif track_item == pcbnew.DRAWSEGMENT: 
                else:
                    #create_Track(pcb,first_trk_extNode,startP,layer,width,Nname) #B_Cu,0.2)
                    #if delete_before_connect:
                    deleteListTracks(pcb,tracks)
                    create_Track(pcb,startP,first_trk_extNode,layer,width,Nname) #B_Cu,0.2)
                    #create_Draw(pcb,startP,startP,F_Mask,1.5)
                    newEP = create_round_segments(pcb,startP,angle1,endP,angle2,center,radius,layer,width,Nname,segments) #B_Cu,0.2)
                    #wxLogDebug(str(newEP)+':'+str(endP),True)
                    #create_Draw(pcb,endP,endP,B_Mask,1.9)
                    create_Track(pcb,endP,last_trk_extNode,layer,width,Nname) # B_Cu,0.2)
                    #create_Track(pcb,last_trk_extNode,endP,layer,width,Nname) # B_Cu,0.2)
                    #deleteSelectedTracks(pcb)
                    #selectListTracks(pcb,tracks)
                    w3 = 3*float(width)
                    rad = float(ToMM(radius))
                    wxLogDebug(str(w3),debug)
                    angle=angle1-angle2
                    if angle > math.degrees(math.pi):
                        angle -= math.degrees(2*math.pi)
                    elif angle < -math.degrees(math.pi):
                        angle += 2*math.degrees(math.pi)
                    
                    msg = u'Corner Radius: {0:.3f} mm'.format(rad)
                    msg+= u'\nAngle between tracks: {0:.1f} deg'.format(abs(angle))
                    if calc_len is not None:
                        msg+= u'\nSelected Tracks Length: {0:.3f} mm'.format(calc_len)
                    if rad < w3:
                        msg += u'\n\u2718 ALERT: Radius < 3 *(track width) !!!\n[{0:.3f}mm < 3*{1:.3f}mm]'.format(rad,width)
                    #else:
                    #    #msg = u'\n\u2714 Radius > 3 * (track width)'
                    #    msg = u'\u2714 Corner Radius: {0:.3f} mm'.format(rad)
                    
                    wxLogDebug(msg,True)
                    pcbnew.Refresh()
    # import round_trk; reload(round_trk)
    # import round_trk; import importlib; importlib.reload(round_trk)
    else:
        wxLogDebug("you must select two tracks (only)",not debug)
#
def Delete_Segments(pcb, track=None):
    global delete_before_connect
    tracks = []
    tracksToKeep = []
    if track is None:
        if  hasattr(pcbnew,'TRACK'):
            track_item = pcbnew.TRACK
        else:
            track_item = pcbnew.PCB_TRACK
        for item in pcb.GetTracks():
            if type(item) is track_item and item.IsSelected():
                tracks.append(item)
        wxLogDebug('tracks selected: '+str(len(tracks)),debug2)
    else:
        tracks.append(track)
    if len (tracks) == 1 and delete_before_connect:            
        Netname = tracks[0].GetNetname()
        tsc = 0
        for c in Netname:
            tsc = tsc + ord(c)
        nseg = 0
        tracksToDel = []
        for track in pcb.GetTracks():
            if hasattr(track,'GetTimeStamp'):
                tsd = track.GetTimeStamp()
            else:
                tsd = track.m_Uuid.AsLegacyTimestamp()
            wxLogDebug('tracks ts: '+str(tsc)+';'+str(tsd),debug2)
            if tsd == tsc and tsd != 0:
                tracksToDel.append(track)
                #pcb.RemoveNative(track)
                nseg+=1
        if nseg > 0:
            tracksToDel_cp = list(tracksToDel)
            l = len (tracksToDel_cp)
            #for track in tracksToDel:
            for i in range(l):
                pcb.RemoveNative(tracksToDel_cp[i])
            wxLogDebug(u'\u2714 Round Segments on Track Net Deleted',True)
    else:
        Netname = tracks[0].GetNetname()
        tsc = 0
        for c in Netname:
            tsc = tsc + ord(c)
        nseg = 0
        tracksToDel = []
        if  hasattr(pcbnew,'TRACK'):
            track_item = pcbnew.TRACK
        else:
            track_item = pcbnew.PCB_TRACK
        for track in pcb.GetTracks():
            if type(track) is track_item and track.IsSelected():
                if hasattr(track,'GetTimeStamp'):
                    tsd = track.GetTimeStamp()
                else:
                    tsd = track.m_Uuid.AsLegacyTimestamp()
                wxLogDebug('tracks ts: '+str(tsc)+';'+str(tsd),debug2)
                if tsd == tsc and tsd != 0:
                    tracksToDel.append(track)
                    #pcb.RemoveNative(track)
                    nseg+=1
                else:
                    tracksToKeep.append(track)
        if nseg > 0:
            tracksToDel_cp = list(tracksToDel)
            l = len (tracksToDel_cp)
            for i in range(l):
                pcb.RemoveNative(tracksToDel_cp[i])
            #for track in tracksToDel:
            #    pcb.RemoveNative(track)
            wxLogDebug(u'\u2714 Round Segments on Selected Track deleted',True)
        elif delete_before_connect:
            wxLogDebug(u'\u2718 you must select One track only',not debug)
        return tracksToKeep
#
def Connect_Segments(pcb):
    tracks = []
    tracksToKeep = []
    if  hasattr(pcbnew,'TRACK'):
        track_item = pcbnew.TRACK
    else:
        track_item = pcbnew.PCB_TRACK
    for item in pcb.GetTracks():
        if type(item) is track_item and item.IsSelected():
            tracks.append(item)
    wxLogDebug(str(len(tracks)),debug)
        
    if len (tracks) >= 2:
        pi_exists = True
        if len (tracks) > 2:
            tracksToKeep = Delete_Segments(pcb)
            if len (tracksToKeep) == 2:
                tracks[0] = tracksToKeep[0]
                tracks[1] = tracksToKeep[1]
            else:
                wxLogDebug(u'\u2718 wrong selection (error)\nselect Only one corner to be straighten',not debug)
        else:
            Delete_Segments(pcb,tracks[0])
        #getting points
        if tracks[0].GetStart().x < tracks[0].GetEnd().x:
            first_trk_startP = tracks[0].GetStart()
            first_trk_endP = tracks[0].GetEnd()
        else:
            first_trk_startP = tracks[0].GetEnd()
            first_trk_endP = tracks[0].GetStart()
        if tracks[1].GetStart().x < tracks[1].GetEnd().x:
            last_trk_startP = tracks[1].GetStart()
            last_trk_endP = tracks[1].GetEnd()
        else:
            last_trk_startP = tracks[1].GetEnd()
            last_trk_endP = tracks[1].GetStart()
        wxLogDebug('sp1:'+str(first_trk_startP)+';'+str(first_trk_endP),debug2)
        wxLogDebug('sp2:'+str(last_trk_startP)+';'+str(last_trk_endP),debug2)
        x1 = float(first_trk_startP.x); y1 = float(first_trk_startP.y)
        x3 = float(first_trk_endP.x); y3 = float(first_trk_endP.y)
        x2 = float(last_trk_startP.x); y2 = float(last_trk_startP.y)
        x4 = float(last_trk_endP.x); y4 =   float(last_trk_endP.y)
        if (x3!=x1) and (x4!=x2):
            N = y2-y1-x2*(y4-y2)/(x4-x2)+x1*(y3-y1)/(x3-x1)
            D = (y3-y1)/(x3-x1)-(y4-y2)/(x4-x2)
            xi = N/D
            yi = y1+(y3-y1)/(x3-x1)*(xi-x1)
        elif (x3==x1):
            xi = x1
            yi = y2+(y4-y2)/(x4-x2)*(x1-x2)
        elif (x4 == x2):
            xi = x2
            yi = y1 + (y3-y1)/(x3-x1)*(x2-x1)
        else:
            pi_exists = False
            wxLogDebug(u'\u2718 intersection point doesn\'t exist',not debug)
        if pi_exists:
            wxLogDebug('pi:'+str(wxPoint(xi,yi)),debug2) #xi)+';'+str(yi),debug1)
            wxLogDebug('sp1:('+str(ToMM(x1))+','+str(ToMM(y1))+')'+\
                    ';('+str(ToMM(x2))+','+str(ToMM(y2))+')',debug2)
            wxLogDebug('sp2:('+str(ToMM(x3))+','+str(ToMM(y3))+')'+\
                    ';('+str(ToMM(x4))+','+str(ToMM(y4))+')',debug2)
            wxLogDebug('pi:('+str(ToMM(xi))+','+str(ToMM(yi))+')',debug2)
            if hasattr(pcbnew,'wxPoint()'):
                pi = wxPoint(xi,yi)
            else:
                pi = VECTOR2I(int(xi),int(yi))
            if show_points2:
                #create_Text(pcb, txt, p, w)
                create_Text(pcb,'1',wxPoint(x1,y1),FromMM(1.0),pcbnew.F_SilkS)
                create_Text(pcb,'2',wxPoint(x2,y2),FromMM(1.0),pcbnew.F_SilkS)
                create_Text(pcb,'3',wxPoint(x3,y3),FromMM(1.0),pcbnew.F_SilkS)
                create_Text(pcb,'4',wxPoint(x4,y4),FromMM(1.0),pcbnew.F_SilkS)
                create_Text(pcb,'C',wxPoint(xi,yi),FromMM(2.0),pcbnew.B_SilkS)
            wxLogDebug('dp1,pi)'+str(distance(wxPoint(x1,y1),pi)),debug2)
            wxLogDebug('dp3,pi)'+str(distance(wxPoint(x3,y3),pi)),debug2)
            if hasattr(pcbnew, 'EDA_RECT'): # kv5,kv6
                if distance(wxPoint(x1,y1),pi) > distance(wxPoint(x3,y3),pi):
                    tracks[0].SetStart(wxPoint(x1,y1))
                    tracks[0].SetEnd(pi)
                else:
                    tracks[0].SetStart(wxPoint(x3,y3))
                    tracks[0].SetEnd(pi)
                wxLogDebug('dp2,pi)'+str(distance(wxPoint(x2,y2),pi)),debug2)
                wxLogDebug('dp4,pi)'+str(distance(wxPoint(x4,y4),pi)),debug2)
                if distance(wxPoint(x2,y2),pi) > distance(wxPoint(x4,y4),pi):
                    tracks[1].SetStart(wxPoint(x2,y2))
                    tracks[1].SetEnd(pi)
                else:
                    tracks[1].SetStart(wxPoint(x4,y4))
                    tracks[1].SetEnd(pi)
            elif hasattr(pcbnew,'wxPoint()'): #kv7
                if distance(wxPoint(x1,y1),pi) > distance(wxPoint(x3,y3),pi):
                    tracks[0].SetStart(VECTOR2I(wxPoint(x1,y1)))
                    tracks[0].SetEnd(VECTOR2I(pi))
                else:
                    tracks[0].SetStart(VECTOR2I(wxPoint(x3,y3)))
                    tracks[0].SetEnd(VECTOR2I(pi))
                wxLogDebug('dp2,pi)'+str(distance(wxPoint(x2,y2),pi)),debug2)
                wxLogDebug('dp4,pi)'+str(distance(wxPoint(x4,y4),pi)),debug2)
                if distance(wxPoint(x2,y2),pi) > distance(wxPoint(x4,y4),pi):
                    tracks[1].SetStart(VECTOR2I(wxPoint(x2,y2)))
                    tracks[1].SetEnd(VECTOR2I(pi))
                else:
                    tracks[1].SetStart(VECTOR2I(wxPoint(x4,y4)))
                    tracks[1].SetEnd(VECTOR2I(pi))            
            else:
                if distance(VECTOR2I(int(x1),int(y1)),pi)> distance(VECTOR2I(int(x3),int(y3)),pi):
                    tracks[0].SetStart(VECTOR2I(int(x1),int(y1)))
                    tracks[0].SetEnd(pi)
                else:
                    tracks[0].SetStart(VECTOR2I(int(x3),int(y3)))
                    tracks[0].SetEnd(pi)
                wxLogDebug('dp2,pi)'+str(distance(VECTOR2I(int(x2),int(y2)),pi)),debug2)
                wxLogDebug('dp4,pi)'+str(distance(VECTOR2I(int(x4),int(y4)),pi)),debug2)
                if distance(VECTOR2I(int(x2),int(y2)),pi) > distance(VECTOR2I(int(x4),int(y4)),pi):
                    tracks[1].SetStart(VECTOR2I(int(x2),int(y2)))
                    tracks[1].SetEnd(pi)
                else:
                    tracks[1].SetStart(VECTOR2I(int(x4),int(y4)))
                    tracks[1].SetEnd(pi)            
            pcbnew.Refresh()
    else:
        wxLogDebug(u'\u2718 you must select two tracks only',not debug)
#
