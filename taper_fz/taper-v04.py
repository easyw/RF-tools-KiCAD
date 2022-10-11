#!/usr/bin/env python

# Taper for pcbnew using filled zones
# easyw
#
# Based 
# on Teardrops for PCBNEW by Niluje 2019 thewireddoesntexist.org
# on kicad Toolbox vy aschaller 

import os
import sys
from math import cos, acos, sin, asin, tan, atan2, sqrt, pi, degrees, radians
from pcbnew import ToMM, TRACK, FromMM, wxPoint, GetBoard, ZONE_CONTAINER, ZONE_SETTINGS
from pcbnew import PAD_ATTRIB_STANDARD, PAD_ATTRIB_SMD, ZONE_FILLER, VECTOR2I
from pcbnew import STARTPOINT, ENDPOINT
import pcbnew
import wx

SMOOTHING_FILLET = ZONE_SETTINGS.SMOOTHING_FILLET


def wxLogDebug(msg,show):
    """printing messages only if show is omitted or True"""
    if show:
        wx.LogMessage(msg)
#

__version__ = "0.0.4"

ToUnits = ToMM
FromUnits = FromMM

MAGIC_TAPER_ZONE_ID = 0x4484

dbg = True #False

def dummy():
    pass
##
def __Zone(board, points, track):
    """Add a zone to the board"""
    z = ZONE_CONTAINER(board)

    # Add zone properties
    z.SetLayer(track.GetLayer())
    z.SetNetCode(track.GetNetCode())
    z.SetZoneClearance(track.GetClearance())
    z.SetMinThickness(25400)  # The minimum
    z.SetPadConnection(2)  # 2 -> solid
    z.SetIsFilled(True)
    z.SetPriority(MAGIC_TAPER_ZONE_ID)  # MAGIC_TEARDROP_ZONE_ID)
    ol = z.Outline()
    ol.NewOutline()

    for p in points:
        ol.Append(p.x, p.y)

    # sys.stdout.write("+")
    return z
##
def __Bezier(p1, p2, p3, p4, n=20.0):
    n = float(n)
    pts = []
    for i in range(int(n)+1):
        t = i/n
        a = (1.0 - t)**3
        b = 3.0 * t * (1.0-t)**2
        c = 3.0 * t**2 * (1.0-t)
        d = t**3

        x = int(a * p1[0] + b * p2[0] + c * p3[0] + d * p4[0])
        y = int(a * p1[1] + b * p2[1] + c * p3[1] + d * p4[1])
        pts.append(wxPoint(x, y))
    return pts
##
def __PointDistance(a,b):
    """Distance between two points"""
    return sqrt((a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1]))
##
def __ComputeCurved(vpercent, w, vec, pad, pts, segs):
    """Compute the curves part points"""

    # A and B are points on the track
    # C and E are points on the via
    # D is midpoint behind the via centre

    # radius = via[1]/2
    radius = pad.GetSize().x/2
    
    minVpercent = float(w*2) / float(pad.GetSize().x) # via[1])
    weaken = (vpercent/100.0  -minVpercent) / (1-minVpercent) / radius

    biasBC = 0.5 * __PointDistance( pts[1], pts[2] )
    biasAE = 0.5 * __PointDistance( pts[4], pts[0] )

    vecC = pts[2] - pad.GetPosition() # via[0]
    tangentC = [ pts[2][0] - vecC[1]*biasBC*weaken,
                 pts[2][1] + vecC[0]*biasBC*weaken ]
    vecE = pts[4] - pad.GetPosition() # via[0]
    tangentE = [ pts[4][0] + vecE[1]*biasAE*weaken,
                 pts[4][1] - vecE[0]*biasAE*weaken ]

    tangentB = [pts[1][0] - vec[0]*biasBC, pts[1][1] - vec[1]*biasBC]
    tangentA = [pts[0][0] - vec[0]*biasAE, pts[0][1] - vec[1]*biasAE]

    curve1 = __Bezier(pts[1], tangentB, tangentC, pts[2], n=segs)
    curve2 = __Bezier(pts[4], tangentE, tangentA, pts[0], n=segs)

    return curve1 + [pts[3]] + curve2
