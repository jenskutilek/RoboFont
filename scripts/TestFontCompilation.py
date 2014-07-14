from string import split
from os import remove
from mojo.roboFont import version

from jkRFoTools.FontChooser import ProcessFonts

def test_compilation(font):
    temp_font = font.copy(showUI=False)

    for g in temp_font:
        g.clear()

    myPath = font.path + "_compiletest.otf"
    result = temp_font.generate(myPath, "otf")
    temp_font.close()

    lines = split(result, "\n")

    if version[:3] == "1.5":
        checkLine = -3
    else:
        checkLine = -1

    if lines[checkLine][:15] == "makeotf [Error]":
        test_result = "ERROR: "
        for r in lines:
            if r[:18] in ["makeotfexe [ERROR]", "makeotfexe [FATAL]"]:
                test_result += r[11:] + "; "
    else:
        test_result = "OK"
        remove(myPath)
    return test_result

ProcessFonts("Test Compilation", test_compilation)