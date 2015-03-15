# Another script which needs an external module linked into RoboFont ...
"""
ln -s /System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/PyObjC/Foundation \
    /Applications/RoboFont.app/Contents/Resources/lib/python2.7/
ln -s /System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/PyObjC/ScriptingBridge \
    /Applications/RoboFont.app/Contents/Resources/lib/python2.7/
"""

# PyObjC
#from Foundation import *
from ScriptingBridge import *

# SpaceCenter
from mojo.UI import AllSpaceCenters

iTunes = SBApplication.applicationWithBundleIdentifier_("com.apple.iTunes")

track = iTunes.currentTrack().lyrics()

for s in AllSpaceCenters():
    s.setRaw(track.replace("\r", " "))