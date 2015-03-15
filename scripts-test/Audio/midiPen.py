from fontTools.pens.basePen import AbstractPen
from midi.MidiOutFile import MidiOutFile
from math import sqrt
#from robofab.objects.objectsRF import RPoint

class MidiPen(AbstractPen):
    prev = (0,0)
    
    def moveTo(self, pt):
        d = distance(self.prev, pt, doRound=True)
        global midi
        midi.update_time(d)
        self.prev = pt
        #print "Pause", d
    
    def lineTo(self, pt):
        d = distance(self.prev, pt, doRound=True)
        global midi
        myNote = getNote(self.prev, pt)
        midi.note_on(channel=0, note=myNote)
        midi.update_time(d)
        midi.note_off(channel=0, note=myNote)
        midi.update_time(0)
        self.prev = pt
        print printNote(myNote)

    def curveTo(self, *pts):
        d = distance(self.prev, pts[-1], doRound=True)
        myNotes = []
        prevNote = 0
        for i in range(len(pts)):
            newNote = getNote(self.prev, pts[i])
            if newNote != prevNote:
                myNotes.append(newNote)
            prevNote = newNote
        global midi
        for myNote in myNotes:
            midi.note_on(channel=0, note=myNote)
            midi.update_time(0)
        midi.update_time(d)
        for myNote in myNotes:
            midi.note_off(channel=0, note=myNote)
        midi.update_time(0)
        self.prev = pts[-1]
         
    def qCurveTo(self, *pts):
        d = distance(self.prev, pts[-1], doRound=True)
        global midi
        midi.update_time(d)
        self.prev = pt
        print "qCurveTo"

    def closePath(self):
        #print "closePath"
        pass

    def endPath(self):
        #print "endPath"
        pass

#    def addComponent(self, baseGlyphName, transformation):
#        print "addComponent"

def distance(p0, p1, doRound=False):
    # Calculate the distance between two points
    d = sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)
    if doRound:
        return int(round(d))
    else:
        return d

def printNote(n):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "H"]
    return names[n % 12]

def getNote(p0, p1):
    d = p1[0]-p0[0]
    n = int(round(abs(d/4)))
    while n < 35:
        #print n,
        n += 12
    #print n
    while n > 80:
        #print n,
        n -= 12
    #print n
    return n

def getSelectionName(selection):
    result = ""
    for gn in selection:
        result += gn
    return result

s = CurrentFont().selection
out_file = 'midi_out/%s-%s_%s.mid' % (CurrentFont().info.familyName, CurrentFont().info.styleName , getSelectionName(s))
out_file = 'midi_out/%s-%s_%s.mid' % ("Nimbus", "Sans", getSelectionName(s))

midi = MidiOutFile(out_file)

# non optional midi framework
midi.header(format=1, nTracks=1, division=1024)
midi.start_of_track()
midi.tempo(int(60000000.0/140))
midi.patch_change(0, 1)

# musical events

pen = MidiPen()

for gn in s:
    g =CurrentFont()[gn]
    midi.sequence_name(gn)
    midi.note_on(channel=9, note=36)
    midi.update_time(0)
    midi.note_off(channel=9, note=36)
    midi.update_time(0)
    g.draw(pen)
    print gn,

#midi.update_time(0)
#midi.note_on(channel=0, note=0x40)

#midi.update_time(192)
#midi.note_off(channel=0, note=0x40)

# non optional midi framework
midi.update_time(0)
midi.end_of_track() # not optional!

midi.eof()