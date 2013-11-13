## Curve Equalizer
## An extension for the RoboFont editor
## Requires RoboFont 1.4
## Version 0.1 by Jens Kutilek 2013-02-13
## Version 0.2 by Jens Kutilek 2013-03-26
## Version 0.3 by Jens Kutilek 2013-04-06
## Version 0.4 by Jens Kutilek 2013-11-13
## http://www.netzallee.de/extra/robofont

import vanilla

from math import sqrt, atan2, degrees, sin, cos, pi
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.extensions import getExtensionDefault, setExtensionDefault

# For experimental quadratic optimization:
from fontTools.misc.bezierTools import calcCubicParameters, calcCubicPoints

# for live preview:
from mojo.UI import UpdateCurrentGlyphView
from mojo.events import addObserver, removeObserver
from MojoDrawingToolsPen import MojoDrawingToolsPen
from mojo.drawingTools import save, restore, stroke, fill, strokeWidth

extensionID = "de.netzallee.curveEQ"


# helper functions

def getTriangleArea(a, b, c):
    return (b.x -a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)

def isOnLeft(a, b, c):
    if getTriangleArea(a, b, c) > 0:
        return True
    return False

def isOnRight(a, b, c):
    if getTriangleArea(a, b, c) < 0:
        return True
    return False

def isCollinear(a, b, c):
    if getTriangleArea(a, b, c) == 0:
        return True
    return False

def distance(p0, p1, doRound=False):
    # Calculate the distance between two points
    d = sqrt((p0.x - p1.x) ** 2 + (p0.y - p1.y) ** 2)
    if doRound:
        return int(round(d))
    else:
        return d



