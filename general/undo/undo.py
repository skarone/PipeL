"""
For work with undo
WARNGING!... IF THERE IS EVAL IN THE CODE THIS DOESN'T WORK

import general.undo.undo as undo

with undo.Undo():
	CODE GOES HERE

"""
import maya.cmds as mc

class Undo(object):
    def __enter__(self):
        mc.undoInfo(openChunk=True)
    def __exit__(self, *exc_info):
        mc.undoInfo(closeChunk=True)

