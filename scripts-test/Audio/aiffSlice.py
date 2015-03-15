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
from math import sin, pi
from robofab.pens.filterPen import flattenGlyph

from robofab.pens.marginPen import MarginPen

def getAverage(myList):
    sum = 0
    for i in myList:
        sum += i
    r = int(sum) / 32
    return r

def main():
    f = CurrentFont()
    a = aifc.open("aiff_out/aiffSlice.aiff", "wb")
    a.setnchannels(1)
    a.setsampwidth(4)
    a.setframerate(44100)
    #for i in range(80):
    #    v = sin(i/44100.0 * 440.0 * pi) * 2**7
    #    print v
    #    a.writeframes(pack("h", v))
    for n in f.selection:
        g = f[n]
        print n
        #for c in g.contours:
        #    print c.box
        #    for 
        for i in range(int(g.width)):
            pen = MarginPen(f, i, isHorizontal=False)
            g.draw(pen)
            l = pen.getAll()
            #print l,
            v = getAverage(l)
            #print v
            a.writeframes(pack("i", v))
            a.writeframes(pack("i", v))
            
    a.close()

if __name__ == "__main__":
    main()