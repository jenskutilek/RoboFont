import aifc

"""
For the "import aifc" to work, you need to link some system libraries into RoboFont:

ln -s /System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/aifc.py \
    /Applications/RoboFont.app/Contents/Resources/lib/python2.7/

ln -s /System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/fractions.py \
    /Applications/RoboFont.app/Contents/Resources/lib/python2.7/

ln -s /System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/decimal.py \
    /Applications/RoboFont.app/Contents/Resources/lib/python2.7/

ln -s /System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/numbers.py \
    /Applications/RoboFont.app/Contents/Resources/lib/python2.7/

"""

from struct import pack
from math import sin, pi, sqrt
from robofab.pens.filterPen import flattenGlyph

def getAverage(myList):
    sum = 0
    for i in myList:
        sum += i
    r = int(sum) / 32
    return r

def distance(p0, p1, doRound=False):
    # Calculate the distance between two points
    d = sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)
    if doRound:
        return int(round(d))
    else:
        return d

def scaleList(l, maxAmp=127):
    #print "Min:", min(l)
    #print "Max:", max(l)
    amp = (max(l) + min(l)) / 2.0
    #print "Amp:", amp
    scaledList = []
    scale = float(maxAmp)/(max(l)-amp)/2
    for v in l:
        scaledList.append(int((v - amp) * scale))
    return scaledList

def getModVal(myList, i):
    # return index from list, endlessly
    return myList[i % len(myList)]

from fractions import gcd
kgv = lambda ns: reduce(lambda x,y:x*y/gcd(x,y),ns)

def each_glyph_to_aiff():
    # chords
    f = CurrentFont()
    #m = 0
    for n in f.selection:
        a = aifc.open("aiff_out/%s_%s.aiff" % (str(f.info.familyName), n), "wb")
        a.setnchannels(1)
        a.setsampwidth(2)
        a.setframerate(44100)
    
        g = f[n]
        flattenGlyph(g, 4)
        print "Glyph:", g.name
        #m += 1
        #a.setmark(m, a.tell(), g.name)
        cDists = {}
        for i in range(len(g)):
            cList = []
            c = g[i]
            b = c.box
            if b is None:
                # ignore anchors, they have no bounding box
                break
            pCenter = ((b[0] + b[2])/2, (b[1] + b[3])/2)
            for p in c.points:
                cList.append(distance(pCenter, (p.x, p.y), doRound=True))
            cDists[i] = cList

        amps = {}
        listLengths = []
        for k, myList in cDists.iteritems():
            listLengths.append(len(myList))
            amps[k] = scaleList(myList, 255)
        print "    Loop lengths: %s (samples)" % listLengths
        loopLength = kgv(listLengths)
        if loopLength < 44100:
            loopLength *= 44100/loopLength
        if loopLength > 441000:
            loopLength /= loopLength/44100
        print "    Chord loop: %i samples" % loopLength
        for i in range(int(round(loopLength))):
            myVal = 0
            numWaves = len(amps.keys())
            for k in amps.iterkeys():
                myVal += getModVal(amps[k], i)
            myVal /= numWaves
            a.writeframes(pack("<h", myVal))            
        #myVal = pack("i", 0)
        #for i in range(10000):
        #    a.writeframes(myVal)
        a.close()
    print "Done."

def all_glyphs_in_one_aiff():
    # all tones after another
    f = CurrentFont()
    a = aifc.open("aiff_out/aiffContours.aiff", "wb")
    a.setnchannels(1)
    a.setsampwidth(4)
    a.setframerate(44100)
    m = 0
    for n in f.selection:
        g = f[n]
        flattenGlyph(g, 4)
        print g.name
        m += 1
        a.setmark(m, a.tell(), g.name)
        cDists = {}
        for i in range(len(g)):
            cList = []
            c = g[i]
            b = c.box
            if b is None:
                # ignore anchors, they have no bounding box
                break
            pCenter = ((b[0] + b[2])/2, (b[1] + b[3])/2)
            for p in c.points:
                cList.append(distance(pCenter, (p.x, p.y), doRound=True))
            cDists[i] = cList
        amps = {}
        for k, myList in cDists.iteritems():
            amps[k] = scaleList(myList, 255)
        for k, v in amps.iteritems():
            print k
            #print v
            for i in range(100):
                for myVal in v:
                    a.writeframes(pack("i", myVal))
        myVal = pack("i", 0)
        for i in range(10000):
            a.writeframes(myVal)
    a.close()
    print "Done."

if __name__ == "__main__":
    each_glyph_to_aiff()
    all_glyphs_in_one_aiff()