import vanilla
from sys import getsizeof
from defconAppKit.windows.baseWindow import BaseWindowController
from lib.scripting.codeEditor import CodeEditor
try:
    from plistlib import writePlistToString
except ImportError:
    from plistlib import dumps as writePlistToString
from knownKeys import known_keys


class UFOCleaner(BaseWindowController):
    
    def __init__(self):
        self._font = CurrentFont()
        self._libkeys = []
        self._key_contents = {}
        self._seen_keys = []
        self._known_keys = known_keys
        self._key_sizes = {}
        self.total_size = 0
        self._collect_keys()
        self._build_ui()
        self._update_total_size_display()
    
    def _build_ui(self):
        columnDescriptions = [
            {"title": "Delete",
            "cell": vanilla.CheckBoxListCell(),
            "width": 40},
            {"title": "Description",
            "typingSensitive": True,
            "editable": False,
            "width": 210},
            {"title": "Size",
            "typingSensitive": True,
            "editable": False,
            "width": 60},
            {"title": "Key",
            "typingSensitive": True,
            "editable": True,
            "width": 220},
            {"title": "Location",
            "typingSensitive": True,
            "editable": False,
            "width": 40},
            
        ]
        self._width = 640
        self._height = 300
        
        self.w = vanilla.Window((self._width, self._height), "UFO Cleaner", (self._width, self._height))
        self.w.key_list = vanilla.List((10, 9, -10, -40),
            self._libkeys,
            columnDescriptions=columnDescriptions,
            drawFocusRing=True,
            #editCallback=self._setDecompose,
            doubleClickCallback=self._open_sheet,
            )
        #self.w.xml = CodeEditor((10, -130, -10, -40), "", lexer="xml")
        
        self.w.total_size = vanilla.TextBox((10, -30 , 240, 20), "")
        self._update_total_size_display()
        
        self.w.action_button = vanilla.Button((-200, -30 , -10, 20), "Delete checked items from UFO",
            callback=self._clean_ufo,
            sizeStyle="small",
        )
        
        self._sheet = False
        self.setUpBaseWindowBehavior()
        self.w.open()
    
    def _collect_keys(self):
        self._seen_keys = []
        self._libkeys = []
        self._key_contents = {}
        self._key_sizes = {}
        
        if self._font is not None:
            
            # Font lib
            for k in self._font.lib.keys():
                if not k in self._seen_keys:
                    self._libkeys.append({
                        "Delete": False,
                        "Description": self._known_keys.get(k, "(%s)" % k.split(".")[-1]),
                        "Size": "? kB",
                        "Key": k,
                        "Location": "Font",
                    })
                    self._seen_keys.append(k)
                    self._key_contents[k] = ""
                self._key_contents[k] += writePlistToString(self._font.lib[k])[173:-9].decode("utf-8")
                self._key_sizes[k] = len(self._key_contents[k])
            
            # Glyph libs
            for g in self._font:
                for k in g.lib.keys():
                    if not k in self._seen_keys:
                        self._libkeys.append({
                        "Delete": False,
                        "Description": self._known_keys.get(k, "(%s)" % k.split(".")[-1]),
                        "Size": "? kB",
                        "Key": k,
                        "Location": "Glyph",
                        })
                        self._seen_keys.append(k)
                        self._key_contents[k] = ""
                    self._key_contents[k] += writePlistToString(g.lib[k])[173:-9].decode("utf-8")
                    self._key_sizes[k] = len(self._key_contents[k])
        
        # Collect key sizes
        total_size = 0
        for i in range(len(self._libkeys)):
            _key = self._libkeys[i]
            size = self._key_sizes[_key["Key"]]
            total_size += size
            if size < 1024:
                _key["Size"] = "%i B" % size
            else:
                _key["Size"] = "%0.1f kB" % (size / 1024)
        self.total_size = total_size
    
    def _open_sheet(self, sender):
        self.s = vanilla.Sheet((self._width-50, 220), self.w, (self._width-50, 220))
        #self.s.contents = vanilla.EditText((10, 10, -10, -40), continuous=False, sizeStyle="small")
        self.s.contents = CodeEditor((10, 10, -10, -40), "", lexer="xml")
        self.s.ok_button = vanilla.Button((-80, -30 , -10, 20), "OK",
            callback=self._close_sheet,
            sizeStyle="small",
        )
        _key = sender.get()[sender.getSelection()[0]] #["Key"]
        self.s.contents.set(self._key_contents[_key["Key"]])
        self._sheet = True
        self.s.open()
    
    def _close_sheet(self, sender):
        self._sheet = False
        self.s.close()
    
    def _clean_ufo(self, sender):
        #print "Cleaning UFO ..."
        keys_to_delete = [k["Key"] for k in self.w.key_list.get() if k["Delete"]]
        #print keys_to_delete
        for k in self._font.lib.keys():
            if k in keys_to_delete:
                del self._font.lib[k]
        self._font.update()
        
        for g in self._font:
            found = False
            for k in g.lib.keys():
                if k in keys_to_delete:
                    found = True
                    del g.lib[k]
            if found:
                g.update()
        
        self._collect_keys()
        self._update_total_size_display()
        self.w.key_list.set(self._libkeys)
    
    def _update_total_size_display(self):
        self.w.total_size.set("Total library size: %0.1f kB" % (self.total_size / 1024))
    
    def windowCloseCallback(self, sender):
        #if self._sheet:
        #    self.s.close()
        super(UFOCleaner, self).windowCloseCallback(sender)

OpenWindow(UFOCleaner)
