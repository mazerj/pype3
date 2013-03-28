# this code fragment will convert a GIF to python source code
#
# python ./inline.py gif-files... >foo.py
#
# from foo import iconname
#

import base64, sys, string

print "import Tkinter"

for file in sys.argv[1:]:
    name = string.split(file, '.')[-2]
    data = base64.encodestring(open(file, "r").read())
    print name + '=Tkinter.PhotoImage(data="""\n' + data + '""")'

