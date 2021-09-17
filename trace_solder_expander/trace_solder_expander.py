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
import uuid

debug = False #True
def wxLogDebug(msg,show):
    """printing messages only if show is omitted or True"""
    if show:
        wx.LogMessage(msg)
#
def find_pcbnew_w():
    windows = wx.GetTopLevelWindows()
    pcbneww = [w for w in windows if "pcbnew" in w.GetTitle().lower()]
    if len(pcbneww) != 1:
        return None
    return pcbneww[0]
#

#if (sys.version[0]) == '2':
#    from .SolderExpanderDlg import SolderExpanderDlg
#else:
#    from .SolderExpanderDlg_py3 import SolderExpanderDlg_y3
#from .SolderExpanderDlg import SolderExpanderDlg
from . import SolderExpanderDlg

ToUnits=pcbnew.ToMM #ToMils
FromUnits=pcbnew.FromMM #Mils

global discretize
discretize = False
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
        global discretize
        SolderExpanderDlg.SolderExpanderDlg.__init__(self, parent)
        self.m_buttonDelete.Bind(wx.EVT_BUTTON, self.onDeleteClick)
        self.SetMinSize(self.GetSize())
        #if self.m_checkBoxD.IsChecked():
        #    discretize = True
        #    #wx.LogMessage(str(discretize) + ' 0')
        #else:
        #    discretize = False
    
#

class Solder_Expander(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Solder Mask Expander for Tracks\n version 2.3"
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
        # _pcbnew_frame = [x for x in wx.GetTopLevelWindows() if x.GetTitle().lower().startswith('pcbnew')][0]
        global discretize
        
        # _pcbnew_frame = [x for x in wx.GetTopLevelWindows() if x.GetName() == 'PcbFrame'][0]
        pcbnew_window = find_pcbnew_w()
        aParameters = SolderExpander_Dlg(pcbnew_window)
        aParameters.m_clearanceMM.SetValue("0.2")
        aParameters.m_bitmap1.SetBitmap(wx.Bitmap( os.path.join(os.path.dirname(os.path.realpath(__file__)), "soldermask_clearance_help.png") ) )
        pcb = pcbnew.GetBoard()
        if not(hasattr(pcbnew,'DRAWSEGMENT')):
        #if hasattr(pcb, 'm_Uuid'):
            aParameters.m_buttonDelete.Disable()
            aParameters.m_buttonDelete.Hide()
            aParameters.m_staticText1011.Hide()
            aParameters.m_checkBoxD.SetToolTip( u"check this to discretize arcs with segments" )
            #if aParameters.m_checkBoxD.IsChecked():
            #    discretize = True
            #    wx.LogMessage(str(discretize) + ' 1')
            #else:
            #    discretize = False
        else:
            aParameters.m_checkBoxD.Hide()
            aParameters.m_staticText10111.Hide()
        modal_result = aParameters.ShowModal()
        clearance = FromMM(self.CheckInput(aParameters.m_clearanceMM.GetValue(), "extra clearance from track width"))
        
        if not(hasattr(pcbnew,'DRAWSEGMENT')):
        #if hasattr(pcb, 'm_Uuid'):
            aParameters.m_buttonDelete.Disable()
            aParameters.m_buttonDelete.Hide()
            aParameters.m_staticText1011.Hide()
            discretize = aParameters.m_checkBoxD.GetValue()
            #if aParameters.m_checkBoxD.IsChecked():
            #    discretize = True
            #    wx.LogMessage(str(discretize) + ' 1')
            #else:
            #    discretize = False
        
        if clearance is not None:
            if modal_result == wx.ID_OK:
                #pcb = pcbnew.GetBoard()
                tracks=getSelTracks(pcb)
                arcs=getSelArcs(pcb)
                if len(tracks) >0 or len(arcs) >0 : #selected tracks >0
                    solderExpander(pcb,tracks,clearance)
                    solderExpander(pcb,arcs,clearance)
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
                        solderExpander(pcb,arcs,clearance)
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
    if  hasattr(pcbnew,'TRACK'):
        track_item = pcbnew.TRACK
    else:
        track_item = pcbnew.PCB_TRACK
    for item in pcb.GetTracks():
        if type(item) is track_item and item.IsSelected():
            tracks.append(item)
    return tracks
#
def getSelArcs(pcb):
    tracks=[]
    if  hasattr(pcbnew,'TRACK'):
        track_item = pcbnew.TRACK
    else:
        track_item = pcbnew.PCB_ARC
        for item in pcb.GetTracks():
            if type(item) is track_item and item.IsSelected():
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
def not_eq(a,b):
    if abs(a-b) >= 1: #1nm
        return True
    else:
        return False
#
# Function to find the circle on
# which the given three points lie
def getCircleCenterRadius(sp,ep,ip):
    # findCircle(x1, y1, x2, y2, x3, y3) :
    # NB add always set float even if values are pcb internal Units!!!
    x1 = float(sp.x); y1 = float(sp.y)
    x2 = float(ep.x); y2 = float(ep.y)
    x3 = float(ip.x); y3 = float(ip.y)
    
    x12 = x1 - x2;
    x13 = x1 - x3;
    y12 = y1 - y2;
    y13 = y1 - y3;
    y31 = y3 - y1;
    y21 = y2 - y1;
    x31 = x3 - x1;
    x21 = x2 - x1;
    
    # x1^2 - x3^2
    sx13 = math.pow(x1, 2) - math.pow(x3, 2);
    # y1^2 - y3^2
    sy13 = math.pow(y1, 2) - math.pow(y3, 2);
    sx21 = math.pow(x2, 2) - math.pow(x1, 2);
    sy21 = math.pow(y2, 2) - math.pow(y1, 2);
    
    f = (((sx13) * (x12) + (sy13) *
      (x12) + (sx21) * (x13) +
      (sy21) * (x13)) // (2 *
      ((y31) * (x12) - (y21) * (x13))));
          
    g = (((sx13) * (y12) + (sy13) * (y12) +
      (sx21) * (y13) + (sy21) * (y13)) //
      (2 * ((x31) * (y12) - (x21) * (y13))));
    
    c = (-math.pow(x1, 2) - math.pow(y1, 2) - 2 * g * x1 - 2 * f * y1);
    
    # eqn of circle be x^2 + y^2 + 2*g*x + 2*f*y + c = 0
    # where centre is (h = -g, k = -f) and
    # radius r as r^2 = h^2 + k^2 - c
    h = -g;
    k = -f;
    sqr_of_r = h * h + k * k - c;
    # r is the radius
    r = round(math.sqrt(sqr_of_r), 5);
    Cx = h
    Cy = k
    radius = r
    return wxPoint(Cx,Cy), radius
