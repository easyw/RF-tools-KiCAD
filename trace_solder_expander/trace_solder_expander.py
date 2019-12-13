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


# some source tips @
# https://github.com/bpkempke/kicad-scripts
# https://github.com/MitjaNemec/Kicad_action_plugins
# https://github.com/jsreynaud/kicad-action-scripts

# import trace_solder_expansion; reload(trace_solder_expansion)

import sys
import os
from pcbnew import *
import wx
import pcbnew
import math

debug = False #True
def wxLogDebug(msg,show):
    """printing messages only if show is omitted or True"""
    if show:
        wx.LogMessage(msg)
#
#if (sys.version[0]) == '2':
#    from .SolderExpanderDlg import SolderExpanderDlg
#else:
#    from .SolderExpanderDlg_py3 import SolderExpanderDlg_y3
#from .SolderExpanderDlg import SolderExpanderDlg
from . import SolderExpanderDlg


# import trace_solder_expansion; reload(trace_solder_expansion)

# Python plugin stuff

class SolderExpander_Dlg(SolderExpanderDlg.SolderExpanderDlg):
    # from https://github.com/MitjaNemec/Kicad_action_plugins
    # hack for new wxFormBuilder generating code incompatible with old wxPython
    # noinspection PyMethodOverriding
    def SetSizeHints(self, sz1, sz2):
        if sys.version_info[0] == 2:
            # wxPython 2
            self.SetSizeHintsSz(sz1, sz2)
        else:
            # wxPython 3
            super(SolderExpander_Dlg, self).SetSizeHints(sz1, sz2)

    def onDeleteClick(self, event):
        return self.EndModal(wx.ID_DELETE)

    def __init__(self,  parent):
        SolderExpanderDlg.SolderExpanderDlg.__init__(self, parent)
        self.m_buttonDelete.Bind(wx.EVT_BUTTON, self.onDeleteClick)
        self.SetMinSize(self.GetSize())
    
#