##
def __ComputeCurvedTracks(vpercent, w1, vec, track, pts, segs):
    """Compute the curves part points"""

    # A and B are points on the track
    # C and E are points on the via
    # D is midpoint behind the via centre

    w2= track.GetWidth()
    # radius = via[1]/2
    radius = w2/2
    
    minVpercent = float(w1*2) / float(w2) # via[1])
    weaken = (vpercent/100.0  -minVpercent) / (1-minVpercent) / radius

    biasBC = 0.5 * __PointDistance( pts[1], pts[2] )
    biasAE = 0.5 * __PointDistance( pts[4], pts[0] )

    vecC = pts[2] - track.GetEnd() # via[0]
    tangentC = [ pts[2][0] - vecC[1]*biasBC*weaken,
                 pts[2][1] + vecC[0]*biasBC*weaken ]
    vecE = pts[4] - track.GetEnd() # via[0]
    tangentE = [ pts[4][0] + vecE[1]*biasAE*weaken,
                 pts[4][1] - vecE[0]*biasAE*weaken ]

    tangentB = [pts[1][0] - vec[0]*biasBC, pts[1][1] - vec[1]*biasBC]
    tangentA = [pts[0][0] - vec[0]*biasAE, pts[0][1] - vec[1]*biasAE]

    curve1 = __Bezier(pts[1], tangentB, tangentC, pts[2], n=segs)
    curve2 = __Bezier(pts[4], tangentE, tangentA, pts[0], n=segs)

    return curve1 + [pts[3]] + curve2
##
def __NormalizeVector(pt):
    """Make vector unit length"""
    norm = sqrt(pt.x * pt.x + pt.y * pt.y)
    return [t / norm for t in pt]