class CurveEqualizer(BaseWindowController):
    
    def __init__(self):
        
        self.methods = {
            0: "fl",
            1: "thirds",
            2: "quad",
            3: "adjust",
            4: "free",
        }
        
        self.methodNames = [
            "Circle",
            "Rule of thirds",
            "TT (experimental)",
            "Adjust fixed:",
            "Adjust free:"
        ]
        
        self.curvatures = {
            0: 0.552,
            1: 0.577,
            2: 0.602,
            3: 0.627,
            4: 0.652,
        }
        
        height = 160
        
        self.w = vanilla.FloatingWindow((200, height), "Curve EQ")
        
        y = 8
        self.w.eqMethodSelector = vanilla.RadioGroup((10, y, -10, 108),
            titles = self.methodNames,
            callback=self._changeMethod,
            sizeStyle="small"
        )
        
        y -= 91
        self.w.eqCurvatureSelector = vanilla.RadioGroup((104, y, -8, 14),
            isVertical = False,
            titles = ["", "", "", "", ""],
            callback=self._changeCurvature,
            sizeStyle="small"
        )
        
        y += 22
        self.w.eqCurvatureSlider = vanilla.Slider((104, y, -8, 14),
            callback=self._changeCurvatureFree,
            minValue=0.5,
            maxValue=1.0,
            #value=self.curvatures[self.w.eqCurvatureSelector.get()],
            sizeStyle="small",
        )
        
        y = height - 32
        self.w.eqSelectedButton = vanilla.Button((10, y , -10, 25), "Equalize selected",
            callback=self._eqSelected,
            sizeStyle="small",
        )
        
        # default method
        self.w.eqMethodSelector.set(getExtensionDefault("%s.%s" %(extensionID, "method"), 0))
        self.method = self.methods[self.w.eqMethodSelector.get()]
        self._checkSecondarySelectors()
        
        # default curvature
        self.w.eqCurvatureSelector.set(getExtensionDefault("%s.%s" %(extensionID, "curvature"), 0))
        self.curvature = self.curvatures[self.w.eqCurvatureSelector.get()]
        
        # default curvature for slider
        self.w.eqCurvatureSlider.set(getExtensionDefault("%s.%s" %(extensionID, "curvatureFree"), 0.5))
        self.curvatureFree = self.w.eqCurvatureSlider.get()
        
        addObserver(self, "_curvePreview", "draw")
        #addObserver(self, "_curvePreview", "drawPreview")
        addObserver(self, "_curvePreview", "drawInactive")
        addObserver(self, "_currentGlyphChanged", "currentGlyphChanged")
        
        self.tmp_glyph = RGlyph()
        UpdateCurrentGlyphView()
        
        self.setUpBaseWindowBehavior()
        self.w.open()
        
    
    # Callbacks
    
    def _changeMethod(self, sender):
        choice = sender.get()
        self.method = self.methods[choice]
        self._checkSecondarySelectors()
        UpdateCurrentGlyphView()
    
    def _changeCurvature(self, sender):
        choice = sender.get()
        self.curvature = self.curvatures[choice]
        UpdateCurrentGlyphView()
    
    def _changeCurvatureFree(self, sender):
        self.curvatureFree = sender.get()
        UpdateCurrentGlyphView()
    
    def _currentGlyphChanged(self, sender=None):
        UpdateCurrentGlyphView()
    
    def windowCloseCallback(self, sender):
        removeObserver(self, "draw")
        removeObserver(self, "drawInactive")
        #removeObserver(self, "drawPreview")
        removeObserver(self, "currentGlyphChanged")
        setExtensionDefault("%s.%s" % (extensionID, "method"), self.w.eqMethodSelector.get())
        setExtensionDefault("%s.%s" % (extensionID, "curvature"), self.w.eqCurvatureSelector.get())
        setExtensionDefault("%s.%s" % (extensionID, "curvatureFree"), self.w.eqCurvatureSlider.get())
        super(CurveEqualizer, self).windowCloseCallback(sender)
        UpdateCurrentGlyphView()
    
    def _checkSecondarySelectors(self):
        # Enable or disable slider/radio buttons based on primary EQ selection
        if self.method == "adjust":
            self.w.eqCurvatureSelector.enable(True)
            self.w.eqCurvatureSlider.enable(False)
        elif self.method == "free":
            self.w.eqCurvatureSelector.enable(False)
            self.w.eqCurvatureSlider.enable(True)
        else:
            self.w.eqCurvatureSelector.enable(False)
            self.w.eqCurvatureSlider.enable(False)
    
    def getNewCoordinates(self, targetPoint, referencePoint, alternateReferencePoint, distance):
        if targetPoint.y == referencePoint.y and targetPoint.x == referencePoint.x:
            phi = atan2(alternateReferencePoint.y - referencePoint.y, alternateReferencePoint.x - referencePoint.x)
        else:
            phi = atan2(targetPoint.y - referencePoint.y, targetPoint.x - referencePoint.x)
        #print degrees(phi)
        #print "Move P1", p1.x, p1.y,
        x = referencePoint.x + cos(phi) * distance
        y = referencePoint.y + sin(phi) * distance
        return (x, y)
    
    def _curvePreview(self, info):
        _doodle_glyph = info["glyph"]
        if _doodle_glyph is not None and len(_doodle_glyph.components) == 0 and _doodle_glyph.selection != []:
            self.tmp_glyph.clear()
            self.tmp_glyph.appendGlyph(_doodle_glyph)
            self._eqSelected()
            pen = MojoDrawingToolsPen(self.tmp_glyph, _doodle_glyph.getParent())
            save()
            stroke(0, 0, 0, 0.5)
            fill(None)
            strokeWidth(info["scale"])
            self.tmp_glyph.draw(pen)
            pen.draw()
            restore()
            #UpdateCurrentGlyphView()
    
    
    # Equalizer methods
    
    def eqFL(self, p0, p1, p2, p3, curvature=0.552):
        # check angles of the bcps
        # in-point BCPs will report angle = 0
        alpha = atan2(p1.y - p0.y, p1.x - p0.x)
        beta  = atan2(p2.y - p3.y, p2.x - p3.x)
        diff = alpha - beta
        if degrees(abs(diff)) < 45:
            print "BCP angle: %0.1f\xb0 - %0.1f\xb0 = %0.1f\xb0" % (degrees(alpha), degrees(beta), degrees(diff))
            #print "BCP angle: %0.1f - %0.1f = %0.1f" % (alpha, beta, diff)
            print "Bezier handles angle restriction in effect."
        else:
            # check if both handles are on the same side of the curve
            if isOnLeft(p0, p3, p1) and isOnLeft(p0, p3, p2) or isOnRight(p0, p3, p1) and isOnRight(p0, p3, p2):
                
                # calculate intersecting point
                
                alpha1 = atan2(p3.y - p0.y, p3.x - p0.x)
                alpha2 = atan2(p1.y - p0.y, p1.x - p0.x)
                alpha = alpha1 - alpha2
                
                gamma1 = atan2(p3.x - p0.x, p3.y - p0.y)
                gamma2 = atan2(p3.x - p2.x, p3.y - p2.y)
                gamma  = gamma1 - gamma2
                
                beta = pi - alpha - gamma
                
                #print "alpha =", degrees(alpha1), "-", degrees(alpha2), "=", degrees(alpha)
                #print "gamma =", degrees(gamma1), "-", degrees(gamma2), "=", degrees(gamma)
                #print "beta =", degrees(beta)
                
                b = abs(distance(p0, p3))
                a = b * sin(alpha) / sin(beta)
                c = b * sin(gamma) / sin(beta)
                
                #print "a =", a
                #print "b =", b
                #print "c =", c
                
                c = c * curvature
                a = a * curvature
                
                # move first control point
                p1.x, p1.y = self.getNewCoordinates(p1, p0, p2, c)
                
                # move second control point
                p2.x, p2.y = self.getNewCoordinates(p2, p3, p1, a)
                
            else:
                print "Handles are not on the same side of the curve."
        return p1, p2
    
    def eqThirds(self, p0, p1, p2, p3):
        # get distances
        a = distance(p0, p1)
        b = distance(p1, p2)
        c = distance(p2, p3)
        
        # calculate equal distance
        d = (a + b + c) / 3.0
    
        # move first control point
        p1.x, p1.y = self.getNewCoordinates(p1, p0, p2, d)
        
        # move second control point
        p2.x, p2.y = self.getNewCoordinates(p2, p3, p1, d)
        
        return p1, p2
    
    def eqQuadratic(self, p0, p1, p2, p3):
        # Nearest quadratic bezier (TT curve)
        #print "In: ", p0, p1, p2, p3
        a, b, c, d = calcCubicParameters((p0.x, p0.y), (p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y))
        #print "Par: %0.0f x^3 + %0.0f x^2 + %0.0f x + %0.0f" % (a[0], b[0], c[0], d[0])
        #print "     %0.0f y^3 + %0.0f y^2 + %0.0f y + %0.0f" % (a[1], b[1], c[1], d[1])
        a = (0.0, 0.0)
        q0, q1, q2, q3 = calcCubicPoints((0.0, 0.0), b, c, d)
        # Find a cubic for a quadratic:
        #cp1 = (q0[0] + 2.0/3 * (q1[0] - q0[0]), q0[1] + 2.0/3 * (q1[1] - q0[1]))
        #cp2 = (q2[0] + 2.0/3 * (q1[0] - q2[0]), q2[1] + 2.0/3 * (q1[1] - q2[1]))
        #print "Out:", q0, q1, q2, q3
        scaleX = (p3.x - p0.x) / (q3[0] - q0[0])
        scaleY = (p3.y - p0.y) / (q3[1] - q0[1])
        #print scaleX, scaleY
        p1.x = (q1[0] - q0[0]) * scaleX + q0[0]
        p1.y = (q1[1] - q0[1]) * scaleY + q0[1]
        p2.x = (q2[0] - q0[0]) * scaleX + q0[0]
        p2.y = (q2[1] - q0[1]) * scaleY + q0[1]
        p3.x = (q3[0] - q0[0]) * scaleX + q0[0]
        p3.y = (q3[1] - q0[1]) * scaleY + q0[1]
        #print p0, p1, p2, p3
        return p1, p2
    
    
    # The main method, check which EQ should be applied and do it (or just apply it on the preview glyph)
    
    def _eqSelected(self, sender=None):
        reference_glyph = CurrentGlyph()
        if reference_glyph.selection != []:
            if sender is None:
                # EQ button not pressed, preview only.
                modify_glyph = self.tmp_glyph
            else:
                modify_glyph = reference_glyph
                reference_glyph.prepareUndo(undoTitle="Equalize curve in /%s" % reference_glyph.name)
            for contourIndex in range(len(reference_glyph.contours)):
                reference_contour = reference_glyph.contours[contourIndex]
                modify_contour = modify_glyph.contours[contourIndex]
                for i in range(len(reference_contour.segments)):
                    reference_segment = reference_contour[i]
                    modify_segment = modify_contour[i]
                    if reference_segment.selected and reference_segment.type == "curve":
                        # last point of the previous segment
                        p0 = modify_contour[i-1][-1]
                        p1, p2, p3 = modify_segment.points
                        
                        if self.method == "fl":
                            p1, p2 = self.eqFL(p0, p1, p2, p3)
                        elif self.method == "thirds":
                            p1, p2 = self.eqThirds(p0, p1, p2, p3)
                        elif self.method == "quad":
                            p1, p2 = self.eqQuadratic(p0, p1, p2, p3)
                        elif self.method == "adjust":
                            p1, p2 = self.eqFL(p0, p1, p2, p3, self.curvature)
                        elif self.method == "free":
                            p1, p2 = self.eqFL(p0, p1, p2, p3, self.curvatureFree)
                        else:
                            print "WARNING: Unknown equalize method: %s" % self.method
                        if sender is not None:
                            p1.round()
                            p2.round()
            reference_glyph.update()
            if sender is not None:
                reference_glyph.performUndo()    

OpenWindow(CurveEqualizer)