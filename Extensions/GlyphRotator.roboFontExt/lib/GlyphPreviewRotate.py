# Advanced GlyphProcessor

from vanilla import FloatingWindow, Slider
from mojo.glyphPreview import GlyphPreview
from GlyphProcessor import GlyphProcessorUI


class RotatedGlyphPreview(GlyphProcessorUI):
    
    def __init__(self):
        self.extensionID = self.getExtensionID()
        self.font = CurrentFont()
        
        self._initSettings()
        self._loadSettings()
        
        self.w = self._buildUI()
        self._addObservers()
        self.setUpBaseWindowBehavior()
        self._draw()
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
            "currentGlyphChanged": ["_currentGlyphChangedObserver",],
        }
    
    def _currentGlyphChangedObserver(self, info=None):
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
    
    def _draw(self):
        if CurrentGlyph() is not None:
            self.previewGlyph = CurrentGlyph().copy()
            y = (self.font.info.ascender + self.font.info.descender) / 2
            self.previewGlyph.rotate(self.settings["rotation"], (self.previewGlyph.width/2.0, y))
        else:
            self.previewGlyph = RGlyph()
        self.w.preview.setGlyph(self.previewGlyph)
    
    def _initSettings(self):
        self.settings = {
            "rotation": 0,
        }
    

OpenWindow(RotatedGlyphPreview)