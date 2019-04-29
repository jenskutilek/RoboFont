from __future__ import absolute_import, division, print_function
# Advanced GlyphProcessor

from vanilla import FloatingWindow, Slider
from mojo.glyphPreview import GlyphPreview
from mojo.roboFont import version as roboFontVersion
from GlyphProcessor import GlyphProcessorUI
from fontTools.misc.transform import Identity


class RotatedGlyphPreview(GlyphProcessorUI):
    
    def __init__(self):
        self.extensionID = self.getExtensionID()
        
        self._initSettings()
        self._loadSettings()
        
        self.w = self._buildUI()
        self._addObservers()
        self.setUpBaseWindowBehavior()
        self._currentGlyphChangedObserver()
        self.w.open()
    
    def _getExtensionID(self):
        return "com.netzallee.rotatedGlyphPreview"
    
    def _buildUI(self):
        w = FloatingWindow((300, 340), "Rotated Glyph Preview", (300, 340), (2560, 1440))
        w.preview = GlyphPreview((2, 2, -2, -40))
        w.rotationSlider = Slider((10, -30, -10, 20),
            minValue=-180,
            maxValue=180,
            value=self.settings["rotation"],
            tickMarkCount=5,
            stopOnTickMarks=False,
            continuous=True,
            callback=self._setRotation,
            sizeStyle="small",
        )
        
        return w
    
    def _getObservers(self):
        return {
            "draw": ["_currentGlyphChangedObserver",],
            "currentGlyphChanged": ["_currentGlyphChangedObserver",],
        }
    
    def _currentGlyphChangedObserver(self, info=None):
        if CurrentFont() is not None:
            self._scale = 1000 / CurrentFont().info.unitsPerEm
            self._y = (CurrentFont().info.ascender + CurrentFont().info.descender) / 2 * self._scale
        else:
            self._scale = 1
            self._y = 500
        self._draw()
        
    def _setRotation(self, sender):
        _rotation = sender.get()
        if 87 <= _rotation <= 93:
            _rotation = 90
        elif -93 <= _rotation <= -87:
            _rotation = -90
        elif -3 <= _rotation <= 3:
            _rotation = 0
        self.settings["rotation"] = _rotation
        self._draw()

    def _deepAppendGlyph(self, glyph, gToAppend, font, offset=(0, 0)):
        if not gToAppend.components:
            glyph.appendGlyph(gToAppend, offset)
        else:
            for component in gToAppend.components:
                if component.baseGlyph not in font.keys():
                    # avoid traceback in the case where the selected glyph
                    # is referencing a component whose glyph is not in the font
                    continue

                compGlyph = font[component.baseGlyph].copy()

                if component.transformation != (1, 0, 0, 1, 0, 0):
                    # if component is skewed and/or is shifted:
                    matrix = component.transformation[0:4]
                    if matrix != (1, 0, 0, 1):  # if component is skewed
                        transformObj = Identity.transform(matrix + (0, 0))
                        # ignore the original component's shifting values
                        compGlyph.transform(transformObj)

                # add the two tuples of offset:
                totalOffset = tuple(map(sum, zip(component.offset, offset)))
                glyph.appendGlyph(compGlyph, totalOffset)

            for contour in gToAppend:
                glyph.appendContour(contour, offset)

        # if the assembled glyph still has components, recursively
        # remove and replace them 1-by-1 by the glyphs they reference:
        if glyph.components:
            nestedComponent = glyph.components[-1]
            glyph.removeComponent(nestedComponent)
            glyph = self._deepAppendGlyph(glyph, font[nestedComponent.baseGlyph], font, nestedComponent.offset)

        return glyph

    def _draw(self):
        cG = CurrentGlyph()
        if cG is not None:
            self.previewGlyph = self._deepAppendGlyph(RGlyph(), cG, CurrentFont())
            self.previewGlyph.width = cG.width * self._scale
            if roboFontVersion >= "2.0b":
                self.previewGlyph.scaleBy((self._scale, self._scale))
                self.previewGlyph.rotateBy(self.settings["rotation"], (self.previewGlyph.width / 2, self._y))
            else:
                self.previewGlyph.scale((self._scale, self._scale))
                self.previewGlyph.rotate(self.settings["rotation"], (self.previewGlyph.width / 2, self._y))
        else:
            self.previewGlyph = RGlyph()
        self.w.preview.setGlyph(self.previewGlyph)
    
    def _initSettings(self):
        self.settings = {
            "rotation": 0,
        }
    

OpenWindow(RotatedGlyphPreview)
