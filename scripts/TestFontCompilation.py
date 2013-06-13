from string import split
from os import remove

f = CurrentFont()
tf = f.copy(showUI=False)

for g in tf:
    g.clear()

myPath = f.path + "_compiletest.otf"
result = tf.generate(myPath, "otf")
tf.close()

lines = split(result, "\n")
if lines[-1][:15] == "makeotf [Error]":
    print "Font compilation failed."
    for r in lines:
        if r[:18] == "makeotfexe [ERROR]":
            print r[11:]
else:
    print "Font will compile successfully."
    remove(myPath)