## 
def __ComputePoints(track, pad, segs):
    """Compute all taper points"""
    hpercent=1; vpercent=100; noBulge=True
    start = track.GetStart()
    end = track.GetEnd()
    module = pad.GetParent()

    # ensure that start is at the via/pad end
    if (__PointDistance(end, pad.GetPosition()) < __PointDistance(start, pad.GetPosition())): # via[0]) < radius:
        start, end = end, start
    # if __PointDistance(end, pad.GetPosition()) < radius: # via[0]) < radius:
    #     start, end = end, start

    # get normalized track vector
    # it will be used a base vector pointing in the track direction
    vecT = __NormalizeVector(end - start)
    trackAngle = atan2(vecT[1],vecT[0])
    if trackAngle > pi:
        trackAngle -=2*pi
    if trackAngle < -pi:
        trackAngle +=2*pi
    trackAngle=degrees(trackAngle)    
    wxLogDebug('trackAngle='+str(trackAngle),dbg)
    #wxLogDebug('vecT='+str(vecT),dbg)
    
    sx = pad.GetSize().x
    sy = pad.GetSize().y
    
    # use an angle range
    if abs(module.GetOrientationDegrees()) == 90 or abs(module.GetOrientationDegrees()) == 270:
        nsx = sx
        nsy  = sy
    else:
        nsx = sy
        nsy  = sx
    if (abs(trackAngle) >= 60 and abs(trackAngle) <= 120) or (abs(trackAngle) >= 240 and abs(trackAngle) <= 300):
        nsx = nsy
        nsy  = nsx
    else:
        nsx = nsx
        nsy  = nsy
        
    radius = nsx/2 # via[1]/2.0
    targetLength = nsy*(hpercent/100.0) # via[1]*(hpercent/100.0)
    wxLogDebug('targetLength='+str(ToMM(targetLength)),dbg)
    
    w = track.GetWidth()/2

    if vpercent > 100:
        vpercent = 100

    # Find point of intersection between track and edge of via
    # This normalizes teardrop lengths
    bdelta = FromMM(0.01)
    backoff=0
    while backoff<radius:
        np = start + wxPoint( vecT[0]*backoff, vecT[1]*backoff )
        if __PointDistance(np, pad.GetPosition()) >= radius: # via[0]) >= radius:
            break
        backoff += bdelta
    start=np

    # vec now points from via to intersect point
    vec = __NormalizeVector(start - pad.GetPosition()) # via[0])

    # choose a teardrop length
    # targetLength = pad.GetSize().x*(hpercent/100.0) # via[1]*(hpercent/100.0)
    n = min(targetLength, track.GetLength() - backoff)
    consumed = 0

    # if shortened, shrink width too
    if n+consumed < targetLength:
        minVpercent = 100* float(w) / float(radius)
        vpercent = vpercent*n/targetLength + minVpercent*(1-n/targetLength)

    # find point on the track, sharp end of the teardrop
    pointB = start + wxPoint( vecT[0]*n +vecT[1]*w , vecT[1]*n -vecT[0]*w )
    pointA = start + wxPoint( vecT[0]*n -vecT[1]*w , vecT[1]*n +vecT[0]*w )

    # In some cases of very short, eccentric tracks the points can end up
    # inside the teardrop. If this happens just cancel adding it
    if ( __PointDistance(pointA, pad.GetPosition()) < radius or
         __PointDistance(pointB, pad.GetPosition()) < radius ):
        return False
    # if ( __PointDistance(pointA, via[0]) < radius or
    #      __PointDistance(pointB, via[0]) < radius ):
    #     return False

    # via side points

    # angular positions of where the teardrop meets the via
    dC = asin(vpercent/100.0)
    dE = -dC

    if noBulge:
        # find (signed) angle between track and teardrop
        offAngle = atan2(vecT[1],vecT[0]) - atan2(vec[1],vec[0])
        if offAngle > pi:
            offAngle -=2*pi
        if offAngle < -pi:
            offAngle +=2*pi

        if offAngle+dC > pi/2:
            dC = pi/2 - offAngle

        if offAngle+dE < -pi/2:
            dE = -pi/2 - offAngle
        #wxLogDebug('offAngle='+str(degrees(offAngle)),dbg)
        
    vecC = [vec[0]*cos(dC)+vec[1]*sin(dC), -vec[0]*sin(dC)+vec[1]*cos(dC)]
    vecE = [vec[0]*cos(dE)+vec[1]*sin(dE), -vec[0]*sin(dE)+vec[1]*cos(dE)]

    pointC = pad.GetPosition() + wxPoint(int(vecC[0] * radius), int(vecC[1] * radius))
    pointE = pad.GetPosition() + wxPoint(int(vecE[0] * radius), int(vecE[1] * radius))
    # pointC = via[0] + wxPoint(int(vecC[0] * radius), int(vecC[1] * radius))
    # pointE = via[0] + wxPoint(int(vecE[0] * radius), int(vecE[1] * radius))

    # Introduce a last point in order to cover the via centre.
    # If not, the zone won't be filled
    pointD = pad.GetPosition() + wxPoint(int(vec[0]*-0.15*radius), int(vec[1]*-0.15*radius))
    # pointD = via[0] + wxPoint(int(vec[0]*-0.5*radius), int(vec[1]*-0.5*radius))

    pts = [pointA, pointB, pointC, pointD, pointE]
    if segs > 2:
        pts = __ComputeCurved(vpercent, w, vecT, pad, pts, segs)

    return pts
##

