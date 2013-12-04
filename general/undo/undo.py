import maya.cmds as mc

class Undo(object):
    def __enter__(self):
        mc.undoInfo(openChunk=True)
    def __exit__(self, *exc_info):
        mc.undoInfo(closeChunk=True)

