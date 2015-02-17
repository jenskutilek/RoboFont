RoboFont
========

Some scripts for the RoboFont editor that you may find useful. Use at your own risk. MIT-licensed.

Curve Equalizer
---------------

Quickly balance the Bézier handles of a curve, or change its curvature. Available from: https://github.com/jenskutilek/Curve-Equalizer

ChangeUPM.py
------------

Changes a UFO’s upm size and scales all metrics and outlines accordingly.

SetVerticalMetrics.py
---------------------

Measures all open fonts and calculates vertical metrics according to Karsten Lücke’s method.

TestFontCompilation.py
---------------------

Makes a copy of the current font and tries to generate it, mainly to check your OT feature code.
All glyphs are cleared, so this is much faster than regular generation where you have to
wait for remove overlaps, decompose, etc.

If any errors occur, the error messages are displayed in the output window.

TestInstallAllOpen.py
---------------------

Test install all open fonts.