def __ComputePointsTracks(track1, track2, segs):
    """Compute all taper points for tracks"""
    hpercent=1; vpercent=100; noBulge=True
    start1 = track1.GetStart()
    end1 = track1.GetEnd()
    start2 = track2.GetStart()
    end2 = track2.GetEnd()
    w1 = track1.GetWidth()/2
    w2 = track2.GetWidth()/2
    
    # ensure that start is at the tracks common
    if (start1 == start2) or (start1 == end2):
        common = start1
    else:
        common = end1
    
    # get normalized track vectors
    # it will be used a base vector pointing in the track direction
    vecT1 = __NormalizeVector(end1 - start1)
    trackAngle1 = atan2(vecT1[1],vecT1[0])
    if trackAngle1 > pi:
        trackAngle1 -=2*pi
    if trackAngle1 < -pi:
        trackAngle1 +=2*pi
    trackAngle1=degrees(trackAngle1)    
    vecT2 = __NormalizeVector(end2 - start2)
    trackAngle2 = atan2(vecT2[1],vecT2[0])
    if trackAngle2 > pi:
        trackAngle2 -=2*pi
    if trackAngle2 < -pi:
        trackAngle2 +=2*pi
    trackAngle2=degrees(trackAngle2)
    wxLogDebug('trackAngle1='+str(trackAngle1),dbg)
    wxLogDebug('trackAngle2='+str(trackAngle2),dbg)
    #wxLogDebug('vecT='+str(vecT),dbg)
    
    radius = w1 # via[1]/2.0
    targetLength = w2*(hpercent/100.0) # via[1]*(hpercent/100.0)
    wxLogDebug('targetLength='+str(ToMM(targetLength)),dbg)
    
    if vpercent > 100:
        vpercent = 100
    
    backoff=0
    # choose a teardrop length
    # targetLength = pad.GetSize().x*(hpercent/100.0) # via[1]*(hpercent/100.0)
    n = min(targetLength, track2.GetLength() - backoff)
    consumed = 0

    # if shortened, shrink width too
    if n+consumed < targetLength:
        minVpercent = 100* float(w1) / float(w2)
        vpercent = vpercent*n/targetLength + minVpercent*(1-n/targetLength)

    # find point on the track, sharp end of the teardrop
    pointB = start1 + wxPoint( vecT1[0]*n +vecT1[1]*w1 , vecT1[1]*n -vecT1[0]*w1 )
    pointA = start1 + wxPoint( vecT1[0]*n -vecT1[1]*w1 , vecT1[1]*n +vecT1[0]*w1 )

    # In some cases of very short, eccentric tracks the points can end up
    # inside the teardrop. If this happens just cancel adding it
    if (__PointDistance(pointA, common) < max(w1,w2)  or
        __PointDistance(pointB, common) < max(w1,w2) ):
        wxLogDebug('aborting'+str(targetLength),dbg)
        return False
    # if ( __PointDistance(pointA, via[0]) < radius or
    #      __PointDistance(pointB, via[0]) < radius ):
    #     return False

    # via side points

    # angular positions of where the teardrop meets the via
    dC = asin(vpercent/100.0)
    dE = -dC

    if noBulge:
        # find (signed) angle between track and teardrop
        offAngle = atan2(vecT1[1],vecT1[0]) - atan2(vecT2[1],vecT2[0])
        if offAngle > pi:
            offAngle -=2*pi
        if offAngle < -pi:
            offAngle +=2*pi

        if offAngle+dC > pi/2:
            dC = pi/2 - offAngle

        if offAngle+dE < -pi/2:
            dE = -pi/2 - offAngle
        #wxLogDebug('offAngle='+str(degrees(offAngle)),dbg)
        
    vecC = [vecT2[0]*cos(dC)+vecT2[1]*sin(dC), -vecT2[0]*sin(dC)+vecT2[1]*cos(dC)]
    vecE = [vecT2[0]*cos(dE)+vecT2[1]*sin(dE), -vecT2[0]*sin(dE)+vecT2[1]*cos(dE)]

    pointC = end2 + wxPoint(int(vecC[0] * w2), int(vecC[1] * w2))
    pointE = end2 + wxPoint(int(vecE[0] * w2), int(vecE[1] * w2))
    # pointC = via[0] + wxPoint(int(vecC[0] * radius), int(vecC[1] * radius))
    # pointE = via[0] + wxPoint(int(vecE[0] * radius), int(vecE[1] * radius))

    # Introduce a last point in order to cover the via centre.
    # If not, the zone won't be filled
    pointD = end2 + wxPoint(int(vecT2[0]*-0.15*w2), int(vecT2[1]*-0.15*w2))
    # pointD = via[0] + wxPoint(int(vec[0]*-0.5*radius), int(vec[1]*-0.5*radius))

    pts = [pointA, pointB, pointC, pointD, pointE]
    if segs > 2:
        pts = __ComputeCurvedTracks(vpercent, w1, vecT1, track2, pts, segs)
        #pts = __ComputeCurved(vpercent, w, vecT, via, pts, segs)

    return pts
