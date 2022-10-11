#!/usr/bin/env python

# Taper for pcbnew using filled zones
# easyw
#
# Based 
# on Teardrops for PCBNEW by Niluje 2019 thewireddoesntexist.org
# on kicad Toolbox vy aschaller 

import os
import sys
from math import cos, acos, sin, asin, tan, atan2, sqrt
from pcbnew import ToMM, TRACK, FromMM, wxPoint, GetBoard, ZONE_CONTAINER, ZONE_SETTINGS
from pcbnew import PAD_ATTRIB_STANDARD, PAD_ATTRIB_SMD, ZONE_FILLER
import pcbnew
import wx

SMOOTHING_FILLET = ZONE_SETTINGS.SMOOTHING_FILLET

def wxLogDebug(msg,show):
    """printing messages only if show is omitted or True"""
    if show:
        wx.LogMessage(msg)


__version__ = "0.0.3"

ToUnits = ToMM
FromUnits = FromMM

MAGIC_TAPER_ZONE_ID = 0x4484

dbg = True #False

def dummy():
    pass

class Taper:
    """
    Class for creating tapers.
    """
    def __init__(self, w1, w2, tlen, net, layer):
        self.w1 = pcbnew.FromMM(w1)         # mm
        self.w2 = pcbnew.FromMM(w2)         # mm
        self.tlen = pcbnew.FromMM(tlen)     # mm
        self.net = net
        self.layer = layer

