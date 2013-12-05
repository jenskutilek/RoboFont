from string import split
from os import remove
from mojo.roboFont import version

f = CurrentFont()
tf = f.copy(showUI=False)

for g in tf:
    g.clear()

myPath = f.path + "_compiletest.otf"
result = tf.generate(myPath, "otf")
tf.close()

lines = split(result, "\n")

if version[:3] == "1.5":
    checkLine = -3
else:
    checkLine = -1

if lines[checkLine][:15] == "makeotf [Error]":
    print "Font compilation failed."
    for r in lines:
        if r[:18] in ["makeotfexe [ERROR]", "makeotfexe [FATAL]"]:
            print r[11:]
else:
    print "Font will compile successfully."
    remove(myPath)