#
def create_Solder(pcb,p1,p2,lyr=None,w=None,Nn=None,Ts=None,pcbG=None):
    #draw segment to test or from Arc
    #new_line = pcbnew.DRAWSEGMENT(pcb)
    if  hasattr(pcbnew,'TRACK'):
        new_line = pcbnew.TRACK(pcb)
    else:
        #new_shape = pcbnew.S_SEGMENT()
        new_line = PCB_SHAPE() 
        # new_shape = pcbnew.PCB_SHAPE()
        # new_line = pcbnew.Cast_to_PCB_SHAPE(new_shape)
        #new_soldermask_shape = PCB_SHAPE()
        #new_soldermask_line = pcbnew.Cast_to_PCB_SHAPE(new_soldermask_shape)
        #new_line = PCB_TRACK(new_shape)
    
    new_line.SetStart(p1)
    new_line.SetEnd(p2)
    if w is None:
        new_line.SetWidth(FromUnits(1.5)) #FromUnits(int(mask_width)))
    else:
        #wx.LogMessage(str(w))
        new_line.SetWidth(w) #FromUnits(w))
    if lyr is None:
        lyr = F_SilkS
    elif lyr is pcbnew.F_Cu:
        lyr is pcbnew.F_Mask
    elif lyr is pcbnew.B_Cu:
        lyr is pcbnew.B_Mask
    # if Nn is not None:
    #     new_line.SetNet(Nn)
    #     #new_line.SetNetname(Nn)
    new_line.SetLayer(lyr) #pcbnew.F_SilkS) #pcb.GetLayerID(mask_layer))
    if Ts is not None and hasattr(pcbnew,'TRACK'):
        tsc = 0
        Nname = new_line.GetNetname()
        for c in Nname:
            tsc = tsc + ord(c)
        if hasattr(new_line, 'SetTimeStamp'):
            new_line.SetTimeStamp(tsc)  # adding a unique number (this netname) as timestamp to mark this segment as generated by this script on this netname
    pcb.Add(new_line)
    if pcbG is not None:
        pcbG.AddItem(new_line)
    
    return new_line