#
def Taper_Zone(board): #, pad, track):
    """Add a Taper zone to the board"""
    if hasattr (pcbnew, 'ZONE_CONTAINER'):
        z = ZONE_CONTAINER(board)
    else:
        z = ZONE(board)
    selPads = Layout.get_selected_pads()
    selTracks = Layout.get_selected_tracks()
    # taper btw pad & track
    if len(selTracks) == 1 and len(selPads) == 1:
        pad = selPads[0]
        track = selTracks[0]
        center = Layout.get_pad_coord
        pts = Layout.closest_track_pad_endpoints(pad, track)
        wxLogDebug('pad size sx='+str(ToMM(pad.GetSize().x))+',sy='+str(ToMM(pad.GetSize().y)),dbg)
        wxLogDebug('track width='+str(ToMM(track.GetWidth()))+',pts x='+str(ToMM(pts[1].x))+',y='+str(ToMM(pts[1].y)),dbg)
        wxLogDebug('y offset='+str(ToMM(abs(pad.GetPosition().y-pts[1].y))),dbg)
        # Add zone properties
        z.SetLayer(track.GetLayer())
        z.SetNetCode(track.GetNetCode())
        z.SetZoneClearance(track.GetClearance())
        z.SetMinThickness(25400)  # The minimum
        z.SetPadConnection(2)  # 2 -> solid
        z.SetIsFilled(True)
        z.SetCornerSmoothingType(SMOOTHING_FILLET)
        z.SetPriority(MAGIC_TAPER_ZONE_ID)
        
        ol = z.Outline()
        ol.NewOutline()
        
        horz = True
        if horz:
            # horizontal pad and track
            w1 = pad.GetSize().y # FromMM(2.0)
            w2 = track.GetWidth() # FromMM(1.0)
            l1 = pad.GetSize().x/2 # FromMM(1.6)
            l2 = track.GetWidth() # FromMM(0.6)
            if pts[1].x > pad.GetPosition().x:
                mirror = 1
            else:
                mirror = -1
            mr = mirror
            l  = (pts[1].x - pad.GetPosition().x)*mr
            #x = pad.GetPosition().x
            #y = pad.GetPosition().y
            x1 = pad.GetPosition().x
            y1 = pad.GetPosition().y
            x2 = pts[1].x
            y2 = pts[1].y
            points = [(x1, y1 + w1/2), (x1 + l1*mr, y1 + w1/2), (x2 + - l2/2*mr, y2 + w2/2), (x2 + l2/2*mr, y2 + w2/2), \
                                                                                            (x2 + l2/2*mr, y2 - w2/2), \
                                                            (x2 - l2/2*mr, y2 - w2/2), \
                                    (x1 + l1*mr, y1 - w1/2), \
                    (x1, y1 - w1/2)]

        else: #vertical
            w1 = pad.GetSize().x # FromMM(2.0)
            w2 = track.GetWidth() # FromMM(1.0)
            l1 = pad.GetSize().y/2 # FromMM(1.6)
            l2 = track.GetWidth() # FromMM(0.6)
            if pts[1].y > pad.GetPosition().y:
                mirror = 1
            else:
                mirror = -1
            mr = mirror
            l  = (pts[1].y - pad.GetPosition().y)*mr
            x1 = pad.GetPosition().x
            y1 = pad.GetPosition().y
            x2 = pts[1].x
            y2 = pts[1].y
            points = [(x1 -w1/2, y1), (x1 -w1/2, y1 + l1*mr), (x2 - w2/2, y2 + l2/2*mr), (x2 -w2/2, y2 + l2/2*mr), \
                                                                                         (x2 +w2/2, y2 + l2/2*mr), \
                                                              (x2 + w2/2, y2 + l2/2*mr), \
                                      (x1 +w1/2, y1 + l1*mr), \
                      (x1 +w1/2, y1)]


       #                                                  w2 
       #                                             3 +------+ 4
       #                                               |  M   | x2,y2 l2
       #                                             2 +  |   + 5
       #           l1    1                     #     /    |     \
       #  0 +------------+                     #  1 +-----|------+ 6
       #    |            |\                    #    |     |      |
       # x1,|            | \ 2 l2              #    |     |      |
       # y1 |     l      |  +---+ 3            #    |     |      |
       #  w1|<-----------|--|-M | w2           #  l1|    l       |
       #    |            |  +---+ 4            #    |     |      |
       #    |            | / 5 x2,y2           #    |     |      |
       #    |            |/                    #    |     |      |
       #  7 +------------+                     #  0 +-----+------+ 7
       #                 6                              x1,y1 w1
                   # 0,           1,                  2,                      3
                   #                                                          4,
                   #                                  5,
                   #              6,
                   # 7
        ## points = [(x1, y1 + w1/2), (x1 + l1*mr, y1 + w1/2), (x2 + - l2/2*mr, y2 + w2/2), (x2 + l2/2*mr, y2 + w2/2), \
        ##                                                                                 (x2 + l2/2*mr, y2 - w2/2), \
        ##                                                 (x2 - l2/2*mr, y2 - w2/2), \
        ##                          (x1 + l1*mr, y1 - w1/2), \
        ##           (x1, y1 - w1/2)]
