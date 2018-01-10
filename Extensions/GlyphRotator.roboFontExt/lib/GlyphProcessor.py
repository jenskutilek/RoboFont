from __future__ import absolute_import, division, print_function
## Glyph Processor
## Version 0.1 by Jens Kutilek 2013-03-27

import vanilla

from mojo.roboFont import CurrentFont, CurrentGlyph
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.extensions import getExtensionDefault, setExtensionDefault
from mojo.UI import UpdateCurrentGlyphView
from mojo.events import addObserver, removeObserver


class GlyphProcessorUI(BaseWindowController):
    
    def __init__(self):
        self.extensionID = self.getExtensionID()
        self.font = CurrentFont()
        self.glyph = CurrentGlyph()
        
        self._initSettings()
        self._loadSettings()
        
        self.w = self._buildUI()
        self._addObservers()
        self.setUpBaseWindowBehavior()
        self.w.open()
        #self.glyph.prepareUndo("Glyph Processor")
        UpdateCurrentGlyphView()
    
    def windowCloseCallback(self, sender):
        #self.glyph.performUndo()
        self._removeObservers()
        self._saveSettings()
        super(GlyphProcessorUI, self).windowCloseCallback(sender)
        UpdateCurrentGlyphView()
    
    def getExtensionID(self):
        return "com.netzallee.glyphProcessor"
    
    def _getObservers(self):
        return {
            #"draw": ["_curvePreview",],
            #"drawInactive": ["_curvePreview"],
            "currentGlyphChanged": ["_currentGlyphChangedObserver",],
            "fontDidOpen": ["_fontDidOpenOrCloseObserver",],
            "fontWillClose": ["_fontWillCloseObserver",],
            "fontDidClose": ["_fontDidOpenOrCloseObserver",],
        }
    
    def _addObservers(self):
        for event, observer in self._getObservers().items():
            for method in observer:
                addObserver(self, method, event)
    
    def _initSettings(self):
        self.settings = {}
    
    def _loadSettings(self):
        #print("Load settings ...")
        for k, v in self.settings.items():
            #print("    Setting: '%s': (Default: %s)" % (k, v),)
            self.settings[k] = getExtensionDefault("%s.%s" %(self.extensionID, k), v)
            #print(self.settings[k])
    
    def _loadSettingsFromFont(self):
        if self.font is None:
            self._initSettings()
        else:
            if self.extensionID in self.font.lib.keys():
                self.settings = self.font.lib[self.extensionID]
            else:
                self._initSettings()
    
    def _saveSettings(self):
        #print("Save settings ...")
        for k, v in self.settings.items():
            #print("    Setting: '%s': %s" % (k, v))
            setExtensionDefault("%s.%s" % (self.extensionID, k), v)
    
    def _saveSettingsToFont(self):
        if self.font is not None:
            self.font.lib[self.extensionID] = self.settings
    
    def _removeObservers(self):
        for event in self._getObservers().keys():
                removeObserver(self, event)
        
    def _buildUI(self):
        w = vanilla.FloatingWindow((200, 100), "Glyph Processor")
        return w
        
    # Callbacks and observers
    
    def _currentGlyphChangedObserver(self, info=None):
        self.glyph = CurrentGlyph()
        if self.font != CurrentFont():
            self._saveSettingsToFont()
            del self.settings
            self.font = CurrentFont()
            self._noFontCallback()
            self._loadSettingsFromFont()
        UpdateCurrentGlyphView()
    
    def _fontDidOpenOrCloseObserver(self, info=None):
        self.font = CurrentFont()
        self._noFontCallback()
        self._loadSettingsFromFont()
        UpdateCurrentGlyphView()
    
    def _fontWillCloseObserver(self, info=None):
        if info["font"] == self.font:
            self._saveSettingsToFont()
    
    def _noFontCallback(self):
        # Enable or disable UI elements ...
        if self.font is None:
            print("Font is None")
        else:
            print("Font is not None")