#
def solderExpander(pcb,tracks,clearance):
    global discretize
    # wx.LogMessage(str(discretize) + ' 2')
    mask_width = clearance #FromMM(.5) # msk espansion value each side
    #mask_layer = pcbnew.F_Mask
    
    # pcb = LoadBoard(in_filename)
    #pcb = pcbnew.GetBoard() 
    
    #ToUnits=pcbnew.ToMM #ToMils
    #FromUnits=pcbnew.FromMM #Mils
    
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
        if hasattr(pcbnew,'DRAWSEGMENT'):
            new_soldermask_line = pcbnew.DRAWSEGMENT(pcb)
            new_soldermask_line.SetStart(start)
            new_soldermask_line.SetEnd(end)
            new_soldermask_line.SetWidth(width+2*mask_width) #FromUnits(int(mask_width)))
            new_soldermask_line.SetLayer(mask_layer) #pcbnew.F_Mask) #pcb.GetLayerID(mask_layer))
            # again possible to mark via as own since no timestamp_t binding kicad v5.1.4
            if hasattr(new_soldermask_line, 'SetTimeStamp'):
                new_soldermask_line.SetTimeStamp(ts)  # adding a unique number (this netname) as timestamp to mark this via as generated by this script on this netname
            pcb.Add(new_soldermask_line)
        elif type(item) is pcbnew.PCB_TRACK: #kicad 5.99
            #new_soldermask_shape = PCB_SHAPE()
            #new_soldermask_line = pcbnew.Cast_to_PCB_SHAPE(new_soldermask_shape)
            new_soldermask_line = PCB_SHAPE()
            new_soldermask_line.SetStart(start)
            new_soldermask_line.SetEnd(end)
            new_soldermask_line.SetWidth(width+2*mask_width)
            new_soldermask_line.SetLayer(mask_layer) #pcbnew.F_Mask) #pcb.GetLayerID(mask_layer))
            # again possible to mark via as own since no timestamp_t binding kicad v5.1.4
            if hasattr(new_soldermask_line, 'SetTimeStamp'):
                new_soldermask_line.SetTimeStamp(ts)  # adding a unique number (this netname) as timestamp to mark this via as generated by this script on this netname
            pcb.Add(new_soldermask_line)
        else: #PCB_ARC kicad 5.99
            #new_soldermask_line = PCB_ARC(PCB_SHAPE())
            #new_soldermask_line.SetMid(item.GetMid())
            #wxLogDebug(str(item.GetMid())+' mid',True)
            md = item.GetMid()
            #wxLogDebug(str(cnt)+' center, radius '+str(rad),True)
            netName = None
            width_new = width +2*mask_width
            cnt, rad = getCircleCenterRadius(start,end,md)
            if discretize:
                segNBR = 16
                groupName = uuid.uuid4() #randomword(5)
                pcb_group = pcbnew.PCB_GROUP(None)
                pcb_group.SetName(groupName)
                pcb.Add(pcb_group)
                create_round_segs(pcb,start,end,cnt,rad,mask_layer,width_new,netName,segNBR,pcb_group)
            else:
                createDwgArc(pcb,start,end,md,cnt,mask_layer,width_new,netName)
        #break;
    pcbnew.Refresh()        
#
def createDwgArc(pcb,p1,p2,mp,cn,lyr=None,w=None,Nn=None,Ts=None):
    # new_arc = pcbnew.PCB_SHAPE()
    # new_arc = pcbnew.Cast_to_PCB_SHAPE(new_arc)
    # new_arc.SetShape(pcbnew.SHAPE_T_ARC)
    # new_arc.SetStart(p1)
    # new_arc.SetMid(md)
    # new_arc.SetEnd(p2)
    # new_arc.SetWidth(w) #250000)
    
    new_arc=pcbnew.PCB_SHAPE()
    new_arc.SetShape(pcbnew.SHAPE_T_ARC)
    use_geo=True
    if use_geo:
    #    new_arc.SetArcGeometry(aStart: 'wxPoint', aMid: 'wxPoint', aEnd: 'wxPoint')
        new_arc.SetArcGeometry(p1,mp,p2)
    else:
        new_arc.SetArcStart(p1)
        new_arc.SetArcEnd(p2)
        new_arc.SetCenter(cn)
    new_arc.SetWidth(w)
    if lyr is None:
        lyr = F_SilkS
    new_arc.SetLayer(lyr) #pcbnew.F_SilkS) #pcb.GetLayerID(mask_layer))
    pcb.Add(new_arc)
    return new_arc
#
def getAngleRadians(p1,p2):
    #return math.degrees(math.atan2((p1.y-p2.y),(p1.x-p2.x)))
    return (math.atan2((p1.y-p2.y),(p1.x-p2.x)))
#

def rotatePoint(r,sa,da,c):
    # sa, da in radians
    x = c.x - math.cos(sa+da) * r
    y = c.y - math.sin(sa+da) * r
    return wxPoint(x,y)
#
def create_round_segs(pcb,sp,ep,cntr,rad,layer,width,Nn,N_SEGMENTS,pcbGroup=None):
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
        #wxLogDebug("pos:"+str(ToUnits(prv_pos.x))+":"+str(ToUnits(prv_pos.y))+";"+str(ToUnits(pos.x))+":"+str(ToUnits(pos.y)),debug)
    for i, p in enumerate(points):
        #if i < len (points)-1:
        if i < len (points)-2:
            t = create_Solder(pcb,p,points[i+1],layer,width,Nn,True,pcbGroup) #adding ts code to segments
    t = create_Solder(pcb,points[-2],ep,layer,width,Nn,True,pcbGroup) #avoiding rounding on last segment
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