#        points = [(x, y + w1/2), (x + l1*mr, y + w1/2), (x + (l - l2/2)*mr, y + w2/2), (x + (l + l2/2)*mr, y + w2/2), \
#                                                                                       (x + (l + l2/2)*mr, y - w2/2), \
#                                                        (x + (l - l2/2)*mr, y - w2/2), \
#                                 (x + l1*mr, y - w1/2), \
#                  (x, y - w1/2)]
#        points = [(x - l1/2, y + w1/2), (x + l1/2, y + w1/2), (x + l - l2/2, y + w2/2), \
#                  (x + l + l2/2, y + w2/2), (x + l + l2/2, y - w2/2), (x + l - l2/2, y - w2/2), \
#                  (x + l1/2, y - w1/2), (x - l1/2, y - w1/2)]
#
     #  points = [(self.w2/2, -self.w2/2), (self.w2/2, self.w2/2), (-self.w2/2, self.w2/2), \
     #          (-self.w2/2 - self.tlen, self.w1/2), (-(self.w1/2 + self.tlen + self.w2/2), self.w1/2), \
     #          (-(self.w1/2 + self.tlen + self.w2/2), -self.w1/2), (-self.w2/2 - self.tlen, -self.w1/2), \
     #          (-self.w2/2, -self.w2/2)]

        points = [pcbnew.wxPoint(*point) for point in points]
        wxLogDebug('points='+str(points),dbg)
        
        for p in points:
            ol.Append(p.x, p.y)
        
        
        #sys.stdout.write("+")
        board.Add(z)
        # RebuildAllZones(board)       
        filler = ZONE_FILLER(board)
        filler.Fill(board.Zones())
        pcbnew.Refresh()
        wxLogDebug('done',True)
    # taper btw two tracks
    elif len(selTracks) == 2 and len(selPads) == 0:
        track1 = selTracks[0]
        track2 = selTracks[1]
        tracks = selTracks
        pts = Layout.closest_track_endpoints(tracks)
        wxLogDebug('track1 width='+str(ToMM(track1.GetWidth()))+',pts x='+str(ToMM(pts[1].x))+',y='+str(ToMM(pts[1].y)),dbg)
        wxLogDebug('track2 width='+str(ToMM(track2.GetWidth()))+',pts x='+str(ToMM(pts[1].x))+',y='+str(ToMM(pts[1].y)),dbg)
        # Add zone properties
        z.SetLayer(track1.GetLayer())
        z.SetNetCode(track1.GetNetCode())
        z.SetZoneClearance(track1.GetClearance())
        z.SetMinThickness(25400)  # The minimum
        z.SetPadConnection(2)  # 2 -> solid
        z.SetIsFilled(True)
        z.SetCornerSmoothingType(SMOOTHING_FILLET)
        z.SetPriority(MAGIC_TAPER_ZONE_ID)
    
        ol = z.Outline()
        ol.NewOutline()
        
        # horizontal tracks
        w1 = track1.GetWidth() # FromMM(2.0)
        w2 = track2.GetWidth() # FromMM(1.0)
        delta = 0
        if pts[0] == pts[1]:
            wxLogDebug('tracks connected',dbg)
            delta = (w1 + w2)/1.5
        if pts[1].x > pts[0].x:
            mirror = 1
        else:
            mirror = -1
        mr = mirror
        l  = (pts[1].x - pts[0].x)*mr
        x1 = pts[0].x - delta*mr
        y1 = pts[0].y
        x2 = pts[1].x + delta*mr
        y2 = pts[1].y
        l1 = w1 # FromMM(1.6)
        l2 = w2 # FromMM(0.6)
        
       #           l1    1
       #  0 +------------+
       #    |            |\
       #    |            | \ 2 l2
       #    |            |  +---+ 3
       #  w1|     M1-----|--|-M2| w2
       #    |    x1,     |  +---+ 4
       #    |    y1      | / 5 x2,y2
       #    |            |/
       #  7 +------------+
       #                 6
                   # 0,           1,                  2,                      3
                   #                                                          4,
                   #                                  5,
                   #              6,
                   # 7
        points = [(x1- w1/2, y1 + w1/2), (x1 + l1/2*mr, y1 + w1/2), (x2 - l2/2*mr, y2 + w2/2), (x2 + l2/2*mr, y2 + w2/2), \
                                                                                               (x2 + l2/2*mr, y2 - w2/2), \
                                                            (x2 - l2/2*mr, y2 - w2/2), \
                                 (x1 + l1/2*mr, y1 - w1/2), \
                  (x1 - w1/2, y1 - w1/2)]


        points = [pcbnew.wxPoint(*point) for point in points]
        wxLogDebug('points='+str(points),dbg)
        
        for p in points:
            ol.Append(p.x, p.y)
        
        
        #sys.stdout.write("+")
        board.Add(z)
        # RebuildAllZones(board)       
        filler = ZONE_FILLER(board)
        filler.Fill(board.Zones())
        pcbnew.Refresh()
        wxLogDebug('done',True)
    
    
    # taper at the end of a track
    elif len(selTracks) == 1 and len(selPads) == 0:
        track = selTracks[0]
        pnt = track.GetStart()   
        #tracks = Layout.get_tracks_by_pos(pnt)
        # we would need to check the not connected track point
        if 0:
            x = track.GetStart().x
            y = track.GetStart().y
        else:
            x = track.GetEnd().x
            y = track.GetEnd().y
        w = track.GetWidth()
        
        #tks = list(board.GetTracksByPosition(track.GetStart()))
        #tks = board.GetTracksByPosition(track.GetStart())
        #wxLogDebug('len trks Start '+len(tks),True)
        #tks = board.GetTracksByPosition(track.GetEnd())
        #wxLogDebug('len trks End '+len(tks),True)
       #                  
       #  0 +------------+ 1
       #    |            |
       #    |            |
       #    |  w         |
       #    |<----+----->|
       #    |    x,y     |
       #    |            |
       #    |            |
       #  3 +------------+ 2
       #                  
                   # 0,                1,
                   # 2                 3
        points = [(x - w/2, y + w/2), (x + w/2, y + w/2), \
                  (x + w/2, y - w/2), (x - w/2, y - w/2)]
        
        points = [pcbnew.wxPoint(*point) for point in points]
        wxLogDebug('points='+str(points),dbg)
        # Add zone properties
        z.SetLayer(track.GetLayer())
        z.SetNetCode(track.GetNetCode())
        z.SetZoneClearance(track.GetClearance())
        z.SetMinThickness(25400)  # The minimum
        z.SetPadConnection(2)  # 2 -> solid
        z.SetIsFilled(True)
        z.SetCornerSmoothingType(SMOOTHING_FILLET)
        z.SetPriority(MAGIC_TAPER_ZONE_ID)
    
        ol = z.Outline()
        ol.NewOutline()

        for p in points:
            ol.Append(p.x, p.y)
        #sys.stdout.write("+")
        board.Add(z)
        # RebuildAllZones(board)       
        filler = ZONE_FILLER(board)
        filler.Fill(board.Zones())
        pcbnew.Refresh()
        wxLogDebug('done',True)
        #return z
