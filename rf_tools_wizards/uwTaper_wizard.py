#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
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
#

# This python script wizard creates an arc track for microwave applications
# Author  easyw
# taskkill -im pcbnew.exe /f &  C:\KiCad-v5-nightly\bin\pcbnew

from __future__ import division

import math, cmath

from pcbnew import *
import pcbnew
import FootprintWizardBase


class uwTaper_wizard(FootprintWizardBase.FootprintWizard):

    def GetName(self):
        return "uW Taper Pad"

    def GetDescription(self):
        return "uW Taper Pad Footprint Wizard"

    def GenerateParameterList(self):

        self.AddParam("Taper", "P1 width", self.uMM, 0.5, min_value=0, hint="Pad 1 width")
        self.AddParam("Taper", "P1 height", self.uMM, 0.5, min_value=0, hint="Pad 1 height")
        self.AddParam("Taper", "P2 width", self.uMM, 1.0, min_value=0, hint="Pad 2 width")
        self.AddParam("Taper", "P2 height", self.uMM, 1.0, min_value=0, hint="Pad 2 height")
        self.AddParam("Taper", "P2 vert offset", self.uMM, 0.0, hint="Pad 2 vertical offset")
        self.AddParam("Taper", "length", self.uMM, 3.0, min_value=0, hint="length")
        self.AddParam("Taper", "solder_clearance", self.uMM, 0.0, min_value=0, hint="Solder Clearance")
        
    def CheckParameters(self):

        pads = self.parameters['Taper']
        

    def GetValue(self):
        name = "{0:.2f}_{1:0.2f}_{2:.2f}_{3:.2f}_{4:.2f}".format(pcbnew.ToMM(self.parameters["Taper"]["P1 width"]),\
               pcbnew.ToMM(self.parameters["Taper"]["P1 height"]),pcbnew.ToMM(self.parameters["Taper"]["P2 width"]),\
               pcbnew.ToMM(self.parameters["Taper"]["P2 height"]),pcbnew.ToMM(self.parameters["Taper"]["length"]))
        return "uwT" + "%s" % name
    
    def GetReferencePrefix(self):
        return "uwT" + "***"

    # build a custom pad
    def smdCustomPolyPad(self, module, size, pos, name, vpoints, layer, solder_clearance):
        pad = D_PAD(module)
        ## NB pads must be the same size and have the same center
        pad.SetSize(size)
        #pad.SetSize(pcbnew.wxSize(size[0]/5,size[1]/5))
        pad.SetShape(PAD_SHAPE_CUSTOM) #PAD_RECT)
        pad.SetAttribute(PAD_ATTRIB_SMD) #PAD_SMD)
        #pad.SetDrillSize (0.)
        #Set only the copper layer without mask
        #since nothing is mounted on these pads
        #pad.SetPos0(wxPoint(0,0)) #pos)
        #pad.SetPosition(wxPoint(0,0)) #pos)
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        #pad.SetOffset(pos)
        pad.SetPadName(name)
        #pad.Rotate(pos, angle)
        pad.SetAnchorPadShape(PAD_SHAPE_RECT) #PAD_SHAPE_CIRCLE) #PAD_SHAPE_RECT)
        if solder_clearance > 0:
            pad.SetLocalSolderMaskMargin(solder_clearance)
            pad.SetLayerSet(pad.ConnSMDMask())
        else:
            pad.SetLayerSet( LSET(layer) )
        
        pad.AddPrimitive(vpoints,0) # (size[0]))
        return pad

    def smdPad(self,module,size,pos,name,ptype,angle_D,layer,solder_clearance,offs=None):
        pad = D_PAD(module)
        pad.SetSize(size)
        pad.SetShape(ptype)  #PAD_SHAPE_RECT PAD_SHAPE_OVAL PAD_SHAPE_TRAPEZOID PAD_SHAPE_CIRCLE 
        # PAD_ATTRIB_CONN PAD_ATTRIB_SMD
        pad.SetAttribute(PAD_ATTRIB_SMD)
        if solder_clearance > 0:
            pad.SetLocalSolderMaskMargin(solder_clearance)
            pad.SetLayerSet(pad.ConnSMDMask())
        else:
            pad.SetLayerSet( LSET(layer) )
        #pad.SetDrillSize (0.)
        #pad.SetLayerSet(pad.ConnSMDMask())
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        #pad.SetOrientationDegrees(90-angle_D/10)
        pad.SetOrientationDegrees(angle_D)
        if offs is not None:
            pad.SetOffset(offs)
        pad.SetName(name)
        return pad

    def Polygon(self, points, layer):
            """
            Draw a polygon through specified points
            """
            import pcbnew
            
            polygon = pcbnew.EDGE_MODULE(self.module)
            polygon.SetWidth(0) #Disables outline

            polygon.SetLayer(layer)
            polygon.SetShape(pcbnew.S_POLYGON)

            polygon.SetPolyPoints(points)

            self.module.Add(polygon)
        
    def BuildThisFootprint(self):

        pads = self.parameters['Taper']
        
        width1 = pads['P1 width']
        width2 = pads['P2 width']
        height1 = pads['P1 height']
        height2 = pads['P2 height']
        length =  pads['length']
        p2vof = pads['P2 vert offset']
        sold_clear = pads['solder_clearance']
        w1=width1;w2=width2;
        h1=height1;h2=height2;
        
        pos = pcbnew.wxPoint(0,0)
        offset1 = pcbnew.wxPoint(0,0)
        #offset2 = pcbnew.wxPoint(length+w1/2,0)
        offset2 = pcbnew.wxPoint(0,0)
        module = self.module
        #  1   2  3  4
        #         +--+
        #        /   |
        #       /    |
        #9 +---+     |
        #  | +     + |
        #8 +---+     |
        #       \    |
        #        \   |
        #         +--+
        #      7  6  5
        points = [
                (-w1/2,-h1/2),
                (w1/2,-h1/2),
                (w1/2+length-w2/2,-h2/2-p2vof),
                (w1/2+length+w2/2,-h2/2-p2vof),
                (w1/2+length+w2/2,h2/2-p2vof),
                (w1/2+length-w2/2,h2/2-p2vof),
                (w1/2,h1/2),
                (-w1/2,h1/2),
                ]        
        #Last two points can be equal
        if points[-2] == points[-1]:
            points = points[:-1]
        points = [wxPoint(*point) for point in points]
        vpoints = wxPoint_Vector(points)
        # self.Polygon(points, F_Cu)

        size_pad = pcbnew.wxSize(width1, height1)
        #module.Add(self.smdPad(module, size_pad, pcbnew.wxPoint(0,0), "1", PAD_SHAPE_RECT,0,F_Cu,sold_clear,offset1))
        module.Add(self.smdCustomPolyPad(module, size_pad, wxPoint(0,0), "1", vpoints,F_Cu,sold_clear))
        
        size_pad = pcbnew.wxSize(width2, height2)
        #solder clearance added only to polygon
        module.Add(self.smdPad(module, size_pad, pcbnew.wxPoint(length+w1/2,0-p2vof), "1", PAD_SHAPE_RECT,0,F_Cu,0.0,offset2))
        
        # Text size
        text_size = self.GetTextSize()  # IPC nominal
        thickness = self.GetTextThickness()
        textposy = self.draw.GetLineThickness()/2 + self.GetTextSize()/2 + thickness #+ outline['margin']
        height = max(height1,height2)
        self.draw.Reference( 0+length/2, -textposy-height/2, text_size )
        self.draw.Value( 0+length/2, textposy+height/2+text_size/2, text_size )
        # set SMD attribute
        module.SetAttributes(pcbnew.MOD_VIRTUAL)
        __version__ = 1.3
        self.buildmessages += ("version: {:.1f}".format(__version__))

uwTaper_wizard().register()
