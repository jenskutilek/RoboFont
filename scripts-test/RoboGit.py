## RoboGit
## An extension for the RoboFont editor
## Requires RoboFont 1.4
## Version 0.1 by Jens Kutilek 2014-02-22

from sys import exit
try:
    import git
except:
    print "You need to install gitpython before you can use this extension."
    print "$ sudo easy_install gitpython"
    exit()

import vanilla

from os.path import join, basename, splitext, split

from defconAppKit.windows.baseWindow import BaseWindowController
from robofab.glifLib2 import GlyphSet, readGlyphFromString

from mojo.events import addObserver, removeObserver
from mojo.UI import OpenGlyphWindow, UpdateCurrentGlyphView, SmartSet, addSmartSet, removeSmartSet
from mojo.drawingTools import save, restore, fill, strokeWidth, drawGlyph


class RoboGit(BaseWindowController):
    
    scmGroupSetName = "git"
    scmModifiedSetName = "git-changes"
    scmUntrackedSetName = "git-untracked"
    glyphStatus = {}
    untrackedGlyphs = []
    repo = None
    drawing = False
    
    def __init__(self):
        
        columnDescriptions = [
            {"title": "Status",
            "width": 40},
            {"title": "Glyph",
            "typingSensitive": True,
            "editable": False},
        ]
        
        self.w = vanilla.FloatingWindow((180, 280), "RoboGit")
        y = 5
        self.w.showGlyphStatusButton = vanilla.Button((10, y , -10, 25), "Show glyph status",
            callback=self.checkGlyphStatus,
            sizeStyle="small",
        )
        y += 26
        self.w.clearGlyphStatusButton = vanilla.Button((10, y , -10, 25), "Clear glyph status",
            callback=self.uncheckGlyphStatus,
            sizeStyle="small",
        )
        y += 30
        self.w.glyphStatusList = vanilla.List((10, y, -10, -10),
            [], #self.fontAnchors.anchorGlyphs.keys(),
            columnDescriptions=columnDescriptions,
            #editCallback=self.updateMarkVisibility,
            doubleClickCallback=self.openGlyphDiffWindow,
            allowsMultipleSelection=True,
            allowsEmptySelection=False,
        )
        
        self.font = CurrentFont()
        
        self.w.clearGlyphStatusButton.enable(False)
        self.w.showGlyphStatusButton.enable(False)
        if self.fontIsVersioned():
            self.w.showGlyphStatusButton.enable(True)
        self.setUpBaseWindowBehavior()
        self.w.open()
    
    def addObservers(self):
        addObserver(self, "drawDiffGlyph", "drawInactive")
        addObserver(self, "drawDiffGlyph", "drawBackground")
    
    def removeObservers(self):
        removeObserver(self, "drawBackground")
        removeObserver(self, "drawInactive")
    
    def findGitDir(self, fontPath):
        head = self.font.fileName
        while len(head) != 0:
            head, tail = split(head)
            if git.repo.fun.is_git_dir(join(head, ".git")):
                return head
        return None
    
    def fontIsVersioned(self):
        fontPath = self.font.fileName
        if fontPath is None:
            print "ERROR: Font must be saved and inserted into a versioning system first!"
        else:
            git_dir = self.findGitDir(fontPath)
            print git_dir
            if git_dir is None:
                self.repo = None
                self.w.showGlyphStatusButton.enable(False)
            else:
                self.repo = git.Repo(git_dir)
                self.w.showGlyphStatusButton.enable(True)
                return True
        return False
    
    def getFileNameToGlyphNameMap(self):
        gs = GlyphSet(join(self.font.fileName, "glyphs"))
        return gs.getReverseContents()
    
    def readGlyphStatusGit(self, glifToGlyphMap):
        self.glyphStatus = {}
        self.fileStatus = {}
        self.glyphBlobIndex = {}
        
        if not self.repo.is_dirty(untracked_files=True):
            # repo is clean
            return None
        
        for u in self.repo.untracked_files:
            path_name, file_name = split(u)
            if split(self.font.fileName)[1] in path_name and file_name[-5:] == ".glif":
                name = glifToGlyphMap[split(u)[1]]
                self.glyphStatus[name] = "U"
                self.glyphBlobIndex[name] = None
                self.untrackedGlyphs.append(name)
        
        for i in range(len(self.repo.index.diff(None))):
            d = self.repo.index.diff(None)[i]
            if d.a_blob is None:
                # new file
                status = "New"
                file_name = d.b_blob.name
                path_name = d.b_blob.path
            else:
                if d.b_blob is None:
                    # deleted file
                    status = "Del"
                    file_name = d.a_blob.name
                    path_name = d.a_blob.path
                else:
                    status = "Chg"
                    file_name = d.b_blob.name
                    path_name = d.b_blob.path
            #print "Result:"
            #print "Path:", path_name
            #print "Font:", self.font.fileName
            #print "File:", file_name
            if split(self.font.fileName)[1] in path_name and file_name[-5:] == ".glif":
                glyph_name = glifToGlyphMap.get(file_name)
                self.glyphStatus[glyph_name] = status
                self.glyphBlobIndex[glyph_name] = i
            else:
                self.fileStatus[file_name] = status
                            
    def openGlyphDiffWindow(self, sender):
        newGlyphName = sender.get()[sender.getSelection()[0]]["Glyph"]
        #print "Goto Glyph:", newGlyphName
        OpenGlyphWindow(glyph=self.font[newGlyphName])
    
    def getHeadGlyphFromRepo(self, glyphName):
        #filepath = self.getGlyphNameToFileNameMap()[glyphName]
        data = self.repo.index.diff(None)[self.glyphBlobIndex[glyphName]].a_blob.data_stream.read()
        temp_glyph = RGlyph()
        readGlyphFromString(data, temp_glyph, temp_glyph.getPointPen())
        return temp_glyph
    
    def readAllHeadGlyphsFromRepo(self):
        self.headGlyphs = {}
        for glyph_name, index in self.glyphBlobIndex.iteritems():
            if index is not None:
                self.headGlyphs[glyph_name] = self.getHeadGlyphFromRepo(glyph_name)
    
    def drawDiffGlyph(self, info):
        g = info["glyph"]
        if g is not None:
            if g.name in self.headGlyphs:
                save()
                strokeWidth(None)
                fill(1,0,0,0.2)
                drawGlyph(self.headGlyphs[g.name])
                restore()
    
    def checkGlyphStatus(self, sender):
        self.readGlyphStatusGit(self.getFileNameToGlyphNameMap())
        changesList = []
        for glyphname, status in self.glyphStatus.iteritems():
            changesList.append({"Status": status, "Glyph": glyphname})
        self.readAllHeadGlyphsFromRepo()
        print self.headGlyphs
        self.w.glyphStatusList.set(changesList)
        self.w.clearGlyphStatusButton.enable(True)
        self.w.showGlyphStatusButton.enable(False)
        #self._addSets()
        self.addObservers()
        self.drawing =  True
        UpdateCurrentGlyphView()
    
    def uncheckGlyphStatus(self, sender):
        self.glyphStatus = {}
        self.glyphBlobIndex = {}
        self.fileStatus = {}
        self.headGlyphs = {}
        self.w.glyphStatusList.set([])
        self.removeObservers()
        #self._removeSets()
        self.w.clearGlyphStatusButton.enable(False)
        self.w.showGlyphStatusButton.enable(True)
        self.drawing =  False
        UpdateCurrentGlyphView()
    
    # FIXME: Adding sets works, but they don't show up in the current font window.
    #        Removing sets doesn't work at all.
    
    def _addSets(self):
        sc = SmartSet()
        sc.name = self.scmModifiedSetName
        sc.glyphNames = self.headGlyphs.keys()
        addSmartSet(sc)
        
        su = SmartSet()
        su.name = self.scmUntrackedSetName
        su.glyphNames = self.untrackedGlyphs
        addSmartSet(su)
    
    def _removeSets(self):
        removeSmartSet(self.scmModifiedSetName)
        removeSmartSet(self.scmUntrackedSetName)
        
    def windowCloseCallback(self, sender):
        if self.drawing:
            self.removeObservers()
        UpdateCurrentGlyphView()
        super(RoboGit, self).windowCloseCallback(sender)

if CurrentFont() is not None:
    OpenWindow(RoboGit)