#
class Layout:
    """
    Class for common Pcbnew layout operations.
    """
    @staticmethod
    def get_selected_pads(board=None):
        if board is None:
            board = pcbnew.GetBoard()
        
        return list(filter(lambda p: p.IsSelected(), board.GetPads()))
    
    @staticmethod
    def get_pad_coord(pads):
        '''Obtain wxPoint(x,y) coordinates of pads.'''
        return list(filter(lambda p: p.GetPosition(), pads))
    
    @staticmethod
    def get_track_width():
        '''Returns current track width dimension that the user has set.'''
        return pcbnew.GetBoard().GetDesignSettings().GetCurrentTrackWidth()
            
    @staticmethod
    def get_selected_pad_centers():
        '''Returns the center coordinates of any module with a selected pad.'''
        board = pcbnew.GetBoard()
        modules = pcbnew.board.GetModules()
        spads = [p for p in board.GetPads() if p.IsSelected()]
        pcoords = [p.GetPosition() for p in spads]
        return [modules.GetPad(p).GetCenter() for p in pcoords]
    
    @staticmethod
    def draw_track_segment(board, start, end, net, layer=0):
        '''Returns a new pcbnew board with an added track.'''
        tseg = pcbnew.TRACK(board)
        tseg.SetStart(start)
        tseg.SetEnd(end)
        tseg.SetWidth(Layout.get_track_width())
        tseg.SetLayer(layer)
        board.Add(tseg)
        return board
    
    @staticmethod
    def get_selected_tracks(board=None):
        if board is None:
            board = pcbnew.GetBoard()
        
        return list(filter(lambda t: t.IsSelected(), board.GetTracks()))
    
    @staticmethod
    def dist(points):
        '''Distance between two points'''
        p0, p1 = points
        return sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
    
    @staticmethod
    def closest_track_endpoints(tracks):
        p0, p1 = tracks[0].GetStart(), tracks[0].GetEnd()
        p2, p3 = tracks[1].GetStart(), tracks[1].GetEnd()
        distances = [Layout.dist([p0, p2]), Layout.dist([p0, p3]), \
                        Layout.dist([p1, p2]), Layout.dist([p1, p3])]
        if distances[0] == min(distances):
            return (p0, p2)
        elif distances[1] == min(distances):
            return (p0, p3)
        elif distances[2] == min(distances):
            return (p1, p2)
        elif distances[3] == min(distances):
            return (p1, p3)
    
    @staticmethod
    def closest_track_pad_endpoints(pad, track):
        p0, p1 = track.GetStart(), track.GetEnd()
        distances = [Layout.dist([p0, pad.GetPosition()]), \
                     Layout.dist([p1, pad.GetPosition()])]
        if distances[0] == min(distances):
            return (pad.GetPosition(), p0)
        elif distances[1] == min(distances):
            return (pad.GetPosition(), p1)
