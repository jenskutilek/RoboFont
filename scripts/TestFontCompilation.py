from os import remove
from os.path import exists
from mojo.roboFont import version

from jkRFoTools.FontChooser import ProcessFonts

from fontCompiler.compiler import FontCompilerOptions
from fontCompiler.emptyCompiler import EmptyOTFCompiler

def test_compilation(font):
    if font.path is None:
        return "ERROR: The font needs to be saved first."
    font = font.naked()
    compiler = EmptyOTFCompiler()
    options = FontCompilerOptions()
    options.outputPath = font.path + "_compiletest.otf"
    reports = compiler.compile(font, options)
    
    if not "makeotf" in reports:
        return "OK"
    
    result = reports["makeotf"]
    lines = result.splitlines()
    
    if lines[-2][:15] == "makeotf [Error]":
        test_result = ""
        for r in lines:
            if r[:18] in ["makeotfexe [ERROR]", "makeotfexe [FATAL]"]:
                test_result += r[11:] + "\n"
    else:
        test_result = "OK"
        if exists(options.outputPath):
            remove(options.outputPath)
    return test_result

ProcessFonts("Test Compilation", test_compilation)