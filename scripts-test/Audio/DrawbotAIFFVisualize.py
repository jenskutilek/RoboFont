from math import sin, pi, sqrt
from robofab.pens.filterPen import flattenGlyph


def distance(p0, p1, doRound=False):
    # Calculate the distance between two points
    d = sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)
    if doRound:
        return int(round(d))
    else:
        return d

class AIFFVisualize(object):
    def __init__(self, font=None):
        self.set_font(font)
        self.x_offset = 30
        self.y_offset = 280
        self.mark_fill = False
        self.size = (1920, 1080)
        self.scale = 1
    
    def get_font_name(self):
        family = ""
        style = ""
        if self.font.info.familyName is not None:
            family = self.font.info.familyName
        else:
            family = "Unknown family name"
        if self.font.info.styleName is not None:
            style = self.font.info.styleName
        else:
            style = "Unknown family name"
        return "%s %s" % (family, style)
    
    def set_font(self, font=None):
        self.font = font
        self.font_name = self.get_font_name()
        if self.font is not None:
            self.upm = self.font.info.unitsPerEm
            self.desc = self.font.info.descender
            self.x_height = self.font.info.xHeight
            self.cap_height = self.font.info.capHeight
            self.asc = self.font.info.ascender
            self.angle = self.font.info.italicAngle
            print self.angle
        else:
            self.upm = 1000
            self.desc = -250
            self.x_height = 500
            self.cap_height = 700
            self.asc = 750
            self.angle = 0
    
    def _drawMetrics(self, glyph):
        save()
        stroke(0.7)
        w = glyph.width
        line((0, self.desc), (0, self.asc))
        if w != 0:
            line((0, self.desc), (w, 0 + self.desc))
            line((0, 0), (w, 0))
            line((0, self.x_height), (w, 0 + self.x_height))
            line((0, self.cap_height), (w, 0 + self.cap_height))
            line((0, self.asc), (w, 0 + self.asc))
            line((w, self.desc), (w, self.asc))
        restore()
    
    def draw(self, glyph_names=[]):
        if glyph_names == []:
            self.font.glyphOrder
        if self.font is not None:
            for n in glyph_names:
                newDrawing()
                size(self.size[0], self.size[1])
                fontSize(24)
                fill(0.3)
            
                glyph = self.font[n]
                audio_glyph = glyph.copy()
                flattenGlyph(audio_glyph, 4)

                x_offset = int(round((self.size[0] - glyph.width * self.scale) / 2))
                scale(self.scale)
                #self._drawMetrics(glyph)
                num_steps = max([len(contour) for contour in audio_glyph])
                print "Steps:", num_steps
                num_frames = 50
                
                # cache wave forms for drawing: make empty dict with
                # an entry for each contour
                wave_forms = {}
                for wave_index in range(len(audio_glyph)):
                    wave_forms[wave_index] = []
                
                for i in range(num_frames):
                    # set up drawing
                    translate(x_offset, self.y_offset)
                    save()
                    fill(0.3)
                    drawGlyph(glyph)
                    
                    for contour_index in range(len(audio_glyph)):
                        contour = audio_glyph[contour_index]
                        if len(contour) > 1:
                            bbox = contour.box
                            # if bbox is None:
                            #    break
                            pCenter = ((bbox[0] + bbox[2])/2, (bbox[1] + bbox[3])/2)
                            segment_index = i * int(round(len(contour) / num_frames)) % len(contour)
                            p = contour[segment_index].points[-1]
                            save()
                            stroke(0)
                            line((pCenter[0] - 5, pCenter[1] - 5), (pCenter[0] + 5, pCenter[1] + 5))
                            line((pCenter[0] - 5, pCenter[1] + 5), (pCenter[0] + 5, pCenter[1] - 5))
                            
                            r = (contour_index + 3) % 3
                            g = (contour_index + 2) % 3
                            b = (contour_index + 1) % 3
                            stroke(r, g, b)
                            strokeWidth(4)
                            line(pCenter, (p.x, p.y))
                            
                            oval(p.x-5, p.y-5, 10, 10)
                            
                            translate(-x_offset, -self.y_offset)
                            
                            wave_x = self.size[0] / num_frames * i + 5 * contour_index + 10
                            wave_forms[contour_index].append(
                                ((wave_x, 0), (wave_x, distance(pCenter, (p.x, p.y))))
                            )
                            #print wave_forms
                            for a, b in wave_forms[contour_index]:
                                line(a, b)
                            restore()
                    restore()
                    if i < num_frames - 1:
                        newPage()
                saveImage("~/Documents/AIFF_visualize_%s.pdf" % n)
        
        else:
            print "There is no font"

if __name__ == '__main__':
    f = CurrentFont()
    av = AIFFVisualize(f)
    av.draw(f.selection)