#
#    @staticmethod
#    def smdRectPad(module, size, pos, name, angle, net):
#        '''Build a rectangular pad.'''
#        pad = pcbnew.D_PAD(module)
#        pad.SetSize(size)
#        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
#        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
#        # Set only the copper layer without mask
#        # since nothing is mounted on these pads
#        pad.SetLayerSet(pcbnew.LSET(pcbnew.F_Cu))       # Get active layer
#        pad.SetPos0(pos)
#        pad.SetPosition(pos)
#        pad.SetPadName(name)
#        
#        pad.Rotate(pos, angle)
#        # Set clearance to small value, because
#        # pads can be very close together.
#        # If distance is smaller than clearance
#        # DRC doesn't allow routing the pads
#        pad.SetLocalClearance(1)
#        pad.SetNet(net)
#
#        return pad
#
#    @staticmethod
#    def Polygon(module, points, layer):
#        '''Draw a polygon through specified points.'''
#        polygon = pcbnew.EDGE_MODULE(module)
#        polygon.SetWidth(0)         # Disables outline
#        polygon.SetLayer(layer)
#        polygon.SetShape(pcbnew.S_POLYGON)
#        polygon.SetPolyPoints(points)
#        module.Add(polygon)
#
#        return module
#
#
#def __GetAllTapers(board):
#    """Just retrieves all teardrops of the current board classified by net"""
#    tapers_zones = {}
#    for zone in [board.GetArea(i) for i in range(board.GetAreaCount())]:
#        if zone.GetPriority() == MAGIC_TAPER_ZONE_ID:
#            netname = zone.GetNetname()
#            if netname not in tapers_zones.keys():
#                tapers_zones[netname] = []
#            tapers_zones[netname].append(zone)
#    return tapers_zones
#
#def __ComputePoints(track, via, hpercent, vpercent, segs):
#    """Compute all teardrop points"""
#    start = track.GetStart()
#    end = track.GetEnd()
#
#    if (segs > 2) and (vpercent > 70.0):
#        # If curved via are selected, max angle is 45 degres --> 70%
#        vpercent = 70.0
#
#    # ensure that start is at the via/pad end
#    d = end - via[0]
#    if sqrt(d.x * d.x + d.y * d.y) < via[1]/2.0:
#        start, end = end, start
#
#    # get normalized track vector
#    # it will be used a base vector pointing in the track direction
#    pt = end - start
#    norm = sqrt(pt.x * pt.x + pt.y * pt.y)
#    vec = [t / norm for t in pt]
#
#    # find point on the track, sharp end of the teardrop
#    w = track.GetWidth()/2
#    radius = via[1]/2
#    n = __TeardropLength(track, via, hpercent)
#    dist = sqrt(n*n + w*w)
#    d = atan2(w, n)
#    vecB = [vec[0]*cos(d)+vec[1]*sin(d), -vec[0]*sin(d)+vec[1]*cos(d)]
#    pointB = start + wxPoint(int(vecB[0] * dist), int(vecB[1] * dist))
#    vecA = [vec[0]*cos(-d)+vec[1]*sin(-d), -vec[0]*sin(-d)+vec[1]*cos(-d)]
#    pointA = start + wxPoint(int(vecA[0] * dist), int(vecA[1] * dist))
#
#    # via side points
#    radius = via[1] / 2
#    d = asin(vpercent/100.0)
#    vecC = [vec[0]*cos(d)+vec[1]*sin(d), -vec[0]*sin(d)+vec[1]*cos(d)]
#    d = asin(-vpercent/100.0)
#    vecE = [vec[0]*cos(d)+vec[1]*sin(d), -vec[0]*sin(d)+vec[1]*cos(d)]
#    pointC = via[0] + wxPoint(int(vecC[0] * radius), int(vecC[1] * radius))
#    pointE = via[0] + wxPoint(int(vecE[0] * radius), int(vecE[1] * radius))
#
#    # Introduce a last point in order to cover the via centre.
#    # If not, the zone won't be filled
#    vecD = [-vec[0], -vec[1]]
#    radius = (via[1]/2)*0.5  # 50% of via radius is enough to include
#    pointD = via[0] + wxPoint(int(vecD[0] * radius), int(vecD[1] * radius))
#
#    pts = [pointA, pointB, pointC, pointD, pointE]
#    if segs > 2:
#        pts = __ComputeCurved(vpercent, w, vec, via, pts, segs)
#
#    return pts
#
#
def RebuildAllZones(pcb):
    """Rebuilt all zones"""
    filler = ZONE_FILLER(pcb)
    filler.Fill(pcb.Zones())

