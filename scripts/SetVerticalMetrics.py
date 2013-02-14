'''
Dieses Macro ermittelt den hoechsten Punkt aller offenen Fonts und den niedrigsten Punkt
einer Auswahl von Glyphen aller offenen Fonts und berechnet auf dieser Basis die vertikalen
Metriken nach dem Schema von Karsten Luecke und schreibt das Ergebnis nach Rueckfrage in
alle offenen Fonts.

2009, Jens Kutilek
'''

from robofab.interface.all.dialogs import AskYesNoCancel

# Versuche die Liste der ausgenommenen Glyphen aus meinem Python-Modul
# "jkFLTools" zu importieren; wenn das nicht klappt, benutze die hier
# angegebene Liste
try:
	from jkFLTools import vMetricsExcludeGlyphs
except:
	vMetricsExcludeGlyphs = ["Aringacute", "aringacute"]

maxY = 0 # Koordinaten
minY = 0

maxG = "" # Glyphnamen
minG = ""

ignored = "" # ignorierte Glyphnamen

# Descender-Wert soll aus dieser Liste von Glyphen ermittelt werden
descenderGlyphNames = ["g", "j", "p", "q", "y"]

# Schleife ueber die geoeffneten Fonts
for i in range(len(AllFonts())):
	# erzeuge eine Kopie des Fonts mit dem Index i
	# (weil Composites aufgeloest werden, aber der Originalfont nicht veraendert werden soll)
	fTemp = AllFonts()[i].copy()
	 
	# Schleife ueber die Glyphen des kopierten Fonts
	for g in fTemp:
		if (g.name in vMetricsExcludeGlyphs) or (g.note == "vMetricsIgnore"):
			# Wenn Glyphname auf Liste der zu ignorierenden Glyphen steht, 
			# oder eine Glyphnote "vMetricsIgnore" enthaelt, notiere nur den
			# Namen und mache sonst nichts
			ignored += g.name + " "
		else:
			# Wenn Glyph nicht ignoriert werden soll ...
			b = g.box
			if (b is not None) and (b[3] > maxY):
				# Y-Koordinate des aktuellen Glyphen ist groesser als vorheriger Wert
				maxY = b[3] # merke den neuen Maximalwert
				maxG = g.name # merke auch den Glyphnamen
	# Fuer den Descender-Wert: Schleife ueber Liste "descenderGlyphNames"
	for n in descenderGlyphNames:
		if n in fTemp.keys():
			# Glyph ist im Font enthalten
			b = fTemp[n].box
			if (b is not None) and (b[1] < minY):
				# Y-Koordinate des aktuellen Glyphen ist kleiner als vorheriger Wert
				minY = b[1] # merke den neuen Minimalwert
				minG = g.name # merke auch den Glyphnamen

# Plausibilitaetspruefung des Descenderwerts
upm = CurrentFont().info.unitsPerEm
if minY > upm  / -10:
	# Wenn minimale y-Koordinate groesser als ein zehntel der
	# UPM-Groesse ist (z.B. Font ohne Unterlaengen) ...
	defaultDescender = upm  / -10 # setze Descender auf 1/10 der UPM
	print "  WARNING: Descender value is", minY, "- setting to default value", defaultDescender
	minY = defaultDescender

# Berechnung der verschiedenen Metrik-Werte nach Schema von Karsten Luecke
vDescender       = minY
vAscender        = minY + upm 
os2TypoDescender = vDescender
os2TypoAscender  = vAscender
hheaAscender     = maxY
hheaDescender    = minY
hheaLineGap      = 0
os2TypoLineGap   = hheaAscender + abs(hheaDescender) - (os2TypoAscender + abs(os2TypoDescender))
os2WinAscent     = hheaAscender
os2WinDescent    = -1 * hheaDescender


# Alle Werte ins Output-Fenster schreiben
print "\nMin:            %5d (%s)" % (minY, minG)
print "Max:            %5d (%s)" % (maxY, maxG)
print "UPM:            %5d" % upm
print "---------------------"
print "Ascender:       %5d" % vAscender
print "Descender:      %5d" % vDescender
print "---------------------"
print "OS/2 TypoAsc.:  %5d" % os2TypoAscender
print "OS/2 TypoDesc.: %5d" % os2TypoDescender
print "OS/2 TypoLinG.: %5d" % os2TypoLineGap
print "---------------------"
print "hhea Ascender:  %5d" % hheaAscender
print "hhea Descender: %5d" % hheaDescender
print "hhea LineGap:   %5d" % hheaLineGap
print "---------------------"
print "OS/2 WinAsc.:   %5d" % os2WinAscent
print "OS/2 WinDesc.:  %5d" % os2WinDescent

print "\nIgnored glyphs:",
if ignored == "":
	print "none"
else:
	print ignored


# Dialogbox, ob ermittelte Metriken in offene Fonts geschrieben werden sollen
setMetrics = AskYesNoCancel("Write calculated vertical metrics to font? (For values see Output window)", title="Set Vertical Metrics", default=0)

if setMetrics == 1:	# Antwort war ja, schreibe Werte in die Fonts
	print "\nWriting metrics to font"
	# Schleife ueber offene Fonts
	for f in AllFonts():
		# Setze Werte im Font
		f.info.ascender = vAscender
		f.info.descender = vDescender
		f.info.openTypeHheaAscender = hheaAscender
		f.info.openTypeHheaDescender = hheaDescender
		f.info.openTypeHheaLineGap = hheaLineGap
		f.info.openTypeOS2TypoAscender = os2TypoAscender
		f.info.openTypeOS2TypoDescender = os2TypoDescender
		f.info.openTypeOS2TypoLineGap = os2TypoLineGap
		f.info.openTypeOS2WinAscent = os2WinAscent
		f.info.openTypeOS2WinDescent = os2WinDescent

else:	# Antwort war nein
	print "\nNot writing metrics to font"