##
##
def SetTaper_Zone(pcb=None):
    """Set tapers for track-pad or track-track"""

    if pcb is None:
        pcb = GetBoard()
    selPads = Layout.get_selected_pads()
    selTracks = Layout.get_selected_tracks()
    # taper btw pad & track
    if len(selTracks) == 1 and len(selPads) == 1:
        pad = selPads[0]
        track = selTracks[0]
        segs = 10
        coor = __ComputePoints(track, pad, segs)
        if coor:
            pcb.Add(__Zone(pcb, coor, track))
            RebuildAllZones(pcb)
    elif len(selTracks) == 2 and len(selPads) == 0:
        track1 = selTracks[0]
        track2 = selTracks[1]
        segs = 10
        coor = __ComputePointsTracks(track1, track2, segs)
        if coor:
            pcb.Add(__Zone(pcb, coor, track1))
            RebuildAllZones(pcb)    
    # square taper at the end of a track
    elif len(selTracks) == 1 and len(selPads) == 0:
        track = selTracks[0]
        pnt = track.GetStart()   
        #tracks = Layout.get_tracks_by_pos(pnt)
        # we would need to check the not connected track point
        start = track.GetStart()
        end   = track.GetEnd()        
        for t in pcb.GetTracks():
            if not(t.IsSelected()):
                if track.GetStart() == t.GetStart():
                    start = track.GetEnd()
                    end   = track.GetStart()
                    break
                elif track.GetEnd() == t.GetStart():
                    start = track.GetStart()
                    end   = track.GetEnd()
                    break
                elif track.GetStart() == t.GetEnd():
                    start = track.GetEnd()
                    end   = track.GetStart()
                    break
                elif track.GetEnd() == t.GetEnd():
                    start = track.GetStart()
                    end   = track.GetEnd()
                    break
        w = track.GetWidth()/2
        n = w
        # get normalized track vector
        # it will be used a base vector pointing in the track direction
        vecT = __NormalizeVector(end - start)
        # find point on the track, sharp end of the teardrop
        pointB = start + wxPoint( vecT[0]*n +vecT[1]*w , vecT[1]*n -vecT[0]*w )
        pointA = start + wxPoint( vecT[0]*n -vecT[1]*w , vecT[1]*n +vecT[0]*w )
        pointD = start - wxPoint( vecT[0]*n +vecT[1]*w , vecT[1]*n -vecT[0]*w )
        pointC = start - wxPoint( vecT[0]*n -vecT[1]*w , vecT[1]*n +vecT[0]*w )
        points = [pointA,pointB,pointC,pointD]
        pcb.Add(__Zone(pcb, points, track))       
        RebuildAllZones(pcb)
    else:
        wx.LogMessage('Select one Track & one Pad')
    
##
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
def RebuildAllZones(pcb):
    """Rebuilt all zones"""
    filler = ZONE_FILLER(pcb)
    filler.Fill(pcb.Zones())

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