#
#
#def SetTaper(hpercent=30, vpercent=70, segs=10, pcb=None, use_smd=False):
#    """Set teardrops on a teardrop free board"""
#
#    if pcb is None:
#        pcb = GetBoard()
#
#    pad_types = [PAD_ATTRIB_STANDARD] + [PAD_ATTRIB_SMD]*use_smd
#    vias = __GetAllVias(pcb)[0] + __GetAllPads(pcb, pad_types)[0]
#    vias_selected = __GetAllVias(pcb)[1] + __GetAllPads(pcb, pad_types)[1]
#    if len(vias_selected) > 0:
#        vias = vias_selected
#
#    teardrops = __GetAllTeardrops(pcb)
#    count = 0
#    for track in [t for t in pcb.GetTracks() if type(t)==TRACK]:
#        for via in [v for v in vias if track.IsPointOnEnds(v[0], int(v[1]/2))]:
#            if (track.GetLength() < __TeardropLength(track, via, hpercent)) or\
#               (track.GetWidth() >= via[1] * vpercent / 100):
#                continue
#
#            found = False
#            if track.GetNetname() in teardrops.keys():
#                for teardrop in teardrops[track.GetNetname()]:
#                    if __DoesTeardropBelongTo(teardrop, track, via):
#                        found = True
#                        break
#
#            # Discard case where pad and track are not on the same layer
#            if (via[3] == "front") and (not track.IsOnLayer(0)):
#                continue
#            if (via[3] == "back") and track.IsOnLayer(0):
#                continue
#
#            if not found:
#                coor = __ComputePoints(track, via, hpercent, vpercent, segs)
#                pcb.Add(__Zone(pcb, coor, track))
#                count += 1
#
#    RebuildAllZones(pcb)
#    print('{0} teardrops inserted'.format(count))
#    return count
#
#
#def RmTapers(pcb=None):
#    """Remove all tapers"""
#
#    if pcb is None:
#        pcb = GetBoard()
#
#    count = 0
#    tapers = __GetAllTeardrops(pcb)
#    for netname in teardrops:
#        for tpaer in tapers[netname]:
#            pcb.Remove(taper)
#            count += 1
#
#    RebuildAllZones(pcb)
#    print('{0} tapers removed'.format(count))
#    return count