class Solder_Expander(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Solder Mask Expander for Tracks\nversion 1.7"
        self.category = "Modify PCB"
        self.description = "Solder Mask Expander for selected Tracks on the PCB"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./soldermask_clearance.png")
        self.show_toolbar_button = True
        
    def Warn(self, message, caption='Warning!'):
        dlg = wx.MessageDialog(
            None, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

    def CheckInput(self, value, data):
        val = None
        try:
            val = float(value.replace(',','.'))
            if val <= 0:
                raise Exception("Invalid")
        except:
            self.Warn(
                "Invalid parameter for %s: Must be a positive number" % data)
            val = None
        return val

    def Run(self):
        #import pcbnew
        #pcb = pcbnew.GetBoard()
        # net_name = "GND"
        #aParameters = SolderExpanderDlg(None)
        _pcbnew_frame = [x for x in wx.GetTopLevelWindows() if x.GetTitle().lower().startswith('pcbnew')][0]
        aParameters = SolderExpander_Dlg(_pcbnew_frame)
        aParameters.m_clearanceMM.SetValue("0.2")
        aParameters.m_bitmap1.SetBitmap(wx.Bitmap( os.path.join(os.path.dirname(os.path.realpath(__file__)), "soldermask_clearance_help.png") ) )
        modal_result = aParameters.ShowModal()
        clearance = FromMM(self.CheckInput(aParameters.m_clearanceMM.GetValue(), "extra clearance from track width"))
        if clearance is not None:
            pcb = pcbnew.GetBoard()
            if modal_result == wx.ID_OK:
                #pcb = pcbnew.GetBoard()
                tracks=getSelTracks(pcb)
                if len(tracks) >0: #selected tracks >0
                    solderExpander(pcb,tracks,clearance)
                else:
                    pads=[]
                    for item in pcb.GetPads():
                        if item.IsSelected():
                            pads.append(item)
                    if len(pads) == 1:
                        tracks=[]
                        tracks = find_Tracks_inNet_Pad(pcb,pads[0])
                        c_tracks = get_contiguous_tracks(pcb,tracks,pads[0])
                        solderExpander(pcb,c_tracks,clearance)
                    else:
                        wx.LogMessage("Solder Mask Expander:\nSelect Tracks\nor One Pad to select connected Tracks")
                        
                #solderExpander(clearance)
            elif modal_result == wx.ID_DELETE:
                Delete_Segments(pcb)
                #wx.LogMessage('Solder Mask Segments on Track Net Deleted')
            else:
                None  # Cancel
        else:
            None  # Invalid input
        aParameters.Destroy()
#
def selectListTracks(pcb,tracks):
    for item in tracks:
        if type(item) is TRACK:
            item.SetSelected()
#
#
#def getSelTracksLength(pcb):
#    ln = 0.
#    for item in pcb.GetTracks():
#        if type(item) is pcbnew.TRACK and item.IsSelected():
#            ln+=(item.GetLength())
#    return(ln)
#    #print(pcbnew.ToMM(ln))
#
def get_contiguous_tracks(pcb,trks,pad):
    LinePoints = []
    LineSegments=[]
    
    #start_point = ToMM(pad.GetPosition())
    startp = (pad.GetPosition())
    start_point = ((startp.x),(startp.y))
    for t in (trks):
        LinePoints.append((t.GetStart().x,t.GetStart().y))
        LinePoints.append((t.GetEnd().x,  t.GetEnd().y))
    wxLogDebug('Points '+str(LinePoints),debug)
    l= len(LinePoints)
    for i in range(0,l,2):
        LineSegments.append((LinePoints[i],LinePoints[i+1]))
    wxLogDebug(str(LineSegments),debug)

    #segments = [(1, 2), (2, 3), (4, 5), (6, 5), (7, 6)]
    #start_point=(4,5)
    #segments_start=segments
    
    segments = LineSegments
    groups=[]
    found=False
    for s in segments:
        found=False
        for g in groups:
            for sCmp in g:
                wxLogDebug('sCmp: '+(str(sCmp)),debug)
                wxLogDebug('s: '+(str(s)),debug)
                if isConn(sCmp,s):  #confronto start e end
                    g.append(s)
                    found=True
                    break;
            if (found):
                break;
        if(not found):
            groups.append([s])
    wxLogDebug('groups: '+(str(groups)),debug)
    wxLogDebug('len groups: '+(str(len(groups))),debug)
    l = 0
    lens = []
    for g in groups:
        lens.append(len(g))
        if l<len(g):
            l = len(g)
    wxLogDebug('len max groups: '+str(l),debug)
    wxLogDebug('lens in groups: '+str(lens),debug)
    found=False
    
    res_g=[]
    wxLogDebug('start '+str((start_point,start_point)),debug)
    wxLogDebug('start '+str(s),debug)
    
    #for g,i in enumerate(groups):
    i=0
    while (i+1) < len (groups):
        found = False
        for s in groups[i]:
            for r in groups[i+1]:
                wxLogDebug('s: '+str(s)+';r: '+str(r),debug)
                if isConn(r,s):
                    for r1 in groups[i+1]:
                        groups[i].append(r1)
                    groups.pop(i+1)
                    found=True
                    break
            if found:
                break
        if not found:
            i+=1
        else:
            i=0
    l = 0
    lens = []
    for g in groups:
        lens.append(len(g))
        if l<len(g):
            l = len(g)
    wxLogDebug('groups merged: '+(str(groups)),debug)
    wxLogDebug('len max groups merged: '+str(l),debug)
    wxLogDebug('lens in groups merged: '+str(lens),debug)
    
    for g in groups:
        for s in g:
            if isConn((start_point,start_point),s):
                res_g = g
                found = True
                break
    wxLogDebug('start '+str(start_point),debug)
    group = res_g
    wxLogDebug('group '+str(res_g),debug)
    wxLogDebug('len group: '+(str(len(group))),debug)
    trks_connected=[]
    for seg in res_g:
        for t in trks:
            tseg = ((t.GetStart().x,t.GetStart().y),(t.GetEnd().x,t.GetEnd().y))
            wxLogDebug('seg '+str(seg),debug)
            wxLogDebug('tseg '+str(tseg),debug)
            if isConn(seg,tseg):
                if t not in trks_connected:
                    trks_connected.append(t)
                    wxLogDebug('t added: '+(str(tseg)),debug)
    wxLogDebug('trks_connected '+str(len(trks_connected)),debug)
    return trks_connected
#
def isEq (p1,p2):
    epsilon = FromMM(0.003) # tolerance 5 nm
    delta = math.hypot(p1[0]-p2[0],p1[1]-p2[1])
    wxLogDebug('delta: '+str(delta)+'eps: '+str(epsilon),debug)
    #wxLogDebug('epsilon: '+str(epsilon),debug)
    if delta <= epsilon:
        wxLogDebug('connected',debug)
        return True
    else:
        return False
#

def isConn(s1,s2):
    #if s1[0] == s2[0] or s1[1] == s2[1]:
    if isEq(s1[0],s2[0]) or isEq(s1[1],s2[1]):
        return True
    #elif s1[0] == s2[1] or s1[1] == s2[0]:
    elif isEq(s1[0],s2[1]) or isEq(s1[1],s2[0]):
        return True
    return False
#

def getSelTracks(pcb):
    tracks=[]
    for item in pcb.GetTracks():
        if type(item) is pcbnew.TRACK and item.IsSelected():
            tracks.append(item)
    return tracks
#
def find_Tracks_inNet_Pad(pcb,pad):
    track_list = []
    # get list of all selected pads
    #selected_pads = [pad1, pad2]
    # get the net the pins are on
    net = pad.GetNetname()
    # find all tracks 
    tracks = pcb.GetTracks()
    # find all tracks on net
    tracks_on_net = []
    for track in tracks:
        track_net_name = track.GetNetname()
        if track_net_name == net:
            tracks_on_net.append(track)
    return tracks_on_net
#

def solderExpander(pcb,tracks,clearance):
        mask_width = clearance #FromMM(.5) # msk espansion value each side
        #mask_layer = pcbnew.F_Mask
        
        # pcb = LoadBoard(in_filename)
        #pcb = pcbnew.GetBoard() 
        
        ToUnits=pcbnew.ToMM #ToMils
        FromUnits=pcbnew.FromMM #Mils
        
        for item in tracks:
            start = item.GetStart()
            end = item.GetEnd()
            width = item.GetWidth()
            layerId = item.GetLayer()
            layer = item.GetLayerSet()
            layerN = item.GetLayerName()
            layer = pcb.GetLayerID(layerN)
            track_net_name = item.GetNetname()
            ts = 0
            for c in track_net_name:
                ts = ts + ord(c)
            #wx.LogMessage("LayerName"+str(layer))

            if layerId == pcbnew.F_Cu:
                mask_layer = pcbnew.F_Mask
            elif layerId == pcbnew.B_Cu: #'B_Cu':
                mask_layer = pcbnew.B_Mask
            else: #we shouldn't arrive here
                mask_layer = pcbnew.F_Mask
            wxLogDebug(" * Track: %s to %s, width %f mask_width %f" % (ToUnits(start),ToUnits(end),ToUnits(width), ToUnits(mask_width)),debug)
            #print (" * Track: %s to %s, width %f mask_width %f" % (ToUnits(start),ToUnits(end),ToUnits(width), ToUnits(mask_width)))
            new_soldermask_line = pcbnew.DRAWSEGMENT(pcb)
            new_soldermask_line.SetStart(start)
            new_soldermask_line.SetEnd(end)
            new_soldermask_line.SetWidth(width+2*mask_width) #FromUnits(int(mask_width)))
            new_soldermask_line.SetLayer(mask_layer) #pcbnew.F_Mask) #pcb.GetLayerID(mask_layer))
            # again possible to mark via as own since no timestamp_t binding kicad v5.1.4
            new_soldermask_line.SetTimeStamp(ts)  # adding a unique number (this netname) as timestamp to mark this via as generated by this script on this netname
            pcb.Add(new_soldermask_line)
            #break;
        pcbnew.Refresh()        
#

def Delete_Segments(pcb):
    draws = []
    #print ("TRACKS WHICH MATCH CRITERIA:")
    for item in pcb.GetDrawings():
    #for item in pcb.GetTracks():
        if type(item) is DRAWSEGMENT and item.IsSelected(): #item.GetNetname() == net_name:
            draws.append(item)
    wxLogDebug(str(len(draws)),debug)
        
    if len (draws) == 1:            
        tsd = draws[0].GetTimeStamp()
        wxLogDebug(str(tsd),debug)
        if tsd != 0:
            target_draws = filter(lambda x: (x.GetTimeStamp() == tsd), pcb.GetDrawings())
            #wx.LogMessage(str(len(target_tracks)))
            target_draws_cp = list(target_draws)
            for i in range(l):
                pcb.RemoveNative(target_draws_cp[i])
            #for draw in target_draws:
            #    #if via.GetTimeStamp() == 55:
            #    pcb.RemoveNative(draw)
                #wx.LogMessage('removing via')
            #pcbnew.Refresh()
            wxLogDebug(u'\u2714 Mask Segments Deleted',True)
        else:
            wxLogDebug(u'\u2718 you must select only Mask segment\n generated by this tool',not debug)
    else:
        #msg = u'\n\u2714 Radius > 3 * (track width)'
        wxLogDebug(u'\u2718 you must select One Mask segment only',not debug)
#
#Solder_Expander().register()

