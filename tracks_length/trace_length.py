#!/usr/bin/env python

# some source tips @
# https://github.com/bpkempke/kicad-scripts
# https://github.com/MitjaNemec/Kicad_action_plugins
# https://github.com/jsreynaud/kicad-action-scripts


# import trace_length; reload(trace_length)

import sys
import os
from pcbnew import *
import wx
import pcbnew
import math
#import threading 

debug = False
def wxLogDebug(msg,dbg):
    """printing messages only if show is omitted or True"""
    if dbg == True:
        wx.LogMessage(msg)
#
 
def getSelTracksLength(pcb):
    ln = 0.
    for item in pcb.GetTracks():
        if type(item) is pcbnew.TRACK and item.IsSelected():
            ln+=(item.GetLength())
    return(ln)
    #print(pcbnew.ToMM(ln))
#
def getSelTracks(pcb):
    tracks=[]
    for item in pcb.GetTracks():
        if type(item) is pcbnew.TRACK and item.IsSelected():
            tracks.append(item)
    return tracks
#
def find_Tracks_between_Pads(pcb,pad1,pad2):
    track_list = []
    # get list of all selected pads
    #selected_pads = [pad1, pad2]
    # get the net the pins are on
    net = pad1.GetNetname()
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

def getTracksListLength(pcb,tracks):
    ln = 0.
    for item in tracks:
        ln+=(item.GetLength())
    return(ln)
#
def selectListTracks(pcb,tracks):
    for item in tracks:
        if type(item) is TRACK:
            item.SetSelected()
#
def getTrackAngleRadians(track):
    #return math.degrees(math.atan2((p1.y-p2.y),(p1.x-p2.x)))
    return (math.atan2((track.GetEnd().y - track.GetStart().y), (track.GetEnd().x - track.GetStart().x)))
#

# Python plugin stuff
class SelectedTracesLenght(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Measure Length for Selected Tracks\nversion 1.2"
        self.category = "Modify PCB"
        self.description = "Measure Length for Selected Tracks"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./trace_length.png")
        self.show_toolbar_button = True
        
    def Run(self):
        #self.pcb = GetBoard()
        pcb = pcbnew.GetBoard() 
        ln=0.
        pads=[]
        tracks=getSelTracks(pcb)
        if len(tracks) >0: #selected tracks >0
            for item in tracks:
                ln+=(item.GetLength())
        else:
            for item in pcb.GetPads():
                if item.IsSelected():
                    pads.append(item)
            if len(pads) == 1:
                tracks=[]
                tracks = find_Tracks_inNet_Pad(pcb,pads[0])
                c_tracks = get_contiguous_tracks(pcb,tracks,pads[0])
                tracks=c_tracks
                # selectListTracks(pcb,tracks) # this seems not to allow deselecting
                ln = getTracksListLength(pcb,tracks)
                selectListTracks(pcb,tracks)
                pcbnew.Refresh()
            
            #else:
            #    wx.LogMessage("Solder Mask Expander:\nSelect Tracks\nor One Pad to select connected Tracks")
        if ln > 0:        
            #wx.LogMessage('Selected Traces Length: {0:.3f} mm'.format(ToMM(ln)))
            wxLogDebug('showing Selected Tracks',debug)
            #wx.LogMessage('debug'+str(debug))
            msg = u"Selected Tracks Length:\n{0:.3f} mm \u2714".format(ToMM(ln))
            if len(tracks) == 1:
                angle = (math.degrees(getTrackAngleRadians(tracks[0])))
                msg+=u"\nTrack Angle: {0:.1f} deg \u2714".format(angle)
            #selectListTracks(pcb,tracks)
            #pcbnew.Refresh()
            wdlg = wx.MessageDialog(None, msg,'Info message',wx.OK | wx.ICON_INFORMATION)
            result = wdlg.ShowModal()
            if result == wx.ID_OK:
                pass
            clearListTracks(pcb,tracks,True)
            #timer = threading.Timer(1000, clearListTracks(pcb,tracks,True)) 
            #timer.start() 
            #blocking dialogw
            #wx.MessageBox("showing selection", 'Info', wx.OK | wx.ICON_INFORMATION)
            #clearListTracks(pcb,tracks)
        elif len(pads) != 1:
            wx.LogMessage('Select Tracks to calculate the Length\nor One Pad to select connected Tracks')
#
 

def selectListTracks(pcb,tracks):
    for item in tracks:
        if type(item) is TRACK:
            item.SetSelected()
            
def clearListTracks(pcb,tracks,refresh=None):
    wxLogDebug('deSelecting Tracks',debug)
    for trk in tracks:
        if trk.IsSelected():
            trk.ClearSelected()           
    if refresh:
        pcbnew.Refresh()
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
    epsilon = FromMM(0.003) # tolerance 3 nm
    delta = math.hypot(p1[0]-p2[0],p1[1]-p2[1])
    wxLogDebug('delta: '+str(delta)+'eps: '+str(epsilon),debug)
    #wxLogDebug('epsilon: '+str(epsilon),debug)
    if delta <= epsilon:
        wxLogDebug('connected',debug)
        return True
    else:
        return False
#
def not_eq(a,b):
    if abs(a-b) >= 1: #1nm
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

#Solder_Expander().register()

